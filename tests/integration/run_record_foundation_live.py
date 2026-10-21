"""Exercise the real Xano foundation using an isolated synthetic dev dataset.

No mocks or production fallback. Credentials stay in an ignored fixture file.
The suite retains clinical records and immutable audit rows as evidence.
"""

import argparse
import json
from pathlib import Path
import time
from urllib.parse import urlparse
import uuid

import httpx


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

    def call(self, method, path, actor, *, expected=(200,), body=None, params=None):
        headers = {"Authorization": "Bearer " + self.config["tokens"][actor]}
        if self.config.get("data_source"):
            headers["X-Data-Source"] = self.config["data_source"]
        response = self.client.request(method, path, headers=headers, json=body, params=params)
        if response.status_code not in expected:
            # Response bodies can contain credentials/clinical data: never echo them.
            raise AssertionError(f"{method} {path}: HTTP {response.status_code} fora do contrato")
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
            after = self.call("GET", api + "/records/tutor", "tutor_a", params={"pet_id": c["pet_a"]})
            assert before == after and self.logs() == logs, "Falha de auditoria persistiu escrita parcial"
            self.record("falha real de auditoria impede resposta de sucesso e reverte escrita clínica")
        finally:
            self.grant("tutor_a", c["pet_a"], c["veterinario_a"], "revogado")
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
        login = self.client.post("/api:H62nB-j2/profiles/login", headers=identity_headers,
                                 json={"email": c["dual_email"], "password": c["dual_password"]})
        assert login.status_code == 200, "Login compartilhado não autenticou a fixture"
        profiles = login.json()["profiles"]
        assert {(row["perfil"], row["id"]) for row in profiles} == {
            ("tutor", c["tutor_a"]), ("veterinario", vet)}
        wrong = self.client.post("/api:H62nB-j2/profiles/login", headers=identity_headers,
                                 json={"email": c["dual_email"], "password": self.marker})
        assert wrong.status_code in denied, "Senha inválida concedeu identidade"
        self.record("mesmo e-mail autentica ambos os perfis somente com credenciais válidas")

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
            for consulta in (None, created["id"]):
                before = self.logs()
                result = self.call("POST", api + "/exams", "vet_a", body={**exam, "consulta_id": consulta})
                assert result["pet_id"] == pet and result.get("consulta_id") == consulta
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

            before = self.logs()
            log_id = before[-1]["id"]
            for actor in ("tutor_a", "tutor_b", "vet_a", "vet_b"):
                for method in ("PATCH", "DELETE"):
                    self.call(method, api + f"/audit/{log_id}", actor, body={"acao": "adulterada"}, expected=(401, 403, 405))
            assert self.logs() == before
            self.record("auditoria permanece imutável para todos os usuários")

            self.grant("tutor_a", pet, vet, "revogado")
            before = self.logs()
            for route in ("/records", "/records/export"):
                self.call("GET", api + route, "vet_a", params={"pet_id": pet}, expected=denied)
            self.call("POST", api + "/consultations", "vet_a", body=self.consultation(), expected=denied)
            assert self.logs() == before
            self.call("GET", api + "/records", "vet_b", params={"pet_id": pet})
            self.record("revogação imediata nega leitura/escrita/exportação e preserva outro veterinário")
        finally:
            # Do not delete clinical history or audit logs, even in development.
            for vet_id in (vet, c["veterinario_b"]):
                self.grant("tutor_a", pet, vet_id, "revogado")
            self.client.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixtures", required=True, type=Path)
    parser.add_argument("--phase", choices=("normal", "audit-failure"), default="normal")
    args = parser.parse_args()
    if not args.fixtures.is_file():
        parser.error("Arquivo de fixtures ausente; configure um Xano de desenvolvimento isolado.")
    try:
        config = json.loads(args.fixtures.read_text())
        verification = Verification(config)
        if args.phase == "audit-failure":
            verification.audit_failure()
        else:
            verification.run()
    except (httpx.HTTPError, AssertionError, ValueError, KeyError) as exc:
        # Never print transport exceptions, tokens, request/response bodies.
        raise SystemExit(f"Integração não concluída ({type(exc).__name__}); confira configuração e contrato.") from None


if __name__ == "__main__":
    main()
