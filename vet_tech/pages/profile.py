import reflex as rx

from vet_tech.components.navigation import sidebar
from vet_tech.components.pets import pet_details, pet_list
from vet_tech.features.auth.state import State


def tutor_area() -> rx.Component:
    return rx.hstack(
        sidebar(),
        rx.box(
            rx.hstack(
                rx.vstack(rx.text("Área do tutor", size="2", color="#53635A"),
                          rx.heading(State.active_section, size="7"), align="start", spacing="1"),
                rx.spacer(),
                rx.cond(State.selected_pet_id != "", rx.badge(State.selected_pet["nome"], size="2")),
                align="center", width="100%", margin_bottom="2rem",
            ),
            rx.cond(State.pet_picker_open | (State.pet_target_id == ""),
                    rx.vstack(rx.text("Escolha um pet para continuar ou cadastre em Novo pet."), pet_list(),
                              align="stretch", width="100%", spacing="4"),
                    rx.cond(State.active_section == "Início", pet_details(),
                            rx.vstack(
                                rx.cond(State.is_loading_pet, rx.text("Carregando dados do pet…", role="status")),
                                rx.cond(State.selected_pet_id != "",
                                        rx.text("Esta seção ainda não está disponível. Os registros serão integrados nas próximas entregas."),
                                        pet_details()),
                                align="stretch", width="100%",
                            ))),
            rx.text(State.pet_message, role="status", margin_top="1rem"),
            as_="main", id="main-content", width="100%", min_width="0", min_height="100dvh",
            padding=rx.breakpoints(initial="24px 16px", lg="40px"),
            margin_left=rx.breakpoints(initial="72px", lg="0"),
        ),
        rx.cond(State.sidebar_expanded, rx.box(
            rx.button("Fechar menu", on_click=State.toggle_sidebar, width="100%", height="100%",
                      variant="ghost", aria_label="Fechar menu", opacity="0"),
            position="fixed", inset="0", background="rgba(0,0,0,.3)", z_index="19",
            display=rx.breakpoints(initial="block", lg="none"),
        )),
        width="100%", align="start", spacing="0", background="#FAFCF8", color="#1A3629",
    )


def veterinarian_area() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.hstack(rx.heading("Área do veterinário", size="6"), rx.spacer(),
                      rx.button("Sair", on_click=State.logout), width="100%"),
            rx.text(State.identity_name),
            rx.text("Seu cadastro profissional está ativo. O acesso aos pets dependerá da autorização do tutor, em uma próxima entrega."),
            align="stretch", spacing="5", padding_y="2rem",
        ),
    )


def profile_view() -> rx.Component:
    return rx.cond(State.profile == "tutor", tutor_area(),
                   rx.cond(State.profile == "veterinario", veterinarian_area(),
                           rx.vstack(rx.text("Não foi possível identificar a sessão."), rx.button("Sair", on_click=State.logout))))
