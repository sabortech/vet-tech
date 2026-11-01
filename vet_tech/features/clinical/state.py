"""Feature mixin: keeps one authenticated State and its session generation."""
import asyncio
import calendar
from time import monotonic
from copy import deepcopy
from datetime import date, datetime, timedelta
from typing import Any
from urllib.parse import urlencode
from uuid import uuid4
from zoneinfo import ZoneInfo

import reflex as rx

from vet_tech.shared.xano_client import XanoRequestError, xano_request
from vet_tech.features.navigation.state import CLINICAL_SECTIONS
from vet_tech.shared.dates import date_label, instant_label

GROUP = "vettech-clinical"
TZ = ZoneInfo("America/Sao_Paulo")
GROUPS = ("vacinas", "medicamentos", "doencas", "exames")


def today() -> str:
    return datetime.now(TZ).date().isoformat()


def display_date(value) -> str:
    return date_label(value) or "Não informado"


def cards(rows: list[dict]) -> list[dict[str, str]]:
    result = []
    for row in rows:
        item = {str(k): "" if v is None else str(v) for k, v in row.items()}
        item["quando"] = (instant_label(row["agendada_para"]) if row.get("agendada_para")
                          else date_label(row.get("data_atendimento") or row.get("data"))) or "Não informado"
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


