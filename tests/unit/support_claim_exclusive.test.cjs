const {test}=require('node:test');const assert=require('node:assert/strict');
const source=require('node:fs').readFileSync('xano/function/support/operate.xs','utf8');
const code=[...source.matchAll(/code = """([\s\S]*?)"""/g)].map(m=>m[1]).find(s=>s.includes('let status=t.status'));
const transition=new Function('$var','$input',code);
const claim=(ticket,actor)=>transition({p:{action:'claim'},ticket},{profile:'veterinario',actor_id:actor});
test('an assigned ticket cannot be claimed again or transferred by another doctor',()=>{
 const first=claim({status:'aguardando',messages:[],events:[]},9);
 assert.equal(first.status,'em_atendimento');assert.equal(first.veterinario_id,9);
 assert.throws(()=>claim(first,10),/assumido/);assert.throws(()=>claim(first,9),/assumido/);
 assert.equal(first.veterinario_id,9);
 assert.throws(()=>claim({...first,status:'encerrado'},10),/assumido/);
});
