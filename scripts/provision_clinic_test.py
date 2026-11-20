"""Provisiona uma clínica sintética no workspace de desenvolvimento confirmado.

Solicita a senha no terminal sem eco; não grava nem exibe credenciais.
"""
import getpass
import json
import subprocess
import sys

from animal_catalog import XanoStore


def main():
    if len(sys.argv) != 4 or sys.argv[1:3] != ["--confirm-development", "167758"]:
        raise RuntimeError("Confirme explicitamente o workspace de desenvolvimento 167758.")
    email = sys.argv[3].strip().lower()
    password = getpass.getpass("Senha da conta de teste: ")
    if not email or not password:
        raise RuntimeError("Credenciais de teste ausentes.")
    store = XanoStore("vetech", 167758)
    for table in ("clinica_admin", "tutor", "veterinario", "reserva_email"):
        if any(str(row.get("email", "")).strip().lower() == email for row in store.pages(store.url(table))):
            raise RuntimeError("E-mail já cadastrado; nenhuma conta foi alterada.")
    name = "Clínica de Teste - Adoção"
    clinics = [row for row in store.pages(store.url("clinica")) if row.get("nome") == name]
    if len(clinics) > 1:
        raise RuntimeError("Mais de uma clínica de teste encontrada; revise o ambiente.")
    if clinics:
        clinic = clinics[0]
    else:
        clinic, status = store.write("POST", "clinica", {"nome": name})
        if not clinic or not clinic.get("id"):
            raise RuntimeError(f"Não foi possível criar clínica de teste (HTTP {status}).")
    payload = {"clinica_id": clinic["id"], "nome": "Administração de teste", "email": email, "senha": password}
    result = subprocess.run(
        ["xano.cmd", "function", "run", "Identity/create_clinica_admin", "-w", "167758", "--stdin", "--no-input-check"],
        input=json.dumps(payload), text=True, capture_output=True, timeout=90,
    )
    if result.returncode:
        raise RuntimeError("Provisionamento da conta falhou; confira a função interna no Xano.")
    print("Clínica e conta de teste provisionadas; valide o login pela aplicação.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
