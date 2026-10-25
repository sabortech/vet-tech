import reflex as rx

from vet_tech.features.navigation.state import NavigationState

from vet_tech.components.navigation import sidebar
from vet_tech.components.pets import pet_details, pet_list
from vet_tech.features.auth.state import State
from vet_tech.components.clinical import booking_dialog, notice, records, tutor_consultations, veterinary_content, veterinary_sidebar


def tutor_area() -> rx.Component:
    return rx.hstack(
        sidebar(),
        rx.box(
            rx.hstack(
                rx.vstack(rx.text("Área do tutor", size="2", color="var(--vt-muted)"),
                          rx.heading(State.active_section, size="7"), align="start", spacing="1"),
                rx.spacer(),
                rx.cond(State.active_section == "Início", booking_dialog()),
                rx.cond(State.selected_pet_id != "", rx.badge(State.selected_pet["nome"], size="2", white_space="normal", max_width="100%")),
                align="center", wrap="wrap", width="100%", margin_bottom="2rem",
            ),
            rx.cond(State.pet_picker_open | (State.pet_target_id == ""),
                    rx.vstack(rx.text("Escolha um pet para continuar ou cadastre em Novo pet."), pet_list(),
                              align="stretch", width="100%", spacing="4"),
                    rx.match(State.active_section,
                        ("Início", pet_details()),
                        ("Consultas", tutor_consultations()),
                        ("Vacinas", rx.vstack(notice(), records("vacinas"), align="stretch")),
                        ("Medicamentos", rx.vstack(notice(), records("medicamentos"), align="stretch")),
                        ("Doenças", rx.vstack(notice(), records("doencas"), align="stretch")),
                        pet_details())),
            rx.text(State.pet_message, role="status", margin_top="1rem"),
            as_="main", id="main-content", width="100%", min_width="0", min_height="100dvh",
            overflow_wrap="anywhere",
            padding=rx.breakpoints(initial="24px 16px", lg="40px"),
            margin_left=rx.breakpoints(initial="72px", lg="0"),
        ),
        rx.cond(NavigationState.sidebar_expanded, rx.box(
            rx.button("Fechar menu", on_click=NavigationState.toggle_sidebar, width="100%", height="100%",
                      variant="ghost", aria_label="Fechar menu", opacity="0"),
            position="fixed", inset="0", background="rgba(0,0,0,.3)", z_index="19",
            display=rx.breakpoints(initial="block", lg="none"),
        )),
        width="100%", align="start", spacing="0", background="var(--vt-page-bg)", color="var(--vt-text)",
    )


def veterinarian_area() -> rx.Component:
    return rx.hstack(veterinary_sidebar(),
        rx.box(veterinary_content(), as_="main", width="100%", min_width="0",
               overflow_wrap="anywhere",
               padding=rx.breakpoints(initial="16px", lg="40px")),
        width="100%", align="start", spacing="0", on_mount=State.load_agenda)


def profile_view() -> rx.Component:
    return rx.cond(State.profile == "tutor", tutor_area(),
                   rx.cond(State.profile == "veterinario", veterinarian_area(),
                           rx.vstack(rx.text("Não foi possível identificar a sessão."), rx.button("Sair", on_click=State.logout))))


def clinical_page() -> rx.Component:
    from vet_tech.components.auth import login_view
    return rx.cond(State.is_authenticated, profile_view(), login_view())
