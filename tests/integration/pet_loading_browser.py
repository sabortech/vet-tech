"""Deterministic browser verification using a local, synthetic Xano HTTP stub.

1. Run this file --serve (binds only 127.0.0.1:9010).
2. Start the real Reflex backend with XANO_API_BASE_URL=http://127.0.0.1:9010.
3. Compile the frontend and run this file --browser against localhost:3000.
Never point the synthetic credentials at a remote workspace.
"""
import argparse
from collections import Counter
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import threading
import time
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


CONTROL = {'delay': 2, 'fail': False, 'rate_limit': False}
COUNTS = Counter()
LOCK = threading.Lock()
PET_NAMES = {'1': 'Pet QA A', '2': 'Pet QA B'}


def animal(pet_id):
    return {'id': int(pet_id), 'nome': PET_NAMES[pet_id], 'especie_id': 1, 'raca_id': 0}


class Stub(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass  # Do not log request payloads or credentials.

    def respond(self, status, body, headers=None):
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(data)))
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        data = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))) or '{}')
        if self.path == '/__control':
            with LOCK:
                CONTROL.update(data)
                if data.get('reset'):
                    COUNTS.clear()
            return self.respond(200, {'ok': True})
        if self.path.endswith('/acesso/login'):
            return self.respond(200, {'authToken': 'synthetic-local-only', 'perfil': 'tutor', 'identidade_id': 1})
        self.respond(404, {})

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == '/__stats':
            with LOCK:
                result = dict(COUNTS)
            return self.respond(200, result)
        with LOCK:
            COUNTS[self.path] += 1
            delay = CONTROL['delay']
            fail = CONTROL['fail'] and '/tutor/consultas' in path
            limited = CONTROL['rate_limit'] and path.endswith('/historico')
            if limited:
                CONTROL['rate_limit'] = False
        if path.endswith('/historico') or '/tutor/consultas' in path:
            if limited:
                return self.respond(429, {}, {'Retry-After': '1'})
            time.sleep(delay)
            if fail:
                return self.respond(503, {})
        if path.endswith('/tutor/me'):
            return self.respond(200, {'perfil': 'tutor', 'identidade_id': 1, 'nome': 'Tutor QA'})
        if path.endswith('/tutor/account'):
            return self.respond(200, {'nome': 'Tutor QA', 'email': 'qa@example.invalid', 'cpf_mascarado': '***', 'telefone': '11999999999', 'endereco': 'QA'})
        if path.endswith('/catalog/especies'):
            return self.respond(200, [{'id': 1, 'nome': 'Cachorro'}])
        if path == '/api:vettech-pets/pets':
            return self.respond(200, [animal('1'), animal('2')])
        if path.startswith('/api:vettech-pets/pets/'):
            return self.respond(200, animal(path.rsplit('/', 1)[-1]))
        if path.endswith('/historico'):
            pet_id = path.split('/pets/')[1].split('/')[0]
            return self.respond(200, {'vacinas': [{'id': int(pet_id), 'vacina': 'Vacina QA ' + pet_id}],
                                     'medicamentos': [], 'doencas': [], 'consultas': []})
        if '/tutor/consultas' in path or path.endswith(('/acessos', '/auditoria')):
            return self.respond(200, [])
        self.respond(404, {})


def control(**values):
    with urlopen(Request('http://127.0.0.1:9010/__control', json.dumps(values).encode(), {'Content-Type': 'application/json'})) as response:
        return json.load(response)


def stats():
    with urlopen('http://127.0.0.1:9010/__stats') as response:
        return json.load(response)


def open_menu(page):
    if page.viewport_size['width'] < 768 and not page.locator('#vet-tech-sidebar').is_visible():
        page.locator('.sidebar-toggle--mobile').click()
        from playwright.sync_api import expect
        expect(page.locator('#vet-tech-sidebar')).to_be_visible()


def navigate(page, label):
    open_menu(page)
    page.get_by_role('link', name=label, exact=True).click()


def menu_action(page, label):
    open_menu(page)
    page.get_by_role('button', name=label, exact=True).click()


