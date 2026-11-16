"""Gera prévias de boas-vindas com dados fictícios; não envia mensagens."""
import argparse
import base64
import html
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
TEMPLATES=ROOT/'xano/templates'


def render(profile,name):
    config=json.loads((TEMPLATES/'welcome_email.json').read_text())
    if profile not in config['profiles'] or not isinstance(name,str) or not name.strip() or len(name)>500:raise ValueError('Mensagem inválida')
    for k in ('brand_color','background_color','text_color','header_color'):
        if not re.fullmatch(r'#[a-fA-F0-9]{6}',config[k]):raise ValueError('Cor inválida')
    for k in ('clinic_image_url','davi_image_url','vitor_image_url','danikelly_image_url','background_image_url','mascot_image_url'):
        if not re.fullmatch(r'https://[a-zA-Z0-9.-]+(?::[0-9]+)?/[^\s"<>]*',config[k]):raise ValueError('Imagem inválida')
    if config['system_url']!='http://localhost:3000/login' and not re.fullmatch(r'https://[a-zA-Z0-9.-]+(?::[0-9]+)?/[^\s"<>]*',config['system_url']):raise ValueError('URL do sistema inválida')
    values={**config,**config['profiles'][profile],'name':name.strip()}
    def substitute(source,safe):
        return re.sub(r'\{\{([a-z_]+)\}\}',lambda m:html.escape(values[m[1]],quote=True) if safe else values[m[1]],source)
    return {'subject':values['subject'],'html':substitute((TEMPLATES/'welcome_email.html').read_text(),True),'text':substitute((TEMPLATES/'welcome_email.txt').read_text(),False)}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'openspec/changes/enviar-boas-vindas-cadastro/evidence/email');a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    config=json.loads((TEMPLATES/'welcome_email.json').read_text())
    for profile,name in (('tutor','Ana Silva'),('veterinario','Alex Oliveira')):
        m=render(profile,name)
        for k,path in (('background_image_url',ROOT/'assets/optimized/fundo.webp'),('mascot_image_url',ROOT/'assets/consultation-pdf/mascote-v-clean.png'),('clinic_image_url',ROOT/'assets/mascote/clinicturtle.jpeg'),('davi_image_url',TEMPLATES/'developers/davi-diniz.jpeg'),('vitor_image_url',TEMPLATES/'developers/vitor-sousa.png'),('danikelly_image_url',TEMPLATES/'developers/danikelly-alves.png')):
            mime={'.png':'image/png','.webp':'image/webp','.jpeg':'image/jpeg'}[path.suffix];m['html']=m['html'].replace(config[k],'data:'+mime+';base64,'+base64.b64encode(path.read_bytes()).decode())
        for ext,key in (('html','html'),('txt','text')):(a.output/(profile+'.'+ext)).write_text(m[key])
    print('Prévias fictícias:',a.output)

if __name__=='__main__':main()
