import reflex as rx

from vet_tech.features.auth.state import State
from vet_tech.components.date_input import perimeter_led


def _clinical_summary(title: str, value: rx.Var, icon_name: str) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.icon(icon_name, size=16, class_name="adoption-clinical__icon", aria_hidden=True),
            rx.text(title, class_name="adoption-clinical__title"),
            align="center",
            spacing="2",
            class_name="adoption-clinical__heading",
        ),
        rx.text(value, class_name="adoption-clinical__value"),
        class_name="adoption-clinical",
    )


def adoption_card(pet: rx.Var) -> rx.Component:
    return rx.box(
        perimeter_led("vet-date-led adoption-card-led", "18"),
        rx.box(
            rx.cond(
                pet["foto"] != "",
                rx.image(src=pet["foto"], alt="Foto de " + pet["nome"], class_name="adoption-card__photo"),
                rx.box(rx.icon("paw-print", size=34), class_name="adoption-card__photo adoption-card__photo--empty"),
            ),
            rx.box(
                rx.heading(pet["nome"], as_="h2", size="5", class_name="adoption-card__name"),
                rx.text(pet["metadados"], class_name="adoption-card__metadata"),
                class_name="adoption-card__identity",
            ),
            class_name="adoption-card__header",
        ),
        rx.box(
            _clinical_summary("Vacinação", pet["vacina_resumo"], "syringe"),
            _clinical_summary("Medicamentos", pet["medicamentos_resumo"], "pill"),
            _clinical_summary("Condições de saúde", pet["doencas_resumo"], "heart-pulse"),
            _clinical_summary("Exame recente", pet["exame_resumo"], "microscope"),
            class_name="adoption-card__clinical",
        ),
        rx.box(
            rx.button(
                "Ver prontuário",
                on_click=State.open_adoption_preview(pet["id"]),
                variant="outline",
                class_name="adoption-card__secondary",
            ),
            rx.button(
                rx.icon("heart", size=17),
                "Adotar",
                on_click=State.open_adoption_confirmation(pet["id"]),
                disabled=(State.adoption_busy_id != "") | State.is_loading_adoption,
                class_name="adoption-card__primary",
            ),
            class_name="adoption-card__actions",
        ),
        class_name="adoption-card",
    )


def adoption_preview_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            perimeter_led("vet-date-led adoption-dialog-led", "22px"),
            rx.image(
                src="/optimized/mascote_logo.webp",
                alt="",
                aria_hidden=True,
                class_name="adoption-dialog__mascot",
            ),
            rx.dialog.title(
                "Resumo clínico de " + State.adoption_preview.get("nome", ""),
                class_name="adoption-dialog__title",
            ),
            rx.dialog.description(
                rx.cond(
                    State.adoption_is_demo,
                    "Perfil fictício de demonstração. Nenhum dado clínico real foi cadastrado.",
                    "Informações compartilhadas para apoiar uma decisão consciente de adoção.",
                ),
                class_name="adoption-dialog__description",
            ),
            rx.box(
                rx.cond(
                    State.adoption_preview.get("foto", "") != "",
                    rx.image(
                        src=State.adoption_preview.get("foto", ""),
                        alt="Foto de " + State.adoption_preview.get("nome", "pet"),
                        class_name="adoption-preview-dialog__photo",
                    ),
                    rx.box(
                        rx.icon("paw-print", size=42, aria_hidden=True),
                        class_name="adoption-preview-dialog__photo adoption-preview-dialog__photo--empty",
                    ),
                ),
                rx.box(
                    rx.box(
                        _clinical_summary("Vacinação", State.adoption_preview.get("vacina_resumo", ""), "syringe"),
                        _clinical_summary("Medicamentos", State.adoption_preview.get("medicamentos_resumo", ""), "pill"),
                        _clinical_summary(
                            "Condições de saúde",
                            State.adoption_preview.get("doencas_resumo", ""),
                            "heart-pulse",
                        ),
                        _clinical_summary("Exames", State.adoption_preview.get("exame_resumo", ""), "microscope"),
                        class_name="adoption-dialog__clinical",
                    ),
                    class_name="adoption-preview-dialog__records",
                ),
                class_name="adoption-preview-dialog__body",
            ),
            rx.box(
                rx.dialog.close(
                    rx.button("Fechar", variant="outline", class_name="adoption-dialog__cancel")
                ),
                class_name="adoption-preview-dialog__actions",
            ),
            class_name="adoption-dialog adoption-preview-dialog",
        ),
        open=State.adoption_preview.get("id", "") != "",
        on_open_change=State.close_adoption_preview,
    )


