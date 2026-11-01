import reflex as rx

from vet_tech.features.auth.state import State


def _pet_photo(pet) -> rx.Component:
    return rx.box(
        rx.cond(
            pet["foto"] != "",
            rx.image(
                src=pet["foto"],
                alt=pet["nome"],
                width="100%",
                height="100%",
                object_fit="cover",
                border_radius="50%",
            ),
            rx.icon("paw-print", size=30, color="var(--vt-green)"),
        ),
        display="flex",
        align_items="center",
        justify_content="center",
        width="88px",
        height="88px",
        flex_shrink="0",
        background="var(--vt-icon-bg)",
        border_radius="50%",
        overflow="hidden",
    )


def _select_scope() -> rx.Component:
    return rx.vstack(
        rx.text("Mostrar", size="2", color="var(--vt-muted)"),
        rx.select.root(
            rx.select.trigger(placeholder="Todos os pets", width="min(100%, 320px)"),
            rx.select.content(
                rx.select.item("Todos os pets", value="todos"),
                rx.foreach(
                    State.pets,
                    lambda pet: rx.select.item(pet["nome"], value=pet["id"]),
                ),
            ),
            value=State.dashboard_scope,
            on_change=State.set_dashboard_scope,
            width="min(100%, 320px)",
        ),
        align="start",
        spacing="1",
    )


def _action_button(label: str, icon_name: str, callback, primary: bool = False) -> rx.Component:
    return rx.button(
        rx.icon(icon_name, size=18),
        label,
        on_click=callback,
        variant="solid" if primary else "outline",
        color_scheme="green",
        white_space="normal",
    )


def _event_text(pet) -> rx.Component:
    return rx.cond(
        pet["proximo_evento"]["data"] != "",
        rx.vstack(
            rx.text(pet["proximo_evento"]["tipo"], weight="bold", color="var(--vt-text)"),
            rx.text(pet["proximo_evento"]["data"], size="2", color="var(--vt-muted)"),
            align="start",
            spacing="1",
        ),
        rx.text("Nenhum próximo evento registrado.", size="2", color="var(--vt-muted)"),
    )


def _followups(pet) -> rx.Component:
    return rx.vstack(
        rx.cond(
            pet["acompanhamentos"].length() > 0,
            rx.vstack(
                rx.foreach(
                    pet["acompanhamentos"],
                    lambda item: rx.hstack(
                        rx.icon("circle-alert", size=17, color="var(--vt-green)"),
                        rx.vstack(
                            rx.text(item["texto"], color="var(--vt-text)"),
                            rx.cond(
                                item["data"] != "",
                                rx.text(item["data"], size="1", color="var(--vt-muted)"),
                            ),
                            align="start",
                            spacing="1",
                        ),
                        align="start",
                        width="100%",
                        padding="var(--vt-space-3)",
                        background="var(--vt-icon-bg)",
                        border_radius="var(--vt-radius-control)",
                    ),
                ),
                rx.cond(
                    pet["acompanhamentos_truncados"],
                    rx.text(
                        "A lista está limitada. Consulte o prontuário para ver os demais registros.",
                        size="2",
                        color="var(--vt-muted)",
                    ),
                ),
                align="stretch",
                spacing="2",
                width="100%",
            ),
            rx.text(
                "Nenhum item de acompanhamento identificado nos registros consultados.",
                color="var(--vt-muted)",
            ),
        ),
        align="stretch",
        spacing="2",
        width="100%",
    )


def _recent_activity(pet) -> rx.Component:
    return rx.vstack(
        rx.cond(
            pet["atividade_recente"].length() > 0,
            rx.foreach(
                pet["atividade_recente"],
                lambda row: rx.hstack(
                    rx.cond(
                        row["tipo"] == "Vacina",
                        rx.icon("syringe", size=18, color="var(--vt-green)"),
                        rx.icon("clipboard-list", size=18, color="var(--vt-green)"),
                    ),
                    rx.vstack(
                        rx.text(row["nome"], weight="bold", color="var(--vt-text)"),
                        rx.text(row["tipo"], size="1", color="var(--vt-muted)"),
                        align="start",
                        spacing="1",
                    ),
                    rx.spacer(),
                    rx.text(row["data"], size="2", color="var(--vt-muted)"),
                    align="center",
                    width="100%",
                    padding_y="var(--vt-space-3)",
                    border_bottom="1px solid var(--vt-border)",
                ),
            ),
            rx.text("Nenhuma consulta finalizada ou vacina registrada para exibir.", color="var(--vt-muted)"),
        ),
        align="stretch",
        spacing="1",
        width="100%",
    )


