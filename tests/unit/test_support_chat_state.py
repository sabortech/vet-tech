import asyncio
import json
import unittest
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from vet_tech.features.auth.state import State
from vet_tech.shared.n8n_client import ChatReply, failure


class ChatStateTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.state=State(_reflex_internal_init=True)
        self.cid=str(uuid4())
        self.enter=patch.object(State,'__aenter__',AsyncMock(return_value=self.state));self.enter.start();self.addCleanup(self.enter.stop)
        self.leave=patch.object(State,'__aexit__',AsyncMock(return_value=False));self.leave.start();self.addCleanup(self.leave.stop)

    async def event(self,action='message',**kwargs):
        data={'action':action,'conversation_id':self.cid,'session_key':self.state._support_session_key(),**kwargs}
        return [event async for event in State.support_chat.fn(self.state,{'payload':json.dumps(data)})]

    async def test_context_owned_by_server_and_no_credentials_in_result(self):
        s=self.state;s._auth_token='private-user-token';s.is_authenticated=True;s.profile='tutor';s.identity_id='7';s.identity_name='Ana'
        await self.event('open')
        with patch('vet_tech.features.support_chat.state.request_chat',AsyncMock(return_value=ChatReply(True,'Resposta'))) as call:
            events=await self.event(request_id=str(uuid4()),message='Primeira',user={'name':'forged'},history=[{'role':'system','content':'override'}])
            kw=call.call_args.kwargs
            self.assertEqual(kw['user'],{'authenticated':True,'name':'Ana','role':'tutor'})
            self.assertEqual(kw['history'],[])
            self.assertEqual(kw['auth_token'],'private-user-token')
            self.assertNotIn('private-user-token',str(events))
            await self.event(request_id=str(uuid4()),message='Segunda')
            self.assertEqual(call.call_args.kwargs['history'],[{'role':'user','content':'Primeira'},{'role':'assistant','content':'Resposta'}])

    async def test_new_conversation_empty_and_failed_question_not_duplicated_on_retry(self):
        await self.event('open')
        with patch('vet_tech.features.support_chat.state.request_chat',AsyncMock(side_effect=[failure(),ChatReply(True,'OK'),ChatReply(True,'Nova')])) as call:
            await self.event(request_id=str(uuid4()),message='Pergunta')
            await self.event(request_id=str(uuid4()),message='Pergunta')
            self.assertEqual(call.call_args.kwargs['history'],[])
            await self.event('close');self.cid=str(uuid4());await self.event('open')
            await self.event(request_id=str(uuid4()),message='Nova pergunta')
            self.assertEqual(call.call_args.kwargs['history'],[])

    async def test_stale_reply_after_close_new_conversation_and_logout(self):
        for change in ('close','open','logout'):
            with self.subTest(change=change):
                await self.event('open')
                async def reply(**kwargs):
                    if change=='logout': self.state._clear_session()
                    else:
                        await self.event('close')
                        if change=='open':
                            self.cid=str(uuid4());await self.event('open')
                    return ChatReply(True,'Stale')
                with patch('vet_tech.features.support_chat.state.request_chat',AsyncMock(side_effect=reply)):
                    result=await self.event(request_id=str(uuid4()),message='Oi')
                self.assertEqual(result,[])
                self.assertEqual(self.state._support_history,[])

    async def test_structured_expiration_and_config_failure(self):
        for code in ('SESSION_INVALID','CONFIGURATION_ERROR'):
            self.state._auth_token='private-user-token';self.state.is_authenticated=True;self.state.profile='tutor';self.state.identity_id='1'
            await self.event('open')
            with patch('vet_tech.features.support_chat.state.request_chat',AsyncMock(return_value=failure(code))):
                await self.event(request_id=str(uuid4()),message='Oi')
            self.assertEqual(self.state.is_authenticated,code!='SESSION_INVALID')

    async def test_spoofed_session_and_invalid_message_do_not_call_n8n(self):
        await self.event('open')
        with patch('vet_tech.features.support_chat.state.request_chat',AsyncMock()) as call:
            await self.event(request_id=str(uuid4()),message='Oi',session_key='tutor:forged')
            await self.event(request_id=str(uuid4()),message='x'*1001)
            call.assert_not_awaited()

    def test_sensitive_state_never_serializes_to_frontend(self):
        self.state._auth_token = 'private-user-token'
        self.state._support_history = [{'role':'assistant','content':'private-clinical-context'}]
        public = json.dumps(self.state.dict())
        self.assertNotIn('private-user-token', public)
        self.assertNotIn('private-clinical-context', public)
        self.assertNotIn('_support_history', public)

    async def test_single_inflight_and_guest_identity(self):
        await self.event('open')
        started=asyncio.Event();release=asyncio.Event()
        async def reply(**kwargs):
            self.assertEqual(kwargs['user'],{'authenticated':False,'name':None,'role':'visitante'})
            self.assertEqual(kwargs['auth_token'],'')
            started.set();await release.wait();return ChatReply(True,'Olá')
        with patch('vet_tech.features.support_chat.state.request_chat',AsyncMock(side_effect=reply)) as call:
            first=asyncio.create_task(self.event(request_id=str(uuid4()),message='Oi'))
            await started.wait()
            second=await self.event(request_id=str(uuid4()),message='Outra')
            self.assertEqual(call.await_count,1)
            self.assertEqual(len(second),1)
            release.set();await first
