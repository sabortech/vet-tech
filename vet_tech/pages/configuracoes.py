"""Configurações do tutor com os componentes visuais compartilhados."""
import reflex as rx

from vet_tech.components.sidebar import layout_com_menu
from vet_tech.features.auth.state import State
from vet_tech.features.navigation.state import NavigationState
from vet_tech.features.settings.state import SettingsState as Settings


def field(label: str, field_id: str, value, handler=None, locked=False, hint=""):
    icon = {"settings-nome": "circle-user-round", "settings-email": "mail", "settings-cpf": "id-card", "settings-telefone": "phone", "settings-endereco": "building-2"}[field_id]
    return rx.box(
        rx.el.label(label, html_for=field_id),
        rx.box(
            rx.icon(icon, size=18, class_name="settings-field-icon", aria_hidden=True),
            rx.el.input(
                id=field_id, value=value,
                on_change=handler, read_only=locked,
                required=not locked,
                disabled=~Settings.loaded | Settings.loading | Settings.saving,
                custom_attrs={"autoComplete": {"settings-nome": "name", "settings-telefone": "tel", "settings-endereco": "street-address"}.get(field_id, "off")},
                type="tel" if field_id == "settings-telefone" else "text",
                class_name="settings-input",
            ),
            rx.cond(locked, rx.icon("lock-keyhole", size=18, class_name="settings-lock")),
            class_name="settings-control settings-control--with-icon",
        ),
        rx.cond(bool(hint), rx.text(hint, class_name="settings-hint")),
        class_name="settings-field" + (" settings-field--wide" if field_id == "settings-endereco" else ""),
    )


def feedback():
    return rx.text(
        Settings.message, role="status",
        class_name=rx.cond(Settings.message_ok, "settings-feedback settings-feedback--ok", "settings-feedback"),
    )


def account():
    return rx.box(
        rx.heading("Dados pessoais", as_="h2"),
        rx.text("Perfil: Tutor", class_name="settings-profile"),
        rx.cond(Settings.loading, rx.text("Carregando seus dados...", role="status")),
        rx.cond(
            ~Settings.loading & ~Settings.loaded,
            rx.box(feedback(), rx.button("Tentar novamente", on_click=Settings.enter, class_name="vt-secondary")),
            rx.form(
                rx.box(
                    field("Nome completo", "settings-nome", Settings.nome, Settings.edit_nome),
                    field("E-mail", "settings-email", Settings.email, locked=True, hint="E-mail utilizado para entrar no sistema. Não pode ser alterado aqui."),
                    field("CPF", "settings-cpf", Settings.cpf_mascarado, locked=True, hint="CPF parcialmente oculto. Não pode ser alterado aqui."),
                    field("Telefone", "settings-telefone", Settings.telefone, Settings.edit_telefone),
                    field("Endereço", "settings-endereco", Settings.endereco, Settings.edit_endereco),
                    class_name="settings-fields",
                ),
                feedback(),
                rx.box(
                    rx.button("Cancelar", type="button", on_click=Settings.cancel, disabled=~Settings.dirty | Settings.saving, class_name="vt-secondary"),
                    rx.button(rx.cond(Settings.saving, "Salvando...", "Salvar alterações"), type="submit", disabled=~Settings.dirty | Settings.saving | ~Settings.loaded, class_name="vt-primary"),
                    class_name="settings-actions",
                ),
                on_submit=Settings.save, reset_on_submit=False, id="settings-account-form",
            ),
        ),
        class_name="settings-card",
    )


def password_field(label, name, autocomplete):
    icon = {"current_password": "lock-keyhole", "new_password": "key-round", "password_confirmation": "shield-check"}[name]
    return rx.box(
        rx.el.label(label, html_for=name),
        rx.box(
            rx.icon(icon, size=18, class_name="settings-field-icon", aria_hidden=True),
            rx.input(name=name, id=name, type="password", required=True, custom_attrs={"autoComplete": autocomplete}, disabled=Settings.saving, class_name="settings-input"),
            rx.el.button(
                rx.icon("eye", size=18, class_name="password-eye-open", aria_hidden=True),
                rx.icon("eye-off", size=18, class_name="password-eye-closed", aria_hidden=True),
                type="button", class_name="settings-eye",
                custom_attrs={"data-password-target": name, "aria-label": f"Mostrar {label.lower()}", "aria-pressed": "false"},
            ),
            class_name="settings-control settings-control--with-icon",
        ), class_name="settings-field",
    )


