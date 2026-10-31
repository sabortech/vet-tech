"""Mascote animada local e ponte privada de eventos do chat Reflex."""

from typing import Literal

import reflex as rx

from vet_tech.features.auth.state import State


def _imagem(nome: str, camada: str) -> rx.Component:
    return rx.el.img(
        src=f"/mascote/{nome}.png",
        alt="",
        decoding="async",
        draggable=False,
        class_name=f"mascote-image {camada}",
    )


def mascote_flutuante(glow_mode: Literal["green", "rgb"] = "green") -> rx.Component:
    """Cria o botão que publica o evento local de abertura do chat."""
    if glow_mode not in ("green", "rgb"):
        raise ValueError("glow_mode deve ser green ou rgb")
    return rx.el.button(
        rx.el.span(class_name="mascote-glow", aria_hidden="true"),
        rx.el.span(class_name="mascote-shadow", aria_hidden="true"),
        rx.el.span(
            rx.el.span(
                rx.el.span(
                    rx.el.span("🐢", class_name="mascote-fallback"),
                    _imagem("mascote_idle", "mascote-idle-image"),
                    class_name="mascote-idle",
                ),
                rx.el.span(
                    _imagem("mascote_hover", "mascote-hover-image"),
                    class_name="mascote-hover",
                ),
                class_name="mascote-tracking",
            ),
            class_name="mascote-art", aria_hidden="true",
        ),
        id="vettech-mascote",
        class_name="mascote",
        type="button",
        aria_label="Abrir assistente Vet Tech",
        draggable=False,
        custom_attrs={"data-glow-mode": glow_mode, "aria-haspopup": "dialog", "aria-expanded": "false"},
    )


def mascote_app_wrap(_stateful: bool) -> rx.Component:
    """O Reflex insere o outlet das páginas neste wrapper único do app."""
    return rx.fragment(
        mascote_flutuante(),
        rx.form(
            rx.el.input(type="hidden", name="payload", id="vettech-chat-payload"),
            rx.el.button(type="submit"),
            on_submit=State.support_chat,
            on_mount=rx.call_script("window.__vetTechChatReady = true; window.dispatchEvent(new Event('vettech:chat-ready'));"),
            method="post",
            id="vettech-chat-bridge", display="none",
        ),
        rx.el.span(
            id="vettech-chat-session", hidden=True,
            custom_attrs={
                "data-chat-name": rx.cond(State.is_authenticated, State.identity_name, ""),
                "data-chat-key": rx.cond(State.is_authenticated, State.profile + ":" + State.identity_id, ""),
            },
        ),
    )
