#!/usr/bin/env python3
"""
PostToolUse hook: напоминание о комплекте при создании/изменении кастомизаций.

  skills/*/SKILL.md → напомнить /sync
  rules/*.md        → напомнить создать хук + скилл если их нет
  scripts/*-check.py или pretool-*.py → напомнить создать скилл
"""
import sys, json, re

SKILL_RE   = re.compile(r'[/\\]skills[/\\][^/\\]+[/\\]SKILL\.md$', re.IGNORECASE)
RULES_RE   = re.compile(r'[/\\]rules[/\\][^/\\]+\.md$', re.IGNORECASE)
SCRIPTS_RE = re.compile(r'[/\\]scripts[/\\][^/\\]+\.(py|sh)$', re.IGNORECASE)

try:
    data = json.load(sys.stdin)
    tool = data.get('tool_name', '')
    inp  = data.get('tool_input', {})

    if tool not in ('Write', 'Edit'):
        sys.exit(0)

    path = inp.get('file_path', '') or ''

    if SKILL_RE.search(path):
        print(
            "📌 skills/ изменён → запусти /sync\n"
            "Скиллы = кастомизация: Telegraph + GitHub + Telegram должны быть актуальны."
        )

    elif RULES_RE.search(path):
        print(
            "📌 rules/ изменён — проверь комплект правила:\n"
            "  ├── Stop hook в scripts/*-check.py  (можно автоматизировать?)\n"
            "  └── Skill в skills/*/SKILL.md        (action или knowledge?)\n"
            "Нет → зафикси почему в комментарии правила. Потом: /sync"
        )

    elif SCRIPTS_RE.search(path):
        fname = re.search(r'[^/\\]+$', path)
        if fname and ('check' in fname.group().lower() or 'pretool' in fname.group().lower()):
            print(
                "📌 Новый хук в scripts/ — создай skill если нужен ручной invoke:\n"
                "  skills/<name>/SKILL.md  с disable-model-invocation: true\n"
                "Потом: /sync"
            )

except Exception:
    pass

sys.exit(0)
