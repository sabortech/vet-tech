import asyncio
from datetime import date, datetime
from typing import Any, TypedDict
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

import reflex as rx

from vet_tech.shared.xano_client import XanoRequestError, xano_request

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


class DashboardPet(TypedDict):
    id: str
    nome: str
    especie: str
    raca: str
    idade: str
    peso: str
    foto: str
    proxima_vacina: DashboardDatedItem
    ultima_consulta: DashboardDatedItem
    proximo_evento: DashboardEvent
    acompanhamentos: list[DashboardFollowup]
    acompanhamentos_truncados: bool
    mensagem_acompanhamento: str
    atividade_recente: list[DashboardActivity]


def _date_value(value: Any) -> date | None:
    if value in (None, ""):
        return None
    try:
        if isinstance(value, (int, float)) or str(value).isdecimal():
            return datetime.fromtimestamp(float(value) / 1000, TZ).date()
        return date.fromisoformat(str(value)[:10])
    except (ValueError, TypeError, OverflowError, OSError):
        return None


def _date_label(value: Any) -> str:
    parsed = _date_value(value)
    return parsed.strftime("%d/%m/%Y") if parsed else ""


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

    events: list[dict[str, str]] = []
    for item in consultations:
        if item.get("status") == "agendada":
            when = item.get("agendada_para")
            event_date = _date_value(when)
            if event_date and event_date >= current:
                events.append({
                    "tipo": "Consulta agendada",
                    "data": _date_label(when),
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
            "data": _date_label(item.get("data_aplicacao") or item.get("data")),
        }
        for item in recent_vaccines
    ]
    recent.extend(
        {
            "tipo": "Consulta",
            "nome": "Consulta finalizada",
            "data": _date_label(consultation_date(item)),
        }
        for item in finalized[:3]
    )
    recent.sort(key=lambda item: _date_value(item["data"]) or date.min, reverse=True)

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
        "peso": str(row["peso_atual"]) if row.get("peso_atual") is not None else "",
        "foto": photo,
        "proxima_vacina": ({
            "nome": str(upcoming_vaccines[0].get("vacina") or "Vacina"),
            "data": _date_label(upcoming_vaccines[0].get("data_prox_dose")),
        } if upcoming_vaccines else {}),
        "ultima_consulta": ({
            "data": _date_label(consultation_date(finalized[0])),
        } if finalized else {}),
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

    async def _fetch_dashboard_pet(self, pet_id: str, token: str) -> DashboardPet:
        endpoint = "tutor/dashboard?" + urlencode({"pet_id": pet_id})
        row = await xano_request("GET", GROUP, endpoint, auth_token=token)
        if not isinstance(row, dict) or str(row.get("id") or "") != pet_id:
            raise XanoRequestError("O Xano retornou uma resposta inválida.")
        return project_pet(row)

    async def _refresh_dashboard_scope(
        self,
        generation: int,
        session: int,
        token: str,
        scope: str,
    ):
        pet_ids = self._dashboard_pet_ids(scope)
        if pet_ids is None:
            if self._dashboard_current(generation, session, token):
                self.dashboard_error = "Pet não disponível."
                self.dashboard_loading = False
            return

        semaphore = asyncio.Semaphore(4)

        async def fetch(pet_id: str) -> DashboardPet:
            async with semaphore:
                return await self._fetch_dashboard_pet(pet_id, token)

        try:
            projected = await asyncio.gather(*(fetch(pet_id) for pet_id in pet_ids))
        except XanoRequestError as error:
            if self._dashboard_current(generation, session, token):
                if error.status_code == 401:
                    self._expire_session()
                else:
                    self.dashboard_error = str(error)
        except (TypeError, ValueError, KeyError):
            if self._dashboard_current(generation, session, token):
                self.dashboard_error = "O Xano retornou uma resposta inválida."
        else:
            if self._dashboard_current(generation, session, token):
                if scope == "todos":
                    self.dashboard_pets = projected
                else:
                    updated = {pet["id"]: pet for pet in self.dashboard_pets}
                    updated.update({pet["id"]: pet for pet in projected})
                    ordered_ids = self._dashboard_pet_ids("todos") or []
                    self.dashboard_pets = [
                        updated[pet_id] for pet_id in ordered_ids if pet_id in updated
                    ]
        finally:
            if self._dashboard_current(generation, session, token):
                self.dashboard_loading = False

    @rx.event
    async def load_dashboard(self):
        if not self.is_authenticated:
            yield rx.redirect("/login")
            return
        if self.profile != "tutor":
            yield rx.redirect("/")
            return
        if self._dashboard_pet_ids(self.dashboard_scope) is None:
            self.dashboard_scope = "todos"
        self._dashboard_generation += 1
        generation = self._dashboard_generation
        session, token = self._session_generation, self._auth_token
        self.dashboard_loading = True
        self.dashboard_error = ""
        yield
        await self._refresh_dashboard_scope(
            generation, session, token, self.dashboard_scope
        )

    @rx.event
    async def set_dashboard_scope(self, value: str):
        if value not in {"todos", *(str(pet.get("id") or "") for pet in self.pets)}:
            return
        self.dashboard_scope = value
        self._dashboard_generation += 1
        generation = self._dashboard_generation
        session, token = self._session_generation, self._auth_token
        if not self.is_authenticated or self.profile != "tutor" or not token:
            return
        self.dashboard_loading = True
        self.dashboard_error = ""
        yield
        await self._refresh_dashboard_scope(
            generation, session, token, value
        )

    @rx.event
    def dashboard_open_clinical(self, pet_id: str, section: str = "inicio"):
        if (
            self.profile == "tutor"
            and self.is_authenticated
            and section in {"inicio", "vacinas"}
            and any(pet["id"] == pet_id for pet in self.dashboard_pets)
            and any(pet["id"] == pet_id for pet in self.pets)
        ):
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
