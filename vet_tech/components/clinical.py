"""Agenda, booking wizard and structured clinical forms."""
import reflex as rx
from vet_tech.components.date_input import date_hint, calendar_panel

from vet_tech.features.auth.state import State


def notice() -> rx.Component:
    return rx.vstack(
        rx.cond(State.clinic_loading, rx.text("Carregando…", role="status")),
        rx.text(State.clinic_message, role="status"), align="stretch", width="100%",
    )


def pet_loading() -> rx.Component:
    return rx.vstack(
        rx.hstack(rx.spinner(size='3'), rx.text('Carregando dados do pet…'), align='center', spacing='3'),
        rx.skeleton(height='80px', width='100%'),
        rx.skeleton(height='80px', width='100%'),
        role='status', aria_live='polite', spacing='4', width='100%', padding='1rem',
    )


def tutor_clinical_content(content: rx.Component) -> rx.Component:
    return rx.box(
        rx.cond(State.is_loading_pet | State.clinic_loading, pet_loading(),
            rx.cond(State.tutor_clinical_loaded, content,
                rx.vstack(
                    rx.text(State.clinic_message, role='status'),
                    rx.cond(State.selected_pet_id != '', rx.button('Tentar novamente', on_click=State.load_tutor_clinical),
                        rx.button('Tentar novamente', on_click=State.retry_pet)),
                    align='stretch', spacing='3'))),
        aria_busy=State.is_loading_pet | State.clinic_loading, width='100%',
    )


def options(rows, value, change, placeholder, control_id=None):
    trigger_props = {"id": control_id} if control_id is not None else {}
    return rx.select.root(
        rx.select.trigger(placeholder=placeholder, width="100%", **trigger_props),
        rx.select.content(rx.foreach(rows, lambda row: rx.select.item(row["nome"], value=row["id"]))),
        value=value, on_change=change, disabled=State.clinic_busy, width="100%",
    )


def booking_dialog() -> rx.Component:
    day_grid = rx.grid(
        *[rx.text(day, size="1", align="center", color="var(--vt-muted)") for day in ("Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom")],
        rx.foreach(State.booking_days, lambda day: rx.button(
            day["label"], on_click=State.booking_choose_day(day["date"]),
            disabled=(day["disabled"] == "sim") | State.booking_busy,
            variant=rx.cond(State.booking_day == day["date"], "solid", "soft"),
            aria_label=day["date"], height="38px", min_width="0",
        )), columns="7", spacing="2", width="100%",
    )
    first = rx.vstack(
        rx.hstack(
            rx.icon_button(rx.icon("chevron-left"), aria_label="Mês anterior", on_click=State.booking_shift_month(-1)),
            rx.text(State.booking_month, weight="bold"),
            rx.icon_button(rx.icon("chevron-right"), aria_label="Próximo mês", on_click=State.booking_shift_month(1)),
            justify="between", width="100%",
        ), day_grid,
        rx.text("Dia selecionado: ", State.booking_day),
        rx.el.label("Horário (08h–17h)", html_for="booking-time"),
        rx.input(id="booking-time", type="time", min="08:00", max="17:00", value=State.booking_time,
                 on_change=State.set_booking_time, width="100%", disabled=State.booking_busy),
        rx.button("Continuar", on_click=State.booking_next, width="100%"),
        align="stretch", spacing="3", width="100%",
    )
    second = rx.vstack(
        rx.text(State.booking_day, " às ", State.booking_time, weight="bold"),
        rx.cond(State.has_pets,
            rx.vstack(
                rx.text("Pet"), options(State.pets, State.booking_pet, State.booking_choose_pet, "Escolha o pet"),
                rx.el.label("Motivo", html_for="booking-reason"),
                rx.text_area(id="booking-reason", value=State.booking_reason, on_change=State.set_booking_reason,
                             placeholder="Descreva o motivo da consulta", width="100%", disabled=State.booking_busy),
                rx.text("Veterinário"), options(State.booking_professionals, State.booking_professional,
                                              State.set_booking_professional, "Escolha o profissional"),
                rx.callout("Ao confirmar, você libera previamente o histórico deste pet ao veterinário escolhido. Você pode revogar o acesso em Consultas.", icon="shield-check"),
                rx.button("Confirmar agendamento", on_click=State.booking_submit,
                          loading=State.booking_busy, width="100%"), align="stretch", width="100%", spacing="3",
            ),
            rx.text("Cadastre um pet em Novo pet antes de confirmar um agendamento.")),
        rx.button("Voltar", on_click=State.booking_back, variant="outline", disabled=State.booking_busy),
        align="stretch", spacing="3", width="100%",
    )
    return rx.dialog.root(
        rx.dialog.trigger(rx.button(rx.icon("calendar-plus", size=18), "Agendar consulta", size="3")),
        rx.dialog.content(
            rx.dialog.title("Agendar consulta"),
            rx.dialog.description(rx.cond(State.booking_step == 1, "Etapa 1 de 2 — dia e horário", "Etapa 2 de 2 — pet e motivo")),
            rx.cond(State.booking_step == 1, first, second),
            rx.text(State.booking_message, role="status", margin_top="12px"),
            rx.dialog.close(rx.button("Cancelar", variant="ghost", disabled=State.booking_busy, margin_top="12px")),
            width="min(95vw, 540px)", max_height="90dvh", overflow_y="auto",
        ), open=State.booking_open, on_open_change=State.booking_set_open,
    )


