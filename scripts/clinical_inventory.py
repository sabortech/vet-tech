"""Inventário clínico somente de leitura; conteúdo sensível fica em .venv ignorado."""
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent))
from animal_catalog import XanoStore, save
from profile_migration_inventory import ROOT, digest

TABLES = ("consulta", "vacina", "medicamento", "doenca", "exame",
          "acesso_autorizado", "log_acesso", "pet", "veterinario", "tutor")


def comparable_script(source):
    """GUID é metadado omitido pela exportação, não diferença de schema."""
    source = re.sub(r'^\s*guid\s*=\s*"[^"]*"\s*$', "", source, flags=re.MULTILINE)
    return re.sub(r"\s+", " ", source).strip()


def analyze(records):
    pets = {row["id"] for row in records["pet"]}
    vets = {row["id"] for row in records["veterinario"]}
    consultations = {row["id"] for row in records["consulta"]}
    issues = []
    seen = set()
    for table in TABLES[:7]:
        for row in records[table]:
            if row.get("pet_id") not in pets:
                issues.append({"table": table, "id": row["id"], "issue": "pet_reference_requires_review"})
            if table in ("consulta", "vacina", "acesso_autorizado", "log_acesso") and row.get("veterinario_id") not in vets:
                issues.append({"table": table, "id": row["id"], "issue": "veterinarian_reference_requires_review"})
            if table == "exame" and row.get("consulta_id") not in (None, 0, "") and row["consulta_id"] not in consultations:
                issues.append({"table": table, "id": row["id"], "issue": "consultation_reference_requires_review"})
            if table == "acesso_autorizado":
                pair = (row.get("pet_id"), row.get("veterinario_id"))
                if pair in seen:
                    issues.append({"table": table, "id": row["id"], "issue": "duplicate_consent_requires_review"})
                seen.add(pair)
    return {"counts": {table: len(rows) for table, rows in records.items()},
            "issues": issues, "ready_for_additive_migration": not issues,
            "record_digests": {table: {str(row["id"]): digest(row) for row in rows}
                               for table, rows in records.items()}}


def main():
    try:
        store = XanoStore("vetech", 167758)
        if store.target["tenant"]:
            raise RuntimeError("Inventário principal exige tenant ausente")
        folder = ROOT / ".venv/clinical-inventory" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        records, schemas, comparisons = {}, {}, {}
        for table in TABLES:
            records[table] = store.pages(store.url(table))
            response = store.request("GET", f'{store.base}/table/{store.tables[table]["id"]}',
                                     params={"include_xanoscript": "true"})
            if not response.is_success:
                raise RuntimeError("Leitura de schema recusada")
            schemas[table] = response.json()
            remote = schemas[table].get("xanoscript", {})
            remote = remote.get("value", "") if isinstance(remote, dict) else str(remote or "")
            local = (ROOT / f"xano/table/{table}.xs").read_text(encoding="utf-8")
            comparisons[table] = {"remote_script_available": bool(remote),
                                  "local_matches_published": comparable_script(local) == comparable_script(remote)}
            if remote:
                save(folder / f"{table}-source.json", {"xanoscript": remote})
        summary = analyze(records)
        summary["schema_comparisons"] = comparisons
        save(folder / "snapshot.json", {"target": store.target, "records": records, "schemas": schemas})
        save(folder / "report.json", summary)
        print(json.dumps({"mode": "read-only", "counts": summary["counts"],
                          "issue_count": len(summary["issues"]), "schema_comparisons": comparisons,
                          "private_artifacts": str(folder.relative_to(ROOT))}))
        return 0
    except (OSError, ValueError, KeyError, RuntimeError, httpx.HTTPError):
        print("Inventário incompleto; conferir conectividade/perfil. Nenhuma escrita remota executada.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
