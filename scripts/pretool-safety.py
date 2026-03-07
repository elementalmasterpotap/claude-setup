#!/usr/bin/env python3
"""
PreToolUse hook: safety checks.
Покрывает (CLAUDE.md §Permissions):
  · --no-verify       → BLOCK
  · git reset --hard  → BLOCK
  · push --force main → BLOCK
  · logo/ assets/ Edit/Write → BLOCK
"""
import sys, json, re

try:
    data  = json.load(sys.stdin)
    tool  = data.get('tool_name', '')
    inp   = data.get('tool_input', {})

    # ── Bash ────────────────────────────────────────────────────────
    if tool == 'Bash':
        cmd = inp.get('command', '') or ''

        if re.search(r'git\s+.*--no-verify', cmd, re.IGNORECASE):
            print(json.dumps({
                "decision": "block",
                "reason": (
                    "⛔ --no-verify заблокирован.\n"
                    "Hooks должны проходить. Исправь проблему в hook, не обходи её.\n"
                    "Правило CLAUDE.md §Permissions"
                )
            }, ensure_ascii=False))
            sys.exit(0)

        if re.search(r'git\s+reset\s+--hard', cmd, re.IGNORECASE):
            print(json.dumps({
                "decision": "block",
                "reason": (
                    "⛔ git reset --hard заблокирован.\n"
                    "Деструктивно — потеряешь uncommitted changes.\n"
                    "Если реально нужно — скажи явно зачем."
                )
            }, ensure_ascii=False))
            sys.exit(0)

        if re.search(
            r'git\s+push\s+.*--force[^-].*\b(main|master)\b'
            r'|git\s+push\s+.*-f\s+.*\b(main|master)\b'
            r'|git\s+push\s+--force\s+origin\s+(main|master)',
            cmd, re.IGNORECASE
        ):
            print(json.dumps({
                "decision": "block",
                "reason": (
                    "⛔ push --force main/master заблокирован.\n"
                    "Перезапишет историю для всех — необратимо."
                )
            }, ensure_ascii=False))
            sys.exit(0)

        # rm -rf (дублируем hookify, но глобально)
        if re.search(r'\brm\s+(-rf|-fr)\b', cmd):
            print(json.dumps({
                "decision": "block",
                "reason": (
                    "⛔ rm -rf заблокирован.\n"
                    "Необратимое удаление. Скажи явно что и зачем удаляешь."
                )
            }, ensure_ascii=False))
            sys.exit(0)

        # claude plugin list зависает без TTY (HK-2)
        if re.search(r'claude\s+plugin\s+list', cmd):
            print(json.dumps({
                "decision": "block",
                "reason": (
                    "⚠️ claude plugin list зависает без TTY.\n"
                    "Используй enabledPlugins из settings.json:\n"
                    "  python3 -c \"import json,os; d=json.load(open(os.path.expanduser('~/.claude/settings.json'))); print(list(d.get('enabledPlugins',{}).keys()))\""
                )
            }, ensure_ascii=False))
            sys.exit(0)

    # ── Edit / Write → logo/ assets/ ────────────────────────────────
    if tool in ('Edit', 'Write', 'Read'):
        path = inp.get('file_path', '') or ''
        if re.search(r'(^|[/\\])(logo|assets)[/\\]', path, re.IGNORECASE):
            print(json.dumps({
                "decision": "block",
                "reason": (
                    "⛔ logo/ и assets/ заморожены.\n"
                    "Правило CLAUDE.md §Permissions."
                )
            }, ensure_ascii=False))
            sys.exit(0)

except Exception:
    pass

sys.exit(0)