def record_card(row, group: str, show_origin=True):
    names = {"vacinas": "vacina", "medicamentos": "nome", "doencas": "nome", "exames": "tipo", "diagnosticos": "nome"}
    fields = {
        "vacinas": [("data_aplicacao_legivel", "Aplicação"), ("lote", "Lote"), ("data_prox_dose_legivel", "Próxima dose")],
        "medicamentos": [("dose_legivel", "Dose"), ("frequencia", "Frequência"), ("via", "Via"), ("tipo", "Tipo"), ("data_inicio_legivel", "Início"), ("data_fim_legivel", "Fim")],
        "doencas": [("estado", "Estado"), ("data_evolucao_legivel", "Evolução"), ("descricao", "Descrição")],
        "diagnosticos": [("estado", "Estado"), ("data_diagnostico_legivel", "Diagnóstico"), ("observacoes", "Observações")],
        "exames": [("status", "Estado"), ("data_solicitacao_legivel", "Solicitação"), ("data_realizacao_legivel", "Realização"), ("data_legivel", "Data do registro anterior"), ("resultado", "Resultado")],
    }
    return rx.card(rx.vstack(
        rx.text(row.get(names.get(group, "nome"), "Registro"), weight="bold"),
        *[rx.cond(row.get(key, "") != "", rx.text(label, ": ", row.get(key, ""), size="2"))
          for key, label in fields[group]],
        rx.text(row.get("origem_legivel", ""), size="1"),
        rx.cond(row.get("veterinario_id", "") != "",
                rx.text("Veterinário: ", row.get("veterinario_nome", row.get("veterinario_id", "")), size="2")),
        rx.cond(show_origin & (row.get("consulta_id", "") != ""),
                rx.button("Ver consulta de origem", on_click=State.show_consultation_detail(row.get("consulta_id", "")), variant="outline")),
        align="stretch", spacing="2"), width="100%")


def records(group: str):
    return rx.vstack(
        rx.cond(State.history_rows.get(group, []).length() == 0, rx.text("Nenhum registro publicado para este pet.")),
        rx.foreach(State.history_rows.get(group, []), lambda row: record_card(row, group)),
        align="stretch", spacing="3", width="100%",
    )


