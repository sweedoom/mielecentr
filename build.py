# -*- coding: utf-8 -*-
"""
Сборка лендинга «ремонт техники Miele» из копии msk.mielecentr.ru.
Правишь config.json -> python build.py -> готовый сайт в docs/
"""
import json, os, re, shutil, sys, subprocess
from pathlib import Path
# Общий помощник сборки: клиент заявок и админка. Подключается по пути
# ../backend ТОЛЬКО во время сборки (в docs/ из backend ничего не копируется).
_BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))
import build_clients  # noqa: E402

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
MIRROR = os.path.join(SRC, "mirror")
OUT = os.path.join(ROOT, "docs")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

cfg = json.load(open(os.path.join(ROOT, "config.json"), encoding="utf-8"))
C = cfg["city"]
L = cfg["leads"]
B = cfg["brand"]
TH = cfg.get("theme", {}) or {}
ACCENT = (TH.get("accent") or "#a3000a").strip()
ACCENT_D = (TH.get("accentDark") or "#7a0008").strip()
GREENS = ("#48a216", "#00966D", "#00966d", "#0f5132", "#3d8b12", "#0b7a52")
ASSET_EXT = (".css", ".js", ".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif", ".ico",
             ".woff", ".woff2", ".ttf", ".eot", ".json", ".txt")


def log(m):
    print(m)


# ------------------------------------------------------------------ ассеты
_RECOLOR_N = 0


def recolor(css_text):
    """Зелёный акцент шаблона -> акцентный цвет из конфига."""
    global _RECOLOR_N
    out = css_text
    for g in GREENS:
        c = out.count(g)
        if c:
            out = out.replace(g, ACCENT)
            _RECOLOR_N += c
    return out


def copy_assets():
    os.makedirs(OUT, exist_ok=True)
    n = 0
    for root, _dirs, files in os.walk(MIRROR):
        rel = os.path.relpath(root, MIRROR)
        dst_dir = OUT if rel == "." else os.path.join(OUT, rel)
        os.makedirs(dst_dir, exist_ok=True)
        for f in files:
            src_f = os.path.join(root, f)
            if f.lower().endswith(".css"):
                try:
                    t = open(src_f, encoding="utf-8", errors="ignore").read()
                except Exception:
                    t = None
                if t is not None:
                    t2 = recolor(t)
                    with open(os.path.join(dst_dir, f), "w", encoding="utf-8") as fh:
                        fh.write(t2)
                    n += 1
                    continue
            shutil.copy2(src_f, os.path.join(dst_dir, f))
            n += 1
    log(f"[assets] скопировано файлов: {n}")
    if _RECOLOR_N:
        log(f"[theme] зелёный -> {ACCENT}: замен {_RECOLOR_N}")
    return n


