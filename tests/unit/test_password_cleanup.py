import asyncio
import hashlib
import hmac
import unittest
from unittest.mock import AsyncMock, patch
from vet_tech.shared.password_cleanup import cleanup_password_records, password_cleanup_lifespan
from vet_tech.shared.xano_client import XanoRequestError


class PasswordCleanupTests(unittest.IsolatedAsyncioTestCase):
    async def test_missing_secret_does_not_call_remote(self):
        with patch.dict('os.environ', {'PASSWORD_CODE_SECRET': ''}), patch('vet_tech.shared.password_cleanup.xano_request', AsyncMock()) as request:
            self.assertFalse(await cleanup_password_records())
            async with password_cleanup_lifespan():
                await asyncio.sleep(0)
        request.assert_not_awaited()

    async def test_signed_request_uses_short_lived_proof_without_raw_secret(self):
        secret='synthetic-secret-with-more-than-32-characters'
        with patch.dict('os.environ', {'PASSWORD_CODE_SECRET': secret}), patch('vet_tech.shared.password_cleanup.time.time', return_value=1800000000), patch('vet_tech.shared.password_cleanup.xano_request', AsyncMock(return_value={'success': True})) as request:
            self.assertTrue(await cleanup_password_records())
        payload=request.await_args.kwargs['json_payload']
        self.assertEqual(payload['timestamp'],1800000000000)
        self.assertEqual(payload['signature'],hmac.new(secret.encode(),b'password-cleanup:1800000000000',hashlib.sha256).hexdigest())
        self.assertNotIn(secret,repr(request.await_args))

    async def test_failure_does_not_log_response_or_secret(self):
        with patch.dict('os.environ', {'PASSWORD_CODE_SECRET': 's'*40}), patch('vet_tech.shared.password_cleanup.xano_request', AsyncMock(side_effect=XanoRequestError('PRIVATE RESPONSE'))), self.assertLogs('vet_tech.shared.password_cleanup',level='WARNING') as logs:
            self.assertFalse(await cleanup_password_records())
        self.assertNotIn('PRIVATE',str(logs.output))

    async def test_lifespan_runs_immediately_and_cancels_on_shutdown(self):
        started=asyncio.Event()
        async def run():
            started.set()
            return True
        with patch.dict('os.environ', {'PASSWORD_CODE_SECRET': 's'*40}), patch('vet_tech.shared.password_cleanup.cleanup_password_records',AsyncMock(side_effect=run)) as cleanup:
            async with password_cleanup_lifespan():
                await asyncio.wait_for(started.wait(),2)
            cleanup.assert_awaited_once()
