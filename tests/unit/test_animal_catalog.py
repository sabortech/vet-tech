import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from animal_catalog import (CatalogError, SEED, XanoStore, apply_seed, build_plan, digest,
                            fingerprint, normalize, rollback, validate_seed)


class MemoryStore:
    """Contrato administrativo em memória, com índice único e falhas injetadas."""
    target = {"workspace": 1, "profile": "test", "tenant": "isolated"}

    def __init__(self):
        self.rows = {"especie": [{"id": 7, "nome": "Cachorro"}],
                     "raca": [{"id": 9, "nome": "Shitzu", "especie_id": 7}],
                     "pet": [{"id": 1, "especie_id": 7, "raca_id": 9}],
                     "veterinario_especie": [{"id": 1, "especie_id": 7}]}
        self.writes = 0
        self.fail_after = None
        self.race_once = False

    def read(self):
        return copy.deepcopy(self.rows)

    def ensure_indexes(self):
        pass

    def write(self, method, table, payload, row_id=None):
        if self.fail_after is not None and self.writes >= self.fail_after:
            raise OSError("Falha de rede sintética")
        self.writes += 1
        rows = self.rows[table]
        if method == "PUT":
            row = next(r for r in rows if r["id"] == row_id)
            row.update(payload)
            return copy.deepcopy(row), 200
        if method == "DELETE":
            rows[:] = [r for r in rows if r["id"] != row_id]
            return {}, 204
        key = (payload.get("especie_id"), payload["nome_normalizado"])
        if any((r.get("especie_id"), r.get("nome_normalizado")) == key for r in rows):
            return None, 409
        row = {"id": max((r["id"] for r in rows), default=0) + 1, **payload}
        rows.append(row)
        if self.race_once:
            self.race_once = False
            return None, 409  # outra execução foi a criadora, esta não é dona do ID
        return copy.deepcopy(row), 200


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.seed = json.loads(SEED.read_text(encoding="utf-8"))
        self.store = MemoryStore()
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path = Path(self.folder.name) / "manifest.json"

    def reviewed(self):
        return {"target": self.store.target, "seed_hash": digest(self.seed),
                "fingerprint": fingerprint(self.store.read()),
                "plan": build_plan(self.seed, self.store.read())}

    def apply(self):
        return apply_seed(self.store, self.seed, self.reviewed(), self.path)

    def test_seed_sources_counts_and_normalization(self):
        validate_seed(self.seed)
        self.assertEqual((len(self.seed["species"]), len(self.seed["breeds"])), (2, 41))
        self.assertEqual(normalize("  CA\u0303O   de  Companhia  "), "cão de companhia")
        self.assertNotEqual(normalize("Siamês"), normalize("Siames"))

    def test_invalid_sets_rejected_before_writing(self):
        mutations = [lambda s: s["breeds"][0].update(name=" "),
                     lambda s: s["breeds"][0].update(species="unknown"),
                     lambda s: s["breeds"][0].update(name="SRD"),
                     lambda s: s["breeds"][1].update(aliases=["French Bulldog"]),
                     lambda s: s["breeds"][0].pop("aliases"),
                     lambda s: s["breeds"][0].update(source="inventada")]
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                seed = copy.deepcopy(self.seed)
                mutate(seed)
                with self.assertRaises(CatalogError):
                    validate_seed(seed)
        self.assertEqual(self.store.writes, 0)

    def test_plan_preserves_legacy_alias_and_is_read_only(self):
        before = self.store.read()
        plan = build_plan(self.seed, before)
        shih = next(r for r in plan if r["key"] == "cao-shih-tzu")
        self.assertEqual((shih["id"], shih["existing_name"]), (9, "Shitzu"))
        self.assertEqual(sum(r["action"] == "create" for r in plan), 41)
        self.assertEqual(before, self.store.read())
        self.assertEqual(self.store.writes, 0)

    def test_ambiguous_existing_aliases_block_all_writes(self):
        self.store.rows["especie"].append({"id": 8, "nome": "Cão"})
        with self.assertRaises(CatalogError):
            self.apply()
        self.assertEqual(self.store.writes, 0)

    def test_duplicated_names_and_orphaned_breeds_block(self):
        for row in ({"id": 10, "nome": " SHITZU ", "especie_id": 7},
                    {"id": 10, "nome": "Raça", "especie_id": 999}):
            store = MemoryStore()
            store.rows["raca"].append(row)
            with self.assertRaises(CatalogError):
                build_plan(self.seed, store.read())

    def test_changed_target_seed_or_snapshot_refused(self):
        for field in ("target", "seed_hash", "fingerprint", "plan"):
            with self.subTest(field=field):
                reviewed = self.reviewed()
                reviewed[field] = None
                with self.assertRaises(CatalogError):
                    apply_seed(self.store, self.seed, reviewed, self.path)
        self.assertEqual(self.store.writes, 0)

    def test_reapplication_creates_zero_and_preserves_references(self):
        refs = self.store.read()["pet"]
        first = self.apply()
        self.assertEqual((first["state"], len(first["created"])), ("complete", 41))
        ids = fingerprint(self.store.read())
        second = self.apply()
        self.assertEqual(second["created"], [])
        self.assertEqual(ids, fingerprint(self.store.read()))
        self.assertEqual(refs, self.store.read()["pet"])

    def test_unique_constraint_race_not_owned_by_loser(self):
        self.store.race_once = True
        result = self.apply()
        self.assertEqual(len(result["created"]), 40)
        self.assertEqual(len(self.store.rows["especie"]), 2)
        self.assertEqual(len(self.store.rows["raca"]), 41)

    def test_partial_failure_persists_intent_and_resumes(self):
        self.store.fail_after = 4
        with self.assertRaises(OSError):
            self.apply()
        partial = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(partial["state"], "incomplete")
        self.assertIsNotNone(partial["pending"])
        self.store.fail_after = None
        result = self.apply()
        self.assertEqual(result["state"], "complete")
        self.assertEqual(len(self.store.rows["raca"]), 41)

    def test_rollback_preserves_used_modified_and_preexisting(self):
        manifest = self.apply()
        breed = next(e for e in manifest["created"] if e["table"] == "raca")
        self.store.rows["pet"].append({"id": 2, "raca_id": breed["id"], "especie_id": 7})
        other = next(e for e in manifest["created"] if e["table"] == "raca" and e != breed)
        next(r for r in self.store.rows["raca"] if r["id"] == other["id"])["nome"] += " editada"
        result = rollback(self.store, manifest, Path(self.folder.name) / "rollback.json")
        self.assertEqual(result["state"], "partial")
        self.assertEqual(len(result["preserved"]), 2)
        self.assertEqual(len(self.store.rows["pet"]), 2)
        self.assertEqual(self.store.rows["raca"][0]["id"], 9)

    def test_full_rollback_keeps_original_ids(self):
        result = rollback(self.store, self.apply(), Path(self.folder.name) / "rollback.json")
        self.assertEqual(result["state"], "complete")
        self.assertEqual([r["id"] for r in self.store.rows["especie"]], [7])
        self.assertEqual([r["id"] for r in self.store.rows["raca"]], [9])

    def test_real_metadata_index_shape_and_missing_index(self):
        store = XanoStore.__new__(XanoStore)
        store.base = "https://example.invalid/api:meta/workspace/1"
        store.tables = {"especie": {"id": 1}, "raca": {"id": 2}}
        species = [{"type": "btree|unique", "fields": [{"name": "nome_normalizado"}]}]
        breeds = [{"type": "btree|unique", "fields": [{"name": "especie_id"}, {"name": "nome_normalizado"}]}]
        store.request = Mock(side_effect=[Mock(is_success=True, json=lambda: species),
                                          Mock(is_success=True, json=lambda: breeds)])
        store.ensure_indexes()
        store.request = Mock(return_value=Mock(is_success=True, json=lambda: []))
        with self.assertRaises(CatalogError):
            store.ensure_indexes()

    def test_unknown_write_result_is_not_repeated_or_owned(self):
        original = self.store.write
        def uncertain(method, table, payload, row_id=None):
            result = original(method, table, payload, row_id)
            if method == "POST":
                raise OSError("Resposta perdida após a escrita")
            return result
        self.store.write = uncertain
        with self.assertRaises(OSError):
            self.apply()
        partial = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(partial["created"], [])
        self.assertEqual(partial["pending"]["operation"], "create")
        self.assertEqual(len(self.store.rows["especie"]), 2)
        self.store.write = original
        resumed = self.apply()
        self.assertEqual(len(resumed["created"]), 40)
        self.assertEqual(len(self.store.rows["especie"]), 2)


if __name__ == "__main__":
    unittest.main()
