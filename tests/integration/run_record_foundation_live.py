"""Exercise the real Xano foundation using an isolated synthetic dev dataset.

No mocks or production fallback. Credentials stay in an ignored fixture file.
The suite retains clinical records and immutable audit rows as evidence.
"""

import argparse
import json
from pathlib import Path
import time
import traceback
from urllib.parse import urlparse
import uuid

import httpx


class ContractMismatch(AssertionError):
    """A safe method/path/status diagnostic, without response bodies."""


class Verification:
    def __init__(self, config, transport=None):
        if config.get("environment") != "development" or config.get("synthetic") is not True:
            raise ValueError("É obrigatório um ambiente development com fixtures synthetic=true.")
        origin = config["origin"].rstrip("/")
        parsed = urlparse(origin)
        if parsed.scheme != "https" or not parsed.hostname or parsed.path not in ("", "/"):
            raise ValueError("origin deve ser uma origem HTTPS de desenvolvimento.")
        self.config = config
        self.client = httpx.Client(base_url=origin, timeout=30, transport=transport)
        self.marker = "fixture-foundation-" + uuid.uuid4().hex
        self.passed = []
        self.request_interval = max(0, float(config.get("request_interval", 2.2)))

    def call(self, method, path, actor, *, expected=(200,), body=None, params=None):
        headers = {"Authorization": "Bearer " + self.config["tokens"][actor]}
        if self.config.get("data_source"):
            headers["X-Data-Source"] = self.config["data_source"]
        time.sleep(self.request_interval)
        response = self.client.request(method, path, headers=headers, json=body, params=params)
        if response.status_code not in expected:
            # Response bodies can contain credentials/clinical data: never echo them.
            raise ContractMismatch(f"{method} {path}: HTTP {response.status_code} fora do contrato")
        return response.json() if response.content and response.is_success else None

    def record(self, label):
        self.passed.append(label)
        print(json.dumps({"scenario": label, "status": "passed"}, ensure_ascii=False), flush=True)

    def grant(self, actor, pet, vet, status="ativo", expected=(200,)):
        return self.call("PUT", "/api:vettech-records/authorizations", actor,
                         body={"pet_id": pet, "veterinario_id": vet, "status": status}, expected=expected)

    def logs(self):
        return self.call("GET", "/api:vettech-records/audit", "tutor_a", params={"pet_id": self.config["pet_a"]})

    def consultation(self, pet=None):
        return {"pet_id": pet or self.config["pet_a"], "data": "2026-10-20", "motivo": self.marker}

    def audit_failure(self):
        """Run only in the dev copy with records/audit deliberately throwing."""
        c = self.config
        api = "/api:vettech-records"
        self.grant("tutor_a", c["pet_a"], c["veterinario_a"])
        try:
            before = self.call("GET", api + "/records/tutor", "tutor_a", params={"pet_id": c["pet_a"]})
            logs = self.logs()
            for route in ("/records", "/records/export"):
                self.call("GET", api + route, "vet_a", params={"pet_id": c["pet_a"]}, expected=(400, 403, 500))
            self.call("POST", api + "/consultations", "vet_a", body=self.consultation(), expected=(400, 403, 500))
            self.call("POST", api + "/exams", "vet_a", body={"pet_id": c["pet_a"], "tipo": self.marker, "data": "2026-10-20"}, expected=(400, 403, 500))
            after = self.call("GET", api + "/records/tutor", "tutor_a", params={"pet_id": c["pet_a"]})
            assert before == after and self.logs() == logs, "Falha de auditoria persistiu escrita parcial"
            self.record("falha real de auditoria impede resposta de sucesso e reverte escrita clínica")
        finally:
            self.grant("tutor_a", c["pet_a"], c["veterinario_a"], "revogado")
            self.client.close()

    def invalid_identity(self):
        """Direct backend checks for absent actors without changing any identity."""
        c = self.config
        c["tokens"]["invalid_identity"] = "invalid-synthetic-token"
        try:
            before = self.logs()
            history = self.call("GET", "/api:vettech-records/records/tutor", "tutor_a", params={"pet_id": c["pet_a"]})
            self.grant("tutor_a", c["pet_a"], c["missing_id"], expected=(400, 422))
            self.call("POST", "/api:vettech-records/consultations", "invalid_identity",
                      body=self.consultation(), expected=(401, 403))
            self.call("POST", "/api:vettech-records/consultations", "vet_a",
                      body={**self.consultation(), "pet_id": None}, expected=(400, 422))
            assert self.logs() == before
            assert self.call("GET", "/api:vettech-records/records/tutor", "tutor_a", params={"pet_id": c["pet_a"]}) == history
            self.record("veterinário inexistente, identidade inválida e pet nulo rejeitados sem escrita ou log de sucesso")
        finally:
            self.client.close()

    def run(self):
        c = self.config
        pet, vet = c["pet_a"], c["veterinario_a"]
        denied = (401, 403)
        invalid = (400, 422)
        api = "/api:vettech-records"

        identity_headers = {}
        if c.get("data_source"):
            identity_headers["X-Data-Source"] = c["data_source"]
        for actor, profile, expected_id in (("tutor_a", "tutor", c["tutor_a"]),
                                             ("vet_a", "veterinario", vet)):
            time.sleep(self.request_interval)
            credentials = c["identity_credentials"][actor]
            login = self.client.post("/api:H62nB-j2/acesso/login", headers=identity_headers,
                                     json={**credentials, "perfil": "administrador"})
            assert login.status_code == 200, "Login não autenticou a identidade sintética"
            result = login.json()
            assert result["perfil"] == profile and result["identidade_id"] == expected_id
            time.sleep(self.request_interval)
            wrong = self.client.post("/api:H62nB-j2/acesso/login", headers=identity_headers,
                                     json={"email": credentials["email"], "password": self.marker})
            assert wrong.status_code in denied, "Senha inválida concedeu identidade"
        time.sleep(self.request_interval)
        options = self.client.get("/api:H62nB-j2/cadastro/opcoes").json()
        time.sleep(self.request_interval)
        duplicate = self.client.post("/api:H62nB-j2/veterinario/signup", headers=identity_headers, json={
            "nome": "Fixture duplicidade", "email": c["identity_credentials"]["tutor_a"]["email"],
            "password": self.marker, "telefone": "11999999999", "crmv": uuid.uuid4().hex[:16],
            "crmv_uf": "SP", "especies_ids": [c["especie_a"]],
            "especialidades_ids": [options["especialidades"][0]["id"]]})
        assert duplicate.status_code in invalid, "E-mail existente em tutor foi aceito para veterinário"
        self.record("identidades por domínio, senha, perfil forjado e e-mail único entre perfis verificados")

        # Establish known state; revocations remain in finally even on failure.
        self.grant("tutor_a", pet, vet, "revogado")
        self.grant("tutor_a", pet, c["veterinario_b"], "revogado")
        try:
            before = self.logs()
            self.call("GET", api + "/records", "vet_a", params={"pet_id": pet}, expected=denied)
            assert self.logs() == before, "Negativa alterou auditoria"
            self.grant("tutor_b", pet, vet, expected=denied)
            self.call("GET", api + "/audit", "tutor_b", params={"pet_id": pet}, expected=denied)
            self.record("acesso sem consentimento e gestão por outro tutor negados")

            self.grant("tutor_a", pet, vet)
            self.grant("tutor_a", pet, c["veterinario_b"])
            auth = self.call("GET", api + "/authorizations", "tutor_a", params={"pet_id": pet})
            assert len([row for row in auth if row["status"] == "ativo"]) == 2
            self.call("GET", api + "/records", "vet_b", params={"pet_id": pet})
            self.record("múltiplos veterinários com autorizações independentes")

            before = self.logs()
            for route, action in [("/records", "visualizacao"), ("/records/export", "exportacao")]:
                self.call("GET", api + route, "vet_a", params={"pet_id": pet})
                after = self.logs()
                added = [row for row in after if row["id"] not in {r["id"] for r in before}]
                assert len(added) == 1 and added[0]["acao"] == action
                assert added[0]["veterinario_id"] == vet and added[0]["data_hora"] is not None
                assert abs(added[0]["data_hora"] / 1000 - time.time()) < 120, "Log não contém timestamp atual com horário"
                before = after
            self.record("leitura e exportação JSON geram exatamente um log cada")

            created = self.call("POST", api + "/consultations", "vet_a",
                                body={**self.consultation(), "veterinario_id": c["veterinario_b"], "perfil": "tutor"})
            assert created["pet_id"] == pet and created["veterinario_id"] == vet
            after = self.logs()
            added = [row for row in after if row["id"] not in {r["id"] for r in before}]
            assert len(added) == 1 and added[0]["acao"] == "edicao"
            self.record("consulta deriva autoria da autenticação e gera um log")

            snapshot = self.call("GET", api + "/records", "vet_a", params={"pet_id": pet})
            before = self.logs()
            self.call("POST", api + "/consultations", "vet_a", body={"data": "2026-10-20", "motivo": self.marker}, expected=invalid)
            self.call("POST", api + "/consultations", "vet_a", body=self.consultation(c["missing_id"]), expected=denied)
            self.call("POST", api + "/consultations", "tutor_a", body={**self.consultation(), "perfil": "veterinario", "veterinario_id": vet}, expected=denied)
            self.call("GET", api + "/records", "vet_a", params={"pet_id": c["pet_b"]}, expected=denied)
            assert self.logs() == before, "Negativas alteraram auditoria"
            check = self.call("GET", api + "/records", "vet_a", params={"pet_id": pet})
            assert check == snapshot, "Validação inválida persistiu dados clínicos"
            self.record("pet ausente/inválido, pet alheio e identidade forjada rejeitados sem escrita")

            exam = {"pet_id": pet, "tipo": self.marker, "data": "2026-10-20"}
            before = self.logs()
            self.call("POST", api + "/exams", "vet_a", body={"tipo": self.marker, "data": "2026-10-20"}, expected=invalid)
            self.call("POST", api + "/exams", "vet_a", body={**exam, "pet_id": c["missing_id"]}, expected=denied)
            assert self.logs() == before
            for consulta in (None, created["id"]):
                before = self.logs()
                result = self.call("POST", api + "/exams", "vet_a", body={**exam, "consulta_id": consulta})
                assert result["pet_id"] == pet
                assert (result.get("consulta_id") in (None, 0)) if consulta is None else result["consulta_id"] == consulta
                after = self.logs()
                added = [row for row in after if row["id"] not in {r["id"] for r in before}]
                assert len(added) == 1 and added[0]["acao"] == "edicao"
            before = self.logs()
            snapshot = self.call("GET", api + "/records/tutor", "tutor_a", params={"pet_id": pet})
            for consulta in (c["consulta_other_pet"], c["missing_id"]):
                self.call("POST", api + "/exams", "vet_a", body={**exam, "consulta_id": consulta}, expected=invalid)
            assert self.logs() == before
            assert self.call("GET", api + "/records/tutor", "tutor_a", params={"pet_id": pet}) == snapshot
            self.record("exame avulso e vinculado aceitos; consulta inválida ou de outro pet rejeitada")

            pet_body = {"nome": self.marker, "especie_id": c["especie_a"], "tutor_id": c["tutor_b"]}
            pets_api = "/api:vettech-pets/pets"
            own_before = self.call("GET", pets_api, "tutor_a")
            other_before = self.call("GET", pets_api, "tutor_b")
            for fields in ({"especie_id": c["missing_id"]}, {"raca_id": c["raca_other_species"]}):
                self.call("POST", pets_api, "tutor_a", body={**pet_body, **fields}, expected=invalid)
            assert self.call("GET", pets_api, "tutor_a") == own_before
            result = self.call("POST", pets_api, "tutor_a", body=pet_body)
            assert result["tutor_id"] == c["tutor_a"]
            assert self.call("GET", pets_api, "tutor_b") == other_before
            self.record("espécie/raça validadas e tentativa de forjar tutor não transfere propriedade")

            self._audit_and_revocation()
        finally:
            # Do not delete clinical history or audit logs, even in development.
            for vet_id in (vet, c["veterinario_b"]):
                self.grant("tutor_a", pet, vet_id, "revogado")
            self.client.close()

    def _audit_and_revocation(self):
        c = self.config
        pet, vet = c["pet_a"], c["veterinario_a"]
        api, denied = "/api:vettech-records", (401, 403)
        before = self.logs()
        log_id = before[-1]["id"]
        for actor in ("tutor_a", "tutor_b", "vet_a", "vet_b"):
            for method in ("PATCH", "DELETE"):
                self.call(method, api + f"/audit/{log_id}", actor, body={"acao": "adulterada"}, expected=(401, 403, 405))
        assert self.logs() == before
        self.record("auditoria permanece imutável para todos os usuários")

        # The existing clinical history must share consent checks and audit timestamp.
        legacy = "/api:vettech-clinical/veterinario/pets/" + str(pet) + "/historico"
        before = self.logs()
        self.call("GET", legacy, "vet_a")
        after = self.logs()
        added = [row for row in after if row["id"] not in {r["id"] for r in before}]
        assert len(added) == 1 and added[0]["data_hora"] is not None
        self.record("histórico clínico existente preserva resposta e gera auditoria com horário")

        self.grant("tutor_a", pet, vet, "revogado")
        before = self.logs()
        for route in ("/records", "/records/export"):
            self.call("GET", api + route, "vet_a", params={"pet_id": pet}, expected=denied)
        self.call("POST", api + "/consultations", "vet_a", body=self.consultation(), expected=denied)
        self.call("GET", legacy, "vet_a", expected=denied)
        assert self.logs() == before
        self.call("GET", api + "/records", "vet_b", params={"pet_id": pet})
        self.record("revogação imediata nega leitura/escrita/exportação e preserva outro veterinário")

    def access_regression(self):
        c = self.config
        for vet_id in (c["veterinario_a"], c["veterinario_b"]):
            self.grant("tutor_a", c["pet_a"], vet_id)
        try:
            self._audit_and_revocation()
        finally:
            for vet_id in (c["veterinario_a"], c["veterinario_b"]):
                self.grant("tutor_a", c["pet_a"], vet_id, "revogado")
            self.client.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixtures", required=True, type=Path)
    parser.add_argument("--phase", choices=("normal", "audit-failure", "identity-negative", "access-regression"), default="normal")
    args = parser.parse_args()
    if not args.fixtures.is_file():
        parser.error("Arquivo de fixtures ausente; configure um Xano de desenvolvimento isolado.")
    try:
        config = json.loads(args.fixtures.read_text())
        verification = Verification(config)
        if args.phase == "audit-failure":
            verification.audit_failure()
        elif args.phase == "access-regression":
            verification.access_regression()
        elif args.phase == "identity-negative":
            verification.invalid_identity()
        else:
            verification.run()
    except (httpx.HTTPError, AssertionError, ValueError, KeyError) as exc:
        # Never print transport exceptions, tokens, request/response bodies.
        line = traceback.extract_tb(exc.__traceback__)[-1].lineno
        detail = f" {exc}" if isinstance(exc, ContractMismatch) else ""
        raise SystemExit(f"Integração não concluída ({type(exc).__name__}, linha {line}).{detail}") from None


if __name__ == "__main__":
    main()
