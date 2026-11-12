"""Feature mixin: keeps one authenticated State and its session generation."""
import asyncio
import base64
import calendar
import json
from hashlib import sha256
from random import choice
import unicodedata
from time import monotonic
from copy import deepcopy
from datetime import date, datetime, timedelta
from typing import Any, TypedDict
from urllib.parse import urlencode
from uuid import uuid4
from zoneinfo import ZoneInfo

import reflex as rx

from vet_tech.shared.xano_client import XanoRequestError, xano_request, xano_request_batch
from vet_tech.features.navigation.state import CLINICAL_SECTIONS
from vet_tech.shared.measurements import weight_label
from vet_tech.shared.dates import calendar_date, date_label, instant_label, instant_datetime
from .consultation_pdf import ConsultationPDFError, map_consultation_document, positive_id, pdf_export_enabled
from .consultation_pdf_template import render_consultation_pdf, RENDER_TIMEOUT_SECONDS

GROUP = "vettech-clinical"
TZ = ZoneInfo("America/Sao_Paulo")
GROUPS = ("vacinas", "medicamentos", "doencas", "exames")
RECORD_BACKGROUNDS = ("/optimized/fundo.webp", "/optimized/fundo02.webp", "/optimized/fundo_mar.webp", "/optimized/fundinho.webp")
WEEKDAYS = ("Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo")
MONTHS = ("janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro")


def agenda_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError:
        return date.fromisoformat(today())


CLINICAL_DATE_FIELDS = {
    "": {"data_atendimento": "Data do atendimento", "retorno_previsto": "Retorno (opcional)"},
    "vacinas": {"data_aplicacao": "Data de aplicação", "data_prox_dose": "Próxima dose (opcional)"},
    "medicamentos": {"data_inicio": "Início", "data_fim": "Fim"},
    "doencas": {"data_diagnostico": "Data do diagnóstico"},
    "exames": {"data_solicitacao": "Solicitação", "data_realizacao": "Realização"},
}


def calendar_days(month_value: str, active: str) -> list[dict[str, str]]:
    year, month = map(int, (month_value or today()[:7]).split("-"))
    days = [n for week in calendar.Calendar().monthdayscalendar(year, month) for n in week]
    days += [0] * (42 - len(days))
    return [{"label": str(n) if n else "", "date": f"{year:04d}-{month:02d}-{n:02d}" if n else "",
             "selected": "sim" if n and f"{year:04d}-{month:02d}-{n:02d}" == active else "nao",
             "today": "sim" if n and f"{year:04d}-{month:02d}-{n:02d}" == today() else "nao"} for n in days]


def agenda_photo(value) -> str:
    # Match the existing pet photo contract; never render arbitrary URI schemes.
    value = str(value or "")
    return value if value.startswith(("https://", "http://", "data:image/jpeg;base64,", "data:image/png;base64,", "data:image/webp;base64,")) else ""


def patient_photo(pet: dict, pet_id: str = "", agenda: list[dict] | None = None) -> dict[str, str]:
    """Call only after a successful authorized read; explicit null overrides cache."""
    if "foto" in pet:
        value = pet["foto"]
        return {"foto": agenda_photo(value), "foto_ausente": "sim" if value is None or value == "" else "nao"}
    for row in agenda or []:
        if str(row.get("pet_id", "")) == str(pet_id) and row.get("autorizado") == "sim" and row.get("pet_foto"):
            return {"foto": agenda_photo(row["pet_foto"]), "foto_ausente": "nao"}
    # Missing contract is not evidence that the database has no image.
    return {"foto": "", "foto_ausente": "nao"}


def today() -> str:
    return datetime.now(TZ).date().isoformat()


def display_date(value) -> str:
    return date_label(value) or "Não informado"


def care_status(row: dict, group: str, day: date) -> dict[str, str]:
    """Presentation only; dates never confirm medication administration."""
    tone, label = "neutral", "Situação não informada"
    if group == "vacinas":
        applied, next_dose = calendar_date(row.get("data_aplicacao")), calendar_date(row.get("data_prox_dose"))
        if applied and applied > day:
            tone, label = "red", "Aplicação prevista — sem confirmação de aplicação"
        elif applied:
            tone, label = "green", "Aplicada — próxima dose não informada"
            if next_dose and next_dose >= applied:
                days = (next_dose - day).days
                tone = "red" if days < 0 else "yellow" if days <= 7 else "green"
                label = "Aplicada — " + ("data da próxima dose ultrapassada" if days < 0 else "próxima dose hoje" if days == 0 else "próxima dose nos próximos 7 dias" if days <= 7 else "próxima dose futura")
    elif group == "medicamentos":
        start, end = calendar_date(row.get("data_inicio")), calendar_date(row.get("data_fim"))
        if start and (end is None and row.get("tipo") == "continuo" or end is not None and end >= start):
            tone, label = ("red", "A iniciar — conforme prescrição") if start > day else ("green", "Período prescrito encerrado") if end and end < day else ("yellow", "Dentro do período prescrito")
    elif group == "exames":
        tone, label = {"solicitado": ("red", "Solicitado"), "realizado": ("green", "Realizado")}.get(row.get("status"), (tone, label))
    elif group in ("diagnosticos", "doencas"):
        tone, label = {"ativa": ("red", "Ativa"), "em_tratamento": ("yellow", "Em tratamento"), "controlada": ("yellow", "Controlada"), "curada": ("green", "Curada")}.get(row.get("estado"), (tone, label))
    return {**row, "care_tone": tone, "care_label": label}


def cards(rows: list[dict]) -> list[dict[str, str]]:
    result = []
    for row in rows:
        item = {str(k): "" if v is None else str(v) for k, v in row.items()}
        item["veterinario_nome"] = str(row.get("veterinario_nome") or "").strip() or "Nome não informado"
        item["quando"] = (instant_label(row["agendada_para"]) if row.get("agendada_para")
                          else date_label(row.get("data_atendimento") or row.get("data"))) or "Não informado"
        scheduled = instant_datetime(row.get("agendada_para"))
        item["consulta_data_legivel"] = scheduled.strftime("%d/%m/%Y") if scheduled else item["quando"]
        item["consulta_hora_legivel"] = scheduled.strftime("%H:%M") if scheduled else "Não informado"
        item["pet_nome"] = str(row.get("pet_nome") or ("Pet " + str(row.get("pet_id", ""))))
        item["autorizado"] = "sim" if row.get("autorizado", True) else "nao"
        item["status"] = str(row.get("status") or "legado")
        for key in ("data", "data_atendimento", "iniciada_em", "finalizada_em", "retorno_previsto", "data_aplicacao", "data_prox_dose", "data_inicio", "data_fim", "data_diagnostico", "data_evolucao", "data_solicitacao", "data_realizacao", "ocorrido_em"):
            formatter = instant_label if key in {"iniciada_em", "finalizada_em", "ocorrido_em"} else date_label
            item[key + "_legivel"] = formatter(row.get(key)) if row.get(key) else ""
        item["dose_legivel"] = (str(row["dose"]) + " " + str(row.get("unidade") or "")) if row.get("dose") is not None else (str(row["dosagem"]) + " (registro anterior)") if row.get("dosagem") is not None else ""
        item["origem_legivel"] = "Consulta " + str(row["consulta_id"]) if row.get("consulta_id") else "Registro anterior sem consulta vinculada"
        result.append(item)
    return result


class ConsultationDay(TypedDict):
    date: str
    label: str
    items: list[dict[str, str]]


def consultation_days(rows: list[dict[str, str]], current_day: str) -> list[ConsultationDay]:
    """Group the loaded page by the local scheduled day without changing its records."""
    current = date.fromisoformat(current_day)
    tomorrow = (current + timedelta(days=1)).isoformat()
    grouped: dict[str, ConsultationDay] = {}
    for row in sorted(rows, key=lambda item: (float(item.get("agendada_para") or 0), item.get("id", ""))):
        scheduled = instant_datetime(row.get("agendada_para"))
        day = scheduled.date().isoformat() if scheduled else ""
        if day not in grouped:
            label = date_label(day) or "Data não informada"
            if day == current_day:
                label = "Hoje — " + label
            elif day == tomorrow:
                label = "Amanhã — " + label
            grouped[day] = {"date": day, "label": label, "items": []}
        grouped[day]["items"].append(row)
    return list(grouped.values())


def pet_summary(row: dict) -> dict[str, str]:
    return {**patient_photo(row), "nome": str(row.get("nome") or "Pet"), "sexo": str(row.get("sexo") or "Não informado"),
            "nascimento": display_date(row.get("data_nasc")),
            "peso": weight_label(row.get("peso_atual"))}


