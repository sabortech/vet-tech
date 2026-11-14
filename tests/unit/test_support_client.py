import os
import unittest
from unittest.mock import AsyncMock, patch

from vet_tech.shared.support_client import SupportConfigurationError, support_request
from vet_tech.shared.xano_client import XanoRequestError


class SupportClientTests(unittest.IsolatedAsyncioTestCase):
    async def test_creation_requires_private_credential(self):
        with patch.dict(os.environ, {'SUPPORT_CHAT_BRIDGE_SECRET': ''}), patch('vet_tech.shared.support_client.xano_request', AsyncMock()) as call:
            with self.assertRaises(SupportConfigurationError):
                await support_request('tutor', 'token', {'action': 'create'})
            call.assert_not_awaited()

    async def test_credential_is_only_added_to_creation(self):
        with patch.dict(os.environ, {'SUPPORT_CHAT_BRIDGE_SECRET': 'private-bridge-key'}), patch('vet_tech.shared.support_client.xano_request', AsyncMock(return_value={'tickets': []})) as call:
            await support_request('tutor', 'token', {'action': 'list'})
            self.assertNotIn('bridge_key', call.call_args.kwargs['json_payload'])
            await support_request('tutor', 'token', {'action': 'create'})
            self.assertEqual(call.call_args.kwargs['json_payload']['bridge_key'], 'private-bridge-key')

    async def test_identity_is_not_taken_from_payload(self):
        with patch('vet_tech.shared.support_client.xano_request', AsyncMock()) as call:
            for profile, token in [('visitante', 'token'), ('tutor', '')]:
                with self.assertRaises(XanoRequestError):
                    await support_request(profile, token, {'action':'list','profile':'tutor'})
            call.assert_not_awaited()

    async def test_malformed_response_is_not_success(self):
        with patch('vet_tech.shared.support_client.xano_request', AsyncMock(return_value={'ok': True})):
            with self.assertRaises(XanoRequestError):
                await support_request('tutor', 'token', {'action': 'list'})
