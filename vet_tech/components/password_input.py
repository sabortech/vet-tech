"""Controles locais de visibilidade, sem guardar valores de senha no State."""
import reflex as rx


def password_visibility_button(field_id: str, label: str, *, disabled=False, class_name="password-eye"):
    return rx.el.button(
        rx.icon("eye", size=18, class_name="password-eye-open", aria_hidden=True),
        rx.icon("eye-off", size=18, class_name="password-eye-closed", aria_hidden=True),
        type="button", disabled=disabled, class_name=class_name,
        custom_attrs={
            "data-password-target": field_id,
            "data-password-label": label.lower(),
            "aria-controls": field_id,
            "aria-label": "Mostrar " + label.lower(),
            "aria-pressed": "false",
        },
    )


def password_control(input_component, field_id: str, label: str, *, disabled=False):
    return rx.box(
        input_component,
        password_visibility_button(field_id, label, disabled=disabled),
        class_name="password-control", position="relative", width="100%",
    )
