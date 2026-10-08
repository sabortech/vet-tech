import reflex as rx

from vet_tech.pages.cadastro import cadastro
from vet_tech.pages.index import index, login_page

app = rx.App(
	stylesheets=[
		"https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;600;700&display=swap"
	],
	style={
		".rt-TextFieldInput::placeholder": {
			"color": "#8A8F98",
			"opacity": "1",
		},
		'.rt-CheckboxRoot[data-state="checked"]': {
			"background_color": "#689554",
			"border_color": "#689554",
			"color": "white",
		},
	},
)
app.add_page(index)
app.add_page(login_page, route="/login", title="Login | Vet Tech")
app.add_page(cadastro, route="/cadastro", title="Cadastro | Vet Tech")
