#!/usr/bin/env python3
"""
Stop hook: PowerShell JSON + кириллица → только одинарные кавычки.
Правило PS-1 (lessons_universal.md): ConvertTo-Json экранирует \\uXXXX → ломается Unicode.
"""
import sys, json, re

# Двойные кавычки с кириллицей в $body / $json / $payload
DOUBLE_CYRILLIC_RE = re.compile(
    r'\$(body|json|payload|data)\s*=\s*"[^"]*[а-яА-ЯёЁ][^"]*"'
)
# ConvertTo-Json когда строка содержит кириллицу рядом
CONVERT_RE = re.compile(r'ConvertTo-Json')

PS_BLOCK_RE = re.compile(
    r'```(?:powershell|ps1|ps)\n(.*?)```',
    re.DOTALL | re.IGNORECASE
)

try:
    data = json.load(sys.stdin)
    if data.get('stop_hook_active', False):
        sys.exit(0)

    text = data.get('last_assistant_message', '')
    blocks = PS_BLOCK_RE.findall(text)

    for block in blocks:
        if DOUBLE_CYRILLIC_RE.search(block):
            print(json.dumps({
                "decision": "block",
                "reason": (
                    "⚠️ PS-1: JSON + кириллица в двойных кавычках!\n"
                    "Используй одинарные: $body = '{\"key\":\"\\u0417\\u043d...\"}'\n"
                    "Правило lessons_universal.md §PS-1"
                )
            }, ensure_ascii=False))
            break

        # Если есть ConvertTo-Json И кириллица в том же блоке
        if CONVERT_RE.search(block) and re.search(r'[а-яА-ЯёЁ]', block):
            print(json.dumps({
                "decision": "warn",
                "reason": (
                    "⚠️ PS-1: ConvertTo-Json + кириллица = двойное экранирование!\n"
                    "\\uXXXX → \\\\uXXXX → GitHub видит буквальный текст.\n"
                    "Используй сырую строку в одинарных кавычках."
                )
            }, ensure_ascii=False))
            break

except Exception:
    pass

sys.exit(0)
