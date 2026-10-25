import reflex as rx

from vet_tech.components.clinical import attendance_content
from vet_tech.features.auth.state import State


def atendimento() -> rx.Component:
    return rx.cond(State.is_authenticated & (State.profile == "veterinario"),
                   attendance_content(), rx.text("Entre com seu perfil veterinário para continuar."))
