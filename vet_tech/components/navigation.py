"""Clinical actions composed into the shared tutor sidebar."""
import reflex as rx

from vet_tech.features.auth.state import State
from vet_tech.features.navigation.state import NavigationState


def menu_button(label: str, icon: str, active=False, **props) -> rx.Component:
    return rx.button(
        rx.hstack(
            rx.icon(icon, size=20, class_name='sidebar-item__icon'),
            rx.text(label, class_name='sidebar-item__label'),
            class_name='sidebar-item__contents',
        ),
        aria_label=label, title=label,
        class_name=rx.cond(active, 'sidebar-item sidebar-action sidebar-item--active', 'sidebar-item sidebar-action'),
        custom_attrs={'aria-current': rx.cond(active, 'page', 'false')}, **props,
    )


def new_pet_dialog() -> rx.Component:
    from vet_tech.components.pets import pet_form
    return rx.dialog.root(
        rx.dialog.trigger(menu_button('Novo pet', 'circle-plus', disabled=State.is_busy)),
        rx.dialog.content(
            rx.dialog.title('Novo pet'),
            rx.dialog.description('Cadastre um animal sob sua responsabilidade.'),
            pet_form(),
            rx.dialog.close(rx.button('Cancelar', type='button', on_click=State.set_pet_modal(False),
                                      variant='outline', disabled=State.is_busy, margin_top='1rem')),
            max_height='85dvh', overflow_y='auto', width='min(95vw, 560px)',
        ),
        open=State.pet_modal_open, on_open_change=State.set_pet_modal,
    )


def tutor_menu_entries(in_settings=False) -> rx.Component:
    from vet_tech.features.settings.state import SettingsState
    return rx.box(
        menu_button('Mudar pet', 'arrow-left-right', active=State.is_pet_picker_page,
            on_click=[SettingsState.request_action('change_pet') if in_settings else State.show_pet_picker, NavigationState.close_drawer]),
        class_name='sidebar-pet-entries',
    )


def tutor_menu_footer(in_settings=False) -> rx.Component:
    from vet_tech.features.settings.state import SettingsState
    return menu_button('Sair', 'log-out',
        on_click=SettingsState.request_action('logout') if in_settings else State.logout)
