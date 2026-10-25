import reflex as rx

from vet_tech.pages.cadastro import cadastro
from vet_tech.pages.configuracoes import configuracoes
from vet_tech.features.settings.state import SettingsState
from vet_tech.pages.index import index, login_page
from vet_tech.shared.config import validate_backend_configuration

app = rx.App(
    head_components=[rx.el.script(src="/preferences.js")],
	stylesheets=[
		"https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;600;700&display=swap",
		"/vet_tech.css",
	],
	style={
		'.rt-CheckboxRoot[data-state="checked"]': {
			"background_color": "#689554",
			"border_color": "#689554",
			"color": "white",
		},
	},
)
app.register_lifespan_task(validate_backend_configuration)
app.add_page(index)
app.add_page(login_page, route="/login", title="Login | Vet Tech")
app.add_page(cadastro, route="/cadastro", title="Cadastro | Vet Tech")

app.add_page(configuracoes, route="/configuracoes", title="Configurações | Vet Tech", on_load=SettingsState.enter)
