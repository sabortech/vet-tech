import reflex as rx

from vet_tech.features.auth.state import State
from vet_tech.features.veterinarians.validation import UFS


def professional_fields() -> rx.Component:
    return rx.vstack(
        rx.input(name="crmv", placeholder="CRMV (somente letras e números)", required=True,
                 max_length=20, aria_label="Número do CRMV", width="100%"),
        rx.select(UFS, name="crmv_uf", placeholder="UF do CRMV", required=True,
                  aria_label="UF do CRMV", width="100%"),
        rx.text("Validação de formato, sem consulta ao conselho profissional.", size="1", color="#53635A"),
        rx.text("Espécies atendidas", weight="bold", size="2"),
        rx.foreach(State.registration_species, lambda item: rx.checkbox(
            item["nome"], checked=State.professional_species.contains(item["id"]),
            on_change=lambda checked: State.toggle_professional_species(item["id"], checked),
            disabled=State.is_busy,
        )),
        rx.text("Especialidades", weight="bold", size="2"),
        rx.foreach(State.registration_specialties, lambda item: rx.checkbox(
            item["nome"], checked=State.professional_specialties.contains(item["id"]),
            on_change=lambda checked: State.toggle_professional_specialty(item["id"], checked),
            disabled=State.is_busy,
        )),
        rx.text("Clínica (opcional)", weight="bold", size="2"),
        rx.select.root(
            rx.select.trigger(placeholder="Sem vínculo com clínica", width="100%"),
            rx.select.content(
                rx.select.item("Sem vínculo com clínica", value="none"),
                rx.foreach(State.registration_clinics, lambda item: rx.select.item(item["nome"], value=item["id"])),
            ),
            value=rx.cond(State.professional_clinic == "", "none", State.professional_clinic),
            on_change=State.choose_professional_clinic, disabled=State.is_busy,
        ),
        rx.cond(State.is_loading_registration_options, rx.text("Carregando opções…", role="status")),
        rx.cond(State.registration_options_message != "", rx.vstack(
            rx.text(State.registration_options_message, role="alert", size="2"),
            rx.button("Tentar carregar opções", type="button", on_click=State.load_registration_options,
                      disabled=State.is_loading_registration_options | State.is_busy, variant="outline"),
        )),
        width="100%", align="stretch", spacing="2",
    )
