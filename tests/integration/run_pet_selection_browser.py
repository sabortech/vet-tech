"""Browser QA against the real local Reflex app and isolated Xano fixtures.

Requires the optional Playwright test dependency and installed Chrome.
Run run_pet_selection_live.py --keep-fixtures first. No production credentials
are printed or filled; only temporary accounts from its ignored fixture file.
"""
import json
from pathlib import Path
import time

from playwright.sync_api import expect, sync_playwright

from run_pet_selection_live import LiveVerification


def run():
    fixture_file = Path(".venv/pet-selection-fixtures.json")
    verification = LiveVerification(fixture_file)
    verification.data = json.loads(fixture_file.read_text(encoding="utf-8"))
    screenshots = Path(".venv/pet-selection-qa")
    screenshots.mkdir(exist_ok=True)
    changed_pet = None
    original_owner = None
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(channel="chrome", headless=True)
            context = browser.new_context(viewport={"width": 1280, "height": 900})
            page = context.new_page()
            page.set_default_timeout(30000)
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))

            def login(account):
                page.goto("http://localhost:3000/login")
                page.locator('input[name="email"]').fill(account["email"])
                page.locator('input[name="password"]').fill(account["password"])
                page.get_by_role("button", name="Login", exact=True).click()
                expect(page.get_by_role("heading", name="Perfil do tutor")).to_be_visible(timeout=60000)

            def overflow_check():
                assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), "Horizontal overflow"

            # Respect the Xano rate-limit window between independent flows.
            time.sleep(21)
            login(verification.data["accounts"][0])
            first, second = [p for p in verification.data["pets"] if p["account"] == "a"]
            expect(page.get_by_text("Escolha um pet na lista para abrir seus dados.")).to_be_visible()
            panel = page.locator("#pet-details")
            first_button = page.get_by_role("button", name="Abrir " + first["name"], exact=True)
            first_button.focus()
            first_button.press("Enter")
            expect(panel.get_by_role("heading", name=first["name"], exact=True)).to_be_visible()
            expect(panel.get_by_text("SRD", exact=False)).to_be_visible()
            overflow_check()
            page.screenshot(path=str(screenshots / "desktop.png"), full_page=True)
            print(json.dumps({"browser_desktop_keyboard_and_first_pet": "passed"}), flush=True)

            # Transfer only this run's second fixture temporarily to exercise
            # the real authorization failure from a previously loaded list.
            time.sleep(21)
            tutors = verification.records("tutor")
            a_email, b_email = [a["email"] for a in verification.data["accounts"][:2]]
            owner_a = next(t["id"] for t in tutors if t["email"] == a_email)
            owner_b = next(t["id"] for t in tutors if t["email"] == b_email)
            url = f'{verification.meta_url}/table/{verification.data["tables"]["pet"]}/content/{second["id"]}'
            fixture = verification.request(verification.meta, "GET", url)
            assert fixture.is_success
            row = fixture.json()
            assert row["tutor_id"] == owner_a and row["nome"].startswith(verification.data["marker"] + " ")
            original_owner = owner_a
            result = verification.request(verification.meta, "PUT", url, json={"tutor_id": owner_b})
            assert result.is_success, f"Fixture transfer failed: HTTP {result.status_code}"
            changed_pet = url
            page.get_by_role("button", name="Abrir " + second["name"], exact=True).click()
            expect(panel.get_by_text("Carregando dados do pet...")).to_be_visible()
            expect(panel.get_by_text("Pet não disponível.", exact=True)).to_be_visible()
            expect(panel.get_by_role("heading", name=first["name"], exact=True)).to_have_count(0)
            page.screenshot(path=str(screenshots / "failure.png"), full_page=True)
            restore = verification.request(verification.meta, "PUT", url, json={"tutor_id": owner_a})
            assert restore.is_success
            restored_row = verification.request(verification.meta, "GET", url)
            assert restored_row.json() == row, "Fixture fields changed beyond the temporary owner transfer"
            changed_pet = None
            page.get_by_role("button", name="Tentar novamente", exact=True).click()
            expect(panel.get_by_role("heading", name=second["name"], exact=True)).to_be_visible()
            print(json.dumps({"browser_real_forbidden_pet_and_retry": "passed"}), flush=True)

            page.set_viewport_size({"width": 390, "height": 844})
            page.get_by_role("button", name="Abrir " + first["name"], exact=True).click()
            expect(panel.get_by_role("heading", name=first["name"], exact=True)).to_be_visible()
            overflow_check()
            page.screenshot(path=str(screenshots / "mobile.png"), full_page=True)
            page.get_by_role("button", name="Voltar à lista", exact=True).click()
            expect(page.get_by_text("Escolha um pet na lista para abrir seus dados.")).to_be_visible()
            page.get_by_role("button", name="Sair", exact=True).click()
            expect(page.locator('input[name="email"]')).to_be_visible()

            time.sleep(21)
            login(verification.data["accounts"][1])
            expect(page.get_by_text("Escolha um pet na lista para abrir seus dados.")).to_be_visible()
            only_pet = next(p for p in verification.data["pets"] if p["account"] == "b")
            expect(page.get_by_role("button", name="Abrir " + only_pet["name"], exact=True)).to_be_visible()
            expect(page.get_by_role("button", name="Abrir " + first["name"], exact=True)).to_have_count(0)
            page.get_by_role("button", name="Sair", exact=True).click()
            expect(page.locator('input[name="email"]')).to_be_visible()

            time.sleep(21)
            login(verification.data["accounts"][2])
            expect(page.get_by_text("Você ainda não cadastrou pets.")).to_be_visible()
            expect(page.get_by_role("heading", name="Cadastrar pet", exact=True)).to_be_visible()
            overflow_check()
            page.screenshot(path=str(screenshots / "empty.png"), full_page=True)
            assert not errors, "Browser JavaScript errors: " + repr(errors)
            print(json.dumps({"browser_mobile_switch_logout_single_pet_empty": "passed", "javascript_errors": 0}), flush=True)
            browser.close()
        verification.verify_existing_records()
    finally:
        if changed_pet is not None:
            restored = verification.request(verification.meta, "PUT", changed_pet, json={"tutor_id": original_owner})
            assert restored.is_success, "Fixture owner restore failed"
        verification.meta.close()
        verification.api.close()


if __name__ == "__main__":
    run()