def consultation_detail():
    return rx.vstack(
        rx.hstack(
            rx.button("Voltar à lista", on_click=State.set_detail_id(""), variant="outline"),
            rx.cond((State.detail.get("status", "") == "finalizada") & State.consultation_pdf_available,
                rx.button("Exportar PDF", on_click=State.request_consultation_pdf,
                          loading=State.pdf_export_busy, disabled=State.pdf_export_busy,
                          aria_label="Exportar PDF da consulta", variant="solid")),
            wrap="wrap", spacing="3"),
        rx.text(State.pdf_export_message, role="status", aria_live="polite"),
        rx.heading("Prontuário da consulta", size="5"),
        rx.text(State.detail.get("quando", "")),
        *[rx.cond(State.detail.get(key, "") != "", rx.text(label, ": ", State.detail.get(key, "")))
          for key, label in (("data_atendimento_legivel", "Data do atendimento"), ("iniciada_em_legivel", "Início real"),
                             ("finalizada_em_legivel", "Fim real"), ("retorno_previsto_legivel", "Retorno previsto"))],
        rx.text("Veterinário: ", State.detail.get("veterinario_id", "")),
        rx.text("Motivo: ", State.detail.get("motivo", "")),
        rx.text("Diagnóstico: ", State.detail.get("diagnostico", "")),
        rx.text("Observações: ", State.detail.get("obs", "")),
        *[rx.vstack(rx.heading(label, size="4"),
             rx.foreach(State.detail_sections.get(group, []), lambda row: record_card(row, group)),
             align="stretch", width="100%") for group, label in (("vacinas", "Vacinas"), ("medicamentos", "Medicamentos"),
                 ("diagnosticos", "Doenças"), ("exames", "Exames"))],
        align="stretch", spacing="4", width="100%",
    )


def tutor_consultations():
    return rx.vstack(
        rx.cond(State.detail_id != "", consultation_detail(), rx.vstack(
            rx.cond(State.consultation_rows.length() == 0, rx.text("Nenhuma consulta para este pet.")),
            rx.foreach(State.consultation_rows, lambda row: rx.card(rx.vstack(
                rx.hstack(rx.text(row["quando"], weight="bold"), rx.badge(row["status"]), wrap="wrap"),
                rx.text(row.get("motivo", "")),
                rx.text("Veterinário: ", row.get("veterinario_id", "")),
                rx.cond((row["status"] == "finalizada") | (row["status"] == "legado"),
                        rx.button("Ver prontuário", on_click=State.show_consultation_detail(row["id"]))),
                align="stretch", spacing="2"), width="100%")),
            align="stretch", width="100%", spacing="3")),
        rx.button('Carregar permissões e histórico de acessos', on_click=State.load_tutor_auxiliary(False),
                  disabled=State.auxiliary_loading, variant='outline'),
        rx.cond(State.auxiliary_loading, rx.hstack(rx.spinner(), rx.text('Carregando permissões e acessos…'), role='status')),
        rx.text(State.auxiliary_message, role='status'),
        rx.cond(State.auxiliary_message != '', rx.button('Tentar novamente: permissões e acessos',
                  on_click=State.load_tutor_auxiliary(True), disabled=State.auxiliary_loading)),
        rx.cond(State.auxiliary_loaded, rx.accordion.root(rx.accordion.item(
            header="Permissões e histórico de acessos", content=rx.vstack(
                rx.button('Atualizar permissões e acessos', on_click=State.load_tutor_auxiliary(True),
                          disabled=State.auxiliary_loading, variant='outline'),
                rx.foreach(State.access_rows, lambda row: rx.hstack(
                    rx.text("Veterinário ", row["veterinario_id"], " — ", row["status"]),
                    rx.button(rx.cond(row["status"] == "ativo", "Revogar", "Reativar"),
                              on_click=State.change_consent(row["id"], rx.cond(row["status"] == "ativo", "revogado", "ativo")),
                              disabled=State.clinic_busy), wrap="wrap")),
                rx.foreach(State.audit_rows, lambda row: rx.text(row.get("acao", ""), " — ", row.get("ocorrido_em_legivel", ""))),
                align="stretch", spacing="3")), collapsible=True, width="100%")),
        align="stretch", width="100%", spacing="4",
    )


def appointment_card(row):
    from vet_tech.components.veterinary_schedule import schedule_card
    return schedule_card(row, show_date=True)


