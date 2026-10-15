"""Verify real per-pet authorization using isolated, temporary test records.

Run with the configured Xano CLI profile and --allow-temporary-records.
By default all fixtures are removed. --keep-fixtures supports browser QA;
run again with --cleanup to remove only the records owned by that run.
Fixture credentials stay in the ignored .venv directory and are never printed.
"""
import argparse
import asyncio
import hashlib
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import sys
import time
import uuid

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


def cli_profile():
    cli = Path(shutil.which("xano.cmd")).parent
    code = (
        "const fs=require('fs');const y=require(process.argv[1]);"
        "const path=process.env.XANO_CONFIG||process.env.USERPROFILE+'/.xano/credentials.yaml';"
        "const c=y.load(fs.readFileSync(path,'utf8'));"
        "console.log(JSON.stringify(c.profiles[process.env.XANO_PROFILE||c.default]));"
    )
    result = subprocess.run(
        ["node", "-e", code, str(cli / "node_modules/@xano/cli/node_modules/js-yaml")],
        capture_output=True, text=True, check=True,
    )
    return json.loads(result.stdout)


def cpf():
    digits = [secrets.randbelow(10) for _ in range(9)]
    for length in (9, 10):
        remainder = sum(d * w for d, w in zip(digits, range(length + 1, 1, -1))) % 11
        digits.append(0 if remainder < 2 else 11 - remainder)
    return "".join(map(str, digits))


