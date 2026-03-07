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

    msg = None

    if SKILL_RE.search(path):
        msg = (
            "📌 skills/ изменён → проверь: Telegraph + GitHub + Telegram актуальны? "
            "Если добавил новый скилл — обнови telegraph_content.py и запусти update_telegraph.py."
        )

    elif RULES_RE.search(path):
        msg = (
            "📌 rules/ изменён — проверь комплект правила: "
            "(1) Stop hook в scripts/*-check.py (можно автоматизировать?); "
            "(2) Skill в skills/*/SKILL.md (action или knowledge?). "
            "Нет → зафикси НЕВОЗМОЖНО в комментарии правила. Потом обнови лонгрид."
        )

    elif SCRIPTS_RE.search(path):
        fname = re.search(r'[^/\\]+$', path)
        if fname and ('check' in fname.group().lower() or 'pretool' in fname.group().lower()):
            msg = (
                "📌 Новый хук в scripts/ — нужно: "
                "(1) зарегистрировать в settings.json; "
                "(2) создать skill если нужен ручной invoke. "
                "Обнови лонгрид через update_telegraph.py."
            )

    if msg:
        print(json.dumps({"decision": "warn", "reason": msg}, ensure_ascii=False))

except Exception:
    pass

sys.exit(0)