def make_logo(path):
    """Логотип собирает logo.py: он измеряет текст настоящим движком браузера,
    поэтому подпись точно совпадает по ширине со словом. Если Playwright
    недоступен — грубый fallback того же дизайна."""
    py = sys.executable  # тот же интерпретатор, что запустил build.py
    try:
        r = subprocess.run([py, os.path.join(ROOT, "logo.py")],
                           check=True, cwd=ROOT, capture_output=True, text=True)
        for line in (r.stdout or "").strip().splitlines():
            log("  " + line.strip())
        if os.path.isfile(path):
            return
    except Exception as e:
        log("[logo] logo.py недоступен (%s) — грубый расчёт" % str(e)[:80])

    # fallback: слово + подпись, ширина по средней ширине символа
    word = (cfg.get("logoWord") or "Miele").strip()
    sub = (cfg.get("logoSub") or "Фирменный сервисный центр техники").strip().upper()
    fs1 = float(cfg.get("logoWordSize") or 46)
    tr = float(cfg.get("logoSubTracking") or 1.6)
    w1 = len(word) * fs1 * 0.62
    n = max(len(sub) - 1, 1)
    fs2 = max(7.0, min(13.0, (w1 - n * tr) / (len(sub) * 0.62)))
    w = round(max(w1, len(sub) * fs2 * 0.62 + n * tr) + 2)
    y1, y2 = round(fs1 * 0.8), round(fs1 * 0.8 + fs1 * 0.14 + fs2 * 1.05)
    h = y2 + 2
    for kind, name in (("header", cfg.get("logo") or "assets/logo.svg"),
                       ("footer", cfg.get("logoFooter") or "assets/logo-footer.svg")):
        cw, cs = ("#1b1b1b", "#6d6d6d") if kind == "header" else ("#ffffff", "#a8a8a8")
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'<text x="0" y="{y1}" font-family="Arial, Helvetica, sans-serif" font-size="{fs1:.0f}" '
            f'font-weight="700" letter-spacing="-0.5" fill="{cw}">{word}'
            f'<tspan fill="{ACCENT}">.</tspan></text>'
            f'<text x="0" y="{y2}" font-family="Arial, Helvetica, sans-serif" font-size="{fs2:.2f}" '
            f'letter-spacing="{tr}" fill="{cs}">{sub}</text></svg>')
        p = os.path.join(OUT, name.replace("/", os.sep))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w", encoding="utf-8").write(svg)
    log("[logo] создан (fallback)")


# ------------------------------------------------------------------ html
h = open(os.path.join(SRC, "original.html"), encoding="utf-8", errors="ignore").read()
orig_len = len(h)
SITE = cfg["siteUrl"].rstrip("/") + "/"

# 1. свои адреса вместо чужих (до вырезания домена)
h = h.replace("https://msk.mielecentr.ru/", SITE)
h = h.replace("http://msk.mielecentr.ru/", SITE)
h = h.replace("//msk.mielecentr.ru/", SITE)

# 2. списки CSS/JS, которые Битрикс подгружал сам — сохраняем до удаления скриптов
CSS_LIST, JS_LIST = [], []
for m in re.finditer(r"BX\.setCSSList\(\[([^\]]+)\]", h):
    CSS_LIST += re.findall(r"'([^']+)'", m.group(1))
for m in re.finditer(r"BX\.setJSList\(\[([^\]]+)\]", h):
    JS_LIST += re.findall(r"'([^']+)'", m.group(1))


def uniq(seq):
    out = []
    for s in seq:
        if s not in out:
            out.append(s)
    return out


CSS_LIST = uniq(CSS_LIST)
JS_LIST = uniq([p for p in JS_LIST
                if not p.startswith("/bitrix/js/")
                and p != "/lib/feedback/feedback.js"
                and "popup.link" not in p])

# 3. чужие счётчики и битрикс-ядро
def is_junk(s):
    return any(k in s for k in ("BX.setJSList", "BX.setCSSList", "window.BX", "BX.message",
                                "_ba.push", "calltouch", "mc.yandex", "quizgo")) or \
           re.search(r'src="[^"]*/bitrix/(?:js|cache/js)/', s) is not None


h, n = re.subn(r"<script\b[^>]*>.*?</script>",
               lambda m: "" if is_junk(m.group(0)) else m.group(0), h, flags=re.S | re.I)
log(f"[clean] удалено чужих/битрикс-скриптов: {n}")
h = re.sub(r"<noscript><div><img src=\"https://mc\.yandex\.ru/watch/\d+\".*?</noscript>", "", h, flags=re.S)
h = re.sub(r'<link[^>]+href="[^"]*/bitrix/js/main/popup/[^"]*"[^>]*>', "", h)

