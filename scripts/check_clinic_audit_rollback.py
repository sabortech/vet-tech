"""Força colisão na auditoria em função de diagnóstico isolada e confirma rollback."""
import json
from pathlib import Path
import secrets
import subprocess
import sys

from animal_catalog import XanoStore


def main():
    if sys.argv[1:] != ["--confirm-development", "167758"]:
        raise RuntimeError("Confirme explicitamente o workspace de desenvolvimento 167758.")
    store = XanoStore("vetech", 167758)
    marker = "qa-audit-" + secrets.token_hex(8)
    admins = [row for row in store.pages(store.url("clinica_admin")) if row.get("nome") == "Administração de teste" and row.get("ativo") is True]
    species = store.pages(store.url("especie"))
    if len(admins) != 1 or not species:
        raise RuntimeError("Administrador ou catálogo de teste indisponível.")
    fixture = Path(__file__).resolve().parents[1] / "tests/fixtures/clinic_audit_rollback.xs"
    function_id = None
    try:
        created = subprocess.run(["xano.cmd", "function", "create", "-w", "167758", "-f", str(fixture), "-o", "json"], capture_output=True, text=True, timeout=90)
        if created.returncode:
            raise RuntimeError("Não foi possível criar a função de diagnóstico isolada.")
        function = json.JSONDecoder().raw_decode(created.stdout.lstrip())[0]
        function_id = function.get("id")
        if not function_id:
            raise RuntimeError("Identificador da função de diagnóstico indisponível.")
        pet, status = store.write("POST", "pet", {"nome": marker + "-base", "especie_id": species[0]["id"], "clinica_id": admins[0]["clinica_id"], "tutor_id": 0})
        if not pet or not pet.get("id"):
            raise RuntimeError(f"Fixture base não criada (HTTP {status}).")
        event, status = store.write("POST", "clinica_adocao_evento", {"clinica_id": admins[0]["clinica_id"], "admin_id": admins[0]["id"], "pet_id": pet["id"], "acao": "cadastro"})
        if not event or not event.get("id"):
            raise RuntimeError(f"Auditoria base não criada (HTTP {status}).")
        payload = {"clinica_id": admins[0]["clinica_id"], "admin_id": admins[0]["id"], "especie_id": species[0]["id"], "existing_event_id": event["id"], "nome": marker + "-rollback"}
        result = subprocess.run(["xano.cmd", "function", "run", "Testing/clinic_audit_rollback", "-w", "167758", "--stdin", "--no-input-check"], input=json.dumps(payload), capture_output=True, text=True, timeout=90)
        response = json.JSONDecoder().raw_decode(result.stdout.lstrip())[0]
        if result.returncode or response.get("status") != "exception":
            raise RuntimeError("A colisão de auditoria não produziu falha controlada.")
        if any(row.get("nome") == marker + "-rollback" for row in store.pages(store.url("pet"))):
            raise RuntimeError("Falha de auditoria deixou pet parcial após rollback.")
        print("PASS: falha na gravação de auditoria reverteu cadastro de pet; tipo:", response.get("exception", {}).get("error_type", "não informado"))
    finally:
        for pet in store.pages(store.url("pet")):
            if pet.get("nome") in (marker + "-base", marker + "-rollback"):
                for event in store.pages(store.url("clinica_adocao_evento")):
                    if event.get("pet_id") == pet["id"]:
                        if not store.request("DELETE", store.url("clinica_adocao_evento") + f"/{event['id']}").is_success:
                            raise RuntimeError("Falha na limpeza de auditoria sintética.")
                if not store.request("DELETE", store.url("pet") + f"/{pet['id']}").is_success:
                    raise RuntimeError("Falha na limpeza de pet sintético.")
        if function_id:
            response = store.request("DELETE", store.base + "/function/" + str(function_id))
            if not response.is_success:
                raise RuntimeError("Não foi possível remover a função de diagnóstico; confira o workspace.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
