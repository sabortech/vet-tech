import reflex as rx
from vet_tech.components.date_input import date_hint, calendar_panel, perimeter_led

from vet_tech.components.sidebar import layout_com_menu
from vet_tech.features.auth.state import State


_PET_PHOTO_PREVIEW_SCRIPT = """
(() => {
  const cleanup = () => {
    if (window.__vetTechPetPhotoPreviewUrl) {
      URL.revokeObjectURL(window.__vetTechPetPhotoPreviewUrl);
      window.__vetTechPetPhotoPreviewUrl = null;
    }
    const root = document.getElementById("pet-photo");
    const preview = document.getElementById("pet-photo-preview");
    root?.removeAttribute("data-preview-visible");
    preview?.removeAttribute("src");
  };
  if (window.__vetTechPetPhotoPreviewHandler) {
    document.removeEventListener("change", window.__vetTechPetPhotoPreviewHandler, true);
  }
  if (window.__vetTechPetPhotoDropHandler) {
    document.removeEventListener("drop", window.__vetTechPetPhotoDropHandler, true);
  }
  if (window.__vetTechPetPhotoPreviewCleanup) {
    window.removeEventListener("vettech:pet-photo-clear", window.__vetTechPetPhotoPreviewCleanup);
  }
  window.__vetTechPetPhotoPreviewObserver?.disconnect();

  const showPreview = (file, root) => {
    cleanup();
    if (!file || file.size > 5 * 1024 * 1024 ||
        !["image/jpeg", "image/png", "image/webp"].includes(file.type)) return;
    const preview = document.getElementById("pet-photo-preview");
    if (!preview) return;
    window.__vetTechPetPhotoPreviewUrl = URL.createObjectURL(file);
    preview.src = window.__vetTechPetPhotoPreviewUrl;
    root.dataset.previewVisible = "true";
  };
  const handler = (event) => {
    const input = event.target;
    if (!(input instanceof HTMLInputElement) || input.type !== "file") return;
    const root = input.closest("#pet-photo");
    if (root) showPreview(input.files?.[0], root);
  };
  const dropHandler = (event) => {
    const root = event.target instanceof Element ? event.target.closest("#pet-photo") : null;
    if (root) showPreview(event.dataTransfer?.files?.[0], root);
  };
  const observer = new MutationObserver(() => {
    if (document.getElementById("pet-photo")) return;
    cleanup();
    document.removeEventListener("change", handler, true);
    document.removeEventListener("drop", dropHandler, true);
    window.removeEventListener("vettech:pet-photo-clear", cleanup);
    observer.disconnect();
    window.__vetTechPetPhotoPreviewHandler = null;
    window.__vetTechPetPhotoDropHandler = null;
    window.__vetTechPetPhotoPreviewCleanup = null;
    window.__vetTechPetPhotoPreviewObserver = null;
  });
  observer.observe(document.body, { childList: true, subtree: true });
  window.__vetTechPetPhotoPreviewHandler = handler;
  window.__vetTechPetPhotoDropHandler = dropHandler;
  window.__vetTechPetPhotoPreviewCleanup = cleanup;
  window.__vetTechPetPhotoPreviewObserver = observer;
  document.addEventListener("change", handler, true);
  document.addEventListener("drop", dropHandler, true);
  window.addEventListener("vettech:pet-photo-clear", cleanup);
})();
"""


def species_select() -> rx.Component:
    return rx.select.root(
        rx.select.trigger(
            placeholder="Selecione a espécie",
            class_name="pet-form__select-trigger",
            custom_attrs={"aria-label": "Selecione a espécie"},
        ),
        rx.select.content(
            rx.select.group(
                rx.foreach(
                    State.species_options,
                    lambda species: rx.select.item(
                        species["nome"],
                        value=species["id"],
                    ),
                )
            )
        ),
        value=State.selected_species_id,
        on_change=State.select_species,
        required=True,
        class_name="pet-form__select",
    )


