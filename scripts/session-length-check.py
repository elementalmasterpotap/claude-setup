#!/usr/bin/env python3
"""
Stop хук: предупреждение о длинной сессии → hint /compact.

Pro тариф: ~44K токенов / 5 часов, ~45 сообщений.
Длинный last_assistant_message = контекст пухнет = тратим окно быстрее.

Если ответ длинный (>2000 символов) И в нём много инфы → remind /compact.
Мягкое предупреждение раз в несколько ответов (через счётчик в файле).
"""
import sys, json, os
from pathlib import Path

COUNTER_FILE = Path.home() / ".claude" / "tasks" / ".compact_counter"
WARN_EVERY = 5   # напоминать каждые N длинных ответов
LONG_THRESHOLD = 2500  # символов — "длинный ответ"

try:
    data = json.load(sys.stdin)
    if data.get("stop_hook_active", False):
        sys.exit(0)

    text = data.get("last_assistant_message", "")

    if len(text) < LONG_THRESHOLD:
        sys.exit(0)

    # Счётчик длинных ответов
    counter = 0
    try:
        counter = int(COUNTER_FILE.read_text().strip())
    except Exception:
        pass

    counter += 1
    COUNTER_FILE.parent.mkdir(exist_ok=True)
    COUNTER_FILE.write_text(str(counter))

    # Предупреждаем каждые WARN_EVERY раз
    if counter % WARN_EVERY == 0:
        print(json.dumps({
            "decision": "block",
            "reason": (
                f"💡 Сессия набирает вес (длинный ответ #{counter}).\n"
                "Pro лимит: ~44K токенов / 5 часов, ~45 сообщений.\n"
                "Если задача сменилась — /compact или /clear сэкономят лимит:\n"
                "  /compact [сохрани: изменённые файлы, задачи, ключевые решения]\n"
                "  /clear   — полный сброс (когда задача совсем другая)\n"
                "Продолжай ответ — это только напоминание."
            )
        }, ensure_ascii=False))

except Exception:
    pass

sys.exit(0)
