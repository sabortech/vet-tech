from typing import Any

import reflex as rx

from vet_tech.features.auth.state import State
from vet_tech.components.professional_registration import professional_fields

VERDE = "var(--vt-green)"
VERDE_ESCURO = "var(--vt-text)"
CINZA_CAMPO = "var(--vt-field-bg)"
LARGURA_FORMULARIO = "320px"


def campo_texto(
    placeholder: str,
    name: str,
    input_type: str = "text",
    **props: Any,
) -> rx.Component:
    autocomplete = props.pop("auto_complete", "off")
    return rx.input(
        placeholder=placeholder,
        type=input_type,
        name=name,
        required=True,
        custom_attrs={"aria-label": placeholder, "autoComplete": autocomplete},
        width="100%",
        height="44px",
        padding_x="14px",
        background=CINZA_CAMPO,
        border="1px solid transparent",
        border_radius="14px",
        color=VERDE_ESCURO,
        font_family="Nunito",
        font_size="14px",
        outline="none",
        _focus={"border": f"1.5px solid {VERDE}", "box_shadow": "none"},
        **props,
    )


def botao_primario() -> rx.Component:
    return rx.button(
        rx.cond(State.is_busy, "Cadastrando…", "Cadastrar"),
        type="submit",
        disabled=State.is_busy,
        width="100%",
        height="36px",
        padding="0",
        background=VERDE,
        color="var(--vt-primary-text)",
        border="none",
        border_radius="999px",
        font_family="Nunito",
        font_size="14px",
        font_weight="600",
        cursor="pointer",
        _hover={"background": "var(--vt-green-hover)"},
    )


def divisor_ou() -> rx.Component:
    return rx.hstack(
        rx.box(height="1px", flex="1", background="var(--vt-border)"),
        rx.text("ou", color="var(--vt-muted)", font_family="Nunito", font_size="11px"),
        rx.box(height="1px", flex="1", background="var(--vt-border)"),
        width="100%",
        align="center",
        spacing="2",
    )


def botao_google() -> rx.Component:
    return rx.button(
        rx.image(
            src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg",
            alt="Google",
            width="18px",
            height="18px",
        ),
        rx.text("Google — em breve", font_family="Nunito", font_size="14px"),
        width="100%",
        height="36px",
        display="flex",
        align_items="center",
        justify_content="center",
        gap="9px",
        padding="0",
        background="var(--vt-surface)",
        color="var(--vt-text)",
        border="1px solid var(--vt-border)",
        border_radius="999px",
        font_weight="400",
        disabled=True,
        title="Cadastro com Google ainda indisponível",
    )


def conteudo_cadastro() -> rx.Component:
    formulario = rx.form(
        rx.vstack(
            rx.select.root(
                rx.select.trigger(placeholder="Perfil a cadastrar", width="100%"),
                rx.select.content(rx.select.item("Tutor", value="tutor"), rx.select.item("Veterinário", value="veterinario")),
                value=State.signup_profile, on_change=State.choose_signup_profile,
                disabled=State.is_busy, aria_label="Perfil a cadastrar",
            ),
            campo_texto("Nome completo", "nome", auto_complete="name"),
            campo_texto("E-mail", "email", "email", auto_complete="email"),
            rx.cond(State.signup_profile == "tutor", rx.vstack(
                campo_texto("CPF", "cpf", value=State.signup_cpf,
                            on_change=State.set_signup_cpf, max_length=14),
                rx.text(State.signup_cpf_feedback, role="status", font_size="12px"),
                campo_texto("Endereço", "endereco", auto_complete="street-address"),
                width="100%", spacing="2",
            ), professional_fields()),
            campo_texto("Telefone", "telefone", "tel", auto_complete="tel"),
            campo_texto("Senha", "password", "password", auto_complete="new-password", id="signup-password"),
            campo_texto("Confirmar Senha", "password_confirmation", "password",
                        auto_complete="new-password", id="signup-password-confirmation"),
            rx.text(State.signup_message, role="alert", color=VERDE_ESCURO,
                    font_size="13px", width="100%"),
            botao_primario(),
            width="100%",
            spacing="2",
        ),
        on_submit=State.signup,
        reset_on_submit=False,
        width="100%",
    )

    painel_formulario = rx.vstack(
        rx.image(
            src="/mascote_logo.png",
            alt="Logo Vet Tech",
            width="75px",
            height="75px",
            object_fit="contain",
        ),
        rx.heading(
            "Vet Tech",
            as_="h1",
            font_family="Nunito",
            font_size="40px",
            font_weight="400",
            line_height="1",
            color=VERDE_ESCURO,
        ),
        rx.vstack(
            rx.text(
                "Olá, Seja Bem-vindo!",
                color="var(--vt-text)",
                font_family="Nunito",
                font_size="22px",
                font_weight="700",
                line_height="1.2",
            ),
            rx.text(
                "Cuide dos seus pets com qualidade!",
                color="var(--vt-text)",
                font_family="Nunito",
                font_size="17px",
                line_height="1.25",
            ),
            align="center",
            spacing="1",
            width="100%",
        ),
        formulario,
        divisor_ou(),
        botao_google(),
        rx.link(
            rx.hstack(
                rx.text(
                    "Já tem uma conta?",
                    color="var(--vt-text)",
                    font_family="Nunito",
                    font_size="13px",
                ),
                rx.text(
                    "Login",
                    color=VERDE,
                    font_family="Nunito",
                    font_size="13px",
                ),
                spacing="1",
                justify="center",
                width="100%",
            ),
            href="/login",
            text_decoration="none",
        ),
        width=LARGURA_FORMULARIO,
        max_width="100%",
        align="center",
        justify="center",
        spacing="3",
    )

    return rx.box(
        rx.hstack(
            rx.box(
                painel_formulario,
                width=["100%", "100%", "50%"],
                height="100%",
                padding=["28px 22px", "36px 30px", "48px 48px"],
                background="var(--vt-surface)",
                display="flex",
                align_items="center",
                justify_content="center",
            ),
            rx.box(
                rx.image(
                    src="/mascote05.png",
                    alt="Mascote Vet Tech segurando uma prancheta",
                    width="100%",
                    height="100%",
                    object_fit="contain",
                    object_position="center",
                    position="absolute",
                    inset="0",
                ),
                width="50%",
                align_self="stretch",
                position="relative",
                background="#80A85C",
                background_image="url('/fundo_mar.jpeg')",
                background_size="cover",
                background_position="center",
                background_repeat="no-repeat",
                display=["none", "none", "block"],
                align_items="center",
                justify_content="center",
            ),
            width="100%",
            height="100%",
            flex_direction=["column", "column", "row"],
            overflow="hidden",
            border_radius="32px",
        ),
        display="flex",
        align_items="center",
        justify_content="center",
        width="min(1040px, calc(100vw - 32px))",
        height="auto",
        min_height="auto",
        overflow="hidden",
        border_radius="32px",
        background="var(--vt-surface)",
        box_shadow="0 22px 65px rgba(20, 39, 24, 0.24)",
    )


def cadastro() -> rx.Component:
    return rx.box(
        conteudo_cadastro(),
        min_height="100vh",
        width="100%",
        display="flex",
        align_items="center",
        justify_content="center",
        padding="16px",
        background_color="#72935B",
        background_image="url('/fundo_mar.jpeg')",
        background_size="cover",
        background_position="center",
        background_repeat="no-repeat",
    )
