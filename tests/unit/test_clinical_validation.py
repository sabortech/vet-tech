"""Executa o mesmo código de validação da Lambda Xano, sem mocks da regra."""
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2]
NOW = int(datetime(2030, 1, 10, 15, tzinfo=timezone.utc).timestamp() * 1000)
CODE = (ROOT / "xano/function/clinical/validate.xs").read_text(encoding="utf-8").split('"""')[1]
RUNNER = "let s='';process.stdin.setEncoding('utf8');process.stdin.on('data',x=>s+=x);process.stdin.on('end',()=>{const d=JSON.parse(s);process.stdout.write(JSON.stringify(new Function('$input',d.code)(d.input)));});"


class ClinicalValidationTests(unittest.TestCase):
    def validate(self, kind, payload):
        completed = subprocess.run(["node", "-e", RUNNER], input=json.dumps({
            "code": CODE, "input": {"kind": kind, "payload": payload, "current_time": NOW}}),
            capture_output=True, text=True, encoding="utf-8", check=True)
        return json.loads(completed.stdout)

    def booking(self, hour="08:00"):
        return {"dia": "2030-01-11", "horario": hour, "motivo": "Avaliação",
                "pet_id": 1, "veterinario_id": 2, "operacao": "abcdef01-2345-6789-abcd"}

    def draft(self):
        return {"motivo": "Avaliação", "diagnostico": "Registro sintético", "data_atendimento": "2030-01-10"}

    def test_booking_boundaries_and_sao_paulo_offset(self):
        for hour in ("08:00", "17:00"):
            with self.subTest(hour=hour):
                result = self.validate("booking", self.booking(hour))
                self.assertTrue(result["valid"])
                instant = datetime.fromtimestamp(result["value"]["agendada_para"]/1000, timezone.utc)
                self.assertEqual(instant.hour, int(hour[:2])+3)

    def test_invalid_hours_past_dates_and_calendar_dates(self):
        cases = [self.booking(h) for h in ("07:59", "17:01", "08:99", "8:00")]
        cases += [{**self.booking(), "dia": "2030-02-30"}]
        for payload in cases:
            self.assertFalse(self.validate("booking", payload)["valid"])

    def test_past_booking_is_flagged_so_committed_retry_can_be_resolved(self):
        result = self.validate("booking", {**self.booking(), "dia": "2029-01-01"})
        self.assertTrue(result["valid"])
        self.assertFalse(result["future"])

    def test_booking_signature_stable_and_rejects_invalid_key(self):
        self.assertEqual(self.validate("booking", self.booking())["signature"],
                         self.validate("booking", self.booking())["signature"])
        self.assertFalse(self.validate("booking", {**self.booking(), "operacao": "x"})["valid"])

    def test_empty_draft_can_be_saved_but_not_finalized(self):
        self.assertTrue(self.validate("draft", {})["valid"])
        self.assertFalse(self.validate("finalize", {})["valid"])

    def test_consultation_without_complements_is_valid(self):
        result = self.validate("finalize", self.draft())
        self.assertTrue(result["valid"])
        self.assertEqual(result["value"]["vacinas"], [])

    def test_payload_cannot_assign_pet_or_author(self):
        result = self.validate("finalize", {**self.draft(), "pet_id": 999,
            "veterinario_id": 999, "status": "finalizada"})
        self.assertFalse(result["valid"])

    def test_complement_cannot_forge_identity_and_error_identifies_line(self):
        result = self.validate("finalize", {**self.draft(), "vacinas": [{"linha_id": "a", "pet_id": 999}]})
        self.assertFalse(result["valid"])
        self.assertIn("vacinas, linha 1", result["error"])

    def test_duplicate_rows_and_incomplete_vaccination_rejected(self):
        row = {"linha_id": "a", "vacina": "Sintética", "lote": "QA", "data_aplicacao": "2030-01-10"}
        self.assertFalse(self.validate("finalize", {**self.draft(), "vacinas": [row, row]})["valid"])
        self.assertFalse(self.validate("finalize", {**self.draft(), "vacinas": [{"linha_id": "a"}]})["valid"])
        self.assertFalse(self.validate("finalize", {**self.draft(), "vacinas": [{**row, "data_prox_dose": "2030-01-09"}]})["valid"])

    def test_decimal_continuous_prescription_does_not_require_end(self):
        row = {"linha_id": "a", "nome": "Registro sintético", "dose": "0.5", "unidade": "unidade",
               "frequencia": "conforme prescrição", "via": "registrada", "tipo": "continuo", "data_inicio": "2030-01-10"}
        result = self.validate("finalize", {**self.draft(), "medicamentos": [row]})
        self.assertTrue(result["valid"])
        self.assertEqual(result["value"]["medicamentos"][0]["dose"], .5)
        self.assertFalse(self.validate("finalize", {**self.draft(), "medicamentos": [{**row, "tipo": "outro"}]})["valid"])

    def test_disease_dates_and_state(self):
        row = {"linha_id": "a", "doenca_id": 1, "data_diagnostico": "2030-01-10", "estado": "controlada"}
        self.assertTrue(self.validate("finalize", {**self.draft(), "doencas": [row]})["valid"])
        self.assertFalse(self.validate("finalize", {**self.draft(), "doencas": [{**row, "estado": "inexistente"}]})["valid"])

    def test_exam_request_without_result_and_completion(self):
        row = {"linha_id": "a", "tipo": "Registro sintético", "status": "solicitado", "data_solicitacao": "2030-01-10"}
        self.assertTrue(self.validate("finalize", {**self.draft(), "exames": [row]})["valid"])
        self.assertFalse(self.validate("finalize", {**self.draft(), "exames": [{**row, "status": "realizado"}]})["valid"])
        done = {**row, "status": "realizado", "data_realizacao": "2030-01-10", "resultado": "Registro sintético"}
        self.assertTrue(self.validate("finalize", {**self.draft(), "exames": [done]})["valid"])

    def test_disease_catalog_normalization(self):
        result = self.validate("disease", {"nome": "  Condição   Sintética  "})
        self.assertEqual(result["value"]["nome_normalizado"], "condição sintética")


if __name__ == "__main__":
    unittest.main()
