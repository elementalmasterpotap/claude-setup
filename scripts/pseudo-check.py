#!/usr/bin/env python3
"""
Stop hook: pseudo-graphics enforcement.
Блокирует ответы с 4+ пунктами списка без псевдографики.
"""
import sys, json, re

# Символы псевдографики
PSEUDO_SYMBOLS = ['├', '└', '│', '═', '╔', '╗', '╚', '╝', '║',
                  '┌', '┐', '┘', '─', '→', '◄', '►', '▼', '▲', '·']
TABLE_RE   = re.compile(r'\|.+\|.+\|')           # markdown-таблица (2+ колонки)
LIST_RE    = re.compile(r'^[ \t]*[-*]\s+\S', re.MULTILINE)
FENCED_RE  = re.compile(r'```.*?```', re.DOTALL)  # вырезать блоки кода

THRESHOLD = 4  # 4+ пунктов → обязательна псевдографика

try:
    data = json.load(sys.stdin)

    if data.get('stop_hook_active', False):
        sys.exit(0)

    text = data.get('last_assistant_message', '')

    # Вырезаем блоки кода — там списки не считаются
    clean = FENCED_RE.sub('', text)

    list_items = LIST_RE.findall(clean)
    has_pseudo = (
        any(s in text for s in PSEUDO_SYMBOLS)
        or TABLE_RE.search(text) is not None
    )

    if len(list_items) >= THRESHOLD and not has_pseudo:
        result = {
            "decision": "block",
            "reason": (
                f"⚠️ {len(list_items)} пунктов списка без псевдографики!\n"
                "Правило: 4+ пунктов → таблица, дерево (├─/└─) или стрелочная схема (→).\n"
                "Переформатируй ответ с псевдографикой."
            )
        }
        print(json.dumps(result, ensure_ascii=False))

except Exception:
    pass

sys.exit(0)
