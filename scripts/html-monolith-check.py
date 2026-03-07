#!/usr/bin/env python3
"""
PreToolUse hook: блокирует запись HTML-монолита без css/ и js/ рядом.
Срабатывает: Write .html-файла > 400 строк без папок css/ и js/ рядом.
Мотивация: монолит 2000 строк vs html+css+js 500 строк → 5× токенов на итерации.
"""
import sys, json, os, re

try:
    data = json.load(sys.stdin)
    if data.get('tool_name') != 'Write':
        sys.exit(0)

    path    = data.get('tool_input', {}).get('file_path', '') or ''
    content = data.get('tool_input', {}).get('content', '') or ''

    # Только .html файлы
    if not path.lower().endswith('.html'):
        sys.exit(0)

    # Считаем строки
    lines = content.count('\n')
    if lines < 400:
        sys.exit(0)

    # Если css/ и js/ уже есть рядом — всё ок
    parent = os.path.dirname(os.path.abspath(path))
    has_css = os.path.isdir(os.path.join(parent, 'css'))
    has_js  = os.path.isdir(os.path.join(parent, 'js'))
    if has_css and has_js:
        sys.exit(0)

    # Проверяем что это не редактирование существующего файла
    # (если файл уже есть — пропускаем, это не первичное создание)
    if os.path.exists(path):
        sys.exit(0)

    missing = []
    if not has_css: missing.append('css/')
    if not has_js:  missing.append('js/')

    print(json.dumps({
        "decision": "block",
        "reason": (
            f"⚠️ HTML-монолит ({lines} строк) без {' и '.join(missing)} рядом.\n"
            f"Сначала создай структуру:\n"
            f"  mkdir -p {os.path.join(parent, 'css')} {os.path.join(parent, 'js')}\n"
            f"Потом пиши index.html (только разметка) + css/style.css + js/main.js.\n"
            f"Экономия токенов при итерациях: 5×. Правило: preferences.md"
        )
    }, ensure_ascii=False))

except Exception:
    pass

sys.exit(0)
