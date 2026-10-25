import reflex as rx

from vet_tech.components.navigation import clinical_menu_actions
from vet_tech.components.sidebar import layout_com_menu
from vet_tech.components.pets import pet_details, pet_list
from vet_tech.features.auth.state import State
from vet_tech.components.clinical import booking_dialog, pet_loading, records, tutor_clinical_content, tutor_consultations, veterinary_content, veterinary_sidebar


def tutor_area() -> rx.Component:
    return layout_com_menu(
        rx.box(
            rx.hstack(
                rx.vstack(rx.text("Área do tutor", size="2", color="var(--vt-muted)"),
                          rx.heading(State.active_section, size="7"), align="start", spacing="1"),
                rx.spacer(),
                rx.cond(State.active_section == "Início", booking_dialog()),
                rx.cond(State.pet_target_id != '', rx.button('Atualizar dados do pet', on_click=State.load_tutor_clinical,
                    disabled=State.clinic_loading | State.is_loading_pet | (State.selected_pet_id == ''), variant='outline')),
                rx.cond(State.selected_pet_id != "", rx.badge(State.selected_pet["nome"], size="2", white_space="normal", max_width="100%")),
                align="center", wrap="wrap", width="100%", margin_bottom="2rem",
            ),
            rx.cond(State.pet_picker_open | (State.pet_target_id == ""),
                    rx.vstack(rx.text("Escolha um pet para continuar ou cadastre em Novo pet."), pet_list(),
                              align="stretch", width="100%", spacing="4"),
                    rx.match(State.active_section,
                        ("Início", rx.vstack(pet_details(),
                            rx.cond(State.clinic_loading, pet_loading()),
                            rx.cond(State.clinic_message != '', rx.vstack(rx.text(State.clinic_message, role='status'),
                                rx.button('Tentar novamente', on_click=State.load_tutor_clinical))),
                            align='stretch', width='100%', aria_busy=State.is_loading_pet | State.clinic_loading)),
                        ("Consultas", tutor_clinical_content(tutor_consultations())),
                        ("Vacinas", tutor_clinical_content(records("vacinas"))),
                        ("Medicamentos", tutor_clinical_content(records("medicamentos"))),
                        ("Doenças", tutor_clinical_content(records("doencas"))),
                        pet_details())),
            rx.text(State.pet_message, role="status", margin_top="1rem"),
            as_="main", id="main-content", width="100%", min_width="0",
            overflow_wrap="anywhere",
        ), pagina_ativa=State.clinical_menu_item, actions=clinical_menu_actions(),
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
