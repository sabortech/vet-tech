import os
from typing import Any, Optional
from urllib.parse import urlencode

import httpx
import reflex as rx

AUTH_API_GROUP = "H62nB-j2"
PET_API_GROUP = "vettech-pets"


class XanoRequestError(Exception):
    pass


async def xano_request(
    method: str,
    api_group: str,
    endpoint: str,
    auth_token: str = "",
    json_payload: Optional[dict[str, Any]] = None,
    form_data: Optional[dict[str, str]] = None,
    files: Optional[dict[str, tuple[str, bytes, str]]] = None,
) -> Any:
    base_url = os.getenv(
        "XANO_API_BASE_URL",
        "https://x8ki-letl-twmt.n7.xano.io",
    ).rstrip("/")
    if not base_url:
        raise XanoRequestError("Configure XANO_API_BASE_URL para conectar ao Xano.")
                
    headers = {}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"

    url = f"{base_url}/api:{api_group}/{endpoint.lstrip('/')}"
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            if files:
                response = await client.request(
                    method,
                    url,
                    headers=headers,
                    data=form_data,
                    files=files,
                )
            else:
                response = await client.request(
                    method,
                    url,
                    headers=headers,
                    json=json_payload,
                )
    except httpx.TimeoutException as error:
        raise XanoRequestError("O Xano demorou para responder. Tente novamente.") from error
    except httpx.RequestError as error:
        raise XanoRequestError("Não foi possível conectar ao Xano.") from error

    if not response.is_success:
        message = "Não foi possível concluir a solicitação."
        try:
            body = response.json()
            if isinstance(body, dict):
                message = body.get("message") or body.get("error") or message
        except ValueError:
            pass
        raise XanoRequestError(str(message))

    if not response.content:
        return None
    return response.json()


