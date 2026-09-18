# -*- coding: utf-8 -*-
"""
Логотип SVG с ТОЧНОЙ подгонкой текста.

Почему не «на глаз»: ширина кириллицы в Arial Bold считается по-разному в
зависимости от регистра и буквы, поэтому эвристика вида «длина * 0.62» даёт
то обрезку, то пустую половину блока. Здесь ширина каждой строки измеряется
реальным движком браузера (canvas measureText), а строки дополнительно
разбиваются так, чтобы быть почти одинаковой длины — блок выглядит ровным.
"""
import asyncio, json, os, sys
sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.abspath(__file__))
cfg = json.load(open(os.path.join(ROOT, "config.json"), encoding="utf-8"))

FONT = '700 100px "Arial", "Helvetica", sans-serif'


def want_lines():
    t1 = (cfg.get("logoText") or "").strip()
    t2 = (cfg.get("logoText2") or "").strip()
    if t1 and t2:
        return [t1, t2]
    src = (t1 or t2 or (cfg.get("brand") or "").strip()
           or cfg.get("brandPhrase") or cfg.get("tagline") or "Сервисный центр").strip()
    if not t1 and not t2:
        return balance(src)
    return [t1] if t1 else [t2]


def balance(phrase, n=2):
    """Разбить фразу на n строк максимально равной длины (по словам)."""
    words = phrase.split()
    if len(words) <= n:
        return words
    best, best_diff = None, None
    # перебираем все позиции разбиения на n частей
    def rec(parts, idx):
        nonlocal best, best_diff
        if idx == len(words):
            if len(parts) == n:
                lens = [len(" ".join(p)) for p in parts]
                diff = max(lens) - min(lens)
                if best_diff is None or diff < best_diff:
                    best, best_diff = [" ".join(p) for p in parts], diff
            return
        for take in (1, 2, 3):
            if idx + take > len(words):
                break
            rec(parts + [words[idx:idx + take]], idx + take)
    rec([], 0)
    return best or [phrase]


async def measure(lines):
    """Вернуть ширину каждой строки при font-size 100 (в px)."""
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page()
        await pg.set_content("<canvas id='c'></canvas>")
        w = await pg.evaluate(
            """([lines, font]) => {
                 const c = document.getElementById('c').getContext('2d');
                 c.font = font;
                 return lines.map(s => c.measureText(s).width);
               }""", [lines, FONT])
        await b.close()
        return w


def build_svg(lines, widths100, target_w, pad, accent, lh_k=1.16):
    """fs подбирается так, чтобы самая длинная строка точно влезла в target_w."""
    maxw100 = max(widths100)
    fs = target_w / (maxw100 / 100.0)
    fs = max(9.0, min(fs, 28.0))   # одна короткая строка не должна раздувать блок
    line_h = fs * lh_k
    h = round(pad * 2 + line_h * len(lines))
    w = round(target_w + pad * 2)
    out = []
    for i, s in enumerate(lines):
        y = pad + line_h * (i + 1) - fs * 0.24
        natural = widths100[i] / 100.0 * fs
        # ровняем правый край по самой длинной строке: только межбуквенные
        # интервалы, глифы не растягиваем. Сильно короткие строки не трогаем.
        if natural < target_w * 0.72:
            tl_attr = ""
        else:
            tl_attr = f' textLength="{target_w}" lengthAdjust="spacing"'
        out.append(
            f'<text x="{pad}" y="{y:.1f}" font-family="Arial, Helvetica, sans-serif" '
            f'font-size="{fs:.2f}" font-weight="700" fill="#ffffff"'
            f'{tl_attr}>{s}</text>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
           f'viewBox="0 0 {w} {h}" role="img">'
           f'<rect width="{w}" height="{h}" rx="10" fill="{accent}"/>'
           + "".join(out) + '</svg>')
    return svg, w, h


async def main():
    lines = want_lines()
    theme = cfg.get("theme", {}) or {}
    accent = theme.get("accent") or "#a3000a"
    width = int(cfg.get("logoWidth") or 250)
    pad = int(cfg.get("logoPad") or 14)
    target = width - pad * 2 - 12          # 12px — место под акцентную полоску слева
    widths = await measure(lines)
    svg, w, h = build_svg(lines, widths, target, pad, accent)
    path = os.path.join(ROOT, "docs", (cfg.get("logo") or "assets/logo.svg").replace("/", os.sep))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8").write(svg)
    print(f"[logo] {len(lines)} строки, {w}x{h}px, fs~{widths and (target/(max(widths)/100)):.1f}")
    for s, ww in zip(lines, widths):
        print(f"       «{s}» → {ww/100*(target/(max(widths)/100)):.0f}px из {target}px")


if __name__ == "__main__":
    asyncio.run(main())
