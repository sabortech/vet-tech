"""Navegador → Reflex real → API HTTP local sintética; não acessa o Xano remoto.

Executar com o Python da .venv. Inicia servidor Reflex de produção temporário,
testa os fluxos e encerra somente os processos criados pelo próprio roteiro.
"""

from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import threading
import time
from urllib.parse import parse_qs, urlsplit
from zoneinfo import ZoneInfo

import httpx
from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / ".venv/dashboard-dates-browser"
TODAY = datetime.now(ZoneInfo("America/Sao_Paulo")).date()
PET = {"id": 1, "nome": "Pet sintético A", "especie_id": 1, "data_nasc": "2024-04-03"}
PET2 = {**PET, "id": 2, "nome": "Pet sintético B"}
REQUESTS = []
ERROR_MODE = False


class SyntheticAPI(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        self.handle_api()

    def do_POST(self):
        self.handle_api()

    def do_PUT(self):
        self.handle_api()

    def handle_api(self):
        global ERROR_MODE
        path = urlsplit(self.path).path.split("/", 2)[-1]
        query = parse_qs(urlsplit(self.path).query)
        raw = self.rfile.read(int(self.headers.get("Content-Length", "0")))
        payload = json.loads(raw) if raw else {}
        REQUESTS.append({"method": self.command, "path": path, "payload": payload})
        profile = "veterinario" if self.headers.get("Authorization") == "Bearer vet-fixture" else "tutor"
        status, body = 200, []
        if path == "acesso/login":
            profile = "veterinario" if payload.get("email", "").startswith("vet") else "tutor"
            body = {"authToken": "vet-fixture" if profile == "veterinario" else "tutor-fixture", "perfil": profile, "identidade_id": 1}
        elif not self.headers.get("Authorization"):
            status, body = 401, {"message": "Sessão inválida."}
        elif path in ("tutor/me", "veterinario/me"):
            body = {"perfil": profile, "identidade_id": 1, "nome": "Conta sintética"}
        elif path == "catalog/especies":
            body = [{"id": 1, "nome": "Cachorro"}]
        elif path == "pets" and self.command == "GET":
            body = [PET, PET2]
        elif path == "pets" and self.command == "POST":
            body = {"id": 3, **payload}
        elif path == "tutor/dashboard":
            pet_id = int(query.get("pet_id", [0])[0])
            if ERROR_MODE:
                status, body = 503, {"message": "Erro sintético"}
            elif pet_id not in (1, 2):
                status, body = 404, {"message": "Pet não disponível."}
            else:
                vaccines = [{"vacina": "Vacina sintética", "data_aplicacao": (TODAY-timedelta(days=30)).isoformat(),
                             "data_prox_dose": TODAY.isoformat() if pet_id == 1 else None}]
                body = {**(PET if pet_id == 1 else PET2), "especie_nome": "Cachorro", "vacinas": vaccines,
                        "consultas": [{"status": "finalizada", "data_atendimento": (TODAY-timedelta(days=1)).isoformat()}], "exames": []}
        elif path == "veterinario/agenda":
            when = int(datetime.now(ZoneInfo("America/Sao_Paulo")).replace(hour=10, minute=0, second=0, microsecond=0).timestamp() * 1000)
            body = {"items": [{"id": 1, "pet_id": 1, "pet_nome": PET["nome"], "status": "em_atendimento", "autorizado": True, "agendada_para": when}], "total": 1, "nextPage": None, "pageTotal": 1}
        elif path == "veterinario/consultas/1/iniciar":
            body = {"id": 1, "status": "em_atendimento"}
        elif path == "veterinario/consultas/1/rascunho" and self.command == "GET":
            body = {"consulta": {"id": 1, "pet_id": 1, "status": "em_atendimento", "versao": 0,
                                  "rascunho": {"data_atendimento": "2026-04-03"}}, "pet": PET}
        elif path == "veterinario/consultas/1/rascunho" and self.command == "PUT":
            body = {"versao": 1, "status": "em_atendimento"}
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())


