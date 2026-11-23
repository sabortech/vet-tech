"""Área de clínica, seguindo o layout visual da área veterinária."""
import reflex as rx

from vet_tech.components.sidebar import layout_com_menu
from vet_tech.components.pets import pet_form
from vet_tech.features.auth.state import State
from vet_tech.features.navigation.state import NavigationState
from vet_tech.features.veterinarians.validation import UFS


def _nav_item(label: str, icon: str) -> rx.Component:
    return rx.el.button(
        rx.hstack(rx.icon(icon, size=20, class_name="sidebar-item__icon"), rx.text(label, class_name="sidebar-item__label"), class_name="sidebar-item__contents"),
        on_click=[State.clinic_navigate(label), NavigationState.close_drawer],
        class_name=rx.cond(State.clinic_section == label, "sidebar-item sidebar-item--active", "sidebar-item"),
        title=label, aria_label=label,
    )


def _vet_card(vet: rx.Var) -> rx.Component:
    return rx.box(
        rx.hstack(rx.icon("stethoscope", size=23), rx.vstack(rx.text(vet["nome"], class_name="vet-schedule-pet-name"), rx.text("CRMV " + vet["crmv"] + " / " + vet["uf"], class_name="vet-schedule-reason"), rx.text(vet["especialidades"], class_name="vet-schedule-reason"), align="start"), spacing="3"),
        class_name="vet-schedule-card",
    )


def _pet_card(pet: rx.Var) -> rx.Component:
    return rx.box(
        rx.hstack(rx.icon("paw-print", size=23), rx.vstack(rx.text(pet["nome"], class_name="vet-schedule-pet-name"), rx.text(rx.cond(pet["disponivel"] == "sim", "Disponível para adoção", "Ainda não publicado"), class_name="vet-schedule-reason"), align="start"), rx.spacer(),
            rx.alert_dialog.root(
                rx.alert_dialog.trigger(rx.button(rx.cond(pet["disponivel"] == "sim", "Retirar", "Publicar"), variant="soft", disabled=State.clinic_admin_loading)),
                rx.alert_dialog.content(rx.alert_dialog.title("Alterar disponibilidade"), rx.alert_dialog.description(rx.cond(pet["disponivel"] == "sim", "Retirar este pet da lista de adoção?", "Disponibilizar este pet para adoção?")),
                    rx.hstack(rx.alert_dialog.cancel(rx.button("Cancelar", variant="soft")), rx.alert_dialog.action(rx.button("Confirmar", on_click=State.clinic_set_availability(pet["id"], pet["disponivel"] != "sim"))), spacing="3", justify="end", margin_top="1em")),
            ), align="center", width="100%"), class_name="vet-schedule-card",
    )


def _pet_form() -> rx.Component:
    return pet_form(clinic=True)


