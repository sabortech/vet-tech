"""Visual agenda composed from the existing authenticated clinical state."""
import reflex as rx

from vet_tech.features.auth.state import State
from vet_tech.features.navigation.state import NavigationState
from vet_tech.components.date_input import calendar_panel, perimeter_led


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


def schedule_card(row, show_date=False):
    from vet_tech.components.clinical import attendance_history_dialog
    return rx.box(
        rx.hstack(
            rx.box(
                rx.cond(row.get("pet_foto", "") != "",
                    rx.avatar(src=row.get("pet_foto", ""), fallback="🐾", size="4", radius="full",
                              custom_attrs={"aria-label": "Foto de " + row["pet_nome"]}),
                    rx.center(rx.icon("paw-print", size=22), class_name="vet-schedule-avatar-fallback",
                              role="img", aria_label=rx.cond(row["autorizado"] == "sim", "Pet sem foto", "Acesso revogado"))),
                perimeter_led("vet-date-led vet-schedule-avatar-led", "50%"),
                class_name="vet-schedule-avatar-frame",
            ),
            rx.vstack(
                *([rx.text(row.get("quando", ""), size="1", class_name="vet-schedule-reason")] if show_date else []),
                rx.text(rx.cond(row["autorizado"] == "sim", row["pet_nome"], "Acesso revogado"), weight="bold", class_name="vet-schedule-pet-name"),
                rx.text(rx.cond(row["autorizado"] == "sim", row.get("motivo", "") , "Autorização revogada pelo tutor."), size="2", class_name="vet-schedule-reason"),
                rx.hstack(rx.icon("clock-3", size=13), rx.text(row["hora"], size="2"), align="center", spacing="1"),
                align="start", spacing="1", min_width="0", flex="1",
            ),
            align="start", spacing="3", width="100%",
        ),
        rx.hstack(
            rx.box(rx.icon(rx.match(row["status"], ("finalizada", "circle-check"),
                                      ("em_atendimento", "stethoscope"), "calendar-clock"), size=12),
                   row["status_label"], class_name="vet-schedule-status"),
            rx.cond(row["autorizado"] == "sim",
                rx.hstack(
                    attendance_history_dialog(pet_id=row.get("pet_id", ""), button_label="Histórico",
                        trigger_id="agenda-history-" + row["id"], button_class="vet-schedule-history-button",
                        variant="soft", size="1", back_label="Voltar às consultas" if show_date else "Voltar à agenda"),
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


def date_picker():
    return rx.dialog.root(
        rx.dialog.trigger(rx.el.button(
            rx.icon("calendar-days", size=21), class_name="vet-date-calendar-button",
            title="Escolher data", aria_label="Escolher data", disabled=State.clinic_loading,
        )),
        calendar_panel(
            title="Um dia de cada vez", description="Escolha uma data para acompanhar seus atendimentos.",
            current_prefix="Na agenda: ", current_label=State.agenda_short_date,
            month_name=State.agenda_calendar_month_name, year=State.agenda_calendar_year,
            years=State.agenda_calendar_years, days=State.agenda_calendar_days,
            previous_month=State.agenda_calendar_shift(-1), next_month=State.agenda_calendar_shift(1),
            choose_month=State.agenda_calendar_choose_month, choose_year=State.agenda_calendar_choose_year,
            choose_day=State.agenda_choose_day, legend="Selecione um dia para abrir a agenda", back_label="Voltar à agenda",
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
                rx.box(perimeter_led("vet-date-led vet-schedule-timeline-led", "15"),
                       rx.hstack(rx.text("Agenda do dia", weight="bold"), rx.spacer(),
                                  rx.text("Horário de Brasília", size="2", color="var(--vt-muted)"),
                                  class_name="vet-schedule-timeline-header", wrap="wrap"),
                       rx.foreach(State.agenda_hours, schedule_hour),
                       class_name="vet-schedule-timeline", aria_label="Calendário vertical de consultas"),
            ))),
        align="stretch", spacing="5", width="100%", aria_busy=State.clinic_loading,
    )
