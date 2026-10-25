import reflex as rx

from vet_tech.components.auth import login_view
from vet_tech.components.pets import profile_view
from vet_tech.pages.profile import veterinarian_area
from vet_tech.features.auth.state import State


def index() -> rx.Component:
    return rx.cond(
        State.is_authenticated,
        rx.cond(State.profile == "veterinario", veterinarian_area(), profile_view()),
        login_view(),
    )


def login_page() -> rx.Component:
    return index()
