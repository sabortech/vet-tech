"""Tutor adoption discovery and confirmation state."""
from datetime import date
from typing import Any

import reflex as rx

from vet_tech.shared.config import adoption_demo_enabled
from vet_tech.shared.dates import calendar_date, date_label
from vet_tech.shared.xano_client import PET_API_GROUP, XanoRequestError, xano_request

_SEX_LABELS = {
    "m": "Macho",
    "male": "Macho",
    "masc": "Macho",
    "masculino": "Macho",
    "macho": "Macho",
    "f": "Fêmea",
    "female": "Fêmea",
    "fem": "Fêmea",
    "femea": "Fêmea",
    "fêmea": "Fêmea",
}

_CONDITION_LABELS = {
    "ativa": "Ativa",
    "em_tratamento": "Em tratamento",
    "controlada": "Controlada",
}


def _text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def _positive_id(value: Any) -> str:
    if isinstance(value, bool):
        return ""
    candidate = _text(value)
    return candidate if candidate.isascii() and candidate.isdecimal() and int(candidate) > 0 else ""


def _photo_url(value: Any) -> str:
    candidate = value.get("url") if isinstance(value, dict) else value
    if not isinstance(candidate, str):
        return ""
    url = candidate.strip()
    local_demo_photo = url.startswith("/petsadocao/") and not any(
        part in {".", ".."} for part in url.split("/")
    )
    return url if local_demo_photo or url.startswith(("https://", "http://", "data:image/")) else ""


def _age_label(value: Any) -> str:
    birth_date = calendar_date(value)
    if birth_date is None or birth_date > date.today():
        return ""
    current = date.today()
    years = current.year - birth_date.year - (
        (current.month, current.day) < (birth_date.month, birth_date.day)
    )
    months = (current.month - birth_date.month) % 12
    if current.day < birth_date.day:
        months = (months - 1) % 12
    if years:
        return f"{years} {'ano' if years == 1 else 'anos'}"
    if months:
        return f"{months} {'mês' if months == 1 else 'meses'}"
    return "Menos de 1 mês"


def _record_list(value: Any, fields: tuple[str, ...], label: str) -> list[dict[str, str]]:
    if not isinstance(value, list):
        raise XanoRequestError(f"O Xano retornou um resumo de {label} incompatível.")
    records = []
    for row in value:
        if not isinstance(row, dict):
            raise XanoRequestError(f"O Xano retornou um resumo de {label} incompatível.")
        records.append({field: _text(row.get(field)) for field in fields})
    return records