def veterinary_content():
    from vet_tech.components.veterinary_schedule import schedule_content, consultations_content
    return rx.vstack(
        rx.hstack(rx.vstack(rx.heading(State.vet_section, size="7"),
                            rx.text(rx.cond(State.vet_section == "Horários", "Sua agenda do dia", "Próximas consultas e atendimentos pendentes"), color="var(--vt-muted)"),
                            align="start", spacing="1"), rx.spacer(),
                  rx.button(rx.icon("refresh-cw", size=17), "Atualizar", on_click=State.load_agenda, disabled=State.clinic_loading),
                  width="100%", align="center", wrap="wrap"),
        rx.cond(State.clinic_message != "", rx.text(State.clinic_message, role="status")),
        rx.cond(State.vet_section == "Horários", schedule_content(),
            consultations_content()),
        rx.hstack(rx.button("Anterior", on_click=State.agenda_page_by(-1), variant="ghost", disabled=(State.agenda_page <= 1) | State.clinic_loading),
                  rx.text("Página ", State.agenda_page, size="2", color="var(--vt-muted)"),
                  rx.button("Próxima", on_click=State.agenda_page_by(1), variant="ghost", disabled=(State.agenda_page * 25 >= State.agenda_total) | State.clinic_loading),
                  justify="center", align="center", wrap="wrap", width="100%"),
        align="stretch", spacing="5", width="100%",
    )


def prior_renderer(group):
    return lambda row: record_card(row, group, False)


def pet_basic_info(info):
    return rx.vstack(
        rx.text(info.get("nome", ""), weight="bold"),
        rx.text("Sexo: ", info.get("sexo", "Não informado")),
        rx.text("Nascimento: ", info.get("nascimento", "Não informado")),
        rx.text("Peso atual: ", info.get("peso", "Não informado")), align="stretch", spacing="1")


LINE_FIELDS = {
    "vacinas": [("vacina", "Vacina", "text"), ("lote", "Lote", "text"), ("data_aplicacao", "Data de aplicação", "date"), ("data_prox_dose", "Próxima dose (opcional)", "date")],
    "medicamentos": [("nome", "Medicamento", "text"), ("dose", "Dose", "number"), ("unidade", "Unidade", "text"),
                     ("frequencia", "Frequência", "text"), ("via", "Via", "text"), ("data_inicio", "Início", "date"), ("data_fim", "Fim", "date")],
    "doencas": [("data_diagnostico", "Data do diagnóstico", "date"), ("observacoes", "Observações", "text")],
    "exames": [("tipo", "Tipo de exame", "text"), ("data_solicitacao", "Solicitação", "date"), ("data_realizacao", "Realização", "date"), ("resultado", "Resultado em texto", "text")],
}


def line_change(group, row, key):
    return lambda value: State.clinical_line_field(group, row["linha_id"], key, value)


def header_change(key):
    return lambda value: State.clinical_field(key, value)


def line_renderer(group):
    return lambda row: clinical_line(row, group)


def clinical_line(row, group):
    special = []
    if group == "doencas":
        special += [rx.el.label("Doença", html_for="clinic-" + row["linha_id"] + "-doenca_id"),
            options(State.disease_options, row["doenca_id"],
                lambda value: State.clinical_line_field(group, row["linha_id"], "doenca_id", value),
                "Escolha a doença", control_id="clinic-" + row["linha_id"] + "-doenca_id")]
    choices = {"doencas": ("estado", ["ativa", "em_tratamento", "curada", "controlada"]),
               "medicamentos": ("tipo", ["continuo", "vermifugo", "antipulgas", "outro"]),
               "exames": ("status", ["solicitado", "realizado"])}
    if group in choices:
        key, items = choices[group]
        labels = {"em_tratamento": "Em tratamento", "continuo": "Contínuo", "vermifugo": "Vermífugo",
                  "antipulgas": "Antipulgas", "ativa": "Ativa", "curada": "Curada", "controlada": "Controlada",
                  "outro": "Outro", "solicitado": "Solicitado", "realizado": "Realizado"}
        special += [rx.el.label("Status" if key == "status" else key.capitalize(), html_for="clinic-" + row["linha_id"] + "-" + key),
            rx.select.root(
                rx.select.trigger(id="clinic-" + row["linha_id"] + "-" + key, placeholder="Selecione"),
                rx.select.content(*[rx.select.item(labels[item], value=item) for item in items]),
                value=row[key], on_change=lambda value: State.clinical_line_field(group, row["linha_id"], key, value),
                disabled=State.clinic_busy)]
    return rx.card(rx.vstack(
        *special,
        *[rx.vstack(rx.el.label(label, html_for="clinic-" + row["linha_id"] + "-" + key),
             (attendance_date_control(key, label, row[key], group, row["linha_id"])
              if kind == "date" else rx.input(
                  id="clinic-" + row["linha_id"] + "-" + key, type=kind, value=row[key],
                  placeholder=label, aria_label=label, on_change=line_change(group, row, key),
                  disabled=State.clinic_busy, width="100%")),
             *([date_hint(row[key])] if kind == "date" else []),
             align="stretch", width="100%", spacing="1")
          for key, label, kind in LINE_FIELDS[group]],
        rx.button("Remover registro", on_click=State.clinical_remove_line(group, row["linha_id"]),
                  variant="ghost", color_scheme="red", disabled=State.clinic_busy),
        align="stretch", spacing="3"), width="100%")


