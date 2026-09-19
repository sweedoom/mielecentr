# -*- coding: utf-8 -*-
"""robots.txt, sitemap.xml, 404.html — то, что нужно при реальном хостинге."""
import os, json, sys
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "docs")
cfg = json.load(open(os.path.join(ROOT, "config.json"), encoding="utf-8"))
SITE = cfg["siteUrl"].rstrip("/") + "/"
TODAY = date.today().isoformat()
_ACC = (cfg.get("theme", {}) or {}).get("accent", "#a3000a")
_ACC_D = (cfg.get("theme", {}) or {}).get("accentDark", "#7a0008")


def main():
    adm_page = (cfg.get("admin", {}) or {}).get("page") or "admin.html"
    robots = (
        "User-agent: *\n"
        "Allow: /\n"
        f"Disallow: /{adm_page}\n"
        "Disallow: /bitrix/\n"
        "Disallow: /upload/\n"
        "\n"
        f"Sitemap: {SITE}sitemap.xml\n"
        f"Host: {SITE}\n"
    )
    open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8").write(robots)

    pages = [("index.html", "1.0"), ("politika.html", "0.3"),
             ("soglasie.html", "0.3"), ("requisites.html", "0.2")]
    urls = "".join(
        f"  <url>\n    <loc>{SITE}{p}</loc>\n    <lastmod>{TODAY}</lastmod>\n"
        f"    <priority>{pr}</priority>\n  </url>\n" for p, pr in pages)
    sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
               f"{urls}</urlset>\n")
    open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8").write(sitemap)

    brand = (cfg.get("brand") or "").strip() or cfg.get("tagline") or "Сервисный центр"
    phone = cfg["phonePretty"]
    notfound = f"""<!doctype html>
<html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Страница не найдена — {brand}</title>
<meta name="robots" content="noindex">
<link rel="icon" href="favicon.png">
<style>
body{{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;
font-family:Arial,sans-serif;color:#fff;background:linear-gradient(135deg,{_ACC},{_ACC_D});text-align:center}}
.box{{padding:40px}}
h1{{font-size:96px;margin:0;line-height:1}}
p{{font-size:20px;opacity:.95}}
a{{display:inline-block;margin-top:24px;padding:14px 32px;background:#fff;color:{_ACC};
border-radius:8px;text-decoration:none;font-weight:700}}
</style></head><body><div class="box">
<h1>404</h1><p>Такой страницы нет</p>
<a href="index.html">На главную</a>
<p style="font-size:16px;margin-top:28px">{brand} · {phone}</p>
</div></body></html>
"""
    open(os.path.join(OUT, "404.html"), "w", encoding="utf-8").write(notfound)
    print("[seo] robots.txt + sitemap.xml + 404.html готовы")


if __name__ == "__main__":
    main()