def project_adoption_pet(value: Any) -> dict[str, str]:
    """Validate and whitelist the public-to-tutor adoption projection."""
    if not isinstance(value, dict) or not _positive_id(value.get("id")):
        raise XanoRequestError("O Xano retornou dados incompatíveis para um pet disponível.")

    birth_date = value.get("data_nasc")
    species = _text(value.get("especie_nome")) or "Espécie não informada"
    breed = _text(value.get("raca_nome")) or "SRD"
    sex_raw = _text(value.get("sexo"))
    sex = _SEX_LABELS.get(sex_raw.casefold(), sex_raw)
    vaccine_value = value.get("vacina")
    if vaccine_value is not None and not isinstance(vaccine_value, dict):
        raise XanoRequestError("O Xano retornou um resumo de vacinação incompatível.")
    vaccine = (
        {
            "nome": _text(vaccine_value.get("nome")),
            "data_aplicacao": date_label(vaccine_value.get("data_aplicacao")),
            "data_prox_dose": date_label(vaccine_value.get("data_prox_dose")),
        }
        if vaccine_value is not None
        else {}
    )
    medications = _record_list(
        value.get("medicamentos"),
        ("nome", "dose", "unidade", "frequencia", "tipo", "data_inicio", "data_fim"),
        "medicamentos",
    )
    medications = [
        {
            **medication,
            "data_inicio": date_label(medication["data_inicio"]),
            "data_fim": date_label(medication["data_fim"]),
        }
        for medication in medications
    ]
    conditions = _record_list(value.get("doencas"), ("nome", "estado"), "condições")
    exam_value = value.get("exame")
    if exam_value is not None and not isinstance(exam_value, dict):
        raise XanoRequestError("O Xano retornou um resumo de exame incompatível.")
    exam = (
        {
            "tipo": _text(exam_value.get("tipo")),
            "data": date_label(exam_value.get("data")),
            "estado": _text(exam_value.get("estado")),
        }
        if exam_value is not None
        else {}
    )

    vaccine_summary = "Não informado"
    if vaccine:
        vaccine_summary = vaccine["nome"] or "Vacina"
        vaccine_dates = []
        if vaccine["data_aplicacao"]:
            vaccine_dates.append(f"aplicada em {vaccine['data_aplicacao']}")
        if vaccine["data_prox_dose"]:
            vaccine_dates.append(f"próxima dose em {vaccine['data_prox_dose']}")
        if vaccine_dates:
            vaccine_summary += " — " + "; ".join(vaccine_dates)

    medication_summaries = []
    for medication in medications:
        details = [
            medication["dose"] + (f" {medication['unidade']}" if medication["unidade"] else "")
            if medication["dose"]
            else "",
            medication["frequencia"],
            medication["tipo"],
            (
                "período: "
                + (medication["data_inicio"] or "início não informado")
                + " a "
                + (medication["data_fim"] or "sem data final")
            ),
        ]
        details = [item for item in details if item]
        medication_summaries.append(
            medication["nome"] + (f" — {', '.join(details)}" if details else "")
        )

    condition_summaries = [
        f"{condition['nome'] or 'Condição clínica'} — "
        f"{_CONDITION_LABELS.get(condition['estado'], 'Acompanhamento')}"
        for condition in conditions
    ]
    exam_summary = "Não informado"
    if exam:
        exam_summary = exam["tipo"] or "Exame"
        if exam["data"]:
            exam_summary += f" — {exam['data']}"
        if exam["estado"]:
            exam_summary += f" — {_CONDITION_LABELS.get(exam['estado'], exam['estado'])}"

    birth_label = date_label(birth_date) or _text(birth_date)
    age = _age_label(birth_date)
    metadata = " · ".join(
        item
        for item in (
            species,
            breed,
            sex,
            age,
            f"{_text(value.get('peso_atual'))} Kg" if value.get("peso_atual") is not None else "",
        )
        if item
    )
    sections = [
        "Vacinação\n" + vaccine_summary,
        "Medicamentos\n" + ("\n".join(medication_summaries) if medication_summaries else "Não informado"),
        "Condições de saúde\n" + ("\n".join(condition_summaries) if condition_summaries else "Não informado"),
        "Exames\n" + exam_summary,
    ]
    return {
        "id": _positive_id(value["id"]),
        "nome": _text(value.get("nome")) or "Pet",
        "especie": species,
        "raca": breed,
        "sexo": sex,
        "data_nasc": birth_label,
        "idade": age,
        "peso_atual": _text(value.get("peso_atual")),
        "foto": _photo_url(value.get("foto")),
        "metadados": metadata,
        "vacina_resumo": vaccine_summary,
        "medicamentos_resumo": "\n".join(medication_summaries) or "Não informado",
        "doencas_resumo": "\n".join(condition_summaries) or "Não informado",
        "exame_resumo": exam_summary,
        "prontuario_resumo": "\n\n".join(sections),
    }


def _demo_adoption_pets() -> list[dict[str, str]]:
    profiles = (
        ("900001", "Hades", "Jiboia", "Não informada", "Macho", "2018-05-01", "hades.jpeg"),
        ("900002", "Lua", "Gato", "SRD", "Fêmea", "2022-10-04", "lua.jpeg"),
        ("900003", "Lulu", "Cachorro", "Lulu-da-pomerânia", "Fêmea", "2021-08-20", "lulu.jpeg"),
        ("900004", "Luna", "Cachorro", "Chow Chow", "Fêmea", "2020-03-16", "luna.jpeg"),
        ("900005", "Nina", "Hamster", "Hamster sírio", "Fêmea", "2025-07-12", "nina.jpeg"),
        ("900006", "Pituco", "Furão", "Furão doméstico", "Macho", "2022-11-02", "pituco.jpeg"),
    )
    return [
        project_adoption_pet(
            {
                "id": pet_id,
                "nome": name,
                "especie_nome": species,
                "raca_nome": breed,
                "sexo": sex,
                "data_nasc": birth_date,
                "foto": f"/petsadocao/{photo}",
                "vacina": None,
                "medicamentos": [],
                "doencas": [],
                "exame": None,
            }
        )
        for pet_id, name, species, breed, sex, birth_date, photo in profiles
    ]