def breed_select() -> rx.Component:
    return rx.select.root(
        rx.select.trigger(
            placeholder="Raça (opcional; deixe vazio para SRD)",
            class_name="pet-form__select-trigger",
            custom_attrs={
                "aria-label": "Raça (opcional; deixe vazio para SRD)",
            },
        ),
        rx.select.content(
            rx.select.group(
                rx.foreach(
                    State.breed_options,
                    lambda breed: rx.select.item(
                        breed["nome"],
                        value=breed["id"],
                    ),
                )
            )
        ),
        value=State.selected_breed_id,
        on_change=State.select_breed,
        disabled=State.selected_species_id == "",
        class_name="pet-form__select",
    )


def pet_field(icon: str, control: rx.Component) -> rx.Component:
    return rx.box(
        rx.icon(icon, size=18, class_name="pet-form__icon", aria_hidden=True),
        control,
        class_name="pet-form__icon-field",
    )


def birth_date_picker() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.el.button(
                rx.text(rx.cond(State.pet_birth_date != "", State.birth_date_label, "Data de nascimento")),
                rx.icon("calendar-days", size=17),
                id="pet-birth-date", type="button", aria_label="Data de nascimento",
                disabled=State.is_busy, class_name="pet-form__field pet-birth-date-trigger",
            ),
        ),
        calendar_panel(
            title="O começo de uma história", description="Escolha a data de nascimento do seu pet.",
            eyebrow="Perfil do pet", current_prefix="Nascimento: ", current_label=State.birth_date_label,
            month_name=State.birth_calendar_month_name, year=State.birth_calendar_year, years=State.birth_calendar_years,
            days=State.birth_calendar_days, previous_month=State.birth_calendar_shift(-1), next_month=State.birth_calendar_shift(1),
            choose_month=State.birth_calendar_choose_month, choose_year=State.birth_calendar_choose_year,
            choose_day=State.birth_calendar_choose_day, legend="Datas futuras não estão disponíveis",
            back_label="Voltar sem alterar", class_name="vet-date-dialog tutor-calendar-dialog pet-birth-calendar",
            disabled=State.is_busy, close_action=State.birth_calendar_set_open(False),
            extra_action=rx.el.button("Limpar data", type="button", on_click=State.birth_calendar_choose_day(""),
                                      class_name="vet-date-back", disabled=State.is_busy),
        ),
        open=State.birth_calendar_open, on_open_change=State.birth_calendar_set_open,
    )


def pet_form() -> rx.Component:
    return rx.box(
        perimeter_led("vet-date-led pets-card-led", "19"),
        rx.heading(
            "Cadastrar pet",
            as_="h2",
            size="4",
            class_name="pet-card__title",
        ),
        rx.box(
            pet_field("paw-print", rx.input(
                placeholder="Nome do pet",
                aria_label="Nome do pet",
                value=State.pet_name,
                on_change=State.set_pet_name,
                class_name="pet-form__field",
            )),
            pet_field("dog", species_select()),
            pet_field("dna", breed_select()),
            pet_field("venus-and-mars", rx.input(
                placeholder="Sexo (opcional)",
                aria_label="Sexo (opcional)",
                value=State.pet_sex,
                on_change=State.set_pet_sex,
                class_name="pet-form__field",
            )),
            rx.vstack(
                pet_field("cake", birth_date_picker()),
                date_hint(State.pet_birth_date), align="stretch", spacing="1",
            ),
            pet_field("weight", rx.input(
                placeholder="Peso atual em Kg (opcional)",
                aria_label="Peso atual em Kg (opcional)",
                type="number",
                min="0",
                step="1",
                value=State.pet_weight,
                on_change=State.set_pet_weight,
                class_name="pet-form__field",
            )),
            pet_field("palette", rx.input(
                placeholder="Cor da pelagem (opcional)",
                aria_label="Cor da pelagem (opcional)",
                value=State.pet_coat_color,
                on_change=State.set_pet_coat_color,
                class_name="pet-form__field",
            )),
            pet_field("microchip", rx.input(
                placeholder="Microchip (opcional)",
                aria_label="Microchip (opcional)",
                type="number",
                min="0",
                step="1",
                value=State.pet_microchip,
                on_change=State.set_pet_microchip,
                class_name="pet-form__field",
            )),
            class_name="pet-form__fields",
        ),
        rx.box(
            rx.upload(
                rx.vstack(
                    rx.icon("camera", size=32, aria_hidden=True),
                    rx.text("Selecionar foto (opcional)"),
                    align="center",
                    spacing="2",
                    class_name="pet-form__upload-prompt",
                ),
                rx.image(
                    id="pet-photo-preview",
                    alt="Pré-visualização da foto selecionada",
                    class_name="pet-form__preview",
                ),
                id="pet-photo",
                accept={
                    "image/jpeg": [".jpg", ".jpeg"],
                    "image/png": [".png"],
                    "image/webp": [".webp"],
                },
                max_files=1,
                # A foto vai em base64 para uma coluna de texto: limite menor evita payloads enormes.
                max_size=1024 * 1024,
                width="100%",
                class_name="pet-form__upload",
                custom_attrs={
                    "aria-label": "Selecionar foto (opcional)",
                },
            ),
            rx.foreach(
                rx.selected_files("pet-photo"),
                lambda file: rx.text(
                    file,
                    class_name="pet-form__filename",
                ),
            ),
            class_name="pet-form__upload-group",
        ),
        rx.button(
            "Cadastrar pet",
            on_click=State.create_pet(rx.upload_files(upload_id="pet-photo")),
            disabled=State.is_busy,
            class_name="pet-form__submit",
        ),
        rx.text(State.pet_message, role="status", class_name="pet-message"),
        rx.script(
            _PET_PHOTO_PREVIEW_SCRIPT,
            id="pet-photo-preview-handler",
        ),
        class_name="pet-card pet-form pet-card--led",
        position="relative",
        isolation="isolate",
    )


