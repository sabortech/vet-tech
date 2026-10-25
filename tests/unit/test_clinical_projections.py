"""Run production Xano Lambda projection code; this does not emulate database auth."""
import json
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2]
RUNNER = "let s='';process.stdin.setEncoding('utf8');process.stdin.on('data',x=>s+=x);process.stdin.on('end',()=>{const d=JSON.parse(s);process.stdout.write(JSON.stringify(new Function('$input','$var',d.code)(d.input,d.vars)));});"


def execute(path, inputs, variables):
    source = (ROOT / path).read_text(encoding="utf-8")
    code = json.JSONDecoder().raw_decode(source.split("code = ", 1)[1])[0]
    result = subprocess.run(["node", "-e", RUNNER], input=json.dumps({"code": code,
        "input": inputs, "vars": variables}), text=True, encoding="utf-8", capture_output=True, check=True)
    return json.loads(result.stdout)


class ClinicalProjectionTests(unittest.TestCase):
    def test_daily_agenda_uses_sao_paulo_midnight(self):
        from datetime import datetime, timezone
        stamp = lambda text: int(datetime.fromisoformat(text).replace(tzinfo=timezone.utc).timestamp()*1000)
        rows = {"reservations": [
            {"id": 1, "pet_id": 5, "status": "agendada", "agendada_para": stamp("2030-01-11T02:59:59")},
            {"id": 2, "pet_id": 5, "status": "agendada", "agendada_para": stamp("2030-01-11T03:00:00")}],
            "consents": [], "pets": []}
        result = execute("xano/api/clinical/agenda_GET.xs", {"dia": "2030-01-11", "page": 1}, rows)
        self.assertEqual([r["id"] for r in result["items"]], [2])

    def test_history_hides_unpublished_complements_and_preserves_shared_ids(self):
        rows = {"consultations": [{"id": 1, "status": "finalizada"}, {"id": 2, "status": "em_atendimento"}],
            "vacina": [{"id": 10, "consulta_id": 1}, {"id": 11, "consulta_id": 2}, {"id": 12, "consulta_id": None}],
            "medicamento": [], "exame": [], "consulta_doenca": [{"id": 20, "consulta_id": 1, "doenca_id": 30, "veterinario_id": 4}],
            "pet_doenca": [{"id": 40, "doenca_id": 30, "consulta_doenca_id": 20}], "doenca": [{"id": 30, "nome": "Synthetic", "pet_id": None}]}
        result = execute("xano/function/clinical/history.xs", {"pet_id": 5}, rows)
        self.assertEqual([r["id"] for r in result["consultas"]], [1])
        self.assertEqual([r["id"] for r in result["vacinas"]], [10, 12])
        self.assertEqual(result["doencas"][0]["consulta_id"], 1)
        self.assertEqual(result["doencas"][0]["veterinario_id"], 4)

    def test_tutor_summary_never_returns_draft_or_unpublished_diagnosis(self):
        result = execute("xano/api/clinical/tutor_consultations_GET.xs", {}, {"rows": [
            {"id": 1, "status": "em_atendimento", "rascunho": {"diagnostico": "secret"}, "diagnostico": "secret"}]})
        self.assertNotIn("rascunho", result[0])
        self.assertNotIn("diagnostico", result[0])

    def test_agenda_uses_local_day_and_redacts_revoked_pet(self):
        rows = {"reservations": [
            {"id": 1, "pet_id": 5, "status": "agendada", "agendada_para": 1893544200000, "motivo": "private"}],
            "consents": [], "pets": [{"id": 5, "nome": "Private"}]}
        result = execute("xano/api/clinical/agenda_GET.xs", {"page": 1}, rows)
        self.assertEqual(set(result["items"][0]), {"id", "status", "agendada_para", "autorizado"})
        self.assertFalse(result["items"][0]["autorizado"])

    def test_pending_appointments_remain_ordered_and_paginated(self):
        rows = {"reservations": [{"id": i, "pet_id": 5, "status": "em_atendimento" if i == 1 else "agendada",
            "agendada_para": i} for i in range(1, 28)] + [{"id": 30, "status": "finalizada"}],
            "consents": [{"pet_id": 5}], "pets": [{"id": 5, "nome": "Synthetic"}]}
        result = execute("xano/api/clinical/agenda_GET.xs", {"page": 2}, rows)
        self.assertEqual(result["total"], 27)
        self.assertEqual([r["id"] for r in result["items"]], [26, 27])


if __name__ == "__main__":
    unittest.main()
