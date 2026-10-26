import reflex as rx

from vet_tech.pages.cadastro import cadastro
from vet_tech.pages.configuracoes import configuracoes
from vet_tech.features.settings.state import SettingsState
from vet_tech.pages.index import index, login_page
from vet_tech.shared.config import validate_backend_configuration
from vet_tech.pages.atendimento import atendimento
from vet_tech.pages.dashboard import dashboard
from vet_tech.pages.profile import clinical_page
from vet_tech.features.auth.state import State
from vet_tech.features.navigation.state import NavigationState

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
app.add_page(index, on_load=NavigationState.close_drawer)
app.add_page(login_page, route="/login", title="Login | Vet Tech", on_load=NavigationState.close_drawer)
app.add_page(cadastro, route="/cadastro", title="Cadastro | Vet Tech")

app.add_page(configuracoes, route="/configuracoes", title="Configurações | Vet Tech", on_load=[NavigationState.close_drawer, SettingsState.enter])
app.add_page(atendimento, route="/atendimento/[consulta_id]", title="Atendimento | Vet Tech", on_load=State.load_attendance)
app.add_page(dashboard, route="/dashboard", title="Dashboard | Vet Tech", on_load=[NavigationState.close_drawer, State.load_dashboard])

app.add_page(clinical_page, route="/prontuario", title="Prontuário | Vet Tech", on_load=[NavigationState.close_drawer, State.enter_clinical_page])
