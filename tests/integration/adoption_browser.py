"""End-to-end adoption flow against an isolated synthetic Xano-compatible API."""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import signal
import socket
import subprocess
import sys
import threading
import time
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import httpx
from playwright.sync_api import expect, sync_playwright

PET = {
    "id": 41,
    "nome": "Luna QA",
    "especie_nome": "Cão",
    "raca_nome": "SRD",
    "sexo": "fêmea",
    "data_nasc": "2021-06-03",
    "peso_atual": 12000,
    "foto": "https://images.example.invalid/luna.jpg",
    "vacina": {
        "nome": "Antirrábica QA",
        "data_aplicacao": "2026-01-03",
        "data_prox_dose": "2027-01-03",
    },
    "medicamentos": [{
        "nome": "Medicamento QA",
        "dose": 2,
        "unidade": "mg",
        "frequencia": "1 vez ao dia",
        "tipo": "continuo",
        "data_inicio": "2026-01-03",
        "data_fim": None,
    }],
    "doencas": [{"nome": "Condição QA", "estado": "em_tratamento"}],
    "exame": {"tipo": "Hemograma QA", "data": "2026-01-04", "estado": "realizado"},
}
OWNED_PET = {
    "id": 7,
    "nome": "Pet existente",
    "especie_id": 1,
    "especie_nome": "Cão",
    "raca_id": None,
    "raca_nome": "SRD",
}
REQUESTS = []


class SyntheticAPI(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def do_GET(self):
        self.handle_api()

    def do_POST(self):
        self.handle_api()

    def handle_api(self):
        path = urlsplit(self.path).path.split("/", 2)[-1]
        raw = self.rfile.read(int(self.headers.get("Content-Length", "0")))
        payload = json.loads(raw) if raw else {}
        REQUESTS.append({"method": self.command, "path": path, "payload": payload})
        status, body = 200, []
        if path == "acesso/login":
            body = {
                "authToken": "synthetic-adoption-token",
                "perfil": "tutor",
                "identidade_id": 12,
            }
        elif not self.headers.get("Authorization"):
            status, body = 401, {"message": "Sessão inválida."}
        elif path == "tutor/me":
            body = {"perfil": "tutor", "identidade_id": 12, "nome": "Tutor QA"}
        elif path == "catalog/especies":
            body = [{"id": 1, "nome": "Cão"}]
        elif path == "pets" and self.command == "GET":
            body = [OWNED_PET]
        elif path == "adoption" and self.command == "GET":
            body = [PET]
        elif path == "adoption" and self.command == "POST":
            body = {
                "id": 41,
                "nome": "Luna QA",
                "especie_id": 1,
                "especie_nome": "Cão",
                "raca_id": None,
                "raca_nome": "SRD",
                "sexo": "fêmea",
                "data_nasc": "2021-06-03",
                "peso_atual": 12000,
                "foto": "https://images.example.invalid/luna.jpg",
            }
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())


