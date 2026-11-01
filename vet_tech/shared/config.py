"""Configuração do backend, validada sem fazer chamadas de rede."""

import os
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import urlsplit

from dotenv import load_dotenv


# Caminho independente do diretório de execução; o ambiente externo tem prioridade.
load_dotenv(
    dotenv_path=Path(__file__).resolve().parents[2] / ".env",
    override=False,
    encoding="utf-8-sig",
)


class ConfigurationError(ValueError):
    """Configuração ausente ou inválida, sem incluir valores sensíveis."""


def get_xano_base_url() -> str:
    value = os.environ.get("XANO_API_BASE_URL", "").strip().rstrip("/")
    try:
        url = urlsplit(value)
        valid = (
            url.scheme in {"http", "https"}
            and url.hostname
            and not url.username
            and not url.password
            and not url.query
            and not url.fragment
            and url.path in {"", "/"}
            and not any(character.isspace() for character in value)
        )
        # Acesso à propriedade também verifica portas inválidas.
        url.port
    except ValueError:
        valid = False
    if not valid:
        raise ConfigurationError(
            "Configure XANO_API_BASE_URL com a origem HTTP(S) do workspace Xano, "
            "sem credenciais, caminho, parâmetros ou fragmento."
        )
    return value


@asynccontextmanager
async def validate_backend_configuration():
    """Interrompe o startup ASGI antes de aceitar requisições sem configuração."""
    get_xano_base_url()
    yield