# 4. вырезаем квиз стороннего сервиса
def drop_block(h, tag, cls):
    n = 0
    pat = re.compile(r"<%s[^>]*class=\"[^\"]*%s[^\"]*\"[^>]*>" % (tag, re.escape(cls)))
    o_r, c_r = re.compile(r"<%s\b[^>]*>" % tag), re.compile(r"</%s\s*>" % tag)
    while True:
        m = pat.search(h)
        if not m:
            break
        depth, pos, guard, end = 0, m.start(), 0, None
        while guard < 50000:
            guard += 1
            o, c = o_r.search(h, pos), c_r.search(h, pos)
            if not c:
                break
            if o and o.start() < c.start():
                if h[o.end() - 2:o.end()] != "/>":
                    depth += 1
                pos = o.end()
            else:
                depth -= 1
                pos = c.end()
                if depth == 0:
                    end = pos
                    break
        if end is None:
            break
        h = h[:m.start()] + h[pos:]
        n += 1
    return h, n


for spec in cfg.get("dropBlocks", []):
    tag, _, cls = spec.partition(".")
    h, k = drop_block(h, tag, cls)
    if k:
        log(f"[clean] вырезан {spec}: {k} шт.")

# 4b. выкидываем HTML-комментарии (мёртвый текст из исходника, в т.ч. чужие описания).
# Условные комментарии IE (<!--[if ...]>) не трогаем.
h = re.sub(r"<!--(?!\[if).*?-->", "", h, flags=re.S)

# 4c. абзацы-дисклеймеры (например «не является официальным представителем»)
for kw in cfg.get("dropParagraphs", []):
    h, k = re.subn(r"<p\b[^>]*>[^<]*" + re.escape(kw) + r"[^<]*</p>", "", h, flags=re.I)
    if k:
        log(f"[clean] удалён абзац с «{kw}»: {k} шт.")
    else:
        log(f"[clean] НЕ НАЙДЕН абзац с «{kw}»")

# 5. подключаем CSS/JS явно (Битрикс больше их не подгружает)
css_local, js_local = [], []
for p in CSS_LIST:
    loc = p.lstrip("/")
    if os.path.isfile(os.path.join(MIRROR, loc.replace("/", os.sep))):
        css_local.append(loc)
    else:
        log(f"[warn] нет файла: {loc}")
for p in JS_LIST:
    loc = p.lstrip("/")
    if os.path.isfile(os.path.join(MIRROR, loc.replace("/", os.sep))):
        js_local.append(loc)
    else:
        log(f"[warn] нет файла: {loc}")
css_html = "".join(f'<link href="{p}" type="text/css" rel="stylesheet" />\n' for p in css_local)
js_html = "".join(f'<script src="{p}"></script>\n' for p in js_local)
log(f"[assets] css: {len(css_local)}, js: {len(js_local)}")

# 6. ссылки: страницы -> заглушки/якоря, файлы -> локальные
LINK_MAP = {
    "/kontakty/politika-konfidentsialnosti/": "politika.html",
    "/sitemap/": None,
}
SERVICE = cfg.get("serviceLinks", "#")


def fix_ref(m):
    attr, url = m.group(1), m.group(2)
    if url.startswith(("http", "//", "#", "mailto:", "tel:", "javascript:", "data:")):
        return m.group(0)
    if not url.startswith("/"):
        return m.group(0)
    path = url.split("?")[0].split("#")[0]
    if path in LINK_MAP:
        return LINK_MAP[path] and f'{attr}="{LINK_MAP[path]}"' or ""
    if path.lower().endswith(ASSET_EXT) or path.startswith(("/bitrix/", "/upload/", "/lib/")):
        return f'{attr}="{url[1:]}"'
    if path == "/":
        return f'{attr}="index.html"'
    if path.startswith("/uslugi/"):
        return f'{attr}="{SERVICE}"'
    return f'{attr}="{cfg["internalLinks"]}"'


h = re.sub(r'(src|href)="([^"]*)"', fix_ref, h)
h = re.sub(r"url\((/upload/[^)]*)\)", lambda m: "url(%s)" % m.group(1)[1:], h)
h = re.sub(r"url\((/bitrix/[^)]*)\)", lambda m: "url(%s)" % m.group(1)[1:], h)

