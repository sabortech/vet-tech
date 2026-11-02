"""Visual agenda composed from the existing authenticated clinical state."""
import reflex as rx

from vet_tech.features.auth.state import State
from vet_tech.features.navigation.state import NavigationState
from vet_tech.features.clinical.state import MONTHS


def veterinary_navigation(in_settings=False):
    from vet_tech.features.navigation.state import VETERINARIAN_DESTINATIONS
    items = []
    for label, icon, destination in (("Horários", "clock-3", "/?secao=horarios"),
                                      ("Consultas", "clipboard-list", "/?secao=consultas"),
                                      ("Configurações", "settings", "/configuracoes")):
        assert destination in VETERINARIAN_DESTINATIONS
        active = (label == "Configurações") if in_settings else ((State.vet_section == label) & (label != "Configurações"))
        contents = rx.hstack(rx.icon(icon, size=20, class_name="sidebar-item__icon"),
                            rx.text(label, class_name="sidebar-item__label"), class_name="sidebar-item__contents")
        props = dict(class_name=rx.cond(active, "sidebar-item sidebar-item--active", "sidebar-item"),
                     title=label, custom_attrs={"aria-label": label, "aria-current": rx.cond(active, "page", "false")})
        if in_settings or label == "Configurações":
            items.append(rx.link(contents, href=destination, on_click=NavigationState.close_drawer, **props))
        else:
            items.append(rx.el.button(contents, on_click=[State.vet_navigate(label), NavigationState.close_drawer], **props))
    return rx.fragment(*items)


def veterinary_actions(in_settings=False):
    from vet_tech.features.settings.state import SettingsState
    return rx.vstack(
        rx.box(rx.icon("user-round", size=24), class_name="vet-schedule-identity-icon"),
        rx.box(rx.text(State.identity_name, weight="bold"), rx.text("Veterinário(a)", size="2"),
               class_name="sidebar-item__label", text_align="center", width="100%"),
        rx.el.button(rx.hstack(rx.icon("log-out", size=18, class_name="sidebar-item__icon"),
                             rx.text("Sair", class_name="sidebar-item__label"), class_name="sidebar-item__contents"),
                     on_click=SettingsState.request_action("logout") if in_settings else State.logout,
                     class_name="sidebar-item vet-schedule-logout", title="Sair", aria_label="Sair"),
        class_name="vet-schedule-identity", align="center", spacing="2", width="100%",
    )


def schedule_card(row):
    return rx.box(
        rx.hstack(
            rx.avatar(src=row.get("pet_foto", ""), fallback="🐾", size="4", radius="full",
                      custom_attrs={"aria-label": rx.cond(row["autorizado"] == "sim", "Foto de " + row["pet_nome"], "Acesso revogado")}),
            rx.vstack(
                rx.text(rx.cond(row["autorizado"] == "sim", row["pet_nome"], "Acesso revogado"), weight="bold", class_name="vet-schedule-pet-name"),
                rx.text(rx.cond(row["autorizado"] == "sim", row.get("motivo", "") , "Autorização revogada pelo tutor."), size="2", class_name="vet-schedule-reason"),
                rx.hstack(rx.icon("clock-3", size=13), rx.text(row["hora"], size="2"), align="center", spacing="1"),
                align="start", spacing="1", min_width="0", flex="1",
            ),
            align="start", spacing="3", width="100%",
        ),
        rx.hstack(
            rx.box(row["status_label"], class_name="vet-schedule-status"),
            rx.cond(row["autorizado"] == "sim",
                rx.hstack(
                    rx.button("Histórico", on_click=State.open_prior_history(row.get("pet_id", "")), variant="ghost", size="1", disabled=State.clinic_busy),
                    rx.cond(row["status"] != "finalizada",
                        rx.button(rx.cond(row["status"] == "em_atendimento", "Retomar", "Começar consulta"),
                                  on_click=State.start_consultation(row["id"]), disabled=State.clinic_busy, size="1", variant="soft")),
                    wrap="wrap", spacing="2", align="center",
                )),
            justify="between", align="center", wrap="wrap", spacing="2", margin_top="12px", width="100%",
        ),
        class_name="vet-schedule-card vet-schedule-card--" + row["status"],
        custom_attrs={"data-appointment-id": row["id"]},
    )


