"""Strict mapping of an authorized export envelope; never consumes the UI cache."""
from dataclasses import dataclass
import os
from typing import Any

from vet_tech.shared.dates import date_label, instant_label

MAX_CHARACTERS = 200_000
MAX_RECORDS = 5_000


def pdf_export_enabled() -> bool:
    """Server-side rollback switch; changing deployment config requires restart."""
    return os.getenv("VET_TECH_CONSULTATION_PDF_ENABLED", "true").casefold() not in {"0", "false", "off"}


class ConsultationPDFError(ValueError):
    """Safe domain failure. Never put raw payloads in the exception message."""


def positive_id(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        raise ConsultationPDFError("Consulta não disponível para exportação.")
    if not str(value).isascii() or not str(value).isdigit() or int(value) <= 0:
        raise ConsultationPDFError("Consulta não disponível para exportação.")
    return int(value)


def text(value: Any) -> str:
    if value is None or value == "":
        return "Não informado"
    if not isinstance(value, (str, int, float)) or isinstance(value, bool):
        raise ConsultationPDFError("Não foi possível preparar os dados da consulta.")
    # Keep ordinary line breaks, remove control characters unsuitable for PDF text.
    return "".join(c for c in str(value) if c in "\n\t" or ord(c) >= 32)


@dataclass(frozen=True)
class ConsultationDocument:
    consultation_id: int
    pet_id: int
    pet_name: str
    veterinarian_id: int
    fields: tuple[tuple[str, str], ...]
    sections: tuple[tuple[str, tuple[tuple[tuple[str, str], ...], ...]], ...]

    @property
    def filename(self) -> str:
        return f"vettech-consulta-{self.consultation_id}.pdf"


# All fields are projected explicitly; raw HTML, URLs and attachments are never assets.
SECTION_FIELDS = {
    "vacinas": ("Vacinas", (("vacina", "Vacina"), ("lote", "Lote"), ("data_aplicacao", "Aplicação"), ("data_prox_dose", "Próxima dose"))),
    "medicamentos": ("Medicamentos", (("nome", "Medicamento"), ("dose", "Dose"), ("unidade", "Unidade"), ("dosagem", "Dosagem registrada"), ("frequencia", "Frequência"), ("via", "Via"), ("tipo", "Tipo"), ("data_inicio", "Início"), ("data_fim", "Término"))),
    "diagnosticos": ("Diagnósticos registrados", (("nome", "Doença"), ("doenca_id", "ID da doença"), ("data_diagnostico", "Data do diagnóstico"), ("estado", "Estado registrado"), ("observacoes", "Observações"))),
    "exames": ("Exames", (("tipo", "Tipo"), ("status", "Estado"), ("data_solicitacao", "Solicitado em"), ("data_realizacao", "Realizado em"), ("resultado", "Resultado"))),
}


def _field(row: dict, key: str) -> str:
    value = row.get(key)
    if key.startswith("data_"):
        return (date_label(value) or "Não informado") if value not in (None, "") else "Não informado"
    return text(value)


def map_consultation_document(payload: Any, pet_id: Any, consultation_id: Any) -> ConsultationDocument:
    pet_id, consultation_id = positive_id(pet_id), positive_id(consultation_id)
    if not isinstance(payload, dict):
        raise ConsultationPDFError("Não foi possível preparar os dados da consulta.")
    positive_id(payload.get("auditoria_id"))
    row, pet = payload.get("consulta"), payload.get("pet")
    if not isinstance(row, dict) or not isinstance(pet, dict):
        raise ConsultationPDFError("Não foi possível preparar os dados da consulta.")
    if (positive_id(row.get("id")) != consultation_id or positive_id(row.get("pet_id")) != pet_id
            or positive_id(pet.get("id")) != pet_id or row.get("status") != "finalizada"):
        raise ConsultationPDFError("Consulta não disponível para exportação.")
    veterinarian_id = positive_id(row.get("veterinario_id"))
    fields = [("Data do atendimento", date_label(row.get("data_atendimento") or row.get("data")) or "Não informado")]
    for key, label in (("agendada_para", "Agendada para"), ("iniciada_em", "Início real"), ("finalizada_em", "Fim real")):
        if row.get(key) not in (None, ""):
            fields.append((label, instant_label(row[key]) or "Não informado"))
    fields.extend((label, text(row.get(key))) for key, label in (("motivo", "Motivo"), ("diagnostico", "Diagnóstico"), ("obs", "Observações")))
    if row.get("retorno_previsto") not in (None, ""):
        fields.append(("Retorno previsto", date_label(row["retorno_previsto"])))
    sections, count = [], 0
    for key, (label, mapping) in SECTION_FIELDS.items():
        records = payload.get(key)
        if not isinstance(records, list):
            raise ConsultationPDFError("Não foi possível preparar os dados da consulta.")
        count += len(records)
        if count > MAX_RECORDS:
            raise ConsultationPDFError("A consulta excede o limite de exportação.")
        included = []
        for item in records:
            if not isinstance(item, dict):
                raise ConsultationPDFError("Não foi possível preparar os dados da consulta.")
            # Defensive filtering also excludes legacy rows with null/zero association.
            if item.get("consulta_id") in (None, 0, "", "0"):
                continue
            if positive_id(item.get("consulta_id")) != consultation_id or positive_id(item.get("pet_id")) != pet_id:
                continue
            projection = []
            for field, title in mapping:
                if field == "dosagem" and item.get("dose") not in (None, ""):
                    continue
                if field == "data_realizacao" and not item.get(field) and item.get("data"):
                    item = {**item, field: item["data"]}
                if item.get(field) not in (None, ""):
                    projection.append((title, _field(item, field)))
            date_key = {"vacinas": "data_aplicacao", "medicamentos": "data_inicio", "diagnosticos": "data_diagnostico", "exames": "data_solicitacao"}[key]
            included.append(((str(item.get(date_key) or ""), positive_id(item.get("id"))), tuple(projection)))
        if included:
            sections.append((label, tuple(r for _, r in sorted(included, key=lambda pair: pair[0]))))
    document = ConsultationDocument(consultation_id, pet_id, text(pet.get("nome")), veterinarian_id, tuple(fields), tuple(sections))
    length = len(document.pet_name) + sum(len(v) for _, v in document.fields)
    length += sum(len(v) for _, records in document.sections for record in records for _, v in record)
    if length > MAX_CHARACTERS:
        raise ConsultationPDFError("A consulta excede o limite de exportação.")
    return document
