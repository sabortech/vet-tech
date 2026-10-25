"""Build an allowlisted clinical schema/API bundle; never deploy or copy records."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
TABLES = ("consulta", "vacina", "medicamento", "doenca", "exame", "acesso_autorizado",
          "log_acesso", "consulta_doenca", "pet_doenca", "clinical_lock")


def prepare():
    destination = ROOT / ".venv/clinical-bundle"
    paths = [ROOT / "xano/table" / (name + ".xs") for name in TABLES]
    paths += sorted((ROOT / "xano/function/clinical").glob("*.xs"))
    paths += sorted((ROOT / "xano/function/records").glob("*.xs"))
    paths += sorted((ROOT / "xano/api/clinical").glob("*.xs"))
    expected = {path.relative_to(ROOT / "xano") for path in paths}
    if destination.exists():
        unexpected = {path.relative_to(destination) for path in destination.rglob("*.xs")} - expected
        if unexpected:
            raise RuntimeError("Unexpected files in bundle; inspect before rebuilding.")
    manifest = []
    for source in paths:
        relative = source.relative_to(ROOT / "xano")
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        manifest.append({"path": relative.as_posix(), "sha256": hashlib.sha256(source.read_bytes()).hexdigest()})
    evidence = ROOT / "openspec/changes/fluxo-consultas-prontuario/bundle-manifest.json"
    evidence.write_text(json.dumps({"workspace": 167758, "profile": "vetech", "branch": "profile-default", "records": False,
        "files": manifest}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"directory": str(destination), "documents": len(paths), "records": False}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    prepare()
