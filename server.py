"""
server.py — PocketFlow 'coding-agent' cookbookiga asoslangan MINIMAL demo server.

MAQSAD: pocketflow-coding-agent/nodes.py dagi ReadFile/ListFiles/RunCommand
tool'larini "real dunyoda" qanday ochilishi mumkinligini ko'rsatish — masalan,
kimdir shu cookbook'ni HTTP API qilib o'raydi (bu juda keng tarqalgan pattern:
"AI coding agent as a service").

Bu server LLM'ni chaqirmaydi — o'rniga /tool endpoint orqali to'g'ridan-to'g'ri
JSON bilan "tool_call" yuborish mumkin, xuddi frontend/LLM orkestratori buni
avtomatik yuborgandek. Bu orqali zaiflikni tarmoq darajasida isbotlaymiz.

FAQAT LOCALHOST'DA, FAQAT SIZNING TEST MUHITINGIZDA ISHLATING.
"""

import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# server.py PocketFlow repo ICHIDA joylashgan deb hisoblanadi
# (masalan ~/cve/PocketFlow/server.py), shuning uchun cookbook papkasi
# shu faylning yonida bo'ladi:
sys.path.insert(0, os.path.join(SCRIPT_DIR, "cookbook", "pocketflow-coding-agent"))

from fastapi import FastAPI
from pydantic import BaseModel
from nodes import ReadFile, ListFiles, GrepSearch, RunCommand  # noqa: E402

app = FastAPI(title="PocketFlow Coding-Agent Demo Server (VULNERABLE - PoC only)")

# Bu "agent" ishlashi kerak bo'lgan sandbox katalog — real deploymentda
# odatda foydalanuvchi repo'si shu yerga clone qilinadi.
WORKDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "workdir"))

TOOLS = {
    "read_file": ReadFile(),
    "list_files": ListFiles(),
    "grep_search": GrepSearch(),
    "run_command": RunCommand(),
}


class ToolCallRequest(BaseModel):
    tool: str
    args: dict


@app.post("/tool")
def call_tool(req: ToolCallRequest):
    """
    Bu endpoint LLM/orkestrator 'tool_call' qarorini qabul qilib,
    tegishli ToolNode.exec() ni chaqiradi — xuddi haqiqiy agentda bo'lgani kabi.
    HECH QANDAY qo'shimcha tekshiruv yo'q (original kodda ham yo'q edi).
    """
    tool = TOOLS.get(req.tool)
    if not tool:
        return {"error": f"Unknown tool: {req.tool}"}

    shared = {
        "tool_call": {"tool": req.tool, "args": req.args},
        "workdir": WORKDIR,
    }
    prep = tool.prep(shared)
    try:
        result = tool.exec(prep)
        return {"result": result}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


@app.get("/")
def root():
    return {
        "status": "running",
        "workdir": WORKDIR,
        "note": "POST /tool with {tool, args} — see poc_remote.py",
    }
