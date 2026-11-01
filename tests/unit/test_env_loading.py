"""Configuração em processos isolados, sem utilizar o .env real."""

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


class EnvLoadingTests(unittest.TestCase):
    def check_loading(self, file_value=None, environment_value=None, bom=False):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            module = root / "vet_tech" / "shared" / "config.py"
            module.parent.mkdir(parents=True)
            source = Path(__file__).resolve().parents[2] / "vet_tech/shared/config.py"
            shutil.copyfile(source, module)
            if file_value is not None:
                (root / ".env").write_text(
                    f'XANO_API_BASE_URL="{file_value}"\n',
                    encoding="utf-8-sig" if bom else "utf-8",
                )
            other_directory = root / "other"
            other_directory.mkdir()
            # Um arquivo no cwd não deve substituir a configuração da raiz.
            (other_directory / ".env").write_text(
                "XANO_API_BASE_URL=https://wrong.example.invalid\n", encoding="utf-8"
            )
            environment = os.environ.copy()
            environment.pop("XANO_API_BASE_URL", None)
            environment.pop("PYTHON_DOTENV_DISABLED", None)
            if environment_value is not None:
                environment["XANO_API_BASE_URL"] = environment_value
            script = (
                "import runpy, sys\n"
                "config = runpy.run_path(sys.argv[1])\n"
                "try:\n"
                "    print(config['get_xano_base_url']())\n"
                "except config['ConfigurationError']:\n"
                "    print('ConfigurationError')\n"
            )
            result = subprocess.run(
                [sys.executable, "-c", script, str(module)],
                cwd=other_directory, env=environment, capture_output=True,
                text=True, timeout=20, check=True,
            )
            self.assertEqual(result.stderr, "")
            return result.stdout.strip()

    def test_loads_root_file_from_another_directory_with_or_without_bom(self):
        for bom in (False, True):
            with self.subTest(bom=bom):
                self.assertEqual(
                    self.check_loading("https://file.example.invalid", bom=bom),
                    "https://file.example.invalid",
                )

    def test_existing_environment_has_priority(self):
        self.assertEqual(
            self.check_loading("https://file.example.invalid", "https://env.example.invalid"),
            "https://env.example.invalid",
        )

    def test_missing_file_allows_environment(self):
        self.assertEqual(
            self.check_loading(environment_value="https://env.example.invalid"),
            "https://env.example.invalid",
        )

    def test_missing_configuration_still_fails(self):
        self.assertEqual(self.check_loading(), "ConfigurationError")

    def test_empty_environment_does_not_fall_back_to_file(self):
        self.assertEqual(
            self.check_loading("https://file.example.invalid", ""),
            "ConfigurationError",
        )
