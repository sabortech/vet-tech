"""Teste real do assistente como visitante, sem imprimir conteúdo ou credenciais."""

import asyncio
import json
from pathlib import Path
import sys
import time
from uuid import uuid4

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from vet_tech.shared.n8n_client import request_chat


async def main() -> int:
    load_dotenv(PROJECT_ROOT / ".env")
    started = time.monotonic()
    result = await request_chat(
        request_id=str(uuid4()),
        conversation_id=str(uuid4()),
        message="Olá! Como uso o Vet Tech?",
        user={"authenticated": False, "name": None, "role": "visitante"},
        history=[],
    )
    print(json.dumps({
        "workflow_success": result.ok,
        "error_code": result.error_code,
        "elapsed_seconds": round(time.monotonic() - started, 2),
    }))
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
