import reflex as rx

from vet_tech.components.auth import login_view, signup_view
from vet_tech.components.pets import profile_view
from vet_tech.features.auth.state import State


def index() -> rx.Component:
    return rx.cond(
        State.is_authenticated,
        profile_view(),
        rx.cond(State.is_registering, signup_view(), login_view()),
    )


def login_page() -> rx.Component:
    return rx.cond(State.is_authenticated, profile_view(), login_view())
