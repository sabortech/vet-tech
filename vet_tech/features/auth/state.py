from typing import Any
from urllib.parse import urlencode

import reflex as rx

from vet_tech.features.auth.validation import is_valid_cpf, normalize_cpf
from vet_tech.shared.xano_client import (
    AUTH_API_GROUP,
    PET_API_GROUP,
    XanoRequestError,
    xano_request,
)


class State(rx.State):
    login_message: str = ""
    is_authenticated: bool = False
    is_busy: bool = False
    is_registering: bool = False
    signup_message: str = ""
    signup_cpf: str = ""
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

    @rx.var
    def signup_cpf_feedback(self) -> str:
        if not self.signup_cpf:
            return ""
        return "CPF válido." if is_valid_cpf(self.signup_cpf) else "CPF inválido."

    @rx.event
    def show_signup(self):
        self.is_registering = True
        self.login_message = ""
        self.signup_message = ""

    @rx.event
    def show_login(self):
        self.is_registering = False
        self.signup_message = ""

    @rx.event
    def set_signup_cpf(self, value: str):
        self.signup_cpf = value
        self.signup_message = ""

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
    async def signup(self, form_data: dict[str, Any]):
        nome = str(form_data.get("nome", "")).strip()
        cpf = normalize_cpf(str(form_data.get("cpf", "")))
        email = str(form_data.get("email", "")).strip().lower()
        telefone = str(form_data.get("telefone", "")).strip()
        endereco = str(form_data.get("endereco", "")).strip()
        password = str(form_data.get("password", ""))

        if not all((nome, cpf, email, telefone, endereco, password)):
            self.signup_message = "Preencha todos os campos obrigatórios."
            return
        if not is_valid_cpf(cpf):
            self.signup_message = "Informe um CPF válido."
            return

        self.is_busy = True
        self.signup_message = ""
        try:
            await xano_request(
                "POST",
                AUTH_API_GROUP,
                "tutor/signup",
                json_payload={
                    "nome": nome,
                    "cpf": cpf,
                    "email": email,
                    "telefone": telefone,
                    "endereco": endereco,
                    "password": password,
                },
            )
        except XanoRequestError as error:
            self.signup_message = str(error)
        else:
            self.is_registering = False
            self.signup_cpf = ""
            self.login_message = "Cadastro realizado. Entre com seu e-mail e senha."
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