def attendance_icon(name: str, large: bool = False):
    return rx.center(rx.icon(name, size=26 if large else 20),
                     class_name="attendance-icon attendance-icon--large" if large else "attendance-icon")


def attendance_date_control(key, label, value, group="", line=""):
    parts = value.split("-")
    display = rx.cond((value != "") & (parts.length() == 3),
                      parts[2] + "/" + parts[1] + "/" + parts[0], "Selecionar data")
    control_id = "clinic-" + (line + "-" if group else "") + key
    return rx.el.button(
        rx.text(display), rx.icon("calendar-days", size=18), id=control_id, type="button",
        on_click=State.clinical_calendar_show(key, group, line), disabled=State.clinical_locked,
        aria_label=label, aria_haspopup="dialog", class_name="attendance-date-trigger",
    )


def attendance_calendar():
    return rx.dialog.root(
        calendar_panel(
            title="Cada cuidado tem seu dia", description="Escolha a data deste registro com carinho.",
            eyebrow=State.clinical_calendar_label, select_menu_class="attendance-date-select-menu",
            current_prefix="Data atual: ", current_label=State.clinical_calendar_date_label,
            month_name=State.clinical_calendar_month_name, year=State.clinical_calendar_year,
            years=State.clinical_calendar_years, days=State.clinical_calendar_days,
            previous_month=State.clinical_calendar_shift(-1), next_month=State.clinical_calendar_shift(1),
            choose_month=State.clinical_calendar_choose_month, choose_year=State.clinical_calendar_choose_year,
            choose_day=State.clinical_calendar_choose_day, legend="Selecione um dia para preencher o campo",
            back_label="Voltar sem alterar", class_name="vet-date-dialog attendance-date-dialog",
            extra_action=rx.el.button("Limpar data", on_click=State.clinical_calendar_choose_day(""),
                                      class_name="vet-date-back attendance-date-clear", disabled=State.clinical_locked),
            on_close_auto_focus=State.clinical_calendar_restore_focus,
        ), open=State.clinical_calendar_open, on_open_change=State.clinical_calendar_set_open,
    )


def attendance_field(key, label, kind, value):
    control = rx.text_area if key in ("diagnostico", "obs") else rx.input
    props = {"type": kind} if control == rx.input else {"resize": "vertical"}
    return rx.vstack(
        rx.el.label(label, html_for="clinic-" + key),
        (attendance_date_control(key, label, value) if kind == "date" else
         control(id="clinic-" + key, value=value, on_change=header_change(key),
                 disabled=State.clinic_busy, width="100%", **props)),
        *([date_hint(value)] if kind == "date" else []),
        align="stretch", spacing="2", class_name="attendance-field" + (" attendance-field--full" if kind != "date" else ""),
    )


def attendance_records(group, label, icon, empty):
    return rx.vstack(
        rx.flex(
            attendance_icon(icon),
            rx.heading(label, size="4"),
            rx.badge(State.clinical_lines[group].length(), class_name="attendance-count"),
            rx.spacer(),
            rx.button(rx.icon("plus", size=16), "Adicionar", on_click=State.clinical_add_line(group),
                      disabled=State.clinic_busy, class_name="attendance-button attendance-button--add"),
            align="center", gap="10px", width="100%", wrap="wrap",
        ),
        rx.cond(State.clinical_lines[group].length() == 0,
                rx.text(empty, class_name="attendance-empty")),
        rx.foreach(State.clinical_lines[group], line_renderer(group)),
        align="stretch", spacing="3", class_name="attendance-record-card",
    )


