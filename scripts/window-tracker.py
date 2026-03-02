#!/usr/bin/env python3
"""
UserPromptSubmit хук: отслеживает 5-часовое окно Pro тарифа.

Pro: сброс rolling каждые 5 часов от ПЕРВОГО сообщения (не от полуночи).
Стратегия: знать сколько времени осталось → планировать задачи.

Пишет в ~/.claude/tasks/.window_start время первого сообщения окна.
Инжектирует предупреждение когда < 30 минут до сброса или после сброса.
"""
import sys, json, os
from pathlib import Path
from datetime import datetime, timedelta

WINDOW_FILE = Path.home() / ".claude" / "tasks" / ".window_start"
WINDOW_HOURS = 5
WARN_MINUTES = 30  # warn когда осталось меньше

def get_window_info():
    now = datetime.now()
    try:
        start_ts = float(WINDOW_FILE.read_text().strip())
        start = datetime.fromtimestamp(start_ts)
        elapsed = now - start
        remaining = timedelta(hours=WINDOW_HOURS) - elapsed

        if remaining.total_seconds() < 0:
            # Окно сбросилось — начинаем новое
            WINDOW_FILE.write_text(str(now.timestamp()))
            return "new", timedelta(hours=WINDOW_HOURS)

        return "active", remaining
    except Exception:
        # Первое сообщение окна
        WINDOW_FILE.parent.mkdir(exist_ok=True)
        WINDOW_FILE.write_text(str(now.timestamp()))
        return "new", timedelta(hours=WINDOW_HOURS)

try:
    payload = json.loads(sys.stdin.read())

    status, remaining = get_window_info()
    remaining_minutes = int(remaining.total_seconds() / 60)

    hints = []

    if status == "new":
        # Новое окно — просто фиксируем, не мешаем
        pass
    elif remaining_minutes <= WARN_MINUTES:
        # Мало осталось → hint
        hints.append(
            f"⚠️ PRO WINDOW: осталось ~{remaining_minutes} мин. "
            "Заверши текущую задачу или /compact перед сбросом. "
            f"После сброса (через ~{remaining_minutes} мин) новые 44K токенов."
        )

    if hints:
        print(json.dumps({
            "injectedSystemPrompt": " ".join(hints)
        }, ensure_ascii=False))

except Exception:
    pass

sys.exit(0)
