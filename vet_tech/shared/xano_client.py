import asyncio
import os
import re
from typing import Any, Optional

import httpx

from vet_tech.shared.config import ConfigurationError, get_xano_base_url

AUTH_API_GROUP = "H62nB-j2"
PET_API_GROUP = "vettech-pets"



_CLINICAL_MESSAGES = ['A consulta foi alterada em outra sessão. Atualize antes de finalizar.', 'A consulta foi alterada em outra sessão. Atualize antes de salvar.', 'A consulta não pode ser iniciada.', 'A operação já foi usada com dados diferentes.', 'An account with this email already exists.', 'As senhas não coincidem.', 'Atendimento realizado não pode ter data futura.', 'Autorização não disponível.', 'CRMV deve conter de 1 a 20 letras ou números, sem espaços internos.', 'Campo inválido.', 'Clínica indisponível.', 'Consulta não disponível.', 'Consulta não está em atendimento.', 'Credenciais inválidas.', 'Data inválida.', 'Data ou página inválida.', 'Datas de exame inconsistentes.', 'Datas inconsistentes da vacina.', 'Doença não disponível.', 'Dose inválida.', 'Escolha data e horário futuros.', 'Escolha um horário entre 08h e 17h.', 'Especialidade indisponível.', 'Espécie indisponível.', 'Estado de autorização inválido.', 'Estado do exame inválido.', 'Este horário já está reservado para o pet ou profissional. Escolha outro horário.', 'Evolução de doença inválida.', 'Fim anterior ao início.', 'Formato inválido.', 'Identidade e estado da consulta não podem ser alterados.', 'Identificação repetida de linha.', 'Informe um CPF válido.', 'Informe uma UF válida para o CRMV.', 'Invalid Credentials.', 'Já existe uma conta com esse CPF ou e-mail.', 'Magic link could not be created. Try again.', 'Magic token has expired. Please request another one.', 'O profissional não atende a espécie selecionada.', 'Operação inválida.', 'Passwords do not match!', 'Pet não disponível.', 'Preencha todos os campos obrigatórios.', 'Resultado exige exame realizado.', 'Retorno anterior ao atendimento.', 'Selecione pelo menos uma espécie e uma especialidade.', 'Senha atual incorreta.', 'Sessão inválida.', 'The token did not match', 'This magic link has already been used. Please request another one.', 'Tipo de medicamento inválido.', 'User not found.', 'Vínculo de registro não pode ser alterado.', 'email is required but not provided', 'magic_token is required but was not provided.']
_VALIDATION_FIELDS = {"dia", "horário", "operação", "pet", "profissional", "motivo", "nome da doença", "descrição", "diagnóstico", "observações", "atendimento", "retorno", "linha", "vacina", "aplicação", "lote", "próxima dose", "nome", "unidade", "frequencia", "via", "início", "fim", "doença", "solicitação", "tipo de exame", "realização", "resultado"}


def _known_domain_message(message: str) -> bool:
    if message in _CLINICAL_MESSAGES:
        return True
    clean = re.sub(r"^(vacinas|medicamentos|doencas|exames), linha [1-9][0-9]{0,2}: ", "", message)
    if clean in _CLINICAL_MESSAGES:
        return True
    for prefix in ("Preencha corretamente: ", "Data inválida: ", "Identificador inválido: "):
        if clean.startswith(prefix) and clean.endswith("."):
            return clean[len(prefix):-1] in _VALIDATION_FIELDS
    return False

class XanoRequestError(Exception):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code

    @property
    def session_invalid(self) -> bool:
        return self.status_code == 401 or str(self) == "Sessão inválida."


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
    tenant = os.getenv("XANO_TENANT", "").strip()
    if tenant:
        headers["X-Tenant"] = tenant
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"

    url = f"{base_url}/api:{api_group}/{endpoint.lstrip('/')}"
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            attempts = 3 if api_group == "vettech-clinical" else 1
            for attempt in range(attempts):
                response = await client.request(
                    method, url, headers=headers,
                    **({"data": form_data, "files": files} if files else {"json": json_payload}),
                )
                if response.status_code != 429 or attempt == attempts - 1:
                    break
                try:
                    delay = min(30, max(1, float(response.headers.get("Retry-After", "20"))))
                except ValueError:
                    delay = 20
                await asyncio.sleep(delay)
    except httpx.TimeoutException:
        raise XanoRequestError("O Xano demorou para responder. Tente novamente.") from None
    except httpx.RequestError:
        raise XanoRequestError("Não foi possível conectar ao Xano.") from None

    if response.status_code == 429:
        raise XanoRequestError(
            "O Xano limitou temporariamente as solicitações. "
            "Aguarde alguns instantes e tente novamente.", status_code=429
        )

    if not response.is_success:
        # Apenas mensagens de domínio conhecidas podem atravessar a fronteira
        # do backend. Erros arbitrários podem conter credenciais ou dados clínicos.
        message = "Não foi possível concluir a solicitação."
        safe_messages = {
            "Sessão inválida.",
            "Pet não disponível.",
            "Acesso clínico não disponível. Verifique a autorização do tutor.",
            "Senha atual incorreta.",
            "As senhas não coincidem.",
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
                if isinstance(candidate, str) and (candidate in safe_messages or _known_domain_message(candidate)):
                    message = candidate
        except ValueError:
            pass
        raise XanoRequestError(str(message), status_code=response.status_code)

    if not response.content:
        return None
    try:
        return response.json()
    except ValueError:
        raise XanoRequestError("O Xano retornou uma resposta inválida.") from None
