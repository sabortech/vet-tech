import unittest
from unittest.mock import AsyncMock, patch

import httpx

from vet_tech.shared.xano_client import XanoRequestError, xano_request


class XanoClientTests(unittest.IsolatedAsyncioTestCase):
    def test_error_keeps_message_and_optional_status(self):
        error = XanoRequestError("Falha")
        self.assertEqual(str(error), "Falha")
        self.assertIsNone(error.status_code)

    async def test_http_status_and_authorization_are_preserved(self):
        for status in (401, 404, 503):
            with self.subTest(status=status):
                client = AsyncMock()
                client.request.return_value = httpx.Response(status, json={"message": "Falha"})
                with patch("vet_tech.shared.xano_client.httpx.AsyncClient") as factory:
                    factory.return_value.__aenter__.return_value = client
                    with self.assertRaises(XanoRequestError) as raised:
                        await xano_request("GET", "vettech-pets", "pets/1", auth_token="test-token")
                self.assertEqual(raised.exception.status_code, status)
                self.assertEqual(str(raised.exception), "Falha")
                self.assertEqual(client.request.await_args.kwargs["headers"], {"Authorization": "Bearer test-token"})

    async def test_timeout_has_no_http_status(self):
        client = AsyncMock()
        client.request.side_effect = httpx.ReadTimeout("timeout")
        with patch("vet_tech.shared.xano_client.httpx.AsyncClient") as factory:
            factory.return_value.__aenter__.return_value = client
            with self.assertRaises(XanoRequestError) as raised:
                await xano_request("GET", "vettech-pets", "pets/1")
        self.assertIsNone(raised.exception.status_code)
        self.assertIn("demorou", str(raised.exception))
