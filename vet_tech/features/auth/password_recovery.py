"""Recuperação por código, sem sessão de acesso ou segredos persistidos no cliente."""
from typing import Any
import reflex as rx
from vet_tech.shared.xano_client import AUTH_API_GROUP, XanoRequestError, xano_request

RESET_RECOVERY_FORM = "document.querySelector('#password-recovery-form')?.reset();"


class PasswordRecoveryMixin(rx.State, mixin=True):
    recovery_step: str = ""
    recovery_email: str = ""
    recovery_message: str = ""
    recovery_busy: bool = False
    _recovery_generation: int = 0
    _recovery_challenge: str = ""
    _recovery_token: str = ""

    def _clear_password_recovery(self):
        self._recovery_generation += 1
        self.recovery_step = self.recovery_email = self.recovery_message = ""
        self._recovery_challenge = self._recovery_token = ""
        self.recovery_busy = False

    @rx.event
    def start_password_recovery(self):
        if self.is_authenticated or self.is_busy:
            return
        self._clear_password_recovery()
        self.recovery_step = "email"
        return rx.call_script("document.querySelector('input[name=password]')?.value && (document.querySelector('input[name=password]').value = '');")

    @rx.event
    def cancel_password_recovery(self):
        self._clear_password_recovery()
        return rx.call_script(RESET_RECOVERY_FORM)

    @rx.event
    def recovery_back(self):
        step = self.recovery_step
        self._clear_password_recovery()
        if step in ("code", "password"):
            self.recovery_step = "email"
        return rx.call_script(RESET_RECOVERY_FORM)

    @rx.event
    async def submit_password_recovery(self, form_data: dict[str, Any]):
        if self.recovery_busy or self.is_authenticated or self.recovery_step not in ("email", "code", "password"):
            return
        step = self.recovery_step
        generation = self._recovery_generation
        session = self._session_generation
        if step == "email":
            email = str(form_data.get("email", "")).strip().lower()
            if not email:
                self.recovery_message = "Informe seu e-mail."
                return
            payload, endpoint = {"email": email}, "request"
        elif step == "code":
            code = str(form_data.get("code", "")).strip()
            if len(code) != 6 or not code.isascii() or not code.isdecimal() or not self._recovery_challenge:
                self.recovery_message = "Informe o código de seis dígitos."
                return
            payload, endpoint = {"challenge_id": self._recovery_challenge, "code": code}, "verify"
        else:
            password = str(form_data.get("new_password", ""))
            confirmation = str(form_data.get("password_confirmation", ""))
            if not password or password != confirmation or not self._recovery_token:
                self.recovery_message = "Preencha a nova senha e confirme com o mesmo valor."
                return
            payload, endpoint = {"reset_token": self._recovery_token, "new_password": password, "password_confirmation": confirmation}, "complete"
        self.recovery_busy = True
        self.recovery_message = ""
        yield
        try:
            result = await xano_request("POST", AUTH_API_GROUP, "acesso/password-reset/" + endpoint, json_payload=payload)
            if generation != self._recovery_generation or session != self._session_generation or self.is_authenticated:
                return
            if not isinstance(result, dict) or result.get("ok") is not True:
                raise XanoRequestError("Não foi possível concluir. Tente novamente.")
            if step == "email":
                challenge = result.get("challenge_id")
                if not isinstance(challenge, str) or not challenge:
                    raise XanoRequestError("Resposta de verificação inválida.")
                self.recovery_email = email
                self._recovery_challenge = challenge
                self.recovery_step = "code"
                self.recovery_message = "Se houver uma conta para este e-mail, enviaremos um código. Verifique também o spam."
            elif step == "code":
                token = result.get("reset_token")
                if not isinstance(token, str) or not token:
                    raise XanoRequestError("Resposta de verificação inválida.")
                self._recovery_token = token
                self._recovery_challenge = ""
                self.recovery_step = "password"
                self.recovery_message = "E-mail confirmado. Defina sua nova senha."
            else:
                self._clear_password_recovery()
                self.login_message = "Senha atualizada. Entre com sua nova senha."
                self.login_message_success = True
            yield rx.call_script(RESET_RECOVERY_FORM)
        except XanoRequestError:
            if generation == self._recovery_generation and session == self._session_generation:
                # Não reproduzir detalhes do provedor ou da resolução da conta.
                self.recovery_message = "Não foi possível concluir. Confira os dados ou solicite outro código."
                yield rx.call_script(RESET_RECOVERY_FORM)
        finally:
            if generation == self._recovery_generation and session == self._session_generation:
                self.recovery_busy = False

    @rx.event
    async def resend_recovery_code(self):
        if self.recovery_step != "code" or self.recovery_busy or not self.recovery_email:
            return
        self.recovery_step = "email"
        self._recovery_challenge = ""
        async for event in self.submit_password_recovery({"email": self.recovery_email}):
            yield event
