"""Agenda, booking wizard and structured clinical forms."""
import reflex as rx

from vet_tech.features.auth.state import State


def notice() -> rx.Component:
    return rx.vstack(
        rx.cond(State.clinic_loading, rx.text("Carregando…", role="status")),
        rx.text(State.clinic_message, role="status"), align="stretch", width="100%",
    )


def options(rows, value, change, placeholder):
    return rx.select.root(
        rx.select.trigger(placeholder=placeholder, width="100%"),
        rx.select.content(rx.foreach(rows, lambda row: rx.select.item(row["nome"], value=row["id"]))),
        value=value, on_change=change, disabled=State.clinic_busy, width="100%",
    )


def booking_dialog() -> rx.Component:
    day_grid = rx.grid(
        *[rx.text(day, size="1", align="center", color="#53635A") for day in ("Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom")],
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
        rx.button("Voltar à lista", on_click=State.set_detail_id(""), variant="outline"),
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
        rx.button("Atualizar consultas", on_click=State.load_tutor_clinical, variant="outline", disabled=State.clinic_loading),
        notice(),
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
        rx.accordion.root(rx.accordion.item(
            header="Permissões e histórico de acessos", content=rx.vstack(
                rx.foreach(State.access_rows, lambda row: rx.hstack(
                    rx.text("Veterinário ", row["veterinario_id"], " — ", row["status"]),
                    rx.button(rx.cond(row["status"] == "ativo", "Revogar", "Reativar"),
                              on_click=State.change_consent(row["id"], rx.cond(row["status"] == "ativo", "revogado", "ativo")),
                              disabled=State.clinic_busy), wrap="wrap")),
                rx.foreach(State.audit_rows, lambda row: rx.text(row.get("acao", ""), " — ", row.get("ocorrido_em_legivel", ""))),
                align="stretch", spacing="3")), collapsible=True, width="100%"),
        align="stretch", width="100%", spacing="4",
    )


def veterinary_sidebar():
    return rx.box(rx.vstack(
        rx.heading("Vet Tech", size="5"), rx.text("Área veterinária", size="2"),
        *[rx.button(rx.icon(icon, size=18), text, on_click=State.vet_navigate(text),
                    variant=rx.cond(State.vet_section == text, "solid", "soft"), width="100%",
                    aria_current=rx.cond(State.vet_section == text, "page", "false"))
          for text, icon in (("Horários", "calendar-days"), ("Consultas", "clipboard-list"))],
        rx.spacer(), rx.button("Sair", on_click=State.logout, variant="outline", width="100%"),
        align="stretch", spacing="4", min_height="100dvh", padding="16px"),
        as_="nav", aria_label="Menu veterinário", width=rx.breakpoints(initial="140px", lg="220px"),
        flex_shrink="0", background="#F1F5EC", position="sticky", top="0")


def appointment_card(row, actions=True):
    return rx.card(rx.vstack(
        rx.hstack(rx.text(row["quando"], weight="bold"), rx.badge(row["status"]), wrap="wrap"),
        rx.text(row["pet_nome"]),
        rx.cond(row["autorizado"] == "sim", rx.text(row.get("motivo", "")), rx.text("Acesso clínico revogado pelo tutor.")),
        rx.cond(actions & (row["autorizado"] == "sim"), rx.hstack(
            rx.button(rx.cond(row["status"] == "em_atendimento", "Retomar", "Começar consulta"),
                      on_click=State.start_consultation(row["id"]), disabled=State.clinic_busy),
            rx.button("Ver histórico", on_click=State.open_prior_history(row.get("pet_id", "")), variant="outline"),
            wrap="wrap")), align="stretch", spacing="2"), width="100%")


