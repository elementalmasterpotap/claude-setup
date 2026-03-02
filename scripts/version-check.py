#!/usr/bin/env python3
"""
Stop хук: проверка версий зависимостей.

Правило CLAUDE.md §Версии: всегда latest/next включая pre-release.
Ловит в ответе Claude команды с фиксированными старыми версиями.

Паттерны которые триггерят предупреждение:
  npm install pkg@X.Y.Z    — конкретная версия (не @latest/@next/@beta/@canary)
  pip install pkg==X.Y.Z   — фиксированная версия
  pip install pkg>=X,<Y    — диапазон (ограничение)

НЕ ловит:
  npm install pkg@latest / @next / @beta / @canary — правильно
  pip install pkg           — без версии, правильно
  npm install pkg@^X.Y.Z   — semver range, ок
"""
import sys, json, re

# Конкретная npm версия (X.Y.Z / X.Y.Z-beta.0 — нет @latest/@next/@beta/@canary)
NPM_PINNED_RE = re.compile(
    r'npm\s+(?:install|i|add)\s+[^\n]*?@(\d+\.\d+[\.\d]*)(?:\s|$|")',
    re.IGNORECASE
)

# pip install pkg==X.Y.Z (фиксированная версия)
PIP_PINNED_RE = re.compile(
    r'pip\s+install\s+[^\n]*?[\w\-\.]+==(\d+\.\d+[\.\d\w]*)',
    re.IGNORECASE
)

# Исключения — если рядом есть обоснование (совместимость, legacy, LTS)
EXCEPTION_RE = re.compile(
    r'совместимост|compatibility|legacy|LTS|requires|требует|зависимост|pinned|locked',
    re.IGNORECASE
)

FENCED_RE = re.compile(r'```.*?```', re.DOTALL)

try:
    data = json.load(sys.stdin)
    if data.get('stop_hook_active', False):
        sys.exit(0)

    text = data.get('last_assistant_message', '')

    # Ищем в тексте вне блоков кода (в блоках кода — примеры, не команды)
    # Но команды часто именно в блоках — проверяем везде
    npm_matches  = NPM_PINNED_RE.findall(text)
    pip_matches  = PIP_PINNED_RE.findall(text)

    if not npm_matches and not pip_matches:
        sys.exit(0)

    # Проверяем исключения
    if EXCEPTION_RE.search(text):
        sys.exit(0)

    found = []
    if npm_matches:
        found.append(f"npm @{npm_matches[0]} (используй @next или @latest)")
    if pip_matches:
        found.append(f"pip =={pip_matches[0]} (убери фиксацию или добавь --pre)")

    print(json.dumps({
        "decision": "block",
        "reason": (
            f"⚠️ Фиксированная версия: {' · '.join(found)}\n"
            "Правило: всегда latest/next включая pre-release.\n"
            "  npm → @next (или @latest если нет next)\n"
            "  pip → без ==X.Y.Z, или pip install --pre pkg\n"
            "Если нужна конкретная версия — напиши явно почему (совместимость/LTS)."
        )
    }, ensure_ascii=False))

except Exception:
    pass

sys.exit(0)
