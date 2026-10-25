import reflex as rx

from vet_tech.features.navigation.state import CLINICAL_DESTINATIONS, NavigationState

_NAV_ITEMS = (
    ("dashboard", "Dashboard", "house"),
    ("prontuario", "Prontuário", "clipboard-list"),
    ("vacinas", "Vacinas", "syringe"),
    ("medicamentos", "Medicamentos", "pill"),
    ("doencas", "Doenças", "heart-pulse"),
    ("consultas", "Consultas", "calendar-days"),
    ("exames", "Exames", "microscope"),
    ("meus_pets", "Meus Pets", "paw-print"),
    ("configuracoes", "Configurações", "settings"),
)

_EXISTING_ROUTES = {"meus_pets": "/", "configuracoes": "/configuracoes", **CLINICAL_DESTINATIONS}


def _menu_item(item_id: str, label: str, icon_name: str, pagina_ativa: str) -> rx.Component:
    active = item_id == pagina_ativa
    class_name = rx.cond(active, "sidebar-item sidebar-item--active",
                        "sidebar-item" if item_id in _EXISTING_ROUTES else "sidebar-item sidebar-item--disabled")
    contents = rx.hstack(
        rx.icon(icon_name, class_name="sidebar-item__icon", size=20),
        rx.text(label, class_name="sidebar-item__label"),
        class_name="sidebar-item__contents",
        align="center",
        width="100%",
    )

    if item_id in _EXISTING_ROUTES:
        return rx.link(
            contents,
            href=_EXISTING_ROUTES[item_id],
            on_click=NavigationState.close_drawer,
            class_name=class_name,
            title=label,
            custom_attrs={
                "aria-label": label,
                "aria-current": rx.cond(active, "page", "false"),
            },
        )

    return rx.box(
        contents,
        class_name=class_name,
        title=f"{label} — em breve",
        custom_attrs={
            "aria-label": f"{label}, em breve",
            "aria-disabled": "true",
        },
    )


def _toggle_button(mobile: bool) -> rx.Component:
    is_open = NavigationState.drawer_open if mobile else NavigationState.sidebar_expanded
    icon = (
        rx.cond(
            NavigationState.drawer_open,
            rx.icon("x", size=20),
            rx.icon("menu", size=20),
        )
        if mobile
        else rx.cond(
            NavigationState.sidebar_expanded,
            rx.icon("panel-left-close", size=20),
            rx.icon("menu", size=20),
        )
    )
    label = (
        rx.cond(
            NavigationState.drawer_open,
            "Fechar menu",
            "Abrir menu",
        )
        if mobile
        else rx.cond(
            NavigationState.sidebar_expanded,
            "Recolher menu",
            "Abrir menu",
        )
    )
    return rx.button(
        icon,
        on_click=NavigationState.toggle_drawer if mobile else NavigationState.toggle_sidebar,
        class_name=(
            "sidebar-toggle sidebar-toggle--mobile"
            if mobile
            else "sidebar-toggle sidebar-toggle--desktop"
        ),
        title=label,
        custom_attrs={
            "aria-label": label,
            "aria-expanded": is_open.to(str),
            "aria-controls": "vet-tech-sidebar",
        },
    )


def _sidebar(pagina_ativa: str, actions: rx.Component | None = None) -> rx.Component:
    sidebar_class = rx.cond(
        NavigationState.drawer_open,
        "sidebar sidebar--mobile-open",
        rx.cond(
            NavigationState.sidebar_expanded,
            "sidebar",
            "sidebar sidebar--collapsed",
        ),
    )
    return rx.box(
        rx.hstack(
            rx.hstack(
                rx.icon("paw-print", size=24),
                rx.text("Vet Tech", class_name="sidebar-brand__label"),
                class_name="sidebar-brand",
                align="center",
                spacing="3",
            ),
            rx.spacer(),
            _toggle_button(mobile=False),
            class_name="sidebar-header",
            align="center",
            width="100%",
        ),
        rx.box(
            *[
                _menu_item(item_id, label, icon_name, pagina_ativa)
                for item_id, label, icon_name in _NAV_ITEMS
            ],
            class_name="sidebar-navigation",
            role="navigation",
            custom_attrs={"aria-label": "Navegação principal"},
        ),
        *([rx.box(actions, class_name='sidebar-actions')] if actions is not None else []),
        id="vet-tech-sidebar",
        class_name=sidebar_class,
    )


def layout_com_menu(conteudo: rx.Component, pagina_ativa: str, actions: rx.Component | None = None) -> rx.Component:
    return rx.box(
        _sidebar(pagina_ativa, actions),
        rx.button(
            on_click=NavigationState.close_drawer,
            id="vet-tech-drawer-escape-close",
            display="none",
            aria_hidden="true",
            tab_index=-1,
        ),
        rx.button(
            on_click=NavigationState.close_drawer,
            class_name="sidebar-backdrop",
            title="Fechar menu",
            custom_attrs={
                "aria-label": "Fechar menu",
                "aria-hidden": (~NavigationState.drawer_open).to(str),
            },
        ),
        rx.box(
            rx.box(
                _toggle_button(mobile=True),
                class_name="mobile-toolbar",
            ),
            conteudo,
            class_name="app-content",
        ),
        class_name="app-layout",
    )
