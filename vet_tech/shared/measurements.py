"""Display conventions for registered pet measurements; never converts values."""


def weight_label(value, missing: str = "Não informado") -> str:
    value = "" if value is None else str(value).strip()
    return f"{value} Kg" if value else missing
