"""Ponte de eventos do chat: credenciais e contexto ficam no State privado."""

import json
import os
from uuid import UUID
from typing import Any

import reflex as rx

from vet_tech.shared.n8n_client import ChatReply, failure, request_chat, trim_history
from vet_tech.shared.direct_client import direct_request
from vet_tech.shared.support_client import SupportConfigurationError, support_request
from vet_tech.shared.xano_client import XanoRequestError, xano_request, PET_API_GROUP


def _result_event(request_id: str, conversation_id: str, result: ChatReply):
    detail = {"request_id": request_id, "conversation_id": conversation_id,
              "ok": result.ok, "reply": result.reply,
              "error": None if result.ok else {"code": result.error_code},
              "handoff": bool(result.handoff_reason)}
    return rx.call_script(
        "window.dispatchEvent(new CustomEvent('vettech:chat-response', {detail:"
        + json.dumps(detail, ensure_ascii=True) + "}));"
    )


def _valid_id(value) -> bool:
    try:
        return isinstance(value, str) and str(UUID(value)) == value
    except (ValueError, TypeError, AttributeError):
        return False


class SupportChatMixin(rx.State, mixin=True):
    _support_conversation: str = ""
    _support_history: list[dict[str, str]] = []
    _support_request: str = ""
    _support_generation: int = 0
    _support_session: int = -1
    _support_transcript: list[dict[str, str]] = []
    _support_handoff_reason: str = ""
    _support_handoff_context: list[dict[str, str]] = []
    _direct_thread: int = 0
    _support_human_ticket: int = 0
    _support_human_busy: bool = False

    def _reset_support_chat(self):
        self._support_conversation = ""
        self._support_history = []
        self._support_request = ""
        self._support_generation += 1
        self._support_session = -1
        self._support_transcript = []
        self._support_handoff_reason = ""
        self._support_handoff_context = []
        self._direct_thread = 0
        self._support_human_ticket = 0
        self._support_human_busy = False

    def _support_session_key(self) -> str:
        return f"{self.profile}:{self.identity_id}" if self.is_authenticated and self._auth_token else ""

    @rx.event(background=True)
    async def support_chat(self, form_data: dict[str, Any]):
        raw = form_data.get("payload", "")
        if not isinstance(raw, str) or len(raw) > 10000:
            return
        try:
            data = json.loads(raw)
        except (ValueError, TypeError):
            return
        if not isinstance(data, dict) or not _valid_id(data.get("conversation_id")):
            return
        conversation_id = data["conversation_id"]
        request_id = data.get("request_id", "")
        action = data.get("action")
        if action in ("direct_veterinarians", "direct_tutors", "direct_list", "direct_start", "direct_get", "direct_send", "direct_edit", "direct_delete"):
            async for event in self._direct_chat_operation(data):
                yield event
            return
        if action in ("support_pets", "support_list", "support_get", "support_create", "support_claim", "support_send", "support_close", "support_edit", "support_delete"):
            async for event in self._support_human_operation(data):
                yield event
            return
        async with self:
            # A chave do DOM só evita eventos atrasados: nunca identifica ou autoriza.
            if data.get("session_key") != self._support_session_key():
                return
            if action == "open":
                self._reset_support_chat()
                self._support_conversation = conversation_id
                self._support_session = self._session_generation
                return
            if action == "close":
                if conversation_id == self._support_conversation:
                    self._reset_support_chat()
                return
            if action != "message" or not _valid_id(request_id):
                return
            text = data.get("message")
            if not isinstance(text, str) or not 1 <= len(text.strip()) <= 1000:
                yield _result_event(request_id, conversation_id, failure("INVALID_REQUEST"))
                return
            if (conversation_id != self._support_conversation
                    or self._support_session != self._session_generation):
                return
            if self._support_human_ticket or self._direct_thread:
                yield _result_event(request_id, conversation_id, failure("INVALID_REQUEST"))
                return
            if self._support_request:
                yield _result_event(request_id, conversation_id, failure())
                return
            self._support_request = request_id
            generation, session, token = self._support_generation, self._session_generation, self._auth_token
            authenticated = bool(self.is_authenticated and token)
            user = {"authenticated": authenticated,
                    "name": self.identity_name if authenticated else None,
                    "role": self.profile if authenticated else "visitante"}
            previous = [dict(row) for row in self._support_history]
        result = await request_chat(request_id=request_id, conversation_id=conversation_id,
                                    message=text.strip(), user=user, history=previous, auth_token=token)
        async with self:
            if (generation != self._support_generation or session != self._session_generation
                    or token != self._auth_token or conversation_id != self._support_conversation
                    or request_id != self._support_request):
                return
            self._support_request = ""
            if result.session_invalid and authenticated:
                self._expire_session()
            elif result.ok:
                safe_text = text.strip()
                for credential in (token, os.getenv("N8N_CHAT_WEBHOOK_SECRET", ""), os.getenv("SUPPORT_CHAT_BRIDGE_SECRET", "")):
                    if credential:
                        safe_text = safe_text.replace(credential, "[credencial omitida]")
                pair = [
                    {"role": "user", "content": safe_text},
                    {"role": "assistant", "content": result.reply},
                ]
                self._support_history = trim_history(previous + pair)
                self._support_transcript += pair
                if result.handoff_reason and authenticated and self.profile == "tutor":
                    self._support_handoff_reason = result.handoff_reason
                elif result.handoff_reason:
                    result = ChatReply(True, result.reply)
                if self._support_handoff_reason:
                    self._support_handoff_context = [dict(row) for row in self._support_transcript]
            yield _result_event(request_id, conversation_id, result)

    async def _support_human_operation(self, data):
        action = data["action"].removeprefix("support_")
        rid, cid = data.get("request_id"), data.get("conversation_id")
        if not _valid_id(rid):
            return
        async with self:
            if (not self.is_authenticated or not self._auth_token
                    or data.get("session_key") != self._support_session_key()
                    or cid != self._support_conversation
                    or self._support_session != self._session_generation
                    or self._support_human_busy):
                return
            payload = {"action": action}
            if action in ("get", "claim", "send", "close", "edit", "delete"):
                ticket = data.get("ticket_id")
                if type(ticket) is not int or ticket < 1:
                    return
                payload["ticket_id"] = ticket
            if action in ("edit", "delete"):
                if (not _valid_id(data.get("operation_id")) or not _valid_id(data.get("message_id"))
                        or type(data.get("expected_revision")) is not int or data["expected_revision"] < 0):
                    return
                payload.update(operation_id=data["operation_id"], message_id=data["message_id"], expected_revision=data["expected_revision"])
                if action == "edit":
                    text = data.get("message")
                    if not isinstance(text, str) or not 1 <= len(text.strip()) <= 1000:
                        return
                    payload["message"] = text.strip()
            if action in ("send", "close"):
                if not _valid_id(data.get("operation_id")):
                    return
                value = data.get("message" if action == "send" else "reason")
                if not isinstance(value, str) or not 1 <= len(value.strip()) <= 1000:
                    return
                payload.update(operation_id=data["operation_id"])
                payload["message" if action == "send" else "reason"] = value.strip()
                if action == "close":
                    if data.get("expected_status") not in ("aguardando", "em_atendimento"):
                        return
                    expected_status = data["expected_status"]
                    allowed = ((self.profile == "tutor" and expected_status == "aguardando")
                               or (self.profile == "veterinario" and expected_status == "em_atendimento"))
                    if not allowed:
                        detail = {"request_id": rid, "conversation_id": cid, "action": action,
                                  "ok": False, "retryable": False,
                                  "error": "Somente o veterinário responsável pode encerrar o atendimento em andamento."}
                        yield rx.call_script("window.dispatchEvent(new CustomEvent('vettech:support-response', {detail:"
                                             + json.dumps(detail, ensure_ascii=True) + "}));")
                        return
                    payload["expected_status"] = expected_status
            if "read_through" in data:
                if action not in ("get", "send", "close") or not _valid_id(data["read_through"]):
                    return
                payload["read_through"] = data["read_through"]
                if "read_revision" in data:
                    if type(data["read_revision"]) is not int or data["read_revision"] < 0:
                        return
                    payload["read_revision"] = data["read_revision"]
            if action == "create":
                if (self.profile != "tutor" or not self._support_handoff_reason
                        or not self._support_handoff_context or data.get("consent") is not True
                        or type(data.get("pet_id")) is not int or self._support_request):
                    return
                payload.update(pet_id=data["pet_id"], consent=True, conversation_id=cid,
                               reason=self._support_handoff_reason,
                               context=[dict(row) for row in self._support_handoff_context])
            token, profile, session, generation = self._auth_token, self.profile, self._session_generation, self._support_generation
            self._support_human_busy = True
        result, error, session_invalid = {}, "", False
        retryable = True
        try:
            if action == "pets":
                if profile != "tutor":
                    result = {"pets": []}
                else:
                    pets = await xano_request("GET", PET_API_GROUP, "pets", auth_token=token)
                    result = {"pets": [{"id": row["id"], "name": row["nome"]} for row in pets]}
            else:
                result = await support_request(profile, token, payload)
        except SupportConfigurationError as caught:
            error = str(caught)
            retryable = False
        except XanoRequestError as caught:
            session_invalid = caught.session_invalid
            if str(caught) in ("A mensagem foi alterada. Atualize a conversa antes de tentar novamente.",
                               "O prazo de 10 minutos para editar ou apagar esta mensagem terminou."):
                error = str(caught)
                retryable = False
            else:
                error = "Sua sessão expirou. Entre novamente." if caught.session_invalid else "Não foi possível concluir o atendimento. Atualize ou tente novamente."
        async with self:
            if (session != self._session_generation or token != self._auth_token
                    or generation != self._support_generation or cid != self._support_conversation):
                return
            self._support_human_busy = False
            if session_invalid:
                self._expire_session()
                return
            if not error and isinstance(result.get("ticket"), dict):
                self._direct_thread = 0
                self._support_human_ticket = int(result["ticket"]["id"])
                self._support_generation += 1
                self._support_request = ""
            detail = {"request_id": rid, "conversation_id": cid, "action": action,
                      "ok": not bool(error), "error": error, "retryable": retryable, **result}
            yield rx.call_script("window.dispatchEvent(new CustomEvent('vettech:support-response', {detail:"
                                 + json.dumps(detail, ensure_ascii=True) + "}));")

    async def _direct_chat_operation(self, data):
        action = data["action"].removeprefix("direct_")
        rid, cid = data.get("request_id"), data.get("conversation_id")
        if not _valid_id(rid):
            return
        async with self:
            if (not self.is_authenticated or not self._auth_token
                    or self.profile not in ("tutor", "veterinario")
                    or data.get("session_key") != self._support_session_key()
                    or cid != self._support_conversation
                    or self._support_session != self._session_generation
                    or self._support_human_busy):
                return
            if (action == "tutors" and self.profile != "veterinario") or (action == "veterinarians" and self.profile != "tutor"):
                return
            payload = {"action": action}
            if action in ("get", "send", "edit", "delete", "start"):
                key = ("veterinario_id" if self.profile == "tutor" else "tutor_id") if action == "start" else "thread_id"
                if type(data.get(key)) is not int or data[key] < 1:
                    return
                payload[key] = data[key]
            if action in ("tutors", "veterinarians", "list"):
                page = data.get("page", 1)
                search = data.get("search", "")
                if type(page) is not int or not 1 <= page <= 10000 or not isinstance(search, str) or len(search) > 100:
                    return
                payload.update(page=page, search=search.strip())
            if action in ("send", "edit", "delete"):
                if not _valid_id(data.get("operation_id")):
                    return
                payload["operation_id"] = data["operation_id"]
            if action in ("send", "edit"):
                text = data.get("message")
                if not isinstance(text, str) or not 1 <= len(text.strip()) <= 1000:
                    return
                payload["message"] = text.strip()
            if action in ("edit", "delete"):
                if not _valid_id(data.get("message_id")) or type(data.get("expected_revision")) is not int or data["expected_revision"] < 0:
                    return
                payload.update(message_id=data["message_id"], expected_revision=data["expected_revision"])
            if "read_through" in data:
                if action not in ("get", "send") or not _valid_id(data["read_through"]):
                    return
                revision = data.get("read_revision", 0)
                if type(revision) is not int or revision < 0:
                    return
                payload.update(read_through=data["read_through"], read_revision=revision)
            token, profile = self._auth_token, self.profile
            session, generation = self._session_generation, self._support_generation
            self._support_human_busy = True
        result, error, expired = {}, "", False
        try:
            result = await direct_request(profile, token, payload)
        except XanoRequestError as caught:
            expired = caught.session_invalid
            error = "Sua sessão expirou. Entre novamente." if expired else str(caught)
        async with self:
            if (session != self._session_generation or token != self._auth_token
                    or generation != self._support_generation or cid != self._support_conversation):
                return
            self._support_human_busy = False
            if expired:
                self._expire_session()
                return
            if not error and isinstance(result.get("thread"), dict):
                self._direct_thread = int(result["thread"]["id"])
                self._support_human_ticket = 0
                self._support_generation += 1
                self._support_request = ""
            detail = {"request_id": rid, "conversation_id": cid, "action": action,
                      "ok": not bool(error), "error": error, **result}
            yield rx.call_script("window.dispatchEvent(new CustomEvent('vettech:direct-response', {detail:"
                                 + json.dumps(detail, ensure_ascii=True) + "}));")
