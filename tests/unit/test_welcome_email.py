"""Conteúdo, escape e paridade do template realmente enviado pelo Xano."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import unittest
ROOT=Path(__file__).resolve().parents[2]

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
preview=load('welcome_preview','scripts/preview_welcome_email.py')
sync=load('welcome_sync','scripts/sync_welcome_email.py')

class WelcomeEmailTests(unittest.TestCase):
    def test_generated_renderer_is_current(self):
        self.assertEqual(sync.OUTPUT.read_text(),sync.generated())

    def test_profiles_have_distinct_and_appropriate_guidance(self):
        tutor=preview.render('tutor','Ana');vet=preview.render('veterinario','Alex')
        self.assertNotEqual(tutor['subject'],vet['subject'])
        self.assertIn('Cadastre seus pets',tutor['text'])
        self.assertNotIn('Organize seus horários',tutor['text'])
        self.assertIn('Organize seus horários',vet['text'])
        self.assertIn('autorização concedida pelos tutores',vet['text'])
        for message in (tutor,vet):
            self.assertNotIn('PetSync',message['html'])
            self.assertIn('href="http://localhost:3000/login"',message['html'])
            self.assertIn('Acesse nosso sistema: http://localhost:3000/login',message['text'])
            self.assertNotIn('{{',message['html'])
            for name in ('Davi Diniz','Vitor Sousa','Danikelly Alves','Copyright © by Vet Tech Team'):
                self.assertIn(name,message['text']);self.assertIn(name,message['html'])

    def test_name_is_escaped_and_invalid_profiles_rejected(self):
        m=preview.render('tutor','Ana <script>&"')
        self.assertNotIn('<script>',m['html']);self.assertIn('Ana &lt;script&gt;&amp;&quot;',m['html'])
        self.assertIn('Ana <script>&"',m['text'])
        for profile,name in [('user','Ana'),('Tutor','Ana'),('tutor',''),('tutor',' '*3),('tutor','x'*501),('tutor',42)]:
            with self.subTest(profile=profile,name=str(name)[:10]):
                with self.assertRaises(ValueError):preview.render(profile,name)

    def test_images_are_https_without_attachments_or_password_flow_content(self):
        m=preview.render('tutor','Ana')
        for forbidden in ('data:image','cid:','box-shadow','Seu código de verificação','Não foi você?'):
            self.assertNotIn(forbidden,m['html'])
        self.assertEqual(m['html'].count('<img '),5)
        self.assertNotIn('attachments',m)
        config=json.loads((ROOT/'xano/templates/welcome_email.json').read_text())
        self.assertIn('background="'+config['background_image_url']+'"',m['html'])
        self.assertIn(config['mascot_image_url'],m['html'])
        self.assertEqual(config['header_color'],'#526b35')

    @unittest.skipUnless(shutil.which('node'),'Node necessário para executar o renderizador real')
    def test_native_javascript_and_local_preview_match(self):
        for profile in ('tutor','veterinario'):
            data={'profile':profile,'name':'  Álex <&> "\'  '}
            code='const $input='+json.dumps(data)+';process.stdout.write(JSON.stringify((()=>{'+sync.renderer_code()+'})()));'
            got=json.loads(subprocess.check_output(['node'],input=code,text=True))
            self.assertEqual(got,preview.render(**data))

    @unittest.skipUnless(shutil.which('node'),'Node necessário para testar recibo Brevo')
    def test_receipt_needs_success_status_and_message_id_and_handles_uncertainty(self):
        s=(ROOT/'xano/function/notifications/deliver_welcome_email.xs').read_text()
        line=[v for v in s.splitlines() if 'code = ' in v][-1];code=json.loads(line.split('code = ',1)[1])
        for status,result,accepted,state in [(201,{'messageId':'<id>'},True,'aceito'),(201,{},False,'incerto'),(401,{'message':'denied'},False,'falhou'),(429,{},False,'falhou'),(500,{},False,'incerto'),(0,{},False,'incerto')]:
            payload={'delivery':{'response':{'status':status,'result':result}}}
            js='const $var='+json.dumps(payload)+';process.stdout.write(JSON.stringify((()=>{'+code+'})()));'
            got=json.loads(subprocess.check_output(['node'],input=js,text=True))
            self.assertEqual(got['accepted'],accepted);self.assertEqual(got['state'],state)
            if not accepted:self.assertEqual(got['provider_id'],'')