def history_patient_profile(sections):
    from vet_tech.components.veterinary_schedule import consultation_avatar
    info = State.prior_pet_info
    return rx.box(
        rx.box(consultation_avatar(info.get("foto", ""), "7", info.get("foto_ausente", "nao") == "sim"), class_name="history-profile-portrait",
               role="img", aria_label="Foto de " + info.get("nome", "pet")),
        rx.box(
            rx.hstack(rx.icon("paw-print", size=14), rx.text("Perfil do pet"), spacing="2", align="center", class_name="history-profile-eyebrow"),
            rx.heading(info.get("nome", "Pet"), size="6", class_name="history-profile-name"),
            rx.text("Uma história de cuidado, em cada registro.", class_name="history-profile-description"),
            class_name="history-profile-identity"),
        rx.box(*[
            rx.box(rx.text(State.prior_history.get(group, []).length(), class_name="history-profile-count"),
                   rx.text(label, class_name="history-profile-stat-label"), class_name="history-profile-stat")
            for group, label, _ in sections], class_name="history-profile-stats", role="group", aria_label="Registros publicados por categoria"),
        rx.box(*[
            rx.box(rx.icon(icon, size=16),
                   rx.vstack(rx.text(label, class_name="history-profile-fact-label"),
                             rx.text(info.get(key, "Não informado"), class_name="history-profile-fact-value"),
                             spacing="1", align="start"), class_name="history-profile-fact")
            for icon, label, key in (("venus-and-mars", "Sexo", "sexo"), ("calendar-heart", "Nascimento", "nascimento"), ("weight", "Peso informado", "peso"))],
            class_name="history-profile-facts"),
        class_name="attendance-history-pet history-profile", role="group", aria_label="Perfil de " + info.get("nome", "pet"),
    )


def attendance_history_dialog(pet_id=None, button_label="Consultar histórico anterior",
                              trigger_id="attendance-history-trigger", button_class="attendance-button attendance-history-button",
                              variant="outline", size="2", back_label="Voltar ao atendimento"):
    pet_id = State.clinical_pet_id if pet_id is None else pet_id
    sections = (("consultas", "Consultas", "stethoscope"), ("vacinas", "Vacinas", "syringe"),
                ("medicamentos", "Medicamentos", "pill"), ("doencas", "Doenças", "heart-pulse"),
                ("exames", "Exames", "microscope"))
    return rx.dialog.root(
        rx.dialog.trigger(rx.button(rx.icon("history", size=17), button_label,
            on_click=[State.prepare_prior_history(), State.open_prior_history(pet_id)],
            variant=variant, size=size, id=trigger_id, disabled=State.clinic_busy,
            class_name=button_class)),
        rx.dialog.content(
            rx.box(
                rx.hstack(rx.icon("folder-heart", size=20), rx.text("MEMÓRIAS DE CUIDADO"), spacing="2",
                          class_name="attendance-history-eyebrow"),
                rx.dialog.title("Histórico anterior", class_name="attendance-history-title"),
                rx.dialog.description("Cada cuidado faz parte dessa história. Consulte os registros publicados do pet.",
                                      class_name="attendance-history-description"),
                rx.box(rx.image(src="/mascote_logo.png", alt="", aria_hidden=True),
                       class_name="attendance-history-turtle", aria_hidden=True),
                rx.dialog.close(rx.button(rx.icon("x", size=20), aria_label="Fechar histórico",
                                           variant="ghost", class_name="attendance-history-close")),
                class_name="attendance-history-header"),
            rx.box(
                rx.cond(State.prior_history.length() > 0,
                    rx.vstack(
                        history_patient_profile(sections),
                        *[rx.box(
                            rx.hstack(rx.icon(icon, size=19), rx.heading(label, size="4"),
                                      rx.badge(State.prior_history.get(group, []).length()),
                                      spacing="3", align="center", class_name="attendance-history-section-title"),
                            rx.cond(State.prior_history.get(group, []).length() == 0,
                                rx.text("Nenhum registro publicado nesta categoria.", class_name="attendance-history-empty"),
                                rx.foreach(State.prior_history.get(group, []),
                                    (lambda row: rx.box(rx.text(row.get("quando", ""), weight="bold"),
                                        rx.text(row.get("diagnostico", "")), rx.text(row.get("obs", "")),
                                        class_name="attendance-history-consultation"))
                                    if group == "consultas" else prior_renderer(group))),
                            class_name="attendance-history-section") for group, label, icon in sections],
                        align="stretch", spacing="4", width="100%"),
                    rx.cond(State.prior_history_message != "",
                        rx.vstack(rx.icon("circle-alert", size=28), rx.text(State.prior_history_message, role="alert"),
                            rx.button("Tentar novamente", on_click=[State.prepare_prior_history(),
                                State.open_prior_history(pet_id)]),
                            align="center", class_name="attendance-history-feedback"),
                        rx.hstack(rx.spinner(), rx.text("Buscando a história deste pet…"), role="status",
                                  justify="center", class_name="attendance-history-feedback"))),
                class_name="attendance-history-body"),
            rx.flex(rx.text("Um olhar para o passado, mais cuidado no presente."),
                    rx.dialog.close(rx.button(back_label, variant="outline")),
                    align="center", justify="between", wrap="wrap", gap="12px", class_name="attendance-history-footer"),
            class_name="attendance-history-dialog", max_width="860px", width="calc(100vw - 32px)",
            on_close_auto_focus=State.restore_prior_history_focus(trigger_id),
        ),
    )