def _metric(title: str, value, detail, icon_name: str) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.box(
                    rx.icon(icon_name, size=19, color="var(--vt-green)"),
                    display="flex",
                    align_items="center",
                    justify_content="center",
                    width="38px",
                    height="38px",
                    background="var(--vt-icon-bg)",
                    border_radius="var(--vt-radius-control)",
                ),
                rx.text(title, size="2", color="var(--vt-muted)"),
                align="center",
                spacing="2",
            ),
            rx.text(value, size="5", weight="bold", color="var(--vt-text)"),
            rx.text(detail, size="2", color="var(--vt-muted)"),
            align="start",
            spacing="2",
            width="100%",
        ),
        width="100%",
        background="var(--vt-surface)",
    )


def _individual_pet(pet) -> rx.Component:
    return rx.vstack(
        rx.card(
            rx.hstack(
                _pet_photo(pet),
                rx.vstack(
                    rx.heading(pet["nome"], size="6", color="var(--vt-text)"),
                    rx.text(pet["especie"], " · ", pet["raca"], color="var(--vt-muted)"),
                    rx.text(pet["idade"], color="var(--vt-muted)"),
                    rx.text(pet["mensagem_acompanhamento"], size="2", color="var(--vt-muted)"),
                    align="start",
                    spacing="1",
                ),
                rx.spacer(),
                align="center",
                width="100%",
                wrap="wrap",
            ),
            width="100%",
            background="var(--vt-surface)",
        ),
        rx.grid(
            _metric(
                "Peso cadastrado",
                rx.cond(pet["peso"] != "", pet["peso"], "Não informado"),
                "Valor registrado",
                "scale",
            ),
            _metric(
                "Próxima vacina",
                rx.cond(pet["proxima_vacina"]["nome"] != "", pet["proxima_vacina"]["nome"], "Sem próxima dose informada"),
                pet["proxima_vacina"]["data"],
                "syringe",
            ),
            _metric(
                "Última consulta",
                rx.cond(pet["ultima_consulta"]["data"] != "", pet["ultima_consulta"]["data"], "Não registrada"),
                "Consulta finalizada",
                "clipboard-list",
            ),
            columns=rx.breakpoints(initial="1", sm="2", lg="3"),
            spacing="4",
            width="100%",
        ),
        rx.grid(
            rx.card(
                rx.vstack(
                    rx.heading("Próximo evento registrado", size="4"),
                    _event_text(pet),
                    align="start",
                    spacing="3",
                    width="100%",
                ),
                width="100%",
            ),
            rx.card(
                rx.vstack(
                    rx.heading("Itens registrados para acompanhar", size="4"),
                    _followups(pet),
                    align="start",
                    spacing="3",
                    width="100%",
                ),
                width="100%",
            ),
            columns=rx.breakpoints(initial="1", lg="2"),
            spacing="4",
            width="100%",
        ),
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.heading("Atividade recente", size="4"),
                    rx.spacer(),
                    _action_button(
                        "Histórico de vacinas",
                        "syringe",
                        State.dashboard_open_clinical(pet["id"], "vacinas"),
                    ),
                    align="center",
                    width="100%",
                    wrap="wrap",
                ),
                _recent_activity(pet),
                align="stretch",
                spacing="3",
                width="100%",
            ),
            width="100%",
        ),
        rx.hstack(
            _action_button(
                "Agendar consulta",
                "calendar-plus",
                State.dashboard_book_pet(pet["id"]),
                primary=True,
            ),
            _action_button(
                "Abrir prontuário",
                "clipboard-list",
                State.dashboard_open_clinical(pet["id"], "inicio"),
            ),
            align="center",
            wrap="wrap",
            width="100%",
        ),
        align="stretch",
        spacing="4",
        width="100%",
    )


