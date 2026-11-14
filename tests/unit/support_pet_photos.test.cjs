const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const source=fs.readFileSync('xano/function/support/operate.xs','utf8');
const blocks=[...source.matchAll(/code = """([\s\S]*?)"""/g)].map(m=>m[1]);
test('list projects one photo per pet without exposing context to the queue',()=>{
 const project=new Function('$var','$input',blocks.find(s=>s.includes('const pet_photos=')));
 const rows=[1,2].map(id=>({id,pet_id:7,pet_photo:'data:image/png;base64,AAAA',status:'aguardando',tutor_id:1,events:[{id:1,action:'create'}],reason:'private',context:['private']}));
 const out=project({rows},{profile:'veterinario',actor_id:9});
 assert.deepEqual(out.pet_photos,{'7':'data:image/png;base64,AAAA'});
 assert.equal(out.tickets.length,2);
 for(const t of out.tickets){assert.deepEqual(t.events,[]);assert.equal(t.pet_id,7);assert.equal(t.context,undefined);assert.equal(t.reason,undefined);assert.equal(t.pet_photo,undefined);}
});
test('authorized detail includes photo and supports a missing photo',()=>{
 const project=new Function('$var','$input',blocks.find(s=>s.includes('const t=$var.ticket,v=$var.vet;')));
 for(const photo of [null,'https://example.com/pet.jpg']){
  const out=project({ticket:{id:1,events:[]},vet:null,pet:{id:7,nome:'Luna',foto:photo,tutor_name:'Ana'}},{profile:'tutor'});
  assert.equal(out.ticket.pet.photo,photo);assert.deepEqual(out.ticket.tutor,{name:'Ana'});
 }
});

test('only authorized veterinary detail projects contact fields; no extra personal fields',()=>{
 const project=new Function('$var','$input',blocks.find(s=>s.includes('const t=$var.ticket,v=$var.vet;')));
 const vars={ticket:{id:1,events:[]},vet:null,pet:{id:7,nome:'Luna',tutor_name:'Ana',tutor_phone:'11999999999',tutor_email:'qa@example.invalid',cpf:'private',password:'private'}};
 assert.deepEqual(project(vars,{profile:'tutor'}).ticket.tutor,{name:'Ana'});
 assert.deepEqual(project(vars,{profile:'veterinario'}).ticket.tutor,{name:'Ana',phone:'11999999999',email:'qa@example.invalid'});
});