def veterinary_content():
    timeline = rx.vstack(*[agenda_hour(hour) for hour in range(8, 18)],
        spacing="0", width="100%", align="stretch", aria_label="Calendário vertical de consultas")
    return rx.vstack(
        rx.hstack(rx.heading(State.vet_section, size="7"), rx.spacer(),
                  rx.button("Atualizar", on_click=State.load_agenda, disabled=State.clinic_loading), width="100%", wrap="wrap"),
        notice(),
        rx.cond(State.vet_section == "Horários", rx.vstack(
            rx.el.label("Dia da agenda", html_for="agenda-day"),
            rx.input(id="agenda-day", type="date", value=State.agenda_day, on_change=State.agenda_choose_day),
            rx.button("Hoje", on_click=State.agenda_today, variant="outline", disabled=State.clinic_loading),
            rx.cond(State.agenda_rows.length() == 0, rx.text("Nenhuma consulta neste dia.")), timeline,
            align="stretch", width="100%", spacing="4"),
            rx.vstack(rx.text("Próximas consultas e atendimentos pendentes"),
                rx.cond(State.upcoming_rows.length() == 0, rx.text("Nenhum atendimento pendente.")),
                rx.foreach(State.upcoming_rows, lambda row: appointment_card(row)), align="stretch", width="100%", spacing="4")),
        rx.hstack(rx.button("Anterior", on_click=State.agenda_page_by(-1), disabled=State.agenda_page <= 1),
                  rx.text("Página ", State.agenda_page),
                  rx.button("Próxima", on_click=State.agenda_page_by(1), disabled=State.agenda_page * 25 >= State.agenda_total), wrap="wrap"),
        prior_history_panel(),
        align="stretch", spacing="4", width="100%",
    )


def agenda_hour(hour):
    # Visual stacking preserves readability without assigning a clinical duration.
    return rx.hstack(
        rx.text(f"{hour:02d}:00", size="2", color="#53635A", width="48px", flex_shrink="0"),
        rx.vstack(rx.foreach(State.agenda_rows, lambda row: rx.cond(
            row.get("hora", "").startswith(f"{hour:02d}:"), rx.box(
                rx.text(row.get("hora", ""), " · ", row["pet_nome"], weight="bold"), rx.badge(row["status"]),
                padding="8px", background="#E2EDD9", border_radius="8px", border="1px solid #99B38A", width="100%"))),
            spacing="2", align="stretch", width="100%", min_width="0"),
        min_height="90px", align="start", width="100%", padding_y="8px", border_top="1px solid #DEE5D8")


def prior_history_panel():
    return rx.cond(State.prior_history.length() > 0, rx.card(rx.vstack(
        rx.heading("Histórico publicado do pet", size="4"),
        pet_basic_info(State.prior_pet_info),
        rx.foreach(State.prior_history.get("consultas", []), lambda row: rx.vstack(
            rx.text(row["quando"], weight="bold"), rx.text(row.get("diagnostico", "")),
            rx.text(row.get("obs", "")), align="start", padding_y="8px")),
        *[rx.vstack(rx.heading(label, size="3"),
            rx.foreach(State.prior_history.get(group, []), prior_renderer(group)), align="stretch", width="100%")
          for group, label in (("vacinas", "Vacinas"), ("medicamentos", "Medicamentos"), ("doencas", "Doenças"), ("exames", "Exames"))],
        align="stretch", spacing="3"), width="100%"))


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
        special += [rx.text("Doença"), options(State.disease_options, row["doenca_id"],
            lambda value: State.clinical_line_field(group, row["linha_id"], "doenca_id", value), "Escolha a doença")]
    choices = {"doencas": ("estado", ["ativa", "em_tratamento", "curada", "controlada"]),
               "medicamentos": ("tipo", ["continuo", "vermifugo", "antipulgas", "outro"]),
               "exames": ("status", ["solicitado", "realizado"])}
    if group in choices:
        key, items = choices[group]
        special += [rx.text(key.capitalize()), rx.select(items, placeholder="Selecione", value=row[key],
            on_change=lambda value: State.clinical_line_field(group, row["linha_id"], key, value), disabled=State.clinic_busy)]
    return rx.card(rx.vstack(
        *special,
        *[rx.vstack(rx.text(label, as_="label"),
             rx.input(type=kind, value=row[key], placeholder=label, aria_label=label,
                      on_change=line_change(group, row, key),
                      disabled=State.clinic_busy, width="100%"), align="stretch", width="100%", spacing="1")
          for key, label, kind in LINE_FIELDS[group]],
        rx.button("Remover registro", on_click=State.clinical_remove_line(group, row["linha_id"]),
                  variant="ghost", color_scheme="red", disabled=State.clinic_busy),
        align="stretch", spacing="3"), width="100%")