def consultation_summary(pet: dict, history: dict) -> dict[str, str]:
    """Only explicit named clinical records are presented as allergy records."""
    result = pet_summary(pet)
    allergies = []
    for row in history.get("doencas", []) + history.get("diagnosticos", []):
        name = str(row.get("nome") or "").strip()
        normalized = "".join(char for char in unicodedata.normalize("NFD", name.casefold()) if not unicodedata.combining(char))
        if "alerg" in normalized and not any(negation in normalized for negation in ("nao alerg", "sem alerg")):
            label = name + (" · " + str(row["estado"]).replace("_", " ") if row.get("estado") else "")
            if label not in allergies:
                allergies.append(label)
    result["alergias"] = "; ".join(allergies) or "Alergias não informadas"
    vaccines = sorted(history.get("vacinas", []), key=lambda row: str(row.get("data_aplicacao") or ""), reverse=True)
    consultations = sorted(history.get("consultas", []), key=lambda row: str(row.get("data_atendimento") or row.get("data") or ""), reverse=True)
    result["ultima_vacina"] = (str(vaccines[0].get("vacina") or "Vacina") + " · " + display_date(vaccines[0].get("data_aplicacao"))) if vaccines else "Não informada"
    result["ultima_consulta"] = display_date(consultations[0].get("data_atendimento") or consultations[0].get("data")) if consultations else "Não informada"
    return result


def attendance_saved_toast(finalized: bool):
    return rx.toast.success(
        "Consulta finalizada com sucesso!" if finalized else "Rascunho salvo com sucesso!",
        description="Os registros estão disponíveis ao tutor." if finalized else "Você pode continuar o atendimento com tranquilidade.",
        position="bottom-left", duration=5000, close_button=True, class_name="attendance-saved-toast",
        style={"background": "var(--vet-toast-bg)", "color": "var(--vet-text)", "border": "1px solid var(--vet-border)", "border_radius": "14px"},
    )


