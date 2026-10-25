import reflex as rx

from vet_tech.features.navigation.state import NavigationState

from vet_tech.components.pets import pet_form
from vet_tech.features.auth.state import State

SECTIONS = [("Início", "house"), ("Vacinas", "syringe"), ("Medicamentos", "pill"),
            ("Doenças", "heart-pulse"), ("Consultas", "clipboard-list")]


def menu_label(text: str) -> rx.Component:
    return rx.cond(NavigationState.sidebar_expanded, rx.text(text, white_space="nowrap"))


def menu_button(label: str, icon: str, **props) -> rx.Component:
    return rx.button(
        rx.icon(icon, size=20), menu_label(label), aria_label=label, title=label,
        width="100%", justify="start", height="44px", color="inherit",
        variant="ghost", **props,
    )


def new_pet_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(menu_button("Novo pet", "circle-plus", disabled=State.is_busy)),
        rx.dialog.content(
            rx.dialog.title("Novo pet"),
            rx.dialog.description("Cadastre um animal sob sua responsabilidade."),
            pet_form(),
            rx.dialog.close(rx.button("Cancelar", variant="outline", disabled=State.is_busy, margin_top="1rem")),
            max_height="85dvh", overflow_y="auto", width="min(95vw, 560px)",
        ),
        open=State.pet_modal_open, on_open_change=State.set_pet_modal,
    )


def sidebar() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(rx.image(src="/mascote_logo.png", alt="Vet Tech", width="32px", height="32px"),
                      menu_label("Vet Tech"), align="center", spacing="2"),
            rx.button(rx.icon("panel-left", size=20), menu_label("Recolher menu"),
                      aria_label=rx.cond(NavigationState.sidebar_expanded, "Recolher menu", "Expandir menu"),
                      aria_expanded=NavigationState.sidebar_expanded, on_click=NavigationState.toggle_sidebar,
                      variant="outline", width="100%", justify="start"),
            *[menu_button(label, icon, on_click=State.clinical_section(label),
                          background=rx.cond(State.active_section == label, "var(--vt-icon-bg)", "transparent"),
                          custom_attrs={"aria-current": rx.cond(State.active_section == label, "page", "false")})
              for label, icon in SECTIONS],
            rx.spacer(),
            rx.link("Meus Pets", href="/", color="inherit"),
            rx.link("Configurações", href="/configuracoes", color="inherit"),
            new_pet_dialog(),
            menu_button("Mudar pet", "arrow-left-right", on_click=State.show_pet_picker),
            menu_button("Sair", "log-out", on_click=State.logout),
            height="100%", align="stretch", spacing="3", padding="12px",
        ),
        as_="nav", aria_label="Menu principal", background="var(--vt-surface)", color="var(--vt-text)",
        border_right="1px solid var(--vt-border)", height="100dvh", overflow_y="auto",
        width=rx.cond(NavigationState.sidebar_expanded, "260px", "72px"), flex_shrink="0",
        position=rx.breakpoints(initial="fixed", lg="sticky"), top="0", left="0", z_index="20",
    )
