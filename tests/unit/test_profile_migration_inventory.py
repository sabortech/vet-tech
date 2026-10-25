import unittest

from scripts.profile_migration_inventory import migration_plan


class ProfileMigrationInventoryTests(unittest.TestCase):
    def test_normalized_email_conflict_across_domain_tables(self):
        data = {"tutor": [{"id": 1, "email": " Person@Example.org ", "password": "existing-hash"}],
                "veterinario": [{"id": 1, "email": "person@example.org", "cmv": "123", "crmv_uf": "SP"}]}
        plan = migration_plan(data)
        self.assertIn("duplicate_email", {row["kind"] for row in plan["conflicts"]})
        self.assertFalse(plan["ready_for_backfill"])
        self.assertEqual(data["tutor"][0]["password"], "existing-hash")
        self.assertEqual(plan["password_fields"]["tutor"]["present"], 1)

    def test_no_uf_or_professional_links_are_invented(self):
        plan = migration_plan({"veterinario": [{"id": 5, "email": "vet@example.org", "cmv": "123", "especialidade": "Texto legado"}]})
        self.assertEqual({row["kind"] for row in plan["conflicts"]}, {
            "professional_registration_requires_review", "specialty_mapping_requires_review", "professional_links_require_review"})
        self.assertEqual(plan["password_fields"]["veterinario"]["unavailable"], 1)

    def test_snapshot_retains_existing_ids_and_digests_without_mutating_rows(self):
        data = {"tutor": [{"id": 7, "email": "person@example.org"}], "pet": [{"id": 8, "tutor_id": 7}]}
        plan = migration_plan(data)
        self.assertTrue(plan["ready_for_backfill"])
        self.assertEqual(plan["reservations_to_create"], [{"email": "person@example.org", "perfil": "tutor", "identidade_id": 7}])
        self.assertEqual(len(plan["record_digests"]["pet"]["8"]), 64)
        self.assertEqual(data["pet"], [{"id": 8, "tutor_id": 7}])

    def test_invalid_identity_and_clinic_block_migration(self):
        plan = migration_plan({"veterinario": [{"id": 2, "email": "", "cmv": "!", "clinica_id": 999}]})
        kinds = {row["kind"] for row in plan["conflicts"]}
        self.assertTrue({"invalid_email", "unknown_clinic", "professional_registration_requires_review"} <= kinds)


if __name__ == "__main__":
    unittest.main()
