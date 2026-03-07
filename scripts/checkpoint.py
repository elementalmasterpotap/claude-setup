#!/usr/bin/env python3
"""
PostToolUse hook: checkpoint — логирует изменённые файлы в ~/.claude/SESSION.md
Срабатывает на Write и Edit. Хранит историю файлов текущей сессии.
"""
import sys, json
from datetime import datetime
from pathlib import Path

SESSION_FILE = Path.home() / '.claude' / 'SESSION.md'

try:
    data = json.load(sys.stdin)
    tool = data.get('tool_name', '')
    inp  = data.get('tool_input', {})

    if tool not in ('Write', 'Edit'):
        sys.exit(0)

    file_path = inp.get('file_path', '') or ''
    if not file_path:
        sys.exit(0)

    ts    = datetime.now().strftime('%H:%M:%S')
    entry = f"- `{file_path}` [{tool}] {ts}\n"

    if SESSION_FILE.exists():
        content = SESSION_FILE.read_text(encoding='utf-8')
        if '## Файлы' in content:
            content = content + entry
        else:
            content = content.rstrip() + f"\n\n## Файлы\n{entry}"
    else:
        date_str = datetime.now().strftime('%Y-%m-%d %H:%M')
        content  = f"# SESSION\n**Начато:** {date_str}\n\n## Файлы\n{entry}"

    SESSION_FILE.write_text(content, encoding='utf-8')

except Exception:
    pass

sys.exit(0)
