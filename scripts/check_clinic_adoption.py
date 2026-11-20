"""Valida transferência e concorrência usando somente registros sintéticos identificados."""
from concurrent.futures import ThreadPoolExecutor
import getpass
import json
import secrets
import subprocess
import sys
import time

import httpx
from animal_catalog import XanoStore


def cpf():
    digits = [secrets.randbelow(10) for _ in range(9)]
    for length in (9, 10):
        remainder = sum(d * w for d, w in zip(digits, range(length + 1, 1, -1))) % 11
        digits.append(0 if remainder < 2 else 11 - remainder)
    return "".join(map(str, digits))


def request(client, method, url, **kwargs):
    for attempt in range(6):
        response = client.request(method, url, **kwargs)
        if response.status_code != 429:
            return response
        time.sleep(min(30, 5 * (attempt + 1)))
    return response


def main():
    if len(sys.argv) != 4 or sys.argv[1:3] != ["--confirm-development", "167758"]:
        raise RuntimeError("Confirme explicitamente o workspace de desenvolvimento 167758.")
    email, password = sys.argv[3].strip().lower(), getpass.getpass("Senha da conta de teste: ")
    store = XanoStore("vetech", 167758)
    origin = store.target["origin"]
    auth = origin + "/api:H62nB-j2/"
    pets_api = origin + "/api:vettech-pets/"
    marker = "qa-adocao-" + secrets.token_hex(8)
    emails = [marker + "-a@example.invalid", marker + "-b@example.invalid"]
    pet_id = None
    try:
        with httpx.Client(timeout=40) as client:
            login = request(client, "POST", auth + "acesso/login", json={"email": email, "password": password})
            if not login.is_success or login.json().get("perfil") != "clinica":
                raise RuntimeError("Falha no login da clínica de teste.")
            clinic_headers = {"Authorization": "Bearer " + login.json()["authToken"]}
            admins = [a for a in store.pages(store.url("clinica_admin")) if a.get("email") == email and a.get("id") == login.json().get("identidade_id")]
            if len(admins) != 1 or not admins[0].get("clinica_id"):
                raise RuntimeError("Clínica de teste não identificada.")
            other_clinic, status = store.write("POST", "clinica", {"nome": marker + "-clinica"})
            if not other_clinic or not other_clinic.get("id"):
                raise RuntimeError(f"Fixture de outra clínica falhou: HTTP {status}.")
            vet_ids = []
            for index, clinic_id in enumerate((admins[0]["clinica_id"], other_clinic["id"], 0)):
                vet, status = store.write("POST", "veterinario", {"nome": marker + "-vet-" + str(index), "email": marker + "-vet-" + str(index) + "@example.invalid", "crmv": marker[-12:] + str(index), "crmv_uf": "SP", "clinica_id": clinic_id})
                if not vet or not vet.get("id"):
                    raise RuntimeError(f"Fixture veterinária falhou: HTTP {status}.")
                vet_ids.append(vet["id"])
            vet_list = request(client, "GET", auth + "clinica/veterinarios", headers=clinic_headers)
            vet_ids_visible = {v.get("id") for v in vet_list.json()} if vet_list.is_success else set()
            if vet_ids[0] not in vet_ids_visible or vet_ids[1] in vet_ids_visible or vet_ids[2] in vet_ids_visible:
                raise RuntimeError("Listagem não isolou veterinários vinculados à clínica.")
            catalog = request(client, "GET", auth + "clinica/catalogo", headers=clinic_headers)
            if not catalog.is_success or not catalog.json().get("especies"):
                raise RuntimeError("Catálogo indisponível.")
            foreign_pet, status = store.write("POST", "pet", {"nome": marker + "-outro", "especie_id": catalog.json()["especies"][0]["id"], "clinica_id": other_clinic["id"], "tutor_id": 0, "disponivel_adocao": False})
            if not foreign_pet or not foreign_pet.get("id"):
                raise RuntimeError(f"Fixture de pet de outra clínica falhou: HTTP {status}.")
            foreign_list = request(client, "GET", auth + "clinica/pets", headers=clinic_headers)
            if not foreign_list.is_success or any(row.get("id") == foreign_pet["id"] for row in foreign_list.json()):
                raise RuntimeError("Pet de outra clínica apareceu na listagem.")
            foreign_update = request(client, "POST", auth + "clinica/disponibilidade", headers=clinic_headers, json={"pet_id": foreign_pet["id"], "disponivel": True})
            if foreign_update.is_success or foreign_update.status_code == 429:
                raise RuntimeError("Não foi possível confirmar a rejeição de pet de outra clínica.")
            create = request(client, "POST", auth + "clinica/pets", headers=clinic_headers, json={"nome": marker, "especie_id": catalog.json()["especies"][0]["id"]})
            if not create.is_success:
                raise RuntimeError(f"Cadastro de fixture falhou: HTTP {create.status_code}.")
            pet_id = create.json()["id"]
            vaccine, status = store.write("POST", "vacina", {"pet_id": pet_id, "veterinario_id": vet_ids[0], "vacina": marker, "data_aplicacao": "2026-01-01", "origem_linha": marker})
            if not vaccine or not vaccine.get("id"):
                raise RuntimeError(f"Fixture clínica falhou: HTTP {status}.")
            authorization, status = store.write("POST", "acesso_autorizado", {"pet_id": pet_id, "veterinario_id": vet_ids[0], "status": "ativo"})
            if not authorization or not authorization.get("id"):
                raise RuntimeError(f"Fixture de autorização falhou: HTTP {status}.")
            clinical = subprocess.run(["xano.cmd", "function", "run", "records/require_access", "-w", "167758", "--stdin", "--no-input-check"], input=json.dumps({"pet_id": pet_id, "veterinario_id": vet_ids[0], "acao": "visualizacao"}), text=True, capture_output=True, timeout=90)
            try:
                clinical_result = json.JSONDecoder().raw_decode(clinical.stdout.lstrip())[0]
            except ValueError:
                raise RuntimeError("Não foi possível verificar a proteção clínica.") from None
            if clinical.returncode or clinical_result.get("status") != "exception" or clinical_result.get("exception", {}).get("error_type") != "ERROR_CODE_ACCESS_DENIED":
                raise RuntimeError("Pet sem tutor recebeu acesso clínico indevido.")
            pub = request(client, "POST", auth + "clinica/disponibilidade", headers=clinic_headers, json={"pet_id": pet_id, "disponivel": True})
            if not pub.is_success:
                raise RuntimeError(f"Publicação de fixture falhou: HTTP {pub.status_code}.")
            tokens = []
            for address in emails:
                pwd = secrets.token_urlsafe(24)
                signup = request(client, "POST", auth + "tutor/signup", json={"email": address, "password": pwd, "nome": marker, "cpf": cpf(), "telefone": "11999999999", "endereco": "Fixture sintética"})
                if not signup.is_success:
                    raise RuntimeError(f"Cadastro de tutor sintético falhou: HTTP {signup.status_code}.")
                result = request(client, "POST", auth + "acesso/login", json={"email": address, "password": pwd})
                if not result.is_success or result.json().get("perfil") != "tutor":
                    raise RuntimeError("Login do tutor sintético falhou.")
                tokens.append(result.json()["authToken"])
            for token in tokens:
                headers = {"Authorization": "Bearer " + token}
                listing = request(client, "GET", pets_api + "adoption", headers=headers)
                if not listing.is_success or not any(row.get("id") == pet_id for row in listing.json()):
                    raise RuntimeError(f"Pet publicado ausente da adoção: HTTP {listing.status_code}.")
                if request(client, "GET", pets_api + f"pets/{pet_id}", headers=headers).is_success:
                    raise RuntimeError("Tutor leu pet antes da adoção.")
            def adopt(token):
                return httpx.post(pets_api + "adoption", headers={"Authorization": "Bearer " + token}, json={"pet_id": pet_id}, timeout=40)
            with ThreadPoolExecutor(max_workers=2) as pool:
                outcomes = list(pool.map(adopt, tokens))
            winners = [index for index, response in enumerate(outcomes) if response.is_success]
            if len(winners) != 1 or any(response.status_code == 429 for response in outcomes):
                raise RuntimeError("Concorrência não produziu exatamente um adotante: " + ",".join(str(x.status_code) for x in outcomes))
            winner = winners[0]
            winner_headers = {"Authorization": "Bearer " + tokens[winner]}
            loser_headers = {"Authorization": "Bearer " + tokens[1 - winner]}
            if not request(client, "GET", pets_api + f"pets/{pet_id}", headers=winner_headers).is_success:
                raise RuntimeError("Tutor vencedor não consegue consultar o pet.")
            if request(client, "GET", pets_api + f"pets/{pet_id}", headers=loser_headers).is_success:
                raise RuntimeError("Tutor perdedor consegue consultar o pet.")
            clinic_pets = request(client, "GET", auth + "clinica/pets", headers=clinic_headers)
            if not clinic_pets.is_success or any(row.get("id") == pet_id for row in clinic_pets.json()):
                raise RuntimeError("Pet adotado continua vinculado à clínica.")
            if request(client, "POST", auth + "clinica/disponibilidade", headers=clinic_headers, json={"pet_id": pet_id, "disponivel": True}).is_success:
                raise RuntimeError("Clínica conseguiu republicar pet adotado.")
            rows = [p for p in store.pages(store.url("pet")) if p.get("id") == pet_id and p.get("nome") == marker]
            if len(rows) != 1 or rows[0].get("clinica_id") not in (None, 0) or not rows[0].get("tutor_id") or rows[0].get("disponivel_adocao"):
                raise RuntimeError(f"Vínculos persistidos após adoção são incompatíveis (registro={len(rows)}, clínica_presente={bool(rows and rows[0].get('clinica_id'))}, tutor_presente={bool(rows and rows[0].get('tutor_id'))}, disponível={rows[0].get('disponivel_adocao') if rows else 'ausente'}).")
            recorded_vaccine = [v for v in store.pages(store.url("vacina")) if v.get("id") == vaccine["id"] and v.get("pet_id") == pet_id and v.get("vacina") == marker]
            recorded_access = [a for a in store.pages(store.url("acesso_autorizado")) if a.get("id") == authorization["id"] and a.get("pet_id") == pet_id]
            if len(recorded_vaccine) != 1 or len(recorded_access) != 1 or recorded_access[0].get("status") != "revogado":
                raise RuntimeError("Histórico não preservado ou autorização anterior não revogada.")
            second = request(client, "POST", auth + "clinica/pets", headers=clinic_headers, json={"nome": marker + "-race", "especie_id": catalog.json()["especies"][0]["id"]})
            if not second.is_success:
                raise RuntimeError("Não foi possível criar segunda fixture concorrente.")
            second_id = second.json()["id"]
            published = request(client, "POST", auth + "clinica/disponibilidade", headers=clinic_headers, json={"pet_id": second_id, "disponivel": True})
            if not published.is_success:
                raise RuntimeError("Não foi possível publicar segunda fixture concorrente.")
            def withdraw():
                return httpx.post(auth + "clinica/disponibilidade", headers=clinic_headers, json={"pet_id": second_id, "disponivel": False}, timeout=40)
            def adopt_second():
                return httpx.post(pets_api + "adoption", headers=winner_headers, json={"pet_id": second_id}, timeout=40)
            with ThreadPoolExecutor(max_workers=2) as pool:
                withdrawal = pool.submit(withdraw)
                adoption = pool.submit(adopt_second)
                outcomes = [withdrawal.result(), adoption.result()]
            if sum(outcome.is_success for outcome in outcomes) != 1 or any(outcome.status_code == 429 for outcome in outcomes):
                raise RuntimeError("Concorrência entre retirada e adoção inconclusiva: " + ",".join(str(x.status_code) for x in outcomes))
        print("PASS: listagem, privacidade antes da adoção, concorrência e transferência exclusiva.")
    finally:
        # Descobre somente registros identificados pelo marcador único desta execução.
        matches = [p for p in store.pages(store.url("pet")) if p.get("nome") == marker]
        if len(matches) > 1 or (pet_id is not None and matches and matches[0].get("id") != pet_id):
            raise RuntimeError("Identidade da fixture divergente; limpeza interrompida.")
        if matches:
            target = matches[0]["id"]
            for table in ("clinica_adocao_evento", "clinical_lock", "vacina", "acesso_autorizado"):
                for row in store.pages(store.url(table)):
                    if row.get("pet_id") == target:
                        if not store.request("DELETE", store.url(table) + f"/{row['id']}").is_success:
                            raise RuntimeError("Falha na limpeza de dependências sintéticas.")
            if not store.request("DELETE", store.url("pet") + f"/{target}").is_success:
                raise RuntimeError("Falha na limpeza do pet sintético.")
        for foreign_pet in store.pages(store.url("pet")):
            if foreign_pet.get("nome") in (marker + "-outro", marker + "-race"):
                for event in store.pages(store.url("clinica_adocao_evento")):
                    if event.get("pet_id") == foreign_pet["id"]:
                        if not store.request("DELETE", store.url("clinica_adocao_evento") + f"/{event['id']}").is_success:
                            raise RuntimeError("Falha na limpeza da auditoria concorrente.")
                if not store.request("DELETE", store.url("pet") + f"/{foreign_pet['id']}").is_success:
                    raise RuntimeError("Falha na limpeza de pet sintético de outra clínica.")
        for vet in store.pages(store.url("veterinario")):
            if vet.get("nome", "").startswith(marker + "-vet-") and vet.get("email", "").startswith(marker + "-vet-"):
                if not store.request("DELETE", store.url("veterinario") + f"/{vet['id']}").is_success:
                    raise RuntimeError("Falha na limpeza de veterinário sintético.")
        for clinic in store.pages(store.url("clinica")):
            if clinic.get("nome") == marker + "-clinica":
                if not store.request("DELETE", store.url("clinica") + f"/{clinic['id']}").is_success:
                    raise RuntimeError("Falha na limpeza de clínica sintética.")
        tutors = [t for t in store.pages(store.url("tutor")) if t.get("email") in emails and t.get("nome") == marker]
        for tutor in tutors:
            events = [e for e in store.pages(store.url("welcome_email_event")) if e.get("profile") == "tutor" and e.get("identity_id") == tutor["id"]]
            for event in events:
                for attempt in store.pages(store.url("welcome_email_attempt")):
                    if attempt.get("event_id") == event["id"]:
                        if not store.request("DELETE", store.url("welcome_email_attempt") + f"/{attempt['id']}").is_success:
                            raise RuntimeError("Falha na limpeza de tentativa sintética.")
                if not store.request("DELETE", store.url("welcome_email_event") + f"/{event['id']}").is_success:
                    raise RuntimeError("Falha na limpeza de evento sintético.")
            for reservation in store.pages(store.url("reserva_email")):
                if reservation.get("email") == tutor.get("email"):
                    if not store.request("DELETE", store.url("reserva_email") + f"/{reservation['id']}").is_success:
                        raise RuntimeError("Falha na limpeza de reserva sintética.")
            if not store.request("DELETE", store.url("tutor") + f"/{tutor['id']}").is_success:
                raise RuntimeError("Falha na limpeza de tutor sintético.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