# 7. меню на якоря этой же страницы
def fix_nav(m):
    txt = re.sub(r"<[^>]+>", "", m.group(0))
    txt = re.sub(r"\s+", " ", txt).strip()
    tgt = cfg.get("navTargets", {}).get(txt)
    if tgt:
        return re.sub(r'href="[^"]*"', f'href="{tgt}"', m.group(0), count=1)
    return m.group(0)


h = re.sub(r"<a\b[^>]*>.*?</a>", fix_nav, h, flags=re.S)

# 8. юридическая информация -> страница реквизитов, «Карта сайта» долой
h = re.sub(r'<a href="javascript:void\(0\);"\s+class="btn btn-primary popup-link"\s+'
           r'data-popup-id="1">\s*Юридическая информация\s*</a>',
           '<a href="requisites.html" class="btn btn-primary">Юридическая информация</a>', h)
h = re.sub(r'href="politika\.html">Политика конфиденциальности</a>',
           'href="politika.html">Политика конфиденциальности</a>\n'
           '<a href="requisites.html">Реквизиты</a>', h, count=1)

# 8b. ссылка «Карта сайта» вела в несуществующий раздел — убираем её совсем
h = re.sub(r'<a\s*>(?:(?!</a>).)*?Карта сайта\s*</a>', '', h, flags=re.S)

# 8c. юрлицо в подвале: «Юрлицо: ООО «ХОЛОДОК», ИНН 7452172713»
if cfg.get("footerLegal", True):
    CO = cfg.get("company", {}) or {}
    bits = []
    if CO.get("shortName"):
        bits.append("Юрлицо: " + CO["shortName"])
    if CO.get("inn"):
        bits.append("ИНН " + CO["inn"])
    if bits:
        legal = ", ".join(bits)
        h, k = re.subn(r'(<a href="requisites\.html">Реквизиты</a>)',
                       r'\1<br><p class="legal">%s</p>' % legal, h, count=1)
        if k:
            log(f"[legal] в подвал добавлено: {legal}")

# 9. якорь для блока услуг
h = h.replace('<div class="uslugi_index">', '<div class="uslugi_index" id="uslugi">', 1)

# 10. контакты: сначала почта, потом бренд (иначе бренд съест домен)
h = re.sub(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]*mielecentr\.ru", cfg["email"], h)
_holodok = "ХОЛОД-ОК"  # ← сюда можно вписать своё название, если понадобится
if B:
    # порядок важен: сначала составные фразы, иначе останется мусор вида «БРЕНД Center»
    h = h.replace("Сервисный центр Miele (Миле)", f"Сервисный центр {B}: ремонт техники Miele (Миле)")
    h = h.replace("Сервисный центр Miele Center", f"Сервисный центр {B}")
    h = h.replace("сервисный центр Miele Center", f"сервисный центр {B}")
    h = h.replace("Сервисный центр Miele ", f"Сервисный центр {B} ")
    h = h.replace("Miele Center", B)
    h = h.replace("Miele Центр", B)
    h = h.replace("Miele Service", B)
else:
    # названия компании нет — используем формулировку из cfg.brandPhrase
    PH = (cfg.get("brandPhrase") or "Сервисный центр").strip()
    PH_l = PH[0].lower() + PH[1:]          # для серединки предложения
    h = h.replace("Сервисный центр Miele (Миле)  в", PH + " в")
    h = h.replace("Сервисный центр Miele (Миле) в", PH + " в")
    h = h.replace("Сервисный центр Miele  в", PH + " в")
    h = h.replace("Miele (Миле)  ", "Miele (Миле) ")  # двойные пробелы из исходника
    h = h.replace("Miele Service кнопка домой", "Кнопка домой")
    h = h.replace("Сервисный центр Miele Center", PH)
    h = h.replace("сервисный центр Miele Center", PH_l)
    h = h.replace("В Miele Center", "В " + PH_l)
    h = h.replace("Miele Center", PH)
    h = h.replace("Miele Центр", PH)
    h = h.replace("Miele Service", PH)
