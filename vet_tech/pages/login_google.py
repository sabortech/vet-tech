import reflex as rx

from vet_tech.components.auth import google_return_view


def login_google_page() -> rx.Component:
    """Retorno do Google; a conclusão do login roda em `State.finish_google_login`."""
    return google_return_view()
