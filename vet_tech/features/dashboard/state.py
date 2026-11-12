import asyncio
import time
from datetime import date, datetime
from typing import Any, TypedDict
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

import reflex as rx

from vet_tech.shared.xano_client import XanoRequestError, xano_request, xano_request_batch
from vet_tech.shared.measurements import weight_label
from vet_tech.shared.dates import calendar_date, date_label, instant_datetime

GROUP = "vettech-clinical"
TZ = ZoneInfo("America/Sao_Paulo")


class DashboardDatedItem(TypedDict):
    nome: str
    data: str


class DashboardEvent(TypedDict):
    tipo: str
    data: str


class DashboardFollowup(TypedDict):
    tipo: str
    texto: str
    data: str


class DashboardActivity(TypedDict):
    tipo: str
    nome: str
    data: str


class DashboardVaccineIndicator(TypedDict):
    estado: str
    texto: str
    nome: str
    data: str


class DashboardPet(TypedDict):
    id: str
    nome: str
    especie: str
    raca: str
    idade: str
    peso: str
    foto: str
    indicador_vacina: DashboardVaccineIndicator
    proxima_vacina: DashboardDatedItem
    ultima_consulta: DashboardDatedItem
    proximo_evento: DashboardEvent
    acompanhamentos: list[DashboardFollowup]
    acompanhamentos_truncados: bool
    mensagem_acompanhamento: str
    atividade_recente: list[DashboardActivity]


def _date_value(value: Any) -> date | None:
    return calendar_date(value)


def _date_label(value: Any) -> str:
    return date_label(value)


def _date_sort_key(value: Any) -> date:
    return _date_value(value) or date.min


def _age_label(value: Any, today: date | None = None) -> str:
    birth = _date_value(value)
    current = today or datetime.now(TZ).date()
    if birth is None or birth > current:
        return "Idade não informada"
    years = current.year - birth.year - ((current.month, current.day) < (birth.month, birth.day))
    if years:
        return f"{years} {'ano' if years == 1 else 'anos'}"
    months = max(0, (current.year - birth.year) * 12 + current.month - birth.month
                 - (current.day < birth.day))
    if months:
        return f"{months} {'mês' if months == 1 else 'meses'}"
    return "Menos de 1 mês"