class AdoptionMixin(rx.State, mixin=True):
    adoption_pets: list[dict[str, str]] = []
    adoption_preview: dict[str, str] = {}
    adoption_is_demo: bool = False
    adoption_confirmation_open: bool = False
    adoption_target_id: str = ""
    adoption_busy_id: str = ""
    adoption_message: str = ""
    adoption_error: bool = False
    is_loading_adoption: bool = False
    _adoption_generation: int = 0
    _demo_adopted_ids: list[str] = []

    @rx.var
    def adoption_target_name(self) -> str:
        pet = next(
            (item for item in self.adoption_pets if item["id"] == self.adoption_target_id),
            None,
        )
        return pet["nome"] if pet else "este pet"

    def _clear_adoption_session(self):
        self._adoption_generation += 1
        self.adoption_pets = []
        self.adoption_preview = {}
        self.adoption_is_demo = False
        self.adoption_confirmation_open = False
        self.adoption_target_id = ""
        self.adoption_busy_id = ""
        self.adoption_message = ""
        self.adoption_error = False
        self.is_loading_adoption = False
        self._demo_adopted_ids = []

    @rx.event
    def load_adoption(self):
        if not self.is_authenticated or not self._auth_token:
            return rx.redirect("/login")
        if self.profile != "tutor":
            return rx.redirect("/")
        if self.is_loading_adoption or self.adoption_busy_id:
            return
        if adoption_demo_enabled():
            self._adoption_generation += 1
            self.adoption_is_demo = True
            self.adoption_pets = [
                pet for pet in _demo_adoption_pets()
                if pet["id"] not in self._demo_adopted_ids
            ]
            self.adoption_message = ""
            self.adoption_error = False
            self.is_loading_adoption = False
            return
        self.adoption_is_demo = False

        self._adoption_generation += 1
        generation = self._adoption_generation
        session = self._session_generation
        self.is_loading_adoption = True
        self.adoption_message = ""
        self.adoption_error = False
        return self.__class__.fetch_adoption(generation, session)

    @rx.event(background=True)
    async def fetch_adoption(self, generation: int, session: int):
        async with self:
            if (
                session != self._session_generation
                or generation != self._adoption_generation
                or not self.is_authenticated
                or self.profile != "tutor"
            ):
                return
            token = self._auth_token
        error = None
        adoption_pets = None
        try:
            result = await xano_request(
                "GET", PET_API_GROUP, "adoption", auth_token=token
            )
            if not isinstance(result, list):
                raise XanoRequestError("O Xano retornou uma lista de adoção incompatível.")
            adoption_pets = [project_adoption_pet(item) for item in result]
        except XanoRequestError as caught:
            error = caught
        finally:
            async with self:
                if (
                    session == self._session_generation
                    and generation == self._adoption_generation
                    and token == self._auth_token
                ):
                    if error is not None:
                        if error.status_code == 401:
                            self._expire_session()
                            return
                        self.adoption_message = str(error)
                        self.adoption_error = True
                    elif adoption_pets is not None:
                        self.adoption_pets = adoption_pets
                    self.is_loading_adoption = False

    @rx.event
    def open_adoption_preview(self, pet_id: str):
        pet = next((item for item in self.adoption_pets if item["id"] == pet_id), None)
        if pet is None:
            self.adoption_message = "Este pet não está mais disponível nesta lista. Atualize para verificar."
            self.adoption_error = True
            return
        self.adoption_preview = pet

    @rx.event
    def close_adoption_preview(self, opened: bool):
        if not opened:
            self.adoption_preview = {}

    @rx.event
    def open_adoption_confirmation(self, pet_id: str):
        if self.adoption_busy_id or self.is_loading_adoption:
            return
        if not any(item["id"] == pet_id for item in self.adoption_pets):
            self.adoption_message = "Este pet não está mais disponível nesta lista. Atualize para verificar."
            self.adoption_error = True
            return
        self.adoption_target_id = pet_id
        self.adoption_message = ""
        self.adoption_error = False
        self.adoption_confirmation_open = True

    @rx.event
    def set_adoption_confirmation(self, opened: bool):
        if self.adoption_busy_id:
            return
        self.adoption_confirmation_open = opened and bool(self.adoption_target_id)
        if not opened:
            self.adoption_target_id = ""

    @rx.event
    def confirm_adoption(self):
        if self.adoption_busy_id or self.is_loading_adoption or not self.adoption_confirmation_open:
            return
        target_id = self.adoption_target_id
        numeric_id = _positive_id(target_id)
        if not any(item["id"] == target_id for item in self.adoption_pets) or not numeric_id:
            self.adoption_message = "Este pet não está mais disponível nesta lista. Atualize para verificar."
            self.adoption_error = True
            return
        if not self.is_authenticated or self.profile != "tutor" or not self._auth_token:
            return rx.redirect("/login")

        if self.adoption_is_demo:
            pet = next(
                (item for item in self.adoption_pets if item["id"] == target_id),
                None,
            )
            if pet is None:
                self.adoption_message = "Este perfil demonstrativo não está mais disponível nesta lista."
                self.adoption_error = True
                return
            self._demo_adopted_ids = [*self._demo_adopted_ids, target_id]
            self.adoption_pets = [
                item for item in self.adoption_pets if item["id"] != target_id
            ]
            self.adoption_preview = {}
            self.adoption_confirmation_open = False
            self.adoption_target_id = ""
            self.adoption_message = (
                f"Simulação: {pet['nome']} foi marcado como adotado nesta sessão. "
                "Nada foi salvo no Xano nem adicionado a Meus Pets/Mudar pet."
            )
            self.adoption_error = False
            return

        self.adoption_busy_id = target_id
        self.adoption_message = ""
        self.adoption_error = False
        return self.__class__.perform_adoption(target_id, self._session_generation)

    @rx.event(background=True)
    async def perform_adoption(self, target_id: str, session: int):
        async with self:
            if (
                session != self._session_generation
                or self.adoption_busy_id != target_id
                or not self.adoption_confirmation_open
                or not self.is_authenticated
                or self.profile != "tutor"
            ):
                return
            token = self._auth_token
            pet = next(
                (item for item in self.adoption_pets if item["id"] == target_id),
                None,
            )
            numeric_id = _positive_id(target_id)
            if pet is None or not numeric_id:
                self.adoption_busy_id = ""
                self.adoption_message = "Este pet não está mais disponível nesta lista. Atualize para verificar."
                self.adoption_error = True
                return
            pet = dict(pet)
        error = None
        adopted_pet = None
        try:
            result = await xano_request(
                "POST",
                PET_API_GROUP,
                "adoption",
                auth_token=token,
                json_payload={"pet_id": int(numeric_id)},
            )
            if (
                not isinstance(result, dict)
                or _positive_id(result.get("id")) != target_id
                or not _positive_id(result.get("especie_id"))
                or not _text(result.get("nome"))
            ):
                raise XanoRequestError("O Xano confirmou uma resposta incompatível para a adoção.")

            adopted_pet = {
                "id": target_id,
                "raca_id": _text(result.get("raca_id")),
                "nome": _text(result.get("nome")) or pet["nome"],
                "especie": _text(result.get("especie_nome")) or pet["especie"],
                "raca": _text(result.get("raca_nome")) or pet["raca"],
                "sexo": pet["sexo"],
                "data_nasc": date_label(result.get("data_nasc")) or pet["data_nasc"],
                "metadados": " · ".join(
                    item
                    for item in (
                        _text(result.get("especie_nome")) or pet["especie"],
                        _text(result.get("raca_nome")) or pet["raca"],
                        pet["sexo"],
                        date_label(result.get("data_nasc")) or pet["data_nasc"],
                    )
                    if item
                ),
                "foto": _photo_url(result.get("foto")) or pet["foto"],
                "peso_atual": _text(result.get("peso_atual")),
            }
        except XanoRequestError as caught:
            error = caught
        async with self:
            if session != self._session_generation or token != self._auth_token:
                return
            if error is not None:
                if error.status_code == 401:
                    self._expire_session()
                    return
                self.adoption_message = str(error)
                self.adoption_error = True
            elif adopted_pet is not None:
                self._adoption_generation += 1
                self.is_loading_adoption = False
                self.adoption_pets = [
                    item for item in self.adoption_pets if item["id"] != target_id
                ]
                if not any(item["id"] == target_id for item in self.pets):
                    self.pets = [*self.pets, adopted_pet]
                self.adoption_confirmation_open = False
                self.adoption_target_id = ""
                self.adoption_message = f"{adopted_pet['nome']} agora faz parte da sua família."
                self.adoption_error = False
            self.adoption_busy_id = ""