slug = (cfg.get("brandSlug") or "").strip()
if slug:
    h = h.replace("mielecentr", slug)
h = h.replace("+7 (495) 877-14-12", cfg["phonePretty"])
h = h.replace("+74958771412", cfg["phoneRaw"])

# 11. город по падежам (длинные формы раньше коротких)
h = h.replace("Москве", C["prep"]).replace("Москвы", C["gen"])
h = h.replace("Москвой", C["abl"]).replace("Москву", C["acc"]).replace("Москва", C["nom"])

# 12. текстовые правки (до вырезания адреса — иначе фраза уже не совпадёт)
for a, b in cfg.get("textFixes", []):
    if a in h:
        h = h.replace(a, b)
        log(f"[text] «{a[:45]}…» → «{b[:45]}…»")
    else:
        log(f"[text] НЕ НАЙДЕНО: {a[:60]}")

# 13. адрес: он нам не нужен — работаем только с выездом мастера
addr = (cfg.get("address") or "").strip()
h = h.replace("г. Москва, улица 1905 года, д 3", addr)
h = h.replace("г. Москва, Учительская, 16Б", addr)
if not addr:
    for pat in (r'<div id="headadr">.*?</div>',
                r'<div id="footer_address">.*?</div>',
                r'<div class="hdslide_contact_email">.*?</div>\s*</div>'):
        h = re.sub(pat, "", h, flags=re.S)
    log("[addr] адрес не задан — все блоки с адресом вырезаны")
h = h.replace("Ежедневно: с 08:00 до 00:00", cfg["workHours"])

# 14. логотип: шапка и футер получают СВОИ версии (тёмная/светлая),
#     фактические размеры подставим после генерации SVG (ниже, перед записью)
h = h.replace('src="log2.svg"', f'src="{cfg["logo"]}"')
h = h.replace('src="log.svg"', f'src="{cfg["logo"]}"')
h = h.replace('src="favicon.png"', f'src="{cfg.get("favicon", "favicon.png")}"')

# ------------------------------------------------------------------ инъекции
head_add = ['<script>window.BX=window.BX||{message:function(){},ready:function(f){jQuery(f);}};</script>']
for yid in cfg["counters"].get("yandex", []) or []:
    head_add.append(
        '<script>(function(m,e,t,r,i,k,a){m[i]=m[i]||function(){(m[i].a=m[i].a||[]).push(arguments)};'
        'm[i].l=1*new Date();k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,'
        'k.src=r,a.parentNode.insertBefore(k,a)})(window,document,"script",'
        '"https://mc.yandex.ru/metrika/tag.js","ym");ym(%s,"init",{clickmap:true,trackLinks:true,'
        'accurateTrackBounce:true,webvisor:true});</script>' % yid)
if cfg["counters"].get("gtag"):
    g = cfg["counters"]["gtag"]
    head_add.append(f'<script async src="https://www.googletagmanager.com/gtag/js?id={g}"></script>'
                    f'<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}'
                    f'gtag("js",new Date());gtag("config","{g}");</script>')

lead_html = build_clients.make_lead_script(cfg)
log("[leads] клиент заявок подключён (endpoint: %s)"
    % (build_clients.leads_endpoint(cfg) or "не настроен"))

h = h.replace("</head>", "".join(head_add) + css_html + "</head>")

