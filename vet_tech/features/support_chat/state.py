"""Ponte de eventos do chat: credenciais e contexto ficam no State privado."""

import json
from uuid import UUID
from typing import Any

import reflex as rx

from vet_tech.shared.n8n_client import ChatReply, failure, request_chat, trim_history


def _result_event(request_id: str, conversation_id: str, result: ChatReply):
    detail = {"request_id": request_id, "conversation_id": conversation_id,
              "ok": result.ok, "reply": result.reply,
              "error": None if result.ok else {"code": result.error_code}}
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

    def _reset_support_chat(self):
        self._support_conversation = ""
        self._support_history = []
        self._support_request = ""
        self._support_generation += 1
        self._support_session = -1

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
                self._support_history = trim_history(previous + [
                    {"role": "user", "content": text.strip()},
                    {"role": "assistant", "content": result.reply},
                ])
            yield _result_event(request_id, conversation_id, result)
