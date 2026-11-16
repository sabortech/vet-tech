"""Formulário público de recuperação dentro da apresentação existente do login."""
import reflex as rx
from vet_tech.features.auth.state import State
from vet_tech.components.password_input import password_control


def recovery_input(label: str, name: str, kind: str, autocomplete: str):
    field_id = "recovery-" + name
    control = rx.input(
        id=field_id, name=name, type=kind, required=True,
        disabled=State.recovery_busy, width="100%", height="44px",
        background="var(--vt-field-bg)", color="var(--vt-text)",
        custom_attrs={"autoComplete": autocomplete, **({"inputMode": "numeric", "pattern": "[0-9]{6}", "maxLength": "6"} if name == "code" else {})},
    )
    if kind == "password":
        control = password_control(control, field_id, label, disabled=State.recovery_busy)
    return rx.vstack(
        rx.el.label(label, html_for=field_id), control,
        align="stretch", spacing="1", width="100%",
    )


def password_recovery():
    return rx.vstack(
        rx.vstack(
            rx.text("Vet Tech Team", font_family="Nunito", font_size="24px", font_weight="700", color="var(--vt-text)"),
            rx.image(src="/consultation-pdf/mascote-v.png", alt="Tartaruga Vet Tech com os braços em V", width="132px", height="96px", object_fit="contain"),
            align="center", spacing="1",
        ),
        rx.heading("Recupere seu acesso", size="6", color="var(--vt-text)"),
        rx.text("Confirme seu e-mail para definir uma nova senha.", color="var(--vt-muted)", text_align="center"),
        rx.form(
            rx.vstack(
                rx.match(
                    State.recovery_step,
                    ("email", recovery_input("E-mail cadastrado", "email", "email", "email")),
                    ("code", rx.vstack(
                        recovery_input("Código recebido por e-mail", "code", "text", "one-time-code"),
                        rx.text("Válido por 10 minutos. Aguarde 60 segundos antes de reenviar.", font_size="13px", color="var(--vt-muted)"),
                        rx.button("Reenviar código", type="button", variant="soft", on_click=State.resend_recovery_code, disabled=State.recovery_busy),
                        width="100%", align="stretch",
                    )),
                    rx.vstack(
                        recovery_input("Nova senha", "new_password", "password", "new-password"),
                        recovery_input("Confirmar nova senha", "password_confirmation", "password", "new-password"),
                        width="100%", align="stretch",
                    ),
                ),
                rx.text(State.recovery_message, role="status", color="var(--vt-text)", font_size="13px"),
                rx.button(
                    rx.cond(State.recovery_busy, "Aguarde...", rx.match(State.recovery_step, ("email", "Enviar código"), ("code", "Verificar código"), "Atualizar senha")),
                    type="submit", disabled=State.recovery_busy, width="100%", background="var(--vt-green)", color="white", border_radius="999px",
                ),
                rx.hstack(
                    rx.button("Voltar", type="button", variant="ghost", on_click=State.recovery_back),
                    rx.button("Cancelar", type="button", variant="ghost", on_click=State.cancel_password_recovery),
                    justify="between", width="100%",
                ),
                align="stretch", width="100%", spacing="3",
            ),
            on_submit=State.submit_password_recovery, reset_on_submit=False,
            id="password-recovery-form", width="100%",
        ),
        align="center", width="min(100%, 360px)", spacing="4",
    )
