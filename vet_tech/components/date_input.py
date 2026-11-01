"""Confirmação brasileira da data, preservando o valor ISO do input nativo."""

import reflex as rx


def date_hint(value) -> rx.Component:
    parts = value.split("-")
    return rx.text(
        rx.cond(
            (value != "") & (parts.length() == 3),
            "Data selecionada: " + parts[2] + "/" + parts[1] + "/" + parts[0],
            "Selecione a data no calendário.",
        ),
        size="1", color="var(--vt-muted)", aria_live="polite",
    )
