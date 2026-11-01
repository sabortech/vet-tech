"""Verifica o contrato publicado com uma conta/pet/vacinas sintéticos isolados.

Exige --development para confirmar o ambiente. Não altera registros anteriores,
não remove consultas ou logs e limpa somente os IDs próprios desta execução.
"""

import argparse
from datetime import datetime, timedelta
import json
from pathlib import Path
import secrets
import sys
import time
from uuid import uuid4
from zoneinfo import ZoneInfo

import httpx

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from animal_catalog import XanoStore, save
from vet_tech.features.dashboard.state import project_pet
from vet_tech.shared.config import get_xano_base_url


def run():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--development", action="store_true", required=True)
    parser.parse_args()
    store = XanoStore("vetech", 167758)
    assert store.target["origin"] == get_xano_base_url(), "Origem configurada difere do perfil"
    today = datetime.now(ZoneInfo("America/Sao_Paulo")).date()
    prefix = "qa-dashboard-dates-" + uuid4().hex[:12]
    folder = ROOT / ".venv/dashboard-dates-live" / prefix
    email = prefix + "@example.invalid"
    password = secrets.token_urlsafe(24)
    ids = {"tutor": [], "reserva_email": [], "pet": [], "vacina": []}
    checks = []
    token = ""
    client = httpx.Client(timeout=30)

    def persist():
        save(folder / "ledger.json", {"prefix": prefix, "created": ids, "checks": checks})

    def check(name, condition):
        checks.append({"name": name, "passed": bool(condition)})
        persist()
        assert condition, "Falha: " + name

    def api(method, group, endpoint, payload=None, expected=200):
        for _ in range(4):
            response = client.request(method, f'{store.target["origin"]}/api:{group}/{endpoint}',
                headers={"Authorization": "Bearer " + token} if token else {}, json=payload)
            if response.status_code != 429:
                break
            time.sleep(3)
        accepted = {200, 201} if expected == 200 else {expected}
        assert response.status_code in accepted, f"HTTP inesperado: {response.status_code}"
        return response.json()

    def create(table, payload):
        row, status = store.write("POST", table, payload)
        assert row and status in (200, 201), f"Não foi possível criar fixture {table}"
        ids[table].append(row["id"])
        persist()
        return row

    try:
        digits = [secrets.randbelow(10) for _ in range(9)]
        for weight in (10, 11):
            remainder = sum(n * (weight - i) for i, n in enumerate(digits)) * 10 % 11
            digits.append(0 if remainder == 10 else remainder)
        api("POST", "H62nB-j2", "tutor/signup", {"nome": prefix, "email": email,
            "password": password, "cpf": "".join(map(str, digits)), "telefone": "00000000000", "endereco": "Fixture sintética"})
        for table in ("tutor", "reserva_email"):
            ids[table] = [r["id"] for r in store.pages(store.url(table)) if r.get("email") == email]
        persist()
        assert len(ids["tutor"]) == 1
        token = api("POST", "H62nB-j2", "acesso/login", {"email": email, "password": password})["authToken"]
        species = store.pages(store.url("especie"))[0]["id"]
        pet = api("POST", "vettech-pets", "pets", {"nome": prefix, "especie_id": species, "data_nasc": "2024-04-03"})
        ids["pet"].append(pet["id"])
        persist()
        vaccine = create("vacina", {"pet_id": pet["id"], "vacina": prefix,
            "data_aplicacao": (today - timedelta(days=30)).isoformat()})
        endpoint = f'tutor/dashboard?pet_id={pet["id"]}'
        row = api("GET", "vettech-clinical", endpoint)
        check("aplicacao_sem_proxima_dose_nao_inventa_evento", project_pet(row, today)["proxima_vacina"] == {"nome": "", "data": ""})
        check("nascimento_preserva_data_civil", row.get("data_nasc") == "2024-04-03")
        changed, status = store.write("PUT", "vacina", {"data_prox_dose": today.isoformat()}, vaccine["id"])
        check("fixture_data_proxima_dose_iso_aceita", status == 200)
        row = api("GET", "vettech-clinical", endpoint)
        save(folder / "private-comparison.json", {"vaccine_after_update": changed, "dashboard": row})
        print(json.dumps({"fixture_next_dose_type": type(changed.get("data_prox_dose")).__name__,
                          "fixture_pet_retained": changed.get("pet_id") == pet["id"],
                          "dashboard_vaccine_count": len(row.get("vacinas", [])),
                          "dashboard_vaccine_date_types": sorted({type(r.get("data_prox_dose")).__name__ for r in row.get("vacinas", [])})}), flush=True)
        check("dashboard_autenticado_retornou_proxima_dose", any(r.get("data_prox_dose") == today.isoformat() for r in row.get("vacinas", [])))
        check("projecao_mostra_hoje_em_formato_brasileiro", project_pet(row, today)["proxima_vacina"] == {"nome": prefix, "data": today.strftime("%d/%m/%Y")})
        create("vacina", {"pet_id": pet["id"], "vacina": prefix + "-futura", "data_aplicacao": today.isoformat(), "data_prox_dose": (today+timedelta(days=10)).isoformat()})
        row = api("GET", "vettech-clinical", endpoint)
        check("menor_data_vence_entre_varias_doses", project_pet(row, today)["proxima_vacina"]["nome"] == prefix)
        token = ""
        api("GET", "vettech-clinical", endpoint, expected=401)
        check("sem_sessao_leitura_negada", True)
    finally:
        # Descobre uma criação de resposta perdida apenas pelo prefixo exclusivo.
        for table in ("tutor", "reserva_email"):
            for row in store.pages(store.url(table)):
                if row.get("email") == email and row["id"] not in ids[table]:
                    ids[table].append(row["id"])
        for row in store.pages(store.url("pet")):
            if row.get("tutor_id") in ids["tutor"] and row.get("nome") == prefix and row["id"] not in ids["pet"]:
                ids["pet"].append(row["id"])
        for row in store.pages(store.url("vacina")):
            if row.get("pet_id") in ids["pet"] and str(row.get("vacina", "")).startswith(prefix) and row["id"] not in ids["vacina"]:
                ids["vacina"].append(row["id"])
        persist()
        for table in ("vacina", "pet", "reserva_email", "tutor"):
            for row_id in ids[table]:
                response = store.request("GET", store.url(table) + f"/{row_id}")
                assert response.is_success, "Não foi possível conferir fixture antes da limpeza"
                row = response.json()
                if table == "vacina":
                    owned = row.get("pet_id") in ids["pet"] and str(row.get("vacina", "")).startswith(prefix)
                elif table == "pet":
                    owned = row.get("nome") == prefix and row.get("tutor_id") in ids["tutor"]
                else:
                    owned = row.get("email") == email
                assert owned, "Fixture não corresponde ao escopo desta execução"
                response = store.request("DELETE", store.url(table) + f"/{row_id}")
                assert response.is_success, "Limpeza de fixture não confirmada"
            remaining = {r["id"] for r in store.pages(store.url(table))}
            check("limpeza_" + table, not remaining.intersection(ids[table]))
        client.close()
        store.client.close()
    save(folder / "result.json", {"checks": checks, "cleaned": True})
    print(json.dumps({"mode": "live-synthetic", "checks": checks, "cleaned": True}))


if __name__ == "__main__":
    run()
