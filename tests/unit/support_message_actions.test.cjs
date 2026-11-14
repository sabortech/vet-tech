const {test}=require('node:test');const assert=require('node:assert/strict');
const source=require('node:fs').readFileSync('xano/function/support/operate.xs','utf8');
const blocks=[...source.matchAll(/code = """([\s\S]*?)"""/g)].map(m=>m[1]);
const transition=new Function('$var','$input',blocks.find(s=>s.includes('let status=t.status')));
const project=new Function('$var','$input',blocks.find(s=>s.includes('const t=$var.ticket,v=$var.vet')));
const validate=new Function('$input',blocks[0]);
const mid='11111111-1111-4111-8111-111111111111',op='22222222-2222-4222-8222-222222222222';
const original=()=>({status:'em_atendimento',veterinario_id:9,messages:[{id:mid,author_profile:'tutor',author_id:1,text:'Original',at:1000,read_at:2000}],events:[]});
const request=(action='edit',extra={})=>({action,message_id:mid,expected_revision:0,operation_id:op,message:'Alterada',...extra});
const run=(p,t=original(),profile='tutor',actor=1,now=2000)=>{const realNow=Date.now;Date.now=()=>now;try{return transition({p,ticket:t},{profile,actor_id:actor});}finally{Date.now=realNow;}};
test('only the author may edit/delete during active attendance',()=>{
 for(const action of ['edit','delete']){
  assert.throws(()=>run(request(action),original(),'veterinario',9),/disponível/);
  assert.throws(()=>run(request(action),original(),'tutor',2),/disponível/);
  assert.throws(()=>run(request(action),{...original(),status:'encerrado'}),/disponível/);
 }
});
test('edit preserves sent time, increments revision and invalidates read receipt',()=>{
 const out=run(request());assert.equal(out.messages[0].text,'Alterada');assert.equal(out.messages[0].at,1000);assert.equal(out.messages[0].revision,1);assert.ok(out.messages[0].edited_at);assert.equal(out.messages[0].read_at,null);
 assert.equal(out.events[0].value.previous_text,'Original');
 const retry=run(request(),out);assert.equal(retry.changed,false);assert.equal(retry.events.length,1);
 assert.throws(()=>run(request('edit',{operation_id:'other',expected_revision:0}),out),/alterada/);
});
test('delete clears public text, preserves private audit and is idempotent',()=>{
 const out=run(request('delete'));assert.equal(out.messages[0].text,'');assert.ok(out.messages[0].deleted_at);assert.equal(out.messages[0].revision,1);
 const visible=project({ticket:out,pet:{id:7,nome:'Pet'},vet:null},{profile:'tutor'});
 assert.equal(JSON.stringify(visible).includes('Original'),false);assert.equal(out.events[0].value.previous_text,'Original');
 assert.equal(run(request('delete'),out).changed,false);
 assert.throws(()=>run(request('edit',{operation_id:'new',expected_revision:1}),out),/disponível/);
});
test('operation reuse cannot target another message or content',()=>{
 const out=run(request());assert.throws(()=>run(request('edit',{message:'Outra'}),out),/utilizada/);
 assert.throws(()=>run(request('delete'),out),/utilizada/);
});
test('old read marker cannot acknowledge edited content',()=>{
 const out=run(request());
 const stale=run({action:'get',read_through:mid,read_revision:0},out,'veterinario',9);assert.equal(stale.changed,false);assert.equal(stale.messages[0].read_at,null);
 const fresh=run({action:'get',read_through:mid,read_revision:1},out,'veterinario',9);assert.ok(fresh.messages[0].read_at);
});
test('invalid mutation inputs rejected before transition',()=>{
 assert.throws(()=>validate({payload:request('edit',{ticket_id:1,message:''})}),/inválida/);
 assert.throws(()=>validate({payload:request('delete',{ticket_id:1,expected_revision:true})}),/inválida/);
 assert.throws(()=>validate({payload:request('edit',{ticket_id:1,message:'a'.repeat(1001)})}),/inválida/);
});

test('10 minute window uses original send time and allows exact boundary',()=>{
 for(const action of ['edit','delete']){
  assert.equal(run(request(action),original(),'tutor',1,601000).changed,true);
  assert.throws(()=>run(request(action),original(),'tutor',1,601001),/10 minutos/);
  assert.throws(()=>run(request(action),{...original(),messages:[{...original().messages[0],at:NaN}]}),/10 minutos/);
  assert.throws(()=>run(request(action),{...original(),messages:[{...original().messages[0],at:3000}]}),/10 minutos/);
 }
 const out=run(request(),original(),'tutor',1,600999);
 assert.throws(()=>run(request('edit',{operation_id:'another',expected_revision:1}),out,'tutor',1,601001),/10 minutos/);
 assert.equal(run(request(),out,'tutor',1,601001).changed,false);
});