def _overview_pet(pet) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                _pet_photo(pet),
                rx.vstack(
                    rx.heading(pet["nome"], size="5", color="var(--vt-text)"),
                    rx.text(pet["especie"], " · ", pet["raca"], " · ", pet["idade"], color="var(--vt-muted)"),
                    align="start",
                    spacing="1",
                ),
                align="center",
                width="100%",
                wrap="wrap",
            ),
            rx.divider(),
            rx.vstack(
                rx.text(
                    "Peso cadastrado: ",
                    rx.cond(pet["peso"] != "", pet["peso"], "Não informado"),
                    color="var(--vt-text)",
                ),
                rx.text(
                    "Próxima vacina: ",
                    rx.cond(
                        pet["proxima_vacina"]["nome"] != "",
                        pet["proxima_vacina"]["nome"] + " · " + pet["proxima_vacina"]["data"],
                        "Sem próxima dose informada",
                    ),
                    color="var(--vt-text)",
                ),
                rx.text(
                    "Última consulta: ",
                    rx.cond(
                        pet["ultima_consulta"]["data"] != "",
                        pet["ultima_consulta"]["data"],
                        "Não registrada",
                    ),
                    color="var(--vt-text)",
                ),
                rx.text(pet["mensagem_acompanhamento"], size="2", color="var(--vt-muted)"),
                _event_text(pet),
                align="start",
                spacing="2",
                width="100%",
            ),
            rx.hstack(
                _action_button(
                    "Ver Dashboard do pet",
                    "paw-print",
                    State.set_dashboard_scope(pet["id"]),
                ),
                _action_button(
                    "Agendar para este pet",
                    "calendar-plus",
                    State.dashboard_book_pet(pet["id"]),
                    primary=True,
                ),
                _action_button(
                    "Vacinas",
                    "syringe",
                    State.dashboard_open_clinical(pet["id"], "vacinas"),
                ),
                _action_button(
                    "Prontuário",
                    "clipboard-list",
                    State.dashboard_open_clinical(pet["id"], "inicio"),
                ),
                align="center",
                wrap="wrap",
                width="100%",
            ),
            align="stretch",
            spacing="3",
            width="100%",
        ),
        width="100%",
        background="var(--vt-surface)",
    )


def dashboard_content() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.text("Área do tutor", size="2", color="var(--vt-muted)"),
                    rx.heading("Dashboard", size="7", color="var(--vt-text)"),
                    align="start",
                    spacing="1",
                ),
                rx.spacer(),
                _select_scope(),
                rx.cond(
                    State.dashboard_scope != "todos",
                    rx.button(
                        rx.icon("calendar-plus", size=18),
                        "Agendar consulta",
                        on_click=State.dashboard_book_pet(State.dashboard_scope),
                        color_scheme="green",
                    ),
                ),
                align="center",
                wrap="wrap",
                width="100%",
            ),
            rx.cond(
                State.dashboard_loading,
                rx.hstack(
                    rx.spinner(color="var(--vt-green)"),
                    rx.text("Carregando dados do Dashboard...", color="var(--vt-muted)"),
                    role="status",
                    aria_live="polite",
                    align="center",
                    padding="var(--vt-space-6)",
                ),
                rx.cond(
                    State.dashboard_error != "",
                    rx.vstack(
                        rx.text(State.dashboard_error, color="var(--vt-error)", role="alert"),
                        rx.button("Tentar novamente", on_click=State.load_dashboard, variant="outline"),
                        align="start",
                        spacing="3",
                    ),
                    rx.cond(
                        State.dashboard_pets.length() == 0,
                        rx.card(
                            rx.vstack(
                                rx.icon("paw-print", size=34, color="var(--vt-green)"),
                                rx.heading("Nenhum pet cadastrado", size="5"),
                                rx.text(
                                    "Cadastre um pet para visualizar os dados disponíveis no Dashboard.",
                                    color="var(--vt-muted)",
                                ),
                                rx.button(
                                    "Cadastrar pet",
                                    on_click=State.set_pet_modal(True),
                                    color_scheme="green",
                                ),
                                align="center",
                                spacing="3",
                                width="100%",
                            ),
                            width="100%",
                        ),
                        rx.cond(
                            State.dashboard_is_all_pets,
                            rx.vstack(
                                rx.heading("Seus pets", size="5"),
                                rx.foreach(State.dashboard_visible_pets, _overview_pet),
                                align="stretch",
                                spacing="4",
                                width="100%",
                            ),
                            rx.foreach(State.dashboard_visible_pets, _individual_pet),
                        ),
                    ),
                ),
            ),
            align="stretch",
            spacing="5",
            width="100%",
        ),
        as_="main",
        id="main-content",
        width="100%",
        min_width="0",
        padding=rx.breakpoints(initial="16px", lg="40px"),
    )


def tutor_dashboard_page() -> rx.Component:
    from vet_tech.components.navigation import clinical_menu_actions
    from vet_tech.components.sidebar import layout_com_menu

    return rx.cond(
        State.is_authenticated & (State.profile == "tutor"),
        layout_com_menu(
            dashboard_content(),
            pagina_ativa="dashboard",
            actions=clinical_menu_actions(),
        ),
        rx.fragment(),
    )
