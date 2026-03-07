#!/usr/bin/env python3
"""
Stop hook: GH-2 — загрузка ассетов через uploads.github.com, не api.github.com.
Правило lessons_universal.md §GH-2.
"""
import sys, json, re

# api.github.com + /releases/ + /assets → неправильный endpoint для загрузки
API_UPLOAD_RE = re.compile(
    r'api\.github\.com.*/repos/.*/releases/\d+/assets',
    re.IGNORECASE
)
# Правильный endpoint
UPLOADS_RE = re.compile(r'uploads\.github\.com', re.IGNORECASE)

try:
    data = json.load(sys.stdin)
    if data.get('stop_hook_active', False):
        sys.exit(0)

    text = data.get('last_assistant_message', '')

    # Проверяем только если это явно загрузка (Invoke-RestMethod -Method POST или PUT)
    if API_UPLOAD_RE.search(text) and not UPLOADS_RE.search(text):
        # Дополнительно — только если есть POST/PUT (загрузка, не чтение)
        if re.search(r'(POST|PUT|upload|загрузи)', text, re.IGNORECASE):
            print(json.dumps({
                "decision": "warn",
                "reason": (
                    "⚠️ GH-2: неправильный endpoint для загрузки ассетов!\n"
                    "  Неправильно: api.github.com/.../releases/{id}/assets\n"
                    "  Правильно:   uploads.github.com/repos/.../releases/{id}/assets\n"
                    "Правило lessons_universal.md §GH-2"
                )
            }, ensure_ascii=False))

except Exception:
    pass

sys.exit(0)
