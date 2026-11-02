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
        rx.icon("paw-print", size=80, aria_hidden=True, class_name="vet-profile-watermark"),
        rx.hstack(
            rx.box(
                rx.cond(State.veterinarian_initials != "", rx.text(State.veterinarian_initials), rx.icon("user-round", size=24)),
                rx.box(rx.icon("stethoscope", size=12), class_name="vet-profile-avatar-detail", aria_hidden=True),
                class_name="vet-profile-avatar", aria_hidden=True,
            ),
            rx.vstack(rx.text("Veterinário(a)", class_name="vet-profile-eyebrow"),
                      rx.text(State.identity_name, class_name="vet-profile-name", title=State.identity_name),
                      spacing="1", align="start", class_name="sidebar-item__label vet-profile-details"),
            align="center", spacing="3", width="100%", class_name="vet-profile-header",
        ),
        rx.box(
            rx.hstack(rx.cond(State.identity_professional_loading, rx.spinner(size="1"), rx.icon("id-card", size=19)),
                      rx.vstack(rx.text("Registro profissional", class_name="vet-profile-registration-label"),
                                rx.text(State.veterinarian_registration, class_name="vet-profile-registration-value"),
                                spacing="1", align="start", min_width="0"), align="center", spacing="2"),
            rx.cond(State.identity_professional_error,
                rx.el.button("Tentar novamente", on_click=State.load_professional_identity, class_name="vet-profile-retry")),
            class_name="sidebar-item__label vet-profile-registration", role="status", aria_live="polite",
        ),
        rx.el.button(rx.hstack(rx.icon("log-out", size=17, class_name="sidebar-item__icon"),
                             rx.text("Sair da conta", class_name="sidebar-item__label"), class_name="sidebar-item__contents"),
                     on_click=SettingsState.request_action("logout") if in_settings else State.logout,
                     class_name="sidebar-item vet-schedule-logout", title="Sair", aria_label="Sair"),
        class_name="vet-schedule-identity", align="stretch", spacing="3", width="100%",
        on_mount=State.load_professional_identity,
    )


