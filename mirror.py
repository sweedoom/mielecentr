import re, os, time, urllib.request, urllib.parse
from concurrent.futures import ThreadPoolExecutor

BASE = "https://msk.mielecentr.ru"
ROOT = r"G:\SlavaSaitOffer\miele\src"
MIRROR = os.path.join(ROOT, "mirror")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
      "Referer": BASE + "/"}
ASSET_EXT = (".css", ".js", ".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif", ".ico", ".woff", ".woff2", ".ttf", ".eot", ".json", ".txt")


def fetch(url, tries=4):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=40) as r:
                return r.read()
        except Exception as e:
            last = e
            time.sleep(1.5 * (i + 1))
    raise last


def save(path, data):
    full = os.path.join(MIRROR, path.replace("/", os.sep).lstrip(os.sep))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "wb") as f:
        f.write(data)
    return len(data)


def norm(u, base=None):
    u = u.strip()
    if u.startswith("//"):
        return "https:" + u
    if u.startswith("/"):
        return BASE + u
    if u.startswith("http"):
        return u
    if base:
        return urllib.parse.urljoin(base, u)
    return None


html = open(os.path.join(ROOT, "original.html"), encoding="utf-8", errors="ignore").read()
urls = set()
for m in re.finditer(r'(?:src|href|data-src|data-bg|data-original)=["\']([^"\']+)', html):
    urls.add(m.group(1))
for m in re.finditer(r'srcset="([^"]+)"', html):
    for part in m.group(1).split(","):
        urls.add(part.strip().split(" ")[0])
for m in re.finditer(r"url\((['\"]?)([^)'\"]+)", html):
    urls.add(m.group(2))
# Bitrix dynamic CSS/JS lists
for m in re.finditer(r'BX\.set(?:CSS|JS)List\(\[([^\]]+)\]', html):
    for part in re.findall(r"'([^']+)'", m.group(1)):
        urls.add(part)

cands = set()
for u in urls:
    n = norm(u)
    if n and n.startswith(BASE):
        cands.add(n)

# parse css for nested assets (fonts, sprites) — 2 passes
for _ in range(2):
    for c in [u for u in list(cands) if u.split("?")[0].lower().endswith(".css")]:
        try:
            body = fetch(c).decode("utf-8", "ignore")
            for m in re.finditer(r"url\((['\"]?)([^)'\"]+)", body):
                u = m.group(2)
                if u.startswith("data:"):
                    continue
                n = norm(u, base=c)
                if n and n.startswith(BASE):
                    cands.add(n)
        except Exception as e:
            print("CSS FAIL", c, e)

assets = sorted(u for u in cands if u.split("?")[0].lower().endswith(ASSET_EXT))
print("ASSET FILES:", len(assets), flush=True)


def job(u):
    p = urllib.parse.urlparse(u).path
    full = os.path.join(MIRROR, p.replace("/", os.sep).lstrip(os.sep))
    if os.path.exists(full) and os.path.getsize(full) > 0:
        return (u, p, -1)
    try:
        return (u, p, save(p, fetch(u)))
    except Exception as e:
        return (u, p, "ERR %s" % e)


ok = err = 0
fails = []
with ThreadPoolExecutor(max_workers=4) as ex:
    for u, p, res in ex.map(job, assets):
        if isinstance(res, int):
            ok += 1
        else:
            err += 1
            fails.append(u)
            print("FAIL", u, res, flush=True)
print("downloaded ok=%d err=%d" % (ok, err))
open(os.path.join(ROOT, "failed.txt"), "w").write("\n".join(fails))
