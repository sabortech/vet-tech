"""Date hints and shared calendar presentation; callers own state and ISO values."""

import reflex as rx
from vet_tech.features.clinical.state import MONTHS


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


def calendar_select(options, value, on_change, label, kind, menu_class="", disabled=False):
    return rx.select.root(
        rx.select.trigger(
            rx.hstack(rx.text(value), rx.icon("chevron-down", size=17, class_name="vet-date-select-chevron"),
                      align="center", justify="between", width="100%", spacing="2"),
            aria_label=label, class_name="vet-date-select-trigger vet-date-select-trigger--" + kind,
        ),
        rx.select.content(
            rx.select.group(rx.foreach(options, lambda option: rx.select.item(option, value=option, class_name="vet-date-select-option"))),
            position="popper", side="bottom", side_offset=8, align="start",
            custom_attrs={"avoidCollisions": False}, class_name="vet-date-select-menu " + menu_class,
        ), value=value, on_change=on_change, disabled=disabled,
    )



def perimeter_led(class_name="vet-date-led", radius="24.5"):
    return rx.el.svg(
        rx.el.svg.rect(x="1.5", y="1.5", rx=radius, ry=radius,
                       custom_attrs={"pathLength": 100}, class_name="vet-date-led-track"),
        class_name=class_name, aria_hidden="true", focusable="false",
    )



def calendar_panel(*, title, description, current_prefix, current_label, month_name, year, years,
                   days, previous_month, next_month, choose_month, choose_year, choose_day,
                   legend, back_label, class_name="vet-date-dialog", extra_action=None,
                   on_close_auto_focus=None, eyebrow="Sua agenda, com carinho", select_menu_class="",
                   disabled=False, heading="Escolher data", close_action=None):
    """Shared calendar presentation; callers retain their own state and events."""
    return rx.dialog.content(
        perimeter_led(),
        rx.box(
            rx.box(
                rx.box(rx.icon("sparkles", size=16), rx.text(eyebrow), class_name="vet-date-eyebrow"),
                rx.dialog.title(title, class_name="vet-date-title"),
                rx.dialog.description(description, class_name="vet-date-description"),
                rx.image(src="/optimized/espreitando.webp", alt="", class_name="vet-date-turtle", aria_hidden="true"),
                rx.box(rx.icon("calendar-check", size=18), rx.text(current_prefix, current_label), class_name="vet-date-current"),
                class_name="vet-date-welcome",
            ),
            rx.box(
                rx.hstack(rx.text(heading, weight="bold", size="4"), rx.spacer(),
                    rx.dialog.close(rx.el.button(rx.icon("x", size=19), class_name="vet-date-close", type="button", on_click=close_action, disabled=disabled, aria_label="Fechar calendário")),
                    align="center", margin_bottom="24px"),
                rx.hstack(
                    rx.el.button(rx.icon("chevron-left", size=20), on_click=previous_month, type="button", disabled=disabled, aria_label="Mês anterior", class_name="vet-date-month-arrow"),
                    calendar_select([name.capitalize() for name in MONTHS], month_name,
                                    choose_month, "Mês do calendário", "month", menu_class=select_menu_class, disabled=disabled),
                    calendar_select(years, year,
                                    choose_year, "Ano do calendário", "year", menu_class=select_menu_class, disabled=disabled),
                    rx.el.button(rx.icon("chevron-right", size=20), on_click=next_month, type="button", disabled=disabled, aria_label="Próximo mês", class_name="vet-date-month-arrow"),
                    align="center", justify="between", spacing="2", class_name="vet-date-month-controls",
                ),
                rx.box(*[rx.text(name) for name in ("Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom")], class_name="vet-date-weekdays"),
                rx.box(rx.foreach(days, lambda day: rx.el.button(
                    day["label"], on_click=choose_day(day["date"]), disabled=(day["date"] == "") | (day.get("disabled", "nao") == "sim") | disabled, type="button",
                    aria_label=day["date"], aria_pressed=day["selected"] == "sim",
                    class_name=rx.cond(day["selected"] == "sim", "vet-date-day is-selected",
                                       rx.cond(day["today"] == "sim", "vet-date-day is-today", "vet-date-day")) + rx.cond(
                        day["date"] == "", " is-empty", rx.cond((day.get("disabled", "nao") == "sim") | disabled, " is-disabled", "")),
                )), class_name="vet-date-days", role="group", aria_label="Dias do mês"),
                rx.hstack(rx.box(class_name="vet-date-today-dot"), rx.text("Hoje", size="2"),
                          rx.spacer(), rx.text(legend, size="1"),
                          class_name="vet-date-legend", align="center", wrap="wrap", spacing="2"),
                *([extra_action] if extra_action is not None else []),
                rx.dialog.close(rx.el.button(back_label, class_name="vet-date-back", type="button", on_click=close_action, disabled=disabled)),
                class_name="vet-date-month-panel",
            ), class_name="vet-date-layout",
        ),
        class_name=class_name, width="min(780px, calc(100vw - 32px))", max_width="780px", on_close_auto_focus=on_close_auto_focus,
    )
