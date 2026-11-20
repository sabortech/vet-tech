"""Exercita a área da clínica sem alterar pets no backend de desenvolvimento."""
import getpass
import base64
from pathlib import Path
import secrets
import sys

from playwright.sync_api import expect, sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from animal_catalog import XanoStore


def main():
    if len(sys.argv) != 2:
        raise RuntimeError("Informe apenas o e-mail da conta de teste.")
    password = getpass.getpass("Senha da conta de teste: ")
    store = XanoStore("vetech", 167758)
    marker = "qa-clinic-ui-" + secrets.token_hex(8)
    try:
      with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe", headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.set_default_timeout(30000)
        page.goto("http://127.0.0.1:3199/login", wait_until="domcontentloaded")
        page.get_by_label("E-mail", exact=True).fill(sys.argv[1])
        page.get_by_label("Senha", exact=True).fill(password)
        page.get_by_role("button", name="Login", exact=True).click()
        expect(page.get_by_role("heading", name="Veterinários", exact=True)).to_be_visible()
        expect(page.get_by_text("Área da clínica", exact=True)).to_be_visible()
        page.screenshot(path="output/clinic-desktop.png", full_page=True)
        page.get_by_role("button", name="Pets para adoção", exact=True).click()
        expect(page.get_by_role("heading", name="Cadastrar pet para adoção")).to_be_visible()
        expect(page.get_by_label("Nome do pet")).to_be_visible()
        page.screenshot(path="output/clinic-pets-desktop.png", full_page=True)
        page.get_by_label("Nome do pet").fill(marker)
        page.get_by_label("Selecione a espécie", exact=True).click()
        page.get_by_role("option").first.click()
        photo = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/aWQAAAAASUVORK5CYII=")
        page.locator('#pet-photo input[type="file"]').set_input_files({"name": "foto.png", "mimeType": "image/png", "buffer": photo})
        page.get_by_role("button", name="Cadastrar pet", exact=True).click()
        expect(page.get_by_text(marker, exact=True)).to_be_visible(timeout=45000)
        print("Cadastro confirmado; verificando limpeza e imagem.", flush=True)
        try:
            expect(page.get_by_label("Nome do pet")).to_have_value("")
        except AssertionError:
            raise RuntimeError("O nome não foi limpo após cadastrar.") from None
        try:
            expect(page.locator("#pet-photo")).not_to_have_attribute("data-preview-visible", "true")
        except AssertionError:
            raise RuntimeError("A prévia da foto não foi limpa após cadastrar.") from None
        saved = [p for p in store.pages(store.url("pet")) if p.get("nome") == marker]
        assert len(saved) == 1 and saved[0].get("foto") == "data:image/png;base64," + base64.b64encode(photo).decode("ascii")
        print("Limpeza e base64 confirmados; verificando publicação.", flush=True)
        card = page.locator(".vet-schedule-card").filter(has_text=marker)
        card.get_by_role("button", name="Publicar").click()
        page.get_by_role("alertdialog").get_by_role("button", name="Confirmar").click()
        expect(card.get_by_text("Disponível para adoção")).to_be_visible(timeout=45000)
        card.get_by_role("button", name="Retirar").click()
        page.get_by_role("alertdialog").get_by_role("button", name="Confirmar").click()
        expect(card.get_by_text("Ainda não publicado")).to_be_visible(timeout=45000)
        page.set_viewport_size({"width": 390, "height": 844})
        expect(page.get_by_label("Nome do pet")).to_be_visible()
        page.screenshot(path="output/clinic-pets-mobile.png", full_page=True)
        browser.close()
    finally:
        matches = [p for p in store.pages(store.url("pet")) if p.get("nome") == marker]
        if len(matches) > 1:
            raise RuntimeError("Mais de uma fixture de navegador; limpeza interrompida.")
        if matches:
            pet_id = matches[0]["id"]
            for event in store.pages(store.url("clinica_adocao_evento")):
                if event.get("pet_id") == pet_id:
                    if not store.request("DELETE", store.url("clinica_adocao_evento") + f"/{event['id']}").is_success:
                        raise RuntimeError("Falha ao remover auditoria sintética.")
            if not store.request("DELETE", store.url("pet") + f"/{pet_id}").is_success:
                raise RuntimeError("Falha ao remover pet sintético.")
    print("PASS: login compartilhado e área da clínica em desktop e celular.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        if isinstance(exc, RuntimeError):
            print(str(exc), file=sys.stderr)
        else:
            print(f"Verificação de navegador falhou ({type(exc).__name__}); nenhuma credencial foi registrada.", file=sys.stderr)
        raise SystemExit(1)
