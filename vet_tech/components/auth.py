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


def signup_view() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.heading("Cadastro de tutor", size="6"),
            rx.text("Preencha seus dados para criar sua conta."),
            rx.form(
                rx.vstack(
                    rx.input(
                        placeholder="Nome completo",
                        type="text",
                        name="nome",
                        required=True,
                        width="100%",
                    ),
                    rx.input(
                        placeholder="CPF",
                        type="text",
                        name="cpf",
                        value=State.signup_cpf,
                        on_change=State.set_signup_cpf,
                        required=True,
                        max_length=14,
                        width="100%",
                    ),
                    rx.text(State.signup_cpf_feedback, role="status"),
                    rx.input(
                        placeholder="E-mail",
                        type="email",
                        name="email",
                        required=True,
                        width="100%",
                    ),
                    rx.input(
                        placeholder="Telefone",
                        type="tel",
                        name="telefone",
                        required=True,
                        width="100%",
                    ),
                    rx.input(
                        placeholder="Endereço",
                        type="text",
                        name="endereco",
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
                        "Cadastrar",
                        type="submit",
                        disabled=State.is_busy,
                        width="100%",
                    ),
                    align="stretch",
                    spacing="3",
                    width="100%",
                ),
                on_submit=State.signup,
                width="100%",
            ),
            rx.text(State.signup_message, role="status"),
            rx.button(
                "Já tenho uma conta",
                on_click=State.show_login,
                variant="ghost",
            ),
            spacing="3",
            align="stretch",
            width="100%",
            max_width="32rem",
        ),
        padding_top="4rem",
    )
