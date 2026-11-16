"""Sincroniza o renderizador Xano de boas-vindas com os templates canônicos; sem rede."""
import argparse
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TEMPLATES=ROOT/'xano/templates'
OUTPUT=ROOT/'xano/function/notifications/render_welcome_email.xs'


def renderer_code():
    config=json.loads((TEMPLATES/'welcome_email.json').read_text())
    return '\n'.join([
        'const config='+json.dumps(config,ensure_ascii=False)+';',
        'const template='+json.dumps((TEMPLATES/'welcome_email.html').read_text(),ensure_ascii=False)+';',
        'const plain='+json.dumps((TEMPLATES/'welcome_email.txt').read_text(),ensure_ascii=False)+';',
        r'''const p=$input;
if(!Object.hasOwn(config.profiles,p.profile)||typeof p.name!=='string'||!p.name.trim()||p.name.length>500)throw Error('Mensagem inválida.');
for(const k of ['brand_color','background_color','text_color','header_color'])if(!/^#[0-9a-fA-F]{6}$/.test(config[k]))throw Error('Cor inválida.');
for(const k of ['clinic_image_url','davi_image_url','vitor_image_url','danikelly_image_url','background_image_url','mascot_image_url'])if(!/^https:\/\/[a-z0-9.-]+(?::[0-9]+)?\/[^\s"<>]*$/i.test(config[k]))throw Error('Imagem inválida.');
if(config.system_url!=='http://localhost:3000/login'&&!/^https:\/\/[a-z0-9.-]+(?::[0-9]+)?\/[^\s"<>]*$/i.test(config.system_url))throw Error('URL do sistema inválida.');
const values={...config,...config.profiles[p.profile],name:p.name.trim()};
const escape=v=>String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#x27;'}[c]));
const render=(source,safe)=>source.replace(/\{\{([a-z_]+)\}\}/g,(_,key)=>{if(typeof values[key]!=='string')throw Error('Variável inválida.');return safe?escape(values[key]):values[key];});
return {subject:values.subject,html:render(template,true),text:render(plain,false)};'''])


def generated():
    code=renderer_code()
    if '"""' in code:raise ValueError('Delimitador Xano inválido')
    return '''// Gerado por scripts/sync_welcome_email.py; editar xano/templates/welcome_email.*.
function "Notifications/render_welcome_email" {
  input { text name\n    text profile }
  stack {
    api.lambda {
      code = """
'''+code+'''
      """
      timeout = 5
    } as $message
  }
  response = $message
  history = false
  tags = ["vettech", "welcome-email"]
}
'''


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    content=generated()
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text()!=content:raise SystemExit('Renderizador desatualizado; execute scripts/sync_welcome_email.py')
        print('Renderizador de boas-vindas sincronizado.')
    else:
        OUTPUT.parent.mkdir(parents=True,exist_ok=True);OUTPUT.write_text(content);print('Gerado:',OUTPUT)

if __name__=='__main__':main()
