import reflex as rx

from vet_tech.components.sidebar import layout_com_menu
from vet_tech.components.pets import pet_details, pet_selection_empty_state
from vet_tech.features.auth.state import State
from vet_tech.components.clinical import booking_dialog, pet_loading, records, tutor_clinical_content, tutor_consultations, veterinary_content


def _records_header(title: str, description: str) -> rx.Component:
    return rx.box(
        rx.box(
            rx.heading(title, size="7"),
            rx.text(description, color="var(--vt-muted)"),
            class_name="vaccines-heading",
        ),
        rx.box(
            rx.cond(State.selected_pet_id != "",
                rx.box(
                    rx.avatar(src=State.selected_pet.get("foto", ""), fallback="🐾", alt=State.selected_pet["nome"], size="2", radius="full"),
                    rx.box(rx.text("Pet selecionado", class_name="vaccines-pet-label"),
                           rx.text(State.selected_pet["nome"], class_name="vaccines-pet-name"), min_width="0"),
                    class_name="vaccines-current-pet",
                ),
            ),
            *([rx.cond(State.detail_id != "",
                rx.button(rx.icon("arrow-left", size=17), "Voltar à lista",
                    on_click=State.set_detail_id(""), variant="outline", class_name="consultation-header-back"))]
              if title == "Consultas" else []),
            rx.button(rx.icon("refresh-cw", size=17), "Atualizar",
                      on_click=State.load_tutor_clinical,
                      disabled=State.clinic_loading | State.is_loading_pet | (State.selected_pet_id == ""),
                      class_name="vaccines-refresh", aria_label="Atualizar registros do pet"),
            *([rx.cond((State.detail_id != "") & (State.detail.get("status", "") == "finalizada") & State.consultation_pdf_available,
                rx.button(rx.icon("download", size=17), "Exportar PDF", on_click=State.open_consultation_pdf,
                    id="consultation-pdf-trigger",
                    loading=State.pdf_export_busy, disabled=State.pdf_export_busy,
                    aria_label="Exportar PDF da consulta", class_name="consultation-header-export"))]
              if title == "Consultas" else []),
            class_name="vaccines-header-actions",
        ),
        class_name="vaccines-header consultations-header" if title == "Consultas" else "vaccines-header",
    )


def tutor_area() -> rx.Component:
    from vet_tech.components.consultation_pdf import consultation_pdf_dialog
    return layout_com_menu(
        rx.box(
            rx.cond(
                State.pet_target_id == "",
                pet_selection_empty_state(),
                rx.fragment(
                    rx.cond(
                        State.active_section == "Início",
                        rx.hstack(
                            rx.button(rx.icon("arrow-left", size=18), "Voltar à lista", on_click=State.close_pet, variant="ghost"),
                            rx.spacer(),
                            booking_dialog(),
                            rx.button(rx.icon("refresh-cw", size=17), "Atualizar dados", on_click=State.load_tutor_clinical,
                                      disabled=State.clinic_loading | State.is_loading_pet | (State.selected_pet_id == ""), variant="outline"),
                            class_name="pet-record-toolbar", align="center", wrap="wrap", width="100%",
                        ),
                    rx.cond((State.active_section == "Vacinas") | (State.active_section == "Medicamentos") | (State.active_section == "Doenças") | (State.active_section == "Consultas"),
                        rx.cond(State.active_section == "Vacinas",
                            _records_header("Vacinas", "Histórico de vacinação do seu pet"),
                            rx.cond(State.active_section == "Medicamentos",
                                _records_header("Medicamentos", "Prescrições e cuidados registrados para seu pet"),
                                rx.cond(State.active_section == "Doenças",
                                    _records_header("Doenças", "Condições e acompanhamento de saúde do seu pet"),
                                    _records_header("Consultas", "Agendamentos e prontuários do seu pet")))), rx.hstack(
                        rx.vstack(rx.text("Área do tutor", size="2", color="var(--vt-muted)"),
                                  rx.heading(State.active_section, size="7"), align="start", spacing="1"),
                        rx.spacer(),
                        rx.cond(State.active_section == "Início", booking_dialog()),
                        rx.cond(State.pet_target_id != '', rx.button('Atualizar dados do pet', on_click=State.load_tutor_clinical,
                            disabled=State.clinic_loading | State.is_loading_pet | (State.selected_pet_id == ''), variant='outline')),
                        rx.cond(State.selected_pet_id != "", rx.badge(State.selected_pet["nome"], size="2", white_space="normal", max_width="100%")),
                        align="center", wrap="wrap", width="100%", margin_bottom="2rem",
                        class_name="tutor-section-header",
                    )),
                    ),
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
                                pet_details()),
                ),
            ),
            rx.cond(State.pet_message != "", rx.text(State.pet_message, role="status", margin_top="1rem")),
            consultation_pdf_dialog(),
            as_="main", id="main-content", width="100%", min_width="0",
            overflow_wrap="anywhere",
            class_name=rx.cond((State.active_section == "Início") & (State.pet_target_id != ""), "pet-record-page", rx.cond((State.active_section == "Vacinas") & (State.pet_target_id != ""), "tutor-vaccines-page", rx.cond((State.active_section == "Medicamentos") & (State.pet_target_id != ""), "tutor-medications-page", ""))),
        ), pagina_ativa=State.clinical_menu_item,
    )


def veterinarian_area() -> rx.Component:
    from vet_tech.components.veterinary_schedule import veterinary_navigation, veterinary_actions
    from vet_tech.components.consultation_pdf import consultation_pdf_dialog
    return layout_com_menu(
        rx.box(veterinary_content(), consultation_pdf_dialog(), as_="main", id="main-content", class_name="vet-schedule",
               on_mount=State.enter_veterinary_agenda, width="100%", min_width="0"),
        pagina_ativa="horarios", actions=veterinary_actions(), navigation=veterinary_navigation(),
    )


def profile_view() -> rx.Component:
    return rx.cond(State.profile == "tutor", tutor_area(),
                   rx.cond(State.profile == "veterinario", veterinarian_area(),
                           rx.vstack(rx.text("Não foi possível identificar a sessão."), rx.button("Sair", on_click=State.logout))))


def clinical_page() -> rx.Component:
    from vet_tech.components.auth import login_view
    return rx.cond(State.is_authenticated, profile_view(), login_view())
