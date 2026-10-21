"""Safety checks for the live verification harness; no Xano business-rule mocks."""

import importlib.util
from pathlib import Path
import unittest

import httpx


spec = importlib.util.spec_from_file_location(
    "record_verification",
    Path(__file__).parents[1] / "integration" / "run_record_foundation_live.py",
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class VerificationSafetyTests(unittest.TestCase):
    def test_requires_explicit_synthetic_development(self):
        for config in ({}, {"environment": "production", "synthetic": True},
                       {"environment": "development", "synthetic": False}):
            with self.subTest(config=config), self.assertRaises(ValueError):
                module.Verification(config)

    def test_rejects_insecure_or_non_origin_url(self):
        for origin in ("http://dev.example.invalid", "https://dev.example.invalid/api:prod", "invalid"):
            with self.subTest(origin=origin), self.assertRaises(ValueError):
                module.Verification({"environment": "development", "synthetic": True, "origin": origin})

    def test_failure_does_not_echo_backend_secrets(self):
        config = {"environment": "development", "synthetic": True,
                  "origin": "https://dev.example.invalid", "tokens": {"vet_a": "secret-token"}}
        transport = httpx.MockTransport(lambda request: httpx.Response(500, text="password=private-clinical-data"))
        verification = module.Verification(config, transport)
        try:
            with self.assertRaises(AssertionError) as failure:
                verification.call("GET", "/api:vettech-records/records", "vet_a")
            self.assertNotIn("private-clinical-data", str(failure.exception))
            self.assertNotIn("secret-token", str(failure.exception))
        finally:
            verification.client.close()


if __name__ == "__main__":
    unittest.main()
