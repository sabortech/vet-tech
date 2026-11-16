"""Parity between the editable preview and the actual Xano renderer."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT=Path(__file__).resolve().parents[2]

def load(name, path):
    spec=importlib.util.spec_from_file_location(name, ROOT/path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

preview=load('email_preview','scripts/preview_password_email.py')
sync=load('email_sync','scripts/sync_password_email.py')


class PasswordEmailTests(unittest.TestCase):
    def test_generated_xano_matches_editable_templates(self):
        self.assertEqual(sync.OUTPUT.read_text(),sync.generated())

    @unittest.skipUnless(shutil.which('node'), 'Node is needed to execute the Xano JavaScript renderer')
    def test_xano_and_preview_render_identical_bodies_and_preserve_leading_zero(self):
        for purpose in ('reset','change'):
            payload={'purpose':purpose,'code':'012345','validity_minutes':10}
            code='const $input='+json.dumps(payload)+';const result=(()=>{'+sync.renderer_code()+'})();process.stdout.write(JSON.stringify(result));'
            actual=json.loads(subprocess.check_output(['node'],input=code,text=True))
            self.assertEqual(actual,preview.render(**{k:payload[k] for k in payload}))
            self.assertIn('012345',actual['html'])
            self.assertNotIn('{{',actual['text'])

    def test_rejects_invalid_code(self):
        for code in ('12345','１２３４５６','<svg/>',123456):
            with self.assertRaises(ValueError):
                preview.render('reset',code,10)

    def test_header_uses_https_image_in_body_without_attachments(self):
        message = preview.render('reset', '012345', 10)
        config = json.loads((ROOT/'xano/templates/password_verification.json').read_text())
        self.assertTrue(config['header_image_url'].startswith('https://'))
        self.assertIn('src="' + config['header_image_url'] + '"', message['html'])
        self.assertNotIn('attachments', message)
        self.assertNotIn('cid:', message['html'])
        self.assertNotIn('data:image', message['html'])
        self.assertIn('alt="Vet Tech', message['html'])
        self.assertIn('012345', message['text'])

    def test_sender_returns_only_acceptance_and_disables_history(self):
        sender=(ROOT/'xano/function/security/send_password_email.xs').read_text()
        self.assertIn('response = {accepted: true}',sender)
        self.assertIn('textContent: $message.text',sender)
        self.assertIn('htmlContent: $message.html',sender)
        self.assertNotIn('attachments:',sender)
        self.assertIn('history = false',sender)

    @unittest.skipUnless(shutil.which('node'), 'Node is needed to execute sender validation')
    def test_sender_configuration_accepts_verified_address_formats_and_rejects_injection(self):
        sender=(ROOT/'xano/function/security/send_password_email.xs').read_text()
        line=next(line for line in sender.splitlines() if 'code = ' in line)
        code=json.loads(line.split('code = ',1)[1])
        for raw,valid in (
            ('Vet Tech <vet.tech.impact@gmail.com>', True),
            ('vet.tech.impact@gmail.com', True),
            ('', False), ('Vet Tech <invalid>', False),
            ('Vet Tech\r\nBcc: other@example.com <vet.tech.impact@gmail.com>', False),
            ('Vet Tech <vet.tech.impact@gmail.com>, other@example.com', False),
        ):
            with self.subTest(raw=raw):
                script='const $env='+json.dumps({'PASSWORD_EMAIL_FROM':raw})+';process.stdout.write(JSON.stringify((()=>{'+code+'})()));'
                result=json.loads(subprocess.check_output(['node'],input=script,text=True))
                self.assertEqual(result['valid'], valid)
                if valid:
                    self.assertEqual(result['email'],'vet.tech.impact@gmail.com')
                    self.assertEqual(result['name'],'Vet Tech')
