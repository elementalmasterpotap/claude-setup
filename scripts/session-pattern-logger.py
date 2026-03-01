#!/usr/bin/env python3
"""
PostToolUse hook: session-pattern-logger
Пассивно логирует паттерны для /review в ~/.claude/tasks/SESSION_PATTERNS.md

Паттерны:
  repeated-edit    — Edit одного файла дважды подряд (исправление)
  repeated-command — Bash команда 3+ раз за сессию
  new-file         — Write нового файла (потенциально новая конвенция)
"""
import sys, json, re
from datetime import datetime
from pathlib import Path

PATTERNS_FILE = Path.home() / '.claude' / 'tasks' / 'SESSION_PATTERNS.md'
SESSION_FILE  = Path.home() / '.claude' / 'SESSION.md'

def log_pattern(pattern_type, detail, note=''):
    ts = datetime.now().strftime('%Y-%m-%dT%H:%M')
    entry = f"[{ts}] {pattern_type} | {detail}"
    if note:
        entry += f" | {note}"
    entry += '\n'

    PATTERNS_FILE.parent.mkdir(parents=True, exist_ok=True)
    if PATTERNS_FILE.exists():
        PATTERNS_FILE.write_text(
            PATTERNS_FILE.read_text(encoding='utf-8') + entry,
            encoding='utf-8'
        )
    else:
        header = f"# SESSION_PATTERNS — {datetime.now().strftime('%Y-%m-%d')}\n\n"
        PATTERNS_FILE.write_text(header + entry, encoding='utf-8')

def get_session_edits():
    """Читает список файлов из SESSION.md (из checkpoint.py)."""
    if not SESSION_FILE.exists():
        return []
    text = SESSION_FILE.read_text(encoding='utf-8')
    # Строки вида: - `path` [Edit] 14:23
    return re.findall(r'`([^`]+)`\s*\[Edit\]', text)

def get_pattern_commands():
    """Читает уже залогированные команды из SESSION_PATTERNS.md."""
    if not PATTERNS_FILE.exists():
        return {}
    text = PATTERNS_FILE.read_text(encoding='utf-8')
    counts = {}
    for line in text.splitlines():
        if 'repeated-command' in line or 'bash-command' in line:
            # [ts] bash-command | <cmd> | ...
            parts = line.split('|')
            if len(parts) >= 2:
                cmd = parts[1].strip()
                counts[cmd] = counts.get(cmd, 0) + 1
    return counts

def get_pattern_edits():
    """Читает уже залогированные repeated-edit из SESSION_PATTERNS.md."""
    if not PATTERNS_FILE.exists():
        return []
    text = PATTERNS_FILE.read_text(encoding='utf-8')
    logged = []
    for line in text.splitlines():
        if 'repeated-edit' in line:
            parts = line.split('|')
            if len(parts) >= 2:
                logged.append(parts[1].strip())
    return logged

try:
    data = json.load(sys.stdin)
    tool = data.get('tool_name', '')
    inp  = data.get('tool_input', {})

    # ── Edit: ловим повторный Edit того же файла ──────────────────────────────
    if tool == 'Edit':
        file_path = inp.get('file_path', '') or ''
        if file_path:
            session_edits = get_session_edits()
            logged_edits  = get_pattern_edits()
            # Файл уже редактировался в этой сессии И ещё не залогирован как паттерн
            edit_count = session_edits.count(file_path)
            if edit_count >= 1 and file_path not in logged_edits:
                log_pattern('repeated-edit', file_path, f'Edit ×{edit_count + 1}')

    # ── Write: новый файл — потенциально новая конвенция ──────────────────────
    elif tool == 'Write':
        file_path = inp.get('file_path', '') or ''
        if file_path and not Path(file_path).exists():
            # Только новые файлы в .claude/ или scripts/ — интересные
            if any(p in file_path.replace('\\', '/') for p in ['.claude/', 'scripts/', 'skills/', 'agents/']):
                log_pattern('new-file', file_path, 'Write нового файла в служебной директории')

    # ── Bash: ловим повторные команды ─────────────────────────────────────────
    elif tool == 'Bash':
        cmd = (inp.get('command', '') or '').strip()
        if not cmd or len(cmd) < 8:
            sys.exit(0)

        # Нормализуем: убираем аргументы-значения, оставляем паттерн команды
        # python3 ~/.claude/update_telegraph.py → python3 ~/.claude/update_telegraph.py
        cmd_key = cmd.split('\n')[0][:80]  # первая строка, до 80 символов

        counts = get_pattern_commands()
        current = counts.get(cmd_key, 0)

        if current == 0:
            # Первый раз — просто логируем как "видели"
            log_pattern('bash-command', cmd_key)
        elif current == 2:
            # Третий раз — это паттерн
            log_pattern('repeated-command', cmd_key, f'×{current + 1} запуска')

except Exception:
    pass

sys.exit(0)