class ClinicalMixin(rx.State, mixin=True):
    @rx.event
    def set_booking_time(self, value: str):
        if not self.booking_busy and not self._booking_uncertain:
            self.booking_time = value

    @rx.event
    def set_booking_reason(self, value: str):
        if not self.booking_busy and not self._booking_uncertain:
            self.booking_reason = value

    @rx.event
    def set_booking_professional(self, value: str):
        if (not self.booking_busy and not self._booking_uncertain
                and any(row["id"] == value for row in self.booking_professionals)):
            self.booking_professional = value
            self.booking_message = ""

    @rx.event
    def set_detail_id(self, value: str):
        self._invalidate_pdf_export()
        self.detail_id = value

    @rx.event
    def set_disease_name(self, value: str):
        self.disease_name = value

    @rx.event
    def set_disease_description(self, value: str):
        self.disease_description = value

    @rx.event
    def set_clinical_confirm_leave(self, value: bool):
        self.clinical_confirm_leave = value

    booking_open: bool = False
    booking_step: int = 1
    booking_month: str = ""
    booking_day: str = ""
    booking_time: str = ""
    booking_pet: str = ""
    booking_professional: str = ""
    booking_reason: str = ""
    booking_professionals: list[dict[str, str]] = []
    booking_message: str = ""
    booking_busy: bool = False
    _booking_operation: str = ""
    _booking_generation: int = 0
    _booking_sent: dict = {}
    _booking_uncertain: bool = False
    vet_section: str = "Horários"
    agenda_day: str = ""
    agenda_calendar_open: bool = False
    agenda_calendar_month: str = ""
    agenda_rows: list[dict[str, str]] = []
    upcoming_rows: list[dict[str, str]] = []
    consultation_tab: str = "Pendentes"
    consultation_search: str = ""
    consultation_status: str = "Todos os estados"
    consultation_selected: str = ""
    consultation_info: dict[str, str] = {}
    consultation_summary_loading: bool = False
    consultation_summary_error: str = ""
    _consultation_generation: int = 0

    @rx.var(cache=False)
    def consultation_day_groups(self) -> list[ConsultationDay]:
        return consultation_days(self.upcoming_rows, today())

    agenda_page: int = 1
    agenda_total: int = 0
    clinic_message: str = ""
    clinic_busy: bool = False
    clinic_loading: bool = False

    @rx.var
    def agenda_date_label(self) -> str:
        day = agenda_date(self.agenda_day)
        return f"{WEEKDAYS[day.weekday()]}, {day.day:02d} de {MONTHS[day.month - 1]} de {day.year}"

    @rx.var
    def agenda_short_date(self) -> str:
        return agenda_date(self.agenda_day).strftime("%d/%m/%Y")

    @rx.var
    def agenda_calendar_month_name(self) -> str:
        value = agenda_date((self.agenda_calendar_month or today()[:7]) + "-01")
        return MONTHS[value.month - 1].capitalize()

    @rx.var
    def agenda_calendar_year(self) -> str:
        return (self.agenda_calendar_month or today()[:7])[:4]

    @rx.var
    def agenda_calendar_years(self) -> list[str]:
        year = int(self.agenda_calendar_year)
        return [str(y).zfill(4) for y in range(max(1, year - 10), min(9999, year + 10) + 1)]

    @rx.var
    def agenda_calendar_days(self) -> list[dict[str, str]]:
        return calendar_days(self.agenda_calendar_month, self.agenda_day or today())

    @rx.var
    def agenda_week(self) -> list[dict[str, str]]:
        day = agenda_date(self.agenda_day)
        monday = day - timedelta(days=day.weekday())
        return [{"date": (item := monday + timedelta(days=i)).isoformat(),
                 "label": WEEKDAYS[i][:3], "day": f"{item.day:02d}"} for i in range(7)]

    @rx.var
    def agenda_hours(self) -> list[int]:
        hours = [int(row["hora"][:2]) for row in self.agenda_rows if row.get("hora")]
        return list(range(min([8, *hours]), max([17, *hours]) + 1))

    @rx.var
    def agenda_completed(self) -> int:
        return sum(row.get("status") == "finalizada" for row in self.agenda_rows)

    @rx.var
    def agenda_in_progress(self) -> int:
        return sum(row.get("status") == "em_atendimento" for row in self.agenda_rows)
    _clinic_generation: int = 0
    _tutor_history_pet: str = ""
    _tutor_loaded_at: float = 0.0
    _tutor_history_loaded_at: float = 0.0
    _tutor_running: int = -1
    tutor_clinical_loaded: bool = False
    auxiliary_loading: bool = False
    auxiliary_loaded: bool = False
    auxiliary_message: str = ""
    _auxiliary_generation: int = 0
    _auxiliary_running: int = -1
    consultation_rows: list[dict[str, str]] = []
    history_rows: dict[str, list[dict[str, str]]] = {}
    _record_background_choices: dict[str, str] = {}
    access_rows: list[dict[str, str]] = []
    audit_rows: list[dict[str, str]] = []
    pdf_export_busy: bool = False
    pdf_export_message: str = ""
    _pdf_generation: int = 0
    _pdf_key: str = ""
    _pdf_target: tuple[str, str] = ("", "")
    _pdf_route: str = ""
    _pdf_profile: str = ""
    _pdf_origin: str = ""
    _pdf_signature: str = ""
    _pdf_trigger: str = ""
    pdf_preview_open: bool = False
    pdf_preview_loading: bool = False
    pdf_preview_ready: bool = False
    pdf_preview_title: str = ""
    pdf_preview_token: str = ""
    _pdf_preview_bytes: bytes = b""
    pdf_preview_fields: list[dict[str, str]] = []
    pdf_preview_sections: list[dict[str, str]] = []
    detail_id: str = ""
    detail: dict[str, str] = {}
    detail_sections: dict[str, list[dict[str, str]]] = {}
    clinical_id: str = ""
    clinical_version: int = 0
    clinical_status: str = ""
    clinical_pet_name: str = ""
    clinical_pet_id: str = ""
    clinical_pet_info: dict[str, str] = {}
    prior_pet_info: dict[str, str] = {}
    clinical_reason: str = ""
    clinical_diagnosis: str = ""
    clinical_notes: str = ""
    clinical_agenda_day: str = ""
    clinical_date: str = ""
    clinical_return: str = ""
    clinical_lines: dict[str, list[dict[str, str]]] = {key: [] for key in GROUPS}
    clinical_dirty: bool = False
    clinical_confirm_leave: bool = False
    disease_options: list[dict[str, str]] = []
    disease_name: str = ""
    disease_description: str = ""
    prior_history: dict[str, list[dict[str, str]]] = {}
    prior_history_message: str = ""
    _save_uncertain: bool = False
    _pending_version: int = -1
    _pending_payload: dict = {}
    _prior_generation: int = 0

    clinical_calendar_open: bool = False
    clinical_calendar_month: str = ""
    clinical_calendar_group: str = ""
    clinical_calendar_line: str = ""
    clinical_calendar_field: str = ""

    @rx.var
    def clinical_calendar_value(self) -> str:
        if not self.clinical_calendar_group:
            return {"data_atendimento": self.clinical_date, "retorno_previsto": self.clinical_return}.get(self.clinical_calendar_field, "")
        for row in self.clinical_lines.get(self.clinical_calendar_group, []):
            if row["linha_id"] == self.clinical_calendar_line:
                return row.get(self.clinical_calendar_field, "")
        return ""

    @rx.var
    def clinical_calendar_label(self) -> str:
        return CLINICAL_DATE_FIELDS.get(self.clinical_calendar_group, {}).get(self.clinical_calendar_field, "Escolher data")

    @rx.var
    def clinical_calendar_date_label(self) -> str:
        return date_label(self.clinical_calendar_value) or "Nenhuma data selecionada"

    @rx.var
    def clinical_calendar_trigger_id(self) -> str:
        return "clinic-" + (self.clinical_calendar_line + "-" if self.clinical_calendar_group else "") + self.clinical_calendar_field

    @rx.var
    def clinical_calendar_month_name(self) -> str:
        return MONTHS[int((self.clinical_calendar_month or today()[:7])[5:7]) - 1].capitalize()

    @rx.var
    def clinical_calendar_year(self) -> str:
        return (self.clinical_calendar_month or today()[:7])[:4]

    @rx.var
    def clinical_calendar_years(self) -> list[str]:
        year = int(self.clinical_calendar_year)
        return [str(y).zfill(4) for y in range(max(1, year - 10), min(9999, year + 10) + 1)]

    @rx.var
    def clinical_calendar_days(self) -> list[dict[str, str]]:
        return calendar_days(self.clinical_calendar_month, self.clinical_calendar_value)

    def _clinical_calendar_editable(self) -> bool:
        if self.profile != "veterinario" or not self.clinical_id or self.clinical_status != "em_atendimento" or self.clinical_locked:
            return False
        group, field = self.clinical_calendar_group, self.clinical_calendar_field
        if field not in CLINICAL_DATE_FIELDS.get(group, {}):
            return False
        return not group or any(row["linha_id"] == self.clinical_calendar_line for row in self.clinical_lines.get(group, []))

    def _clear_clinical_calendar(self):
        self.clinical_calendar_open = False
        self.clinical_calendar_month = ""
        self.clinical_calendar_group = self.clinical_calendar_line = self.clinical_calendar_field = ""

    @rx.event
    def clinical_calendar_restore_focus(self):
        return rx.call_script("document.getElementById(" + json.dumps(self.clinical_calendar_trigger_id) + ")?.focus()")

    @rx.event
    def clinical_calendar_show(self, field: str, group: str = "", line: str = ""):
        self.clinical_calendar_group, self.clinical_calendar_line, self.clinical_calendar_field = group, line, field
        if not self._clinical_calendar_editable():
            self._clear_clinical_calendar()
            return
        self.clinical_calendar_month = agenda_date(self.clinical_calendar_value).isoformat()[:7]
        self.clinical_calendar_open = True

    @rx.event
    def clinical_calendar_set_open(self, value: bool):
        # Only explicit field buttons may open the dialog.
        if not value:
            self.clinical_calendar_open = False

    @rx.event
    def clinical_calendar_shift(self, offset: int):
        if not self.clinical_calendar_open or not self._clinical_calendar_editable():
            return
        year, month = map(int, (self.clinical_calendar_month or today()[:7]).split("-"))
        serial = year * 12 + month - 1 + offset
        if 12 <= serial < 120000:
            self.clinical_calendar_month = f"{serial // 12:04d}-{serial % 12 + 1:02d}"

    @rx.event
    def clinical_calendar_choose_month(self, value: str):
        names = [name.capitalize() for name in MONTHS]
        if self.clinical_calendar_open and self._clinical_calendar_editable() and value in names:
            self.clinical_calendar_month = f"{self.clinical_calendar_year}-{names.index(value) + 1:02d}"

    @rx.event
    def clinical_calendar_choose_year(self, value: str):
        if self.clinical_calendar_open and self._clinical_calendar_editable() and value.isascii() and value.isdecimal() and 1 <= int(value) <= 9999:
            self.clinical_calendar_month = f"{int(value):04d}-" + (self.clinical_calendar_month or today()[:7])[5:7]

    @rx.event
    def clinical_calendar_choose_day(self, value: str):
        if not self.clinical_calendar_open or not self._clinical_calendar_editable():
            return
        if value:
            try:
                parsed = date.fromisoformat(value)
                if parsed.isoformat() != value:
                    return
            except ValueError:
                return
        if self.clinical_calendar_group:
            self.clinical_line_field(self.clinical_calendar_group, self.clinical_calendar_line, self.clinical_calendar_field, value)
        else:
            self.clinical_field(self.clinical_calendar_field, value)
        self.clinical_calendar_open = False

    @rx.var
    def booking_locked(self) -> bool:
        return self.booking_busy or self._booking_uncertain

    @rx.var
    def clinical_locked(self) -> bool:
        return self.clinic_busy or self._save_uncertain

    def _with_record_backgrounds(self, history, pet_id):
        projected = {group: [dict(row) for row in rows] for group, rows in history.items()}
        for group in ("vacinas", "medicamentos", "doencas", "diagnosticos", "exames", "consultas"):
            rows = projected.get(group, [])
            keys = []
            for row in rows:
                identity = row.get("id") or sha256(json.dumps(
                    {key: value for key, value in row.items() if key != "fundo_card"},
                    sort_keys=True, ensure_ascii=False,
                ).encode()).hexdigest()
                keys.append(f"{pet_id}:{group}:{identity}")
            used = {self._record_background_choices[key] for key in keys if key in self._record_background_choices}
            previous = None
            for key, row in zip(keys, rows):
                if key not in self._record_background_choices:
                    available = [background for background in RECORD_BACKGROUNDS if background not in used]
                    if not available:
                        used = set()
                        available = [background for background in RECORD_BACKGROUNDS if background != previous]
                    self._record_background_choices[key] = choice(available)
                background = self._record_background_choices[key]
                row["fundo_card"] = background
                used.add(background)
                previous = background
        return projected

    def _clear_clinical_pet(self):
        self._invalidate_pdf_export()
        self._clinic_generation += 1
        self._auxiliary_generation += 1
        self._tutor_loaded_at = 0.0
        self._tutor_history_loaded_at = 0.0
        self.tutor_clinical_loaded = False
        self.auxiliary_loading = self.auxiliary_loaded = False
        self.auxiliary_message = ""
        self._tutor_history_pet = ""
        self.history_rows = {}
        self.consultation_rows = []
        self.access_rows = []
        self.audit_rows = []
        self.detail_id = ""
        self.detail = {}
        self.detail_sections = {}
        self.clinic_loading = False
        self.clinic_message = ""

    def _clear_clinical_session(self):
        self._record_background_choices = {}
        self._clear_clinical_calendar()
        self._clear_clinical_pet()
        self._prior_generation += 1
        self._booking_generation += 1
        self.booking_open = False
        self.booking_busy = False
        self.booking_professionals = []
        self.booking_day = self.booking_time = self.booking_pet = ""
        self.booking_professional = self.booking_reason = self.booking_message = ""
        self._booking_sent = {}
        self._booking_uncertain = False
        self._booking_operation = ""
        self._clear_consultation_summary()
        self.consultation_tab = "Pendentes"
        self.consultation_search = ""
        self.consultation_status = "Todos os estados"
        self.agenda_rows = self.upcoming_rows = []
        self.agenda_calendar_open = False
        self.agenda_calendar_month = ""
        self.clinical_id = self.clinical_pet_id = self.clinical_pet_name = ""
        self.clinical_pet_info = self.prior_pet_info = {}
        self.clinical_status = self.clinical_reason = self.clinical_diagnosis = self.clinical_notes = ""
        self.clinical_agenda_day = ""
        self.clinical_date = self.clinical_return = ""
        self.clinical_lines = {key: [] for key in GROUPS}
        self.prior_history = {}
        self.prior_history_message = ""
        self.disease_options = []
        self.disease_name = self.disease_description = ""
        self.clinical_dirty = False
        self.clinical_confirm_leave = False
        self.clinic_busy = False
        self.vet_section = "Horários"
        self._save_uncertain = False
        self._pending_payload = {}

    def _clinical_current(self, session, token):
        return bool(token) and token == self._auth_token and session == self._session_generation

    def _clinic_error(self, error):
        if error.status_code == 401:
            self._expire_session()
        else:
            self.clinic_message = str(error)
            if error.status_code in (403, 404):
                self._clear_consultation_summary()
                self._clear_clinical_calendar()
                self._prior_generation += 1
                self.clinical_agenda_day = ""
                self.clinical_id = self.clinical_pet_id = self.clinical_pet_name = ""
                self.clinical_pet_info = self.prior_pet_info = {}
                self.clinical_reason = self.clinical_status = ""
                self.clinical_lines = {key: [] for key in GROUPS}
                self.clinical_diagnosis = self.clinical_notes = ""
                self.prior_history = {}
                self.prior_history_message = ""

    @rx.var
    def booking_calendar_locked(self) -> bool:
        return self.booking_busy or self._booking_uncertain

    @rx.var
    def booking_date_label(self) -> str:
        return date_label(self.booking_day) or "Nenhuma data selecionada"

    @rx.var
    def booking_month_name(self) -> str:
        return MONTHS[int((self.booking_month or today()[:7])[5:7])-1].capitalize()

    @rx.var
    def booking_year(self) -> str:
        return (self.booking_month or today()[:7])[:4]

    @rx.var
    def booking_years(self) -> list[str]:
        year = int(self.booking_year)
        return [str(y).zfill(4) for y in range(max(1, year-10), min(9998, year+10)+1)]

    @rx.var
    def booking_days(self) -> list[dict[str, str]]:
        return [{**day, "disabled": "sim" if day["date"] and day["date"] < today() else "nao"}
                for day in calendar_days(self.booking_month, self.booking_day)]

    @rx.event
    def booking_set_open(self, value: bool):
        if self.booking_busy:
            return
        if value:
            if self.profile != "tutor":
                return
            self.booking_step = 1
            self.booking_month = today()[:7]
            self.booking_message = ""
            if not self._booking_uncertain:
                self._booking_operation = str(uuid4())
            self.booking_open = True
        elif self._booking_uncertain:
            self.booking_message = "Confirme o resultado do envio anterior antes de fechar ou alterar a reserva."
        else:
            self.booking_open = False
            self._booking_generation += 1
            self.booking_day = self.booking_time = self.booking_pet = ""
            self.booking_professional = self.booking_reason = ""
            self.booking_professionals = []

    @rx.event
    def booking_shift_month(self, offset: int):
        if not self.booking_open or self.booking_calendar_locked:
            return
        year, month = map(int, (self.booking_month or today()[:7]).split("-"))
        serial = year * 12 + month - 1 + offset
        if 12 <= serial < 119988:
            self.booking_month = f"{serial // 12:04d}-{serial % 12 + 1:02d}"

    @rx.event
    def booking_choose_month(self, value: str):
        names = [name.capitalize() for name in MONTHS]
        if self.booking_open and not self.booking_calendar_locked and value in names:
            self.booking_month = f"{self.booking_year}-{names.index(value)+1:02d}"

    @rx.event
    def booking_choose_year(self, value: str):
        if (self.booking_open and not self.booking_calendar_locked and value.isascii()
                and value.isdecimal() and 1 <= int(value) <= 9998):
            self.booking_month = f"{int(value):04d}-" + (self.booking_month or today()[:7])[5:7]

    @rx.event
    def booking_choose_day(self, value: str):
        if not self.booking_open or self.booking_calendar_locked:
            return
        try:
            chosen = date.fromisoformat(value)
        except ValueError:
            return
        if chosen.isoformat() == value and value >= today():
            self.booking_day = value
            self.booking_message = ""

    @rx.var
    def booking_pet_name(self) -> str:
        return next((row["nome"] for row in self.pets if row["id"] == self.booking_pet), "Pet não selecionado")

    @rx.var
    def booking_professional_name(self) -> str:
        return next((row["nome"] for row in self.booking_professionals if row["id"] == self.booking_professional), "Veterinário não selecionado")

    @rx.event
    def booking_next(self):
        if not self.booking_open or self.booking_calendar_locked:
            return
        try:
            instant = datetime.fromisoformat(f"{self.booking_day}T{self.booking_time}").replace(tzinfo=TZ)
            if not ("08:00" <= self.booking_time <= "17:00") or instant <= datetime.now(TZ):
                raise ValueError
        except ValueError:
            self.booking_message = "Escolha dia e horário futuros entre 08h e 17h."
            return
        if (not any(row["id"] == self.booking_pet for row in self.pets)
                or not any(row["id"] == self.booking_professional for row in self.booking_professionals)):
            self.booking_message = "Escolha o pet e um veterinário para o atendimento."
            return
        self.booking_step = 2
        self.booking_message = ""

    @rx.event
    def booking_back(self):
        if not self.booking_busy and not self._booking_uncertain:
            self.booking_step = 1

    @rx.event
    async def booking_choose_pet(self, value: str):
        if self.booking_busy or self._booking_uncertain:
            return
        self._booking_generation += 1
        generation = self._booking_generation
        self.booking_pet = value
        self.booking_professional = ""
        self.booking_professionals = []
        self.booking_message = "Carregando profissionais…"
        session, token = self._session_generation, self._auth_token
        try:
            rows = await xano_request("GET", GROUP, "tutor/profissionais?" + urlencode({"pet_id": value}), auth_token=token)
            if generation == self._booking_generation and self._clinical_current(session, token):
                self.booking_professionals = cards(rows)
                self.booking_message = "" if rows else "Nenhum profissional atende a espécie deste pet."
        except XanoRequestError as error:
            if generation == self._booking_generation and self._clinical_current(session, token):
                if error.status_code == 401:
                    self._expire_session()
                else:
                    self.booking_message = str(error)

    @rx.event
    async def booking_submit(self):
        if self.booking_busy or self.profile != "tutor":
            return
        if not all((self.booking_day, self.booking_time, self.booking_pet, self.booking_professional, self.booking_reason.strip())):
            self.booking_message = "Preencha pet, motivo e profissional."
            return
        self.booking_busy = True
        session, token = self._session_generation, self._auth_token
        if not self._booking_uncertain:
            self._booking_sent = {"dia": self.booking_day, "horario": self.booking_time,
                "pet_id": self.booking_pet, "veterinario_id": self.booking_professional,
                "motivo": self.booking_reason, "operacao": self._booking_operation or str(uuid4())}
        yield
        try:
            await xano_request("POST", GROUP, "tutor/consultas", auth_token=token, json_payload={"payload": self._booking_sent})
            if self._clinical_current(session, token):
                self._booking_uncertain = False
                self.booking_busy = False
                self.booking_set_open(False)
                self.clinic_message = "Consulta agendada. O profissional já pode consultar o histórico publicado do pet escolhido."
                if str(self._booking_sent.get('pet_id')) == self.selected_pet_id:
                    # Invalidate reads begun before the confirmed write.
                    self.clinic_loading = False
                    event = self._prepare_tutor_clinical(force=True, reservations_only=True)
                    if event is not None:
                        yield event
        except XanoRequestError as error:
            if self._clinical_current(session, token):
                if error.status_code == 401:
                    self._expire_session()
                else:
                    self._booking_uncertain = error.status_code is None or error.status_code >= 500
                    self.booking_message = str(error) + (" Reenvie para confirmar a mesma reserva." if self._booking_uncertain else "")
        finally:
            if self._clinical_current(session, token):
                self.booking_busy = False

    @rx.event
    async def clinical_section(self, section: str):
        if section not in ("Início", "Consultas", "Vacinas", "Medicamentos", "Doenças"):
            return
        if section != self.active_section:
            self._invalidate_pdf_export()
        self.active_section = section
        event = self._prepare_tutor_clinical()
        if event is not None:
            yield event

    @rx.var
    def clinical_menu_item(self) -> str:
        return next((key for key, label in CLINICAL_SECTIONS.items()
                     if label == self.active_section and key != 'inicio'), 'prontuario')

    @rx.event
    def enter_clinical_page(self):
        """Runs for both path and query changes, including browser history."""
        if not self.is_authenticated:
            return rx.redirect('/login')
        if self.profile != 'tutor':
            return
        key = self.router.url.query_parameters.get('secao', 'inicio')
        self.active_section = CLINICAL_SECTIONS.get(key, 'Início')
        self._invalidate_pdf_export()
        self.detail_id = ''
        pet_id = self.router.url.query_parameters.get('pet_id', '')
        if pet_id:
            if any(pet.get('id') == pet_id for pet in self.pets):
                self._start_pet_selection(pet_id)
                return type(self).load_selected_pet(self._pet_context_generation)
            self._clear_pet_context()
            self.pet_picker_open = True
            self.pet_detail_message = 'Pet não disponível.'
            return
        return self._prepare_tutor_clinical()

    def _prepare_tutor_clinical(self, force: bool = False, reservations_only: bool = False):
        if self.profile != 'tutor' or not self.selected_pet_id or not self._auth_token:
            return
        if self.clinic_loading and not reservations_only:
            return
        if not force and self.tutor_clinical_loaded and monotonic() - self._tutor_loaded_at < 60:
            return
        reservations_only = (reservations_only and self.tutor_clinical_loaded
                             and monotonic() - self._tutor_history_loaded_at < 60)
        self._clinic_generation += 1
        self.clinic_loading = True
        self.clinic_message = ''
        self._tutor_loaded_at = 0.0
        self.tutor_clinical_loaded = False
        self._invalidate_pdf_export()
        self.detail_id = ''
        self.detail = {}
        self.detail_sections = {}
        if not reservations_only:
            self.history_rows = {}
        self.consultation_rows = []
        # The concrete State owns this mixin's background handlers.
        return self.__class__.fetch_tutor_clinical(self._clinic_generation, reservations_only)

    @rx.event
    async def load_tutor_clinical(self):
        event = self._prepare_tutor_clinical(force=True)
        if event is not None:
            yield event

    def _tutor_load_current(self, generation, session, token, pet):
        return (generation == self._clinic_generation and self._clinical_current(session, token)
                and pet == self.selected_pet_id)

    @rx.event
    def ensure_tutor_clinical(self):
        return self._prepare_tutor_clinical()

    def _tutor_load_error(self, error):
        if error.status_code == 401:
            self._expire_session()
        elif error.status_code in (403, 404):
            self._clear_pet_context()
            self.pet_detail_message = str(error)
            self.pet_message = str(error)
        else:
            self.clinic_message = str(error)

    @rx.event(background=True)
    async def fetch_tutor_clinical(self, generation: int, reservations_only: bool = False):
        async with self:
            session, token, pet = self._session_generation, self._auth_token, self.selected_pet_id
            if not pet or not self.clinic_loading or not self._tutor_load_current(generation, session, token, pet):
                return
            if self._tutor_running == generation:
                return
            self._tutor_running = generation
            history = {key: [dict(row) for row in rows] for key, rows in self.history_rows.items()}
        error = None
        try:
            reads = [xano_request('GET', GROUP, 'tutor/consultas?' + urlencode({'pet_id': pet}), auth_token=token)]
            if not reservations_only:
                reads.insert(0, xano_request('GET', GROUP, f'tutor/pets/{pet}/historico', auth_token=token))
            async with xano_request_batch():
                results = await asyncio.gather(*reads, return_exceptions=True)
            errors = [item for item in results if isinstance(item, BaseException)]
            if errors:
                raise next((item for item in errors if isinstance(item, XanoRequestError) and item.status_code in (401, 403, 404)), errors[0])
            if reservations_only:
                appointments = results[0]
            else:
                history, appointments = results
                if not isinstance(history, dict) or not all(isinstance(rows, list) for rows in history.values()):
                    raise XanoRequestError('O Xano retornou uma resposta inválida.')
                history = {key: cards(rows) for key, rows in history.items()}
            if not isinstance(appointments, list):
                raise XanoRequestError('O Xano retornou uma resposta inválida.')
            appointments = cards(appointments)
        except XanoRequestError as caught:
            error = caught
        except (TypeError, ValueError, KeyError):
            error = XanoRequestError('O Xano retornou uma resposta inválida.')
        async with self:
            if not self._tutor_load_current(generation, session, token, pet):
                return
            self.clinic_loading = False
            if error is not None:
                self._tutor_load_error(error)
            else:
                self._tutor_history_pet = pet
                self.history_rows = self._with_record_backgrounds(history, pet)
                self.consultation_rows = self._with_record_backgrounds({"consultas": appointments}, pet)["consultas"]
                if not reservations_only:
                    self._tutor_history_loaded_at = monotonic()
                self._tutor_loaded_at = self._tutor_history_loaded_at
                self.tutor_clinical_loaded = True

    def _prepare_tutor_auxiliary(self, force: bool = False):
        if self.profile != 'tutor' or not self.selected_pet_id or not self._auth_token:
            return
        if self.auxiliary_loading and not force:
            return
        if self.auxiliary_loaded and not force:
            return
        self._auxiliary_generation += 1
        self.auxiliary_loading = True
        self.auxiliary_loaded = False
        self.auxiliary_message = ''
        self.access_rows = self.audit_rows = []
        return self.__class__.fetch_tutor_auxiliary(self._auxiliary_generation)

    @rx.event
    def load_tutor_auxiliary(self, force: bool = False):
        return self._prepare_tutor_auxiliary(force)

    @rx.event(background=True)
    async def fetch_tutor_auxiliary(self, generation: int):
        async with self:
            session, token, pet = self._session_generation, self._auth_token, self.selected_pet_id
            if not pet or generation != self._auxiliary_generation or not self.auxiliary_loading:
                return
            if self._auxiliary_running == generation:
                return
            self._auxiliary_running = generation
        error = None
        try:
            # Auxiliary reads are sequential to limit pressure on the Xano quota.
            accesses = await xano_request('GET', GROUP, f'tutor/pets/{pet}/acessos', auth_token=token)
            logs = await xano_request('GET', GROUP, f'tutor/pets/{pet}/auditoria', auth_token=token)
            if not isinstance(accesses, list) or not isinstance(logs, list):
                raise XanoRequestError('O Xano retornou uma resposta inválida.')
            accesses, logs = cards(accesses), cards(logs)
        except XanoRequestError as caught:
            error = caught
        except (TypeError, ValueError, KeyError):
            error = XanoRequestError('O Xano retornou uma resposta inválida.')
        async with self:
            if generation != self._auxiliary_generation or not self._clinical_current(session, token) or pet != self.selected_pet_id:
                return
            self.auxiliary_loading = False
            if error is not None:
                if error.status_code in (401, 403, 404):
                    self._tutor_load_error(error)
                else:
                    self.auxiliary_message = str(error)
            else:
                self.access_rows, self.audit_rows = accesses, logs
                self.auxiliary_loaded = True

    def _invalidate_pdf_export(self):
        self._pdf_generation += 1
        self.pdf_export_busy = self.pdf_preview_loading = False
        self.pdf_preview_open = self.pdf_preview_ready = False
        self.pdf_export_message = ""
        self.pdf_preview_title = ""
        self.pdf_preview_token = ""
        self._pdf_preview_bytes = b""
        self.pdf_preview_fields = []
        self.pdf_preview_sections = []
        self._pdf_key = self._pdf_signature = ""
        self._pdf_target = ("", "")
        self._pdf_route = self._pdf_profile = self._pdf_origin = ""

    @rx.var
    def consultation_pdf_available(self) -> bool:
        return pdf_export_enabled()

    def _pdf_location(self):
        return self.router.url.path + "?" + urlencode(sorted(self.router.url.query_parameters.items()))

    def _open_pdf_preview(self, pet, consultation, origin, trigger):
        if (not pdf_export_enabled() or not self.is_authenticated or not self._auth_token
                or self.profile not in ("tutor", "veterinario")):
            return
        try:
            target = (str(positive_id(pet)), str(positive_id(consultation)))
        except ConsultationPDFError:
            return
        # Repeated clicks while the same panel is open reuse its authorized read.
        if self.pdf_preview_open and self._pdf_target == target and self._pdf_profile == self.profile:
            return
        self._invalidate_pdf_export()
        self._pdf_target = target
        self._pdf_profile, self._pdf_origin = self.profile, origin
        self._pdf_route, self._pdf_trigger = self._pdf_location(), trigger
        self.pdf_preview_token = str(uuid4())
        self.pdf_preview_open = self.pdf_preview_loading = True
        return self.__class__.load_consultation_pdf_preview(self._pdf_generation)

    @rx.event
    def open_consultation_pdf(self):
        if self.profile == "tutor":
            if self.active_section == "Consultas" and self.detail.get("status") == "finalizada":
                return self._open_pdf_preview(self.selected_pet_id, self.detail_id, "tutor", "consultation-pdf-trigger")
        elif self.profile == "veterinario" and self.clinical_status == "finalizada":
            return self._open_pdf_preview(self.clinical_pet_id, self.clinical_id, "attendance", "attendance-pdf-trigger")

    def _pdf_agenda_allowed(self, pet, consultation):
        rows = self.upcoming_rows if self.vet_section == "Consultas" else self.agenda_rows
        return any(r.get("id") == consultation and r.get("pet_id") == pet
                   and r.get("status") == "finalizada" and r.get("autorizado") == "sim" for r in rows)

    @rx.event
    def open_agenda_consultation_pdf(self, pet: str, consultation: str):
        if self.profile != "veterinario":
            return
        if self._pdf_agenda_allowed(pet, consultation):
            return self._open_pdf_preview(pet, consultation, "agenda", "agenda-pdf-" + consultation)

    @rx.event
    def change_pdf_preview_open(self, opened: bool):
        if not opened:
            self._invalidate_pdf_export()
            return rx.call_script("window.vetTechPDFPreview?.clear()")

    @rx.event
    def restore_pdf_focus(self):
        return rx.call_script("document.getElementById(" + json.dumps(self._pdf_trigger) + ")?.focus()")

    def _pdf_current(self, generation, session, token, pet, consultation):
        common = (pdf_export_enabled() and generation == self._pdf_generation
                  and self._clinical_current(session, token) and self.is_authenticated
                  and self.pdf_preview_open and self.profile == self._pdf_profile
                  and (pet, consultation) == self._pdf_target and self._pdf_location() == self._pdf_route)
        if not common:
            return False
        if self._pdf_origin == "tutor":
            return (self.profile == "tutor" and pet == self.selected_pet_id
                    and consultation == self.detail_id and self.active_section == "Consultas"
                    and self.detail.get("status") == "finalizada")
        if self._pdf_origin == "attendance":
            return (self.profile == "veterinario" and pet == self.clinical_pet_id
                    and consultation == self.clinical_id and self.clinical_status == "finalizada")
        return self._pdf_origin == "agenda" and self.profile == "veterinario" and self._pdf_agenda_allowed(pet, consultation)

    def _set_pdf_preview(self, document, content=b""):
        self._pdf_signature = sha256(repr(document).encode()).hexdigest()
        self.pdf_preview_title = document.pet_name + " · Consulta nº " + str(document.consultation_id)
        # Bytes are private and limited by the existing renderer; never a public State var or URL.
        self._pdf_preview_bytes = content
        self.pdf_preview_fields = []
        self.pdf_preview_sections = []
        self.pdf_preview_ready = True

    def _show_pdf_preview(self, content):
        encoded = base64.b64encode(content).decode("ascii")
        return rx.call_script("window.vetTechPDFPreview?.show(" + json.dumps(encoded) + "," + json.dumps(self.pdf_preview_token) + ")")

    def _pdf_failure(self, error):
        if isinstance(error, XanoRequestError):
            if error.session_invalid:
                self._expire_session()
                return
            if error.status_code in (403, 404):
                # Do not leave sensitive preview data visible after a denial.
                self.pdf_preview_ready = False
                self.pdf_preview_title = ""
                self.pdf_preview_fields = []
                self.pdf_preview_sections = []
                self._pdf_signature = self._pdf_key = ""
                self._pdf_preview_bytes = b""
            self.pdf_export_message = {403: "Você não tem acesso a esta consulta.",
                404: "Consulta não disponível para exportação.",
                400: "Não foi possível exportar esta consulta. Atualize o prontuário.",
                409: "A consulta foi alterada. Atualize o prontuário.",
                429: "Aguarde alguns instantes e tente novamente."}.get(error.status_code,
                    "Não foi possível exportar o PDF. Tente novamente.")
        else:
            self.pdf_export_message = "Não foi possível gerar o PDF. Tente novamente."

    @rx.event(background=True)
    async def load_consultation_pdf_preview(self, generation: int):
        async with self:
            session, token = self._session_generation, self._auth_token
            pet, consultation = self._pdf_target
            if not self.pdf_preview_loading or not self._pdf_current(generation, session, token, pet, consultation):
                return
            profile = self._pdf_profile
        try:
            payload = await xano_request("GET", GROUP,
                f"{profile}/pets/{positive_id(pet)}/consultas/{positive_id(consultation)}/previa-pdf", auth_token=token)
            document = map_consultation_document(payload, pet, consultation)
            del payload
            async with self:
                if not self._pdf_current(generation, session, token, pet, consultation):
                    return
            content = await asyncio.wait_for(asyncio.to_thread(render_consultation_pdf, document), timeout=RENDER_TIMEOUT_SECONDS)
            async with self:
                if self._pdf_current(generation, session, token, pet, consultation):
                    self._set_pdf_preview(document, content)
                    yield self._show_pdf_preview(content)
        except Exception as error:
            async with self:
                if self._pdf_current(generation, session, token, pet, consultation):
                    self._pdf_failure(error)
                    if isinstance(error, XanoRequestError) and error.status_code in (401, 403, 404):
                        yield rx.call_script("window.vetTechPDFPreview?.clear()")
        finally:
            async with self:
                if self._pdf_current(generation, session, token, pet, consultation):
                    self.pdf_preview_loading = False

    @rx.event
    def retry_pdf_preview(self):
        if self.pdf_preview_open and not self.pdf_preview_ready and not self.pdf_preview_loading and not self.pdf_export_busy:
            self._pdf_generation += 1
            self.pdf_preview_loading = True
            self.pdf_export_message = ""
            return self.__class__.load_consultation_pdf_preview(self._pdf_generation)

    @rx.event
    def request_consultation_pdf(self):
        if (not pdf_export_enabled() or self.pdf_export_busy or self.pdf_preview_loading
                or not self.pdf_preview_ready or not self.pdf_preview_open):
            return
        pet, consultation = self._pdf_target
        if not self._pdf_current(self._pdf_generation, self._session_generation, self._auth_token, pet, consultation):
            return
        if not self._pdf_key:
            self._pdf_key = str(uuid4())
        self._pdf_generation += 1
        self.pdf_export_busy = True
        self.pdf_export_message = ""
        return self.__class__.generate_consultation_pdf(self._pdf_generation)

    @rx.event(background=True)
    async def generate_consultation_pdf(self, generation: int):
        async with self:
            session, token = self._session_generation, self._auth_token
            pet, consultation = self._pdf_target
            if not self.pdf_export_busy or not self._pdf_current(generation, session, token, pet, consultation):
                return
            operation, profile, signature = self._pdf_key, self._pdf_profile, self._pdf_signature
        try:
            # One authorized request for download; no history/catalog refresh.
            payload = await xano_request("POST", GROUP,
                f"{profile}/pets/{positive_id(pet)}/consultas/{positive_id(consultation)}/exportar",
                auth_token=token, json_payload={"operacao": operation})
            async with self:
                if not self._pdf_current(generation, session, token, pet, consultation):
                    return
            document = map_consultation_document(payload, pet, consultation)
            del payload
            if sha256(repr(document).encode()).hexdigest() != signature:
                content = await asyncio.wait_for(asyncio.to_thread(render_consultation_pdf, document), timeout=RENDER_TIMEOUT_SECONDS)
                async with self:
                    if self._pdf_current(generation, session, token, pet, consultation):
                        self._set_pdf_preview(document, content)
                        self._pdf_key = ""
                        self.pdf_export_message = "As informações foram atualizadas. Confira a prévia e clique novamente em Baixar PDF."
                        yield self._show_pdf_preview(content)
                return
            async with self:
                if not self._pdf_current(generation, session, token, pet, consultation):
                    return
                content = self._pdf_preview_bytes
            if not content:
                content = await asyncio.wait_for(asyncio.to_thread(render_consultation_pdf, document), timeout=RENDER_TIMEOUT_SECONDS)
            async with self:
                if not self._pdf_current(generation, session, token, pet, consultation):
                    return
                self._pdf_key = ""
                self.pdf_export_busy = False
                self.pdf_export_message = "PDF pronto para download."
                yield rx.download(data=content, filename=document.filename, mime_type="application/pdf")
        except Exception as error:
            async with self:
                if self._pdf_current(generation, session, token, pet, consultation):
                    self._pdf_failure(error)
                    if isinstance(error, XanoRequestError) and error.status_code in (401, 403, 404):
                        yield rx.call_script("window.vetTechPDFPreview?.clear()")
        finally:
            async with self:
                if self._pdf_current(generation, session, token, pet, consultation):
                    self.pdf_export_busy = False

    @rx.event
    def show_consultation_detail(self, value: str):
        self._invalidate_pdf_export()
        self.detail_id = value
        self.detail = next((dict(r) for r in self.history_rows.get("consultas", []) if r["id"] == value), {})
        day = date.fromisoformat(today())
        self.detail_sections = {key: [care_status(r, key, day) for r in rows if r.get("consulta_id") == value]
                                for key, rows in self.history_rows.items() if key != "consultas"}
        self.active_section = "Consultas"

    @rx.event
    async def change_consent(self, access_id: str, status: str):
        if self.clinic_busy or not self.selected_pet_id:
            return
        session, token, pet = self._session_generation, self._auth_token, self.selected_pet_id
        self.clinic_busy = True
        yield
        try:
            await xano_request("PUT", GROUP, f"tutor/pets/{pet}/acessos/{access_id}", auth_token=token, json_payload={"status": status})
            if self._clinical_current(session, token) and pet == self.selected_pet_id:
                event = self._prepare_tutor_auxiliary(force=True)
                if event is not None:
                    yield event
        except XanoRequestError as error:
            if self._clinical_current(session, token):
                self._clinic_error(error)
        finally:
            if self._clinical_current(session, token):
                self.clinic_busy = False

    @rx.event
    async def enter_veterinary_agenda(self):
        if self.profile != "veterinario":
            return
        section = {"horarios": "Horários", "consultas": "Consultas"}.get(
            self.router.url.query_parameters.get("secao", "horarios"), "Horários")
        async for event in self.vet_navigate(section):
            yield event

    @rx.event
    async def vet_navigate(self, section: str):
        if section not in ("Horários", "Consultas") or self.profile != "veterinario":
            return
        self.vet_section = section
        self.agenda_page = 1
        if not self.agenda_day:
            self.agenda_day = today()
        async for event in self.load_agenda():
            yield event

    @rx.event
    async def agenda_today(self):
        async for event in self.agenda_choose_day(today()):
            yield event

    @rx.event
    async def agenda_day_by(self, offset: int):
        value = (agenda_date(self.agenda_day) + timedelta(days=offset)).isoformat()
        async for event in self.agenda_choose_day(value):
            yield event

    @rx.event
    def agenda_calendar_set_open(self, value: bool):
        if self.profile != "veterinario":
            return
        if value:
            self.agenda_calendar_month = (self.agenda_day or today())[:7]
        self.agenda_calendar_open = value

    @rx.event
    def agenda_calendar_shift(self, offset: int):
        if self.profile != "veterinario":
            return
        year, month = map(int, (self.agenda_calendar_month or today()[:7]).split("-"))
        serial = year * 12 + month - 1 + offset
        if 12 <= serial < 120000:
            self.agenda_calendar_month = f"{serial // 12:04d}-{serial % 12 + 1:02d}"

    @rx.event
    def agenda_calendar_choose_month(self, value: str):
        if self.profile == "veterinario" and value in [name.capitalize() for name in MONTHS]:
            month = [name.capitalize() for name in MONTHS].index(value) + 1
            self.agenda_calendar_month = f"{self.agenda_calendar_year}-{month:02d}"

    @rx.event
    def agenda_calendar_choose_year(self, value: str):
        if self.profile == "veterinario" and value.isascii() and value.isdecimal() and 1 <= int(value) <= 9999:
            self.agenda_calendar_month = f"{int(value):04d}-" + (self.agenda_calendar_month or today()[:7])[5:7]

    @rx.event
    async def agenda_choose_day(self, value: str):
        try:
            date.fromisoformat(value)
        except ValueError:
            return
        self.agenda_day = value
        self.agenda_calendar_open = False
        self.agenda_page = 1
        async for event in self.load_agenda():
            yield event

    @rx.event
    async def agenda_page_by(self, offset: int):
        self.agenda_page = max(1, self.agenda_page + offset)
        async for event in self.load_agenda():
            yield event

    def _clear_consultation_summary(self):
        self._consultation_generation += 1
        self.consultation_selected = ""
        self.consultation_info = {}
        self.consultation_summary_loading = False
        self.consultation_summary_error = ""

    @rx.event
    async def filter_consultations(self, field: str, value: str):
        if self.profile != "veterinario":
            return
        if field == "tab" and value in ("Pendentes", "Hoje", "Próximas", "Concluídas", "Canceladas"):
            self.consultation_tab = value
            self.consultation_status = "Todos os estados"
        elif field == "search":
            self.consultation_search = value[:100]
        elif field == "status" and value in ("Todos os estados", "Agendada", "Em atendimento", "Concluída", "Cancelada"):
            self.consultation_status = value
        else:
            return
        self.agenda_page = 1
        async for event in self.load_agenda():
            yield event

    @rx.event
    async def select_consultation(self, value: str):
        if self.profile != "veterinario" or self.vet_section != "Consultas":
            return
        row = next((row for row in self.upcoming_rows if row["id"] == value and row["autorizado"] == "sim"), None)
        if not row:
            return
        self._clear_consultation_summary()
        self.consultation_selected = value
        self.consultation_summary_loading = True
        generation, session, token = self._consultation_generation, self._session_generation, self._auth_token
        yield
        try:
            data = await xano_request("GET", GROUP, f"veterinario/pets/{int(row['pet_id'])}/historico", auth_token=token)
            if generation == self._consultation_generation and self._clinical_current(session, token):
                self.consultation_info = consultation_summary(data["pet"], data["historico"])
                self.consultation_info.update(patient_photo(data["pet"], row["pet_id"], self.agenda_rows + self.upcoming_rows))
                self.consultation_info.update(motivo=row.get("motivo", ""), pet_id=row["pet_id"], status=row.get("status", ""))
        except (ValueError, XanoRequestError) as error:
            if generation == self._consultation_generation and self._clinical_current(session, token):
                self.consultation_info = {}
                self.consultation_summary_error = "Não foi possível carregar o resumo. Atualize a lista ou selecione o paciente novamente."
                if isinstance(error, XanoRequestError):
                    self._clinic_error(error)
        finally:
            if generation == self._consultation_generation and self._clinical_current(session, token):
                self.consultation_summary_loading = False

    @rx.event
    async def load_agenda(self):
        self._invalidate_pdf_export()
        if self.profile != "veterinario":
            return
        if not self.agenda_day:
            self.agenda_day = today()
        self._clinic_generation += 1
        generation, session, token = self._clinic_generation, self._session_generation, self._auth_token
        self._clear_consultation_summary()
        self.clinic_loading = True
        self.clinic_message = ""
        self.agenda_total = 0
        self.agenda_rows = []
        self.upcoming_rows = []
        self._prior_generation += 1
        self.prior_history = {}
        self.prior_history_message = ""
        self.prior_pet_info = {}
        yield
        try:
            params = {"page": self.agenda_page}
            if self.vet_section == "Horários":
                params["dia"] = self.agenda_day or today()
            else:
                params.update(aba=self.consultation_tab, busca=self.consultation_search,
                              estado={"Agendada": "agendada", "Em atendimento": "em_atendimento", "Concluída": "finalizada", "Cancelada": "cancelada"}.get(self.consultation_status, ""))
            data = await xano_request("GET", GROUP, "veterinario/agenda?" + urlencode(params), auth_token=token)
            if generation == self._clinic_generation and self._clinical_current(session, token):
                if self.vet_section == "Consultas" and (
                    data.get("contrato_consultas") not in (1, 2, 3) or
                    (self.consultation_tab == "Próximas" and data.get("contrato_consultas") != 3) or
                    ((self.consultation_tab == "Canceladas" or self.consultation_status == "Cancelada") and data.get("contrato_consultas") not in (2, 3))
                ) and (
                    self.consultation_tab != "Pendentes" or self.consultation_search or self.consultation_status != "Todos os estados"
                ):
                    self.agenda_total = 0
                    self.clinic_message = "Os filtros de consultas precisam da atualização da API Xano. A lista de pendentes continua disponível."
                    return
                rows = cards(data["items"])
                for row, source in zip(rows, data["items"]):
                    instant = datetime.fromtimestamp(int(row["agendada_para"]) / 1000, TZ)
                    row["hora"] = instant.strftime("%H:%M")
                    row["hora_grupo"] = str(instant.hour)
                    photo = patient_photo({"foto": source["pet_foto"]} if "pet_foto" in source else {}) if row["autorizado"] == "sim" else {"foto": "", "foto_ausente": "nao"}
                    row["pet_foto"] = photo["foto"]
                    row["foto_ausente"] = photo["foto_ausente"]
                    row["status_label"] = {"agendada": "Agendada", "em_atendimento": "Em atendimento", "finalizada": "Concluída", "cancelada": "Cancelada"}.get(row["status"], "Não informado")
                    row["top"] = str(max(0, (instant.hour * 60 + instant.minute - 480) * 1.5)) + "px"
                if self.vet_section == "Horários":
                    self.agenda_rows = rows
                else:
                    self.upcoming_rows = rows
                self.agenda_total = int(data["total"])
        except XanoRequestError as error:
            if generation == self._clinic_generation and self._clinical_current(session, token):
                self._clinic_error(error)
        finally:
            if generation == self._clinic_generation and self._clinical_current(session, token):
                self.clinic_loading = False

    @rx.event
    async def start_consultation(self, value: str):
        if self.clinic_busy or self.profile != "veterinario":
            return
        session, token = self._session_generation, self._auth_token
        self.clinic_busy = True
        yield
        try:
            await xano_request("POST", GROUP, f"veterinario/consultas/{int(value)}/iniciar", auth_token=token)
            if self._clinical_current(session, token):
                yield rx.redirect(f"/atendimento/{int(value)}")
        except (ValueError, XanoRequestError) as error:
            if self._clinical_current(session, token):
                self.clinic_message = str(error)
        finally:
            if self._clinical_current(session, token):
                self.clinic_busy = False

    @rx.event
    async def load_attendance(self):
        self._invalidate_pdf_export()
        self._clear_clinical_calendar()
        self._clinic_generation += 1
        generation, session, token = self._clinic_generation, self._session_generation, self._auth_token
        self.clinic_message = ""
        self.clinic_loading = True
        self.clinical_id = ""
        self.clinical_agenda_day = ""
        self.clinical_pet_info = {}
        self.clinical_lines = {key: [] for key in GROUPS}
        if self.profile != "veterinario" or not token:
            self.clinic_loading = False
            yield rx.redirect("/login")
            return
        yield
        try:
            value = int(self.router.page.params.get("consulta_id", "0"))
            data = await xano_request("GET", GROUP, f"veterinario/consultas/{value}/rascunho", auth_token=token)
            if generation != self._clinic_generation or not self._clinical_current(session, token):
                return
            row = data["consulta"]
            self.clinical_id = str(row["id"])
            scheduled = instant_datetime(row.get("agendada_para"))
            self.clinical_agenda_day = scheduled.date().isoformat() if scheduled else (self.agenda_day or today())
            self.clinical_pet_id = str(row["pet_id"])
            self.clinical_pet_name = str(data["pet"]["nome"])
            self.clinical_pet_info = pet_summary(data["pet"])
            self.clinical_pet_info.update(patient_photo(data["pet"], self.clinical_pet_id, self.agenda_rows + self.upcoming_rows))
            self.clinical_status = row["status"]
            self.clinical_version = int(row["versao"])
            draft = row.get("rascunho") or {}
            self.clinical_reason = draft.get("motivo", row.get("motivo", ""))
            self.clinical_diagnosis = draft.get("diagnostico", "")
            self.clinical_notes = draft.get("obs", "")
            self.clinical_date = draft.get("data_atendimento") or today()
            self.clinical_return = draft.get("retorno_previsto") or ""
            self.clinical_lines = {key: [{k: "" if v is None else str(v) for k, v in r.items()}
                                         for r in draft.get(key, [])] for key in GROUPS}
            self.clinical_dirty = False
            self._save_uncertain = False
            if self.clinical_status == "finalizada":
                self.disease_options = []
                return
            catalog = await xano_request("GET", GROUP, f"veterinario/pets/{self.clinical_pet_id}/doencas", auth_token=token)
            if generation == self._clinic_generation and self._clinical_current(session, token):
                self.disease_options = cards(catalog)
        except (ValueError, XanoRequestError) as error:
            if generation == self._clinic_generation and self._clinical_current(session, token):
                if isinstance(error, XanoRequestError):
                    self._clinic_error(error)
                else:
                    self.clinic_message = "Consulta inválida."
        finally:
            if generation == self._clinic_generation and self._clinical_current(session, token):
                self.clinic_loading = False

    @rx.event
    def clinical_field(self, field: str, value: str):
        fields = {"motivo": "clinical_reason", "diagnostico": "clinical_diagnosis", "obs": "clinical_notes",
                  "data_atendimento": "clinical_date", "retorno_previsto": "clinical_return"}
        if field in fields and not self.clinic_busy and not self._save_uncertain:
            setattr(self, fields[field], value)
            self.clinical_dirty = True

    @rx.event
    def clinical_add_line(self, group: str):
        if group in GROUPS and not self.clinic_busy and not self._save_uncertain:
            data = deepcopy(self.clinical_lines)
            fields = {"vacinas": ["vacina", "lote", "data_aplicacao", "data_prox_dose"],
                      "medicamentos": ["nome", "dose", "unidade", "frequencia", "via", "tipo", "data_inicio", "data_fim"],
                      "doencas": ["doenca_id", "data_diagnostico", "estado", "observacoes"],
                      "exames": ["tipo", "status", "data_solicitacao", "data_realizacao", "resultado"]}[group]
            row = {key: "" for key in fields}
            row["linha_id"] = str(uuid4())
            data[group].append(row)
            self.clinical_lines = data
            self.clinical_dirty = True

    @rx.event
    def clinical_line_field(self, group: str, line: str, field: str, value: str):
        if group not in GROUPS or self.clinic_busy or self._save_uncertain:
            return
        data = deepcopy(self.clinical_lines)
        for row in data[group]:
            if row["linha_id"] == line and field in row and field != "linha_id":
                row[field] = value
        self.clinical_lines = data
        self.clinical_dirty = True

    @rx.event
    def clinical_remove_line(self, group: str, line: str):
        if group in GROUPS and not self.clinic_busy and not self._save_uncertain:
            data = deepcopy(self.clinical_lines)
            data[group] = [r for r in data[group] if r["linha_id"] != line]
            self.clinical_lines = data
            self.clinical_dirty = True

    def _clinical_payload(self):
        return {"motivo": self.clinical_reason, "diagnostico": self.clinical_diagnosis,
                "obs": self.clinical_notes, "data_atendimento": self.clinical_date,
                "retorno_previsto": self.clinical_return, **deepcopy(self.clinical_lines)}

    def _confirm_completed_attendance(self):
        """Update existing cards without navigating or loading the agenda again."""
        self._clear_clinical_calendar()
        self.agenda_rows = [dict(row, status="finalizada", status_label="Concluída")
                            if row.get("id") == self.clinical_id else row for row in self.agenda_rows]
        self.upcoming_rows = [row for row in self.upcoming_rows if row.get("id") != self.clinical_id]

    @rx.event
    async def save_attendance(self, finalize: bool = False):
        if self.clinic_busy or not self.clinical_id or self.profile != "veterinario":
            return
        session, token, value = self._session_generation, self._auth_token, self.clinical_id
        self.clinic_busy = True
        self.clinic_message = ""
        yield
        try:
            if self._save_uncertain:
                current = await xano_request("GET", GROUP, f"veterinario/consultas/{value}/rascunho", auth_token=token)
                if not self._clinical_current(session, token) or value != self.clinical_id:
                    return
                row = current["consulta"]
                if row["status"] == "finalizada":
                    self.clinical_status = "finalizada"
                    self.clinical_dirty = False
                    self._save_uncertain = False
                    self.clinic_message = "Consulta finalizada. Registros disponíveis ao tutor."
                    self._confirm_completed_attendance()
                    yield attendance_saved_toast(True)
                    return
                if row["versao"] != self._pending_version:
                    if row.get("rascunho") == self._pending_payload:
                        self.clinical_version = row["versao"]
                        self.clinical_dirty = False
                        self._save_uncertain = False
                        self.clinic_message = "Rascunho salvo e confirmado."
                        yield attendance_saved_toast(False)
                        return
                    self.clinic_message = "Houve outra alteração. Recarregue a consulta antes de continuar."
                    return
                self._save_uncertain = False
            payload = self._clinical_payload()
            self._pending_payload = deepcopy(payload)
            self._pending_version = self.clinical_version
            action = "finalizar" if finalize else "rascunho"
            result = await xano_request("POST" if finalize else "PUT", GROUP,
                f"veterinario/consultas/{value}/{action}", auth_token=token,
                json_payload={"payload": payload, "versao": self.clinical_version})
            if self._clinical_current(session, token) and value == self.clinical_id:
                self.clinical_version = result["versao"]
                self.clinical_status = result["status"]
                self.clinical_dirty = False
                self._save_uncertain = False
                self.clinic_message = "Consulta finalizada. Registros disponíveis ao tutor." if finalize else "Rascunho salvo."
                if finalize:
                    self._confirm_completed_attendance()
                    yield attendance_saved_toast(True)
                else:
                    yield attendance_saved_toast(False)
        except XanoRequestError as error:
            if self._clinical_current(session, token) and value == self.clinical_id:
                self._save_uncertain = error.status_code is None or error.status_code >= 500
                self._clinic_error(error)
        finally:
            if self._clinical_current(session, token):
                self.clinic_busy = False

    @rx.event
    async def create_disease(self):
        if self.clinic_busy or not self.clinical_pet_id:
            return
        session, token, value = self._session_generation, self._auth_token, self.clinical_id
        self.clinic_busy = True
        yield
        try:
            row = await xano_request("POST", GROUP, f"veterinario/pets/{self.clinical_pet_id}/doencas", auth_token=token,
                                    json_payload={"payload": {"nome": self.disease_name, "descricao": self.disease_description}})
            if self._clinical_current(session, token) and value == self.clinical_id:
                if not any(item["id"] == str(row["id"]) for item in self.disease_options):
                    self.disease_options += cards([row])
                self.disease_name = self.disease_description = ""
        except XanoRequestError as error:
            if self._clinical_current(session, token):
                self._clinic_error(error)
        finally:
            if self._clinical_current(session, token):
                self.clinic_busy = False

    @rx.event
    def restore_prior_history_focus(self, trigger_id: str):
        return rx.call_script("document.getElementById(" + json.dumps(trigger_id) + ")?.focus()")

    @rx.event
    def prepare_prior_history(self):
        """Clear the previous presentation before opening the attendance dialog."""
        self.prior_history = {}
        self.prior_history_message = ""
        self.prior_pet_info = {}

    @rx.event
    async def open_prior_history(self, pet_id: str):
        self._prior_generation += 1
        generation = self._prior_generation
        self.prior_history = {}
        self.prior_history_message = ""
        self.prior_pet_info = {}
        session, token = self._session_generation, self._auth_token
        try:
            data = await xano_request("GET", GROUP, f"veterinario/pets/{int(pet_id)}/historico", auth_token=token)
            if generation == self._prior_generation and self._clinical_current(session, token):
                self.prior_pet_info = pet_summary(data["pet"])
                self.prior_pet_info.update(patient_photo(data["pet"], pet_id, self.agenda_rows + self.upcoming_rows))
                self.prior_history = {key: cards(rows) for key, rows in data["historico"].items()}
        except (ValueError, XanoRequestError) as error:
            if generation == self._prior_generation and self._clinical_current(session, token):
                self.prior_history_message = str(error)

    @rx.event
    def leave_attendance(self, discard: bool = False):
        if self.clinic_busy:
            return
        if self.clinical_dirty and not discard:
            self.clinical_confirm_leave = True
            return
        self.clinical_confirm_leave = False
        self.clinical_dirty = False
        self._invalidate_pdf_export()
        self._clear_clinical_calendar()
        return rx.redirect("/")
