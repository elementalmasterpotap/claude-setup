#!/usr/bin/env python3
"""
Stop hook: deploy commands must be non-interactive.
Правило workflow_universal.md: деплой с -NoPrompt / --yes / -y.
"""
import sys, json, re

# Маркеры команд установки/деплоя
DEPLOY_RE = re.compile(
    r'(\.\/install|powershell[^\n]*install|bash[^\n]*install|\.\/deploy|python[^\n]*setup\.py\s+install)',
    re.IGNORECASE
)

# Допустимые флаги без интерактива
NOPROMPT_RE = re.compile(
    r'(-NoPrompt|--yes\b|-y\b|--force\b|-f\b|--quiet\b|-q\b|--non-interactive)',
    re.IGNORECASE
)

# Только в bash/powershell блоках кода
CODE_BLOCK_RE = re.compile(
    r'```(?:bash|powershell|ps1|ps|sh|cmd)?\n(.*?)```',
    re.DOTALL | re.IGNORECASE
)

try:
    data = json.load(sys.stdin)
    if data.get('stop_hook_active', False):
        sys.exit(0)

    text = data.get('last_assistant_message', '')
    blocks = CODE_BLOCK_RE.findall(text)

    for block in blocks:
        if DEPLOY_RE.search(block) and not NOPROMPT_RE.search(block):
            print(json.dumps({
                "decision": "warn",
                "reason": (
                    "⚠️ Команда деплоя без флага без интерактива!\n"
                    "Добавь: -NoPrompt / --yes / -y\n"
                    "Правило workflow_universal.md §Деплой"
                )
            }, ensure_ascii=False))
            break

except Exception:
    pass

sys.exit(0)
