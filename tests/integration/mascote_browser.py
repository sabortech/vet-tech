"""Verifica a mascote real e animações isoladas sem serviços externos.

Uso: python tests/integration/mascote_browser.py --url http://localhost:3000
Requer Playwright e Chromium. --authenticated usa somente o stub local de QA.
"""
import argparse
import json
import re
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[2]
INSTRUMENT = """() => {
  window.probe = {frames:0, maxMs:0, readsInFrame:0, moves:0};
  const raf=window.requestAnimationFrame.bind(window);
  let inside=false;
  window.requestAnimationFrame=cb=>raf(t=>{
    const start=performance.now(); inside=true;
    try { cb(t); } finally { inside=false; probe.frames++; probe.maxMs=Math.max(probe.maxMs,performance.now()-start); }
  });
  const rect=Element.prototype.getBoundingClientRect;
  Element.prototype.getBoundingClientRect=function(){if(inside)probe.readsInFrame++;return rect.call(this);};
  const listen=window.addEventListener.bind(window);
  window.addEventListener=(type,fn,options)=>{if(type==='pointermove')probe.moves++;return listen(type,fn,options);};
}"""


def assert_overlay_geometry(page):
    result = page.evaluate("""() => {
      const button=document.getElementById('vettech-mascote');
      const content=document.querySelector('.login-view,.app-layout')||document.body;
      const snapshot=()=>{
        const r=content.getBoundingClientRect();
        return [r.x,r.y,r.width,r.height,document.documentElement.scrollHeight];
      };
      const before=snapshot(),display=button.style.display;
      button.style.display='none';const after=snapshot();button.style.display=display;
      return {before,after,position:getComputedStyle(button).position,
        layoutWrapper:!!document.querySelector('.mascote-app')};
    }""")
    assert result['before']==result['after'], result
    assert result['position']=='fixed' and not result['layoutWrapper'], result
    return True