def attendance_patient():
    from vet_tech.components.veterinary_schedule import consultation_avatar
    info = State.clinical_pet_info
    return rx.box(
        rx.flex(
            rx.box(consultation_avatar(info.get("foto", ""), "7", info.get("foto_ausente", "nao") == "sim"),
                   class_name="attendance-patient-portrait", role="img", aria_label="Foto de " + State.clinical_pet_name),
            rx.vstack(
                rx.flex(
                    rx.heading(State.clinical_pet_name, size="6"),
                    rx.badge(rx.box(class_name="attendance-status-dot"),
                             rx.match(State.clinical_status,
                                      ("em_atendimento", "Em atendimento"),
                                      ("finalizada", "Finalizada"), ("agendada", "Agendada"), "Status indisponível"),
                             class_name="attendance-status"),
                    align="center", gap="12px", wrap="wrap",
                ),
                rx.flex(*[
                    rx.hstack(rx.icon(icon, size=15), rx.text(label, ": ", info.get(key, "Não informado")),
                              *([rx.cond(info.get(key, "Não informado") != "Não informado", rx.text("kg"))] if key == "peso" else []),
                              spacing="1", align="center", class_name="attendance-chip")
                    for key, label, icon in (("sexo", "Sexo", "venus-and-mars"),
                                             ("nascimento", "Nascimento", "calendar-days"),
                                             ("peso", "Peso atual", "weight"))], gap="8px", wrap="wrap"),
                spacing="3", align="stretch", flex="1", min_width="0",
            ),
            attendance_history_dialog(),
            align="center", gap="18px", wrap="wrap",
        ), class_name="attendance-patient",
    )


