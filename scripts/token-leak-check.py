#!/usr/bin/env python3
"""
Stop hook: no real tokens in response.
Правило CLAUDE.md §Pre-push: блокировать реальные секреты в ответе.
"""
import sys, json, re

TOKEN_RE = re.compile(
    r'ghp_[A-Za-z0-9]{36}'
    r'|[0-9]{10}:AA[A-Za-z0-9_\-]{33}'
    r'|475c06[a-f0-9]{50}'
    r'|edit\.telegra\.ph/auth/[A-Za-z0-9_\-]{20,}'
)

# Плейсхолдеры — ок
PLACEHOLDER_RE = re.compile(
    r'ghp_X{5,}'
    r'|\$TOKEN|\$GITHUB_TOKEN|\$TELEGRAPH_TOKEN|\$TELEGRAM_BOT_TOKEN'
    r'|your_token|YOUR_TOKEN|XXXX'
)

try:
    data = json.load(sys.stdin)
    if data.get('stop_hook_active', False):
        sys.exit(0)

    text = data.get('last_assistant_message', '')
    matches = TOKEN_RE.findall(text)

    if matches:
        print(json.dumps({
            "decision": "block",
            "reason": (
                f"⛔ В ответе реальный токен: {matches[0][:12]}...\n"
                "Замени на плейсхолдер: ghp_XXXX / $TOKEN / your_token_here"
            )
        }, ensure_ascii=False))

except Exception:
    pass

sys.exit(0)