class State(rx.State):
    login_message: str = ""
    is_authenticated: bool = False
    is_busy: bool = False
    pet_message: str = ""
    is_loading_pets: bool = False
    pet_name: str = ""
    selected_species_id: str = ""
    selected_breed_id: str = ""
    pet_sex: str = ""
    pet_birth_date: str = ""
    pet_weight: str = ""
    pet_coat_color: str = ""
    pet_microchip: str = ""
    species_options: list[dict[str, str]] = []
    breed_options: list[dict[str, str]] = []
    pets: list[dict[str, str]] = []
    _auth_token: str = ""

    @rx.var
    def has_pets(self) -> bool:
        return bool(self.pets)

    @rx.event
    def set_pet_name(self, value: str):
        self.pet_name = value

    @rx.event
    def set_pet_sex(self, value: str):
        self.pet_sex = value

    @rx.event
    def set_pet_birth_date(self, value: str):
        self.pet_birth_date = value

    @rx.event
    def set_pet_weight(self, value: str):
        self.pet_weight = value

    @rx.event
    def set_pet_coat_color(self, value: str):
        self.pet_coat_color = value

    @rx.event
    def set_pet_microchip(self, value: str):
        self.pet_microchip = value

    @rx.event
    async def login(self, form_data: dict[str, Any]):
        email = form_data.get("email", "").strip()
        password = form_data.get("password", "")
        if not email or not password:
            self.login_message = "Informe e-mail e senha."
            return

        self.is_busy = True
        self.login_message = ""
        try:
            result = await xano_request(
                "POST",
                AUTH_API_GROUP,
                "tutor/login",
                json_payload={
                    "email": email,
                    "password": password,
                },
            )
            token = result.get("authToken") if isinstance(result, dict) else None
            if not token:
                raise XanoRequestError("O Xano não retornou uma sessão válida.")

            self._auth_token = str(token)
            self.is_authenticated = True
            await self._load_species()
            await self._load_pets()
        except XanoRequestError as error:
            self._auth_token = ""
            self.is_authenticated = False
            self.login_message = str(error)
        finally:
            self.is_busy = False

    @rx.event
    async def logout(self):
        self._auth_token = ""
        self.is_authenticated = False
        self.login_message = ""
        self.pet_message = ""
        self.species_options = []
        self.breed_options = []
        self.pets = []

    async def _load_species(self):
        result = await xano_request(
            "GET",
            PET_API_GROUP,
            "catalog/especies",
            auth_token=self._auth_token,
        )
        self.species_options = [
            {"id": str(item["id"]), "nome": str(item.get("nome") or "")}
            for item in result or []
        ]

    async def _load_breeds(self, species_id: str) -> list[dict[str, str]]:
        query = urlencode({"especie_id": species_id})
        result = await xano_request(
            "GET",
            PET_API_GROUP,
            f"catalog/racas?{query}",
            auth_token=self._auth_token,
        )
        return [
            {"id": str(item["id"]), "nome": str(item.get("nome") or "")}
            for item in result or []
        ]

    @rx.event
    async def select_species(self, species_id: str):
        self.selected_species_id = species_id
        self.selected_breed_id = ""
        self.breed_options = []
        self.pet_message = ""
        if not species_id:
            return
        try:
            self.breed_options = await self._load_breeds(species_id)
        except XanoRequestError as error:
            self.pet_message = str(error)

    @rx.event
    def select_breed(self, breed_id: str):
        self.selected_breed_id = breed_id

    async def _load_pets(self):
        self.is_loading_pets = True
        try:
            result = await xano_request(
                "GET",
                PET_API_GROUP,
                "pets",
                auth_token=self._auth_token,
            )
            species_names = {item["id"]: item["nome"] for item in self.species_options}
            species_ids = sorted(
                {
                    str(item.get("especie_id"))
                    for item in result or []
                    if item.get("especie_id") is not None
                }
            )
            breed_names: dict[str, str] = {}
            for species_id in species_ids:
                for breed in await self._load_breeds(species_id):
                    breed_names[breed["id"]] = breed["nome"]

            self.pets = [
                {
                    "id": str(item.get("id") or ""),
                    "nome": str(item.get("nome") or "Pet"),
                    "especie": species_names.get(
                        str(item.get("especie_id")),
                        "Espécie",
                    ),
                    "raca": breed_names.get(
                        str(item.get("raca_id")),
                        "SRD" if not item.get("raca_id") else "Raça",
                    ),
                    "sexo": str(item.get("sexo") or ""),
                    "data_nasc": str(item.get("data_nasc") or ""),
                    "peso_atual": str(item.get("peso_atual") or ""),
                }
                for item in result or []
            ]
        except XanoRequestError as error:
            self.pet_message = str(error)
        finally:
            self.is_loading_pets = False

    @rx.event
    async def refresh_pets(self):
        if self._auth_token:
            self.pet_message = ""
            await self._load_pets()

    @rx.event
    async def create_pet(self, files: list[rx.UploadFile]):
        if not self._auth_token:
            self.pet_message = "Entre novamente para cadastrar pets."
            return
        if not self.pet_name.strip() or not self.selected_species_id:
            self.pet_message = "Informe o nome e a espécie do pet."
            return

        form_data = {
            "nome": self.pet_name.strip(),
            "especie_id": self.selected_species_id,
        }
        if self.selected_breed_id:
            form_data["raca_id"] = self.selected_breed_id
        if self.pet_sex.strip():
            form_data["sexo"] = self.pet_sex.strip()
        if self.pet_birth_date:
            form_data["data_nasc"] = self.pet_birth_date
        if self.pet_weight:
            try:
                form_data["peso_atual"] = str(int(self.pet_weight))
            except ValueError:
                self.pet_message = "O peso deve ser um número inteiro."
                return
        if self.pet_coat_color.strip():
            form_data["cor_pelo"] = self.pet_coat_color.strip()
        if self.pet_microchip:
            if not self.pet_microchip.isdigit():
                self.pet_message = "O microchip deve conter somente números."
                return
            form_data["num_microchip"] = self.pet_microchip

        upload = files[0] if files else None
        upload_files = None
        if upload:
            content = await upload.read()
            upload_files = {
                "foto": (
                    upload.name,
                    content,
                    upload.content_type or "application/octet-stream",
                )
            }

        self.is_busy = True
        self.pet_message = ""
        try:
            await xano_request(
                "POST",
                PET_API_GROUP,
                "pets",
                auth_token=self._auth_token,
                form_data=form_data if upload_files else None,
                files=upload_files,
                json_payload=form_data if not upload_files else None,
            )
            self.pet_name = ""
            self.selected_breed_id = ""
            self.pet_sex = ""
            self.pet_birth_date = ""
            self.pet_weight = ""
            self.pet_coat_color = ""
            self.pet_microchip = ""
            self.pet_message = "Pet cadastrado com sucesso."
            await self._load_pets()
            return rx.clear_selected_files("pet-photo")
        except XanoRequestError as error:
            self.pet_message = str(error)
        finally:
            self.is_busy = False


