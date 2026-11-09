"""Shared, scrollable preview of the actual generated PDF."""
import reflex as rx

from vet_tech.components.date_input import perimeter_led
from vet_tech.features.auth.state import State


def consultation_pdf_dialog() -> rx.Component:
    return rx.box(
        rx.script(src="/consultation-pdf-preview.js?v=2"),
        rx.dialog.root(
            rx.dialog.content(
                perimeter_led(),
                rx.box(
                    rx.box(
                        rx.box(rx.icon("file-text", size=16), rx.text("PRONTUÁRIO VETTECH"), class_name="vet-date-eyebrow"),
                        rx.dialog.title("Tudo pronto para conferir", class_name="vet-date-title pdf-preview-heading"),
                        rx.dialog.description("Veja o documento completo antes de baixar e compartilhar.", class_name="vet-date-description"),
                        rx.image(src="/optimized/espreitando.webp", alt="", aria_hidden="true", class_name="pdf-preview-mascot"),
                        rx.box(rx.icon("shield-check", size=17), rx.text("Documento da consulta finalizada"), class_name="pdf-preview-caption"),
                        class_name="pdf-preview-welcome"),
                    rx.box(
                        rx.flex(rx.box(rx.text("Prévia do PDF", weight="bold", size="4"),
                                      rx.text(State.pdf_preview_title, class_name="pdf-preview-patient")),
                                rx.button(rx.icon("x", size=18), on_click=State.change_pdf_preview_open(False),
                                          variant="ghost", aria_label="Fechar prévia"),
                                justify="between", align="center", gap="12px", class_name="pdf-preview-toolbar"),
                        rx.box(
                            rx.cond(State.pdf_preview_loading,
                                rx.hstack(rx.spinner(size="2"), rx.text("Preparando o documento…"), role="status", class_name="pdf-preview-loading")),
                            rx.el.div(id="consultation-pdf-pages", class_name="pdf-preview-pages",
                                      custom_attrs={"data-preview-token": State.pdf_preview_token},
                                      hidden=~State.pdf_preview_ready, role="region", aria_label="Páginas do prontuário em PDF", tab_index=0),
                            rx.cond((State.pdf_export_message != "") & ~State.pdf_preview_ready,
                                rx.box(rx.icon("file-warning", size=28), rx.text(State.pdf_export_message, role="status"),
                                       rx.button("Tentar novamente", on_click=State.retry_pdf_preview, variant="outline"),
                                       class_name="pdf-preview-error")),
                            class_name="pdf-preview-document", aria_busy=State.pdf_preview_loading),
                        rx.cond(State.pdf_preview_ready & (State.pdf_export_message != ""),
                            rx.text(State.pdf_export_message, role="status", class_name="pdf-preview-feedback")),
                        rx.flex(rx.button("Voltar", on_click=State.change_pdf_preview_open(False), variant="outline"),
                                rx.button(rx.icon("download", size=18), "Baixar PDF", on_click=State.request_consultation_pdf,
                                          loading=State.pdf_export_busy,
                                          disabled=State.pdf_preview_loading | ~State.pdf_preview_ready | State.pdf_export_busy,
                                          aria_label="Baixar PDF da consulta"),
                                class_name="pdf-preview-actions"),
                        class_name="pdf-preview-main"),
                    class_name="pdf-preview-layout"),
                on_close_auto_focus=State.restore_pdf_focus.prevent_default,
                class_name="vet-date-dialog pdf-preview-dialog"),
            open=State.pdf_preview_open, on_open_change=State.change_pdf_preview_open),
        on_unmount=State.change_pdf_preview_open(False),
    )
