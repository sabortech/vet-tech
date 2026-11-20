"""Operações da área administrativa, isoladas pela sessão autenticada."""

import base64

import reflex as rx

from vet_tech.shared.dates import calendar_date
from vet_tech.shared.xano_client import AUTH_API_GROUP, XanoRequestError, xano_request


class ClinicMixin(rx.State, mixin=True):
    clinic_section: str = "Veterinários"
    clinic_name: str = ""
    clinic_admin_vets: list[dict[str, str]] = []
    clinic_admin_pets: list[dict[str, str]] = []
    clinic_catalog_species: list[dict[str, str]] = []
    clinic_catalog_breeds: list[dict[str, str]] = []
    clinic_selected_species: str = ""
    clinic_admin_loading: bool = False
    clinic_admin_loaded: bool = False
    clinic_admin_message: str = ""

    def _clear_clinic_admin(self):
        self.clinic_section = "Veterinários"
        self.clinic_name = ""
        self.clinic_admin_vets = []
        self.clinic_admin_pets = []
        self.clinic_catalog_species = []
        self.clinic_catalog_breeds = []
        self.clinic_selected_species = ""
        self.clinic_admin_loading = False
        self.clinic_admin_loaded = False
        self.clinic_admin_message = ""

    @rx.var
    def clinic_filtered_breeds(self) -> list[dict[str, str]]:
        return [b for b in self.clinic_catalog_breeds if b["especie_id"] == self.clinic_selected_species]

    @rx.event
    def clinic_select_species(self, value: str):
        self.clinic_selected_species = value

    @rx.event
    def clinic_navigate(self, section: str):
        if section in ("Veterinários", "Pets para adoção"):
            self.clinic_section = section
            self.clinic_admin_message = ""

    @rx.event
    async def clinic_load(self):
        if not self.is_authenticated or self.profile != "clinica" or self.clinic_admin_loading:
            return
        self.clinic_admin_loading = True
        self.clinic_admin_message = ""
        session, token = self._session_generation, self._auth_token
        yield
        try:
            vets = await xano_request("GET", AUTH_API_GROUP, "clinica/veterinarios", auth_token=token)
            pets = await xano_request("GET", AUTH_API_GROUP, "clinica/pets", auth_token=token)
            catalog = await xano_request("GET", AUTH_API_GROUP, "clinica/catalogo", auth_token=token)
            if session != self._session_generation or token != self._auth_token:
                return
            if not isinstance(vets, list) or not isinstance(pets, list) or not isinstance(catalog, dict):
                raise XanoRequestError("Resposta inválida do servidor.")
            self.clinic_admin_vets = [{"nome": str(v.get("nome") or "Não informado"), "crmv": str(v.get("crmv") or ""), "uf": str(v.get("crmv_uf") or ""), "especialidades": ", ".join(str(x) for x in v.get("especialidades", []) if x)} for v in vets]
            self.clinic_admin_pets = [{"id": str(p.get("id") or ""), "nome": str(p.get("nome") or "Pet"), "disponivel": "sim" if p.get("disponivel_adocao") is True else "nao"} for p in pets]
            self.clinic_catalog_species = [{"id": str(x["id"]), "nome": str(x.get("nome") or "")} for x in catalog.get("especies", [])]
            self.clinic_catalog_breeds = [{"id": str(x["id"]), "nome": str(x.get("nome") or ""), "especie_id": str(x.get("especie_id") or "")} for x in catalog.get("racas", [])]
            self.species_options = list(self.clinic_catalog_species)
            self.clinic_admin_loaded = True
        except (XanoRequestError, KeyError, TypeError) as error:
            if session == self._session_generation:
                self.clinic_admin_message = str(error) if isinstance(error, XanoRequestError) else "Não foi possível carregar os dados."
        finally:
            if session == self._session_generation:
                self.clinic_admin_loading = False

    @rx.event
    async def clinic_create_pet(self, files: list[rx.UploadFile]):
        if not self.is_authenticated or self.profile != "clinica" or self.clinic_admin_loading or self.is_busy:
            return
        name = self.pet_name.strip()
        species = self.selected_species_id
        breed = self.selected_breed_id
        if not name or not species.isdecimal() or (breed and not breed.isdecimal()):
            self.clinic_admin_message = "Informe o nome e a espécie do pet."
            return
        payload = {"nome": name, "especie_id": int(species)}
        if breed:
            payload["raca_id"] = int(breed)
        if self.pet_sex.strip():
            payload["sexo"] = self.pet_sex.strip()
        if self.pet_birth_date:
            birth = calendar_date(self.pet_birth_date)
            if birth is None:
                self.clinic_admin_message = "Informe uma data de nascimento válida."
                return
            payload["data_nasc"] = birth.isoformat()
        if self.pet_coat_color.strip():
            payload["cor_pelo"] = self.pet_coat_color.strip()
        if self.pet_microchip:
            if not self.pet_microchip.isdigit():
                self.clinic_admin_message = "O microchip deve conter somente números."
                return
            payload["num_microchip"] = int(self.pet_microchip)
        weight = self.pet_weight.strip()
        if weight:
            if not weight.isdecimal():
                self.clinic_admin_message = "O peso deve ser um número inteiro."
                return
            payload["peso_atual"] = int(weight)
        session, token = self._session_generation, self._auth_token
        self.clinic_admin_loading = True
        self.is_busy = True
        yield
        try:
            if files:
                upload = files[0]
                content = await upload.read()
                if session != self._session_generation or token != self._auth_token:
                    return
                content_type = upload.content_type or "application/octet-stream"
                if content_type not in ("image/jpeg", "image/png", "image/webp") or len(content) > 1024 * 1024:
                    raise XanoRequestError("Selecione uma imagem JPEG, PNG ou WebP de até 1 MB.")
                payload["foto"] = f"data:{content_type};base64,{base64.b64encode(content).decode('ascii')}"
            pet = await xano_request("POST", AUTH_API_GROUP, "clinica/pets", auth_token=token, json_payload=payload)
            if session != self._session_generation or token != self._auth_token:
                return
            if not isinstance(pet, dict) or not str(pet.get("id", "")).isdecimal():
                raise XanoRequestError("Resposta incompatível ao cadastrar pet.")
            self.clinic_admin_pets = self.clinic_admin_pets + [{"id": str(pet["id"]), "nome": str(pet.get("nome") or name), "disponivel": "nao"}]
            self._reset_pet_form()
            self.clinic_admin_message = "Pet cadastrado. Publique-o quando estiver pronto para adoção."
            yield [rx.clear_selected_files("pet-photo"), rx.call_script('window.dispatchEvent(new Event("vettech:pet-photo-clear"));')]
        except XanoRequestError as error:
            if session == self._session_generation:
                self.clinic_admin_message = str(error)
        finally:
            if session == self._session_generation:
                self.clinic_admin_loading = False
                self.is_busy = False

    @rx.event
    async def clinic_set_availability(self, pet_id: str, available: bool):
        if not self.is_authenticated or self.profile != "clinica" or self.clinic_admin_loading or not pet_id.isdecimal():
            return
        session, token = self._session_generation, self._auth_token
        self.clinic_admin_loading = True
        yield
        try:
            result = await xano_request("POST", AUTH_API_GROUP, "clinica/disponibilidade", auth_token=token, json_payload={"pet_id": int(pet_id), "disponivel": available})
            if session != self._session_generation or token != self._auth_token:
                return
            if not isinstance(result, dict) or str(result.get("id")) != pet_id or result.get("disponivel_adocao") is not available:
                raise XanoRequestError("Resposta incompatível ao atualizar disponibilidade.")
            self.clinic_admin_pets = [{**p, "disponivel": "sim" if available else "nao"} if p["id"] == pet_id else p for p in self.clinic_admin_pets]
            self.clinic_admin_message = "Disponibilidade atualizada."
        except XanoRequestError as error:
            if session == self._session_generation:
                self.clinic_admin_message = str(error)
        finally:
            if session == self._session_generation:
                self.clinic_admin_loading = False