def browser_check():
    from playwright.sync_api import expect, sync_playwright

    results = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel='chrome', headless=True)
        try:
            for width in (1366, 390):
                print(f'Checking viewport {width}', flush=True)
                control(delay=2, fail=False, rate_limit=False, reset=True)
                context = browser.new_context(viewport={'width': width, 'height': 900})
                page = context.new_page()
                page.route('https://fonts.googleapis.com/**', lambda route: route.abort())
                page.route('https://fonts.gstatic.com/**', lambda route: route.abort())
                page.set_default_timeout(15000)
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.goto('http://localhost:3000/login', wait_until='domcontentloaded')
                page.get_by_label('E-mail', exact=True).fill('qa@example.invalid')
                page.get_by_label('Senha', exact=True).fill('synthetic-local-only')
                page.get_by_role('button', name='Login', exact=True).click()
                expect(page.get_by_role('heading', name='Perfil do tutor', exact=True)).to_be_visible()
                navigate(page, 'Prontuário')
                expect(page.get_by_role('heading', name='Início', exact=True)).to_be_visible()
                first = page.get_by_role('button', name='Abrir Pet QA A', exact=True)
                expect(first).to_be_visible()
                first.focus()
                start = time.perf_counter()
                first.click()
                expect(page.get_by_text('Carregando dados do pet…', exact=True).first).to_be_visible()
                loading_ms = round((time.perf_counter() - start) * 1000)
                navigate(page, 'Vacinas')
                expect(page.get_by_role('heading', name='Vacinas', exact=True)).to_be_visible()
                expect(page.get_by_text('Nenhum registro publicado para este pet.')).not_to_be_visible()
                expect(page.get_by_text('Vacina QA 1', exact=True)).to_be_visible()
                loaded_ms = round((time.perf_counter() - start) * 1000)
                print(f'{width}: initial loading and parallel fetch passed', flush=True)
                initial = stats()
                start = time.perf_counter()
                open_menu(page)
                page.get_by_role('link', name='Medicamentos', exact=True).focus()
                page.get_by_role('link', name='Medicamentos', exact=True).press('Enter')
                expect(page.get_by_text('Nenhum registro publicado para este pet.', exact=True)).to_be_visible()
                navigation_ms = round((time.perf_counter() - start) * 1000)
                navigate(page, 'Doenças')
                expect(page.get_by_role('heading', name='Doenças', exact=True)).to_be_visible()
                assert stats() == initial, 'Repeated API calls on cached navigation'
                assert not any('/acessos' in route or '/auditoria' in route for route in initial)
                assert sum(count for route, count in initial.items() if '/historico' in route or '/tutor/consultas' in route) == 2
                # Failure, accessible retry and empty-success behavior.
                control(fail=True)
                page.get_by_role('button', name='Atualizar dados do pet', exact=True).click()
                expect(page.get_by_text('Carregando dados do pet…', exact=True)).to_be_visible()
                expect(page.get_by_role('button', name='Tentar novamente', exact=True)).to_be_visible()
                expect(page.get_by_text('Nenhum registro publicado para este pet.')).not_to_be_visible()
                control(fail=False)
                page.get_by_role('button', name='Tentar novamente', exact=True).click()
                expect(page.get_by_text('Nenhum registro publicado para este pet.', exact=True)).to_be_visible()
                print(f'{width}: cached navigation and retry passed', flush=True)
                # Keep navigation responsive while the Xano client retries 429.
                control(rate_limit=True)
                page.get_by_role('button', name='Atualizar dados do pet', exact=True).click()
                expect(page.get_by_text('Carregando dados do pet…', exact=True)).to_be_visible()
                navigate(page, 'Medicamentos')
                expect(page.get_by_role('heading', name='Medicamentos', exact=True)).to_be_visible()
                expect(page.get_by_text('Carregando dados do pet…', exact=True)).to_be_visible()
                navigate(page, 'Configurações')
                expect(page.locator('#settings-nome')).to_have_value('Tutor QA')
                navigate(page, 'Meus Pets')
                expect(page.get_by_role('heading', name='Perfil do tutor', exact=True)).to_be_visible()
                navigate(page, 'Prontuário')
                expect(page.get_by_role('heading', name='Início', exact=True)).to_be_visible()
                open_menu(page)
                expect(page.get_by_role('button', name='Mudar pet', exact=True)).to_be_visible()
                # A delayed A response must never fill B's sections.
                control(delay=3)
                menu_action(page, 'Mudar pet')
                page.get_by_role('button', name='Abrir Pet QA A', exact=True).click()
                expect(page.get_by_text('Carregando dados do pet…', exact=True).first).to_be_visible()
                menu_action(page, 'Mudar pet')
                page.get_by_role('button', name='Abrir Pet QA B', exact=True).click()
                navigate(page, 'Vacinas')
                expect(page.get_by_text('Vacina QA 2', exact=True)).to_be_visible()
                expect(page.get_by_text('Vacina QA 1', exact=True)).not_to_be_visible()
                navigate(page, 'Consultas')
                page.get_by_role('button', name='Carregar permissões e histórico de acessos', exact=True).click()
                expect(page.get_by_role('button', name='Permissões e histórico de acessos', exact=True)).to_be_visible()
                assert any('/acessos' in route for route in stats())
                assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), 'Horizontal overflow'
                assert not errors, 'Browser runtime errors: ' + repr(errors)
                menu_action(page, 'Sair')
                expect(page.get_by_role('button', name='Login', exact=True)).to_be_visible()
                results.append({'width': width, 'loading_ms': loading_ms, 'load_ms': loaded_ms,
                                'cached_navigation_ms': navigation_ms, 'initial_requests': initial, 'passed': True})
                print(json.dumps(results[-1], ensure_ascii=False), flush=True)
                context.close()
        finally:
            browser.close()
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--serve', action='store_true')
    parser.add_argument('--browser', action='store_true')
    args = parser.parse_args()
    if args.serve:
        ThreadingHTTPServer(('127.0.0.1', 9010), Stub).serve_forever()
    elif args.browser:
        browser_check()