def pet_list() -> rx.Component:
    return rx.box(
        perimeter_led("vet-date-led pets-card-led", "19"),
        rx.box(
            rx.heading(
                "Meus pets",
                as_="h2",
                size="4",
                class_name="pet-card__title",
            ),
            rx.button(
                rx.icon("refresh-cw", size=16),
                "Atualizar lista",
                on_click=State.refresh_pets,
                class_name="pet-refresh",
            ),
            class_name="pet-card__header",
        ),
        rx.cond(
            State.is_loading_pets,
            rx.text("Carregando pets..."),
            rx.cond(
                State.has_pets,
                rx.box(
                    rx.foreach(
                        State.pets,
                        lambda pet: rx.box(
                            rx.box(
                                rx.cond(
                                    pet["foto"] != "",
                                    rx.image(src=pet["foto"], alt=pet["nome"]),
                                    rx.icon("paw-print", size=28),
                                ),
                                class_name="pet-entry__avatar",
                            ),
                            rx.box(
                                rx.text(
                                    pet["nome"],
                                    class_name="pet-entry__name",
                                ),
                                rx.text(
                                    pet["metadados"],
                                    class_name="pet-entry__meta",
                                ),
                                class_name="pet-entry__details",
                            ),
                            rx.button(
                                rx.cond(
                                    (State.pet_target_id == pet["id"]) & State.is_loading_pet,
                                    rx.fragment(rx.spinner(size="1"), "Carregando…"),
                                    rx.cond(
                                        State.selected_pet_id == pet["id"],
                                        rx.fragment(rx.icon("check", size=16), "Pet selecionado"),
                                        rx.fragment("Abrir ", pet["nome"]),
                                    ),
                                ),
                                on_click=State.open_pet(pet["id"]),
                                variant=rx.cond(State.selected_pet_id == pet["id"], "solid", "outline"),
                                class_name="pet-entry__action",
                                aria_pressed=(State.selected_pet_id == pet["id"]).to(str),
                                aria_label=rx.cond(
                                    State.selected_pet_id == pet["id"],
                                    "Pet selecionado: " + pet["nome"],
                                    "Abrir " + pet["nome"],
                                ),
                                aria_busy=(State.pet_target_id == pet["id"]) & State.is_loading_pet,
                            ),
                            class_name="pet-entry",
                        ),
                    ),
                    class_name="pet-list",
                ),
                rx.text("Você ainda não cadastrou pets."),
            ),
        ),
        class_name="pet-card pet-card--led",
        position="relative",
        isolation="isolate",
    )


