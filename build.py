# -*- coding: utf-8 -*-
"""
Сборка лендинга «ремонт техники Miele» из копии msk.mielecentr.ru.
Правишь config.json -> python build.py -> готовый сайт в docs/
"""
import json, os, re, shutil, sys, base64, subprocess

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
    поэтому строки ровные и ничего не обрезается. Если Playwright недоступен —
    грубый fallback по той же формуле."""
    venv_py = r"C:\Users\Cypher\.workbuddy-ai\binaries\python\envs\default\Scripts\python.exe"
    py = venv_py if os.path.isfile(venv_py) else sys.executable
    try:
        r = subprocess.run([py, os.path.join(ROOT, "logo.py")],
                           check=True, cwd=ROOT, capture_output=True, text=True)
        for line in (r.stdout or "").strip().splitlines():
            log("  " + line.strip())
        if os.path.isfile(path):
            log("[logo] создан (точная подгонка): %s" % cfg.get("logo", "assets/logo.svg"))
            return
    except Exception as e:
        log("[logo] logo.py недоступен (%s) — грубый расчёт" % str(e)[:80])

    t1 = (cfg.get("brand") or "").strip()
    if t1:
        lines = [t1]
    else:
        lines = [cfg.get("logoText") or cfg.get("tagline") or "Сервисный центр"]
        if cfg.get("logoText2"):
            lines.append(cfg["logoText2"])
    fs = 19 if len(lines) > 1 else 20
    lh = 22
    h_px = 16 + lh * len(lines) + 10
    w = max(220, 16 + max(len(s) for s in lines) * int(fs * 0.68) + 24)
    texts = "".join(
        f'<text x="20" y="{16 + lh * i + 4}" font-family="Arial, sans-serif" font-size="{fs}"'
        f' font-weight="700" fill="#ffffff" textLength="{min(len(s) * fs * 0.66, w - 32):.0f}"'
        f' lengthAdjust="spacingAndGlyphs">{s}</text>' for i, s in enumerate(lines))
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h_px}" viewBox="0 0 {w} {h_px}">'
        f'<rect width="{w}" height="{h_px}" rx="10" fill="{ACCENT}"/>{texts}</svg>')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
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

# 14. логотип (ширина картинки — из cfg.logoWidth, чтобы длинная подпись влезла)
h = h.replace('src="log2.svg"', f'src="{cfg["logo"]}"')
h = h.replace('src="log.svg"', f'src="{cfg["logo"]}"')
h = h.replace('src="favicon.png"', f'src="{cfg.get("favicon", "favicon.png")}"')
_lw = int(cfg.get("logoWidth") or 230)
h = re.sub(r'(<img style="width: )130(px;" src="assets/logo\.svg")', rf'\g<1>{_lw}\g<2>', h)

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

lead_js = """
<script>
window.SITE_LEADS = __LEADS__;
(function(){
  function collect(form){
    var f = jQuery(form);
    var t = jQuery.trim(f.find('.title').first().text());
    return {
      title: t || 'Заявка с сайта',
      name: f.find('[name="form_name"]').val() || '',
      phone: f.find('[name="form_phone"]').val() || '',
      email: f.find('[name="form_email"]').val() || '',
      message: f.find('[name="form_message"]').val() || '',
      page: location.href
    };
  }
  function ok(form){
    var f = jQuery(form);
    var box = f.find('.title').first();
    var THANKS = '<div class="thanks_form" style="color:__ACCENT__;font-weight:700;padding:12px 0">'
               + 'Спасибо! Заявка отправлена, мы перезвоним в течение 5 минут.</div>';
    if (box.length) {
      box.html(THANKS);
    } else {
      f.prepend(THANKS);
    }
    f.find('input, textarea').prop('disabled', true);
    f.find('button').prop('disabled', true);
    setTimeout(function(){ try { jQuery.fancybox.close(); } catch(e){} }, 1800);
  }
  function fail(form, msg){
    var f = jQuery(form);
    var err = f.find('[id^="garant_error"]').first();
    if (err.length) { err.html(msg); } else { alert(msg); }
  }
__TG_FN__
  function postLead(L, d){
    if (!L.sb || !L.sb.url || !L.sb.key) return null;
    var base = {name: d.name, phone: d.phone, message: d.message, source: d.title,
                page: d.page, status: 'new', site: L.site || ''};
    function send(payload){
      return fetch(L.sb.url + '/rest/v1/leads', {
        method: 'POST',
        headers: {apikey: L.sb.key, Authorization: 'Bearer ' + L.sb.key,
                  'Content-Type': 'application/json', Prefer: 'return=minimal'},
        body: JSON.stringify(payload)
      });
    }
    return send(base).then(function(r){
      if (r && r.ok) return r;
      // в старой схеме нет колонки site - кладём тег сайта в utm
      var p2 = {};
      for (var k in base) { if (k !== 'site') p2[k] = base[k]; }
      p2.utm = L.site || '';
      return send(p2);
    }).catch(function(){ return null; });
  }
  jQuery(function($){
    $(document).off('submit.leads').on('submit.leads', 'form.feedback', function(e){
      e.preventDefault();
      e.stopImmediatePropagation();
      var form = this, f = $(form), d = collect(form), L = window.SITE_LEADS;
      var ch = f.find('input[type=checkbox]');
      if (ch.length && !ch.prop('checked')) { fail(form, 'Необходимо дать согласие на обработку данных'); return false; }
      var digits = (d.phone.match(/\\d+/g) || []).join('');
      if (digits.length < 10) { fail(form, 'Введите номер телефона полностью'); return false; }
      var storeP = null;
      if (L.sb && L.sb.url && L.sb.key) {
        storeP = postLead(L, d);
      } else if (L.backend) {
        storeP = fetch(L.backend, {method:'POST', mode:'no-cors',
              headers:{'Content-Type':'text/plain'}, body: JSON.stringify(d)})
              .catch(function(){ return null; });
      }
      if (L.mode === 'telegram' && L.tgToken && L.tgChats && L.tgChats.length) {
        var p = sendTG(d, L);
        (storeP ? Promise.all([p, storeP]) : p).then(function(){ ok(form); },
                                                     function(){ ok(form); });
      } else if (storeP) {
        storeP.then(function(){ ok(form); }, function(){ ok(form); });
      } else {
        __FALLBACK__
      }
      return false;
    });
  });
})();
</script>
"""
_TG_CHATS = [str(c) for c in (L.get("telegramChatIds") or
                              ([L["telegramChatId"]] if L.get("telegramChatId") else []))]
_USE_TG = bool(L.get("mode") == "telegram" and L.get("telegramBotToken") and _TG_CHATS)


def _enc(v):
    return base64.b64encode(str(v or "").encode()).decode()


_SB = cfg.get("admin", {}).get("supabase", {}) or {}
SITE_TAG = (cfg.get("siteTag") or "").strip() or "site"
SRC_NAME = (L.get("sourceName") or cfg.get("siteName") or "Сайт").strip()
_LEADS_CFG = {
    "backend": cfg.get("admin", {}).get("backendUrl", ""),
    "mode": L.get("mode", "mailto"),
    "endpoint": L.get("endpoint", ""),
    "sb": {"url": _SB.get("url", ""), "key": _SB.get("anonKey", "")},
    "site": SITE_TAG,
    "source": SRC_NAME,
}
if _USE_TG:
    _LEADS_CFG["tgToken"] = _enc(L.get("telegramBotToken", ""))
    _LEADS_CFG["tgChats"] = _TG_CHATS
    log(f"[leads] заявки уходят в Telegram, получателей: {len(_TG_CHATS)}")
lead_js = lead_js.replace("__LEADS__", json.dumps(_LEADS_CFG, ensure_ascii=False))

if _USE_TG:
    tg_fn = """
  function sendTG(d, L){
    var text = 'Новая заявка\\\\n' +
               'Источник: ' + (d.source || L.source || '') + '\\\\n' +
               'Форма: ' + d.title + '\\\\n' +
               'Телефон: ' + d.phone +
               (d.name ? '\\\\nИмя: ' + d.name : '') +
               (d.email ? '\\\\nE-mail: ' + d.email : '') +
               (d.message ? '\\\\nСообщение: ' + d.message : '') +
               '\\\\nСтраница: ' + d.page;
    var token = atob(L.tgToken);
    return Promise.all((L.tgChats || []).map(function(chat){
      return fetch('https://api.telegram.org/bot' + token + '/sendMessage', {
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({chat_id: chat, text: text})
      }).catch(function(){ return null; });
    }));
  }"""
    fallback = """
      sendTG(d, L).then(function(){ ok(form); }, function(){
        alert('Не удалось отправить. Позвоните нам или напишите на почту.');
      });"""
elif L.get("mode") == "endpoint" and L.get("endpoint"):
    tg_fn = ""
    fallback = """
      fetch(L.endpoint, {method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify(d)}).then(function(){ ok(form); },
            function(){ alert('Ошибка отправки. Попробуйте позже.'); });"""
else:
    tg_fn = ""
    fallback = """
      window.location.href = 'mailto:__EMAIL__?subject=' + encodeURIComponent(d.title) +
        '&body=' + encodeURIComponent('Телефон: ' + d.phone + (d.name ? ', Имя: ' + d.name : '') +
        (d.message ? ', Сообщение: ' + d.message : '') + '\\\\nСтраница: ' + d.page);
      ok(form);"""

lead_js = lead_js.replace("__TG_FN__", tg_fn).replace("__FALLBACK__", fallback)
lead_js = lead_js.replace("__EMAIL__", cfg["email"]).replace("__ACCENT__", ACCENT)

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

h = h.replace("</body>", js_html + lead_js + "</body>")

# ------------------------------------------------------------------ запись
copy_assets()
make_logo(os.path.join(OUT, cfg["logo"].replace("/", os.sep)))
with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
    f.write(h)

# админка (собирается всегда: с Supabase — общее хранилище, без него — локальный режим)
A = cfg.get("admin", {}) or {}
_sb = A.get("supabase", {}) or {}
_adm_url = A.get("backendUrl", "")
_ADM_PAGE = A.get("page") or "admin.html"
adm_src = os.path.join(ROOT, "admin_src.html")
if os.path.isfile(adm_src):
    tpl = open(adm_src, encoding="utf-8").read()
    b64 = lambda x: base64.b64encode(str(x).encode()).decode()
    _chats = json.dumps(_TG_CHATS if _USE_TG else [])
    _pws, _seen = [], set()
    for _p in (A.get("storePassword") or "", A.get("password") or "", "holodok2026"):
        if _p and _p not in _seen:
            _seen.add(_p)
            _pws.append(_p)
    tpl = (tpl.replace("@STORE_PWS@", json.dumps(_pws, ensure_ascii=False))
              .replace("@LEADS_BACKEND@", _adm_url)
              .replace("@SB_URL_B64@", b64(_sb.get("url", "")))
              .replace("@SB_KEY_B64@", b64(_sb.get("anonKey", "")))
              .replace("@TG_TOKEN_B64@", b64(L.get("telegramBotToken", "") if _USE_TG else ""))
              .replace("@TG_CHATS@", _chats)
              .replace("@SOURCE_MAP@", json.dumps(cfg.get("sourceNames", {}) or {}, ensure_ascii=False))
              .replace("@SITE_TAG@", SITE_TAG)
              .replace("@SOURCE_NAME@", SRC_NAME)
              .replace("@SITE_NAME@", cfg.get("siteName") or cfg.get("brandPhrase") or "Сервисный центр")
              .replace("@SHORT_NAME@", cfg.get("logoText") or cfg.get("siteName") or "Сервисный центр")
              .replace("@PHONE@", cfg.get("phonePretty", ""))
              .replace("@ACCENT@", ACCENT)
              .replace("@ACCENT_DARK@", ACCENT_D)
              .replace("@ADMIN_PW@", A.get("password", "")))
    open(os.path.join(OUT, _ADM_PAGE), "w", encoding="utf-8").write(tpl)
    _mode = "Supabase" if (_sb.get("url") and _sb.get("anonKey")) else "локальный режим"
    log(f"[admin] {_ADM_PAGE} собран (хранилище: {_mode}, уведомления: "
        f"{len(_TG_CHATS) if _USE_TG else 0} получателей)")
else:
    log("[admin] нет шаблона admin_src.html")

# политика / реквизиты / seo
try:
    import subprocess
    subprocess.run([sys.executable, os.path.join(ROOT, "policy.py")], check=True, cwd=ROOT)
    subprocess.run([sys.executable, os.path.join(ROOT, "seo.py")], check=True, cwd=ROOT)
    venv_py = r"C:\Users\Cypher\.workbuddy-ai\binaries\python\envs\default\Scripts\python.exe"
    if os.path.isfile(venv_py):
        subprocess.run([venv_py, os.path.join(ROOT, "render_brand.py")], check=True, cwd=ROOT)
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