def schedule_card(row, show_date=False):
    from vet_tech.components.clinical import attendance_history_dialog
    return rx.box(
        rx.hstack(
            rx.box(
                rx.cond(row.get("pet_foto", "") != "",
                    rx.box(consultation_avatar(row.get("pet_foto", ""), "4"), role="img", aria_label="Foto de " + row["pet_nome"]),
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
                    rx.cond((row["status"] == "agendada") | (row["status"] == "em_atendimento"),
                        rx.button(rx.cond(row["status"] == "em_atendimento", "Retomar", "Começar consulta"),
                                  on_click=State.start_consultation(row["id"]), disabled=State.clinic_busy, size="1", variant="soft", class_name="vet-schedule-start-button")),
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


def consultation_avatar(src, size):
    return rx.box(
        rx.avatar(src=src, fallback="", radius="full", size=size),
        rx.icon("paw-print", size=26, aria_hidden=True, class_name="consultations-avatar-paw"),
        class_name="consultations-avatar",
    )


def consultation_status_led(status, radius="16", class_name="vet-date-led consultations-status-led"):
    return rx.cond((status == "agendada") | (status == "em_atendimento") | (status == "finalizada"),
        perimeter_led(class_name, radius))


def consultation_card(row):
    from vet_tech.components.clinical import attendance_history_dialog
    allowed = row["autorizado"] == "sim"
    return rx.box(
        consultation_status_led(row["status"]),
        rx.el.button(
            consultation_avatar(row.get("pet_foto", ""), "5"),
            rx.box(rx.text(rx.cond(allowed, row["pet_nome"], "Acesso revogado"), class_name="consultations-pet-name"),
                   rx.text(rx.cond(allowed, row.get("motivo", ""), "Autorização revogada pelo tutor."), class_name="consultations-muted")),
            on_click=State.select_consultation(row["id"]), disabled=~allowed,
            class_name="consultations-patient-button", aria_label="Selecionar " + row["pet_nome"],
            aria_pressed=(State.consultation_selected == row["id"]),
        ),
        rx.box(rx.hstack(rx.icon("calendar-days", size=16), rx.text(row["quando"]), spacing="2", align="center"),
               rx.box(row["status_label"], class_name="consultations-status"), class_name="consultations-card-details"),
        rx.cond(allowed, rx.vstack(
            rx.cond((row["status"] == "agendada") | (row["status"] == "em_atendimento"), rx.button(
                rx.cond(row["status"] == "em_atendimento", "Retomar atendimento", "Iniciar atendimento"),
                on_click=State.start_consultation(row["id"]), disabled=State.clinic_busy, class_name="consultations-start")),
            attendance_history_dialog(pet_id=row.get("pet_id", ""), button_label="Ver prontuário",
                trigger_id="consultations-history-" + row["id"], button_class="consultations-history",
                variant="outline", size="2", back_label="Voltar às consultas"), spacing="2", align="stretch",
            class_name="consultations-card-actions")),
        class_name=rx.cond(State.consultation_selected == row["id"], "consultations-card is-selected", "consultations-card") + " consultations-card--" + row["status"],
        custom_attrs={"data-consultation-id": row["id"]},
    )


def consultation_fact(icon, label, value):
    return rx.box(rx.hstack(rx.icon(icon, size=15), rx.text(label, weight="bold"), spacing="2", align="center"),
                  rx.text(value, class_name="consultations-fact-value"), class_name="consultations-fact")


def consultation_patient_summary():
    info = State.consultation_info
    return rx.box(
        consultation_status_led(info.get("status", "")),
        rx.hstack(rx.icon("heart-pulse", size=19), rx.text("Resumo do paciente", weight="bold"), spacing="2", align="center", class_name="consultations-summary-title"),
        rx.cond(State.consultation_summary_loading,
            rx.hstack(rx.spinner(), rx.text("Carregando resumo…"), role="status", padding_y="24px"),
            rx.cond(State.consultation_summary_error != "", rx.text(State.consultation_summary_error, role="alert"),
                rx.cond(info.get("nome", "") != "", rx.fragment(
                    rx.hstack(consultation_avatar(info.get("foto", ""), "6"),
                        rx.vstack(rx.text(info.get("nome", ""), class_name="consultations-pet-name"),
                                  rx.text("Nascimento: ", info.get("nascimento", ""), class_name="consultations-muted"), align="start", spacing="1"), spacing="3", align="center", margin_y="20px"),
                    rx.text(State.identity_name, weight="bold"),
                    rx.text("Veterinário(a) responsável", class_name="consultations-muted"),
                    rx.box(
                        consultation_fact("weight", "Peso informado", info.get("peso", "Não informado")),
                        consultation_fact("syringe", "Última vacina", info.get("ultima_vacina", "Não informada")),
                        consultation_fact("shield-alert", "Alergias", info.get("alergias", "Alergias não informadas")),
                        consultation_fact("calendar-check", "Última consulta", info.get("ultima_consulta", "Não informada")),
                        class_name="consultations-facts"),
                    rx.text("Alergias conforme doenças e diagnósticos registrados no prontuário.", class_name="consultations-source"),
                    rx.text("Motivo da consulta", weight="bold", margin_top="20px"),
                    rx.text(info.get("motivo", "Não informado"), class_name="consultations-muted"),
                ), rx.box(rx.icon("mouse-pointer-click", size=28), rx.text("Selecione um paciente", weight="bold"),
                          rx.text("Toque no nome ou na foto para consultar o resumo do prontuário.", class_name="consultations-muted"),
                          class_name="consultations-summary-empty")))),
        rx.box(rx.image(src="/mascote/babyturtle.png", alt="", aria_hidden=True, class_name="consultations-baby-turtle"),
               rx.text("Um cuidado de cada vez.", class_name="consultations-muted"), class_name="consultations-summary-footer"),
        class_name="consultations-summary consultations-summary--" + info.get("status", ""), aria_busy=State.consultation_summary_loading,
    )


def consultations_content():
    return rx.box(
        rx.box(
            rx.box(*[rx.el.button(label, on_click=State.filter_consultations("tab", label),
                class_name=rx.cond(State.consultation_tab == label, "consultations-tab is-active", "consultations-tab"),
                aria_pressed=(State.consultation_tab == label)) for label in ("Pendentes", "Hoje", "Próximas", "Concluídas", "Canceladas")],
                class_name="consultations-tabs", role="group", aria_label="Período das consultas"),
            rx.input(rx.input.slot(rx.icon("search", size=18)), placeholder="Buscar por nome do pet",
                value=State.consultation_search, on_change=lambda value: State.filter_consultations("search", value),
                debounce_timeout=400, radius="full", aria_label="Buscar por nome do pet", class_name="consultations-search"),
            rx.hstack(
                rx.icon("sliders-horizontal", size=18, aria_hidden=True, class_name="consultations-filter-icon"),
                rx.select(["Todos os estados", "Agendada", "Em atendimento", "Concluída", "Cancelada"],
                    value=State.consultation_status, on_change=lambda value: State.filter_consultations("status", value),
                    aria_label="Filtrar por estado da consulta", radius="full", class_name="consultations-filter"),
                class_name="consultations-filter-control", align="center", spacing="2"),
            class_name="consultations-toolbar"),
        rx.box(
            rx.box(rx.hstack(rx.text("Atendimentos", weight="bold"), rx.spacer(),
                rx.text(State.agenda_total, " resultados", class_name="consultations-muted"), width="100%", margin_bottom="12px"),
                rx.cond(State.clinic_loading, rx.hstack(rx.spinner(), rx.text("Carregando consultas…"), role="status", padding="24px"),
                    rx.cond(State.clinic_message == "", rx.cond(State.upcoming_rows.length() == 0,
                        rx.box(rx.icon("calendar-heart", size=32), rx.text("Nenhuma consulta encontrada", weight="bold"),
                            rx.text("Experimente outro período ou nome de pet.", class_name="consultations-muted"), class_name="consultations-empty"),
                        rx.foreach(State.upcoming_rows, consultation_card)))),
                class_name="consultations-list", aria_busy=State.clinic_loading),
            consultation_patient_summary(), class_name="consultations-columns"),
        class_name="consultations-page",
    )
