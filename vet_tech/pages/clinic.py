"""Área de clínica, seguindo o layout visual da área veterinária."""
import reflex as rx

from vet_tech.components.sidebar import layout_com_menu
from vet_tech.components.pets import pet_form
from vet_tech.features.auth.state import State
from vet_tech.features.navigation.state import NavigationState


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


def clinic_area() -> rx.Component:
    navigation = rx.fragment(_nav_item("Veterinários", "stethoscope"), _nav_item("Pets para adoção", "paw-print"))
    actions = rx.vstack(rx.text("Clínica", class_name="vet-profile-eyebrow"), rx.text(State.clinic_name, class_name="vet-profile-name"), rx.text(State.identity_name), rx.el.button(rx.hstack(rx.icon("log-out", size=17), rx.text("Sair da conta")), on_click=State.logout, class_name="sidebar-item vet-schedule-logout"), class_name="vet-schedule-identity", width="100%")
    content = rx.box(
        rx.hstack(rx.vstack(rx.text("Área da clínica", color="var(--vt-muted)"), rx.heading(State.clinic_section, size="7"), align="start"), rx.spacer(), rx.button(rx.icon("refresh-cw", size=17), "Atualizar", on_click=State.clinic_load, disabled=State.clinic_admin_loading, variant="soft"), width="100%", align="center"),
        rx.cond(State.clinic_admin_loading, rx.spinner()),
        rx.cond((State.clinic_admin_message != "") & (State.clinic_section != "Pets para adoção"), rx.text(State.clinic_admin_message, role="status")),
        rx.cond(State.clinic_section == "Veterinários",
            rx.cond(State.clinic_admin_vets.length() > 0, rx.vstack(rx.foreach(State.clinic_admin_vets, _vet_card), align="stretch", spacing="3"), rx.cond(State.clinic_admin_loaded & ~State.clinic_admin_loading, rx.text("Nenhum veterinário vinculado."))),
            rx.vstack(_pet_form(), rx.heading("Pets cadastrados", size="4"), rx.cond(State.clinic_admin_pets.length() > 0, rx.foreach(State.clinic_admin_pets, _pet_card), rx.cond(State.clinic_admin_loaded & ~State.clinic_admin_loading, rx.text("Nenhum pet cadastrado."))), align="stretch", spacing="4")),
        as_="main", id="main-content", class_name="vet-schedule", width="100%", min_width="0", on_mount=State.clinic_load,
    )
    return layout_com_menu(content, pagina_ativa="clinica", navigation=navigation, actions=actions)