def pet_picker_view() -> rx.Component:
    return rx.box(
        rx.box(
            rx.heading("Selecionar pet", as_="h1"),
            rx.link(rx.icon("arrow-left", size=17), "Voltar a Meus Pets", href="/",
                    class_name="pet-picker-back"),
            class_name="profile-heading",
        ),
        rx.box(
            rx.image(src="/optimized/espreitando.webp", alt="", aria_hidden="true",
                     class_name="pet-picker-turtle"),
            pet_list(),
            class_name="pet-picker-layout",
        ),
        rx.cond(State.pet_message != "", rx.text(State.pet_message, role="status", class_name="pet-picker-message")),
        class_name="profile-page pet-picker-page",
    )


def profile_view() -> rx.Component:
    return layout_com_menu(
        rx.cond(State.is_pet_picker_page, pet_picker_view(),
        rx.box(
            rx.box(
                rx.heading("Perfil do tutor", as_="h1"),
                rx.button(
                    "Sair",
                    on_click=State.logout,
                    class_name="profile-logout",
                ),
                class_name="profile-heading",
            ),
            rx.box(
                pet_form(),
                rx.box(
                    pet_list(),
                    rx.image(
                        src="/optimized/mascote-perfil.webp",
                        alt="",
                        class_name="pet-mascot",
                        custom_attrs={"aria-hidden": "true"},
                    ),
                    class_name="pet-list-column",
                ),
                class_name="profile-grid",
            ),
            class_name="profile-page",
        )),
        pagina_ativa=rx.cond(State.is_pet_picker_page, "mudar_pet", "meus_pets"),
    )


def booking_pet_choice_dialog() -> rx.Component:
    """Prepare a consultation through the existing pet selection or registration."""
    return rx.dialog.root(
        rx.dialog.trigger(rx.button(
            rx.icon("calendar-plus", size=18), "Gostaria de agendar uma consulta?",
            variant="outline", size="3", class_name="pet-booking-invitation",
        )),
        rx.dialog.content(
            perimeter_led("vet-date-led pet-booking-choice-led", "25"),
            rx.dialog.close(rx.button(rx.icon("x", size=20), aria_label="Fechar opções de agendamento",
                                      variant="ghost", class_name="pet-booking-choice-close")),
            rx.image(src="/optimized/espreitando.webp", alt="", aria_hidden="true",
                     class_name="pet-booking-choice-turtle"),
            rx.box(
                rx.box(
                    rx.box(
                        rx.badge(rx.icon("heart", size=14), "O próximo cuidado começa aqui", variant="soft"),
                        rx.dialog.title("Vamos agendar uma consulta?", class_name="pet-booking-choice-title"),
                        rx.dialog.description("Primeiro, escolha quem vai receber esse carinho.",
                                              class_name="pet-booking-choice-description"),
                        class_name="pet-booking-choice-copy",
                    ),
                    class_name="pet-booking-choice-header",
                ),
                rx.box(
                    rx.dialog.close(rx.el.button(
                        rx.box(rx.icon("paw-print", size=28), class_name="pet-booking-choice-icon"),
                        rx.text("Meu pet já está cadastrado", class_name="pet-booking-choice-card-title"),
                        rx.text("Encontre seu companheiro na lista e continue para cuidar dele.",
                                class_name="pet-booking-choice-card-description"),
                        rx.box(rx.text("Ir para Mudar pet"), rx.icon("arrow-right", size=18),
                               class_name="pet-booking-choice-action"),
                        on_click=State.show_pet_picker, class_name="pet-booking-choice-card", type="button",
                    )),
                    rx.dialog.close(rx.el.button(
                        rx.box(rx.icon("circle-plus", size=28), class_name="pet-booking-choice-icon"),
                        rx.text("Quero cadastrar um novo pet", class_name="pet-booking-choice-card-title"),
                        rx.text("Apresente seu pet para a gente e comece o histórico de cuidados.",
                                class_name="pet-booking-choice-card-description"),
                        rx.box(rx.text("Cadastrar em Meus Pets"), rx.icon("arrow-right", size=18),
                               class_name="pet-booking-choice-action"),
                        on_click=rx.redirect("/"), class_name="pet-booking-choice-card pet-booking-choice-card--new", type="button",
                    )),
                    class_name="pet-booking-choice-grid",
                ),
                rx.text("Depois de escolher ou cadastrar, você poderá agendar a consulta do seu pet.",
                        class_name="pet-booking-choice-note"),
            class_name="pet-booking-choice-body"),
            class_name="pet-booking-choice-dialog",
            width="min(860px, calc(100vw - 48px))", max_width="860px", padding="0",
        ),
    )