def project_pet(row: dict[str, Any], today: date | None = None) -> DashboardPet:
    current = today or datetime.now(TZ).date()
    consultations = [item for item in row.get("consultas", []) if isinstance(item, dict)]
    vaccines = [item for item in row.get("vacinas", []) if isinstance(item, dict)]
    exams = [item for item in row.get("exames", []) if isinstance(item, dict)]

    def consultation_date(item: dict[str, Any]) -> Any:
        return item.get("data_atendimento") or item.get("data") or item.get("agendada_para")

    finalized = [
        item for item in consultations
        if item.get("status") == "finalizada" and _date_value(consultation_date(item))
    ]
    finalized.sort(key=lambda item: _date_sort_key(consultation_date(item)), reverse=True)

    vaccine_dates = [
        item for item in vaccines
        if _date_value(item.get("data_prox_dose")) is not None
    ]
    upcoming_vaccines = [
        item for item in vaccine_dates
        if _date_value(item.get("data_prox_dose")) >= current
    ]
    upcoming_vaccines.sort(key=lambda item: _date_sort_key(item.get("data_prox_dose")))

    # Same future dose as the existing summary; otherwise show the latest past date.
    reference = upcoming_vaccines[0] if upcoming_vaccines else max(
        vaccine_dates, key=lambda item: _date_sort_key(item.get("data_prox_dose")), default=None
    )
    indicator: DashboardVaccineIndicator = {
        "estado": "sem-data", "texto": "Sem próxima dose registrada", "nome": "", "data": ""
    }
    if reference is not None:
        due = _date_value(reference.get("data_prox_dose"))
        days = (due - current).days
        unit = "dia" if abs(days) == 1 else "dias"
        if days > 7:
            tone, label = "futura", f"Próxima dose em {days} {unit}"
        elif days > 0:
            tone, label = "proxima", f"Dose prevista em {days} {unit}"
        elif days == 0:
            tone, label = "hoje", "Dose prevista para hoje"
        else:
            tone, label = "ultrapassada", f"Data prevista há {abs(days)} {unit} — confira os registros"
        indicator = {"estado": tone, "texto": label,
                     "nome": str(reference.get("vacina") or "Vacina"),
                     "data": _date_label(reference.get("data_prox_dose"))}

    events: list[dict[str, str]] = []
    for item in consultations:
        if item.get("status") == "agendada":
            when = item.get("agendada_para")
            instant = instant_datetime(when)
            event_date = instant.date() if instant else _date_value(when)
            if event_date and event_date >= current:
                events.append({
                    "tipo": "Consulta agendada",
                    "data": event_date.strftime("%d/%m/%Y"),
                    "ordem": event_date.isoformat(),
                })
        when = item.get("retorno_previsto")
        event_date = _date_value(when)
        if event_date and event_date >= current:
            events.append({
                "tipo": "Retorno previsto",
                "data": _date_label(when),
                "ordem": event_date.isoformat(),
            })
    for item in vaccines:
        when = item.get("data_prox_dose")
        event_date = _date_value(when)
        if event_date and event_date >= current:
            events.append({
                "tipo": f"Próxima dose: {item.get('vacina') or 'Vacina'}",
                "data": _date_label(when),
                "ordem": event_date.isoformat(),
            })
    events.sort(key=lambda item: item["ordem"])
    next_event = events[0] if events else {}

    followups: list[dict[str, str]] = []
    for item in vaccine_dates:
        due = _date_value(item.get("data_prox_dose"))
        if due and due < current:
            followups.append({
                "tipo": "vacina",
                "texto": f"Data registrada para a próxima dose de {item.get('vacina') or 'vacina'} ultrapassada.",
                "data": _date_label(item.get("data_prox_dose")),
            })
    for item in consultations:
        due = _date_value(item.get("retorno_previsto"))
        if due and due < current:
            followups.append({
                "tipo": "retorno",
                "texto": "Data registrada para o retorno ultrapassada.",
                "data": _date_label(item.get("retorno_previsto")),
            })
    for item in exams:
        if item.get("status") == "solicitado" and not item.get("data_realizacao"):
            followups.append({
                "tipo": "exame",
                "texto": f"A realização de {item.get('tipo') or 'exame'} não está registrada.",
                "data": _date_label(item.get("data_solicitacao")),
            })

    recent_vaccines = sorted(
        [
            item for item in vaccines
            if _date_value(item.get("data_aplicacao") or item.get("data")) is not None
        ],
        key=lambda item: _date_sort_key(item.get("data_aplicacao") or item.get("data")),
        reverse=True,
    )[:3]
    recent = [
        {
            "tipo": "Vacina",
            "nome": str(item.get("vacina") or "Vacina"),
            "data": str(item.get("data_aplicacao") or item.get("data")),
        }
        for item in recent_vaccines
    ]
    recent.extend(
        {
            "tipo": "Consulta",
            "nome": "Consulta finalizada",
            "data": str(consultation_date(item)),
        }
        for item in finalized[:3]
    )
    recent.sort(key=lambda item: _date_value(item["data"]) or date.min, reverse=True)
    for item in recent:
        item["data"] = _date_label(item["data"])

    photo = row.get("foto")
    if isinstance(photo, dict):
        photo = photo.get("url", "")
    photo = photo.strip() if isinstance(photo, str) else ""
    if not photo.startswith(("https://", "http://", "data:image/")):
        photo = ""

    followups_limited = row.get("acompanhamentos_truncados") is True
    return {
        "id": str(row.get("id") or ""),
        "nome": str(row.get("nome") or "Pet"),
        "especie": str(row.get("especie_nome") or "Espécie não informada"),
        "raca": str(row.get("raca_nome") or ("SRD" if not row.get("raca_id") else "Raça não informada")),
        "idade": _age_label(row.get("data_nasc"), current),
        "peso": weight_label(row.get("peso_atual"), missing=""),
        "foto": photo,
        "indicador_vacina": indicator,
        "proxima_vacina": ({
            "nome": str(upcoming_vaccines[0].get("vacina") or "Vacina"),
            "data": _date_label(upcoming_vaccines[0].get("data_prox_dose")),
        } if upcoming_vaccines else {"nome": "", "data": ""}),
        "ultima_consulta": ({
            "data": _date_label(consultation_date(finalized[0])),
        } if finalized else {"data": ""}),
        "proximo_evento": {
            "tipo": next_event.get("tipo", ""),
            "data": next_event.get("data", ""),
        },
        "acompanhamentos": followups,
        "acompanhamentos_truncados": followups_limited,
        "mensagem_acompanhamento": (
            (
                "Itens registrados para acompanhar."
                + (
                    " A lista exibida é limitada; consulte o prontuário para ver os demais registros."
                    if followups_limited else ""
                )
            )
            if followups else "Nenhum item de acompanhamento identificado nos registros consultados."
        ),
        "atividade_recente": recent[:6],
    }


