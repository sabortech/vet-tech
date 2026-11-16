"""Configurações da conta: sessão privada compartilhada e rascunho isolado."""
import json
import time
from typing import Any

import reflex as rx

from vet_tech.features.auth.state import State as AuthState
from vet_tech.features.navigation.state import NavigationState, TUTOR_DESTINATIONS, VETERINARIAN_DESTINATIONS
from vet_tech.shared.xano_client import AUTH_API_GROUP, XanoRequestError, xano_request

_PASSWORD_RESET = """document.querySelector('#settings-password-form')?.reset();
window.vetTechPasswords?.hideAll('#settings-password-form');"""


class SettingsState(rx.State):
    tab: str = "account"
    nome: str = ""
    telefone: str = ""
    endereco: str = ""
    email: str = ""
    cpf_mascarado: str = ""
    crmv: str = ""
    crmv_uf: str = ""
    account_profile: str = ""
    loaded: bool = False
    loading: bool = False
    saving: bool = False
    message: str = ""
    message_ok: bool = False
    discard_open: bool = False
    has_local_password: bool = True
    password_code_sent: bool = False
    _password_challenge: str = ""
    _password_generation: int = 0
    _snapshot: dict[str, str] = {}
    _session: str = ""
    _pending: str = ""
    _loaded_at: float = 0.0
    _context: tuple[str, str, str, int] = ("", "", "", -1)

    @staticmethod
    def _context_for(auth) -> tuple[str, str, str, int]:
        return (auth._auth_token, auth.profile, auth.identity_id, auth._session_generation)

    def _current(self, auth, context) -> bool:
        return bool(self._session) and context == self._context == self._context_for(auth)

    def _destinations(self):
        if self.account_profile == "veterinario":
            return VETERINARIAN_DESTINATIONS
        return TUTOR_DESTINATIONS if self.account_profile == "tutor" else frozenset()

    @rx.var
    def password_email_hint(self) -> str:
        local, separator, domain = self.email.partition("@")
        return (local[:1] + "***@" + domain) if separator else "seu e-mail cadastrado"

    @rx.var
    def crmv_label(self) -> str:
        return " / ".join(part for part in (self.crmv, self.crmv_uf) if part) or "Não informado"

    @rx.var
    def baseline_json(self) -> str:
        return json.dumps(self._snapshot)

    @rx.var
    def dirty(self) -> bool:
        return self.loaded and self._snapshot != self._draft()

    def _draft(self) -> dict[str, str]:
        draft = {"nome": self.nome.strip(), "telefone": self.telefone.strip()}
        if self.account_profile == "tutor":
            draft["endereco"] = self.endereco.strip()
        return draft

    def clear(self):
        self._clear_password_challenge()
        self.nome = self.telefone = self.endereco = self.email = self.cpf_mascarado = ""
        self.crmv = self.crmv_uf = self.account_profile = ""
        self._context = ("", "", "", -1)
        self.loaded = self.loading = self.saving = self.discard_open = False
        self.message = ""
        self.has_local_password = True
        self.message_ok = False
        self.tab = "account"
        self._session = self._pending = ""
        self._snapshot = {}
        self._loaded_at = 0.0

    def _apply(self, result: Any):
        identity_fields = ("crmv", "crmv_uf") if self.account_profile == "veterinario" else ("endereco", "cpf_mascarado")
        keys = ("nome", "telefone", "email", *identity_fields)
        if not isinstance(result, dict) or not all(isinstance(result.get(k), str) for k in keys):
            raise XanoRequestError("O Xano retornou uma resposta inválida.")
        self.nome, self.telefone, self.email = (result[k] for k in ("nome", "telefone", "email"))
        self.endereco = self.cpf_mascarado = self.crmv = self.crmv_uf = ""
        if self.account_profile == "veterinario":
            self.crmv, self.crmv_uf = result["crmv"], result["crmv_uf"]
        else:
            self.endereco, self.cpf_mascarado = result["endereco"], result["cpf_mascarado"]
        self.has_local_password = result.get("possui_senha", self.has_local_password) is not False
        self._snapshot = self._draft()
        self.loaded = True
        self._loaded_at = time.monotonic()

    def _sync_professional_identity(self, auth):
        if self.account_profile == "veterinario":
            auth.identity_crmv, auth.identity_crmv_uf = self.crmv, self.crmv_uf.upper()
            auth.identity_professional_loaded = True
            auth.identity_professional_loading = auth.identity_professional_error = False

    @rx.event
    async def enter(self):
        auth = await self.get_state(AuthState)
        if not auth.is_authenticated or not auth._auth_token:
            self.clear()
            yield rx.redirect("/login")
            return
        if auth.profile not in ("tutor", "veterinario"):
            self.clear()
            yield rx.redirect("/login")
            return
        token = auth._auth_token
        context = self._context_for(auth)
        if self._context != context:
            self.clear()
            self._session = token
            self._context = context
            self.account_profile = auth.profile
        if self.loading or self.saving:
            return
        self.tab = "account"
        if self.loaded and time.monotonic() - self._loaded_at < 60:
            return
        self.loading = True
        self.message = ""
        yield
        yield SettingsState.load_account

    @rx.event(background=True)
    async def load_account(self):
        async with self:
            auth = await self.get_state(AuthState)
            token = self._session
            context = self._context
            if not self._current(auth, context) or not self.loading:
                return
        result = None
        error = None
        try:
            result = await xano_request("GET", AUTH_API_GROUP, context[1] + "/account", auth_token=token)
        except XanoRequestError as caught:
            error = caught
        expired = False
        async with self:
            auth = await self.get_state(AuthState)
            if not self._current(auth, context):
                return
            try:
                if error is not None:
                    if error.session_invalid:
                        expired = True
                    else:
                        self.message = str(error)
                else:
                    self._apply(result)
                    self._sync_professional_identity(auth)
            except XanoRequestError as caught:
                self.message = str(caught)
            finally:
                self.loading = False
        if expired:
            yield AuthState.logout

    @rx.event
    def edit_nome(self, value: str):
        if self.loaded and not self.saving:
            self.nome = value
            self.message = ""

    @rx.event
    def edit_telefone(self, value: str):
        if self.loaded and not self.saving:
            self.telefone = value
            self.message = ""

    @rx.event
    def edit_endereco(self, value: str):
        if self.loaded and not self.saving:
            self.endereco = value
            self.message = ""

    @rx.event
    def cancel(self):
        if not self.saving:
            for key, value in self._snapshot.items():
                setattr(self, key, value)
            self.message = ""

    @rx.event
    async def save(self, form_data: dict[str, Any]):
        if self.saving or self.loading or not self.loaded or not self.dirty:
            return
        auth = await self.get_state(AuthState)
        token = auth._auth_token
        context = self._context
        if not self._current(auth, context):
            yield AuthState.logout
            return
        draft = self._draft()
        if not all(draft.values()):
            self.message = "Preencha todos os campos obrigatórios."
            self.message_ok = False
            return
        self.saving = True
        self.message = ""
        yield
        try:
            result = await xano_request("PATCH", AUTH_API_GROUP, context[1] + "/account", auth_token=token, json_payload=draft)
            if self._current(auth, context):
                self._apply(result)
                self._sync_professional_identity(auth)
                auth.identity_name = self.nome
                self.message = "Dados atualizados com sucesso."
                self.message_ok = True
        except XanoRequestError as error:
            if self._current(auth, context):
                self.message_ok = False
                if error.session_invalid:
                    yield AuthState.logout
                else:
                    self.message = str(error)
        finally:
            if self._current(auth, context):
                self.saving = False

    def _clear_password_challenge(self):
        self.password_code_sent = False
        self._password_challenge = ""
        self._password_generation += 1

    @rx.event
    def cancel_password_challenge(self):
        self._clear_password_challenge()
        self.saving = False
        self.message = ""
        return rx.call_script(_PASSWORD_RESET)

    @rx.event
    async def request_password_code(self, form_data: dict[str, Any]):
        if self.saving:
            return
        auth = await self.get_state(AuthState)
        context = self._context
        if not self._current(auth, context):
            yield AuthState.logout
            return
        current = str(form_data.get("current_password", ""))
        if not current:
            self.message = "Informe sua senha atual."
            self.message_ok = False
            return
        generation = self._password_generation
        self.saving = True
        self.message = ""
        self.message_ok = False
        yield
        try:
            result = await xano_request("POST", AUTH_API_GROUP, context[1] + "/password/request-code", auth_token=context[0], json_payload={"current_password": current})
            if not self._current(auth, context) or generation != self._password_generation:
                return
            if not isinstance(result, dict) or result.get("ok") is not True or not isinstance(result.get("challenge_id"), str) or not result["challenge_id"]:
                raise XanoRequestError("Resposta de verificação inválida.")
            self._password_challenge = result["challenge_id"]
            self.password_code_sent = True
            self.message = "Solicitação recebida. Confira seu e-mail e o spam. O código vale por 10 minutos."
            self.message_ok = True
            yield rx.call_script(_PASSWORD_RESET)
        except XanoRequestError as error:
            if self._current(auth, context) and generation == self._password_generation:
                if error.session_invalid:
                    yield AuthState.logout
                else:
                    self.message = str(error)
                    yield rx.call_script(_PASSWORD_RESET)
        finally:
            if self._current(auth, context) and generation == self._password_generation:
                self.saving = False

    @rx.event
    async def change_password(self, form_data: dict[str, Any]):
        if self.saving:
            return
        auth = await self.get_state(AuthState)
        token = auth._auth_token
        context = self._context
        if not self._current(auth, context):
            yield AuthState.logout
            return
        payload = {key: str(form_data.get(key, "")) for key in ("current_password", "new_password", "password_confirmation")}
        self.message_ok = False
        if not all(payload.values()):
            self.message = "Preencha todos os campos obrigatórios."
            return
        if payload["new_password"] != payload["password_confirmation"]:
            self.message = "As senhas não coincidem."
            return
        code = str(form_data.get("code", "")).strip()
        if not self._password_challenge or len(code) != 6 or not code.isascii() or not code.isdecimal():
            self.message = "Solicite e informe o código de seis dígitos enviado ao seu e-mail."
            return
        payload.update(challenge_id=self._password_challenge, code=code)
        generation = self._password_generation
        self.saving = True
        self.message = ""
        yield
        try:
            result = await xano_request("POST", AUTH_API_GROUP, context[1] + "/password", auth_token=token, json_payload=payload)
            if self._current(auth, context) and generation == self._password_generation:
                if not isinstance(result, dict) or result.get("success") is not True:
                    raise XanoRequestError("Não foi possível confirmar a alteração da senha.")
                yield rx.call_script(_PASSWORD_RESET)
                await auth.logout()
                auth.login_message = "Senha atualizada. Entre novamente com sua nova senha."
                auth.login_message_success = True
                yield rx.redirect("/login")
        except XanoRequestError as error:
            if self._current(auth, context) and generation == self._password_generation:
                if error.session_invalid:
                    yield AuthState.logout
                else:
                    self.message = str(error)
                    yield rx.call_script(_PASSWORD_RESET)
        finally:
            if self._current(auth, context) and generation == self._password_generation:
                self.saving = False

    @rx.event
    def request_action(self, action: str):
        if self.saving:
            return
        allowed = {"account", "security", "preferences", "logout", "history", *self._destinations()}
        if self.account_profile == "tutor":
            allowed.add("change_pet")
        if action not in allowed:
            return
        if self.dirty:
            self._pending = action
            self.discard_open = True
            return
        return self._execute(action)

    @rx.event
    def request_navigation(self, destination: str):
        """The browser guard detected unsaved live inputs, possibly before a delta."""
        if self.saving or destination not in self._destinations():
            return
        self._pending = destination
        self.discard_open = True

    def _execute(self, action: str):
        self._clear_password_challenge()
        self.message = ""
        self.message_ok = False
        if action in {"account", "security", "preferences"}:
            self.tab = action
            return rx.call_script(_PASSWORD_RESET)
        if action == "logout":
            return AuthState.logout
        if action == "change_pet":
            return [NavigationState.close_drawer, AuthState.show_pet_picker]
        if action == "history":
            return rx.call_script("window.vetTechLeaveHistory?.();")
        return [NavigationState.close_drawer, rx.redirect(action)]

    @rx.event
    def keep_editing(self):
        self.discard_open = False
        self._pending = ""
        return rx.call_script('requestAnimationFrame(() => window.__vetTechNavigationTrigger?.focus());')

    @rx.event
    def discard(self):
        action = self._pending
        self.cancel()
        self._pending = ""
        self.discard_open = False
        return self._execute(action)

    @rx.event
    def history_back(self):
        # The browser checked the live inputs; do not wait for an input delta.
        self._pending = "history"
        self.discard_open = True

    @rx.event
    async def define_first_password(self):
        auth = await self.get_state(AuthState)
        if not self._current(auth, self._context) or self.has_local_password:
            return
        auth._clear_session()
        auth.recovery_step = "email"
        self.clear()
        yield rx.redirect("/login")