def attendance_content():
    return rx.container(rx.vstack(
        rx.hstack(rx.heading("Atendimento", size="7"), rx.spacer(),
                  rx.button("Voltar às consultas", on_click=State.leave_attendance(False), variant="outline"), width="100%", wrap="wrap"),
        notice(),
        rx.cond(State.clinical_id != "", rx.vstack(
            rx.heading(State.clinical_pet_name, size="5"), rx.badge(State.clinical_status),
            pet_basic_info(State.clinical_pet_info),
            rx.button("Consultar histórico anterior", on_click=State.open_prior_history(State.clinical_pet_id), variant="outline"),
            prior_history_panel(),
            rx.text(rx.cond(State.clinical_dirty, "Há alterações não salvas", "Última versão confirmada"), role="status"),
            rx.cond(State.clinical_status == "em_atendimento", rx.vstack(
                *[rx.vstack(rx.el.label(label, html_for="clinic-"+key),
                     rx.input(id="clinic-"+key, type=kind, value=value,
                              on_change=header_change(key),
                              disabled=State.clinic_busy, width="100%"), align="stretch", width="100%")
                  for key, label, kind, value in (("data_atendimento", "Data do atendimento", "date", State.clinical_date),
                      ("motivo", "Motivo", "text", State.clinical_reason), ("diagnostico", "Diagnóstico", "text", State.clinical_diagnosis),
                      ("obs", "Observações", "text", State.clinical_notes), ("retorno_previsto", "Retorno (opcional)", "date", State.clinical_return))],
                *[rx.vstack(rx.hstack(rx.heading(label, size="4"), rx.spacer(),
                       rx.button("Adicionar", on_click=State.clinical_add_line(group), disabled=State.clinic_busy), width="100%"),
                       rx.foreach(State.clinical_lines[group], line_renderer(group)),
                       align="stretch", spacing="3", width="100%")
                  for group, label in (("vacinas", "Vacinas"), ("medicamentos", "Medicamentos"), ("doencas", "Doenças"), ("exames", "Exames"))],
                rx.accordion.root(rx.accordion.item(header="Cadastrar doença no catálogo", content=rx.vstack(
                    rx.input(placeholder="Nome da doença", value=State.disease_name, on_change=State.set_disease_name, aria_label="Nome da doença"),
                    rx.text_area(placeholder="Descrição", value=State.disease_description, on_change=State.set_disease_description, aria_label="Descrição da doença"),
                    rx.button("Cadastrar referência", on_click=State.create_disease, disabled=State.clinic_busy), align="stretch")), collapsible=True),
                rx.hstack(rx.button("Salvar rascunho", on_click=State.save_attendance(False), disabled=State.clinic_busy, variant="outline"),
                          rx.button("Terminar consulta", on_click=State.save_attendance(True), loading=State.clinic_busy), wrap="wrap"),
                align="stretch", spacing="5", width="100%"),
                rx.text("Atendimento finalizado. Os registros publicados estão disponíveis ao tutor.")),
            align="stretch", width="100%", spacing="4")),
        rx.alert_dialog.root(rx.alert_dialog.content(
            rx.alert_dialog.title("Descartar alterações não salvas?"),
            rx.alert_dialog.description("A última versão salva permanece no banco. As alterações locais serão descartadas."),
            rx.hstack(rx.alert_dialog.cancel(rx.button("Continuar editando", on_click=State.set_clinical_confirm_leave(False))),
                      rx.alert_dialog.action(rx.button("Descartar e voltar", on_click=State.leave_attendance(True))), wrap="wrap")),
            open=State.clinical_confirm_leave),
        align="stretch", spacing="5", padding_y="32px"), max_width="960px")
