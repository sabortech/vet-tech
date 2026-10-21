from typing import Any
from urllib.parse import urlencode

import reflex as rx

from vet_tech.features.auth.validation import is_valid_cpf, normalize_cpf
from vet_tech.features.veterinarians.validation import professional_payload
from vet_tech.shared.xano_client import (
    AUTH_API_GROUP,
    PET_API_GROUP,
    XanoRequestError,
    xano_request,
)


class State(rx.State):
    profile: str = ""
    identity_id: str = ""
    identity_name: str = ""
    signup_profile: str = "tutor"
    registration_species: list[dict[str, str]] = []
    registration_specialties: list[dict[str, str]] = []
    registration_clinics: list[dict[str, str]] = []
    professional_species: list[str] = []
    professional_specialties: list[str] = []
    professional_clinic: str = ""
    registration_options_message: str = ""
    is_loading_registration_options: bool = False
    active_section: str = "Início"
    sidebar_expanded: bool = True
    pet_modal_open: bool = False
    pet_picker_open: bool = False
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
    _registration_generation: int = 0

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
        self.profile = ""
        self.identity_id = ""
        self.identity_name = ""
        self.active_section = "Início"
        self.sidebar_expanded = True
        self.pet_modal_open = False
        self.pet_picker_open = False
        self._registration_generation += 1
        self.professional_species = []
        self.professional_specialties = []
        self.professional_clinic = ""
        self.registration_species = []
        self.registration_specialties = []
        self.registration_clinics = []
        self.registration_options_message = ""
        self.is_loading_registration_options = False
        self._reset_pet_form()
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
        if self.is_busy:
            return
        self._clear_session()
        email = form_data.get("email", "").strip()
        password = form_data.get("password", "")
        if not email or not password:
            self.login_message = "Informe e-mail e senha."
            return

        self.login_message = ""
        self.is_busy = True
        session = self._session_generation
        try:
            result = await xano_request(
                "POST",
                AUTH_API_GROUP,
                "acesso/login",
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
            profile = result.get("perfil")
            identity_id = str(result.get("identidade_id", ""))
            if profile not in ("tutor", "veterinario") or not identity_id.isascii() or not identity_id.isdecimal() or int(identity_id) <= 0:
                raise XanoRequestError("O Xano não retornou uma identidade válida.")
            identity = await xano_request("GET", AUTH_API_GROUP, f"{profile}/me", auth_token=str(token))
            if session != self._session_generation:
                return
            if not isinstance(identity, dict) or identity.get("perfil") != profile or str(identity.get("identidade_id")) != identity_id:
                raise XanoRequestError("Não foi possível confirmar a identidade da sessão.")
            self._auth_token = str(token)
            self.profile = profile
            self.identity_id = identity_id
            self.identity_name = str(identity.get("nome") or "")
            self.is_authenticated = True
            if profile == "veterinario":
                return
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

        if not all((nome, email, telefone, password)):
            self.signup_message = "Preencha todos os campos obrigatórios."
            return
        payload = {"nome": nome, "email": email, "telefone": telefone, "password": password}
        if self.signup_profile == "tutor":
            if not endereco:
                self.signup_message = "Preencha todos os campos obrigatórios."
                return
            if not is_valid_cpf(cpf):
                self.signup_message = "Informe um CPF válido."
                return
            payload.update(cpf=cpf, endereco=endereco)
            endpoint = "tutor/signup"
        elif self.signup_profile == "veterinario":
            try:
                payload.update(professional_payload(form_data, self.professional_species, self.professional_specialties, self.professional_clinic))
            except ValueError as error:
                self.signup_message = str(error)
                return
            endpoint = "veterinario/signup"
        else:
            self.signup_message = "Selecione o perfil a cadastrar."
            return

        if password != str(form_data.get("password_confirmation", "")):
            self.signup_message = "As senhas não coincidem."
            return

        self.is_busy = True
        session = self._session_generation
        self.signup_message = ""
        yield
        try:
            await xano_request(
                "POST",
                AUTH_API_GROUP,
                endpoint,
                json_payload=payload,
            )
        except XanoRequestError as error:
            if session == self._session_generation:
                self.signup_message = str(error)
        else:
            if session != self._session_generation:
                return
            self.is_registering = False
            self.signup_cpf = ""
            self.login_message = "Cadastro realizado. Entre com seu e-mail e senha."
            yield rx.set_value("signup-password", "")
            yield rx.set_value("signup-password-confirmation", "")
            yield rx.redirect("/login")
        finally:
            if session == self._session_generation:
                self.is_busy = False

    @rx.event
    async def logout(self):
        self._clear_session()
        self.login_message = ""
        return rx.clear_selected_files("pet-photo")

    @rx.event
    async def choose_signup_profile(self, value: str):
        if self.is_busy or value not in ("tutor", "veterinario"):
            return
        self.signup_profile = value
        self.signup_message = ""
        self.professional_species = []
        self.professional_specialties = []
        self.professional_clinic = ""
        self._registration_generation += 1
        if value == "veterinario":
            await self.load_registration_options()

    @rx.event
    async def load_registration_options(self):
        self._registration_generation += 1
        generation = self._registration_generation
        self.is_loading_registration_options = True
        self.registration_options_message = ""
        try:
            result = await xano_request("GET", AUTH_API_GROUP, "cadastro/opcoes")
            if generation != self._registration_generation:
                return
            def options(key):
                return [{"id": str(row["id"]), "nome": str(row.get("nome") or "")} for row in result[key]]
            self.registration_species = options("especies")
            self.registration_specialties = options("especialidades")
            self.registration_clinics = options("clinicas")
            if not self.registration_species or not self.registration_specialties:
                self.registration_options_message = "Cadastro profissional indisponível: faltam opções de espécies ou especialidades."
        except (XanoRequestError, KeyError, TypeError) as error:
            if generation == self._registration_generation:
                self.registration_species = []
                self.registration_specialties = []
                self.registration_clinics = []
                self.registration_options_message = "Não foi possível carregar as opções de cadastro. Tente novamente."
        finally:
            if generation == self._registration_generation:
                self.is_loading_registration_options = False

    @rx.event
    def toggle_professional_species(self, value: str, checked: bool):
        if not self.is_busy:
            self.professional_species = [i for i in self.professional_species if i != value] + ([value] if checked else [])

    @rx.event
    def toggle_professional_specialty(self, value: str, checked: bool):
        if not self.is_busy:
            self.professional_specialties = [i for i in self.professional_specialties if i != value] + ([value] if checked else [])

    @rx.event
    def choose_professional_clinic(self, value: str):
        if not self.is_busy:
            self.professional_clinic = "" if value == "none" else value

    def _reset_pet_form(self):
        self.pet_name = ""
        self.pet_sex = ""
        self.pet_birth_date = ""
        self.pet_weight = ""
        self.pet_coat_color = ""
        self.pet_microchip = ""
        self.selected_species_id = ""
        self.selected_breed_id = ""
        self.breed_options = []
        self.pet_message = ""

    @rx.event
    def change_section(self, value: str):
        if value in ("Início", "Vacinas", "Medicamentos", "Doenças", "Consultas"):
            self.active_section = value
            self.pet_picker_open = False

    @rx.event
    def toggle_sidebar(self):
        self.sidebar_expanded = not self.sidebar_expanded

    @rx.event
    def set_pet_modal(self, opened: bool):
        if self.is_busy or self.profile != "tutor":
            return
        self._reset_pet_form()
        self.pet_modal_open = opened
        return rx.clear_selected_files("pet-photo")

    @rx.event
    def show_pet_picker(self):
        self.pet_picker_open = True
        self.active_section = "Início"

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
        session = self._session_generation
        self.selected_species_id = species_id
        self.selected_breed_id = ""
        self.breed_options = []
        self.pet_message = ""
        if not species_id:
            return
        try:
            breeds = await self._load_breeds(species_id)
            if session == self._session_generation and species_id == self.selected_species_id:
                self.breed_options = breeds
        except XanoRequestError as error:
            if session == self._session_generation and species_id == self.selected_species_id:
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
            self.pet_picker_open = False
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
        if self.is_busy:
            return
        session = self._session_generation
        self.is_busy = True
        yield
        try:
            if session != self._session_generation:
                return
            result = await self._create_pet(files)
            if result is not None and session == self._session_generation:
                yield result
        finally:
            if session == self._session_generation:
                self.is_busy = False

    async def _create_pet(self, files: list[rx.UploadFile]):
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

        self.is_busy = True
        self.pet_message = ""
        session = self._session_generation
        token = self._auth_token
        try:
            upload = files[0] if files else None
            upload_files = None
            if upload:
                content = await upload.read()
                if session != self._session_generation:
                    return
                upload_files = {"foto": (upload.name, content, upload.content_type or "application/octet-stream")}
            await xano_request(
                "POST",
                PET_API_GROUP,
                "pets",
                auth_token=token,
                form_data=form_data if upload_files else None,
                files=upload_files,
                json_payload=form_data if not upload_files else None,
            )
            if session != self._session_generation:
                return
            self.pet_modal_open = False
            self.pet_name = ""
            self.selected_breed_id = ""
            self.pet_sex = ""
            self.pet_birth_date = ""
            self.pet_weight = ""
            self.pet_coat_color = ""
            self.pet_microchip = ""
            self.pet_message = "Pet cadastrado com sucesso."
            await self._load_pets()
            if session != self._session_generation:
                return
            return rx.clear_selected_files("pet-photo")
        except XanoRequestError as error:
            if session == self._session_generation:
                if error.status_code == 401:
                    self._expire_session()
                else:
                    self.pet_message = str(error)
        finally:
            if session == self._session_generation:
                self.is_busy = False