class TutorDashboardMixin(rx.State, mixin=True):
    dashboard_scope: str = "todos"
    dashboard_pets: list[DashboardPet] = []
    dashboard_loading: bool = False
    dashboard_error: str = ""
    _dashboard_generation: int = 0
    _dashboard_running_generation: int = -1
    _dashboard_loaded_at: dict[str, float] = {}
    _dashboard_cache_day: str = ""
    _dashboard_cache_pet_ids: list[str] = []

    @rx.var
    def dashboard_context_pet_id(self) -> str:
        """Explicit owned-pet choice remains identifiable while details load."""
        candidate = str(self.selected_pet.get("id") or self.pet_target_id or "")
        return candidate if candidate and any(str(pet.get("id")) == candidate for pet in self.pets) else ""

    @rx.var
    def dashboard_visible_pets(self) -> list[DashboardPet]:
        if self.dashboard_scope == "todos":
            return self.dashboard_pets
        return [pet for pet in self.dashboard_pets if pet.get("id") == self.dashboard_scope]

    @rx.var
    def dashboard_is_all_pets(self) -> bool:
        return self.dashboard_scope == "todos"

    def _dashboard_current(self, generation: int, session: int, token: str) -> bool:
        return (
            generation == self._dashboard_generation
            and session == self._session_generation
            and token == self._auth_token
            and bool(token)
        )

    def _clear_dashboard_session(self):
        self._dashboard_generation += 1
        self._dashboard_running_generation = -1
        self._invalidate_dashboard_cache()
        self.dashboard_scope = "todos"
        self.dashboard_pets = []
        self.dashboard_loading = False
        self.dashboard_error = ""

    def _dashboard_pet_ids(self, scope: str) -> list[str] | None:
        owned_ids = [
            str(pet.get("id") or "")
            for pet in self.pets
            if str(pet.get("id") or "").isascii()
            and str(pet.get("id") or "").isdecimal()
            and int(str(pet.get("id") or "")) > 0
        ]
        if scope == "todos":
            return owned_ids
        return [scope] if scope in owned_ids else None

    def _invalidate_dashboard_cache(self):
        self._dashboard_loaded_at = {}
        self._dashboard_cache_day = ""
        self._dashboard_cache_pet_ids = []

    def _dashboard_cache_fresh(self, scope: str) -> bool:
        ids = self._dashboard_pet_ids(scope)
        available_ids = {pet["id"] for pet in self.dashboard_pets}
        now = time.monotonic()
        return (
            bool(ids) and not self.dashboard_error
            and self._dashboard_cache_pet_ids == self._dashboard_pet_ids("todos")
            and self._dashboard_cache_day == datetime.now(TZ).date().isoformat()
            and all(pet_id in available_ids
                    and 0 <= now - self._dashboard_loaded_at.get(pet_id, float("-inf")) < 15
                    for pet_id in ids)
        )

    async def _fetch_dashboard_pet(self, pet_id: str, token: str) -> DashboardPet:
        endpoint = "tutor/dashboard?" + urlencode({"pet_id": pet_id})
        row = await xano_request("GET", GROUP, endpoint, auth_token=token)
        if not isinstance(row, dict) or str(row.get("id") or "") != pet_id:
            raise XanoRequestError("O Xano retornou uma resposta inválida.")
        return project_pet(row)

    @rx.event(background=True)
    async def fetch_dashboard(self, generation: int):
        async with self:
            session, token = self._session_generation, self._auth_token
            if (not self._dashboard_current(generation, session, token)
                    or self.profile != "tutor" or not self.dashboard_loading
                    or self._dashboard_running_generation == generation):
                return
            self._dashboard_running_generation = generation
            scope = self.dashboard_scope
            pet_ids = self._dashboard_pet_ids(scope)
            if pet_ids is None:
                self.dashboard_error = "Pet não disponível."
                self.dashboard_loading = False
                return
        semaphore = asyncio.Semaphore(4)

        async def fetch(pet_id: str) -> DashboardPet:
            async with semaphore:
                return await self._fetch_dashboard_pet(pet_id, token)

        error = None
        projected = []
        try:
            if pet_ids:
                async with xano_request_batch():
                    tasks = [asyncio.create_task(fetch(pet_id)) for pet_id in pet_ids]
                    try:
                        for completed in asyncio.as_completed(tasks):
                            pet = await completed
                            projected.append(pet)
                            async with self:
                                if not self._dashboard_current(generation, session, token):
                                    return
                                if self._dashboard_pet_ids(scope) != pet_ids:
                                    raise XanoRequestError("A lista de pets mudou. Atualize o Dashboard.")
                                updated = {row["id"]: row for row in self.dashboard_pets}
                                updated[pet["id"]] = pet
                                owned_ids = self._dashboard_pet_ids("todos") or []
                                self.dashboard_pets = [updated[pet_id] for pet_id in owned_ids if pet_id in updated]
                    finally:
                        # An early failure must not leave requests using a closed pool.
                        for task in tasks:
                            if not task.done():
                                task.cancel()
                        await asyncio.gather(*tasks, return_exceptions=True)
        except XanoRequestError as caught:
            error = caught
        except (TypeError, ValueError, KeyError):
            error = XanoRequestError("O Xano retornou uma resposta inválida.")
        async with self:
            if not self._dashboard_current(generation, session, token):
                return
            self.dashboard_loading = False
            if error is not None:
                if error.status_code == 401:
                    self._expire_session()
                else:
                    self.dashboard_error = str(error)
                return
            # Membership may have changed while HTTP was running.
            if self._dashboard_pet_ids(scope) != pet_ids:
                self.dashboard_error = "A lista de pets mudou. Atualize o Dashboard."
                return
            by_id = {pet["id"]: pet for pet in projected}
            projected = [by_id[pet_id] for pet_id in pet_ids]
            now = time.monotonic()
            self._dashboard_loaded_at.update({pet_id: now for pet_id in pet_ids})
            self._dashboard_cache_day = datetime.now(TZ).date().isoformat()
            self._dashboard_cache_pet_ids = self._dashboard_pet_ids("todos") or []
            if scope == "todos":
                self.dashboard_pets = projected
            else:
                updated = {pet["id"]: pet for pet in self.dashboard_pets}
                updated.update({pet["id"]: pet for pet in projected})
                ordered_ids = self._dashboard_pet_ids("todos") or []
                self.dashboard_pets = [updated[pet_id] for pet_id in ordered_ids if pet_id in updated]

    @rx.event
    async def load_dashboard(self, force: bool = False):
        if not self.is_authenticated:
            yield rx.redirect("/login")
            return
        if self.profile != "tutor":
            yield rx.redirect("/")
            return
        if self.dashboard_loading:
            return
        if self._dashboard_pet_ids(self.dashboard_scope) is None:
            self.dashboard_scope = "todos"
        if not force and self._dashboard_cache_fresh(self.dashboard_scope):
            return
        self._dashboard_generation += 1
        generation = self._dashboard_generation
        self.dashboard_loading = True
        self.dashboard_error = ""
        yield
        yield type(self).fetch_dashboard(generation)

    @rx.event
    async def set_dashboard_scope(self, value: str):
        if value not in {"todos", *(str(pet.get("id") or "") for pet in self.pets)}:
            return
        if self.dashboard_loading and self.dashboard_scope == value:
            return
        self.dashboard_scope = value
        self._dashboard_generation += 1
        generation = self._dashboard_generation
        session, token = self._session_generation, self._auth_token
        if not self.is_authenticated or self.profile != "tutor" or not token:
            return
        if self._dashboard_cache_fresh(value):
            self.dashboard_loading = False
            return
        self.dashboard_loading = True
        self.dashboard_error = ""
        yield
        yield type(self).fetch_dashboard(generation)

    @rx.event
    def dashboard_open_clinical(self, pet_id: str, section: str = "inicio"):
        if (
            self.profile == "tutor"
            and self.is_authenticated
            and section in {"inicio", "vacinas"}
            and any(pet["id"] == pet_id for pet in self.dashboard_pets)
            and any(pet["id"] == pet_id for pet in self.pets)
        ):
            self._invalidate_dashboard_cache()
            return rx.redirect(f"/prontuario?secao={section}&pet_id={pet_id}")

    @rx.event
    async def dashboard_book_pet(self, pet_id: str):
        if (
            self.profile != "tutor"
            or not self.is_authenticated
            or self.booking_busy
            or self._booking_uncertain
            or not any(pet["id"] == pet_id for pet in self.dashboard_pets)
            or not any(pet["id"] == pet_id for pet in self.pets)
        ):
            return
        self._invalidate_dashboard_cache()
        self.booking_open = True
        self.booking_step = 1
        self.booking_month = datetime.now(TZ).date().isoformat()[:7]
        self.booking_message = ""
        self.booking_day = self.booking_time = ""
        self.booking_pet = pet_id
        self.booking_professional = ""
        self.booking_professionals = []
        self._booking_operation = ""
        yield
        await self.booking_choose_pet(pet_id)
