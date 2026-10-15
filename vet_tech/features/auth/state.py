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
    selected_pet: dict[str, str] = {}
    pet_target_id: str = ""
    pet_detail_message: str = ""
    is_loading_pet: bool = False
    _auth_token: str = ""
    _session_generation: int = 0
    _pet_context_generation: int = 0
    _pet_list_generation: int = 0

    @rx.var
    def selected_pet_id(self) -> str:
        """Validated pet context for future per-pet features; never a pending ID."""
        return self.selected_pet.get("id", "")

    def _clear_pet_context(self):
        """Invalidate all pet-scoped data and pending work in one place.

        Future clinical features must clear their pet-scoped state here and
        check the same session/context generation before accepting responses.
        """
        self._pet_context_generation += 1
        self.selected_pet = {}
        self.pet_target_id = ""
        self.pet_detail_message = ""
        self.is_loading_pet = False

    def _clear_session(self):
        self._session_generation += 1
        self._pet_list_generation += 1
        self._clear_pet_context()
        self._auth_token = ""
        self.is_authenticated = False
        self.pets = []
        self.species_options = []
        self.breed_options = []
        self.selected_species_id = ""
        self.selected_breed_id = ""
        self.pet_message = ""
        self.is_loading_pets = False
        self.is_busy = False

    def _pet_request_is_current(self, generation: int, session: int, token: str) -> bool:
        return (
            generation == self._pet_context_generation
            and session == self._session_generation
            and token == self._auth_token
            and bool(token)
        )

    def _expire_session(self):
        self._clear_session()
        self.login_message = "Sua sessão expirou. Entre novamente."

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
        self.signup_cpf = ""
        return rx.redirect("/cadastro")

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

        self.login_message = ""
        self._clear_session()
        self.is_busy = True
        session = self._session_generation
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
            if session != self._session_generation:
                return
            if not token:
                raise XanoRequestError("O Xano não retornou uma sessão válida.")

            self._auth_token = str(token)
            self.is_authenticated = True
            self.pets = []
            self.species_options = []
            self.breed_options = []
            self.selected_species_id = ""
            self.selected_breed_id = ""
            self.pet_message = ""
            try:
                await self._load_species()
            except XanoRequestError as error:
                if session != self._session_generation:
                    return
                if error.status_code == 401:
                    self._expire_session()
                    return
                self.pet_message = f"Não foi possível carregar as espécies: {error}"
            if session != self._session_generation:
                return
            await self._load_pets()
        except XanoRequestError as error:
            if session == self._session_generation:
                self._clear_session()
                self.login_message = str(error)
        finally:
            if session == self._session_generation:
                self.is_busy = False

    @rx.event
    async def signup(self, form_data: dict[str, Any]):
        if self.is_busy:
            return
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

        if password != str(form_data.get("password_confirmation", "")):
            self.signup_message = "As senhas não coincidem."
            return

        self.is_busy = True
        self.signup_message = ""
        yield
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
            yield rx.redirect("/login")
        finally:
            self.is_busy = False

    @rx.event
    async def logout(self):
        self._clear_session()
        self.login_message = ""

    async def _load_species(self):
        session = self._session_generation
        result = await xano_request(
            "GET",
            PET_API_GROUP,
            "catalog/especies",
            auth_token=self._auth_token,
        )
        if session != self._session_generation:
            return
        self.species_options = [
            {"id": str(item["id"]), "nome": str(item.get("nome") or "")}
            for item in result or []
        ]

    async def _load_breeds(self, species_id: str, token: str | None = None) -> list[dict[str, str]]:
        query = urlencode({"especie_id": species_id})
        result = await xano_request(
            "GET",
            PET_API_GROUP,
            f"catalog/racas?{query}",
            auth_token=self._auth_token if token is None else token,
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

    def _start_pet_selection(self, pet_id: str):
        self._clear_pet_context()
        if not self._auth_token:
            self._expire_session()
            return
        if not pet_id.isascii() or not pet_id.isdecimal() or int(pet_id) <= 0:
            self.pet_detail_message = "Identificador de pet inválido."
            return
        self.pet_target_id = str(int(pet_id))
        self.is_loading_pet = True

    async def _load_pet_detail(self):
        pet_id = self.pet_target_id
        if not pet_id or not self._auth_token:
            return
        generation = self._pet_context_generation
        session = self._session_generation
        token = self._auth_token
        try:
            pet = await xano_request("GET", PET_API_GROUP, f"pets/{pet_id}", auth_token=token)
            if not self._pet_request_is_current(generation, session, token):
                return
            if not isinstance(pet, dict) or str(pet.get("id")) != pet_id:
                raise XanoRequestError("O Xano retornou dados incompatíveis com o pet solicitado.")

            species_id = str(pet.get("especie_id") or "")
            species_name = next((item["nome"] for item in self.species_options if item["id"] == species_id), "")
            warnings = [] if species_name else ["Não foi possível identificar a espécie no catálogo."]
            breed_id = str(pet.get("raca_id") or "")
            breed_name = "SRD"
            if breed_id not in ("", "0"):
                breed_name = "Raça"
                try:
                    breeds = await self._load_breeds(species_id, token=token)
                    breed_name = next((item["nome"] for item in breeds if item["id"] == breed_id), "Raça")
                    if breed_name == "Raça":
                        warnings.append("Não foi possível identificar a raça no catálogo.")
                except XanoRequestError as error:
                    if error.status_code == 401:
                        raise
                    warnings.append(f"Não foi possível consultar as raças: {error}")
            if not self._pet_request_is_current(generation, session, token):
                return
            details = {
                key: "" if pet.get(key) is None else str(pet[key])
                for key in ("id", "nome", "especie_id", "raca_id", "sexo", "data_nasc", "peso_atual", "cor_pelo", "num_microchip")
            }
            details.update(nome=details["nome"] or "Pet", especie=species_name or "Espécie", raca=breed_name)
            self.selected_pet = details
            self.pet_detail_message = " ".join(warnings)
        except XanoRequestError as error:
            if self._pet_request_is_current(generation, session, token):
                if error.status_code == 401:
                    self._expire_session()
                else:
                    self.selected_pet = {}
                    self.pet_detail_message = str(error)
        finally:
            if self._pet_request_is_current(generation, session, token):
                self.is_loading_pet = False

    @rx.event
    async def open_pet(self, pet_id: str):
        self._start_pet_selection(pet_id)
        generation = self._pet_context_generation
        yield
        if generation == self._pet_context_generation:
            await self._load_pet_detail()

    @rx.event
    async def retry_pet(self):
        self._start_pet_selection(self.pet_target_id)
        generation = self._pet_context_generation
        yield
        if generation == self._pet_context_generation:
            await self._load_pet_detail()

    @rx.event
    def close_pet(self):
        self._clear_pet_context()

    async def _load_pets(self):
        self._pet_list_generation += 1
        list_generation = self._pet_list_generation
        session = self._session_generation
        token = self._auth_token
        target = self.pet_target_id
        self._clear_pet_context()
        context_generation = self._pet_context_generation
        self.is_loading_pets = True
        try:
            result = await xano_request(
                "GET",
                PET_API_GROUP,
                "pets",
                auth_token=token,
            )
            species_names = {item["id"]: item["nome"] for item in self.species_options}
            species_ids = sorted(
                {
                    str(item.get("especie_id"))
                    for item in result or []
                    if item.get("especie_id") and item.get("raca_id")
                }
            )
            breed_names: dict[str, str] = {}
            for species_id in species_ids:
                try:
                    breeds = await self._load_breeds(species_id, token=token)
                except XanoRequestError as error:
                    if session != self._session_generation or list_generation != self._pet_list_generation:
                        return
                    if error.status_code == 401:
                        raise
                    self.pet_message = f"Pets carregados, mas não foi possível consultar as raças: {error}"
                    continue
                for breed in breeds:
                    breed_names[breed["id"]] = breed["nome"]

            if session != self._session_generation or list_generation != self._pet_list_generation:
                return
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
                    "peso_atual": str(item["peso_atual"]) if item.get("peso_atual") is not None else "",
                }
                for item in result or []
            ]
            if context_generation == self._pet_context_generation and target:
                if any(item["id"] == target for item in self.pets):
                    self._start_pet_selection(target)
                    await self._load_pet_detail()
                else:
                    self.pet_detail_message = "O pet selecionado não está mais disponível."
        except XanoRequestError as error:
            if session == self._session_generation and list_generation == self._pet_list_generation:
                if error.status_code == 401:
                    self._expire_session()
                else:
                    self.pet_message = str(error)
        finally:
            if session == self._session_generation and list_generation == self._pet_list_generation:
                self.is_loading_pets = False

    @rx.event
    async def refresh_pets(self):
        if self._auth_token:
            self.pet_message = ""
            self._pet_context_generation += 1
            self.selected_pet = {}
            self.is_loading_pet = bool(self.pet_target_id)
            self.is_loading_pets = True
            yield
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
