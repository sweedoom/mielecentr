# -*- coding: utf-8 -*-
"""
Логотип: чистая типографика вместо цветного блока.

Вид: «Miele» крупно (тёмный) + красная фирменная точка, ниже — подпись
«ФИРМЕННЫЙ СЕРВИСНЫЙ ЦЕНТР ТЕХНИКИ» разрядкой. Две версии:
  assets/logo.svg        — для шапки (тёмный текст на белом фоне)
  assets/logo-footer.svg — для футера (светлый текст на тёмном фоне #222)
Ширина каждой строки измеряется реальным движком браузера (canvas measureText),
поэтому подпись подбирается точно под ширину слова — никаких «на глаз».
"""
import asyncio, json, os, sys
sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.abspath(__file__))
cfg = json.load(open(os.path.join(ROOT, "config.json"), encoding="utf-8"))

WORD_FONT = '700 100px "Arial", "Helvetica", sans-serif'
SUB_FONT = '400 100px "Arial", "Helvetica", sans-serif'


async def measure(word, sub):
    """Ширина строк при font-size 100 (в px)."""
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page()
        await pg.set_content("<canvas id='c'></canvas>")
        w = await pg.evaluate(
            """([word, sub, wf, sf]) => {
                 const c = document.getElementById('c').getContext('2d');
                 c.font = wf;  const wWord = c.measureText(word).width;
                 c.font = sf;  const wSub  = c.measureText(sub).width;
                 return {wWord, wSub};
               }""", [word, sub, WORD_FONT, SUB_FONT])
        await b.close()
        return w["wWord"], w["wSub"]


def build_svg(word, sub, w_word100, w_sub100, kind):
    """kind: 'header' (тёмный на белом) | 'footer' (светлый на #222)."""
    theme = cfg.get("theme", {}) or {}
    accent = theme.get("accent") or "#a3000a"

    fs1 = float(cfg.get("logoWordSize") or 52)
    fs2 = float(cfg.get("logoSubSize") or 10)
    tracking = float(cfg.get("logoSubTracking") or 1.2)

    w_word = w_word100 / 100.0 * fs1
    w_sub = w_sub100 / 100.0 * fs2 + max(len(sub) - 1, 1) * tracking

    if kind == "header":
        c_word, c_sub = "#1b1b1b", "#6d6d6d"
    else:
        c_word, c_sub = "#ffffff", "#a8a8a8"

    w = round(max(w_word, w_sub) + 2)
    y1 = round(fs1 * 0.80)
    y2 = round(y1 + fs1 * 0.16 + fs2)
    h = y2 + 2

    dot = f'<tspan fill="{accent}">.</tspan>'
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="{word}">'
        f'<text x="0" y="{y1}" font-family="Arial, Helvetica, sans-serif" '
        f'font-size="{fs1:.1f}" font-weight="700" letter-spacing="-0.5" fill="{c_word}">'
        f'{word}{dot}</text>'
        f'<text x="0" y="{y2}" font-family="Arial, Helvetica, sans-serif" '
        f'font-size="{fs2:.2f}" font-weight="400" letter-spacing="{tracking}" fill="{c_sub}">{sub}</text>'
        f'</svg>')
    return svg, w, h


async def main():
    word = (cfg.get("logoWord") or "Miele").strip()
    sub = (cfg.get("logoSub") or "ФИРМЕННЫЙ СЕРВИСНЫЙ ЦЕНТР ТЕХНИКИ").strip().upper()
    w_word100, w_sub100 = await measure(word, sub)

    for kind, name in (("header", cfg.get("logo") or "assets/logo.svg"),
                       ("footer", cfg.get("logoFooter") or "assets/logo-footer.svg")):
        svg, w, h = build_svg(word, sub, w_word100, w_sub100, kind)
        path = os.path.join(ROOT, "docs", name.replace("/", os.sep))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, "w", encoding="utf-8").write(svg)
        print(f"[logo:{kind}] {name} — {w}x{h}px")


if __name__ == "__main__":
    asyncio.run(main())
