"""Teste controlado com pet sintético; remove somente os registros criados aqui."""
import getpass
import secrets
import sys

import httpx
from animal_catalog import XanoStore


def main():
    if len(sys.argv) != 4 or sys.argv[1:3] != ["--confirm-development", "167758"]:
        raise RuntimeError("Confirme explicitamente o workspace de desenvolvimento 167758.")
    email, password = sys.argv[3].strip().lower(), getpass.getpass("Senha da conta de teste: ")
    store = XanoStore("vetech", 167758)
    origin = store.target["origin"]
    base = origin + "/api:H62nB-j2/"
    marker = "Fixture adocao " + secrets.token_hex(8)
    pet_id = None
    try:
        with httpx.Client(timeout=30) as client:
            login = client.post(base + "acesso/login", json={"email": email, "password": password})
            if not login.is_success or login.json().get("perfil") != "clinica":
                raise RuntimeError("Autenticação de teste falhou.")
            headers = {"Authorization": "Bearer " + login.json()["authToken"]}
            catalog = client.get(base + "clinica/catalogo", headers=headers)
            if not catalog.is_success or not catalog.json().get("especies"):
                raise RuntimeError("Catálogo de espécies indisponível.")
            species_id = catalog.json()["especies"][0]["id"]
            invalid_species = client.post(base + "clinica/pets", headers=headers, json={"nome": marker + "-invalido", "especie_id": 2147483647})
            if invalid_species.status_code not in (400, 404, 422):
                raise RuntimeError(f"Espécie inválida não foi rejeitada corretamente (HTTP {invalid_species.status_code}).")
            foreign_breed = next((r for r in catalog.json().get("racas", []) if r.get("especie_id") != species_id), None)
            if foreign_breed:
                invalid_breed = client.post(base + "clinica/pets", headers=headers, json={"nome": marker + "-invalido", "especie_id": species_id, "raca_id": foreign_breed["id"]})
                if invalid_breed.status_code not in (400, 404, 422):
                    raise RuntimeError(f"Raça de outra espécie não foi rejeitada corretamente (HTTP {invalid_breed.status_code}).")
            create = client.post(base + "clinica/pets", headers=headers, json={"nome": marker, "especie_id": species_id})
            if not create.is_success:
                raise RuntimeError(f"Cadastro de pet falhou (HTTP {create.status_code}).")
            pet_id = create.json().get("id")
            if not isinstance(pet_id, int) or create.json().get("disponivel_adocao") is not False:
                raise RuntimeError("Resposta de cadastro incompatível.")
            listed = client.get(base + "clinica/pets", headers=headers)
            if not listed.is_success or not any(p.get("id") == pet_id and p.get("disponivel_adocao") is False for p in listed.json()):
                match = [p for p in listed.json() if p.get("id") == pet_id] if listed.is_success else []
                record = next((p for p in store.pages(store.url("pet")) if p.get("id") == pet_id), {})
                raise RuntimeError(f"Pet cadastrado não aparece como indisponível (HTTP {listed.status_code}, correspondências {len(match)}, vínculo tutor {record.get('tutor_id')}, vínculo clínica presente {bool(record.get('clinica_id'))}).")
            for available in (True, False):
                change = client.post(base + "clinica/disponibilidade", headers=headers, json={"pet_id": pet_id, "disponivel": available})
                if not change.is_success or change.json().get("disponivel_adocao") is not available:
                    raise RuntimeError(f"Atualização de disponibilidade falhou (HTTP {change.status_code}).")
            rows = [row for row in store.pages(store.url("clinica_adocao_evento")) if row.get("pet_id") == pet_id]
            if {row.get("acao") for row in rows} != {"cadastro", "publicacao", "retirada"}:
                raise RuntimeError("Eventos administrativos incompletos.")
        print("PASS: cadastro isolado, disponibilidade inicial, publicação, retirada e auditoria.")
    finally:
        for invalid in [row for row in store.pages(store.url("pet")) if row.get("nome") == marker + "-invalido"]:
            for event in store.pages(store.url("clinica_adocao_evento")):
                if event.get("pet_id") == invalid["id"]:
                    if not store.request("DELETE", store.url("clinica_adocao_evento") + f"/{event['id']}").is_success:
                        raise RuntimeError("Falha ao limpar auditoria sintética inválida.")
            if not store.request("DELETE", store.url("pet") + f"/{invalid['id']}").is_success:
                raise RuntimeError("Falha ao limpar pet sintético inválido.")
        if pet_id is None:
            matches = [row for row in store.pages(store.url("pet")) if row.get("nome") == marker]
            if len(matches) > 1:
                raise RuntimeError("Mais de uma fixture com o marcador; limpeza interrompida.")
            pet_id = matches[0]["id"] if matches else None
        if pet_id is not None:
            matches = [row for row in store.pages(store.url("pet")) if row.get("id") == pet_id and row.get("nome") == marker]
            if len(matches) != 1:
                raise RuntimeError("Identidade da fixture não confirmada; limpeza interrompida.")
            for row in store.pages(store.url("clinica_adocao_evento")):
                if row.get("pet_id") == pet_id:
                    response = store.request("DELETE", store.url("clinica_adocao_evento") + f"/{row['id']}")
                    if not response.is_success:
                        raise RuntimeError("Falha ao limpar auditoria sintética.")
            response = store.request("DELETE", store.url("pet") + f"/{pet_id}")
            if not response.is_success:
                raise RuntimeError("Falha ao limpar pet sintético.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
