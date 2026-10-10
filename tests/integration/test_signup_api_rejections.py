"""Verifica rejeicoes na API real sem criar contas.

Execucao explicita: definir XANO_TEST_AUTH_URL com a URL do grupo Authentication
e executar python -m unittest discover -s tests/integration -v.
Os testes de cadastro bem-sucedido e persistencia usam fixtures isoladas e nao
fazem parte desta suite de chamadas sem criacao de contas.
"""

import os
import unittest

import httpx


AUTH_URL = os.getenv("XANO_TEST_AUTH_URL", "").rstrip("/")


@unittest.skipUnless(AUTH_URL, "Defina XANO_TEST_AUTH_URL para executar contra Xano")
class SignupApiRejectionTests(unittest.TestCase):
    def setUp(self):
        self.client = httpx.Client(timeout=25)
        self.addCleanup(self.client.close)

    def payload(self):
        return {
            "nome": "Teste automatizado sem cadastro",
            "cpf": "11111111111",
            "email": "vet-tech-rejection@example.invalid",
            "telefone": "11999999999",
            "endereco": "Endereco ficticio de teste",
            "password": "SenhaSomenteDeTeste!2026",
        }

    def assert_rejected(self, payload, expected_message=None):
        response = self.client.post(f"{AUTH_URL}/tutor/signup", json=payload)
        self.assertEqual(response.status_code, 400)
        body = response.json()
        self.assertFalse(body.get("success", False))
        self.assertNotIn("password", body)
        self.assertNotIn("authToken", body)
        if expected_message:
            self.assertEqual(body.get("message"), expected_message)

    def test_each_required_field_missing(self):
        for field in self.payload():
            with self.subTest(field=field):
                payload = self.payload()
                del payload[field]
                self.assert_rejected(payload)

    def test_cpf_with_invalid_length(self):
        payload = self.payload()
        payload["cpf"] = "123"
        self.assert_rejected(payload, "Informe um CPF válido.")

    def test_cpf_with_repeated_digits(self):
        self.assert_rejected(self.payload(), "Informe um CPF válido.")

    def test_cpf_with_wrong_check_digits(self):
        payload = self.payload()
        payload["cpf"] = "52998224724"
        self.assert_rejected(payload, "Informe um CPF válido.")

    def test_cpf_with_letters(self):
        payload = self.payload()
        payload["cpf"] = "5299822472a"
        self.assert_rejected(payload, "Informe um CPF válido.")


if __name__ == "__main__":
    unittest.main()