def pet_selection_empty_state() -> rx.Component:
    """Shared invitation for every clinical section without a pet context."""
    return rx.box(
        rx.box(
            rx.box(perimeter_led("vet-date-led pet-selection-led", "20"), class_name="pet-selection-scene-outline"),
            class_name="pet-selection-art-frame", aria_hidden="true",
        ),
        rx.vstack(
            rx.badge(
                rx.icon("heart", size=14), "Cada cuidado começa com uma escolha",
                variant="soft", class_name="pet-selection-eyebrow",
            ),
            rx.heading("Vamos cuidar de quem você ama?", size="7", text_align="center"),
            rx.text(
                "Escolha seu companheiro em Meus Pets e acompanhe de perto cada cuidado.",
                text_align="center", class_name="pet-selection-description",
            ),
            rx.button(
                rx.icon("paw-print", size=18),
                "Selecionar pet em Meus Pets",
                rx.icon("arrow-right", size=18),
                on_click=State.show_pet_picker,
                size="3",
            ),
            booking_pet_choice_dialog(),
            align="center", spacing="4",
            class_name="pet-selection-copy",
        ),
        class_name="pet-selection-empty",
    )


def pet_detail_row(label: str, key: str, icon: str) -> rx.Component:
    return rx.box(
        perimeter_led("vet-date-led pet-record-led", "16"),
        rx.box(rx.icon(icon, size=22), class_name="pet-record-fact-icon"),
        rx.text(label, class_name="pet-record-fact-label"),
        rx.text(rx.cond(State.selected_pet[key] != "", State.selected_pet[key] + " Kg" if key == "peso_atual" else State.selected_pet[key], "Não informado"),
                class_name="pet-record-fact-value"),
        class_name="pet-record-fact",
    )


def pet_details() -> rx.Component:
    """Identity and registered facts of the authorized selected pet."""
    return rx.box(
        rx.cond(
            State.pet_target_id != "",
            rx.cond(
                State.is_loading_pet,
                rx.hstack(rx.spinner(size="3"), rx.text("Carregando dados do pet…"), role="status", aria_live="polite"),
                rx.cond(
                    State.selected_pet_id != "",
                    rx.vstack(
                        rx.box(
                            perimeter_led("vet-date-led pet-record-led", "18"),
                            rx.box(
                              perimeter_led("vet-date-led pet-record-led pet-record-photo-led", "50%"),
                              rx.avatar(
                                src=State.selected_pet.get("foto", ""),
                                fallback="🐾",
                                alt=State.selected_pet["nome"],
                                class_name="pet-record-photo",
                              ),
                              class_name="pet-record-photo-frame",
                            ),
                            rx.box(
                                rx.heading(State.selected_pet["nome"], size="8"),
                                rx.text(State.selected_pet["especie"], " · ", State.selected_pet["raca"]),
                                class_name="pet-record-identity",
                            ),
                            rx.image(src="/optimized/mascote02-sem-sombra.webp", loading="lazy", decoding="async", alt="", aria_hidden="true", class_name="pet-record-mascot"),
                            class_name="pet-record-hero",
                        ),
                        rx.box(
                            pet_detail_row("Sexo", "sexo", "venus-and-mars"),
                            pet_detail_row("Nascimento", "data_nasc_legivel", "calendar-days"),
                            pet_detail_row("Peso atual", "peso_atual", "weight"),
                            pet_detail_row("Pelagem", "cor_pelo", "waves"),
                            pet_detail_row("Microchip", "num_microchip", "cpu"),
                            class_name="pet-record-facts",
                        ),
                        align="stretch", spacing="4", width="100%",
                    ),
                    rx.button("Tentar novamente", on_click=State.retry_pet),
                ),
            ),
            rx.text("Selecione um pet em Meus Pets para abrir seus dados."),
        ),
        rx.cond(State.pet_detail_message != "", rx.text(State.pet_detail_message, role="status", margin_top="1rem")),
        id="pet-details", class_name="pet-record-details", width="100%",
        aria_label="Dados do pet selecionado", aria_busy=State.is_loading_pet,
    )
