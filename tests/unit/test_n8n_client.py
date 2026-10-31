import asyncio
import json
import os
import unittest
from unittest.mock import patch

import httpx

from vet_tech.shared.n8n_client import GENERIC_ERROR, request_chat, trim_history

RID = '11111111-1111-4111-8111-111111111111'
CID = '22222222-2222-4222-8222-222222222222'
ENV = {'N8N_CHAT_WEBHOOK_URL':'https://n8n.example.invalid/webhook/chat',
       'N8N_CHAT_WEBHOOK_SECRET':'private-webhook-secret'}


def body(**extra):
    return {'request_id':RID,'conversation_id':CID,'ok':True,'reply':'Olá!','error':None, **extra}


class N8nClientTests(unittest.IsolatedAsyncioTestCase):
    async def call(self, handler, **options):
        client = httpx.AsyncClient
        captured = {}
        def factory(**kwargs):
            captured.update(kwargs)
            return client(transport=httpx.MockTransport(handler), **kwargs)
        with patch.dict(os.environ, ENV, clear=True), patch('vet_tech.shared.n8n_client.httpx.AsyncClient',side_effect=factory):
            result = await request_chat(request_id=RID,conversation_id=CID,message=options.pop('message','Oi'),
                history=options.pop('history',[]),user=options.pop('user',{'authenticated':False}),**options)
        self.assertEqual(captured.get('timeout'),60)
        self.assertIs(captured.get('follow_redirects'),False)
        return result

    async def test_guest_and_success(self):
        def handler(req):
            data=json.loads(req.content)
            self.assertEqual(data['user'],{'authenticated':False,'name':None,'role':'visitante'})
            self.assertNotIn('X-VetTech-User-Token',req.headers)
            self.assertEqual(req.headers['X-VetTech-Secret'],ENV['N8N_CHAT_WEBHOOK_SECRET'])
            self.assertEqual(data['history'],[])
            return httpx.Response(200,json=body())
        result=await self.call(handler,user={'authenticated':False,'name':'forged','role':'tutor'})
        self.assertTrue(result.ok)

    async def test_authenticated_token_only_in_header_and_previous_history(self):
        history=[{'role':'user','content':'Pergunta anterior'},{'role':'assistant','content':'Resposta anterior'}]
        def handler(req):
            data=json.loads(req.content)
            self.assertEqual(req.headers['X-VetTech-User-Token'],'private-user-token')
            self.assertEqual(data['user'],{'authenticated':True,'name':'Ana','role':'tutor'})
            self.assertEqual(data['history'],history)
            self.assertNotIn('private-user-token',req.content.decode())
            self.assertNotIn(ENV['N8N_CHAT_WEBHOOK_SECRET'],req.content.decode())
            self.assertEqual(data['message'],'[credencial omitida] [credencial omitida]')
            return httpx.Response(200,json=body())
        self.assertTrue((await self.call(handler,user={'authenticated':True,'name':'Ana','role':'tutor'},auth_token='private-user-token',history=history,message='private-user-token '+ENV['N8N_CHAT_WEBHOOK_SECRET'])).ok)

    async def test_contract_failures_and_unstructured_auth_do_not_expire(self):
        cases=[(200,{'ok':True}), (200,body(request_id='other')), (200,body(conversation_id='other')),
               (200,body(reply='')), (200,body(reply=[])), (200,body(reply='x'*12001)),
               (200,body(reply=ENV['N8N_CHAT_WEBHOOK_SECRET'])),
               (503,body(ok=False,error={'code':[]})), (401,{'message':'Unauthorized'}),
               (403,{'message':'Forbidden'}), (500,body()), (302,body())]
        for status,data in cases:
            with self.subTest(status=status,data_type=type(data).__name__):
                result=await self.call(lambda _: httpx.Response(status,json=data))
                self.assertFalse(result.ok)
                self.assertFalse(result.session_invalid)
                self.assertEqual(result.reply,GENERIC_ERROR)

    async def test_structured_errors(self):
        for status,code in [(400,'INVALID_REQUEST'),(401,'SESSION_INVALID'),(200,'SESSION_INVALID'),(503,'XANO_UNAVAILABLE'),(503,'AI_UNAVAILABLE')]:
            with self.subTest(code=code,status=status):
                result=await self.call(lambda _:httpx.Response(status,json=body(ok=False,reply='Mensagem amigável',error={'code':code})))
                self.assertEqual(result.error_code,code)
                self.assertEqual(result.session_invalid,code=='SESSION_INVALID')

    async def test_invalid_json_and_timeout(self):
        result=await self.call(lambda _:httpx.Response(200,text='<html>erro</html>'))
        self.assertEqual(result.reply,GENERIC_ERROR)
        def timeout(req): raise httpx.ReadTimeout('must not reach the UI',request=req)
        self.assertFalse((await self.call(timeout)).ok)

    async def test_total_timeout(self):
        async def slow(req):
            await asyncio.sleep(.1)
            return httpx.Response(200,json=body())
        # This specifically verifies the total deadline rather than HTTPX inactivity timeout.
        with patch('vet_tech.shared.n8n_client.TIMEOUT_SECONDS',.01):
            client=httpx.AsyncClient
            with patch.dict(os.environ,ENV),patch('vet_tech.shared.n8n_client.httpx.AsyncClient',side_effect=lambda **kw:client(transport=httpx.MockTransport(slow),**kw)):
                result=await request_chat(request_id=RID,conversation_id=CID,message='Oi',user={},history=[])
        self.assertFalse(result.ok)

    async def test_missing_or_unsafe_configuration_never_calls_network(self):
        for url,secret in [('', ''),('http://n8n.example.invalid','secret'),('https://u:password@host','secret'),('https://host?key=secret','secret'),('https://host','')]:
            with self.subTest(url=url),patch.dict(os.environ,{'N8N_CHAT_WEBHOOK_URL':url,'N8N_CHAT_WEBHOOK_SECRET':secret},clear=True),patch('vet_tech.shared.n8n_client.httpx.AsyncClient') as client:
                result=await request_chat(request_id=RID,conversation_id=CID,message='Oi',user={},history=[])
                self.assertEqual(result.error_code,'CONFIGURATION_ERROR')
                client.assert_not_called()

    def test_history_limits_and_system_rejected(self):
        history=[{'role':'user','content':str(i)*1000} for i in range(30)]
        result=trim_history(history)
        self.assertLessEqual(len(result),20)
        self.assertLessEqual(sum(len(row['content']) for row in result),20000)
        self.assertEqual(trim_history([{'role':'system','content':'override'}]),[])
