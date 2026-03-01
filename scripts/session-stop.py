#!/usr/bin/env python3
"""
Stop hook: session-stop — дописывает в ~/.claude/SESSION.md последний промпт
пользователя и время завершения. Нужен для восстановления контекста после
разрыва соединения.

При reconnect: написать «продолжай» — Claude прочитает SESSION.md.
"""
import sys, json, os
from datetime import datetime
from pathlib import Path

SESSION_FILE = Path.home() / '.claude' / 'SESSION.md'

try:
    data = json.load(sys.stdin)

    # Не зацикливаться если хук уже активен
    if data.get('stop_hook_active', False):
        sys.exit(0)

    transcript_path = data.get('transcript_path', '')
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Читаем последний промпт пользователя из транскрипта
    last_user_msg = ''
    if transcript_path and os.path.exists(transcript_path):
        with open(transcript_path, encoding='utf-8', errors='ignore') as f:
            lines = [l.strip() for l in f if l.strip()]

        for line in reversed(lines):
            try:
                d = json.loads(line)
                if d.get('type') != 'user':
                    continue
                content = d.get('message', {}).get('content', '')
                if isinstance(content, list):
                    for c in content:
                        if isinstance(c, dict) and c.get('type') == 'text':
                            text = c.get('text', '').strip()
                            # Пропускаем system-reminder и tool-result артефакты
                            if text and '<system-reminder>' not in text[:50]:
                                last_user_msg = text[:400]
                                break
                elif isinstance(content, str) and content.strip():
                    if '<system-reminder>' not in content[:50]:
                        last_user_msg = content.strip()[:400]
                if last_user_msg:
                    break
            except Exception:
                pass

    # Читаем SESSION.md, удаляем старый блок --- в конце если есть
    if SESSION_FILE.exists():
        content = SESSION_FILE.read_text(encoding='utf-8')
        # Убираем предыдущий Stop-блок (он всегда после ---)
        if '\n---\n' in content:
            content = content[:content.rfind('\n---\n')]
    else:
        content = f"# SESSION\n**Начато:** {ts}"

    # Дописываем финальный блок
    stop_block = f"\n---\n**Завершено:** {ts}\n"
    if last_user_msg:
        stop_block += f"**Последний промпт:** {last_user_msg}\n"
    if transcript_path:
        stop_block += f"**Транскрипт:** `{transcript_path}`\n"
    stop_block += "\n> При reconnect: напиши **«продолжай»** или **«что делали?»**\n"

    SESSION_FILE.write_text(content.rstrip() + stop_block, encoding='utf-8')

except Exception:
    pass

sys.exit(0)