# мелкие визуальные правки: fancybox-триггеры вместо javascript:; и стиль для строки юрлица
h = h.replace('href="javascript:;"', 'href="#"')          # чище URL, fancybox всё равно перехватит по data-fancybox
h = h.replace(
    "</head>",
    "<style>"
    "p.legal{color:#888;font-size:13px;margin:8px 0 0;line-height:1.4}"
    # мобильный фолбэк: оригинальный шаблон задаёт подвалу ширину больше вьюпорта
    "@media (max-width:768px){"
    "html,body{overflow-x:hidden}"
    "footer #footer_top_main,footer #footer_bottom_main{max-width:100%;box-sizing:border-box;padding:0 12px}"
    "footer .kontakty,footer .company,footer .proekty,footer .dopmenu{width:100%;float:none;margin:0 0 12px}"
    "footer img[width]{max-width:100%;height:auto}"
    "}"
    "</style></head>")

h = h.replace("</body>", js_html + lead_html + "</body>")

# Miele: чистая адаптивная вёрстка (frontend.py). Вызываем сразу после
# подключения клиента заявок: frontend._extract_tail вырезает
# <script>window.SITE_LEADS …</script> и переносит его в новый <body>.
try:
    import frontend
    h = frontend.improve_html(h, cfg)
    log("[frontend] вёрстка улучшена (frontend.improve_html)")
except Exception as e:
    log("[frontend] пропущен: %s" % e)


# ------------------------------------------------------------------ запись
copy_assets()
make_logo(os.path.join(OUT, cfg["logo"].replace("/", os.sep)))


def _svg_w(p):
    try:
        m = re.search(r'width="(\d+)"', open(p, encoding="utf-8").read())
        return int(m.group(1)) if m else 150
    except Exception:
        return 150


# ширина <img> в шапке — по фактической ширине SVG
_w_head = _svg_w(os.path.join(OUT, cfg["logo"].replace("/", os.sep)))
h = re.sub(r'(<img style="width: )\d+(px;" src="assets/logo\.svg")',
           rf'\g<1>{_w_head}\g<2>', h, count=1)
# футер: ВТОРОЙ логотип (светлая версия) и его ширина
_footer_logo = cfg.get("logoFooter") or "assets/logo-footer.svg"
_w_foot = _svg_w(os.path.join(OUT, _footer_logo.replace("/", os.sep)))


def _second_logo(m):
    _second_logo.n += 1
    if _second_logo.n == 2:
        return m.group(1) + str(_w_foot) + m.group(2) + _footer_logo + m.group(4)
    return m.group(0)


_second_logo.n = 0
h = re.sub(r'(<img style="width: )\d+(px;" src=")(assets/logo\.svg)(")',
           _second_logo, h)
log(f"[logo] шапка {cfg['logo']} ({_w_head}px), футер {_footer_logo} ({_w_foot}px)")

with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
    f.write(h)

# админка: страница-шаблон admin_src.html + assets/admin-app.js.
# Отдельного admin/config.js нет — конфигурация уже внутри страницы.
_adm_dst = build_clients.render_admin(ROOT, OUT, cfg)
if _adm_dst:
    log("[admin] %s собран" % os.path.basename(_adm_dst))
else:
    log("[admin] нет шаблона admin_src.html")

# политика / реквизиты / seo
try:
    import subprocess
    subprocess.run([sys.executable, os.path.join(ROOT, "policy.py")], check=True, cwd=ROOT)
    subprocess.run([sys.executable, os.path.join(ROOT, "seo.py")], check=True, cwd=ROOT)
    subprocess.run([sys.executable, os.path.join(ROOT, "render_brand.py")], check=True, cwd=ROOT)
except Exception as e:
    log("[render] ошибка: %s" % e)
open(os.path.join(OUT, ".nojekyll"), "w").write("")

dom = cfg.get("domain")
if dom:
    open(os.path.join(OUT, "CNAME"), "w").write(dom + "\n")
    log(f"[domain] CNAME -> {dom}")

left = len(re.findall(r"mielecentr|Miele Center|Miele Центр", h, re.I))
left_phone = h.count("877-14-12") + h.count("495")
log(f"[html] {orig_len} -> {len(h)} символов")
log(f"[check] осталось чужого: {left}, старых телефонов: {left_phone}")
log(f"[done] сайт собран в {OUT}")
