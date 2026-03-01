#!/usr/bin/env python3
"""
Stop hook: patchnote format check.
Правило workflow_universal.md §Патчнот:
  - Заголовок: ## Патч vX.X.X — YYYY-MM-DD
  - Tagline в курсиве (*...*) обязателен
  - От первого лица: убрал / прикрутил / поймал
"""
import sys, json, re

HEADER_RE  = re.compile(r'^##\s+Патч\s+v\d+\.\d+', re.MULTILINE | re.IGNORECASE)
TAGLINE_RE = re.compile(r'^\*[^*\n]+\*\s*$', re.MULTILINE)  # строка *курсив*

# Маркеры третьего лица / не от первого
THIRD_PERSON = [
    'было добавлено', 'была добавлена', 'было исправлено', 'была исправлена',
    'было реализовано', 'была реализована', 'изменения были',
]

try:
    data = json.load(sys.stdin)
    if data.get('stop_hook_active', False):
        sys.exit(0)

    text = data.get('last_assistant_message', '')

    # Срабатывает только если это патчнот
    if not HEADER_RE.search(text):
        sys.exit(0)

    issues = []
    if not TAGLINE_RE.search(text):
        issues.append("нет tagline в курсиве (*Одна строка — суть патча*)")

    found_third = [p for p in THIRD_PERSON if p in text.lower()]
    if found_third:
        issues.append(f"не от первого лица: «{found_third[0]}» → «убрал / прикрутил / поймал»")

    if issues:
        print(json.dumps({
            "decision": "block",
            "reason": (
                "⚠️ Патчнот не по формату:\n"
                + "\n".join(f"  · {i}" for i in issues) +
                "\nПравило workflow_universal.md §Патчнот"
            )
        }, ensure_ascii=False))

except Exception:
    pass

sys.exit(0)
