# -*- coding: utf-8 -*-
"""Проверка свободных .ru доменов через raw-whois (порт 43, whois.tcinet.ru)."""
import socket, sys, re, time
sys.stdout.reconfigure(encoding="utf-8")

SERVER = "whois.tcinet.ru"      # реестр .ru/.рф
FREE_MARKERS = ("no entries found", "not found", "status: free", "ничего не найдено")


def whois(domain, server=SERVER, port=43, timeout=10):
    try:
        s = socket.create_connection((server, port), timeout=timeout)
        s.sendall((domain + "\r\n").encode("ascii", "ignore"))
        buf = b""
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            buf += chunk
        s.close()
        return buf.decode("utf-8", "ignore")
    except Exception as e:
        return "ERR " + str(e)


def is_free(text):
    low = text.lower()
    if low.startswith("err"):
        return None
    return any(m in low for m in FREE_MARKERS)


if __name__ == "__main__":
    cands = [d.strip() for d in (sys.argv[1:] or []) if d.strip()]
    free, taken, err = [], [], []
    for d in cands:
        r = whois(d)
        st = is_free(r)
        if st is None:
            err.append(d)
            print(f"?      {d}  ({r[:60]})")
        elif st:
            free.append(d)
            print(f"СВОБОДЕН  {d}")
        else:
            taken.append(d)
            print(f"занят     {d}")
        time.sleep(0.4)
    print(f"\n--- ИТОГ: свободных {len(free)}, занятых {len(taken)}, ошибок {len(err)} ---")
    if free:
        print("СВОБОДНЫЕ:", ", ".join(free))
