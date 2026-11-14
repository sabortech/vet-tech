const {test}=require('node:test');
const assert=require('node:assert/strict');
const source=require('node:fs').readFileSync('xano/function/support/operate.xs','utf8');
const code=[...source.matchAll(/code = """([\s\S]*?)"""/g)].map(m=>m[1]).find(s=>s.includes('let status=t.status'));
const transition=new Function('$var','$input',code);
function close(profile,status='em_atendimento',expected=status,actor=profile==='tutor'?1:9,events=[]){
 return transition({p:{action:'close',expected_status:expected,reason:'Concluído',operation_id:'op-1'},ticket:{status,veterinario_id:9,messages:[],events}},{profile,actor_id:actor});
}
test('tutor cannot end active care or forge awaiting status',()=>{
 assert.throws(()=>close('tutor'),/autorizado/);
 assert.throws(()=>close('tutor','em_atendimento','aguardando'),/mudou/);
});
test('only the assigned veterinarian ends active care',()=>{
 assert.equal(close('veterinario').status,'encerrado');
 assert.throws(()=>close('veterinario','em_atendimento','em_atendimento',10),/autorizado/);
 assert.throws(()=>close('veterinario','aguardando'),/autorizado/);
});
test('tutor may cancel awaiting and retry without adding events',()=>{
 const result=close('tutor','aguardando');assert.equal(result.status,'encerrado');assert.equal(result.events.length,1);
 const retry=close('tutor','encerrado','aguardando',1,result.events);assert.equal(retry.changed,false);assert.equal(retry.events.length,1);
});
test('assigned veterinarian retry remains idempotent',()=>{
 const result=close('veterinario');const retry=close('veterinario','encerrado','em_atendimento',9,result.events);
 assert.equal(retry.changed,false);assert.equal(retry.events.length,1);
});
