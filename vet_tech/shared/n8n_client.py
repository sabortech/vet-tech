"""Transporte privado do assistente. Não registra payloads ou credenciais."""

import asyncio
import os
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlsplit

import httpx

GENERIC_ERROR = "Não consegui responder agora. Tente novamente."
SESSION_ERROR = "Sua sessão expirou ou não pôde ser confirmada. Entre novamente no Vet Tech para consultar os dados dos seus pets."
TIMEOUT_SECONDS = 60
MAX_REPLY = 12000


@dataclass(frozen=True)
class ChatReply:
    ok: bool
    reply: str
    error_code: str = ""

    @property
    def session_invalid(self) -> bool:
        return self.error_code == "SESSION_INVALID"


def failure(code: str = "AI_UNAVAILABLE") -> ChatReply:
    return ChatReply(False, SESSION_ERROR if code == "SESSION_INVALID" else GENERIC_ERROR, code)


def _configuration() -> tuple[str, str]:
    value = os.getenv("N8N_CHAT_WEBHOOK_URL", "").strip()
    secret = os.getenv("N8N_CHAT_WEBHOOK_SECRET", "").strip()
    try:
        url = urlsplit(value)
        valid = (url.scheme == "https" and url.hostname and not url.username
                 and not url.password and not url.query and not url.fragment
                 and not any(c.isspace() for c in value) and bool(secret)
                 and not any(c in secret for c in "\r\n"))
        url.port
        secret.encode("ascii")
    except (ValueError, UnicodeError):
        valid = False
    if not valid:
        raise ValueError("Configuração do assistente indisponível.")
    return value, secret


def trim_history(items: list[dict[str, str]]) -> list[dict[str, str]]:
    """Contexto anterior, limitado independentemente do histórico visual."""
    result = []
    budget = 20000
    for item in reversed(items[-20:]):
        content = item.get("content", "")
        if item.get("role") not in ("user", "assistant") or not isinstance(content, str):
            continue
        if len(content) > budget:
            break
        result.append({"role": item["role"], "content": content})
        budget -= len(content)
    return list(reversed(result))


def _parse(response: httpx.Response, request_id: str, conversation_id: str,
           secrets: tuple[str, ...]) -> ChatReply:
    if len(response.content) > 131072:
        return failure()
    try:
        body = response.json()
    except ValueError:
        return failure("CONFIGURATION_ERROR" if response.status_code in (401, 403) else "AI_UNAVAILABLE")
    if (not isinstance(body, dict) or body.get("request_id") != request_id
            or body.get("conversation_id") != conversation_id):
        return failure()
    reply = body.get("reply")
    if (not isinstance(reply, str) or not reply.strip() or len(reply) > MAX_REPLY
            or any(secret and secret in reply for secret in secrets)):
        return failure()
    if response.status_code == 200 and body.get("ok") is True and body.get("error") is None:
        return ChatReply(True, reply.strip())
    error = body.get("error")
    if body.get("ok") is not False or not isinstance(error, dict):
        return failure()
    code = error.get("code")
    expected = {"INVALID_REQUEST": (400,), "SESSION_INVALID": (401, 200),
                "XANO_UNAVAILABLE": (503,), "AI_UNAVAILABLE": (503,)}
    if not isinstance(code, str) or code not in expected or response.status_code not in expected[code]:
        return failure()
    return ChatReply(False, reply.strip(), code)


async def request_chat(*, request_id: str, conversation_id: str, message: str,
                       user: dict[str, Any], history: list[dict[str, str]],
                       auth_token: str = "") -> ChatReply:
    try:
        url, secret = _configuration()
    except ValueError:
        return failure("CONFIGURATION_ERROR")
    authenticated = bool(user.get("authenticated") and auth_token)
    identity = {"authenticated": authenticated,
                "name": user.get("name") if authenticated else None,
                "role": user.get("role") if authenticated else "visitante"}
    if authenticated and identity["role"] not in ("tutor", "veterinario"):
        return failure("SESSION_INVALID")
    headers = {"X-VetTech-Secret": secret, "Content-Type": "application/json"}
    if authenticated:
        headers["X-VetTech-User-Token"] = auth_token
    # Não repetir credenciais conhecidas em texto livre/contexto, mesmo se coladas por engano.
    def redact(text: str) -> str:
        for credential in (secret, auth_token):
            if credential:
                text = text.replace(credential, "[credencial omitida]")
        return text
    if isinstance(identity["name"], str):
        identity["name"] = redact(identity["name"])
    payload = {"request_id": request_id, "conversation_id": conversation_id,
               "message": redact(message), "user": identity,
               "history": [{"role": row["role"], "content": redact(row["content"])}
                           for row in trim_history(history)]}
    try:
        # wait_for limita o tempo total, incluindo conexão e leitura lenta.
        async def execute():
            async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS, follow_redirects=False) as client:
                return await client.post(url, headers=headers, json=payload)
        response = await asyncio.wait_for(execute(), timeout=TIMEOUT_SECONDS)
    except (httpx.RequestError, asyncio.TimeoutError, ValueError):
        return failure()
    return _parse(response, request_id, conversation_id, (secret, auth_token))
