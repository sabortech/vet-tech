/* Local-only mascot controller. No Reflex state or network events. */
(() => {
  "use strict";
  if (window.__mascoteInit) return;
  window.__mascoteInit = true;

  function mount() {
    const button = document.getElementById("vettech-mascote");
    if (!button) return false;
    const tracking = button.querySelector(".mascote-tracking");
    const glow = button.querySelector(".mascote-glow");
    const reduced = matchMedia("(prefers-reduced-motion: reduce)");
    let center = { x: 0, y: 0 };
    let target = { x: 0, y: 0 }, current = { x: 0, y: 0 };
    let frame = 0, rgbTimer = 0, hue = 0;
    let hovered = false, focused = false, pressed = false, chatOpen = false;
    const paused = () => chatOpen || hovered || focused || pressed || reduced.matches || document.hidden;
    const timers = () => {
      clearTimeout(rgbTimer);
    };
    const cancel = () => { cancelAnimationFrame(frame); frame = 0; };

    function geometry() {
      const rect = button.getBoundingClientRect();
      center = { x: rect.left + rect.width / 2, y: rect.top + rect.height / 2 };
    }
    function paint() {
      tracking.style.transform = `translate(${current.x * 4}px, ${current.y * 4}px) rotate(${current.x * 4}deg)`;
    }
    function reset() {
      target = { x: 0, y: 0 }; current = { x: 0, y: 0 };
      paint();
    }
    function tick() {
      frame = 0;
      if (paused() || !button.isConnected) return;
      const dx = target.x - center.x, dy = target.y - center.y;
      const radius = Math.max(240, Math.hypot(dx, dy));
      const x = dx / radius, y = dy / radius;
      current.x += (x - current.x) * .16;
      current.y += (y - current.y) * .16;
      paint();
      if (Math.max(Math.abs(x - current.x), Math.abs(y - current.y)) > .001) {
        frame = requestAnimationFrame(tick);
      }
    }
    // Exactly one passive pointermove listener; no DOM reads/writes here.
    window.addEventListener("pointermove", event => {
      if (event.pointerType === "touch" || paused()) return;
      target.x = event.clientX;
      target.y = event.clientY;
      if (!frame) frame = requestAnimationFrame(tick);
    }, { passive: true });
    window.addEventListener("resize", geometry, { passive: true });
    window.addEventListener("scroll", geometry, { passive: true, capture: true });

    function rgb() {
      clearTimeout(rgbTimer);
      if (button.dataset.glowMode !== "rgb") glow.style.filter = "";
      if (document.hidden || reduced.matches || !(chatOpen || hovered || focused || pressed) || button.dataset.glowMode !== "rgb") return;
      // Deliberately no CSS filter animation. Only this small glow changes hue.
      glow.style.filter = `hue-rotate(${hue++ % 360}deg)`;
      rgbTimer = setTimeout(rgb, 200);
    }
    function interaction() {
      button.classList.toggle("is-hovered", hovered);
      button.classList.toggle("is-pressed", pressed);
      button.classList.toggle("is-paused", chatOpen || hovered || focused || pressed);
      cancel();
      reset();
      rgb();
    }
    button.addEventListener("pointerenter", e => { hovered = e.pointerType !== "touch"; interaction(); });
    button.addEventListener("pointerleave", () => { hovered = false; interaction(); });
    button.addEventListener("focus", () => { focused = button.matches(":focus-visible"); interaction(); });
    button.addEventListener("blur", () => { focused = false; pressed = false; interaction(); });
    button.addEventListener("keydown", e => {
      if (e.key === "Enter" || e.key === " ") { focused = true; interaction(); }
    });
    button.addEventListener("pointerdown", e => {
      pressed = true;
      button.setPointerCapture(e.pointerId);
      interaction();
    });
    function release() { pressed = false; interaction(); }
    button.addEventListener("pointerup", release);
    button.addEventListener("pointercancel", release);
    button.addEventListener("lostpointercapture", release);
    button.addEventListener("click", () => window.dispatchEvent(new CustomEvent("vettech:mascote-click")));

    window.addEventListener("vettech:chat-state", event => {
      chatOpen = event.detail.open;
      button.classList.toggle("is-chat-open", chatOpen);
      interaction();
    });

    function preferences() {
      timers(); cancel(); reset();
      button.classList.toggle("is-hidden", document.hidden);
      if (!reduced.matches && !document.hidden) { rgb(); }
      else glow.style.filter = "";
    }
    document.addEventListener("visibilitychange", preferences);
    reduced.addEventListener("change", preferences);

    function assets() {
      const images = [...button.querySelectorAll("img")];
      for (const img of images) img.classList.toggle("is-loaded", img.complete && img.naturalWidth > 0);
      button.classList.toggle("assets-ready", images.filter(img => !img.classList.contains("mascote-hover-image")).every(img => img.classList.contains("is-loaded")));
      button.classList.toggle("hover-ready", images.some(img => img.classList.contains("mascote-hover-image") && img.classList.contains("is-loaded")));
    }
    for (const img of button.querySelectorAll("img")) {
      img.addEventListener("load", assets);
      img.addEventListener("error", assets);
    }
    const preload = new Image();
    preload.decoding = "async";
    preload.src = "/mascote/mascote_hover.png";
    geometry(); assets(); preferences();
    return true;
  }

  function start() {
    if (mount()) return;
    // Hydration can follow the head script. Disconnect as soon as the global
    // wrapper mounts; navigation preserves this wrapper and its listeners.
    const observer = new MutationObserver(() => { if (mount()) observer.disconnect(); });
    observer.observe(document.documentElement, { childList: true, subtree: true });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start, { once: true });
  else start();
})();