def run(args):
    evidence = ROOT / args.evidence
    evidence.mkdir(parents=True, exist_ok=True)
    results = {}
    with sync_playwright() as p:
        opts = {"headless": True}
        if args.chromium:
            opts["executable_path"] = args.chromium
        browser = p.chromium.launch(**opts)
        context = browser.new_context(viewport={"width": 1366, "height": 900})
        context.route("https://fonts.googleapis.com/**", lambda r: r.abort())
        context.route("https://fonts.gstatic.com/**", lambda r: r.abort())
        page = context.new_page()
        sent = []
        page.on("websocket", lambda ws: ws.on("framesent", lambda payload: sent.append(payload)))
        page.goto(args.url + "/login", wait_until="networkidle")
        button = page.get_by_role("button", name="Abrir assistente Vet Tech")
        expect(button).to_have_count(1)
        expect(button).to_have_class(re.compile("assets-ready"))
        geometry = button.evaluate("""e => {
          const img=e.querySelector('.mascote-idle-image'),r=e.getBoundingClientRect();
          const imageRect=img.getBoundingClientRect();
          return {width:r.width,height:r.height,ratio:img.naturalWidth/img.naturalHeight,
            imageRatio:imageRect.width/imageRect.height,fit:getComputedStyle(img).objectFit,
            right:innerWidth-r.right,bottom:innerHeight-r.bottom};
        }""")
        assert geometry == {"width":140,"height":140,"ratio":1,"imageRatio":1,"fit":"contain","right":24,"bottom":24}, geometry
        results["proportion"] = geometry
        background = page.locator('.login-background').evaluate("""e=>{
          const r=e.getBoundingClientRect();return {top:r.top,bottom:r.bottom,height:innerHeight,position:getComputedStyle(e).position,cover:getComputedStyle(e).backgroundSize};
        }""")
        assert background['top'] <= 0 and background['bottom'] >= background['height'], background
        assert background['position']=='absolute' and background['cover']=='cover'
        page.screenshot(path=str(evidence/'login-desktop.png'))
        results["login_full_background"] = background
        page.wait_for_timeout(500)
        baseline = len([x for x in sent if str(x).startswith("42")])
        for x in range(10, 300, 20):
            page.mouse.move(x, 50)
        page.wait_for_timeout(1500)
        assert len([x for x in sent if str(x).startswith("42")]) == baseline
        results["backend_movement_events"] = 0
        page.evaluate("window.savedMascote=document.getElementById('vettech-mascote')")
        page.get_by_role("button", name="Não tem uma conta? Cadastre-se!").click()
        page.wait_for_url("**/cadastro")
        assert page.evaluate("savedMascote===document.getElementById('vettech-mascote')")
        results["public_spa_same_node"] = True
        geometry_checks = []
        for width in (390, 1366):
            page.set_viewport_size({"width": width, "height": 900})
            for route in ("/login", "/cadastro"):
                page.goto(args.url + route, wait_until="networkidle")
                geometry_checks.append([width, route, assert_overlay_geometry(page)])
        results["public_geometry_unchanged"] = geometry_checks
        page.set_viewport_size({"width": 1366, "height": 900})
        routes = ["/", "/login", "/cadastro", "/configuracoes", "/prontuario", "/atendimento/1"]
        for route in routes:
            page.goto(args.url + route, wait_until="domcontentloaded")
            expect(button).to_have_count(1)
            expect(button).to_be_visible()
        results["routes_with_global_button"] = routes

        if args.authenticated:
            if not args.url.startswith(("http://localhost:", "http://127.0.0.1:")):
                raise ValueError("QA sintético exige origem local")
            page.goto(args.url + "/login", wait_until="networkidle")
            page.get_by_label("E-mail", exact=True).fill("qa@example.invalid")
            page.get_by_label("Senha", exact=True).fill("synthetic-local-only")
            page.get_by_role("button", name="Login", exact=True).click()
            expect(page.get_by_role("heading", name="Perfil do tutor", exact=True)).to_be_visible()
            page.evaluate("window.savedMascote=document.getElementById('vettech-mascote')")
            for name in ("Configurações", "Meus Pets", "Prontuário"):
                page.get_by_role("link", name=name, exact=True).first.click()
                expect(button).to_be_visible()
                assert page.evaluate("savedMascote===document.getElementById('vettech-mascote')")
            results["authenticated_spa_same_node"] = True
            collisions = []
            for width in (390, 768, 1366):
                page.set_viewport_size({"width": width, "height": 900})
                for route in ("/", "/configuracoes", "/prontuario"):
                    page.goto(args.url + route, wait_until="networkidle")
                    assert_overlay_geometry(page)
                    page.evaluate("scrollTo(0,document.documentElement.scrollHeight)")
                    page.wait_for_timeout(150)
                    collisions.append([width, route, "geometry unchanged"])
                    page.screenshot(path=str(evidence / f"page-{width}-{route.strip('/') or 'index'}.png"))
            results["authenticated_geometry_unchanged"] = collisions

        # Use the exact component DOM in isolation to measure only its own work.
        markup = button.evaluate("""e=>{
          const clone=e.cloneNode(true),original=e.querySelectorAll('svg *');
          clone.querySelectorAll('svg *').forEach((node,i)=>{
            for(const key of ['fill','stroke','strokeWidth'])node.style[key]=getComputedStyle(original[i])[key];
          });return clone.outerHTML;
        }""")
        fixture = context.new_page()
        fixture.route("**/__mascote-test", lambda r: r.fulfill(
            content_type="text/html", body=f'<!doctype html><html><head><link rel="stylesheet" href="/mascote.css"></head><body>{markup}</body></html>'))
        fixture.goto(args.url + "/__mascote-test")
        fixture.evaluate(INSTRUMENT)
        script = (ROOT / "assets/mascote.js").read_text()
        fixture.add_script_tag(content=script)
        fixture.add_script_tag(content=script)
        assert fixture.evaluate("probe.moves") == 1
        fixture.evaluate("window.clicks=0;window.addEventListener('vettech:mascote-click',()=>clicks++)")
        mascot = fixture.locator("#vettech-mascote")
        fixture.mouse.move(30, 30)
        fixture.wait_for_timeout(1500)
        transform = fixture.locator(".mascote-tracking").evaluate("e=>e.style.transform")
        assert "translate(0px, 0px)" not in transform
        count = fixture.evaluate("probe.frames")
        fixture.wait_for_timeout(300)
        assert fixture.evaluate("probe.frames") == count
        assert fixture.evaluate("probe.readsInFrame") == 0
        mascot.hover()
        fixture.wait_for_timeout(300)
        expect(fixture.locator(".mascote-hover")).to_have_css("opacity", "1")
        glow = fixture.locator(".mascote-glow")
        curve = glow.evaluate("""e=>{
          const animation=e.getAnimations().find(a=>a.animationName==='mascote-glow-intro');
          animation.pause();
          const samples=[0,1000,2000,3000,4000].map(time=>{
            animation.currentTime=time;return Number(getComputedStyle(e).opacity);
          });
          const result={samples,iterations:animation.effect.getTiming().iterations,
            duration:animation.effect.getTiming().duration};
          animation.currentTime=3900;animation.play();return result;
        }""")
        assert curve['samples'] == [0,.95,.12,.95,.75], curve
        assert curve['iterations'] == 1 and curve['duration'] == 4000, curve
        fixture.wait_for_function("""document.querySelector('.mascote-glow').getAnimations()
          .find(a=>a.animationName==='mascote-glow-intro').playState==='finished'""")
        assert glow.evaluate('e=>getComputedStyle(e).opacity') == '0.75'
        fixture.wait_for_timeout(250)
        assert glow.evaluate('e=>getComputedStyle(e).opacity') == '0.75'
        fixture.mouse.move(20,20)
        fixture.wait_for_timeout(250)
        assert glow.evaluate('e=>getComputedStyle(e).opacity') == '0'
        mascot.hover()
        assert glow.evaluate("e=>e.getAnimations().some(a=>a.animationName==='mascote-glow-intro' && a.playState==='running')")
        results['two_slow_pulses_then_steady'] = curve
        mascot.click()
        fixture.mouse.move(20, 20)
        mascot.focus()
        fixture.keyboard.press("Enter")
        fixture.keyboard.press("Space")
        assert fixture.evaluate("clicks") == 3
        assert mascot.evaluate("e=>e.matches(':focus-visible')")
        expect(fixture.locator(".mascote-hover")).to_have_css("opacity", "1")
        fixture.screenshot(path=str(evidence / "hover-focus.png"))
        mascot.evaluate("e=>e.dataset.glowMode='rgb'")
        mascot.hover()
        fixture.wait_for_timeout(450)
        hue_filter = fixture.locator(".mascote-glow").evaluate("e=>e.style.filter")
        assert "hue-rotate(" in hue_filter and hue_filter != "hue-rotate(0deg)"
        assert fixture.locator(".mascote-art").evaluate("e=>getComputedStyle(e).filter") == "none"
        mascot.evaluate("e=>e.dataset.glowMode='green'")
        results["rgb_only_glow"] = True
        fixture.evaluate("document.activeElement.blur()")
        fixture.mouse.move(10, 10)
        assert fixture.locator(".mascote-head, .mascote-eyes, .mascote-breathe").count() == 0
        results["whole_image_tracking"] = True
        fixture.emulate_media(reduced_motion="reduce")
        fixture.mouse.move(100, 200)
        fixture.wait_for_timeout(300)
        reduced_count = fixture.evaluate("probe.frames")
        fixture.mouse.move(300, 200)
        fixture.wait_for_timeout(300)
        assert fixture.evaluate("probe.frames") == reduced_count
        assert fixture.locator(".mascote-shadow").evaluate("e=>getComputedStyle(e).animationName") == "none"
        mascot.hover()
        expect(fixture.locator(".mascote-hover")).to_have_css("opacity", "1")
        assert glow.evaluate('e=>getComputedStyle(e).animationName') == 'none'
        assert glow.evaluate('e=>getComputedStyle(e).opacity') == '0.75'
        results["reduced_motion"] = True
        fixture.emulate_media(reduced_motion="no-preference")
        fixture.evaluate("Object.defineProperty(document,'hidden',{configurable:true,value:true});document.dispatchEvent(new Event('visibilitychange'))")
        hidden_count = fixture.evaluate("probe.frames")
        fixture.mouse.move(400, 200)
        fixture.wait_for_timeout(300)
        assert fixture.evaluate("probe.frames") == hidden_count
        assert "is-hidden" in mascot.get_attribute("class")
        results["hidden_pauses"] = True
        fixture.evaluate("Object.defineProperty(document,'hidden',{configurable:true,value:false});document.dispatchEvent(new Event('visibilitychange'))")
        fixture.mouse.move(20, 20)
        fixture.wait_for_timeout(1500)
        fixture.screenshot(path=str(evidence / "idle-desktop.png"))
        results["tracking"] = fixture.evaluate("probe")

        mobile = browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
        touch_page = mobile.new_page()
        touch_page.goto(args.url + "/login", wait_until="networkidle")
        mb = touch_page.locator("#vettech-mascote")
        assert mb.bounding_box()["width"] == 96
        before = touch_page.locator(".mascote-tracking").evaluate("e=>e.style.transform")
        mb.dispatch_event("pointermove", {"pointerType": "touch", "clientX": 20, "clientY": 20})
        touch_page.wait_for_timeout(200)
        assert touch_page.locator(".mascote-tracking").evaluate("e=>e.style.transform") == before
        touch_page.evaluate("window.clicks=0;window.addEventListener('vettech:mascote-click',()=>clicks++)")
        mb.tap()
        assert touch_page.evaluate("clicks") == 1
        # Real touchStart/touchEnd through Chromium for pressed-state verification.
        cdp = mobile.new_cdp_session(touch_page)
        box = mb.bounding_box()
        cdp.send("Input.dispatchTouchEvent", {"type": "touchStart", "touchPoints": [{"x": box["x"]+48, "y": box["y"]+48}]})
        expect(mb).to_have_class(re.compile("is-pressed"))
        cdp.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []})
        touch_page.screenshot(path=str(evidence / "mobile.png"))
        results["touch"] = True

        missing_hover = context.new_page()
        missing_hover.route("**/mascote/mascote_hover.png", lambda r:r.abort())
        missing_hover.goto(args.url + "/login", wait_until="networkidle")
        mh=missing_hover.locator('#vettech-mascote')
        expect(mh).to_have_class(re.compile('assets-ready'))
        mh.hover()
        missing_hover.wait_for_timeout(300)
        assert missing_hover.locator('.mascote-idle').evaluate('e=>getComputedStyle(e).opacity')=='1'
        assert missing_hover.locator('.mascote-hover').evaluate('e=>getComputedStyle(e).opacity')=='0'
        assert missing_hover.locator('.mascote-glow').evaluate('e=>Number(getComputedStyle(e).opacity)')>0
        results['missing_hover_keeps_idle']=True
        led_page = context.new_page()
        led_page.goto(args.url + "/login", wait_until="networkidle")
        led_page.locator('#vettech-mascote').hover()
        led_page.wait_for_timeout(4250)
        led_page.screenshot(path=str(evidence / "led-login.png"))

        fallback = context.new_page()
        fallback.route("**/mascote/*.png", lambda r: r.abort())
        fallback.goto(args.url + "/login", wait_until="networkidle")
        fb = fallback.locator("#vettech-mascote")
        expect(fb).to_be_visible()
        assert "assets-ready" not in fb.get_attribute("class")
        assert fallback.locator(".mascote-fallback").evaluate("e=>getComputedStyle(e).opacity") == "1"
        results["fallback"] = True
        browser.close()
    (evidence / "results.json").write_text(json.dumps(results, indent=2))
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:3000")
    parser.add_argument("--chromium")
    parser.add_argument("--authenticated", action="store_true")
    parser.add_argument("--evidence", default="/tmp/vet-tech-mascote-evidence")
    run(parser.parse_args())
