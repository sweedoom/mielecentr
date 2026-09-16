# -*- coding: utf-8 -*-
"""Генерит favicon и og-image под бренд через Playwright."""
import os, sys, json, asyncio
sys.stdout.reconfigure(encoding="utf-8")
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "docs")
cfg = json.load(open(os.path.join(ROOT, "config.json"), encoding="utf-8"))
brand = cfg["brand"]
city = cfg["city"]["nom"]


def html_og():
    return f"""<!doctype html><html><head><meta charset='utf-8'><style>
html,body{{margin:0;height:100%}}
body{{display:flex;align-items:center;justify-content:center;font-family:Inter,Arial,sans-serif;color:#fff;
background:linear-gradient(135deg,#00966D 0%,#0f5132 100%)}}
.wrap{{text-align:center;padding:60px}}
.b{{font-size:120px;font-weight:800;letter-spacing:-2px}}
.s{{font-size:42px;font-weight:500;margin-top:30px;opacity:.95}}
.t{{font-size:32px;margin-top:80px;opacity:.85}}
</style></head><body><div class='wrap'>
<div class='b'>{brand}</div>
<div class='s'>{cfg.get("tagline","Сервисный центр")}</div>
<div class='t'>{city} · {cfg["phonePretty"]}</div>
</div></body></html>"""


def html_fav():
    letter = (brand[:1] or "B").upper()
    return f"""<!doctype html><html><head><meta charset='utf-8'><style>
html,body{{margin:0;height:100%}}
body{{display:flex;align-items:center;justify-content:center;font-family:Inter,Arial,sans-serif;color:#fff;background:#00966D}}
.b{{font-size:200px;font-weight:800;line-height:1}}
</style></head><body><div class='b'>{letter}</div></body></html>"""


async def main():
    os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 1200, "height": 630})
        await pg.set_content(html_og())
        await pg.wait_for_timeout(150)
        await pg.screenshot(path=os.path.join(OUT, "assets", "og-default.jpg"),
                            type="jpeg", quality=88)
        pg = await b.new_page(viewport={"width": 64, "height": 64})
        await pg.set_content(html_fav())
        await pg.wait_for_timeout(100)
        await pg.screenshot(path=os.path.join(OUT, "favicon.png"))
        await b.close()
    print("[render] og + favicon готовы")

asyncio.run(main())