def digest(record):
    return hashlib.sha256(json.dumps(record, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


class LiveVerification:
    def __init__(self, fixture_file):
        profile = cli_profile()
        self.origin = profile["instance_origin"].rstrip("/")
        self.meta_url = f'{self.origin}/api:meta/workspace/{profile["workspace"]}'
        self.meta = httpx.Client(timeout=40, headers={"Authorization": "Bearer " + profile["access_token"]})
        self.api = httpx.Client(timeout=40)
        self.path = fixture_file
        self.data = {"marker": "vt-select-" + uuid.uuid4().hex[:12], "accounts": [], "pets": [], "tables": {}, "baseline": {}}

    def request(self, client, method, url, **kwargs):
        for attempt in range(6):
            result = client.request(method, url, **kwargs)
            if result.status_code != 429:
                return result
            time.sleep(min(2 ** attempt, 8))
        raise AssertionError("Rate limit persistente")

    def records(self, table):
        rows, page = [], 1
        while True:
            r = self.request(self.meta, "GET", f'{self.meta_url}/table/{self.data["tables"][table]}/content', params={"page": page, "per_page": 100})
            assert r.is_success, f"Metadata read failed: HTTP {r.status_code}"
            body = r.json()
            rows.extend(body if isinstance(body, list) else body["items"])
            if isinstance(body, list) or not body.get("nextPage"):
                return rows
            page = body["nextPage"]

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data), encoding="utf-8")

    def prepare(self):
        assert not self.path.exists(), "Fixture file exists; clean up the previous run first"
        r = self.request(self.meta, "GET", self.meta_url + "/table", params={"per_page": 100})
        assert r.is_success
        body = r.json()
        self.data["tables"] = {item["name"]: item["id"] for item in body["items"] if item["name"] in ("tutor", "pet")}
        assert len(self.data["tables"]) == 2
        for table in self.data["tables"]:
            self.data["baseline"][table] = {str(row["id"]): digest(row) for row in self.records(table)}
        self.save()
        for label in ("a", "b", "empty"):
            account = {"email": f'{self.data["marker"]}-{label}@example.invalid', "password": secrets.token_urlsafe(20)}
            self.data["accounts"].append(account)
            self.save()
            payload = {**account, "nome": "Fixture seleção " + label, "cpf": cpf(), "telefone": "11999999999", "endereco": "Endereço fictício de teste"}
            r = self.request(self.api, "POST", self.origin + "/api:H62nB-j2/tutor/signup", json=payload)
            assert r.status_code == 200, f"Test signup failed: HTTP {r.status_code}"
            token = self.login(account)
            for number in range(2 if label == "a" else 1 if label == "b" else 0):
                headers = {"Authorization": "Bearer " + token}
                species = self.request(self.api, "GET", self.origin + "/api:vettech-pets/catalog/especies", headers=headers)
                assert species.is_success and species.json(), "No species available for test fixtures"
                name = f'{self.data["marker"]} Pet {label.upper()}{number + 1}'
                r = self.request(self.api, "POST", self.origin + "/api:vettech-pets/pets", headers=headers,
                                 json={"nome": name, "especie_id": species.json()[0]["id"], "raca_id": None})
                assert r.status_code == 200, f"Test pet creation failed: HTTP {r.status_code}"
                self.data["pets"].append({"id": r.json()["id"], "name": name, "account": label})
                self.save()

    def login(self, account):
        r = self.request(self.api, "POST", self.origin + "/api:H62nB-j2/tutor/login", json={key: account[key] for key in ("email", "password")})
        assert r.status_code == 200 and r.json().get("authToken"), "Fixture login failed"
        return r.json()["authToken"]

    def run(self):
        first, second = self.data["accounts"][:2]
        token_a, token_b = self.login(first), self.login(second)
        a = next(p for p in self.data["pets"] if p["account"] == "a")
        b = next(p for p in self.data["pets"] if p["account"] == "b")
        checks = [(str(a["id"]), token_a, 200), (str(b["id"]), token_b, 200),
                  (str(a["id"]), token_b, 404), (str(b["id"]), token_a, 404),
                  ("1000000000", token_a, 404), ("0", token_a, 400), ("abc", token_a, 404),
                  (str(a["id"]), "", 401), (str(a["id"]), "invalid-test-token", 401)]
        for pet_id, token, status in checks:
            r = self.request(self.api, "GET", f"{self.origin}/api:vettech-pets/pets/{pet_id}",
                             headers={"Authorization": "Bearer " + token} if token else {})
            assert r.status_code == status, f"Pet ID {pet_id}: expected HTTP {status}, received {r.status_code}"
            if status == 200:
                assert set(r.json()) == {"id", "nome", "especie_id", "raca_id", "sexo", "data_nasc", "peso_atual", "cor_pelo", "num_microchip"}
            elif status == 404 and pet_id != "abc":
                assert r.json().get("message") == "Pet não disponível.", "404 must be generic"
        print(json.dumps({"api_authorization_cases": len(checks), "status": "passed"}), flush=True)
        asyncio.run(self.verify_reflex_flow())
        self.verify_existing_records()

    async def verify_reflex_flow(self):
        os.environ["XANO_API_BASE_URL"] = self.origin
        from vet_tech.features.auth.state import State
        state = State(_reflex_internal_init=True)
        for account in self.data["accounts"]:
            # Public API verification just sent a burst of requests. Respect
            # the free-plan window before each separate real-user flow.
            await asyncio.sleep(21)
            await State.login.fn(state, {key: account[key] for key in ("email", "password")})
            assert state.is_authenticated and not state.selected_pet_id, f"Fixture session failed: {state.login_message}"
            account_pets = [p for p in self.data["pets"] if p["account"] == ("a" if account == self.data["accounts"][0] else "b" if account == self.data["accounts"][1] else "empty")]
            for fixture in account_pets:
                updates = State.open_pet.fn(state, str(fixture["id"]))
                await updates.__anext__()
                assert not state.selected_pet_id and state.is_loading_pet
                _ = [update async for update in updates]
                assert state.selected_pet_id == str(fixture["id"]), f"Detail failed: {state.pet_detail_message}"
                assert state.selected_pet["nome"] == fixture["name"]
            if account_pets:
                alien = next(p for p in self.data["pets"] if p["account"] != account_pets[0]["account"])
                _ = [update async for update in State.open_pet.fn(state, str(alien["id"]))]
                assert not state.selected_pet_id and state.is_authenticated
            else:
                assert state.pets == []
            await State.logout.fn(state)
            assert not state.selected_pet_id and not state.is_authenticated
        print(json.dumps({"reflex_real_xano_flow": "passed", "accounts": 3, "pets": 3}), flush=True)

    def verify_existing_records(self):
        for table, baseline in self.data["baseline"].items():
            current = {str(row["id"]): digest(row) for row in self.records(table)}
            assert all(current.get(key) == value for key, value in baseline.items()), "A preexisting record changed"
        print(json.dumps({"preexisting_records": "unchanged"}), flush=True)

    def cleanup(self):
        marker = self.data["marker"]
        owned_tutors = [row for row in self.records("tutor") if row.get("email") in {a["email"] for a in self.data["accounts"]}]
        assert all(row["email"].startswith(marker + "-") and str(row["id"]) not in self.data["baseline"]["tutor"] for row in owned_tutors)
        tutor_ids = {row["id"] for row in owned_tutors}
        owned_pets = [row for row in self.records("pet") if row.get("tutor_id") in tutor_ids and row.get("nome", "").startswith(marker + " ")]
        for table, rows in (("pet", owned_pets), ("tutor", owned_tutors)):
            for row in rows:
                assert str(row["id"]) not in self.data["baseline"][table]
                r = self.request(self.meta, "DELETE", f'{self.meta_url}/table/{self.data["tables"][table]}/content/{row["id"]}')
                assert r.is_success, f"Fixture cleanup failed: HTTP {r.status_code}"
        self.verify_existing_records()
        self.path.unlink(missing_ok=True)
        print(json.dumps({"fixtures": "removed"}), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-temporary-records", action="store_true", required=True)
    parser.add_argument("--keep-fixtures", action="store_true")
    parser.add_argument("--cleanup", action="store_true")
    parser.add_argument("--fixture-file", type=Path, default=Path(".venv/pet-selection-fixtures.json"))
    args = parser.parse_args()
    verification = LiveVerification(args.fixture_file)
    try:
        if args.cleanup:
            verification.data = json.loads(args.fixture_file.read_text(encoding="utf-8"))
            verification.cleanup()
        else:
            try:
                verification.prepare()
                verification.run()
            finally:
                if verification.data["tables"] and (not args.keep_fixtures or sys.exc_info()[0]):
                    verification.cleanup()
    finally:
        verification.api.close()
        verification.meta.close()


if __name__ == "__main__":
    main()
