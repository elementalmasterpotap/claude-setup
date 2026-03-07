#!/usr/bin/env python3
"""
Stop hook: anti-rationalization gate.
Блокирует Клода если в финальном ответе обнаружены фразы-отмазки.
Документация: https://code.claude.com/docs/en/hooks#stop
"""
import sys, json

COP_OUTS = [
    # RU
    'за рамками задачи', 'за пределами задачи',
    'нужно больше контекста для того', 'нужно больше информации',
    'этот баг существовал до', 'баг существовал до меня',
    'эта проблема существовала до',
    'не могу выполнить без дополнительного',
    'это не входит в мою задачу',
    'для этого нужен доступ к',
    # EN
    'out of scope', 'beyond the scope',
    'need more context to complete',
    'pre-existing issue', 'pre-existing bug',
    'this issue existed before',
    'requires further investigation to',
    'cannot complete without additional',
    "that's outside my",
]

try:
    data = json.load(sys.stdin)

    # КРИТИЧНО: если хук уже активен — не зацикливаться
    if data.get('stop_hook_active', False):
        sys.exit(0)

    text = data.get('last_assistant_message', '').lower()

    found = [c for c in COP_OUTS if c.lower() in text]

    if found:
        result = {
            "decision": "block",
            "reason": (
                f"⚠️ Обнаружена отмазка: «{found[0]}»\n"
                "Задача не выполнена — продолжай работу.\n"
                "Если есть реальное техническое ограничение — "
                "объясни конкретно: какой файл, какая строка, какой код, почему невозможно."
            )
        }
        print(json.dumps(result, ensure_ascii=False))

except Exception:
    pass  # любая ошибка — молча пропускаем, не ломаем работу

sys.exit(0)
