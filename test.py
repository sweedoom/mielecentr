# -*- coding: utf-8 -*-
"""Smoke-тест готового сайта: скриншоты, ошибки консоли, работа форм."""
import asyncio, os, sys, subprocess, time, json
sys.stdout.reconfigure(encoding="utf-8")
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(ROOT, "docs")
PORT = 8899
BASE = f"http://127.0.0.1:{PORT}/"


async def main():
    srv = subprocess.Popen([sys.executable, "-m", "http.server", str(PORT), "--bind", "127.0.0.1"],
                           cwd=DOCS, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.2)
    errors, failed, tg = [], [], []
    try:
        async with async_playwright() as p:
            b = await p.chromium.launch()
            pg = await b.new_page(viewport={"width": 1440, "height": 900})
            pg.on("console", lambda m: errors.append("CONSOLE %s: %s" % (m.type, m.text[:200]))
                  if m.type == "error" else None)
            pg.on("pageerror", lambda e: errors.append("PAGEERROR: %s" % (e.stack or str(e))[:300]))
            pg.on("requestfailed", lambda r: failed.append("%s %s" % (r.url[:120], r.failure)))

            async def mock(route):
                body = json.loads(route.request.post_data or "{}")
                tg.append(body)
                await route.fulfill(status=200, content_type="application/json",
                                    body='{"ok":true,"result":{"message_id":1}}')
            await pg.route("**/api.telegram.org/**", mock)
            await pg.route("**/rest/v1/leads**", mock)

            await pg.goto(BASE, wait_until="networkidle", timeout=60000)
            await pg.wait_for_timeout(1500)
            await pg.screenshot(path=os.path.join(ROOT, "shot_top.png"))
            await pg.screenshot(path=os.path.join(ROOT, "shot_full.png"), full_page=True)

            # попап-форма «Заказать звонок»
            try:
                await pg.click("text=Заказать звонок", timeout=4000)
                await pg.wait_for_selector("#form_callback_popup", state="visible", timeout=4000)
                await pg.fill('#form_callback_popup input[name="form_name"]', "ТестПоп")
                await pg.fill('#form_callback_popup input[name="form_phone"]', "+7 (999) 111-22-33")
                await pg.locator('#form_callback_popup button[type="submit"]').click()
                await pg.wait_for_timeout(2200)
                await pg.screenshot(path=os.path.join(ROOT, "shot_popup_after.png"))
                # закрываем попап, чтобы не мешал основной форме
                try:
                    await pg.evaluate("if(window.jQuery&&jQuery.fancybox)jQuery.fancybox.close()")
                except Exception:
                    pass
                await pg.wait_for_timeout(500)
                print("POPUP FORM: отправок в канал =", sum(1 for x in tg))
            except Exception as e:
                errors.append("POPUP: %s" % str(e)[:240])

            # основная форма
            try:
                # прокручиваем и пробуем обычный клик, если мешает оверлей — через JS
                await pg.evaluate("document.getElementById('form_vopros_expert').scrollIntoView({block:'center'})")
                await pg.wait_for_timeout(400)
                await pg.fill('#form_vopros_expert input[name="form_name"]', "Тест")
                await pg.fill('#form_vopros_expert input[name="form_phone"]', "+7 (999) 584-43-58")
                before = len(tg)
                try:
                    await pg.locator('#form_vopros_expert button[type="submit"]').click(timeout=3000)
                except Exception:
                    await pg.evaluate("document.querySelector('#form_vopros_expert button[type=submit]').click()")
                await pg.wait_for_timeout(2200)
                txt = await pg.inner_text("#form_vopros_expert")
                await pg.screenshot(path=os.path.join(ROOT, "shot_form.png"))
                print("MAIN FORM:", txt.replace("\n", " | ")[:240])
                print("MAIN FORM: новых отправок =", len(tg) - before)
            except Exception as e:
                errors.append("FORM: %s" % str(e)[:300])

            await pg.close()
            pg = await b.new_page(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
            pg.on("pageerror", lambda e: errors.append("M-PAGEERROR: %s" % str(e)[:200]))
            await pg.goto(BASE, wait_until="networkidle", timeout=60000)
            await pg.wait_for_timeout(1200)
            await pg.screenshot(path=os.path.join(ROOT, "shot_mobile.png"))
            await pg.screenshot(path=os.path.join(ROOT, "shot_mobile_full.png"), full_page=True)
            await b.close()
    finally:
        srv.terminate()

    print("\n--- ОТПРАВЛЕНО ВО ВНЕШНИЕ КАНАЛЫ: %d ---" % len(tg))
    for t in tg:
        print("  ", json.dumps(t, ensure_ascii=False)[:240])
    print("\n--- ОШИБКИ (%d) ---" % len(errors))
    for e in errors[:25]:
        print("  ", e)
    print("\n--- НЕ ЗАГРУЗИЛОСЬ (%d) ---" % len(failed))
    for f in failed[:25]:
        print("  ", f)


asyncio.run(main())