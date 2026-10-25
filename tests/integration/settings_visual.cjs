/* Focused visual/guard regression after the complete functional integration. */
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
const root=path.resolve(__dirname,'../..'),evidence=path.join(root,'openspec/changes/archive/2026-10-25-adicionar-configuracoes-tutor/evidence');
const c=JSON.parse(fs.readFileSync(path.join(root,'.env.settings-fixtures.json')));
if(c.environment!=='development'||c.synthetic!==true)throw Error('Synthetic development only');
const origin=process.env.VETTECH_TEST_URL||'http://127.0.0.1:3000';
const wait=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{const browser=await chromium.launch({headless:true,executablePath:process.env.VETTECH_CHROMIUM_PATH,args:['--no-sandbox']});
try{const page=await browser.newPage({viewport:{width:1366,height:1000}});
await page.goto(origin+'/login',{waitUntil:'networkidle'});
await page.locator('[name=email]').fill(c.actors[0].data.email);await page.locator('[name=password]').fill(c.actors[0].data.password);
await page.getByRole('button',{name:'Login',exact:true}).click();await page.getByRole('heading',{name:'Perfil do tutor',exact:true}).waitFor({timeout:30000});await wait(7000);
await page.getByRole('link',{name:'Configurações',exact:true}).click();await page.waitForFunction(()=>document.getElementById('settings-nome')?.value.startsWith('Fixture'));
await page.locator('#settings-nome').fill('Fixture histórico pendente');
await page.evaluate(()=>history.back());await page.getByRole('alertdialog').waitFor();await page.getByRole('button',{name:'Continuar editando'}).click();
if(await page.locator('#settings-nome').inputValue()!=='Fixture histórico pendente')throw Error('History lost draft');
await page.getByRole('button',{name:'Cancelar',exact:true}).click();
console.log('PASS history guard retains draft');
const tab=async name=>{await page.getByRole('tab',{name,exact:true}).click();await page.waitForFunction(n=>document.querySelector('[role=tab][aria-selected=true]')?.textContent===n,name);};
for(const theme of ['light','dark']){
 await tab('Preferências');if(theme==='dark')await page.locator('#theme-switch').check();else await page.locator('#theme-switch').uncheck();
 await tab('Minha conta');
 for(const width of [1366,1920,768,390]){
  await page.setViewportSize({width,height:1000});await wait(700);
  const layout=await page.evaluate(()=>({viewport:innerWidth,overflow:document.documentElement.scrollWidth>innerWidth,sidebar:getComputedStyle(document.querySelector('.sidebar')).width,transform:getComputedStyle(document.querySelector('.sidebar')).transform,readOnly:getComputedStyle(document.getElementById('settings-email')).color,fill:getComputedStyle(document.getElementById('settings-email')).webkitTextFillColor}));
  if(layout.overflow)throw Error('Overflow');
  if(theme==='dark'&&(layout.readOnly==='rgb(0, 0, 0)'||layout.fill==='rgb(0, 0, 0)'))throw Error('Unreadable readonly');
  console.log(JSON.stringify({theme,...layout}));
  await page.screenshot({path:path.join(evidence,`settings-${theme}-${width}.png`),fullPage:true});
 }
}
await page.setViewportSize({width:1366,height:1000});await wait(700);await tab('Preferências');await page.screenshot({path:path.join(evidence,'preferences-dark-1366.png'),fullPage:true});
await page.getByRole('link',{name:'Meus Pets',exact:true}).click();await wait(700);
await page.getByRole('combobox',{name:'Selecione a espécie',exact:true}).click();await page.getByRole('listbox').waitFor();
await page.screenshot({path:path.join(evidence,'pets-select-dark-1366.png'),fullPage:true});await page.keyboard.press('Escape');
console.log('PASS dark pet selector');
await page.getByRole('button',{name:'Sair',exact:true}).click();await page.getByRole('button',{name:'Login',exact:true}).waitFor();
console.log('PASS final visual and history checks');
}finally{await browser.close();}})().catch(e=>{console.error(e.message);process.exitCode=1;});
