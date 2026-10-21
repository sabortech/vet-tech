from typing import Any, Optional

import httpx

from vet_tech.shared.config import ConfigurationError, get_xano_base_url

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
    try:
        base_url = get_xano_base_url()
    except ConfigurationError as error:
        raise XanoRequestError(str(error)) from None

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
    except httpx.TimeoutException:
        raise XanoRequestError("O Xano demorou para responder. Tente novamente.") from None
    except httpx.RequestError:
        raise XanoRequestError("Não foi possível conectar ao Xano.") from None

    if not response.is_success:
        # Apenas mensagens de domínio conhecidas podem atravessar a fronteira
        # do backend. Erros arbitrários podem conter credenciais ou dados clínicos.
        message = "Não foi possível concluir a solicitação."
        safe_messages = {
            "Preencha todos os campos obrigatórios.",
            "Já existe uma conta com esse CPF ou e-mail.",
            "E-mail já cadastrado.",
            "CPF já cadastrado.",
            "Informe um CPF válido.",
            "Credenciais inválidas.",
            "A espécie informada não existe.",
            "A raça informada não existe.",
            "A raça informada não pertence à espécie selecionada.",
        }
        try:
            body = response.json()
            if isinstance(body, dict):
                candidate = body.get("message") or body.get("error")
                if isinstance(candidate, str) and candidate in safe_messages:
                    message = candidate
        except ValueError:
            pass
        raise XanoRequestError(str(message))

    if not response.content:
        return None
    try:
        return response.json()
    except ValueError:
        raise XanoRequestError("O Xano retornou uma resposta inválida.") from None
