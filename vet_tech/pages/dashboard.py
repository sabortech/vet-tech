import reflex as rx

from vet_tech.components.auth import login_view
from vet_tech.components.dashboard import tutor_dashboard_page
from vet_tech.features.auth.state import State


def dashboard() -> rx.Component:
    return rx.cond(State.is_authenticated, tutor_dashboard_page(), login_view())
