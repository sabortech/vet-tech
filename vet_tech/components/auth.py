import reflex as rx

from vet_tech.features.auth.state import State


def login_view() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.heading("Perfil do tutor", size="6"),
            rx.text("Entre com as credenciais da sua conta de tutor."),
            rx.form(
                rx.vstack(
                    rx.input(
                        placeholder="E-mail",
                        type="email",
                        name="email",
                        required=True,
                        width="100%",
                    ),
                    rx.input(
                        placeholder="Senha",
                        type="password",
                        name="password",
                        required=True,
                        width="100%",
                    ),
                    rx.button(
                        "Entrar",
                        type="submit",
                        disabled=State.is_busy,
                        width="100%",
                    ),
                    align="stretch",
                    spacing="3",
                    width="100%",
                ),
                on_submit=State.login,
                width="100%",
            ),
            rx.text(State.login_message, role="status"),
            rx.button(
                "Criar conta de tutor",
                on_click=State.show_signup,
                variant="ghost",
            ),
            spacing="3",
            align="stretch",
            width="100%",
            max_width="32rem",
        ),
        padding_top="4rem",
    )