def run():
    global ERROR_MODE
    OUTPUT.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(("127.0.0.1", 0), SyntheticAPI)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    with socket.socket() as available:
        available.bind(("127.0.0.1", 0))
        port = available.getsockname()[1]
    origin = f"http://localhost:{port}"
    environment = {**os.environ, "XANO_API_BASE_URL": f"http://127.0.0.1:{server.server_port}", "XANO_TENANT": ""}
    checks = []
    errors = []
    log = (OUTPUT / "reflex.log").open("w", encoding="utf-8")
    process = subprocess.Popen(
        [sys.executable, "-m", "reflex", "run", "--env", "prod", "--single-port", "--backend-port", str(port)],
        cwd=ROOT, env=environment, stdout=log, stderr=subprocess.STDOUT,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
    )
    try:
        for _ in range(120):
            if process.poll() is not None:
                raise RuntimeError("Servidor de teste encerrou; consulte o log privado")
            try:
                if httpx.get(origin, timeout=1).status_code == 200:
                    break
            except httpx.HTTPError:
                pass
            time.sleep(0.5)
        else:
            raise RuntimeError("Servidor de teste não iniciou")
        with sync_playwright() as p:
            browser = p.chromium.launch(channel="chrome", headless=True)
            try:
                for locale in ("pt-BR", "en-US"):
                    context = browser.new_context(locale=locale, timezone_id="Pacific/Auckland" if locale == "en-US" else "America/Sao_Paulo")
                    page = context.new_page()
                    page.on("pageerror", lambda error: errors.append(str(error)))
                    page.set_default_timeout(30000)
                    page.goto(origin + "/login")
                    page.get_by_label("E-mail", exact=True).fill("tutor@example.invalid")
                    page.get_by_label("Senha", exact=True).fill("synthetic-password")
                    page.get_by_role("button", name="Login", exact=True).click()
                    expect(page.get_by_role("heading", name="Perfil do tutor", exact=True)).to_be_visible()
                    page.get_by_role("link", name="Dashboard", exact=True).first.click()
                    expect(page.get_by_text("Sem próxima dose informada", exact=False)).to_be_visible()
                    expect(page.get_by_text("Próxima vacina: Vacina sintética", exact=False)).to_be_visible()
                    page.get_by_role("button", name="Ver Dashboard do pet", exact=True).first.click()
                    expect(page.get_by_text("Vacina sintética", exact=True).first).to_be_visible()
                    expect(page.get_by_text(TODAY.strftime("%d/%m/%Y"), exact=True).first).to_be_visible()
                    checks.append(locale + ": dashboard geral/individual e estado vazio")
                    ERROR_MODE = True
                    page.get_by_role("link", name="Meus Pets", exact=True).first.click()
                    page.get_by_role("link", name="Dashboard", exact=True).first.click()
                    expect(page.get_by_role("button", name="Tentar novamente", exact=True)).to_be_visible()
                    ERROR_MODE = False
                    page.get_by_role("button", name="Tentar novamente", exact=True).click()
                    expect(page.get_by_text("Vacina sintética", exact=True).first).to_be_visible()
                    checks.append(locale + ": falha e recuperação")
                    page.get_by_role("link", name="Meus Pets", exact=True).first.click()
                    page.locator("#pet-birth-date").fill("2026-04-03")
                    expect(page.get_by_text("Data selecionada: 03/04/2026", exact=True)).to_be_visible()
                    expect(page.locator("#pet-birth-date")).to_have_value("2026-04-03")
                    page.get_by_label("Nome do pet", exact=True).fill("Pet sintético C")
                    page.get_by_role("combobox").first.click()
                    page.get_by_role("option", name="Cachorro", exact=True).click()
                    page.get_by_role("button", name="Cadastrar pet", exact=True).click()
                    page.wait_for_timeout(400)
                    assert any(r["path"] == "pets" and r["method"] == "POST" and r["payload"].get("data_nasc") == "2026-04-03" for r in REQUESTS)
                    checks.append(locale + ": nascimento brasileiro e payload ISO")
                    context.close()
                    context = browser.new_context(locale=locale, timezone_id="Pacific/Auckland" if locale == "en-US" else "America/Sao_Paulo")
                    page = context.new_page()
                    page.on("pageerror", lambda error: errors.append(str(error)))
                    page.set_default_timeout(30000)
                    page.goto(origin + "/login")
                    page.get_by_label("E-mail", exact=True).fill("vet@example.invalid")
                    page.get_by_label("Senha", exact=True).fill("synthetic-password")
                    page.get_by_role("button", name="Login", exact=True).click()
                    expect(page.get_by_role("heading", name="Consultas", exact=True)).to_be_visible()
                    page.get_by_role("button", name="Horários", exact=True).click()
                    page.locator("#agenda-day").fill("2026-04-03")
                    expect(page.get_by_text("Data selecionada: 03/04/2026", exact=True)).to_be_visible()
                    page.get_by_role("button", name="Consultas", exact=True).click()
                    page.get_by_role("button", name="Retomar", exact=True).click()
                    expect(page.get_by_role("heading", name="Atendimento", exact=True)).to_be_visible()
                    page.locator("#clinic-data_atendimento").fill("2026-04-23")
                    expect(page.get_by_text("Data selecionada: 23/04/2026", exact=True)).to_be_visible()
                    page.get_by_role("button", name="Salvar rascunho", exact=True).click()
                    expect(page.get_by_text("Rascunho salvo.", exact=True)).to_be_visible()
                    assert any(r["method"] == "PUT" and r["payload"].get("payload", {}).get("data_atendimento") == "2026-04-23" for r in REQUESTS)
                    checks.append(locale + ": agenda/atendimento brasileiro e rascunho ISO")
                    context.close()
            finally:
                browser.close()
        assert not errors, "Erros JavaScript no teste; consulte os resultados privados"
        result = {"mode": "local-synthetic-http-api", "checks": checks, "javascript_errors": errors}
        (OUTPUT / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(result, ensure_ascii=True))
    finally:
        if process.poll() is None:
            if os.name == "nt":
                completed = subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], capture_output=True)
                if completed.returncode and process.poll() is None:
                    process.terminate()
            else:
                process.terminate()
            process.wait(timeout=20)
        server.shutdown()
        server.server_close()
        log.close()


if __name__ == "__main__":
    run()
