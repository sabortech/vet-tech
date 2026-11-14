"""Authenticated support operations; the creation credential never reaches the browser."""

import os
from typing import Any

from vet_tech.shared.xano_client import XanoRequestError, xano_request


class SupportConfigurationError(XanoRequestError):
    """Configuração local ausente; repetir a operação não resolve."""


async def support_request(profile: str, token: str, payload: dict[str, Any]):
    if profile not in ("tutor", "veterinario") or not token:
        raise XanoRequestError("Sessão inválida.", 401)
    body = {"payload": payload}
    if payload.get("action") == "create":
        secret = os.getenv("SUPPORT_CHAT_BRIDGE_SECRET", "")
        if not secret:
            raise SupportConfigurationError("O encaminhamento está indisponível por configuração. Tente mais tarde.")
        body["bridge_key"] = secret
    result = await xano_request("POST", "vettech-support", f"{profile}/chat",
                                auth_token=token, json_payload=body)
    if not isinstance(result, dict) or not ("ticket" in result or "tickets" in result):
        raise XanoRequestError("Resposta do atendimento inválida.")
    return result