def pet_summary(row: dict) -> dict[str, str]:
    return {"nome": str(row.get("nome") or "Pet"), "sexo": str(row.get("sexo") or "Não informado"),
            "nascimento": display_date(row.get("data_nasc")),
            "peso": str(row["peso_atual"]) if row.get("peso_atual") is not None else "Não informado"}


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
        if not self.booking_busy and not self._booking_uncertain:
            self.booking_professional = value

    @rx.event
    def set_detail_id(self, value: str):
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
    vet_section: str = "Consultas"
    agenda_day: str = ""
    agenda_rows: list[dict[str, str]] = []
    upcoming_rows: list[dict[str, str]] = []
    agenda_page: int = 1
    agenda_total: int = 0
    clinic_message: str = ""
    clinic_busy: bool = False
    clinic_loading: bool = False
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
    access_rows: list[dict[str, str]] = []
    audit_rows: list[dict[str, str]] = []
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
    clinical_date: str = ""
    clinical_return: str = ""
    clinical_lines: dict[str, list[dict[str, str]]] = {key: [] for key in GROUPS}
    clinical_dirty: bool = False
    clinical_confirm_leave: bool = False
    disease_options: list[dict[str, str]] = []
    disease_name: str = ""
    disease_description: str = ""
    prior_history: dict[str, list[dict[str, str]]] = {}
    _save_uncertain: bool = False
    _pending_version: int = -1
    _pending_payload: dict = {}
    _prior_generation: int = 0

    @rx.var
    def booking_locked(self) -> bool:
        return self.booking_busy or self._booking_uncertain

    @rx.var
    def clinical_locked(self) -> bool:
        return self.clinic_busy or self._save_uncertain

    def _clear_clinical_pet(self):
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
        self.agenda_rows = self.upcoming_rows = []
        self.clinical_id = self.clinical_pet_id = self.clinical_pet_name = ""
        self.clinical_pet_info = self.prior_pet_info = {}
        self.clinical_status = self.clinical_reason = self.clinical_diagnosis = self.clinical_notes = ""
        self.clinical_date = self.clinical_return = ""
        self.clinical_lines = {key: [] for key in GROUPS}
        self.prior_history = {}
        self.disease_options = []
        self.disease_name = self.disease_description = ""
        self.clinical_dirty = False
        self.clinical_confirm_leave = False
        self.clinic_busy = False
        self.vet_section = "Consultas"
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
                self._prior_generation += 1
                self.clinical_id = self.clinical_pet_id = self.clinical_pet_name = ""
                self.clinical_pet_info = self.prior_pet_info = {}
                self.clinical_reason = self.clinical_status = ""
                self.clinical_lines = {key: [] for key in GROUPS}
                self.clinical_diagnosis = self.clinical_notes = ""
                self.prior_history = {}

    @rx.var
    def booking_days(self) -> list[dict[str, str]]:
        month = self.booking_month or today()[:7]
        year, number = map(int, month.split("-"))
        return [{"date": d.isoformat(), "label": str(d.day) if d.month == number else "",
                 "disabled": "sim" if d.month != number or d.isoformat() < today() else "nao"}
                for week in calendar.Calendar().monthdatescalendar(year, number) for d in week]

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
        year, month = map(int, (self.booking_month or today()[:7]).split("-"))
        serial = year * 12 + month - 1 + offset
        self.booking_month = f"{serial // 12:04d}-{serial % 12 + 1:02d}"

    @rx.event
    def booking_choose_day(self, value: str):
        if not self._booking_uncertain:
            self.booking_day = value

    @rx.event
    def booking_next(self):
        try:
            instant = datetime.fromisoformat(f"{self.booking_day}T{self.booking_time}").replace(tzinfo=TZ)
            if not ("08:00" <= self.booking_time <= "17:00") or instant <= datetime.now(TZ):
                raise ValueError
        except ValueError:
            self.booking_message = "Escolha dia e horário futuros entre 08h e 17h."
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
                self.history_rows = history
                self.consultation_rows = appointments
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

    @rx.event
    def show_consultation_detail(self, value: str):
        self.detail_id = value
        self.detail = next((dict(r) for r in self.history_rows.get("consultas", []) if r["id"] == value), {})
        self.detail_sections = {key: [dict(r) for r in rows if r.get("consulta_id") == value]
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
    async def agenda_choose_day(self, value: str):
        try:
            date.fromisoformat(value)
        except ValueError:
            return
        self.agenda_day = value
        self.agenda_page = 1
        async for event in self.load_agenda():
            yield event

    @rx.event
    async def agenda_page_by(self, offset: int):
        self.agenda_page = max(1, self.agenda_page + offset)
        async for event in self.load_agenda():
            yield event

    @rx.event
    async def load_agenda(self):
        if self.profile != "veterinario":
            return
        self._clinic_generation += 1
        generation, session, token = self._clinic_generation, self._session_generation, self._auth_token
        self.clinic_loading = True
        self.clinic_message = ""
        self.agenda_rows = []
        self.upcoming_rows = []
        self._prior_generation += 1
        self.prior_history = {}
        self.prior_pet_info = {}
        yield
        try:
            params = {"page": self.agenda_page}
            if self.vet_section == "Horários":
                params["dia"] = self.agenda_day or today()
            data = await xano_request("GET", GROUP, "veterinario/agenda?" + urlencode(params), auth_token=token)
            if generation == self._clinic_generation and self._clinical_current(session, token):
                rows = cards(data["items"])
                for row in rows:
                    instant = datetime.fromtimestamp(int(row["agendada_para"]) / 1000, TZ)
                    row["hora"] = instant.strftime("%H:%M")
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
        self._clinic_generation += 1
        generation, session, token = self._clinic_generation, self._session_generation, self._auth_token
        self.clinic_message = ""
        self.clinic_loading = True
        self.clinical_id = ""
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
            self.clinical_pet_id = str(row["pet_id"])
            self.clinical_pet_name = str(data["pet"]["nome"])
            self.clinical_pet_info = pet_summary(data["pet"])
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
                    return
                if row["versao"] != self._pending_version:
                    if row.get("rascunho") == self._pending_payload:
                        self.clinical_version = row["versao"]
                        self.clinical_dirty = False
                        self._save_uncertain = False
                        self.clinic_message = "Rascunho salvo e confirmado."
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
    async def open_prior_history(self, pet_id: str):
        self._prior_generation += 1
        generation = self._prior_generation
        self.prior_history = {}
        self.prior_pet_info = {}
        session, token = self._session_generation, self._auth_token
        try:
            data = await xano_request("GET", GROUP, f"veterinario/pets/{int(pet_id)}/historico", auth_token=token)
            if generation == self._prior_generation and self._clinical_current(session, token):
                self.prior_pet_info = pet_summary(data["pet"])
                self.prior_history = {key: cards(rows) for key, rows in data["historico"].items()}
        except (ValueError, XanoRequestError) as error:
            if generation == self._prior_generation and self._clinical_current(session, token):
                self.clinic_message = str(error)

    @rx.event
    def leave_attendance(self, discard: bool = False):
        if self.clinic_busy:
            return
        if self.clinical_dirty and not discard:
            self.clinical_confirm_leave = True
            return
        self.clinical_confirm_leave = False
        self.clinical_dirty = False
        return rx.redirect("/")
