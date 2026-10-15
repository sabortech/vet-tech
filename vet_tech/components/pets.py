import reflex as rx

from vet_tech.features.auth.state import State


def species_select() -> rx.Component:
    return rx.select.root(
        rx.select.trigger(placeholder="Selecione a espécie"),
        rx.select.content(
            rx.select.group(
                rx.foreach(
                    State.species_options,
                    lambda species: rx.select.item(
                        species["nome"],
                        value=species["id"],
                    ),
                )
            )
        ),
        value=State.selected_species_id,
        on_change=State.select_species,
        required=True,
    )


def breed_select() -> rx.Component:
    return rx.select.root(
        rx.select.trigger(placeholder="Raça (opcional; deixe vazio para SRD)"),
        rx.select.content(
            rx.select.group(
                rx.foreach(
                    State.breed_options,
                    lambda breed: rx.select.item(
                        breed["nome"],
                        value=breed["id"],
                    ),
                )
            )
        ),
        value=State.selected_breed_id,
        on_change=State.select_breed,
        disabled=State.selected_species_id == "",
    )


def pet_form() -> rx.Component:
    return rx.vstack(
        rx.heading("Cadastrar pet", size="4"),
        rx.input(
            placeholder="Nome do pet",
            value=State.pet_name,
            on_change=State.set_pet_name,
            width="100%",
        ),
        species_select(),
        breed_select(),
        rx.input(
            placeholder="Sexo (opcional)",
            value=State.pet_sex,
            on_change=State.set_pet_sex,
            width="100%",
        ),
        rx.input(
            type="date",
            value=State.pet_birth_date,
            on_change=State.set_pet_birth_date,
            width="100%",
        ),
        rx.input(
            placeholder="Peso atual (opcional)",
            type="number",
            min="0",
            step="1",
            value=State.pet_weight,
            on_change=State.set_pet_weight,
            width="100%",
        ),
        rx.input(
            placeholder="Cor da pelagem (opcional)",
            value=State.pet_coat_color,
            on_change=State.set_pet_coat_color,
            width="100%",
        ),
        rx.input(
            placeholder="Microchip (opcional)",
            type="number",
            min="0",
            step="1",
            value=State.pet_microchip,
            on_change=State.set_pet_microchip,
            width="100%",
        ),
        rx.upload(
            rx.text("Selecionar foto (opcional)"),
            id="pet-photo",
            accept={"image/jpeg": [".jpg", ".jpeg"], "image/png": [".png"], "image/webp": [".webp"]},
            max_files=1,
            max_size=5 * 1024 * 1024,
            width="100%",
        ),
        rx.foreach(rx.selected_files("pet-photo"), rx.text),
        rx.button(
            "Cadastrar pet",
            on_click=State.create_pet(rx.upload_files(upload_id="pet-photo")),
            disabled=State.is_busy,
        ),
        rx.text(State.pet_message, role="status"),
        align="stretch",
        spacing="3",
        width="100%",
    )


def pet_list() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.heading("Meus pets", size="4"),
            rx.spacer(),
            rx.button("Atualizar lista", on_click=State.refresh_pets),
            width="100%",
            align="center",
        ),
        rx.cond(
            State.is_loading_pets,
            rx.text("Carregando pets..."),
            rx.cond(
                State.has_pets,
                rx.vstack(
                    rx.foreach(
                        State.pets,
                        lambda pet: rx.box(
                            rx.text(pet["nome"], weight="bold"),
                            rx.text(pet["especie"], " · ", pet["raca"]),
                            rx.text(pet["sexo"], " · ", pet["data_nasc"]),
                            rx.button(
                                "Abrir ", pet["nome"],
                                on_click=State.open_pet(pet["id"]),
                                variant="outline",
                                margin_top="0.5rem",
                            ),
                            rx.cond(
                                State.selected_pet_id == pet["id"],
                                rx.text("Pet selecionado", size="1", color="#50753F"),
                            ),
                            width="100%",
                            padding_y="0.75rem",
                            border_bottom="1px solid #d9dedb",
                        ),
                    ),
                    width="100%",
                    align="stretch",
                    spacing="0",
                ),
                rx.text("Você ainda não cadastrou pets."),
            ),
        ),
        width="100%",
        align="stretch",
        spacing="3",
    )


def pet_detail_row(label: str, key: str) -> rx.Component:
    return rx.vstack(
        rx.text(label, weight="bold", size="2"),
        rx.text(rx.cond(State.selected_pet[key] != "", State.selected_pet[key], "Não informado")),
        align="start",
        spacing="1",
    )


def pet_details() -> rx.Component:
    """Pet-scoped area; future clinical sections use State.selected_pet_id."""
    return rx.box(
        rx.cond(
            State.pet_target_id != "",
            rx.vstack(
                rx.button("Voltar à lista", on_click=State.close_pet, variant="outline"),
                rx.cond(
                    State.is_loading_pet,
                    rx.text("Carregando dados do pet...", role="status"),
                    rx.cond(
                        State.selected_pet_id != "",
                        rx.vstack(
                            rx.heading(State.selected_pet["nome"], size="5"),
                            rx.text(State.selected_pet["especie"], " · ", State.selected_pet["raca"]),
                            rx.grid(
                                pet_detail_row("Sexo", "sexo"),
                                pet_detail_row("Nascimento", "data_nasc"),
                                pet_detail_row("Peso atual", "peso_atual"),
                                pet_detail_row("Pelagem", "cor_pelo"),
                                pet_detail_row("Microchip", "num_microchip"),
                                columns=rx.breakpoints(initial="1", sm="2"),
                                spacing="4",
                                width="100%",
                            ),
                            align="stretch",
                            spacing="3",
                            width="100%",
                        ),
                        rx.button("Tentar novamente", on_click=State.retry_pet),
                    ),
                ),
                width="100%",
                align="stretch",
                spacing="3",
            ),
            rx.text("Escolha um pet na lista para abrir seus dados."),
        ),
        rx.text(State.pet_detail_message, role="status", margin_top="0.5rem"),
        id="pet-details",
        width="100%",
        padding="1rem",
        border="1px solid #d9dedb",
        border_radius="0.75rem",
        aria_label="Dados do pet selecionado",
    )


def profile_view() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.hstack(
                rx.heading("Perfil do tutor", size="6"),
                rx.spacer(),
                rx.button("Sair", on_click=State.logout),
                width="100%",
                align="center",
            ),
            pet_details(),
            pet_list(),
            rx.divider(),
            pet_form(),
            align="stretch",
            spacing="5",
            width="100%",
            max_width="48rem",
        ),
        padding_y="2rem",
    )
