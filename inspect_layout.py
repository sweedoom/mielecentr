# -*- coding: utf-8 -*-
"""Замер вёрстки шапки: не вылезает ли логотип, не ломает ли блоки."""
import asyncio, os, sys, subprocess, time, json
sys.stdout.reconfigure(encoding="utf-8")
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(ROOT, "docs")
PORT = 8911
BASE = f"http://127.0.0.1:{PORT}/"


async def probe(pg, label):
    r = await pg.evaluate("""() => {
      const out = [];
      const q = (s) => document.querySelector(s);
      const box = (el) => { if (!el) return null;
        const r = el.getBoundingClientRect();
        return {x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height)}; };
      const logo = q('img[src="assets/logo.svg"]');
      // ближайшие контейнеры логотипа
      let p = logo, chain = [];
      for (let i = 0; i < 4 && p.parentElement; i++) {
        p = p.parentElement;
        chain.push({tag: p.tagName, id: p.id, cls: (p.className||'').toString().slice(0,40), box: box(p)});
      }
      // все картинки в шапке
      const hdr = q('#header') || q('header');
      const overlaps = [];
      if (logo && hdr) {
        const lr = logo.getBoundingClientRect(), hr = hdr.getBoundingClientRect();
        if (lr.bottom > hr.bottom + 1) overlaps.push('лого ВЫХОДИТ за низ шапки на ' + Math.round(lr.bottom - hr.bottom) + 'px');
        if (lr.top < hr.top - 1) overlaps.push('лого выше шапки на ' + Math.round(hr.top - lr.top) + 'px');
      }
      // что перекрывает лого (исключая предков)
      if (logo) {
        const lr = logo.getBoundingClientRect();
        document.querySelectorAll('#header a, #header div, #header nav, #header ul, #top_menu *').forEach(el => {
          if (logo.contains(el) || el.contains(logo) || el === logo) return;
          const r = el.getBoundingClientRect();
          if (r.width > 5 && r.height > 5) {
            const ix = Math.max(0, Math.min(r.right, lr.right) - Math.max(r.left, lr.left));
            const iy = Math.max(0, Math.min(r.bottom, lr.bottom) - Math.max(r.top, lr.top));
            if (ix > 8 && iy > 8)
              overlaps.push((el.id ? '#' + el.id : el.tagName) + ' пересекает лого (' + Math.round(ix) + 'x' + Math.round(iy) + 'px)');
          }
        });
      }
      return {
        viewport: {w: innerWidth, h: innerHeight},
        hscroll: document.documentElement.scrollWidth > document.documentElement.clientWidth,
        scrollW: document.documentElement.scrollWidth,
        header: box(hdr),
        logo: box(logo),
        logoAlt: logo ? logo.alt : null,
        parents: chain,
        problems: overlaps.slice(0, 10)
      };
    }""")
    print(f"\n===== {label} =====")
    print(json.dumps(r, ensure_ascii=False, indent=1))


async def main():
    srv = subprocess.Popen([sys.executable, "-m", "http.server", str(PORT), "--bind", "127.0.0.1"],
                           cwd=DOCS, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.2)
    try:
        async with async_playwright() as p:
            b = await p.chromium.launch()
            for w, h, label in ((1440, 900, "ДЕСКТОП 1440"), (390, 844, "МОБИЛА 390")):
                pg = await b.new_page(viewport={"width": w, "height": h})
                await pg.goto(BASE, wait_until="networkidle", timeout=60000)
                await pg.wait_for_timeout(1200)
                await probe(pg, label)
                await pg.screenshot(path=os.path.join(ROOT, f"layout_{w}.png"))
                await pg.close()
            await b.close()
    finally:
        srv.terminate()


if __name__ == "__main__":
    asyncio.run(main())
