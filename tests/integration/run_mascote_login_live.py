"""Login local real sem persistir senha, tokens, capturas ou dados de conta.

Definir VET_TECH_TEST_EMAIL e VET_TECH_TEST_PASSWORD somente no ambiente do teste.
"""
import argparse
import json
import os

from playwright.sync_api import sync_playwright

from mascote_browser import assert_overlay_geometry


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:3001")
    parser.add_argument("--chromium", required=True)
    args = parser.parse_args()
    if not args.url.startswith(("http://localhost:", "http://127.0.0.1:")):
        raise SystemExit("O teste exige endereço local.")
    email = os.environ["VET_TECH_TEST_EMAIL"]
    password = os.environ["VET_TECH_TEST_PASSWORD"]
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path=args.chromium)
        page = browser.new_page(viewport={"width": 1366, "height": 900})
        try:
            page.goto(args.url + "/login", wait_until="networkidle")
            page.get_by_label("E-mail", exact=True).fill(email)
            page.get_by_label("Senha", exact=True).fill(password)
            page.get_by_role("button", name="Login", exact=True).click()
            page.get_by_role("heading", name="Perfil do tutor", exact=True).wait_for(timeout=45000)
            assert_overlay_geometry(page)
            page.evaluate("window.originalMascote=document.getElementById('vettech-mascote')")
            checked = []
            for destination in ("Configurações", "Meus Pets"):
                page.get_by_role("link", name=destination, exact=True).first.click()
                page.wait_for_timeout(700)
                assert page.evaluate("originalMascote===document.getElementById('vettech-mascote')")
                assert_overlay_geometry(page)
                checked.append(destination)
            print(json.dumps({"login_success": True, "global_mascot_persisted": True,
                              "layout_unchanged": True, "navigation_checked": checked}))
        except Exception as error:
            # Não imprimir snapshots do DOM autenticado nem payloads de rede.
            print(json.dumps({"login_success": False, "failure_type": type(error).__name__}))
            raise SystemExit(1) from None
        finally:
            browser.close()


if __name__ == "__main__":
    main()