def attendance_content():
    from vet_tech.components.veterinary_schedule import consultation_status_led
    return rx.box(rx.el.link(rel="stylesheet", href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap"), rx.vstack(
        consultation_status_led(State.clinical_status, radius="23", class_name="vet-date-led consultations-status-led attendance-form-led"),
        rx.flex(
            rx.hstack(attendance_icon("stethoscope", True), rx.heading("Atendimento", size="7"), align="center", spacing="3"),
            rx.button(rx.icon("arrow-left", size=17), "Voltar às consultas",
                      on_click=State.leave_attendance(False), variant="outline", class_name="attendance-button"),
            justify="between", align="center", gap="16px", wrap="wrap", class_name="attendance-header",
        ),
        rx.box(notice(), class_name="attendance-notice"),
        rx.cond(State.clinical_id != "", rx.vstack(
            attendance_patient(),
            rx.hstack(rx.icon(rx.cond(State.clinical_dirty, "circle-dot", "circle-check"), size=15),
                      rx.text(rx.cond(State.clinical_dirty, "Há alterações não salvas", "Última versão confirmada"), role="status"),
                      spacing="2", align="center", class_name="attendance-confirmation"),
            rx.cond(State.clinical_status == "em_atendimento", rx.vstack(
                rx.box(
                    rx.heading("Dados do atendimento", size="5", class_name="attendance-section-title"),
                    rx.grid(*[
                        attendance_field(key, label, kind, value)
                        for key, label, kind, value in (
                            ("data_atendimento", "Data do atendimento", "date", State.clinical_date),
                            ("retorno_previsto", "Retorno (opcional)", "date", State.clinical_return),
                            ("motivo", "Motivo", "text", State.clinical_reason),
                            ("diagnostico", "Diagnóstico", "text", State.clinical_diagnosis),
                            ("obs", "Observações", "text", State.clinical_notes))],
                        class_name="attendance-fields"), width="100%",
                ),
                rx.box(
                    rx.heading("Registros clínicos", size="5", class_name="attendance-section-title"),
                    rx.grid(*[
                        attendance_records(group, label, icon, empty)
                        for group, label, icon, empty in (
                            ("vacinas", "Vacinas", "syringe", "Nenhuma vacina registrada"),
                            ("medicamentos", "Medicamentos", "pill", "Nenhum medicamento registrado"),
                            ("doencas", "Doenças", "heart-pulse", "Nenhuma doença registrada"),
                            ("exames", "Exames", "microscope", "Nenhum exame registrado"))],
                        class_name="attendance-records"), width="100%",
                ),
                rx.accordion.root(rx.accordion.item(
                    header=rx.hstack(attendance_icon("plus"), rx.text("Cadastrar doença no catálogo"), spacing="3", align="center"),
                    content=rx.vstack(
                        rx.el.label("Nome da doença", html_for="attendance-disease-name"),
                        rx.input(id="attendance-disease-name", placeholder="Nome da doença", value=State.disease_name,
                                 on_change=State.set_disease_name, aria_label="Nome da doença"),
                        rx.el.label("Descrição", html_for="attendance-disease-description"),
                        rx.text_area(id="attendance-disease-description", placeholder="Descrição", value=State.disease_description,
                                     on_change=State.set_disease_description, aria_label="Descrição da doença"),
                        rx.button("Cadastrar referência", on_click=State.create_disease, disabled=State.clinic_busy,
                                  class_name="attendance-button"), align="stretch", spacing="3")),
                    collapsible=True, class_name="attendance-catalog"),
                rx.flex(
                    rx.button(rx.icon("save", size=18), "Salvar rascunho", on_click=State.save_attendance(False),
                              disabled=State.clinic_busy, variant="outline", class_name="attendance-button"),
                    rx.button(rx.icon("check", size=18), "Terminar consulta", on_click=State.save_attendance(True),
                              loading=State.clinic_busy, class_name="attendance-button"),
                    justify="between", gap="14px", class_name="attendance-actions",
                ), align="stretch", spacing="6", width="100%"),
                rx.text("Atendimento finalizado. Os registros publicados estão disponíveis ao tutor.")),
            align="stretch", width="100%", spacing="4")),
        attendance_calendar(),
        rx.alert_dialog.root(rx.alert_dialog.content(
            rx.alert_dialog.title("Descartar alterações não salvas?"),
            rx.alert_dialog.description("A última versão salva permanece no banco. As alterações locais serão descartadas."),
            rx.hstack(rx.alert_dialog.cancel(rx.button("Continuar editando", on_click=State.set_clinical_confirm_leave(False))),
                      rx.alert_dialog.action(rx.button("Descartar e voltar", on_click=State.leave_attendance(True))), wrap="wrap")),
            open=State.clinical_confirm_leave),
        align="stretch", spacing="5", class_name="attendance-glass"), class_name="attendance-page attendance-page--" + State.clinical_status)
