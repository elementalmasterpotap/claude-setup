---
name: new-rule
description: Создать новое правило с полным комплектом — rules/*.md + Stop hook + Skill. Вызывать когда нужно зафиксировать новый паттерн/правило в системе.
disable-model-invocation: true
argument-hint: [название правила] [описание]
---

Создай новое правило с полным комплектом: $ARGUMENTS

## Алгоритм:

```
1. Определить куда писать правило
   ├── карта правил в CLAUDE.md "Новые записи"
   └── проверить дубли в смежных файлах

2. Написать правило
   └── rules/<file>.md или CLAUDE.md — сжато, без воды

3. Stop hook (scripts/<name>-check.py)
   ├── можно автоматизировать? → создать
   │   ├── что ловить: regex / паттерн в тексте ответа
   │   ├── BLOCK или WARN
   │   └── зарегистрировать в settings.json → Stop[]
   └── невозможно → написать комментарий почему в файле правила

4. Skill (skills/<name>/SKILL.md)
   ├── action (disable-model-invocation: true) — если есть команда для вызова
   ├── knowledge (user-invocable: false) — если справочный контент
   └── невозможно → написать комментарий почему

5. Синхронизировать
   └── python3 ~/.claude/update_telegraph.py
```

## Шаблон Stop hook:

```python
#!/usr/bin/env python3
"""Stop hook: <описание>. Правило <файл>."""
import sys, json, re

PATTERN_RE = re.compile(r'...', re.IGNORECASE)
FENCED_RE  = re.compile(r'```.*?```', re.DOTALL)

try:
    data = json.load(sys.stdin)
    if data.get('stop_hook_active', False):
        sys.exit(0)

    text  = data.get('last_assistant_message', '')
    clean = FENCED_RE.sub('', text)

    if PATTERN_RE.search(clean):
        print(json.dumps({
            "decision": "block",  # или "warn"
            "reason": "⚠️ <объяснение>\nПравило <файл>"
        }, ensure_ascii=False))

except Exception:
    pass

sys.exit(0)
```

## Шаблон Skill:

```yaml
---
name: <name>
description: <когда использовать — Claude читает это для авто-загрузки>
disable-model-invocation: true   # action
# user-invocable: false          # knowledge
argument-hint: [аргументы]
---

Инструкции для Claude...
```

## После создания:

- Добавить hook в settings.json → Stop[] (или PreToolUse[])
- Запустить: `python3 ~/.claude/update_telegraph.py`
