import unittest
from unittest.mock import AsyncMock, patch

import httpx

from vet_tech.shared.xano_client import XanoRequestError, xano_request


class XanoClientTests(unittest.IsolatedAsyncioTestCase):
    async def test_rate_limit_retries_same_post_after_rejection(self):
        client = AsyncMock()
        client.request.side_effect = [httpx.Response(429, headers={"Retry-After": "2"}), httpx.Response(200, json={"id": 1})]
        with patch("vet_tech.shared.xano_client.httpx.AsyncClient") as factory, patch("vet_tech.shared.xano_client.asyncio.sleep", new_callable=AsyncMock) as sleep:
            factory.return_value.__aenter__.return_value = client
            result = await xano_request("POST", "group", "route", json_payload={"operacao": "stable"})
        self.assertEqual(result, {"id": 1})
        self.assertEqual(client.request.await_args_list[0], client.request.await_args_list[1])
        sleep.assert_awaited_once_with(2)

    async def test_rate_limit_is_bounded_and_other_failures_are_not_retried(self):
        for code, expected_calls in ((429, 3), (500, 1), (400, 1)):
            client = AsyncMock()
            client.request.return_value = httpx.Response(code, json={"message": "Failure"})
            with patch("vet_tech.shared.xano_client.httpx.AsyncClient") as factory, patch("vet_tech.shared.xano_client.asyncio.sleep", new_callable=AsyncMock):
                factory.return_value.__aenter__.return_value = client
                with self.assertRaises(XanoRequestError):
                    await xano_request("POST", "group", "route")
            self.assertEqual(client.request.await_count, expected_calls)

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
