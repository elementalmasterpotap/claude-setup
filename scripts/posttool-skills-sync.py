#!/usr/bin/env python3
"""
PostToolUse hook: напоминание синхронизировать после изменения skills/.
Если Write/Edit затронул SKILL.md → напомнить запустить /sync.
"""
import sys, json, re

SKILL_MD_RE = re.compile(r'[/\\]skills[/\\][^/\\]+[/\\]SKILL\.md$', re.IGNORECASE)

try:
    data  = json.load(sys.stdin)
    tool  = data.get('tool_name', '')
    inp   = data.get('tool_input', {})

    if tool in ('Write', 'Edit'):
        path = inp.get('file_path', '') or ''
        if SKILL_MD_RE.search(path):
            print(
                "📌 skills/ изменён → запусти /sync (или python3 ~/.claude/update_telegraph.py)\n"
                "Скиллы = кастомизация: Telegraph + GitHub + Telegram должны быть актуальны."
            )

except Exception:
    pass

sys.exit(0)
