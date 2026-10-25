"""Read-only Xano inventory for the shared-profile migration.

Private records stay under the ignored .venv/profile-migration directory.
Only counts and conflict categories are printed. No remote write is supported.
"""

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

import httpx

ROOT = Path(__file__).resolve().parents[1]
PRIVATE_ROOT = ROOT / ".venv" / "profile-migration"
UFS = set("AC AL AP AM BA CE DF ES GO MA MT MS MG PA PB PR PE PI RJ RN RS RO RR SC SP SE TO".split())
TABLES = ("tutor", "veterinario", "clinica", "especie", "raca", "pet")


def normalized_email(value):
    return str(value or "").strip().lower()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def migration_plan(records):
    """Return a private dry-run plan; IDs are retained but no identity is invented."""
    conflicts, reservations, emails, registrations = [], [], defaultdict(list), defaultdict(list)
    clinics = {row["id"] for row in records.get("clinica", [])}
    password_summary = {}
    for profile, password_field in (("tutor", "password"), ("veterinario", "senha")):
        password_summary[profile] = {"present": 0, "unavailable": 0}
        for row in records.get(profile, []):
            ref = {"perfil": profile, "id": row["id"]}
            email = normalized_email(row.get("email"))
            if not email or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
                conflicts.append({"kind": "invalid_email", **ref})
            else:
                emails[email].append(ref)
                reservations.append({"email": email, "perfil": profile, "identidade_id": row["id"]})
            key = "present" if row.get(password_field) else "unavailable"
            password_summary[profile][key] += 1
            if profile == "veterinario":
                crmv = str(row.get("crmv") or row.get("cmv") or "").strip().upper()
                uf = str(row.get("crmv_uf") or "").strip().upper()
                if not re.fullmatch(r"[A-Z0-9]{1,20}", crmv) or uf not in UFS:
                    conflicts.append({"kind": "professional_registration_requires_review", **ref})
                else:
                    registrations[(uf, crmv)].append(ref)
                if row.get("clinica_id") not in (None, 0, "", "0") and row["clinica_id"] not in clinics:
                    conflicts.append({"kind": "unknown_clinic", **ref})
                # A free-text specialty is not silently mapped to a new catalog ID.
                if row.get("especialidade"):
                    conflicts.append({"kind": "specialty_mapping_requires_review", **ref})
                if not row.get("especies_ids") or not row.get("especialidades_ids"):
                    conflicts.append({"kind": "professional_links_require_review", **ref})
    for refs in emails.values():
        if len(refs) > 1:
            conflicts.append({"kind": "duplicate_email", "records": refs})
    for refs in registrations.values():
        if len(refs) > 1:
            conflicts.append({"kind": "duplicate_professional_registration", "records": refs})
    return {
        "mode": "read-only", "ready_for_backfill": not conflicts,
        "counts": {name: len(rows) for name, rows in records.items()},
        "conflicts": conflicts, "reservations_to_create": reservations,
        "password_fields": password_summary,
        "record_digests": {name: {str(row["id"]): digest(row) for row in rows} for name, rows in records.items()},
        "restore_policy": "Preserve IDs and original fields/hashes; restore only from verified private backup during a write freeze. Never truncate or rehash stored credentials.",
    }


def cli_profile():
    executable = shutil.which("xano.cmd") or shutil.which("xano")
    if not executable:
        raise RuntimeError("CLI do Xano indisponível")
    yaml_module = Path(executable).parent / "node_modules/@xano/cli/node_modules/js-yaml"
    code = (
        "const fs=require('fs'),y=require(process.argv[1]);"
        "const p=process.env.XANO_CONFIG||process.env.USERPROFILE+'/.xano/credentials.yaml';"
        "const c=y.load(fs.readFileSync(p,'utf8'));"
        "const r=c.profiles[process.env.XANO_PROFILE||c.default];"
        "if(!r)process.exit(2);process.stdout.write(JSON.stringify(r));"
    )
    result = subprocess.run(["node", "-e", code, str(yaml_module)], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError("Não foi possível ler o perfil Xano configurado; nenhuma credencial foi exibida")
    return json.loads(result.stdout)


def read_pages(client, url):
    rows, page, visited = [], 1, set()
    while page:
        if page in visited:
            raise RuntimeError("Paginação repetida na API de metadados")
        visited.add(page)
        response = client.get(url, params={"page": page, "per_page": 100})
        if not response.is_success:
            raise RuntimeError(f"Leitura Xano recusada: HTTP {response.status_code}")
        body = response.json()
        if isinstance(body, list):
            rows.extend(body)
            break
        if not isinstance(body, dict) or not isinstance(body.get("items"), list):
            raise RuntimeError("Resposta de paginação inesperada")
        rows.extend(body["items"])
        page = body.get("nextPage")
    return rows


def collect():
    profile = cli_profile()
    origin = profile["instance_origin"].rstrip("/")
    if not origin.startswith("https://"):
        raise RuntimeError("O perfil deve usar HTTPS")
    base = f'{origin}/api:meta/workspace/{profile["workspace"]}'
    with httpx.Client(timeout=40, headers={"Authorization": "Bearer " + profile["access_token"]}) as client:
        tables = {row["name"]: row for row in read_pages(client, base + "/table")}
        if any(name not in tables for name in TABLES):
            raise RuntimeError("Tabelas obrigatórias ausentes no workspace selecionado")
        records = {name: read_pages(client, f'{base}/table/{tables[name]["id"]}/content') for name in TABLES}
    return {"captured_at": datetime.now(timezone.utc).isoformat(), "workspace": profile["workspace"], "tables": {name: tables[name] for name in TABLES}, "records": records}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, help="Revisar snapshot privado local sem chamadas remotas")
    args = parser.parse_args()
    try:
        snapshot = json.loads(args.snapshot.read_text(encoding="utf-8")) if args.snapshot else collect()
        plan = migration_plan(snapshot["records"])
        PRIVATE_ROOT.mkdir(parents=True, exist_ok=True)
        run = PRIVATE_ROOT / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        run.mkdir()
        (run / "snapshot.json").write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
        (run / "plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"mode": plan["mode"], "counts": plan["counts"], "ready_for_backfill": plan["ready_for_backfill"], "conflict_count": len(plan["conflicts"]), "conflict_categories": sorted({c["kind"] for c in plan["conflicts"]}), "password_fields": plan["password_fields"], "private_artifacts": str(run.relative_to(ROOT))}, ensure_ascii=False))
        return 0
    except (RuntimeError, OSError, ValueError, KeyError, httpx.HTTPError):
        # HTTP and filesystem exceptions may contain tokens, URLs or PII.
        print("Inventário não concluído. Verifique conectividade/perfil e formato do snapshot. Nenhuma escrita remota foi executada.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
