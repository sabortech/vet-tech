"""Clinical actions composed into the shared tutor sidebar."""
import reflex as rx

from vet_tech.components.pets import pet_form
from vet_tech.features.auth.state import State
from vet_tech.features.navigation.state import NavigationState


def menu_button(label: str, icon: str, **props) -> rx.Component:
    return rx.button(
        rx.hstack(
            rx.icon(icon, size=20, class_name='sidebar-item__icon'),
            rx.text(label, class_name='sidebar-item__label'),
            class_name='sidebar-item__contents',
        ),
        aria_label=label, title=label,
        class_name='sidebar-item sidebar-action', **props,
    )


def new_pet_dialog() -> rx.Component:
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


def clinical_menu_actions() -> rx.Component:
    return rx.box(
        new_pet_dialog(),
        menu_button('Mudar pet', 'arrow-left-right', on_click=[State.show_pet_picker, NavigationState.close_drawer]),
        menu_button('Sair', 'log-out', on_click=State.logout),
        class_name='sidebar-action-list',
    )
