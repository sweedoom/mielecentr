import re, os, sys
sys.stdout.reconfigure(encoding="utf-8")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")
h = open(os.path.join(OUT, "index.html"), encoding="utf-8", errors="ignore").read()
# убираем HTML-комментарии — в исходнике бывают закомментированные блоки с битыми ссылками
h_chk = re.sub(r"<!--.*?-->", "", h, flags=re.S)

refs = set()
for m in re.finditer(r'(?:src|href)="([^"]+)"', h_chk):
    refs.add(m.group(1))
for m in re.finditer(r'srcset="([^"]+)"', h_chk):
    for p in m.group(1).split(","):
        refs.add(p.strip().split(" ")[0])
for m in re.finditer(r"url\((['\"]?)([^)'\"]+)", h_chk):
    refs.add(m.group(2))

missing, local, ext = [], 0, 0
for r in sorted(refs):
    if r.startswith(("http", "#", "mailto", "tel", "data:", "javascript:")):
        ext += 1
        continue
    local += 1
    p = os.path.join(OUT, r.split("?")[0].replace("/", os.sep))
    if not os.path.exists(p):
        missing.append(r)

print(f"всего ссылок: {len(refs)} | локальных: {local} | внешних/якорей: {ext}")
print(f"БИТЫХ (файла нет): {len(missing)}")
for m in missing[:25]:
    print("   ", m)
print()
print("внешние ресурсы (должны быть CDN):")
for r in sorted(refs):
    if r.startswith("http"):
        print("   ", r)