def login_view() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.heading("Perfil do tutor", size="6"),
            rx.text("Entre com as credenciais da sua conta de tutor."),
            rx.form(
                rx.vstack(
                    rx.input(
                        placeholder="E-mail",
                        type="email",
                        name="email",
                        required=True,
                        width="100%",
                    ),
                    rx.input(
                        placeholder="Senha",
                        type="password",
                        name="password",
                        required=True,
                        width="100%",
                    ),
                    rx.button(
                        "Entrar",
                        type="submit",
                        disabled=State.is_busy,
                        width="100%",
                    ),
                    align="stretch",
                    spacing="3",
                    width="100%",
                ),
                on_submit=State.login,
                width="100%",
            ),
            rx.text(State.login_message, role="status"),
            spacing="3",
            align="stretch",
            width="100%",
            max_width="32rem",
        ),
        padding_top="4rem",
    )


def species_select() -> rx.Component:
    return rx.select.root(
        rx.select.trigger(placeholder="Selecione a espécie"),
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
    )


def breed_select() -> rx.Component:
    return rx.select.root(
        rx.select.trigger(placeholder="Raça (opcional; deixe vazio para SRD)"),
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
    )


def pet_form() -> rx.Component:
    return rx.vstack(
        rx.heading("Cadastrar pet", size="4"),
        rx.input(
            placeholder="Nome do pet",
            value=State.pet_name,
            on_change=State.set_pet_name,
            width="100%",
        ),
        species_select(),
        breed_select(),
        rx.input(
            placeholder="Sexo (opcional)",
            value=State.pet_sex,
            on_change=State.set_pet_sex,
            width="100%",
        ),
        rx.input(
            type="date",
            value=State.pet_birth_date,
            on_change=State.set_pet_birth_date,
            width="100%",
        ),
        rx.input(
            placeholder="Peso atual (opcional)",
            type="number",
            min="0",
            step="1",
            value=State.pet_weight,
            on_change=State.set_pet_weight,
            width="100%",
        ),
        rx.input(
            placeholder="Cor da pelagem (opcional)",
            value=State.pet_coat_color,
            on_change=State.set_pet_coat_color,
            width="100%",
        ),
        rx.input(
            placeholder="Microchip (opcional)",
            type="number",
            min="0",
            step="1",
            value=State.pet_microchip,
            on_change=State.set_pet_microchip,
            width="100%",
        ),
        rx.upload(
            rx.text("Selecionar foto (opcional)"),
            id="pet-photo",
            accept={"image/jpeg": [".jpg", ".jpeg"], "image/png": [".png"], "image/webp": [".webp"]},
            max_files=1,
            max_size=5 * 1024 * 1024,
            width="100%",
        ),
        rx.foreach(rx.selected_files("pet-photo"), rx.text),
        rx.button(
            "Cadastrar pet",
            on_click=State.create_pet(rx.upload_files(upload_id="pet-photo")),
            disabled=State.is_busy,
        ),
        rx.text(State.pet_message, role="status"),
        align="stretch",
        spacing="3",
        width="100%",
    )


def pet_list() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.heading("Meus pets", size="4"),
            rx.spacer(),
            rx.button("Atualizar lista", on_click=State.refresh_pets),
            width="100%",
            align="center",
        ),
        rx.cond(
            State.is_loading_pets,
            rx.text("Carregando pets..."),
            rx.cond(
                State.has_pets,
                rx.vstack(
                    rx.foreach(
                        State.pets,
                        lambda pet: rx.box(
                            rx.text(pet["nome"], weight="bold"),
                            rx.text(pet["especie"], " · ", pet["raca"]),
                            rx.text(pet["sexo"], " · ", pet["data_nasc"]),
                            width="100%",
                            padding_y="0.75rem",
                            border_bottom="1px solid #d9dedb",
                        ),
                    ),
                    width="100%",
                    align="stretch",
                    spacing="0",
                ),
                rx.text("Você ainda não cadastrou pets."),
            ),
        ),
        width="100%",
        align="stretch",
        spacing="3",
    )


def profile_view() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.hstack(
                rx.heading("Perfil do tutor", size="6"),
                rx.spacer(),
                rx.button("Sair", on_click=State.logout),
                width="100%",
                align="center",
            ),
            pet_form(),
            rx.divider(),
            pet_list(),
            align="stretch",
            spacing="5",
            width="100%",
            max_width="48rem",
        ),
        padding_y="2rem",
    )


def index() -> rx.Component:
    return rx.cond(State.is_authenticated, profile_view(), login_view())


app = rx.App()
app.add_page(index)
