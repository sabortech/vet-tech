const {test}=require('node:test');const assert=require('node:assert/strict');
const source=require('node:fs').readFileSync('xano/function/support/operate.xs','utf8');
const blocks=[...source.matchAll(/code = """([\s\S]*?)"""/g)].map(m=>m[1]);
const transition=new Function('$var','$input',blocks.find(s=>s.includes('let status=t.status')));
const validate=new Function('$input',blocks[0]);
const a='11111111-1111-4111-8111-111111111111',b='22222222-2222-4222-8222-222222222222',c='33333333-3333-4333-8333-333333333333';
const messages=[{id:a,author_profile:'veterinario',text:'A'},{id:b,author_profile:'tutor',text:'B'},{id:c,author_profile:'veterinario',text:'C'}];
function run(profile,id,rows=messages,p={action:'get'}){return transition({p:{...p,read_through:id},ticket:{status:'em_atendimento',veterinario_id:9,messages:rows,events:[]}},{profile,actor_id:profile==='tutor'?1:9});}
test('read watermark updates received messages only, up to a valid reference',()=>{
 const first=run('tutor',a);assert.ok(first.messages[0].read_at);assert.equal(first.messages[1].read_at,undefined);assert.equal(first.messages[2].read_at,undefined);assert.equal(first.events.length,0);
 const last=run('tutor',c);assert.ok(last.messages[0].read_at);assert.ok(last.messages[2].read_at);assert.equal(last.messages[1].read_at,undefined);
});
test('cannot mark own, unknown or malformed messages',()=>{
 assert.throws(()=>run('tutor',b),/inválida/);assert.throws(()=>run('veterinario',a),/inválida/);assert.throws(()=>run('tutor','future'),/inválida/);
 assert.throws(()=>validate({payload:{action:'get',ticket_id:1,read_through:'future'}}),/inválida/);
});
test('repeat read is monotonic, does not write or append events',()=>{
 const first=run('tutor',c);const second=run('tutor',c,first.messages);
 assert.equal(second.changed,false);assert.deepEqual(second.messages,first.messages);assert.equal(second.events.length,0);
});
test('veterinarian may acknowledge tutor message without marking own messages',()=>{
 const out=run('veterinario',b);assert.ok(out.messages[1].read_at);assert.equal(out.messages[0].read_at,undefined);
});
test('list includes tutor name only for owned or assigned cards',()=>{
 const project=new Function('$var','$input',blocks.find(s=>s.includes('const pet_photos=')));
 const rows=[{id:1,pet_id:7,status:'aguardando',tutor_id:1,tutor_name:'Ana',events:[]},{id:2,pet_id:7,status:'em_atendimento',tutor_id:1,tutor_name:'Ana',veterinario_id:9,events:[]}];
 const queue=project({rows},{profile:'veterinario',actor_id:9});assert.equal(queue.tickets[0].tutor,null);assert.deepEqual(queue.tickets[1].tutor,{name:'Ana'});
 const tutor=project({rows},{profile:'tutor',actor_id:1});assert.deepEqual(tutor.tickets[0].tutor,{name:'Ana'});
});
