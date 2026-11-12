const test = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const config = require('../../scripts/n8n_support_handoff.json');
const code = config.operations.find(op => op.nodeName === 'Normalizar resposta').parameters.jsCode;
const reason = 'Solicitação de orientação veterinária após conversa com o assistente.';
function run(output, { role = 'tutor', authenticated = true, confirmed = true, token = 'private-session-token', steps = [] } = {}) {
  const req = { request_id: 'request', conversation_id: 'conversation', user: { role, authenticated } };
  const nodes = {
    'Validar requisição': req,
    'Avaliar identidade': { identidade_ok: confirmed, modo: role },
    'Receber pergunta (Webhook)': { headers: { 'x-vettech-user-token': token } },
  };
  return vm.runInNewContext('(function(){' + code + '})()', {
    $input: { first: () => ({ json: { output, intermediateSteps: steps } }) },
    $: name => ({ first: () => ({ json: nodes[name] }) }),
  })[0].json;
}
test('confirmed tutor gets correlated structured proposal', () => {
  const r = run(JSON.stringify({ reply: 'Confirme seu pet e consentimento.', handoff: { type: 'veterinary', reason } }));
  assert.equal(r.statusCode, 200);
  assert.equal(r.response.handoff.reason, reason);
  assert.equal(r.response.request_id, 'request');
  assert.equal(r.response.conversation_id, 'conversation');
});
test('ordinary tutor response has no proposal', () => {
  const r = run(JSON.stringify({ reply: 'Acesse Meus Pets.', handoff: null }));
  assert.equal(r.response.ok, true);
  assert.equal(r.response.handoff, undefined);
});
test('visitor, veterinarian and unconfirmed identity cannot emit handoff', () => {
  for (const options of [{ role: 'visitante', authenticated: false }, { role: 'veterinario' }, { confirmed: false }, { authenticated: false }]) {
    const r = run(JSON.stringify({ reply: 'Texto', handoff: { type: 'veterinary', reason } }), options);
    assert.equal(r.response.handoff, undefined);
  }
  assert.equal(run('Conversa antiga', { role: 'visitante', authenticated: false }).response.reply, 'Conversa antiga');
});
test('malformed and unexpected fields fail closed', () => {
  for (const output of ['não JSON', '{}', JSON.stringify({ reply: '', handoff: null }), JSON.stringify({ reply: 'Oi', handoff: { type: 'veterinary', reason: 'pet_id 12' } }), JSON.stringify({ reply: 'Oi', handoff: { type: 'veterinary', reason, pet_id: 12 } }), JSON.stringify({ reply: 'Oi', handoff: null, command: 'create' })]) {
    const r = run(output);
    assert.equal(r.statusCode, 503);
    assert.equal(r.response.handoff, undefined);
  }
});
test('token leak and expired tools do not emit proposal', () => {
  const output = JSON.stringify({ reply: 'private-session-token', handoff: { type: 'veterinary', reason } });
  assert.equal(run(output).statusCode, 503);
  const expired = run(output, { steps: [{ observation: 'ERROR_CODE_UNAUTHORIZED' }] });
  assert.equal(expired.statusCode, 401);
  assert.equal(expired.response.handoff, undefined);
});
