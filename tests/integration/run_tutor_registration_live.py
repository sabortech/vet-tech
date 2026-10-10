"""Teste externo do cadastro no Xano de desenvolvimento com fixtures temporarias.

Executar somente em desenvolvimento:
python tests/integration/run_tutor_registration_live.py --profile vettech --allow-temporary-accounts

Usa o perfil do Xano CLI; nunca imprime credenciais, CPFs ou registros pessoais.
Remove somente registros cujo email tenha o identificador desta execucao.
"""

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import secrets
import time
import uuid

import httpx
import yaml


class RegistrationVerification:
    def __init__(self, profile):
        self.base = profile["instance_origin"].rstrip("/")
        self.meta_base = f'{self.base}/api:meta/workspace/{profile["workspace"]}'
        self.api_base = f"{self.base}/api:H62nB-j2"
        self.meta = httpx.Client(timeout=40, headers={"Authorization": "Bearer " + profile["access_token"]})
        self.api = httpx.Client(timeout=40)
        self.marker = "vettech-test-" + uuid.uuid4().hex
        self.password = secrets.token_urlsafe(24)
        self.tables = {}
        self.owned_emails = set()
        self.used_cpfs = set()
        self.results = []
        self.initial_ids = {}

    def request(self, client, method, url, **kwargs):
        # So repete rejeicoes explicitas por rate limit; nao repete POST incerto.
        for attempt in range(5):
            response = client.request(method, url, **kwargs)
            if response.status_code != 429:
                return response
            time.sleep(min(2 ** (attempt + 1), 20))
        raise RuntimeError("Rate limit persistente do Xano")

    def records(self, table):
        result = []
        page = 1
        while True:
            response = self.request(self.meta, "GET", f"{self.meta_base}/table/{self.tables[table]}/content", params={"page": page, "per_page": 100})
            if not response.is_success:
                raise RuntimeError(f"Nao foi possivel auditar a tabela {table}: HTTP {response.status_code}")
            data = response.json()
            items = data if isinstance(data, list) else data.get("items", [])
            result.extend(items)
            if isinstance(data, list) or not data.get("nextPage"):
                break
            page = data["nextPage"]
        return result

    def fixtures(self, table):
        return [row for row in self.records(table) if row.get("email") in self.owned_emails]

    def assert_counts(self, expected):
        assert len(self.fixtures("tutor")) == expected, "Contagem inesperada de fixtures em tutor"
        assert not self.fixtures("user"), "O cadastro criou uma identidade generica em user"

    def note(self, scenario):
        self.results.append(scenario)
        print(json.dumps({"scenario": scenario, "status": "passed"}, ensure_ascii=False), flush=True)

    def cpf(self, leading_zero=False):
        while True:
            digits = [0 if leading_zero else 9] + [secrets.randbelow(10) for _ in range(8)]
            for length in (9, 10):
                remainder = sum(d * w for d, w in zip(digits, range(length + 1, 1, -1))) % 11
                digits.append(0 if remainder < 2 else 11 - remainder)
            cpf = "".join(map(str, digits))
            if cpf not in self.used_cpfs and len(set(cpf)) != 1:
                self.used_cpfs.add(cpf)
                return cpf

    def payload(self, label, cpf=None):
        email = f"{self.marker}-{label}@example.invalid"
        self.owned_emails.add(email)
        return {"nome": "Fixture automatizada VetTech", "cpf": cpf or self.cpf(), "email": email, "telefone": "11999999999", "endereco": "Endereco ficticio de teste", "password": self.password}

    def signup(self, payload):
        return self.request(self.api, "POST", f"{self.api_base}/tutor/signup", json=payload)

    def rejected(self, payload, expected_count, expected_message=None):
        response = self.signup(payload)
        assert response.status_code == 400, f"Rejeicao esperada como HTTP 400; obtido {response.status_code}"
        body = response.json()
        assert not body.get("success"), "Rejeicao informou sucesso"
        assert "password" not in body and "authToken" not in body, "Rejeicao expos credenciais"
        if expected_message:
            assert body.get("message") == expected_message, "Mensagem de validacao inesperada"
        self.assert_counts(expected_count)

    def prepare(self):
        response = self.request(self.meta, "GET", f"{self.meta_base}/table", params={"per_page": 100})
        response.raise_for_status()
        data = response.json()
        items = data if isinstance(data, list) else data.get("items", [])
        self.tables = {table["name"]: table["id"] for table in items if table["name"] in ("tutor", "user")}
        assert len(self.tables) == 2, "Tabelas tutor/user nao encontradas"
        for name in self.tables:
            rows = self.records(name)
            self.initial_ids[name] = {row["id"] for row in rows}
            if name == "tutor":
                self.used_cpfs.update(row.get("cpf") for row in rows)
        self.note("preflight_auditoria_disponivel")

    def run(self):
        self.prepare()
        first = self.payload("normal")
        response = self.signup(first)
        assert response.status_code == 200, f"Cadastro valido falhou: HTTP {response.status_code}"
        assert response.json() == {"success": True}, "Resposta do cadastro deve conter somente confirmacao"
        self.assert_counts(1)
        self.note("cadastro_valido_sem_pontuacao_sem_token_ou_senha")

        second = self.payload("formatado", self.cpf(leading_zero=True))
        digits = second["cpf"]
        second["cpf"] = f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"
        response = self.signup(second)
        assert response.status_code == 200, f"Cadastro formatado falhou: HTTP {response.status_code}"
        self.assert_counts(2)
        stored = next(row for row in self.fixtures("tutor") if row["email"] == second["email"])
        assert stored["cpf"] == digits, "CPF nao foi normalizado ou perdeu o zero inicial"
        self.note("cpf_formatado_normalizado_preservando_zero_inicial")

        for field in first:
            payload = self.payload("sem-" + field)
            del payload[field]
            self.rejected(payload, 2)
            self.note("campo_ausente_" + field + "_sem_conta_parcial")

        for label, cpf in [("curto", "123"), ("repetido", "11111111111"), ("verificador", "52998224724"), ("letras", "5299822472a")]:
            payload = self.payload("cpf-" + label, cpf)
            self.rejected(payload, 2, "Informe um CPF válido.")
            self.note("cpf_" + label + "_rejeitado_sem_conta_parcial")

        duplicate = self.payload("cpf-duplicado", first["cpf"])
        self.rejected(duplicate, 2, "Já existe uma conta com esse CPF ou e-mail.")
        self.note("cpf_duplicado_rejeitado_sem_conta_parcial")
        duplicate = self.payload("email-duplicado")
        duplicate["email"] = first["email"].upper()
        self.rejected(duplicate, 2, "Já existe uma conta com esse CPF ou e-mail.")
        self.note("email_duplicado_normalizado_rejeitado_sem_conta_parcial")

        response = self.request(self.api, "POST", f"{self.api_base}/tutor/login", json={"email": first["email"].upper(), "password": self.password})
        assert response.status_code == 200 and response.json().get("authToken"), "Login real apos cadastro falhou"
        assert "password" not in response.json(), "Login expos senha"
        self.note("login_real_apos_cadastro")
        response = self.request(self.api, "POST", f"{self.api_base}/tutor/login", json={"email": first["email"], "password": "SenhaIncorretaDeTeste"})
        assert response.status_code in (401, 403), "Login aceitou senha incorreta"
        self.assert_counts(2)
        self.note("senha_incorreta_rejeitada")

        # As consultas de duplicidade podem concorrer; o indice deve impedir
        # a segunda insercao, inclusive quando ambas passaram pelas consultas.
        persistence_failure = False
        expected = 2
        for attempt in range(3):
            payload = self.payload("concorrencia-" + str(attempt))
            with ThreadPoolExecutor(max_workers=4) as pool:
                responses = list(pool.map(lambda _: self.signup(payload), range(4)))
            assert sum(r.status_code == 200 for r in responses) == 1, "Concorrencia nao criou exatamente uma conta"
            expected += 1
            self.assert_counts(expected)
            failed = [r for r in responses if r.status_code != 200]
            assert all(r.status_code in (400, 409, 500) for r in failed), "Erro inesperado na concorrencia"
            for rejected in failed:
                body = rejected.json()
                message = str(body.get("message", "")).lower()
                unique_failure = any(text in message for text in (
                    "duplicate", "duplicated", "unique constraint", "already exists",
                    "sqlstate[23505]", "sqlstate[23000]",
                ))
                if unique_failure and (rejected.status_code == 500 or body.get("code") == "ERROR_FATAL"):
                    persistence_failure = True
            self.note("concorrencia_" + str(attempt + 1) + "_uma_conta_sem_user")
            if persistence_failure:
                break
        assert persistence_failure, "A corrida nao atingiu uma falha de persistencia; nao considerar esse cenario concluido"
        self.note("falha_real_de_persistencia_sem_conta_parcial")

    def cleanup(self):
        if not self.tables or not self.initial_ids:
            return
        for table in self.tables:
            for row in self.fixtures(table):
                assert row["id"] not in self.initial_ids[table], "Recusa remover registro anterior ao teste"
                assert row.get("email") in self.owned_emails and row["email"].startswith(self.marker + "-"), "Recusa remover registro nao pertencente ao teste"
                url = f'{self.meta_base}/table/{self.tables[table]}/content/{row["id"]}'
                response = self.request(self.meta, "DELETE", url)
                assert response.is_success, f"Limpeza de fixture falhou: HTTP {response.status_code}"
            assert not self.fixtures(table), "Restaram fixtures no banco"
            remaining_ids = {row["id"] for row in self.records(table)}
            assert self.initial_ids[table] <= remaining_ids, "Um registro preexistente desapareceu durante o teste"
        self.note("fixtures_removidas_registros_preexistentes_preservados")

    def close(self):
        self.meta.close()
        self.api.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--allow-temporary-accounts", action="store_true", required=True)
    args = parser.parse_args()
    credentials = Path(os.getenv("XANO_CONFIG", str(Path.home() / ".xano/credentials.yaml")))
    profile = yaml.safe_load(credentials.read_text(encoding="utf-8"))["profiles"][args.profile]
    verification = RegistrationVerification(profile)
    failed = False
    try:
        verification.run()
    except (AssertionError, RuntimeError) as error:
        failed = True
        print(json.dumps({"status": "failed", "message": str(error)}, ensure_ascii=False), flush=True)
    except Exception as error:
        failed = True
        print(json.dumps({"status": "failed", "error_type": type(error).__name__}), flush=True)
    finally:
        try:
            verification.cleanup()
        except Exception as error:
            failed = True
            print(json.dumps({"stage": "cleanup", "status": "failed", "error_type": type(error).__name__}), flush=True)
        verification.close()
    print(json.dumps({"passed_scenarios": len(verification.results), "status": "failed" if failed else "passed"}), flush=True)
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
