---
name: sync
description: Синхронизировать кастомизации Claude — обновить Telegraph лонгрид, запушить в GitHub, обновить Telegram пост. Запускать после изменений в rules/, CLAUDE.md, settings.json, scripts/, templates/.
disable-model-invocation: true
allowed-tools: Bash
---

Синхронизируй все кастомизации Claude:

```bash
python3 ~/.claude/update_telegraph.py
```

## Что делает скрипт:

```
update_telegraph.py
  ├── editPage    → Telegraph лонгрид (контент + дата обновления)
  ├── git push    → GitHub potap-claude-setup (rules/, CLAUDE.md, scripts/, templates/)
  └── editMessage → Telegram пост #47 в @potap_attic (дата + ссылки)
```

После запуска — покажи результат:
- URL Telegraph
- GitHub: synced / no changes
- Telegram: message_id