def _vet_form() -> rx.Component:
    return rx.form(
        rx.vstack(
            rx.heading(rx.cond(State.clinic_vet_form == "novo", "Cadastrar veterinário", "Vincular veterinário"), size="4"),
            rx.cond(State.clinic_vet_form == "novo", rx.fragment(
                rx.input(name="nome", placeholder="Nome completo", aria_label="Nome completo", required=True),
                rx.input(name="telefone", placeholder="Telefone", aria_label="Telefone", required=True),
                rx.input(name="crmv", placeholder="CRMV", aria_label="CRMV", required=True, max_length=20),
                rx.select(UFS, name="crmv_uf", placeholder="UF do CRMV", aria_label="UF do CRMV", required=True),
                rx.text("Espécies atendidas", weight="bold"),
                rx.foreach(State.registration_species, lambda item: rx.checkbox(item["nome"], checked=State.professional_species.contains(item["id"]), on_change=lambda checked: State.toggle_professional_species(item["id"], checked))),
                rx.text("Especialidades", weight="bold"),
                rx.foreach(State.registration_specialties, lambda item: rx.checkbox(item["nome"], checked=State.professional_specialties.contains(item["id"]), on_change=lambda checked: State.toggle_professional_specialty(item["id"], checked))),
                rx.cond(State.registration_options_message != "", rx.text(State.registration_options_message, role="alert")),
            )),
            rx.input(name="email", type="email", placeholder="E-mail do veterinário", aria_label="E-mail do veterinário", required=True),
            rx.cond(State.clinic_vet_form == "novo", rx.fragment(
                rx.input(name="password", type="password", placeholder="Senha provisória", aria_label="Senha provisória", required=True, custom_attrs={"autoComplete": "new-password"}),
                rx.input(name="password_confirmation", type="password", placeholder="Confirmar senha provisória", aria_label="Confirmar senha provisória", required=True, custom_attrs={"autoComplete": "new-password"}),
                rx.text("O veterinário poderá alterar a senha em Configurações.", size="2"),
            ), rx.text("O profissional precisa aceitar o convite em sua conta e estar sem clínica.", size="2")),
            rx.hstack(rx.button("Enviar", type="submit", disabled=State.clinic_admin_loading | State.is_loading_registration_options), rx.button("Cancelar", type="button", variant="soft", on_click=State.clinic_close_vet_form), wrap="wrap"),
            width="100%", align="stretch", spacing="3",
        ), on_submit=State.clinic_submit_vet, reset_on_submit=False, class_name="vet-schedule-card", width="100%",
    )


def clinic_area() -> rx.Component:
    navigation = rx.fragment(_nav_item("Veterinários", "stethoscope"), _nav_item("Pets para adoção", "paw-print"))
    actions = rx.vstack(rx.text("Clínica", class_name="vet-profile-eyebrow"), rx.text(State.clinic_name, class_name="vet-profile-name"), rx.text(State.identity_name), rx.el.button(rx.hstack(rx.icon("log-out", size=17), rx.text("Sair da conta")), on_click=State.logout, class_name="sidebar-item vet-schedule-logout"), class_name="vet-schedule-identity", width="100%")
    content = rx.box(
        rx.hstack(rx.vstack(rx.text("Área da clínica", color="var(--vt-muted)"), rx.heading(State.clinic_section, size="7"), align="start"), rx.spacer(), rx.button(rx.icon("refresh-cw", size=17), "Atualizar", on_click=State.clinic_load, disabled=State.clinic_admin_loading, variant="soft"), width="100%", align="center"),
        rx.cond(State.clinic_admin_loading, rx.spinner()),
        rx.cond((State.clinic_admin_message != "") & (State.clinic_section != "Pets para adoção"), rx.text(State.clinic_admin_message, role="status")),
        rx.cond(State.clinic_section == "Veterinários",
            rx.vstack(
                rx.hstack(rx.button("Cadastrar veterinário", on_click=State.clinic_open_vet_form("novo"), disabled=State.clinic_admin_loading), rx.button("Vincular veterinário", on_click=State.clinic_open_vet_form("vinculo"), disabled=State.clinic_admin_loading, variant="soft"), wrap="wrap"),
                rx.cond(State.clinic_vet_form != "", _vet_form()),
                rx.cond(State.clinic_admin_vets.length() > 0, rx.vstack(rx.foreach(State.clinic_admin_vets, _vet_card), align="stretch", spacing="3"), rx.cond(State.clinic_admin_loaded & ~State.clinic_admin_loading, rx.text("Nenhum veterinário vinculado."))), align="stretch", spacing="4"),
            rx.vstack(_pet_form(), rx.heading("Pets cadastrados", size="4"), rx.cond(State.clinic_admin_pets.length() > 0, rx.foreach(State.clinic_admin_pets, _pet_card), rx.cond(State.clinic_admin_loaded & ~State.clinic_admin_loading, rx.text("Nenhum pet cadastrado."))), align="stretch", spacing="4")),
        as_="main", id="main-content", class_name="vet-schedule", width="100%", min_width="0", on_mount=State.clinic_load,
    )
    return layout_com_menu(content, pagina_ativa="clinica", navigation=navigation, actions=actions)
