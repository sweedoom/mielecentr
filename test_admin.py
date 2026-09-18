# -*- coding: utf-8 -*-
"""Тест админки: вход, список, новая заявка -> Telegram, сводка."""
import asyncio, os, sys, subprocess, time, json
sys.stdout.reconfigure(encoding="utf-8")
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(ROOT, "docs")
PORT = 8903
BASE = f"http://127.0.0.1:{PORT}/"
_cfg = json.load(open(os.path.join(ROOT, "config.json"), encoding="utf-8"))
PAGE = (_cfg.get("admin", {}) or {}).get("page") or "admin.html"
PW = (_cfg.get("admin", {}) or {}).get("password") or ""

LEADS = [
    {"id": "11111111-1111-1111-1111-111111111111", "created_at": "2026-09-16T10:20:00+00:00",
     "name": "Иван", "phone": "+7 (999) 111-11-11", "message": "Не греет духовка",
     "source": "Вызвать мастера", "page": "https://linar.me/mielecentr/", "status": "new", "site": "mielecentr"},
    {"id": "22222222-2222-2222-2222-222222222222", "created_at": "2026-09-15T18:05:00+00:00",
     "name": "Ольга", "phone": "+7 (999) 222-22-22", "message": "", "source": "Заказать звонок",
     "page": "https://linar.me/mielecentr/", "status": "work", "site": "mielecentr", "comment": "перезвонить"},
    # старая заявка без тега — опознаётся по слову miele в адресе страницы
    {"id": "44444444-4444-4444-4444-444444444444", "created_at": "2026-09-13T09:00:00+00:00",
     "name": "Мария", "phone": "+7 (999) 444-44-44", "message": "Старая заявка без тега",
     "source": "Заявка с сайта", "page": "https://linar.me/mielecentr/", "status": "done"},
    # ЧУЖАЯ заявка — другого сайта, в этой админке её быть НЕ должно
    {"id": "33333333-3333-3333-3333-333333333333", "created_at": "2026-09-14T09:00:00+00:00",
     "name": "Пётр", "phone": "+7 (999) 333-33-33", "message": "Парогенератор шипит",
     "source": "Заявка с сайта", "page": "https://linar.me/holodok/", "status": "new", "site": "holodok"},
]


async def main():
    srv = subprocess.Popen([sys.executable, "-m", "http.server", str(PORT), "--bind", "127.0.0.1"],
                           cwd=DOCS, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.2)
    errors, tg, ins = [], [], []
    try:
        async with async_playwright() as p:
            b = await p.chromium.launch()
            pg = await b.new_page(viewport={"width": 1440, "height": 950})
            pg.on("console", lambda m: errors.append("CONSOLE %s: %s" % (m.type, m.text[:200]))
                  if m.type == "error" else None)
            pg.on("pageerror", lambda e: errors.append("PAGEERROR: %s" % (e.stack or str(e))[:300]))

            async def mock_tg(route):
                tg.append(json.loads(route.request.post_data or "{}"))
                await route.fulfill(status=200, content_type="application/json",
                                    body='{"ok":true,"result":{"message_id":1}}')
            async def mock_list(route):
                await route.fulfill(status=200, content_type="application/json",
                                    body=json.dumps([{"admin_leads": {"ok": True, "leads": LEADS}}]))
            async def mock_ins(route):
                ins.append(json.loads(route.request.post_data or "{}"))
                await route.fulfill(status=201, content_type="application/json", body="{}")
            await pg.route("**/api.telegram.org/**", mock_tg)
            await pg.route("**/rest/v1/rpc/admin_leads", mock_list)
            await pg.route("**/rest/v1/leads", mock_ins)

            await pg.goto(BASE + PAGE, wait_until="networkidle", timeout=60000)
            await pg.screenshot(path=os.path.join(ROOT, "adm_login.png"))
            await pg.fill("#pw", PW)
            await pg.click("#loginBtn")
            await pg.wait_for_timeout(1200)
            await pg.screenshot(path=os.path.join(ROOT, "adm_leads.png"))

            rows = await pg.locator("#tb tr").count()
            print("СТРОК В ТАБЛИЦЕ:", rows, "(ждём 3: свои 2 + старая своя; чужая holodok скрыта)")
            print("СТАТ-КАРТОЧКИ:", await pg.locator("#cards .v").all_inner_texts())

            # фильтр «Новые»
            await pg.click('.chip[data-s="new"]')
            await pg.wait_for_timeout(400)
            print("ПОСЛЕ ФИЛЬТРА «Новые»:", await pg.locator("#tb tr").count())

            # карточка заявки
            await pg.click('.chip[data-s=""]')
            await pg.wait_for_timeout(300)
            await pg.locator('#tb button[data-act="open"]').first.click()
            await pg.wait_for_timeout(500)
            await pg.screenshot(path=os.path.join(ROOT, "adm_drawer.png"))
            await pg.click("#dTg")
            await pg.wait_for_timeout(900)
            await pg.click("#dClose")
            await pg.wait_for_timeout(400)

            # новая заявка из админки
            await pg.click("#btnAdd")
            await pg.wait_for_timeout(300)
            await pg.fill("#mName", "Пётр")
            await pg.fill("#mPhone", "+7 (999) 555-55-55")
            await pg.fill("#mMsg", "Посудомойка не сливает")
            await pg.screenshot(path=os.path.join(ROOT, "adm_modal.png"))
            await pg.click("#mSave")
            await pg.wait_for_timeout(1500)
            print("ВСТАВКА В ХРАНИЛИЩЕ:", json.dumps(ins[-1] if ins else None, ensure_ascii=False))

            # сводка
            await pg.click('.side nav a[data-v="stats"]')
            await pg.wait_for_timeout(700)
            await pg.screenshot(path=os.path.join(ROOT, "adm_stats.png"))

            # настройки + тест связи
            await pg.click('.side nav a[data-v="set"]')
            await pg.wait_for_timeout(400)
            await pg.click("#btnTest")
            await pg.wait_for_timeout(1200)
            print("РЕЗУЛЬТАТ ТЕСТА:", await pg.inner_text("#testRes"))
            await pg.screenshot(path=os.path.join(ROOT, "adm_set.png"))

            print("\n--- СООБЩЕНИЯ В TELEGRAM (%d) ---" % len(tg))
            for t in tg:
                print(t.get("chat_id"), "|", (t.get("text") or "").replace("\n", " / "))
    finally:
        srv.terminate()

    print("\n--- ОШИБКИ КОНСОЛИ (%d) ---" % len(errors))
    for e in errors[:15]:
        print(" ", e)


if __name__ == "__main__":
    asyncio.run(main())
