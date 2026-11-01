"""Datas civis e instantes têm contratos distintos, sem adivinhar dia/mês."""

from datetime import date, datetime, timezone
import re
from typing import Any
from zoneinfo import ZoneInfo

BUSINESS_TZ = ZoneInfo("America/Sao_Paulo")


def calendar_date(value: Any) -> date | None:
    """Preserva o dia de uma data ISO; não aplica deslocamento de fuso."""
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if not isinstance(value, str):
        return None
    try:
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            return date.fromisoformat(value)
        # Compatibilidade com respostas ISO que incluem hora em campo civil.
        if re.match(r"^\d{4}-\d{2}-\d{2}T", value):
            return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except ValueError:
        pass
    return None


def instant_datetime(value: Any) -> datetime | None:
    """Timestamp Xano em milissegundos ou ISO com offset, no fuso de negócio."""
    if isinstance(value, bool) or value in (None, ""):
        return None
    try:
        if isinstance(value, (int, float)) or (
            isinstance(value, str) and re.fullmatch(r"-?\d+(?:\.\d+)?", value)
        ):
            return datetime.fromtimestamp(float(value) / 1000, timezone.utc).astimezone(BUSINESS_TZ)
        parsed = value if isinstance(value, datetime) else datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if parsed.tzinfo is not None:
            return parsed.astimezone(BUSINESS_TZ)
    except (ValueError, TypeError, OverflowError, OSError):
        pass
    return None


def date_label(value: Any) -> str:
    parsed = calendar_date(value)
    return parsed.strftime("%d/%m/%Y") if parsed else ""


def instant_label(value: Any) -> str:
    parsed = instant_datetime(value)
    return parsed.strftime("%d/%m/%Y %H:%M") if parsed else date_label(value)
