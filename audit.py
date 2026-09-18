# -*- coding: utf-8 -*-
"""Полный аудит готового сайта: ошибки, ссылки, картинки, вёрстка, формы."""
import asyncio, os, sys, subprocess, time, json
sys.stdout.reconfigure(encoding="utf-8")
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(ROOT, "docs")
PORT = 8901
BASE = f"http://127.0.0.1:{PORT}/"


async def main():
    srv = subprocess.Popen([sys.executable, "-m", "http.server", str(PORT), "--bind", "127.0.0.1"],
                           cwd=DOCS, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.2)
    errs, failed, tg = [], [], []
    try:
        async with async_playwright() as p:
            b = await p.chromium.launch()

            async def mock(route):
                body = json.loads(route.request.post_data or "{}")
                tg.append(body)
                await route.fulfill(status=200, content_type="application/json",
                                    body='{"ok":true,"result":{"message_id":1}}')
            for vw, vh, tag, mob in ((1440, 900, "desktop", False), (390, 844, "mobile", True)):
                pg = await b.new_page(viewport={"width": vw, "height": vh},
                                      is_mobile=mob, has_touch=mob)
                pg.on("console", lambda m, t=tag: errs.append(f"[{t}] CONSOLE {m.type}: {m.text[:180]}")
                      if m.type == "error" else None)
                pg.on("pageerror", lambda e, t=tag: errs.append(f"[{t}] PAGEERROR: {(e.stack or str(e))[:260]}"))
                pg.on("requestfailed", lambda r, t=tag: failed.append(f"[{t}] {r.url[:110]} :: {r.failure}"))
                await pg.route("**/api.telegram.org/**", mock)
                await pg.route("**/supabase.co/rest/v1/leads", mock)

                await pg.goto(BASE, wait_until="networkidle", timeout=60000)
                await pg.wait_for_timeout(1200)

                # 1. горизонтальный скролл
                ov = await pg.evaluate(
                    "() => ({sw: document.documentElement.scrollWidth,"
                    " cw: document.documentElement.clientWidth})")
                if ov["sw"] > ov["cw"] + 2:
                    errs.append(f"[{tag}] ГОРИЗОНТАЛЬНЫЙ СКРОЛЛ: {ov['sw']} > {ov['cw']}")

                # 2. битые картинки
                broken = await pg.evaluate("""() => [...document.images]
                    .filter(i => !i.complete || i.naturalWidth === 0)
                    .map(i => i.getAttribute('src'))""")
                for s in broken:
                    errs.append(f"[{tag}] БИТАЯ КАРТИНКА: {s}")

                # 3. дубли id
                dup = await pg.evaluate("""() => {
                    const m = {}; const d = [];
                    document.querySelectorAll('[id]').forEach(e => {
                      m[e.id] = (m[e.id] || 0) + 1; });
                    for (const k in m) if (m[k] > 1) d.push(k + ' x' + m[k]);
                    return d; }""")
                for d in dup:
                    errs.append(f"[{tag}] ДУБЛЬ id: {d}")

                # 4. ссылки, ведущие в никуда (исключаем fancybox-триггеры и якоря)
                dead = await pg.evaluate("""() => [...document.querySelectorAll('a')]
                    .map(a => ({href: a.getAttribute('href'),
                                fb: a.hasAttribute('data-fancybox'),
                                txt: (a.textContent||'').trim().slice(0,40),
                                tag: a.parentElement && a.parentElement.tagName}))
                    .filter(o => {
                      if (o.fb) return false;                 // fancybox-триггер
                      if (o.href && o.href !== '#') return false;
                      if (!o.txt) return false;
                      // "Меню" в мобильной шапке — это div, не ссылка; в скриншоте мог зацепиться
                      if (o.txt.toLowerCase().startsWith('меню')) return false;
                      return true;
                    })""")
                for d in dead:
                    if d["txt"]:
                        errs.append(f"[{tag}] ПУСТАЯ ССЫЛКА: «{d['txt']}» href={d['href']}")

                # 5. элементы, вылезающие за вьюпорт (исключаем клоны owl-карусели и их потомков)
                wide = await pg.evaluate(f"""() => [...document.querySelectorAll('body *')]
                    .filter(e => {{
                        const cn = (e.className||'').toString();
                        if (/owl-(item|stage)/.test(cn)) return false;
                        // пропускаем содержимое слайдов — они by design за вьюпортом
                        let p = e;
                        while (p && p !== document.body) {{
                            const pc = (p.className||'').toString();
                            if (/slideblock|slider-img|slideoverlay|slpart|slidetext|slidetexthd/.test(pc)) return false;
                            p = p.parentElement;
                        }}
                        const r = e.getBoundingClientRect();
                        return r.width > 0 && (r.right > {vw} + 4 || r.left < -4);
                    }})
                    .slice(0, 6)
                    .map(e => e.tagName + '.' + (e.className||'').toString().slice(0,40)
                         + ' [' + Math.round(e.getBoundingClientRect().left) + '..'
                         + Math.round(e.getBoundingClientRect().right) + ']')""")
                for w in wide:
                    errs.append(f"[{tag}] ВЫЛЕЗАЕТ: {w}")

                await pg.screenshot(path=os.path.join(ROOT, f"audit_{tag}_top.png"))
                await pg.screenshot(path=os.path.join(ROOT, f"audit_{tag}.png"), full_page=True)
                await pg.close()
            await b.close()
    finally:
        srv.terminate()

    print("=== ОШИБКИ (%d) ===" % len(errs))
    for e in errs[:40]:
        print("  ", e)
    print("\n=== НЕ ЗАГРУЗИЛОСЬ (%d) ===" % len(failed))
    for f in failed[:20]:
        print("  ", f)
    print("\n=== КАНАЛЫ: %d ===" % len(tg))


asyncio.run(main())
