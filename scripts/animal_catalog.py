"""Carga administrativa de espécies/raças. Simulação é o modo padrão.

Credenciais vêm do perfil Xano; arquivos operacionais ficam em .venv ignorado.
Não repete escritas de resultado incerto. Consulte xano/seed/README.md.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys
import time
import unicodedata

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent))
from profile_migration_inventory import ROOT, cli_profile, digest

SEED = ROOT / "xano/seed/animal-catalog.json"
PRIVATE = ROOT / ".venv/animal-catalog"
CATALOGS = ("especie", "raca")
REFERENCES = ("pet", "veterinario_especie")


class CatalogError(RuntimeError):
    pass


def normalize(value):
    if not isinstance(value, str) or not value.strip():
        raise CatalogError("Nome vazio ou inválido")
    return " ".join(unicodedata.normalize("NFC", value).split()).casefold()


def validate_seed(seed):
    if not seed.get("version") or not seed.get("sources"):
        raise CatalogError("Versão/fontes obrigatórias")
    keys, species_keys = set(), set()
    aliases = {}
    for kind in ("species", "breeds"):
        if not isinstance(seed.get(kind), list) or not seed[kind]:
            raise CatalogError("Conjunto vazio")
        for item in seed[kind]:
            key = item.get("key", "")
            if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", key) or key in keys:
                raise CatalogError("Chave estável inválida ou repetida")
            keys.add(key)
            if item.get("source") not in seed["sources"]:
                raise CatalogError("Fonte ausente")
            if not seed["sources"][item["source"]].startswith("https://"):
                raise CatalogError("Fonte deve usar HTTPS")
            scope = "species" if kind == "species" else item.get("species")
            if kind == "breeds" and scope not in species_keys:
                raise CatalogError("Raça sem espécie válida")
            if not isinstance(item.get("aliases"), list):
                raise CatalogError("Mapeamento explícito de sinônimos obrigatório")
            for value in [item["name"], *item["aliases"]]:
                token = normalize(value)
                if token in ("srd", "sem raça definida", "sem raca definida"):
                    raise CatalogError("SRD é ausência de raça")
                alias = (scope, token)
                if alias in aliases:
                    raise CatalogError("Nome/sinônimo normalizado duplicado ou ambíguo")
                aliases[alias] = key
            if kind == "species":
                species_keys.add(key)
    return seed


def build_plan(seed, records):
    """Não escreve; rejeita ambiguidades inclusive fora do conjunto selecionado."""
    validate_seed(seed)
    species_rows = {row["id"]: row for row in records["especie"]}
    for table in CATALOGS:
        seen = set()
        for row in records[table]:
            if table == "raca" and row.get("especie_id") not in species_rows:
                raise CatalogError("Raça existente sem espécie válida")
            key = (row.get("especie_id"), normalize(row.get("nome")))
            if key in seen:
                raise CatalogError("Duplicidade normalizada no banco; revisão necessária")
            seen.add(key)
            technical = row.get("nome_normalizado")
            if technical not in (None, "", normalize(row["nome"])):
                raise CatalogError("Chave normalizada existente diverge do nome")
    plan, species_ids = [], {}
    for kind, table in (("species", "especie"), ("breeds", "raca")):
        for item in seed[kind]:
            names = {normalize(n) for n in [item["name"], *item["aliases"]]}
            species_id = species_ids.get(item.get("species"))
            matches = [row for row in records[table]
                       if normalize(row["nome"]) in names
                       and (table == "especie" or
                            (species_id is not None and row["especie_id"] == species_id))]
            if len(matches) > 1:
                raise CatalogError("Sinônimos correspondem a múltiplos IDs; aplicação bloqueada")
            row = matches[0] if matches else None
            if table == "especie":
                species_ids[item["key"]] = row["id"] if row else None
            plan.append({"table": table, "key": item["key"], "name": item["name"],
                         "species": item.get("species"), "id": row["id"] if row else None,
                         "existing_name": row["nome"] if row else None,
                         "action": "reuse" if row else "create"})
    return plan


class XanoStore:
    def __init__(self, profile_name, workspace):
        os.environ["XANO_PROFILE"] = profile_name
        profile = cli_profile()
        if str(profile["workspace"]) != str(workspace):
            raise CatalogError("Workspace não corresponde ao perfil selecionado")
        origin = profile["instance_origin"].rstrip("/")
        if not origin.startswith("https://"):
            raise CatalogError("HTTPS obrigatório")
        self.target = {"origin": origin, "workspace": workspace,
                       "profile": profile_name, "tenant": os.getenv("XANO_TENANT", "")}
        self.base = f"{origin}/api:meta/workspace/{workspace}"
        headers = {"Authorization": "Bearer " + profile["access_token"]}
        if self.target["tenant"]:
            headers["X-Tenant"] = self.target["tenant"]
        self.client = httpx.Client(timeout=40, headers=headers)
        self.tables = {row["name"]: row for row in self.pages(self.base + "/table")}
        if not set((*CATALOGS, *REFERENCES)) <= self.tables.keys():
            raise CatalogError("Tabelas de catálogo/referências ausentes")

    def request(self, method, url, **kwargs):
        # Só 429 explícito garante que a escrita foi recusada antes da execução.
        for attempt in range(4):
            response = self.client.request(method, url, **kwargs)
            if response.status_code != 429:
                return response
            if attempt < 3:
                time.sleep(min(20, 5 * (attempt + 1)))
        raise CatalogError("Limite do Xano; retome pelo manifesto")

    def pages(self, url):
        rows, page, seen = [], 1, set()
        while page:
            if page in seen:
                raise CatalogError("Paginação repetida")
            seen.add(page)
            response = self.request("GET", url, params={"page": page, "per_page": 100})
            if not response.is_success:
                raise CatalogError(f"Leitura administrativa: HTTP {response.status_code}")
            body = response.json()
            if isinstance(body, list):
                return rows + body
            if not isinstance(body, dict) or not isinstance(body.get("items"), list):
                raise CatalogError("Paginação inválida")
            rows.extend(body["items"])
            page = body.get("nextPage")
        return rows

    def url(self, table):
        return f'{self.base}/table/{self.tables[table]["id"]}/content'

    def read(self):
        return {name: self.pages(self.url(name)) for name in (*CATALOGS, *REFERENCES)}

    def ensure_indexes(self):
        for table, names in (("especie", {"nome_normalizado"}),
                             ("raca", {"especie_id", "nome_normalizado"})):
            url = f'{self.base}/table/{self.tables[table]["id"]}/index'
            response = self.request("GET", url)
            if not response.is_success:
                raise CatalogError("Não foi possível confirmar índices únicos publicados")
            body = response.json()
            indexes = body if isinstance(body, list) else body.get("index", body.get("indexes", []))
            if not any("unique" in str(index.get("type", ""))
                       and {field["name"] for field in index.get("fields", index.get("field", []))} == names
                       for index in indexes):
                raise CatalogError(f"Índice único normalizado não publicado: {table}")

    def write(self, method, table, row, row_id=None):
        url = self.url(table) + (f"/{row_id}" if row_id is not None else "")
        response = self.request(method, url, json=row)
        if not response.is_success:
            # Não confunde qualquer erro 400 com corrida de unicidade.
            return None, response.status_code
        return response.json() if response.content else {}, response.status_code


def fingerprint(records):
    return {name: {str(row["id"]): digest(row) for row in rows}
            for name, rows in records.items()}


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)


def run_directory():
    folder = PRIVATE / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    folder.mkdir(parents=True)
    return folder


def apply_seed(store, seed, reviewed, manifest_path):
    records = store.read()
    plan = build_plan(seed, records)
    if reviewed["target"] != store.target or reviewed["seed_hash"] != digest(seed):
        raise CatalogError("Ambiente/conjunto difere da simulação revisada")
    if reviewed["fingerprint"] != fingerprint(records) or reviewed["plan"] != plan:
        raise CatalogError("Estado mudou desde a simulação; gere e revise novo plano")
    store.ensure_indexes()
    manifest = {"target": store.target, "seed_hash": digest(seed), "version": seed["version"],
                "state": "running", "created": [], "pending": None, "normalized": []}
    save(manifest_path, manifest)
    try:
        # Campo técnico apenas; nomes/IDs/relacionamentos anteriores são preservados.
        for table in CATALOGS:
            for row in records[table]:
                key = normalize(row["nome"])
                if row.get("nome_normalizado") == key:
                    continue
                manifest["pending"] = {"operation": "normalize", "table": table, "id": row["id"]}
                save(manifest_path, manifest)
                # A API de metadados usa PUT; enviar o registro completo preserva
                # nome, ID, timestamp e vínculo mesmo com semântica de substituição.
                result, status = store.write("PUT", table, {**row, "nome_normalizado": key}, row["id"])
                if result is None:
                    raise CatalogError(f"Backfill técnico recusado: HTTP {status}")
                manifest["normalized"].append({"table": table, "id": row["id"]})
                manifest["pending"] = None
                save(manifest_path, manifest)
        for item in plan:
            if item["action"] == "reuse":
                continue
            current = store.read()
            latest = next(p for p in build_plan(seed, current) if p["key"] == item["key"])
            if latest["action"] == "reuse":
                continue
            payload = {"nome": item["name"], "nome_normalizado": normalize(item["name"])}
            if item["table"] == "raca":
                parent = next(p for p in build_plan(seed, current) if p["key"] == item["species"])
                if parent["id"] is None:
                    raise CatalogError("Espécie ainda não criada")
                payload["especie_id"] = parent["id"]
            manifest["pending"] = {"operation": "create", "table": item["table"], "payload": payload}
            save(manifest_path, manifest)
            result, status = store.write("POST", item["table"], payload)
            if result is None:
                # Uma corrida só é aceita se agora existir exatamente a entrada correta.
                if status not in (400, 409):
                    raise CatalogError(f"Criação recusada: HTTP {status}")
                after = next(p for p in build_plan(seed, store.read()) if p["key"] == item["key"])
                if after["id"] is None:
                    raise CatalogError(f"Criação recusada: HTTP {status}")
            else:
                manifest["created"].append({"table": item["table"], "id": result["id"],
                                            "record_hash": digest(result)})
            manifest["pending"] = None
            save(manifest_path, manifest)
        after = store.read()
        if any(item["action"] == "create" for item in build_plan(seed, after)):
            raise CatalogError("Lote incompleto")
        for table, rows in records.items():
            indexed = {row["id"]: row for row in after[table]}
            for row in rows:
                actual = indexed.get(row["id"], {})
                if any(actual.get(key) != value for key, value in row.items()
                       if key != "nome_normalizado"):
                    raise CatalogError("Registro anterior foi alterado")
        manifest["state"] = "complete"
        manifest["counts"] = {name: len(rows) for name, rows in after.items()}
        save(manifest_path, manifest)
        return manifest
    except Exception:
        manifest["state"] = "incomplete"
        manifest["confirmed_created_count"] = len(manifest["created"])
        save(manifest_path, manifest)
        raise


def rollback(store, manifest, path):
    if manifest["target"] != store.target:
        raise CatalogError("Manifesto pertence a outro ambiente")
    result = {"deleted": [], "preserved": [], "state": "running"}
    # Operador deve suspender as escritas nos catálogos/pets/aptidões durante reversão.
    for entry in reversed(manifest["created"]):
        records = store.read()
        table, row_id = entry["table"], entry["id"]
        row = next((row for row in records[table] if row["id"] == row_id), None)
        if row is None:
            continue
        if table == "raca":
            used = any(p.get("raca_id") == row_id for p in records["pet"])
        else:
            used = any(r.get("especie_id") == row_id
                       for name in ("pet", "raca", "veterinario_especie") for r in records[name])
        if used or digest(row) != entry["record_hash"]:
            result["preserved"].append({**entry, "reason": "referenced" if used else "modified"})
        else:
            result["pending"] = entry
            save(path, result)
            _, status = store.write("DELETE", table, {}, row_id)
            if status not in (200, 204):
                result["state"] = "incomplete"
                save(path, result)
                raise CatalogError("Reversão incompleta; consultar relatório")
            result["deleted"].append(entry)
            result.pop("pending", None)
        save(path, result)
    result["state"] = "partial" if result["preserved"] else "complete"
    save(path, result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=Path, default=SEED)
    parser.add_argument("--validate", action="store_true", help="Validação local sem rede")
    parser.add_argument("--profile")
    parser.add_argument("--workspace", type=int)
    parser.add_argument("--apply", type=Path, metavar="PLAN", help="Aplicar plano revisado")
    parser.add_argument("--rollback", type=Path, metavar="MANIFEST")
    parser.add_argument("--writes-suspended", action="store_true")
    args = parser.parse_args()
    folder = None
    try:
        seed = validate_seed(json.loads(args.seed.read_text(encoding="utf-8")))
        if args.validate:
            print(json.dumps({"valid": True, "species": len(seed["species"]),
                              "breeds": dict(Counter(b["species"] for b in seed["breeds"]))}))
            return 0
        if not args.profile or not args.workspace or (args.apply and args.rollback):
            raise CatalogError("Selecione perfil e workspace; aplicação/reversão são exclusivas")
        store = XanoStore(args.profile, args.workspace)
        folder = run_directory()
        if args.rollback:
            if not args.writes_suspended:
                raise CatalogError("Suspenda escritas de pets/aptidões/catálogos antes de reverter")
            result = rollback(store, json.loads(args.rollback.read_text(encoding="utf-8")), folder / "rollback.json")
            print(json.dumps({"state": result["state"], "deleted": len(result["deleted"]),
                              "preserved": len(result["preserved"]), "report": str(folder.relative_to(ROOT))}))
        elif args.apply:
            result = apply_seed(store, seed, json.loads(args.apply.read_text(encoding="utf-8")), folder / "manifest.json")
            print(json.dumps({"state": result["state"], "created": len(result["created"]),
                              "counts": result["counts"], "manifest": str((folder / "manifest.json").relative_to(ROOT))}))
        else:
            before = store.read()
            plan = build_plan(seed, before)
            reviewed = {"target": store.target, "seed_hash": digest(seed), "plan": plan,
                        "fingerprint": fingerprint(before)}
            if fingerprint(before) != fingerprint(store.read()):
                raise CatalogError("Dados mudaram durante a simulação")
            save(folder / "plan.json", reviewed)
            print(json.dumps({"mode": "dry-run", "counts": {k: len(v) for k, v in before.items()},
                              "actions": dict(Counter((p["table"] + ":" + p["action"]) for p in plan)),
                              "plan": str((folder / "plan.json").relative_to(ROOT))}))
        return 0
    except (CatalogError, RuntimeError, ValueError, KeyError, OSError, httpx.HTTPError):
        print("Operação incompleta. Consulte o manifesto privado e valide perfil, conectividade, índices e conflitos. Nenhuma credencial foi exibida.", file=sys.stderr)
        if folder is not None:
            print(json.dumps({"state": "incomplete", "report": str(folder.relative_to(ROOT))}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
