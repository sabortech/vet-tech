"""Real API verification with explicitly authorized, ledgered synthetic fixtures.

Private snapshots/tokens stay in .venv/clinical-smoke. Never prints API bodies.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import secrets
import time
from threading import Lock
from uuid import uuid4

import httpx

from animal_catalog import XanoStore, save
from profile_migration_inventory import digest

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / ".venv/clinical-smoke"
TABLES = ("tutor", "veterinario", "reserva_email", "veterinario_especie", "veterinario_especialidade",
          "pet", "consulta", "vacina", "medicamento", "exame", "doenca", "consulta_doenca",
          "pet_doenca", "acesso_autorizado", "log_acesso", "clinical_lock")
CLEAN_ORDER = ("pet_doenca", "consulta_doenca", "vacina", "medicamento", "exame", "log_acesso",
               "acesso_autorizado", "clinical_lock", "consulta", "doenca", "pet",
               "veterinario_especie", "veterinario_especialidade", "reserva_email", "veterinario", "tutor")


class Smoke:
    def __init__(self, folder):
        self.folder = Path(folder).resolve()
        if not self.folder.is_relative_to(PRIVATE.resolve()):
            raise RuntimeError("Run must stay inside private fixture directory")
        self.store = XanoStore("vetech", 167758)
        self.path = self.folder / "ledger.json"
        self.data = json.loads(self.path.read_text(encoding="utf-8")) if self.path.exists() else {}
        self.client = httpx.Client(timeout=40)
        self._response_lock = Lock()

    def persist(self):
        save(self.path, self.data)

    def snapshot(self):
        return {table: self.store.pages(self.store.url(table)) for table in TABLES}

    def initialize(self):
        if self.data:
            return
        baseline = self.snapshot()
        save(self.folder / "baseline.json", baseline)
        prefix = "qa-clinical-" + uuid4().hex[:12]
        self.data = {"prefix": prefix, "actors": {}, "pets": {}, "created": {t: [] for t in TABLES},
                     "checks": [], "baseline": {t: {str(r["id"]): digest(r) for r in rows} for t, rows in baseline.items()}}
        self.persist()

    def api(self, method, route, actor=None, payload=None, group="vettech-clinical"):
        if self.data.get("cleaned"):
            raise RuntimeError("Fixtures already removed; start a new private run")
        headers = {"Authorization": "Bearer " + self.data["actors"][actor]["token"]} if actor else {}
        for attempt in range(6):
            response = self.client.request(method, f'{self.store.target["origin"]}/api:{group}/{route}', headers=headers, json=payload)
            if response.status_code != 429:
                break
            time.sleep(5)
        try:
            body = response.json()
        except ValueError:
            body = {}
        with self._response_lock:
            save(self.folder / "last-response.json", {"method": method, "route": route, "status": response.status_code, "body": body})
        return response.status_code, body

    def check(self, name, condition):
        self.data["checks"].append({"name": name, "passed": bool(condition)})
        self.persist()
        print(json.dumps({"check": name, "passed": bool(condition)}), flush=True)
        if not condition:
            raise RuntimeError("Check failed: " + name + "; private response saved")

    def ok(self, name, method, route, actor=None, payload=None, group="vettech-clinical"):
        status, body = self.api(method, route, actor, payload, group)
        self.check(name, status in (200, 201))
        return body

    def deny(self, name, method, route, actor=None, payload=None):
        status, body = self.api(method, route, actor, payload)
        self.check(name, status in (400, 401, 403, 404))
        return body

    def track(self, table, row):
        value = int(row["id"])
        if str(value) in self.data["baseline"][table]:
            raise RuntimeError("Fixture ID overlaps baseline")
        if value not in self.data["created"][table]:
            self.data["created"][table].append(value)
            self.persist()
        return value

    def discover(self):
        """Recover fixture descendants only via explicit ownership references."""
        rows = self.snapshot()
        prefix = self.data["prefix"]
        for table in ("tutor", "veterinario"):
            for row in rows[table]:
                if row.get("email", "").startswith(prefix + "-") and row.get("email", "").endswith("@example.invalid"):
                    self.track(table, row)
        for row in rows["pet"]:
            if row.get("tutor_id") in self.data["created"]["tutor"] and row.get("nome", "").startswith(prefix):
                self.track("pet", row)
        for table in ("consulta", "vacina", "medicamento", "exame", "consulta_doenca", "pet_doenca", "acesso_autorizado", "log_acesso", "clinical_lock"):
            for row in rows[table]:
                if row.get("pet_id") in self.data["created"]["pet"]:
                    self.track(table, row)
        for row in rows["doenca"]:
            if row.get("nome", "").startswith(prefix):
                self.track("doenca", row)
        for table in ("veterinario_especie", "veterinario_especialidade"):
            for row in rows[table]:
                if row.get("veterinario_id") in self.data["created"]["veterinario"]:
                    self.track(table, row)
        for row in rows["reserva_email"]:
            if row.get("email", "").startswith(prefix + "-") and row.get("email", "").endswith("@example.invalid"):
                self.track("reserva_email", row)
        self.persist()
        return rows

    def setup(self):
        self.initialize()
        if self.data.get("cleaned"):
            raise RuntimeError("Fixtures already removed; start a new private run")
        specialties = self.store.pages(self.store.url("especialidade"))
        if not specialties:
            raise RuntimeError("Existing specialty required; no new catalogue data authorized")
        for index, actor in enumerate(("ta", "tb", "va", "vb")):
            if actor not in self.data["actors"]:
                self.data["actors"][actor] = {"email": f'{self.data["prefix"]}-{actor}@example.invalid', "password": secrets.token_urlsafe(24)}
                self.persist()
            user = self.data["actors"][actor]
            if not user.get("id"):
                table = "tutor" if actor[0] == "t" else "veterinario"
                existing = next((r for r in self.store.pages(self.store.url(table)) if r.get("email") == user["email"]), None)
                if not existing:
                    payload = {"nome": self.data["prefix"] + "-" + actor, "email": user["email"], "password": user["password"], "telefone": "00000000000"}
                    if table == "tutor":
                        digits = [int(n) for n in str(secrets.randbelow(900000000) + 100000000)]
                        for weight in (10, 11):
                            digit = 11 - sum(n * (weight - i) for i, n in enumerate(digits)) % 11
                            digits.append(0 if digit >= 10 else digit)
                        payload.update(cpf="".join(map(str, digits)), endereco="Fixture sintética sem endereço real")
                    else:
                        payload.update(crmv="QA" + uuid4().hex[:10].upper(), crmv_uf="SP", especies_ids=[1], especialidades_ids=[specialties[0]["id"]])
                    self.ok("signup_" + actor, "POST", ("tutor" if table == "tutor" else "veterinario") + "/signup", payload=payload, group="H62nB-j2")
                    existing = next(r for r in self.store.pages(self.store.url(table)) if r.get("email") == user["email"])
                user["id"] = self.track(table, existing)
                self.persist()
            if not user.get("token"):
                login = self.ok("login_" + actor, "POST", "acesso/login", payload={"email": user["email"], "password": user["password"]}, group="H62nB-j2")
                user["token"] = login["authToken"]
                self.persist()
        for key, actor, species in (("a", "ta", 1), ("b", "ta", 2), ("c", "tb", 1)):
            if key not in self.data["pets"]:
                name = self.data["prefix"] + "-pet-" + key
                row = next((r for r in self.store.pages(self.store.url("pet")) if r.get("nome") == name and r.get("tutor_id") == self.data["actors"][actor]["id"]), None)
                if not row:
                    row = self.ok("create_pet_" + key, "POST", "pets", actor, {"nome": name, "especie_id": species}, "vettech-pets")
                self.data["pets"][key] = self.track("pet", row)
                self.persist()
        self.discover()
        print(json.dumps({"setup": "ready", "private_ledger": str(self.path.relative_to(ROOT))}), flush=True)

    def booking(self, pet="a", vet="va", hour="10:00", offset=2):
        return {"pet_id": self.data["pets"][pet], "veterinario_id": self.data["actors"][vet]["id"],
                "dia": (datetime.now(timezone.utc) + timedelta(days=offset)).date().isoformat(),
                "horario": hour, "motivo": self.data["prefix"] + "-avaliação sintética", "operacao": str(uuid4())}

    def run(self):
        self.setup()
        a, b, c = (self.data["pets"][key] for key in ("a", "b", "c"))
        self.deny("unauthenticated", "GET", f"tutor/consultas?pet_id={a}")
        self.deny("cross_profile_tutor_as_vet", "GET", "veterinario/agenda", "ta")
        self.deny("cross_profile_vet_as_tutor", "GET", f"tutor/consultas?pet_id={a}", "va")
        self.deny("foreign_pet_professionals", "GET", f"tutor/profissionais?pet_id={c}", "ta")
        options = self.ok("compatible_professionals", "GET", f"tutor/profissionais?pet_id={a}", "ta")
        self.check("minimal_professional_projection", all(set(r) <= {"id", "nome", "crmv", "crmv_uf"} for r in options))
        incompatible = self.booking("b")
        self.deny("incompatible_species", "POST", "tutor/consultas", "ta", {"payload": incompatible})
        for hour in ("07:59", "17:01"):
            self.deny("outside_hours_" + hour, "POST", "tutor/consultas", "ta", {"payload": self.booking(hour=hour)})
        self.deny("past_booking", "POST", "tutor/consultas", "ta", {"payload": self.booking(offset=-2)})
        payload = self.data.get("booking_payload")
        if not payload:
            existing = [r for r in self.store.pages(self.store.url("consulta")) if r.get("pet_id") == a]
            payload = self.booking(hour="08:00")
            if existing:
                original = existing[0]
                payload.update(operacao=original["operacao_chave"].split(":")[-1], motivo=original["motivo"])
            self.data["booking_payload"] = payload
            self.persist()
        reservation = self.ok("booking_08", "POST", "tutor/consultas", "ta", {"payload": payload})
        consult = self.track("consulta", reservation)
        same = self.ok("booking_idempotent_retry", "POST", "tutor/consultas", "ta", {"payload": payload})
        self.check("same_booking_id", reservation["id"] == same["id"])
        self.deny("operation_payload_mismatch", "POST", "tutor/consultas", "ta", {"payload": {**payload, "motivo": "different"}})
        self.ok("booking_17", "POST", "tutor/consultas", "ta", {"payload": self.booking(hour="17:00")})
        consent = self.ok("own_accesses", "GET", f"tutor/pets/{a}/acessos", "ta")[0]
        self.deny("foreign_accesses", "GET", f"tutor/pets/{a}/acessos", "tb")
        self.deny("foreign_history", "GET", f"tutor/pets/{a}/historico", "tb")
        self.ok("prior_history_granted", "GET", f"veterinario/pets/{a}/historico", "va")
        self.deny("ungranted_vet_history", "GET", f"veterinario/pets/{a}/historico", "vb")
        self.ok("manual_start_before_schedule", "POST", f"veterinario/consultas/{consult}/iniciar", "va")
        draft = self.ok("draft_read", "GET", f"veterinario/consultas/{consult}/rascunho", "va")
        self.check("started_state", draft["consulta"]["status"] == "em_atendimento")
        self.ok("start_retry", "POST", f"veterinario/consultas/{consult}/iniciar", "va")
        current = self.ok("start_preserves_timestamp", "GET", f"veterinario/consultas/{consult}/rascunho", "va")
        self.check("same_start_timestamp", draft["consulta"]["iniciada_em"] == current["consulta"]["iniciada_em"])
        record = {"motivo": "Avaliação sintética", "diagnostico": "Registro exclusivamente de teste", "data_atendimento": datetime.now(timezone.utc).date().isoformat(),
                  "vacinas": [{"linha_id": "qa-vaccine", "vacina": "Vacina sintética QA", "lote": "QA", "data_aplicacao": datetime.now(timezone.utc).date().isoformat()}]}
        saved = self.ok("save_draft", "PUT", f"veterinario/consultas/{consult}/rascunho", "va", {"versao": current["consulta"]["versao"], "payload": record})
        recovered = self.ok("recover_draft", "GET", f"veterinario/consultas/{consult}/rascunho", "va")
        self.check("draft_persisted", recovered["consulta"]["rascunho"]["diagnostico"] == record["diagnostico"])
        self.deny("stale_version", "PUT", f"veterinario/consultas/{consult}/rascunho", "va", {"versao": 0, "payload": record})
        self.deny("forged_pet", "PUT", f"veterinario/consultas/{consult}/rascunho", "va", {"versao": saved["versao"], "payload": {**record, "pet_id": c}})
        visible = self.ok("tutor_before_finalization", "GET", f"tutor/pets/{a}/historico", "ta")
        self.check("draft_hidden", not visible["consultas"] and not visible["vacinas"])
        self.ok("revoke_during_attendance", "PUT", f'tutor/pets/{a}/acessos/{consent["id"]}', "ta", {"status": "revogado"})
        self.deny("revoked_save", "PUT", f"veterinario/consultas/{consult}/rascunho", "va", {"versao": saved["versao"], "payload": record})
        agenda = self.ok("redacted_agenda", "GET", "veterinario/agenda", "va")
        self.check("redacted_fields", all(set(r) <= {"id", "status", "agendada_para", "autorizado"} for r in agenda["items"]))
        self.ok("reactivate", "PUT", f'tutor/pets/{a}/acessos/{consent["id"]}', "ta", {"status": "ativo"})
        self.ok("resume_after_reactivation", "GET", f"veterinario/consultas/{consult}/rascunho", "va")
        disease = self.ok("create_disease", "POST", f"veterinario/pets/{a}/doencas", "va", {"payload": {"nome": self.data["prefix"] + "-condição"}})
        self.track("doenca", disease)
        record["doencas"] = [{"linha_id": "qa-disease", "doenca_id": disease["id"], "data_diagnostico": record["data_atendimento"], "estado": "controlada"}]
        record["medicamentos"] = [{"linha_id": "qa-medication", "nome": "Prescrição sintética QA", "dose": "0.5", "unidade": "unidade QA", "frequencia": "Registro QA", "via": "Registro QA", "tipo": "continuo", "data_inicio": record["data_atendimento"]}]
        record["exames"] = [{"linha_id": "qa-exam", "tipo": "Exame sintético QA", "status": "solicitado", "data_solicitacao": record["data_atendimento"]}]
        invalid = {**record, "doencas": [{**record["doencas"][0], "doenca_id": 2147483647}]}
        self.deny("mid_transaction_failure", "POST", f"veterinario/consultas/{consult}/finalizar", "va", {"versao": saved["versao"], "payload": invalid})
        visible = self.ok("rollback_history", "GET", f"tutor/pets/{a}/historico", "ta")
        self.check("no_partial_publication", not visible["vacinas"] and not visible["medicamentos"] and not visible["exames"])
        result = self.ok("finalize", "POST", f"veterinario/consultas/{consult}/finalizar", "va", {"versao": saved["versao"], "payload": record})
        again = self.ok("finalize_retry", "POST", f"veterinario/consultas/{consult}/finalizar", "va", {"versao": saved["versao"], "payload": record})
        self.check("same_finalization", result == again)
        published = self.ok("published_history", "GET", f"tutor/pets/{a}/historico", "ta")
        self.check("complete_publication", all(len(published[key]) == 1 for key in ("consultas", "vacinas", "medicamentos", "exames", "diagnosticos", "doencas")))
        self.check("shared_consultation_origin", all(published[key][0]["consulta_id"] == consult for key in ("vacinas", "medicamentos", "exames", "diagnosticos", "doencas")))
        self.deny("cannot_reopen", "POST", f"veterinario/consultas/{consult}/iniciar", "va")
        self.deny("cannot_edit_finalized", "PUT", f"veterinario/consultas/{consult}/rascunho", "va", {"versao": result["versao"], "payload": record})
        self.ok("revoke_after_finalization", "PUT", f'tutor/pets/{a}/acessos/{consent["id"]}', "ta", {"status": "revogado"})
        visible = self.ok("tutor_keeps_history", "GET", f"tutor/pets/{a}/historico", "ta")
        self.check("history_preserved_after_revoke", len(visible["vacinas"]) == 1)
        self.deny("finalize_retry_requires_consent", "POST", f"veterinario/consultas/{consult}/finalizar", "va", {"versao": saved["versao"], "payload": record})
        self.deny("foreign_audit", "GET", f"tutor/pets/{a}/auditoria", "tb")
        self.ok("audit_owner", "GET", f"tutor/pets/{a}/auditoria", "ta")
        self.discover()

    def cleanup(self):
        current = self.discover()
        save(self.folder / "before-cleanup.json", current)
        for table in CLEAN_ORDER:
            for value in list(self.data["created"][table]):
                if str(value) in self.data["baseline"][table]:
                    raise RuntimeError("Refusing baseline deletion")
                if not any(r["id"] == value for r in current[table]):
                    continue
                # Block fixture cleanup if a record outside the ledger references it.
                field = {"pet": "pet_id", "consulta": "consulta_id", "doenca": "doenca_id", "tutor": "tutor_id", "veterinario": "veterinario_id"}.get(table)
                if field:
                    for other, rows in current.items():
                        if any(r.get(field) == value and r["id"] not in self.data["created"][other] for r in rows):
                            raise RuntimeError("Non-fixture reference blocks cleanup")
                response = self.store.request("DELETE", self.store.url(table) + f"/{value}")
                if response.status_code not in (200, 204, 404):
                    raise RuntimeError("Fixture cleanup refused")
        after = self.snapshot()
        save(self.folder / "after-cleanup.json", after)
        for table, rows in after.items():
            values = {str(r["id"]): digest(r) for r in rows}
            self.check("baseline_preserved_" + table, all(values.get(key) == value for key, value in self.data["baseline"][table].items()))
            self.check("fixtures_removed_" + table, not any(r["id"] in self.data["created"][table] for r in rows))
        self.data["cleaned"] = True
        self.check("technical_locks_clear", not after["clinical_lock"])
        for actor in self.data["actors"].values():
            actor.pop("token", None)
            actor.pop("password", None)
        self.persist()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("setup", "test", "cleanup"))
    parser.add_argument("--run", required=True)
    args = parser.parse_args()
    folder = (PRIVATE / args.run).resolve()
    if not folder.is_relative_to(PRIVATE.resolve()):
        raise SystemExit("Invalid private run path")
    smoke = Smoke(folder)
    try:
        if args.action == "setup": smoke.setup()
        elif args.action == "test": smoke.run()
        else: smoke.cleanup()
    except Exception as error:
        print(json.dumps({"failed": type(error).__name__, "message": str(error)[:200], "private_run": args.run}), flush=True)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
