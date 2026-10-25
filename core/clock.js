// Virtual clock for live, rAF-driven widgets (hairline figures). performance.now and requestAnimationFrame follow the
// GSAP timeline instead of the wall clock, so every rendered frame is deterministic. Figures mount at their scene start
// and can be "driven" by a pointer path keyed to timeline seconds. A backwards seek replays from 0.
(function () {
  let now = 0, q = [], id = 0;
  const realNow = performance.now.bind(performance);
  performance.now = () => now;
  window.requestAnimationFrame = (cb) => { q.push([++id, cb]); return id; };
  window.cancelAnimationFrame = (k) => { q = q.filter((e) => e[0] !== k); };
  window.__figs = [];   // {el, name, start, opts, path: [[t, x, y]], leave, mounted, handle, left}
  const ease = (u) => u * u * (3 - 2 * u);
  function drive(f, t) {
    if (!f.mounted && t >= f.start && window.__hairline) {
      const read = f.el.parentElement.querySelector(".figread");
      f.handle = window.__hairline[f.name](f.el, Object.assign({ theme: "light" }, f.opts, read ? { onRead: (s) => { read.textContent = s; } } : {}));
      f.mounted = true; f.left = false;
    }
    if (!f.mounted || !f.path.length) return;
    const p = f.path, svg = f.el.querySelector("svg") || f.el;
    if (t < p[0][0]) return;
    if (t > p[p.length - 1][0]) {
      if (f.leave && !f.left) { f.left = true; [svg, f.el].forEach((n) => n.dispatchEvent(new PointerEvent("pointerleave", { pointerType: "mouse" }))); }
      return;
    }
    let k = 0; while (k < p.length - 2 && t > p[k + 1][0]) k++;
    const a = p[k], b = p[k + 1] || a, u = b[0] > a[0] ? ease(Math.min(1, (t - a[0]) / (b[0] - a[0]))) : 1;
    const x = a[1] + (b[1] - a[1]) * u, y = a[2] + (b[2] - a[2]) * u, r = svg.getBoundingClientRect();
    svg.dispatchEvent(new PointerEvent("pointermove", { bubbles: true, pointerType: "mouse", clientX: r.left + x * r.width, clientY: r.top + y * r.height }));
  }
  function reset() {
    window.__figs.forEach((f) => { if (f.mounted) { f.handle.destroy(); f.mounted = false; } });
    now = 0; q = [];
  }
  window.__advance = (ms) => {
    if (ms < now - 1) reset();
    while (now < ms - 0.01) {
      now = Math.min(ms, now + 1000 / 120);
      window.__figs.forEach((f) => drive(f, now / 1000));
      const run = q; q = []; run.forEach((e) => e[1](now));
    }
  };
})();
