#!/usr/bin/env python3
"""
Stop hook: Telegraph — только editPage для лонгрида, не createPage.
                       curl + кириллица = CONTENT_TEXT_REQUIRED.
Правило telegraph.md.
"""
import sys, json, re

LONGREAD_PATH = "Kak-ya-kastomiziruyu-Claude-pravila-pamyat-i-moduli-03-01"

CREATE_RE     = re.compile(r'\bcreate[Pp]age\b')
CURL_TG_RE    = re.compile(r'curl\b.*telegra\.ph', re.IGNORECASE | re.DOTALL)
CYRILLIC_RE   = re.compile(r'[а-яА-ЯёЁ]')

CODE_BLOCK_RE = re.compile(r'```.*?```', re.DOTALL)

try:
    data = json.load(sys.stdin)
    if data.get('stop_hook_active', False):
        sys.exit(0)

    text   = data.get('last_assistant_message', '')
    blocks = CODE_BLOCK_RE.findall(text)
    code   = '\n'.join(blocks)

    # createPage упомянут в контексте лонгрида
    if LONGREAD_PATH in text and CREATE_RE.search(text):
        print(json.dumps({
            "decision": "block",
            "reason": (
                "⛔ Лонгрид — только editPage, никогда createPage!\n"
                "Правило telegraph.md: один файл, обновляется в месте, не пересоздаётся."
            )
        }, ensure_ascii=False))

    # curl + кириллица в коде (любой Telegraph)
    elif code and CURL_TG_RE.search(code) and CYRILLIC_RE.search(code):
        print(json.dumps({
            "decision": "warn",
            "reason": (
                "⚠️ curl + кириллица + Telegraph = CONTENT_TEXT_REQUIRED!\n"
                "Правило telegraph.md: для кириллицы — только Python urllib, не curl."
            )
        }, ensure_ascii=False))

except Exception:
    pass

sys.exit(0)