def main():
    api = ThreadingHTTPServer(("127.0.0.1", 0), SyntheticAPI)
    threading.Thread(target=api.serve_forever, daemon=True).start()
    with socket.socket() as available:
        available.bind(("127.0.0.1", 0))
        app_port = available.getsockname()[1]
    origin = f"http://localhost:{app_port}"
    environment = {
        **os.environ,
        "XANO_API_BASE_URL": f"http://127.0.0.1:{api.server_port}",
        "XANO_TENANT": "",
    }
    log = (ROOT / ".venv/adoption-browser.log").open("w", encoding="utf-8")
    process = subprocess.Popen(
        [
            sys.executable, "-m", "reflex", "run", "--env", "prod",
            "--single-port", "--backend-port", str(app_port),
        ],
        cwd=ROOT,
        env=environment,
        stdout=log,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    errors = []
    try:
        for _ in range(120):
            if process.poll() is not None:
                raise RuntimeError("Servidor Reflex de teste encerrou; consulte o log temporário.")
            try:
                if httpx.get(origin, timeout=1).status_code == 200:
                    break
            except httpx.HTTPError:
                pass
            time.sleep(0.5)
        else:
            raise RuntimeError("Servidor Reflex de teste não iniciou.")

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                executable_path="/home/usuario/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome",
                args=["--no-sandbox"],
            )
            page = browser.new_page(viewport={"width": 1440, "height": 1000})
            page.set_default_timeout(30000)
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.route("https://fonts.googleapis.com/**", lambda route: route.abort())
            page.goto(origin + "/login", wait_until="domcontentloaded")
            page.get_by_label("E-mail", exact=True).fill("tutor@example.invalid")
            page.get_by_label("Senha", exact=True).fill("synthetic-password")
            page.get_by_role("button", name="Login", exact=True).click()
            expect(page.locator("#vet-tech-sidebar").get_by_role("link", name="Adoção", exact=True)).to_be_visible()
            page.locator("#vet-tech-sidebar").get_by_role("link", name="Adoção", exact=True).click()
            expect(page.get_by_role("heading", name="Adoção", exact=True)).to_be_visible()
            adoption_link = page.locator("#vet-tech-sidebar").get_by_role("link", name="Adoção", exact=True)
            expect(adoption_link).to_have_attribute("aria-current", "page")
            sidebar_labels = page.locator("#vet-tech-sidebar .sidebar-navigation .sidebar-item__label").all_text_contents()
            assert sidebar_labels.index("Adoção") == sidebar_labels.index("Meus Pets") + 1
            card = page.locator(".adoption-card")
            expect(card.get_by_role("heading", name="Luna QA", exact=True)).to_be_visible()
            expect(card.get_by_text("Medicamento QA", exact=False)).to_be_visible()
            expect(card.get_by_text("Condição QA", exact=False)).to_be_visible()
            expect(card.get_by_text("Hemograma QA", exact=False)).to_be_visible()
            assert [r["path"] for r in REQUESTS].count("adoption") == 1

            card.get_by_role("button", name="Ver prontuário", exact=True).click()
            preview = page.get_by_role("dialog")
            expect(preview.get_by_text("Condição QA", exact=False)).to_be_visible()
            assert [r["path"] for r in REQUESTS].count("adoption") == 1
            preview.get_by_role("button", name="Fechar", exact=True).click()

            card.get_by_role("button", name="Adotar", exact=True).click()
            confirmation = page.get_by_role("dialog")
            expect(confirmation.get_by_text("Deseja adotar Luna QA?", exact=False)).to_be_visible()
            confirmation.get_by_role("button", name="Cancelar", exact=True).click()
            expect(confirmation).not_to_be_visible()
            assert not any(r["path"] == "adoption" and r["method"] == "POST" for r in REQUESTS)
            expect(card.get_by_role("heading", name="Luna QA", exact=True)).to_be_visible()

            card.get_by_role("button", name="Adotar", exact=True).click()
            page.get_by_role("dialog").press("Escape")
            expect(page.get_by_role("dialog")).not_to_be_visible()
            expect(card.get_by_role("button", name="Adotar", exact=True)).to_be_visible()
            expect(card.get_by_role("button", name="Adotar", exact=True)).to_be_enabled()
            assert not any(r["path"] == "adoption" and r["method"] == "POST" for r in REQUESTS)

            card.get_by_role("button", name="Adotar", exact=True).click()
            page.get_by_role("dialog").get_by_role("button", name="Confirmar adoção", exact=True).click()
            expect(page.get_by_text("Luna QA agora faz parte da sua família.", exact=True)).to_be_visible()
            expect(page.locator(".adoption-card")).to_have_count(0)
            post = next(r for r in REQUESTS if r["path"] == "adoption" and r["method"] == "POST")
            assert post["payload"] == {"pet_id": 41}

            sidebar = page.locator("#vet-tech-sidebar")
            sidebar.get_by_role("link", name="Meus Pets", exact=True).click()
            expect(page.get_by_role("heading", name="Perfil do tutor", exact=True)).to_be_visible()
            expect(page.get_by_role("button", name="Abrir Luna QA", exact=True)).to_be_visible()
            sidebar.get_by_role("button", name="Mudar pet", exact=True).click()
            expect(page).to_have_url(origin + "/?selecionar=pet")
            expect(page.get_by_role("button", name="Abrir Luna QA", exact=True)).to_be_visible()
            assert [r["path"] for r in REQUESTS].count("pets") == 1
            assert [r["path"] for r in REQUESTS].count("adoption") == 2
            assert not errors, errors
            browser.close()
        print("PASS: navegação, resumo em memória, cancelar, adoção e listas locais.")
    finally:
        if process.poll() is None:
            os.killpg(process.pid, signal.SIGINT)
            process.wait(timeout=20)
        api.shutdown()
        api.server_close()
        log.close()


if __name__ == "__main__":
    main()
