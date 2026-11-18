"""Local adoption demo flow against a synthetic auth/pet API."""
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

OWNED_PET = {
    "id": 7,
    "nome": "Pet real",
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
        elif path == "adoption":
            status, body = 500, {"message": "Modo demo não deve acessar adoção Xano."}
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
        "VET_TECH_ADOPTION_DEMO": "true",
    }
    log = (ROOT / ".venv/adoption-demo-browser.log").open("w", encoding="utf-8")
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
            adoption_link = page.locator("#vet-tech-sidebar").get_by_role(
                "link", name="Adoção", exact=True
            )
            expect(adoption_link).to_be_visible()
            adoption_link.click()
            expect(page.get_by_role("heading", name="Adoção", exact=True)).to_be_visible()
            app_content = page.locator(".app-content")
            background_image = app_content.evaluate(
                "(element) => getComputedStyle(element).backgroundImage"
            )
            assert "fundpet-pattern-light.svg" in background_image, background_image
            expect(page.get_by_role("status").get_by_text("Demonstração local", exact=False)).to_be_visible()
            cards = page.locator(".adoption-card")
            expect(cards).to_have_count(6)

            expected_photos = {
                "Hades": "hades.jpeg",
                "Lua": "lua.jpeg",
                "Lulu": "lulu.jpeg",
                "Luna": "luna.jpeg",
                "Nina": "nina.jpeg",
                "Pituco": "pituco.jpeg",
            }
            for name, photo in expected_photos.items():
                card = page.locator(".adoption-card").filter(
                    has=page.get_by_role("heading", name=name, exact=True)
                )
                expect(card).to_be_visible()
                led = card.locator("svg.adoption-card-led .vet-date-led-track")
                expect(led).to_have_count(1)
                assert led.evaluate("(element) => getComputedStyle(element).stroke") == "rgb(105, 202, 73)"
                assert led.evaluate("(element) => getComputedStyle(element).animationName") == "vet-date-border-orbit"
                assert led.evaluate("(element) => getComputedStyle(element).animationDirection") == "normal"
                expect(card.locator("img")).to_have_attribute("src", f"/petsadocao/{photo}")
                image_response = page.request.get(origin + f"/petsadocao/{photo}")
                assert image_response.status == 200, (photo, image_response.status)
                expect(card.locator(".adoption-card__clinical")).to_contain_text("Não informado")
                expect(card.locator(".adoption-clinical__icon")).to_have_count(4)
                for title in ("Vacinação", "Medicamentos", "Condições de saúde", "Exame recente"):
                    section = card.locator(".adoption-clinical").filter(
                        has=page.get_by_text(title, exact=True)
                    )
                    expect(section.locator(".adoption-clinical__icon")).to_have_count(1)

            hades_card = page.locator(".adoption-card").filter(
                has=page.get_by_role("heading", name="Hades", exact=True)
            )
            preview_request_count = len(REQUESTS)
            hades_card.get_by_role("button", name="Ver prontuário", exact=True).click()
            preview = page.get_by_role("dialog")
            preview_mascot = preview.locator("img.adoption-dialog__mascot")
            preview_photo = preview.locator(".adoption-preview-dialog__photo")
            preview_records = preview.locator(".adoption-preview-dialog__records")
            preview_led = preview.locator("svg.adoption-dialog-led .vet-date-led-track")
            expect(preview_mascot).to_have_attribute("src", "/optimized/mascote_logo.webp")
            expect(preview_photo).to_have_attribute("src", "/petsadocao/hades.jpeg")
            expect(preview_photo).to_have_attribute("alt", "Foto de Hades")
            assert preview_mascot.evaluate("(image) => getComputedStyle(image).position") == "absolute"
            desktop_preview_layout = preview.evaluate(
                """(dialog) => {
                    const photo = dialog.querySelector('.adoption-preview-dialog__photo').getBoundingClientRect();
                    const records = dialog.querySelector('.adoption-preview-dialog__records');
                    const recordsRect = records.getBoundingClientRect();
                    return {
                        photoRight: photo.right,
                        recordsLeft: recordsRect.left,
                        photoTop: photo.top,
                        recordsTop: recordsRect.top,
                        recordsBorderLeft: getComputedStyle(records).borderLeftWidth,
                    };
                }"""
            )
            assert (
                desktop_preview_layout["photoRight"] <= desktop_preview_layout["recordsLeft"] + 1
                and abs(desktop_preview_layout["photoTop"] - desktop_preview_layout["recordsTop"]) <= 1
                and desktop_preview_layout["recordsBorderLeft"] == "1px"
            ), f"No desktop, foto e registros devem estar lado a lado com divisor vertical: {desktop_preview_layout}"
            assert len(REQUESTS) == preview_request_count, "Abrir a prévia não deve fazer chamadas adicionais ao Xano."
            preview_mascot_position = preview_mascot.evaluate(
                """(image) => {
                    const dialog = image.closest('[role=dialog]');
                    const imageRect = image.getBoundingClientRect();
                    const dialogRect = dialog.getBoundingClientRect();
                    return {
                        titleOffset: dialog.querySelector('.adoption-dialog__title').getBoundingClientRect().top
                            - dialogRect.top,
                        mascotBottom: imageRect.top + imageRect.height * 398 / 512,
                        dialogTop: dialogRect.top,
                    };
                }"""
            )
            assert preview_mascot_position["titleOffset"] < 60, (
                "A mascote da prévia não deve reservar altura acima do título."
            )
            assert abs(preview_mascot_position["mascotBottom"] - preview_mascot_position["dialogTop"]) <= 2, (
                "A base visível da mascote deve encostar na borda do diálogo da prévia."
            )
            preview_close_position = preview.get_by_role("button", name="Fechar", exact=True).evaluate(
                """(button) => {
                    const buttonRect = button.getBoundingClientRect();
                    const dialogRect = button.closest('[role=dialog]').getBoundingClientRect();
                    return {
                        rightInset: dialogRect.right - buttonRect.right,
                        bottomInset: dialogRect.bottom - buttonRect.bottom,
                        horizontalPosition: (buttonRect.left + buttonRect.right) / 2 - dialogRect.left,
                    };
                }"""
            )
            assert (
                preview_close_position["rightInset"] < 40
                and preview_close_position["bottomInset"] < 40
                and preview_close_position["horizontalPosition"] > 0.75 * preview.bounding_box()["width"]
            ), f"O botão Fechar deve ficar no canto inferior direito: {preview_close_position}"
            expect(preview.get_by_text("Perfil fictício de demonstração", exact=False)).to_be_visible()
            expect(preview).to_contain_text("Não informado")
            preview_sections = preview.locator(".adoption-dialog__clinical .adoption-clinical")
            expect(preview_sections).to_have_count(4)
            expect(preview.locator(".adoption-clinical__icon")).to_have_count(4)
            preview_section_alignment = preview_sections.evaluate_all(
                """sections => {
                    const boxes = sections.map(section => {
                        const heading = section.querySelector('.adoption-clinical__heading').getBoundingClientRect();
                        const value = section.querySelector('.adoption-clinical__value').getBoundingClientRect();
                        return {
                            left: section.getBoundingClientRect().left,
                            headingLeft: heading.left,
                            valueLeft: value.left,
                            headingBottom: heading.bottom,
                            valueTop: value.top,
                            height: section.getBoundingClientRect().height,
                        };
                    });
                    return {
                        gridColumns: getComputedStyle(sections[0].parentElement).gridTemplateColumns.split(' ').length,
                        boxes,
                    };
                }"""
            )
            assert preview_section_alignment["gridColumns"] == 1, (
                "As informações clínicas devem ocupar uma coluna para manter alinhamento."
            )
            aligned_content_left = preview_section_alignment["boxes"][0]["headingLeft"]
            assert all(
                abs(section["headingLeft"] - aligned_content_left) <= 2
                and abs(section["headingLeft"] - section["valueLeft"]) <= 2
                and section["valueTop"] >= section["headingBottom"]
                and section["height"] < 100
                for section in preview_section_alignment["boxes"]
            ), f"Os campos clínicos devem ficar alinhados em linhas compactas: {preview_section_alignment}"
            expect(preview_led).to_have_count(1)
            assert preview_led.evaluate("(element) => getComputedStyle(element).stroke") == "rgb(105, 202, 73)"
            assert preview_led.evaluate("(element) => getComputedStyle(element).animationName") == "vet-date-border-orbit"
            assert preview_led.evaluate("(element) => getComputedStyle(element).animationDirection") == "normal"
            page.set_viewport_size({"width": 390, "height": 844})
            mobile_preview_layout = preview.evaluate(
                """(dialog) => {
                    const photo = dialog.querySelector('.adoption-preview-dialog__photo').getBoundingClientRect();
                    const records = dialog.querySelector('.adoption-preview-dialog__records');
                    const recordsRect = records.getBoundingClientRect();
                    const style = getComputedStyle(records);
                    return {
                        photoBottom: photo.bottom,
                        recordsTop: recordsRect.top,
                        recordsBorderTop: style.borderTopWidth,
                        recordsBorderLeft: style.borderLeftWidth,
                    };
                }"""
            )
            assert (
                mobile_preview_layout["recordsTop"] >= mobile_preview_layout["photoBottom"] - 1
                and mobile_preview_layout["recordsBorderTop"] == "1px"
                and mobile_preview_layout["recordsBorderLeft"] == "0px"
            ), f"No celular, foto e registros devem empilhar com divisor horizontal: {mobile_preview_layout}"
            page.set_viewport_size({"width": 1440, "height": 1000})
            preview.get_by_role("button", name="Fechar", exact=True).click()

            hades_card.get_by_role("button", name="Adotar", exact=True).click()
            confirmation = page.get_by_role("dialog")
            mascot = confirmation.locator("img.adoption-dialog__mascot")
            led = confirmation.locator("svg.adoption-dialog-led .vet-date-led-track")
            expect(mascot).to_have_attribute("src", "/optimized/mascote_logo.webp")
            expect(led).to_have_count(1)
            assert mascot.evaluate("(image) => getComputedStyle(image).position") == "absolute"
            dialog_spacing = confirmation.evaluate(
                """(dialog) => ({
                    height: dialog.getBoundingClientRect().height,
                    titleOffset: dialog.querySelector('.adoption-dialog__title').getBoundingClientRect().top
                        - dialog.getBoundingClientRect().top,
                })"""
            )
            assert dialog_spacing["height"] < 320 and dialog_spacing["titleOffset"] < 60, (
                "O diálogo deve ajustar sua altura ao conteúdo, sem espaço vazio acima do título: "
                f"{dialog_spacing}"
            )
            assert led.evaluate("(element) => getComputedStyle(element).stroke") == "rgb(105, 202, 73)"
            assert led.evaluate("(element) => getComputedStyle(element).animationName") == "vet-date-border-orbit"
            assert led.evaluate("(element) => getComputedStyle(element).animationDirection") == "normal"
            assert mascot.evaluate("(image) => image.compareDocumentPosition(image.nextElementSibling) & Node.DOCUMENT_POSITION_FOLLOWING") == 4
            mascot_geometry = mascot.evaluate(
                """(image) => {
                    const canvas = document.createElement('canvas');
                    canvas.width = image.naturalWidth;
                    canvas.height = image.naturalHeight;
                    const context = canvas.getContext('2d');
                    context.drawImage(image, 0, 0);
                    const pixels = context.getImageData(0, 0, canvas.width, canvas.height).data;
                    let visibleBottom = 0;
                    let visibleLeft = canvas.width;
                    let visibleRight = 0;
                    for (let y = canvas.height - 1; y >= 0; y--) {
                        for (let x = 0; x < canvas.width; x++) {
                            if (pixels[(y * canvas.width + x) * 4 + 3] > 0) {
                                visibleBottom = y + 1;
                                break;
                            }
                        }
                        if (visibleBottom) break;
                    }
                    for (let y = 0; y < canvas.height; y++) {
                        for (let x = 0; x < canvas.width; x++) {
                            if (pixels[(y * canvas.width + x) * 4 + 3] > 0) {
                                visibleLeft = Math.min(visibleLeft, x);
                                visibleRight = Math.max(visibleRight, x + 1);
                            }
                        }
                    }
                    const dialogRect = image.closest('[role=dialog]').getBoundingClientRect();
                    const titleRect = image.closest('[role=dialog]').querySelector('.adoption-dialog__title').getBoundingClientRect();
                    const closeRect = image.closest('[role=dialog]').querySelector('[aria-label="Fechar confirmação de adoção"]').getBoundingClientRect();
                    const imageRect = image.getBoundingClientRect();
                    const visibleBottomY = imageRect.top + imageRect.height * visibleBottom / canvas.height;
                    const visibleCenterX = imageRect.left + imageRect.width * (visibleLeft + visibleRight) / (2 * canvas.width);
                    const gapCenterX = (titleRect.right + closeRect.left) / 2;
                    return {
                        imageSize: parseFloat(getComputedStyle(image).height),
                        difference: visibleBottomY - dialogRect.top,
                        gapCenterOffset: visibleCenterX - gapCenterX,
                    };
                }"""
            )
            assert (
                mascot_geometry["imageSize"] >= 120
                and abs(mascot_geometry["difference"]) <= 2
                and abs(mascot_geometry["gapCenterOffset"]) <= 20
            ), (
                "A mascote deve ficar centralizada entre o título e o botão de fechar, encostada na borda: "
                f"{mascot_geometry}"
            )
            expect(confirmation).to_contain_text("simular a adoção de Hades")
            confirmation.get_by_role("button", name="Cancelar", exact=True).click()
            expect(hades_card).to_be_visible()
            assert not any(request["path"] == "adoption" for request in REQUESTS)

            hades_card.get_by_role("button", name="Adotar", exact=True).click()
            page.get_by_role("dialog").get_by_role(
                "button", name="Confirmar adoção", exact=True
            ).click()
            expect(page.get_by_text("Simulação: Hades foi marcado como adotado nesta sessão.", exact=False)).to_be_visible()
            expect(page.locator(".adoption-card")).to_have_count(5)
            assert not any(request["path"] == "adoption" for request in REQUESTS)

            page.locator("#vet-tech-sidebar").get_by_role(
                "link", name="Meus Pets", exact=True
            ).click()
            expect(page.get_by_role("button", name="Abrir Pet real", exact=True)).to_be_visible()
            expect(page.get_by_role("button", name="Abrir Hades", exact=True)).to_have_count(0)
            assert not any(request["path"] == "adoption" for request in REQUESTS)
            assert not errors, errors
            browser.close()
        print("PASS: seis perfis, fotos locais, aviso, resumo sem dados clínicos e adoção apenas demonstrativa.")
    finally:
        if process.poll() is None:
            os.killpg(process.pid, signal.SIGINT)
            process.wait(timeout=20)
        api.shutdown()
        api.server_close()
        log.close()


if __name__ == "__main__":
    main()