def adoption_confirmation_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            perimeter_led("vet-date-led adoption-dialog-led", "22px"),
            rx.image(
                src="/optimized/mascote_logo.webp",
                alt="",
                aria_hidden=True,
                class_name="adoption-dialog__mascot",
            ),
            rx.flex(
                rx.dialog.title("Confirmar adoção", class_name="adoption-dialog__title"),
                rx.dialog.close(
                    rx.button(
                        rx.icon("x", size=18),
                        on_click=State.set_adoption_confirmation(False),
                        aria_label="Fechar confirmação de adoção",
                        variant="ghost",
                        disabled=State.adoption_busy_id != "",
                    )
                ),
                align="center",
                justify="between",
            ),
            rx.dialog.description(
                rx.cond(
                    State.adoption_is_demo,
                    "Deseja simular a adoção de "
                    + State.adoption_target_name
                    + "? O card será removido somente desta sessão. Nada será salvo no Xano nem adicionado a Meus Pets/Mudar pet.",
                    "Deseja adotar "
                    + State.adoption_target_name
                    + "? O pet será vinculado ao seu perfil e deixará de aparecer nesta lista.",
                ),
                class_name="adoption-dialog__description",
            ),
            rx.cond(
                State.adoption_error & (State.adoption_message != ""),
                rx.text(
                    State.adoption_message,
                    role="alert",
                    class_name=rx.cond(
                        State.adoption_error,
                        "adoption-dialog__message adoption-dialog__message--error",
                        "adoption-dialog__message",
                    ),
                ),
            ),
            rx.box(
                rx.dialog.close(
                    rx.button(
                        "Cancelar",
                        on_click=State.set_adoption_confirmation(False),
                        variant="outline",
                        disabled=State.adoption_busy_id != "",
                        class_name="adoption-dialog__cancel",
                    )
                ),
                rx.button(
                    rx.cond(
                        State.adoption_busy_id != "",
                        rx.fragment(rx.spinner(size="1"), "Confirmando…"),
                        "Confirmar adoção",
                    ),
                    on_click=State.confirm_adoption,
                    disabled=State.adoption_busy_id != "",
                    class_name="adoption-dialog__confirm",
                    aria_busy=State.adoption_busy_id != "",
                ),
                class_name="adoption-dialog__actions",
            ),
            class_name="adoption-dialog",
            on_escape_key_down=State.set_adoption_confirmation(False),
        ),
        open=State.adoption_confirmation_open,
        on_open_change=State.set_adoption_confirmation,
    )


def adoption_content() -> rx.Component:
    return rx.box(
        rx.box(
            rx.box(
                rx.heading("Adoção", as_="h1", class_name="adoption-page__title"),
                rx.text(
                    "Conheça pets que estão procurando um novo lar.",
                    class_name="adoption-page__description",
                ),
                class_name="adoption-page__heading",
            ),
            rx.button(
                rx.icon("refresh-cw", size=17),
                "Atualizar lista",
                on_click=State.load_adoption,
                disabled=State.is_loading_adoption | (State.adoption_busy_id != ""),
                class_name="adoption-page__refresh",
            ),
            class_name="adoption-page__header",
        ),
        rx.cond(
            State.adoption_is_demo,
            rx.box(
                rx.icon("info", size=18),
                rx.text(
                    "Demonstração local: estes perfis são fictícios. A adoção é apenas uma simulação nesta sessão; nada é gravado no Xano ou nas listas reais de pets."
                ),
                role="status",
                class_name="adoption-demo-notice",
            ),
        ),
        rx.cond(
            (State.adoption_message != "") & ~State.adoption_confirmation_open,
            rx.text(
                State.adoption_message,
                role=rx.cond(State.adoption_error, "alert", "status"),
                class_name=rx.cond(
                    State.adoption_error,
                    "adoption-page__message adoption-page__message--error",
                    "adoption-page__message",
                ),
            ),
        ),
        rx.cond(
            State.is_loading_adoption,
            rx.box(rx.spinner(size="3"), rx.text("Carregando pets disponíveis…"), class_name="adoption-state"),
            rx.cond(
                State.adoption_pets.length() > 0,
                rx.box(
                    rx.foreach(State.adoption_pets, adoption_card),
                    class_name="adoption-grid",
                ),
                rx.box(
                    rx.icon("heart", size=32),
                    rx.heading("Nenhum pet disponível no momento", as_="h2", size="4"),
                    rx.text("Volte mais tarde ou atualize a lista para verificar novamente."),
                    class_name="adoption-state adoption-state--empty",
                ),
            ),
        ),
        adoption_preview_dialog(),
        adoption_confirmation_dialog(),
        class_name="adoption-page",
        as_="main",
        id="main-content",
    )
