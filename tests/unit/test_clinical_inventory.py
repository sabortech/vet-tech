import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from clinical_inventory import TABLES, analyze, comparable_script


class ClinicalInventoryTests(unittest.TestCase):
    def records(self):
        rows = {name: [] for name in TABLES}
        rows["pet"] = [{"id": 1}]
        rows["veterinario"] = [{"id": 2}]
        return rows

    def test_guid_is_not_a_schema_difference(self):
        self.assertEqual(comparable_script('table a {\n int id\n guid = "abc"\n}'),
                         comparable_script('table a {\n int id\n}'))
        self.assertNotEqual(comparable_script('table a { int id }'),
                            comparable_script('table a { text id }'))

    def test_empty_clinical_tables_are_ready_without_invented_links(self):
        rows = self.records()
        before = copy.deepcopy(rows)
        report = analyze(rows)
        self.assertTrue(report["ready_for_additive_migration"])
        self.assertEqual(report["counts"]["consulta"], 0)
        self.assertEqual(rows, before)

    def test_legacy_disease_is_only_fingerprinted_not_reassociated(self):
        rows = self.records()
        rows["doenca"] = [{"id": 9, "pet_id": 1, "nome": "Legado"}]
        before = copy.deepcopy(rows)
        report = analyze(rows)
        self.assertTrue(report["ready_for_additive_migration"])
        self.assertEqual(rows, before)
        self.assertEqual(set(report["record_digests"]["doenca"]), {"9"})

    def test_duplicate_consent_blocks_migration(self):
        rows = self.records()
        rows["acesso_autorizado"] = [{"id": n, "pet_id": 1, "veterinario_id": 2} for n in (1, 2)]
        report = analyze(rows)
        self.assertFalse(report["ready_for_additive_migration"])
        self.assertEqual(report["issues"][0]["issue"], "duplicate_consent_requires_review")

    def test_dangling_consultation_and_exam_are_reported(self):
        rows = self.records()
        rows["consulta"] = [{"id": 1, "pet_id": 99, "veterinario_id": 99}]
        rows["exame"] = [{"id": 1, "pet_id": 1, "consulta_id": 9}]
        self.assertEqual(len(analyze(rows)["issues"]), 3)


if __name__ == "__main__":
    unittest.main()
