"""Verifica uma identidade administrativa sintética inativa no ambiente de teste."""
import secrets
import sys

import httpx
from animal_catalog import XanoStore


def main():
    if sys.argv[1:] != ["--confirm-development", "167758"]:
        raise RuntimeError("Confirme explicitamente o workspace de desenvolvimento 167758.")
    store = XanoStore("vetech", 167758)
    marker = "qa-inactive-" + secrets.token_hex(8)
    email = marker + "@example.invalid"
    password = secrets.token_urlsafe(24)
    clinics = [row for row in store.pages(store.url("clinica")) if row.get("nome") == "Clínica de Teste - Adoção"]
    if len(clinics) != 1:
        raise RuntimeError("Clínica sintética não identificada de forma única.")
    try:
        admin, status = store.write("POST", "clinica_admin", {"nome": marker, "email": email, "senha": password, "ativo": False, "clinica_id": clinics[0]["id"]})
        if not admin or not admin.get("id"):
            raise RuntimeError(f"Não foi possível criar identidade sintética (HTTP {status}).")
        reservation, status = store.write("POST", "reserva_email", {"email": email, "perfil": "clinica", "identidade_id": admin["id"]})
        if not reservation or not reservation.get("id"):
            raise RuntimeError(f"Não foi possível reservar e-mail sintético (HTTP {status}).")
        base = store.target["origin"] + "/api:H62nB-j2/"
        with httpx.Client(timeout=40) as client:
            response = client.post(base + "acesso/login", json={"email": email, "password": password})
            if response.status_code not in (400, 401, 403):
                raise RuntimeError(f"Conta inativa não foi rejeitada corretamente (HTTP {response.status_code}).")
            public_signup = client.post(base + "clinica/signup", json={"nome": marker, "email": email, "password": password})
            if public_signup.status_code != 404:
                raise RuntimeError(f"Cadastro público precisa de revisão (HTTP {public_signup.status_code}).")
        print("PASS: login de conta inativa e cadastro público recusados.")
    finally:
        for table in ("reserva_email", "clinica_admin"):
            for row in store.pages(store.url(table)):
                if row.get("email") == email:
                    if not store.request("DELETE", store.url(table) + f"/{row['id']}").is_success:
                        raise RuntimeError("Falha ao remover identidade sintética.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
