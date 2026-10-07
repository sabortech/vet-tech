import os
from typing import Any, Optional

import httpx

AUTH_API_GROUP = "H62nB-j2"
PET_API_GROUP = "vettech-pets"


class XanoRequestError(Exception):
    pass


async def xano_request(
    method: str,
    api_group: str,
    endpoint: str,
    auth_token: str = "",
    json_payload: Optional[dict[str, Any]] = None,
    form_data: Optional[dict[str, str]] = None,
    files: Optional[dict[str, tuple[str, bytes, str]]] = None,
) -> Any:
    base_url = os.getenv(
        "XANO_API_BASE_URL",
        "https://x8ki-letl-twmt.n7.xano.io",
    ).rstrip("/")
    if not base_url:
        raise XanoRequestError("Configure XANO_API_BASE_URL para conectar ao Xano.")

    headers = {}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"

    url = f"{base_url}/api:{api_group}/{endpoint.lstrip('/')}"
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            if files:
                response = await client.request(
                    method,
                    url,
                    headers=headers,
                    data=form_data,
                    files=files,
                )
            else:
                response = await client.request(
                    method,
                    url,
                    headers=headers,
                    json=json_payload,
                )
    except httpx.TimeoutException as error:
        raise XanoRequestError("O Xano demorou para responder. Tente novamente.") from error
    except httpx.RequestError as error:
        raise XanoRequestError("Não foi possível conectar ao Xano.") from error

    if not response.is_success:
        message = "Não foi possível concluir a solicitação."
        try:
            body = response.json()
            if isinstance(body, dict):
                message = body.get("message") or body.get("error") or message
        except ValueError:
            pass
        raise XanoRequestError(str(message))

    if not response.content:
        return None
    return response.json()
