import json
import unittest
from unittest.mock import AsyncMock,patch
from uuid import uuid4
from vet_tech.features.auth.state import State
from vet_tech.shared.direct_client import direct_request

class DirectChatTests(unittest.IsolatedAsyncioTestCase):
    async def test_transport_uses_authenticated_profile_and_no_bridge_secret(self):
        with patch('vet_tech.shared.direct_client.xano_request',AsyncMock(return_value={'threads':[]})) as call:
            await direct_request('tutor','private',{'action':'list'})
            self.assertEqual(call.call_args.args,('POST','vettech-support','tutor/conversas'))
            self.assertEqual(call.call_args.kwargs['json_payload'],{'payload':{'action':'list'}})

    async def test_state_identity_and_stale_result(self):
        s=State(_reflex_internal_init=True);s._auth_token='private';s.is_authenticated=True;s.profile='veterinario';s.identity_id='7'
        cid=str(uuid4())
        with patch.object(State,'__aenter__',AsyncMock(return_value=s)),patch.object(State,'__aexit__',AsyncMock(return_value=False)):
            async def event(action,**kw):
                payload={'action':action,'conversation_id':cid,'session_key':s._support_session_key(),**kw}
                return [e async for e in State.support_chat.fn(s,{'payload':json.dumps(payload)})]
            await event('open')
            with patch('vet_tech.features.support_chat.state.direct_request',AsyncMock(return_value={'thread':{'id':3}})) as call:
                result=await event('direct_start',request_id=str(uuid4()),tutor_id=9,actor_id=999)
                self.assertEqual(call.call_args.args,('veterinario','private',{'action':'start','tutor_id':9}))
                self.assertIn('vettech:direct-response',str(result));self.assertEqual(s._direct_thread,3)
                self.assertNotIn('private',str(result))
                await event('direct_send',request_id=str(uuid4()),thread_id=3,operation_id='bad',message='Olá')
                self.assertEqual(call.await_count,1)
            s.profile='tutor'
            with patch('vet_tech.features.support_chat.state.direct_request',AsyncMock()) as call:
                await event('direct_start',request_id=str(uuid4()),tutor_id=9)
                call.assert_not_awaited()
            self.assertNotIn('_direct_thread',s.dict())

    async def test_old_session_response_is_discarded(self):
        s=State(_reflex_internal_init=True);s._auth_token='private';s.is_authenticated=True;s.profile='tutor';s.identity_id='7'
        cid=str(uuid4());s._support_conversation=cid;s._support_session=s._session_generation
        async def stale(*args):
            s._reset_support_chat()
            return {"thread":{"id":1}}
        with patch.object(State,'__aenter__',AsyncMock(return_value=s)),patch.object(State,'__aexit__',AsyncMock(return_value=False)),patch('vet_tech.features.support_chat.state.direct_request',AsyncMock(side_effect=stale)):
            data={"action":"direct_get","conversation_id":cid,"session_key":s._support_session_key(),"request_id":str(uuid4()),"thread_id":1}
            events=[e async for e in s._direct_chat_operation(data)]
            self.assertEqual(events,[]);self.assertEqual(s._direct_thread,0)

    async def test_tutor_selects_veterinarian_without_forging_identity(self):
        s=State(_reflex_internal_init=True);s._auth_token='private';s.is_authenticated=True;s.profile='tutor';s.identity_id='7'
        cid=str(uuid4());s._support_conversation=cid;s._support_session=s._session_generation
        with patch.object(State,'__aenter__',AsyncMock(return_value=s)),patch.object(State,'__aexit__',AsyncMock(return_value=False)),patch('vet_tech.features.support_chat.state.direct_request',AsyncMock(return_value={"thread":{"id":1}})) as call:
            data={"action":"direct_start","conversation_id":cid,"session_key":s._support_session_key(),"request_id":str(uuid4()),"veterinario_id":9,"tutor_id":999}
            events=[e async for e in s._direct_chat_operation(data)]
            self.assertTrue(events)
            self.assertEqual(call.call_args.args,('tutor','private',{'action':'start','veterinario_id':9}))
