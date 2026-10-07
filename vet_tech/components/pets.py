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
            pet_form(),
            rx.divider(),
            pet_list(),
            align="stretch",
            spacing="5",
            width="100%",
            max_width="48rem",
        ),
        padding_y="2rem",
    )
