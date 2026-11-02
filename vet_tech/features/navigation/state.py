import reflex as rx

# Shared server allowlist; labels are mapped to the existing clinical State.
CLINICAL_SECTIONS = {
    'inicio': 'Início', 'vacinas': 'Vacinas', 'medicamentos': 'Medicamentos',
    'doencas': 'Doenças', 'consultas': 'Consultas',
}
CLINICAL_DESTINATIONS = {
    'prontuario': '/prontuario',
    **{key: f'/prontuario?secao={key}' for key in CLINICAL_SECTIONS if key != 'inicio'},
}
TUTOR_DESTINATIONS = frozenset({'/', '/dashboard', '/configuracoes', '/prontuario?secao=inicio', *CLINICAL_DESTINATIONS.values()})
VETERINARIAN_DESTINATIONS = frozenset({'/', '/?secao=horarios', '/?secao=consultas', '/configuracoes'})

_OPEN_DRAWER_KEYBOARD_LISTENER = """(() => {
  if (window.__vetTechDrawerEscapeHandler) {
    window.removeEventListener("keydown", window.__vetTechDrawerEscapeHandler);
  }
  window.__vetTechDrawerEscapeHandler = (event) => {
    if (event.key === "Escape") {
      document.getElementById("vet-tech-drawer-escape-close")?.click();
    }
  };
  window.addEventListener("keydown", window.__vetTechDrawerEscapeHandler);
})();"""

_CLOSE_DRAWER_KEYBOARD_LISTENER = """(() => {
  if (window.__vetTechDrawerEscapeHandler) {
    window.removeEventListener("keydown", window.__vetTechDrawerEscapeHandler);
    window.__vetTechDrawerEscapeHandler = null;
  }
})();"""


class NavigationState(rx.State):
    sidebar_preference: str = rx.LocalStorage(
        "true",
        name="vet_tech_sidebar_expanded",
        sync=True,
    )
    drawer_open: bool = False

    @rx.var
    def sidebar_expanded(self) -> bool:
        return self.sidebar_preference != "false"

    @rx.event
    def toggle_sidebar(self):
        self.sidebar_preference = "false" if self.sidebar_expanded else "true"

    @rx.event
    def toggle_drawer(self):
        self.drawer_open = not self.drawer_open
        return rx.call_script(
            _OPEN_DRAWER_KEYBOARD_LISTENER
            if self.drawer_open
            else _CLOSE_DRAWER_KEYBOARD_LISTENER
        )

    @rx.event
    def close_drawer(self):
        was_open = self.drawer_open
        self.drawer_open = False
        return rx.call_script(_CLOSE_DRAWER_KEYBOARD_LISTENER + (
            "document.querySelector('.sidebar-toggle--mobile')?.focus();" if was_open else ''
        ))

    @rx.event
    def set_sidebar_expanded(self, value: bool):
        self.sidebar_preference = "true" if value else "false"
