#!/usr/bin/env python3
"""
Stop хук: предупреждение о тяжёлых файлах без .claudeignore.

Если в ответе Claude упоминается работа с тяжёлыми файлами
(node_modules, package-lock.json, yarn.lock, *.lock, dist/ и т.д.)
без упоминания .claudeignore → warn: "30–80K токенов зря".

Не блокирует — только предупреждает.
"""
import sys, json, re, os
from pathlib import Path

# Паттерны тяжёлых файлов (токено-жрущие)
HEAVY_RE = re.compile(
    r'package-lock\.json'
    r'|yarn\.lock'
    r'|pnpm-lock\.yaml'
    r'|bun\.lockb'
    r'|Pipfile\.lock'
    r'|poetry\.lock'
    r'|uv\.lock'
    r'|Cargo\.lock'
    r'|node_modules[/\\]'
    r'|\.nyc_output'
    r'|\bdist/\b'
    r'|\bbuild/\b',
    re.IGNORECASE
)

# Паттерны "уже знает о проблеме"
ALREADY_OK = re.compile(
    r'\.claudeignore'
    r'|claudeignore'
    r'|исключён|excluded|ignored'
    r'|не буду читать|не читать',
    re.IGNORECASE
)

FENCED_RE = re.compile(r'```.*?```', re.DOTALL)

try:
    data = json.load(sys.stdin)
    if data.get("stop_hook_active", False):
        sys.exit(0)

    text = data.get("last_assistant_message", "")
    clean = FENCED_RE.sub("", text)

    if HEAVY_RE.search(clean) and not ALREADY_OK.search(clean):
        # Найти конкретный тяжёлый файл для сообщения
        match = HEAVY_RE.search(clean)
        found = match.group(0) if match else "тяжёлый файл"

        print(json.dumps({
            "decision": "block",
            "reason": (
                f"💡 Обнаружен '{found}' — это 30–80K токенов контекста.\n"
                "Если не нужно читать его содержимое — добавь в .claudeignore:\n"
                f"  echo '{found.split('/')[0]}' >> .claudeignore\n"
                "Глобальный шаблон: ~/.claude/templates/.claudeignore\n"
                "Если читать НУЖНО — ок, продолжай. Допиши это в ответ явно."
            )
        }, ensure_ascii=False))

except Exception:
    pass

sys.exit(0)
