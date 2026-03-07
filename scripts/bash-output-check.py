#!/usr/bin/env python3
"""
PostToolUse хук: предупреждает о большом Bash output.

Если Bash tool вернул >3000 символов — это verbose операция
(тесты, логи, fetch документации). В следующий раз лучше субагент:
verbose output остаётся в субагенте, в main context только summary.

Правило из token-budget.md: субагенты для verbose операций.
Источник: официальная документация Anthropic (costs page).
"""
import sys, json

OUTPUT_THRESHOLD = 3000   # символов — граница "большого" вывода
WARN_THRESHOLD   = 6000   # > 6K → блок с советом

# Команды которые всегда verbose и всегда стоит делегировать
ALWAYS_DELEGATE = [
    'npm test', 'pytest', 'go test', 'jest', 'cargo test',
    'find ', 'grep -r', 'git log', 'git diff',
    'cat ', 'head ', 'tail ',
]

try:
    data = json.load(sys.stdin)
    tool = data.get('tool_name', '')

    if tool != 'Bash':
        sys.exit(0)

    inp      = data.get('tool_input', {})
    response = data.get('tool_response', {})
    cmd      = (inp.get('command', '') or '').strip()

    # Вытащить output из response
    output = ''
    if isinstance(response, dict):
        output = response.get('output', '') or response.get('content', '') or ''
    elif isinstance(response, str):
        output = response

    output_len = len(output)

    if output_len < OUTPUT_THRESHOLD:
        sys.exit(0)

    # Проверяем — это делегируемая команда?
    is_delegatable = any(d in cmd for d in ALWAYS_DELEGATE)

    if output_len >= WARN_THRESHOLD or is_delegatable:
        cmd_short = cmd[:60] + ('...' if len(cmd) > 60 else '')
        kb = output_len // 1000

        print(json.dumps({
            "decision": "block",
            "reason": (
                f"💡 Bash вернул ~{kb}K символов: «{cmd_short}»\n"
                "Verbose операции лучше делегировать субагенту:\n"
                "  Task(subagent_type='codebase-explorer', prompt='...')\n"
                "Verbose output остаётся в субагенте → main context чист.\n"
                "Если читать нужно здесь — ок, продолжай."
            )
        }, ensure_ascii=False))

except Exception:
    pass

sys.exit(0)
