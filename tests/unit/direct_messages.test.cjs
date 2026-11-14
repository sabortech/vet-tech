const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs');
const source=fs.readFileSync('xano/function/direct/operate.xs','utf8');
const blocks=[...source.matchAll(/code = """([\s\S]*?)"""/g)].map(m=>m[1]);
const validate=new Function('$input',blocks[0]);
const transition=new Function('$var','$input',blocks.find(b=>b.includes('let messages=t.messages')));
const id='11111111-1111-4111-8111-111111111111';
const run=(p,thread={messages:[],events:[]},profile='veterinario',actor_id=7)=>transition({p,thread},{profile,actor_id});
test('directories restricted to opposite profile and start requires valid peer; payload bounded',()=>{
 for(const action of ['tutors','start'])assert.throws(()=>validate({profile:'tutor',actor_id:1,payload:{action,tutor_id:2}}),/disponível/);
 const p=validate({profile:'tutor',actor_id:1,payload:{action:'start',veterinario_id:7,tutor_id:999}});assert.equal(p.tutor_id,1);assert.equal(p.veterinario_id,7);
 assert.throws(()=>validate({profile:'veterinario',actor_id:7,payload:{action:'veterinarians'}}),/disponível/);
 assert.throws(()=>validate({profile:'veterinario',actor_id:7,payload:{action:'tutors',search:'a'.repeat(101)}}),/Busca/);
 assert.throws(()=>validate({profile:'veterinario',actor_id:7,payload:{action:'send',thread_id:1,message:'ok',operation_id:'bad'}}),/inválida/);
});
test('send idempotence, author checks and revision-aware read receipts',()=>{
 const p={action:'send',operation_id:id,message:'Olá'};
 const first=run(p);assert.equal(first.messages.length,1);assert.equal(run(p,first).changed,false);
 assert.throws(()=>run({...p,message:'outra'},first),/utilizada/);
 const edit={action:'edit',operation_id:'22222222-2222-4222-8222-222222222222',message_id:id,expected_revision:0,message:'Oi'};
 assert.throws(()=>run(edit,first,'tutor',3),/disponível/);
 const changed=run(edit,first);assert.equal(changed.messages[0].revision,1);
 assert.equal(run({action:'get',read_through:id,read_revision:0},changed,'tutor',3).changed,false);
 assert.ok(run({action:'get',read_through:id,read_revision:1},changed,'tutor',3).messages[0].read_at);
 assert.throws(()=>run({...edit,operation_id:'new',expected_revision:1},{...changed,messages:[{...changed.messages[0],at:Date.now()-600001}]}),/10 minutos/);
});
test('projection never returns audit text or clinical information',()=>{
 const project=new Function('$var',blocks.find(b=>b.includes('server_time:Date.now(),thread:')));
 const out=project({thread:{id:1,messages:[],events:[{value:'private'}]},vet:{nome:'Médico'},tutor:{nome:'Ana'}});
 assert.equal(out.thread.tutor.name,'Ana');assert.equal(out.thread.events,undefined);assert.equal(out.thread.pet,undefined);
 assert.ok(source.includes('btree')===false);assert.ok(source.includes('$thread.tutor_id == $input.actor_id'));assert.ok(source.includes('$thread.veterinario_id == $input.actor_id'));
});