def schedule_hour(hour):
    return rx.box(
        rx.text(rx.cond(hour < 10, "0", "") + hour.to_string() + ":00", class_name="vet-schedule-hour-label"),
        rx.box(rx.foreach(State.agenda_rows, lambda row: rx.cond(row["hora_grupo"] == hour.to_string(), schedule_card(row))),
               class_name="vet-schedule-hour-cards"),
        class_name="vet-schedule-hour", role="group", aria_label=hour.to_string() + " horas",
    )


def summary(icon, label, value):
    return rx.box(rx.box(rx.icon(icon, size=21), class_name="vet-schedule-stat-icon"),
                  rx.vstack(rx.text(label, size="2", color="var(--vt-muted)"), rx.text(value, size="6", weight="bold"),
                            align="start", spacing="1"), class_name="vet-schedule-stat")


def calendar_select(options, value, on_change, label, kind):
    return rx.select.root(
        rx.select.trigger(
            rx.hstack(rx.text(value), rx.icon("chevron-down", size=17, class_name="vet-date-select-chevron"),
                      align="center", justify="between", width="100%", spacing="2"),
            aria_label=label, class_name="vet-date-select-trigger vet-date-select-trigger--" + kind,
        ),
        rx.select.content(
            rx.select.group(rx.foreach(options, lambda option: rx.select.item(option, value=option, class_name="vet-date-select-option"))),
            position="popper", side="bottom", side_offset=8, align="start",
            custom_attrs={"avoidCollisions": False}, class_name="vet-date-select-menu",
        ), value=value, on_change=on_change,
    )


def date_picker():
    return rx.dialog.root(
        rx.dialog.trigger(rx.el.button(
            rx.icon("calendar-days", size=21), class_name="vet-date-calendar-button",
            title="Escolher data", aria_label="Escolher data", disabled=State.clinic_loading,
        )),
        rx.dialog.content(
            rx.el.svg(
                rx.el.svg.rect(x="1.5", y="1.5", rx="24.5", ry="24.5",
                               custom_attrs={"pathLength": 100}, class_name="vet-date-led-track"),
                class_name="vet-date-led", aria_hidden="true", focusable="false",
            ),
            rx.box(
                rx.box(
                    rx.box(rx.icon("sparkles", size=16), rx.text("Sua agenda, com carinho"), class_name="vet-date-eyebrow"),
                    rx.dialog.title("Um dia de cada vez", class_name="vet-date-title"),
                    rx.dialog.description("Escolha uma data para acompanhar seus atendimentos.", class_name="vet-date-description"),
                    rx.image(src="/espreitando.png", alt="", class_name="vet-date-turtle", aria_hidden="true"),
                    rx.box(rx.icon("calendar-check", size=18), rx.text("Na agenda: ", State.agenda_short_date), class_name="vet-date-current"),
                    class_name="vet-date-welcome",
                ),
                rx.box(
                    rx.hstack(rx.text("Escolher data", weight="bold", size="4"), rx.spacer(),
                        rx.dialog.close(rx.el.button(rx.icon("x", size=19), class_name="vet-date-close", aria_label="Fechar calendário")),
                        align="center", margin_bottom="24px"),
                    rx.hstack(
                        rx.el.button(rx.icon("chevron-left", size=20), on_click=State.agenda_calendar_shift(-1), aria_label="Mês anterior", class_name="vet-date-month-arrow"),
                        calendar_select([name.capitalize() for name in MONTHS], State.agenda_calendar_month_name,
                                        State.agenda_calendar_choose_month, "Mês do calendário", "month"),
                        calendar_select(State.agenda_calendar_years, State.agenda_calendar_year,
                                        State.agenda_calendar_choose_year, "Ano do calendário", "year"),
                        rx.el.button(rx.icon("chevron-right", size=20), on_click=State.agenda_calendar_shift(1), aria_label="Próximo mês", class_name="vet-date-month-arrow"),
                        align="center", justify="between", spacing="2", class_name="vet-date-month-controls",
                    ),
                    rx.box(*[rx.text(name) for name in ("Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom")], class_name="vet-date-weekdays"),
                    rx.box(rx.foreach(State.agenda_calendar_days, lambda day: rx.el.button(
                        day["label"], on_click=State.agenda_choose_day(day["date"]), disabled=day["date"] == "",
                        aria_label=day["date"], aria_pressed=day["selected"] == "sim",
                        class_name=rx.cond(day["selected"] == "sim", "vet-date-day is-selected",
                                           rx.cond(day["today"] == "sim", "vet-date-day is-today", "vet-date-day")),
                    )), class_name="vet-date-days", role="group", aria_label="Dias do mês"),
                    rx.hstack(rx.box(class_name="vet-date-today-dot"), rx.text("Hoje", size="2"),
                              rx.spacer(), rx.text("Selecione um dia para abrir a agenda", size="1"),
                              class_name="vet-date-legend", align="center", wrap="wrap", spacing="2"),
                    rx.dialog.close(rx.el.button("Voltar à agenda", class_name="vet-date-back")),
                    class_name="vet-date-month-panel",
                ), class_name="vet-date-layout",
            ),
            class_name="vet-date-dialog", width="min(780px, calc(100vw - 32px))", max_width="780px",
        ), open=State.agenda_calendar_open, on_open_change=State.agenda_calendar_set_open,
    )


