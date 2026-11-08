import reflex as rx
from reflex.components.radix.themes.components.tooltip import Tooltip

from vet_tech.features.auth.state import State
from vet_tech.components.date_input import perimeter_led


class _VaccineTooltip(Tooltip):
    """Radix accepts ReactNode content; allow a formatted legend in Reflex."""

    content: rx.Component


def _vaccine_legend(status) -> rx.Component:
    statuses = (
        ("futura", "Verde", "var(--vaccine-legend-green)", "mais de 7 dias até a data prevista."),
        ("proxima", "Amarelo", "var(--vaccine-legend-yellow)", "dose prevista entre 1 e 7 dias."),
        ("hoje", "Âmbar", "var(--vaccine-legend-amber)", "dose prevista para hoje."),
        ("ultrapassada", "Vermelho", "var(--vaccine-legend-red)", "a data prevista já passou; confira os registros."),
        ("sem-data", "Apagado", "var(--vaccine-legend-muted)", "sem próxima dose registrada."),
    )
    return rx.vstack(
        rx.text("Cores do prazo da próxima dose", weight="bold"),
        rx.text(
            "Situação atual: ",
            rx.match(
                status,
                *[(key, rx.text.span(label, color=color, weight="bold"))
                  for key, label, color, _description in statuses],
                rx.text.span("Apagado", color="var(--vaccine-legend-muted)", weight="bold"),
            ),
            margin_bottom="6px",
        ),
        *[
            rx.text(rx.text.span(label + ": ", color=color, weight="bold"), description)
            for _key, label, color, description in statuses
        ],
        rx.text("Data ultrapassada não confirma que a vacina deixou de ser aplicada.", margin_top="6px"),
        rx.text("Clique na barra para abrir Vacinas deste pet."),
        class_name="dashboard-vaccine-legend",
        align="stretch",
        spacing="1",
    )


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
    return rx.hstack(
        rx.icon("sliders-horizontal", size=18, color="var(--vt-muted)"),
        rx.text("Mostrar", size="2", color="var(--vt-muted)"),
        rx.select.root(
            rx.select.trigger(placeholder="Todos os pets", width="100%", aria_label="Mostrar pets"),
            rx.select.content(
                rx.select.item("Todos os pets", value="todos"),
                rx.foreach(
                    State.pets,
                    lambda pet: rx.select.item(pet["nome"], value=pet["id"]),
                ),
            ),
            value=State.dashboard_scope,
            on_change=State.set_dashboard_scope,
        ),
        align="center",
        spacing="3",
        class_name="dashboard-scope",
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
    return rx.box(
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
        class_name="dashboard-individual-metric",
    )


def _individual_pet(pet) -> rx.Component:
    return rx.box(
        perimeter_led("vet-date-led dashboard-card-led", "18"),
        rx.vstack(
        rx.box(
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
            class_name="dashboard-individual-identity",
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
            rx.box(
                rx.vstack(
                    rx.heading("Próximo evento registrado", size="4"),
                    _event_text(pet),
                    align="start",
                    spacing="3",
                    width="100%",
                ),
                width="100%",
            ),
            rx.box(
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
        rx.box(
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
            width="100%", class_name="dashboard-individual-activity",
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
        width="100%", class_name="dashboard-individual-content",
        ),
        class_name="dashboard-pet-card dashboard-individual-card dashboard-pet-card--" + pet["indicador_vacina"]["estado"],
        as_="article",
    )


def _overview_metric(title: str, value, icon_name: str, detail="") -> rx.Component:
    return rx.box(
        rx.icon(icon_name, size=19, aria_hidden="true"),
        rx.text(title, class_name="dashboard-pet-metric__label"),
        rx.text(value, class_name="dashboard-pet-metric__value"),
        rx.cond(detail != "", rx.text(detail, class_name="dashboard-pet-metric__detail")),
        class_name="dashboard-pet-metric",
    )


def _overview_pet(pet) -> rx.Component:
    return rx.box(
        perimeter_led("vet-date-led dashboard-card-led", "10"),
        rx.box(
            rx.avatar(
                src=pet["foto"],
                fallback="🐾",
                alt=pet["nome"],
                radius="small",
                class_name="dashboard-pet-photo",
            ),
            rx.box(
                rx.box(
                    rx.heading(pet["nome"], as_="h3", class_name="dashboard-pet-name"),
                    _selected_pet_context_button(pet),
                    rx.image(src="/consultation-pdf/mascote-v.png", alt="", aria_hidden="true", class_name="dashboard-pet-stamp"),
                    class_name="dashboard-pet-identity",
                ),
                rx.text(pet["especie"], " · ", pet["raca"], " · ", pet["idade"], class_name="dashboard-pet-description"),
                rx.box(
                    _overview_metric("Peso cadastrado", rx.cond(pet["peso"] != "", pet["peso"], "Não informado"), "scale"),
                    _overview_metric("Próxima vacina", rx.cond(pet["proxima_vacina"]["nome"] != "", pet["proxima_vacina"]["nome"], "Sem próxima dose informada"), "syringe", pet["proxima_vacina"]["data"]),
                    _overview_metric("Última consulta", rx.cond(pet["ultima_consulta"]["data"] != "", pet["ultima_consulta"]["data"], "Não registrada"), "calendar-days"),
                    class_name="dashboard-pet-metrics",
                ),
                _VaccineTooltip.create(
                    rx.el.button(
                        rx.box(
                            rx.box(class_name="dashboard-vaccine-led", aria_hidden="true"),
                            rx.text(pet["indicador_vacina"]["texto"], as_="span"),
                            class_name="dashboard-vaccine-status",
                        ),
                        rx.cond(
                            pet["indicador_vacina"]["data"] != "",
                            rx.text(pet["indicador_vacina"]["nome"], " · ", pet["indicador_vacina"]["data"], as_="span", class_name="dashboard-vaccine-reference"),
                        ),
                        rx.box(
                            rx.el.span(class_name="dashboard-pet-track__sweep"),
                            rx.image(src="/consultation-pdf/mascote-v.png", alt="", class_name="dashboard-pet-track__turtle"),
                            class_name="dashboard-pet-track",
                            aria_hidden="true",
                        ),
                        type="button",
                        on_click=State.dashboard_open_clinical(pet["id"], "vacinas"),
                        aria_label="Abrir Vacinas de " + pet["nome"] + ": " + pet["indicador_vacina"]["texto"] + rx.cond(pet["indicador_vacina"]["data"] != "", ". " + pet["indicador_vacina"]["nome"] + " · " + pet["indicador_vacina"]["data"], ""),
                        class_name="dashboard-pet-vaccines dashboard-pet-vaccines--" + pet["indicador_vacina"]["estado"],
                    ),
                    content=_vaccine_legend(pet["indicador_vacina"]["estado"]),
                    side="top",
                    delay_duration=250,
                    collision_padding=16,
                    background="var(--vaccine-legend-bg)",
                    color="var(--vaccine-legend-text)",
                    max_width="min(340px, calc(100vw - 32px))",
                    font_size="12px",
                    line_height="1.6",
                ),
                class_name="dashboard-pet-summary",
            ),
            class_name="dashboard-pet-top",
        ),
        rx.box(
            rx.heading("Acompanhamento detalhado", as_="h4", class_name="dashboard-pet-followup__title"),
            rx.text(pet["mensagem_acompanhamento"]),
            rx.cond(pet["acompanhamentos"].length() > 0, _followups(pet)),
            _event_text(pet),
            class_name="dashboard-pet-followup",
        ),
        rx.box(
            _action_button("Ver Dashboard do pet", "paw-print", State.set_dashboard_scope(pet["id"])),
            _action_button("Agendar consulta", "calendar-plus", State.dashboard_book_pet(pet["id"]), primary=True),
            _action_button("Vacinas", "syringe", State.dashboard_open_clinical(pet["id"], "vacinas")),
            _action_button("Prontuário", "clipboard-list", State.dashboard_open_clinical(pet["id"], "inicio")),
            class_name="dashboard-pet-actions",
        ),
        as_="article",
        class_name="dashboard-pet-card dashboard-pet-card--" + pet["indicador_vacina"]["estado"],
    )


def dashboard_content() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.heading("Seus pets em foco", size="7", color="var(--vt-text)", class_name="dashboard-title"),
                    rx.text("Acompanhe a saúde e os próximos cuidados dos seus pets", color="var(--vt-muted)"),
                    align="start",
                    spacing="1",
                    class_name="dashboard-heading",
                ),
                rx.spacer(),
                rx.button(
                    rx.icon("refresh-cw", size=17),
                    "Atualizar",
                    on_click=State.load_dashboard(True),
                    disabled=State.dashboard_loading,
                    variant="solid",
                ),
                align="center",
                wrap="wrap",
                width="100%",
                class_name="dashboard-header",
            ),
            rx.hstack(
                _select_scope(),
                rx.spacer(),
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
                class_name="dashboard-toolbar",
            ),
            rx.fragment(
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
                ),
                rx.cond(
                    State.dashboard_loading & (State.dashboard_visible_pets.length() == 0),
                    rx.fragment(),
                    rx.cond(
                        State.dashboard_error != "",
                        rx.vstack(
                            rx.text(State.dashboard_error, color="var(--vt-error)", role="alert"),
                            rx.button("Tentar novamente", on_click=State.load_dashboard(True), variant="outline"),
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
                                    rx.box(rx.foreach(State.dashboard_visible_pets, _overview_pet), class_name="dashboard-pets-grid"),
                                    align="stretch",
                                    spacing="4",
                                    width="100%",
                                ),
                                rx.foreach(State.dashboard_visible_pets, _individual_pet),
                            ),
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
        class_name="dashboard-page",
        width="100%",
        min_width="0",
    )


def _selected_pet_context_button(pet) -> rx.Component:
    return rx.cond(
        State.dashboard_is_all_pets & (State.dashboard_context_pet_id == pet["id"]),
        rx.button(
            rx.avatar(src=pet["foto"], fallback="🐾", alt="", size="1", radius="full"),
            rx.box(
                rx.text("Selecionado em Meus Pets", class_name="dashboard-selected-pet-label"),
                rx.text(pet["nome"], class_name="dashboard-selected-pet-name"),
                min_width="0",
            ),
            on_click=State.set_dashboard_scope(pet["id"]),
            aria_label="Ver Dashboard de " + pet["nome"] + ", selecionado em Meus Pets",
            class_name="dashboard-selected-pet",
        ),
    )


def tutor_dashboard_page() -> rx.Component:
    from vet_tech.components.clinical import booking_dialog
    from vet_tech.components.sidebar import layout_com_menu

    return rx.cond(
        State.is_authenticated & (State.profile == "tutor"),
        rx.fragment(
            layout_com_menu(
                dashboard_content(),
                pagina_ativa="dashboard",
            ),
            booking_dialog(show_trigger=False),
        ),
        rx.fragment(),
    )
