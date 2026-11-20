"""Verifica login e isolamento básico da conta de teste sem imprimir credenciais."""
import getpass
import sys

import httpx
from animal_catalog import XanoStore


def main():
    if len(sys.argv) != 4 or sys.argv[1:3] != ["--confirm-development", "167758"]:
        raise RuntimeError("Confirme explicitamente o workspace de desenvolvimento 167758.")
    email = sys.argv[3].strip().lower()
    password = getpass.getpass("Senha da conta de teste: ")
    store = XanoStore("vetech", 167758)
    base = store.target["origin"] + "/api:H62nB-j2/"
    with httpx.Client(timeout=30) as client:
        invalid = client.post(base + "acesso/login", json={"email": email, "password": password + "-invalid"})
        if invalid.status_code not in (400, 401, 403):
            raise RuntimeError(f"Não foi possível confirmar rejeição de senha incorreta (HTTP {invalid.status_code}).")
        login = client.post(base + "acesso/login", json={"email": email, "password": password})
        if not login.is_success:
            raise RuntimeError(f"Login da clínica falhou (HTTP {login.status_code}).")
        identity = login.json()
        if identity.get("perfil") != "clinica" or not identity.get("authToken"):
            raise RuntimeError("Login não retornou uma sessão de clínica válida.")
        headers = {"Authorization": "Bearer " + identity["authToken"]}
        for path in ("clinica/me", "clinica/catalogo", "clinica/veterinarios", "clinica/pets"):
            result = client.get(base + path, headers=headers)
            if not result.is_success:
                raise RuntimeError(f"Falha ao consultar {path} (HTTP {result.status_code}).")
            anonymous = client.get(base + path)
            if anonymous.status_code not in (401, 403):
                raise RuntimeError(f"Não foi possível confirmar rejeição anônima em {path} (HTTP {anonymous.status_code}).")
    print("PASS: login compartilhado, credenciais inválidas e negação anônima.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