def schedule_content():
    return rx.vstack(
        rx.box(
            rx.hstack(
                rx.button(rx.icon("chevron-left", size=19), on_click=State.agenda_day_by(-1), variant="ghost", aria_label="Dia anterior", disabled=State.clinic_loading),
                rx.text(State.agenda_date_label, weight="bold", class_name="vet-schedule-date-label"),
                rx.button(rx.icon("chevron-right", size=19), on_click=State.agenda_day_by(1), variant="ghost", aria_label="Próximo dia", disabled=State.clinic_loading),
                align="center", justify="center", spacing="2", class_name="vet-schedule-date-navigation",
            ),
            rx.hstack(
                rx.el.button(rx.icon("calendar-check", size=18), "Hoje", on_click=State.agenda_today,
                             class_name="vet-date-today-button", disabled=State.clinic_loading),
                date_picker(),
                align="center", spacing="3", class_name="vet-schedule-date-controls",
            ),
            rx.box(rx.foreach(State.agenda_week, lambda day: rx.el.button(
                rx.text(day["label"]), rx.text(day["day"], weight="bold"),
                on_click=State.agenda_choose_day(day["date"]), disabled=State.clinic_loading,
                class_name=rx.cond(State.agenda_day == day["date"], "vet-schedule-week-day is-selected", "vet-schedule-week-day"),
                aria_label=day["date"], aria_pressed=(State.agenda_day == day["date"]),
            )), class_name="vet-schedule-week"),
            class_name="vet-schedule-calendar",
        ),
        rx.cond(State.clinic_loading,
            rx.hstack(rx.spinner(), rx.text("Carregando agenda…"), role="status", padding="24px"),
            rx.cond(State.clinic_message == "", rx.fragment(
                rx.box(summary("calendar-days", "Consultas no dia", State.agenda_total),
                       summary("circle-check", "Concluídas nesta página", State.agenda_completed),
                       summary("stethoscope", "Em atendimento nesta página", State.agenda_in_progress),
                       class_name="vet-schedule-summary"),
                rx.cond(State.agenda_rows.length() == 0,
                    rx.box(rx.icon("calendar-heart", size=36), rx.heading("Seu dia está tranquilo", size="4"),
                           rx.text("Nenhuma consulta agendada para esta data.", color="var(--vt-muted)"),
                           class_name="vet-schedule-empty", role="status")),
                rx.box(rx.hstack(rx.text("Agenda do dia", weight="bold"), rx.spacer(),
                                  rx.text("Horário de Brasília", size="2", color="var(--vt-muted)"),
                                  class_name="vet-schedule-timeline-header", wrap="wrap"),
                       rx.foreach(State.agenda_hours, schedule_hour),
                       class_name="vet-schedule-timeline", aria_label="Calendário vertical de consultas"),
            ))),
        align="stretch", spacing="5", width="100%", aria_busy=State.clinic_loading,
    )