def security():
    return rx.box(
        rx.heading("Alterar senha", as_="h2"),
        rx.text("Confirme sua senha atual para definir uma nova.", class_name="settings-hint"),
        rx.form(
            password_field("Senha atual", "current_password", "current-password"),
            password_field("Nova senha", "new_password", "new-password"),
            password_field("Confirmar nova senha", "password_confirmation", "new-password"),
            feedback(),
            rx.box(rx.button(rx.cond(Settings.saving, "Atualizando...", "Atualizar senha"), type="submit", disabled=Settings.saving, class_name="vt-primary"), class_name="settings-actions"),
            on_submit=Settings.change_password, reset_on_submit=False, id="settings-password-form",
        ),
        rx.text("Após atualizar, você entrará novamente no sistema.", class_name="settings-hint"),
        class_name="settings-card settings-card--security",
    )


def preferences():
    return rx.box(
        rx.box(
            rx.heading("Aparência", as_="h2"),
            rx.box(
                rx.box(rx.el.label("Modo escuro", html_for="theme-switch"), rx.text("Aplicar em todo o sistema, incluindo login, cadastro e menu lateral.", class_name="settings-hint")),
                rx.el.input(type="checkbox", id="theme-switch", role="switch", class_name="settings-switch", custom_attrs={"data-vt-preference": "theme", "aria-label": "Modo escuro"}),
                class_name="settings-preference",
            ),
            rx.text("Lembrar minha preferência neste navegador.", class_name="settings-hint"),
            rx.text("", id="theme-feedback", role="status", class_name="settings-feedback settings-feedback--ok"),
            class_name="settings-card",
        ),
        rx.box(
            rx.heading("Navegação", as_="h2"),
            rx.box(
                rx.box(rx.el.label("Manter o menu lateral expandido", html_for="sidebar-switch"), rx.text("No celular, o menu continua abrindo como uma gaveta.", class_name="settings-hint")),
                rx.el.input(type="checkbox", role="switch", id="sidebar-switch", class_name="settings-switch", checked=NavigationState.sidebar_expanded, on_change=NavigationState.set_sidebar_expanded, custom_attrs={"aria-label": "Manter o menu lateral expandido"}),
                class_name="settings-preference",
            ),
            rx.text("Lembrar minha preferência neste navegador.", class_name="settings-hint"),
            class_name="settings-card",
        ), class_name="settings-preferences",
    )


def discard_dialog():
    return rx.alert_dialog.root(
        rx.alert_dialog.content(
            rx.alert_dialog.title("Descartar alterações?"),
            rx.alert_dialog.description("Você tem alterações não salvas. Deseja continuar editando ou descartá-las?"),
            rx.box(
                rx.alert_dialog.cancel(rx.button("Continuar editando", on_click=Settings.keep_editing, class_name="vt-secondary")),
                rx.alert_dialog.action(rx.button("Descartar alterações", on_click=Settings.discard, class_name="vt-primary")),
                class_name="settings-actions",
            ), class_name="settings-discard",
        ), open=Settings.discard_open,
    )


def settings_view():
    return layout_com_menu(
        rx.box(
            rx.box(rx.heading("Configurações", as_="h1"), rx.button("Sair", on_click=Settings.request_action("logout"), class_name="profile-logout"), class_name="profile-heading"),
            rx.text("Gerencie seus dados, sua segurança e suas preferências.", class_name="settings-subtitle"),
            rx.box(
                rx.box(*[
                rx.button(label, on_click=Settings.request_action(value), role="tab", id=f"tab-{value}",
                    custom_attrs={"aria-selected": (Settings.tab == value).to(str), "aria-controls": "settings-panel"},
                    class_name=rx.cond(Settings.tab == value, "settings-tab settings-tab--active", "settings-tab"))
                for value, label in (("account", "Minha conta"), ("security", "Segurança"), ("preferences", "Preferências"))
            ], role="tablist", custom_attrs={"aria-label": "Seções de configurações"}, class_name="settings-tabs"),
                rx.image(src="/mascote-perfil.png", alt="", aria_hidden=True, class_name="settings-mascot"),
                class_name="settings-tab-row",
            ),
            rx.box(rx.match(Settings.tab, ("account", account()), ("security", security()), preferences()), id="settings-panel", role="tabpanel", custom_attrs={"aria-labelledby": "tab-" + Settings.tab}),
            discard_dialog(),
            rx.button(on_click=Settings.history_back, id="settings-history-guard", display="none"),
            rx.button(on_click=Settings.request_action("/"), id="settings-sidebar-guard", display="none"),
            class_name="settings-page", custom_attrs={"data-dirty": Settings.dirty.to(str), "data-baseline": Settings.baseline_json, "data-saving": Settings.saving.to(str)},
        ), pagina_ativa="configuracoes",
    )


def configuracoes():
    return rx.cond(State.is_authenticated, settings_view(), rx.box(rx.text("Redirecionando para o login...", role="status")))
