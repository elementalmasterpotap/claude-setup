#!/usr/bin/env python3
"""
Публикация патчнота как отдельной Telegraph страницы.
Берёт первый (свежий) блок из PATCHNOTES.md и создаёт новую страницу.

Использование:
  python3 ~/.claude/scripts/publish-patchnote.py [путь к PATCHNOTES.md]

По умолчанию ищет docs/PATCHNOTES.md в текущей директории.
"""
import urllib.request, json, os, sys, re

TOKEN = os.environ.get("TELEGRAPH_TOKEN")
if not TOKEN:
    print("Error: TELEGRAPH_TOKEN not set", file=sys.stderr); sys.exit(1)

# ── Найти PATCHNOTES.md ───────────────────────────────────────────
patchnotes_path = sys.argv[1] if len(sys.argv) > 1 else "docs/PATCHNOTES.md"
if not os.path.exists(patchnotes_path):
    print(f"Error: {patchnotes_path} not found", file=sys.stderr); sys.exit(1)

text = open(patchnotes_path, encoding="utf-8").read()

# ── Извлечь первый патчнот (до второго ## Патч) ───────────────────
blocks = re.split(r'\n(?=## Патч)', text)
if not blocks:
    print("Error: нет патчнотов в файле", file=sys.stderr); sys.exit(1)

block = blocks[0].strip()
if not block:
    block = blocks[1].strip() if len(blocks) > 1 else ""

# Вытащить заголовок и версию
title_match = re.match(r'## (Патч\s+\S+.*?)(?:\n|$)', block)
title = title_match.group(1) if title_match else "Патчнот"

# ── Markdown → Telegraph nodes ────────────────────────────────────
def md_to_nodes(md: str) -> list:
    nodes = []
    lines = md.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]

        # Заголовок (## — h3, ### — h4)
        if line.startswith("### "):
            nodes.append({"tag": "h4", "children": [line[4:].strip()]})
        elif line.startswith("## "):
            nodes.append({"tag": "h3", "children": [line[3:].strip()]})

        # Курсив *tagline*
        elif line.startswith("*") and line.endswith("*") and len(line) > 2:
            nodes.append({"tag": "p", "children": [{"tag": "i", "children": [line[1:-1]]}]})

        # Список
        elif line.startswith("- "):
            items = []
            while i < len(lines) and lines[i].startswith("- "):
                items.append({"tag": "li", "children": [_inline(lines[i][2:])]})
                i += 1
            nodes.append({"tag": "ul", "children": items})
            continue

        # HR ---
        elif line.strip() == "---":
            nodes.append({"tag": "hr"})

        # Обычный параграф
        elif line.strip():
            nodes.append({"tag": "p", "children": [_inline(line.strip())]})

        i += 1
    return nodes

def _inline(text: str):
    """Обрабатывает **bold**, `code` внутри строки."""
    # Если нет разметки — возвращаем строку
    if "**" not in text and "`" not in text:
        return text
    # Простой парсинг: разбиваем на куски
    parts = []
    i = 0
    while i < len(text):
        if text[i:i+2] == "**":
            end = text.find("**", i+2)
            if end != -1:
                parts.append({"tag": "b", "children": [text[i+2:end]]})
                i = end + 2
                continue
        elif text[i] == "`":
            end = text.find("`", i+1)
            if end != -1:
                parts.append({"tag": "code", "children": [text[i+1:end]]})
                i = end + 1
                continue
        # Накапливаем обычный текст
        j = i
        while j < len(text) and text[j:j+2] != "**" and text[j] != "`":
            j += 1
        if j > i:
            parts.append(text[i:j])
        i = j
    return parts if len(parts) > 1 else (parts[0] if parts else text)

nodes = md_to_nodes(block)

# ── Опубликовать на Telegraph ──────────────────────────────────────
data = json.dumps({
    "access_token": TOKEN,
    "title": title,
    "author_name": "Potap",
    "author_url": "https://t.me/potap_attic",
    "content": nodes,
    "return_content": False
}).encode("utf-8")

req = urllib.request.Request(
    "https://api.telegra.ph/createPage",
    data=data,
    headers={"Content-Type": "application/json"}
)
result = json.loads(urllib.request.urlopen(req).read())

if result.get("ok"):
    url = result["result"]["url"]
    print(url)
else:
    print(f"Error: {result}", file=sys.stderr)
    sys.exit(1)
