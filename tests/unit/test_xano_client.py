import os
import traceback
import unittest
from unittest.mock import patch

import httpx

from vet_tech.shared.config import ConfigurationError, get_xano_base_url
from vet_tech.shared.xano_client import XanoRequestError, xano_request


class ConfigurationTests(unittest.TestCase):
    def test_missing_blank_and_invalid_origins_do_not_echo_values(self):
        for value in (None, "", "  ", "secret-value", "https://user:secret@host",
                      "https://host/path", "https://host?token=secret", "https://host:bad"):
            with self.subTest(value=value), patch.dict(os.environ, {}, clear=True):
                if value is not None:
                    os.environ["XANO_API_BASE_URL"] = value
                with self.assertRaises(ConfigurationError) as caught:
                    get_xano_base_url()
                self.assertIn("XANO_API_BASE_URL", str(caught.exception))
                self.assertNotIn("secret", str(caught.exception))

    def test_valid_origin_is_normalized(self):
        for value, expected in ((" https://dev.example.invalid/ ", "https://dev.example.invalid"),
                                ("http://127.0.0.1:8099", "http://127.0.0.1:8099")):
            with patch.dict(os.environ, {"XANO_API_BASE_URL": value}):
                self.assertEqual(get_xano_base_url(), expected)


class StartupTests(unittest.IsolatedAsyncioTestCase):
    async def test_registered_lifespan_rejects_missing_configuration(self):
        from vet_tech.vet_tech import app
        from vet_tech.shared.config import validate_backend_configuration

        self.assertIn(validate_backend_configuration, app._lifespan_tasks)
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ConfigurationError):
                async with validate_backend_configuration():
                    self.fail("A aplicação não deve aceitar requisições.")
        with patch.dict(os.environ, {"XANO_API_BASE_URL": "http://127.0.0.1:8099"}):
            async with validate_backend_configuration():
                pass


class XanoClientTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.environment = patch.dict(os.environ, {"XANO_API_BASE_URL": "https://dev.example.invalid"})
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.client_class = httpx.AsyncClient

    async def request(self, handler, **kwargs):
        transport = httpx.MockTransport(handler)
        with patch("vet_tech.shared.xano_client.httpx.AsyncClient",
                   side_effect=lambda **options: self.client_class(transport=transport, **options)):
            return await xano_request("POST", "pets", "/pets", **kwargs)

    async def test_json_and_bearer_token(self):
        def handler(request):
            self.assertEqual(str(request.url), "https://dev.example.invalid/api:pets/pets")
            self.assertEqual(request.headers["Authorization"], "Bearer synthetic-token")
            self.assertEqual(request.content, b'{"nome":"Rex"}')
            return httpx.Response(200, json={"id": 1})
        self.assertEqual(await self.request(handler, auth_token="synthetic-token",
                                            json_payload={"nome": "Rex"}), {"id": 1})

    async def test_multipart_keeps_fields_and_photo(self):
        def handler(request):
            self.assertNotIn("Authorization", request.headers)
            self.assertIn("multipart/form-data", request.headers["Content-Type"])
            for content in (b'name="nome"', b'Rex', b'name="foto"', b'rex.png', b'image-fixture'):
                self.assertIn(content, request.content)
            return httpx.Response(201, json={"id": 2})
        await self.request(handler, form_data={"nome": "Rex"},
                           files={"foto": ("rex.png", b"image-fixture", "image/png")})

    async def test_empty_response(self):
        self.assertIsNone(await self.request(lambda request: httpx.Response(204)))

    async def test_known_domain_error_preserves_feedback(self):
        with self.assertRaisesRegex(XanoRequestError, "Já existe uma conta"):
            await self.request(lambda request: httpx.Response(400, json={
                "message": "Já existe uma conta com esse CPF ou e-mail."}))

    async def test_error_payloads_do_not_leak_sensitive_content(self):
        for payload in ({"message": "password=secret-token; prontuário Rex"},
                        {"error": {"password": "secret-token"}}, {"message": ["secret-token"]}):
            with self.subTest(payload=payload), self.assertRaises(XanoRequestError) as caught:
                await self.request(lambda request: httpx.Response(500, json=payload))
            self.assertNotIn("secret-token", str(caught.exception))
            self.assertNotIn("prontuário", str(caught.exception))

    async def test_non_json_errors_and_malformed_success_are_actionable(self):
        for status in (200, 502):
            with self.subTest(status=status), self.assertRaises(XanoRequestError):
                await self.request(lambda request: httpx.Response(status, text="secret-response"))

    async def test_network_errors_do_not_leak_request_details(self):
        for exception in (httpx.ReadTimeout, httpx.ConnectError):
            def handler(request):
                raise exception("secret-token", request=request)
            with self.subTest(exception=exception), self.assertRaises(XanoRequestError) as caught:
                await self.request(handler)
            self.assertNotIn("secret-token", "".join(traceback.format_exception(caught.exception)))

    async def test_missing_configuration_does_not_send_request(self):
        with patch.dict(os.environ, {}, clear=True), patch(
            "vet_tech.shared.xano_client.httpx.AsyncClient"
        ) as client:
            with self.assertRaises(XanoRequestError):
                await xano_request("GET", "pets", "pets")
            client.assert_not_called()
