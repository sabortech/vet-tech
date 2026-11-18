import reflex as rx

from vet_tech.components.adoption import adoption_content
from vet_tech.components.auth import login_view
from vet_tech.components.sidebar import layout_com_menu
from vet_tech.features.auth.state import State


def adoption_page() -> rx.Component:
    return rx.cond(
        State.is_authenticated & (State.profile == "tutor"),
        layout_com_menu(adoption_content(), pagina_ativa="adocao"),
        rx.cond(
            State.is_authenticated,
            rx.box(
                rx.text("Adoção está disponível somente para tutores."),
                role="status",
                class_name="adoption-page__restricted",
            ),
            login_view(),
        ),
    )
