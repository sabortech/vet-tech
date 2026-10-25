import reflex as rx

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


def pet_form() -> rx.Component:
    return rx.box(
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
            pet_field("cake", rx.box(
                rx.input(
                    id="pet-birth-date",
                    type="date",
                    aria_label="Data de nascimento",
                    value=State.pet_birth_date,
                    on_change=State.set_pet_birth_date,
                    class_name="pet-form__field",
                ),
                rx.cond(
                    State.pet_birth_date == "",
                    rx.text(
                        "Data de nascimento",
                        class_name="pet-form__date-label",
                        custom_attrs={"aria-hidden": "true"},
                    ),
                    rx.fragment(),
                ),
                rx.icon(
                    "calendar-days",
                    size=16,
                    class_name="pet-form__calendar-icon",
                    custom_attrs={"aria-hidden": "true"},
                ),
                class_name="pet-form__date-control",
                custom_attrs={
                    "data-has-value": rx.cond(
                        State.pet_birth_date == "",
                        "false",
                        "true",
                    ),
                },
            )),
            pet_field("weight", rx.input(
                placeholder="Peso atual (opcional)",
                aria_label="Peso atual (opcional)",
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
                max_size=5 * 1024 * 1024,
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
        class_name="pet-card pet-form",
    )


def pet_list() -> rx.Component:
    return rx.box(
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
                            class_name="pet-entry",
                        ),
                    ),
                    class_name="pet-list",
                ),
                rx.text("Você ainda não cadastrou pets."),
            ),
        ),
        class_name="pet-card",
    )


def profile_view() -> rx.Component:
    return layout_com_menu(
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
                        src="/mascote-perfil.png",
                        alt="",
                        class_name="pet-mascot",
                        custom_attrs={"aria-hidden": "true"},
                    ),
                    class_name="pet-list-column",
                ),
                class_name="profile-grid",
            ),
            class_name="profile-page",
        ),
        pagina_ativa="meus_pets",
    )
