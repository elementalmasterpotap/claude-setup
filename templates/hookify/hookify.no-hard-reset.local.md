---
name: no-hard-reset
enabled: true
event: bash
action: warn
pattern: "git (reset --hard|checkout -- \.|restore \.|clean -f)"
---

⚠️ **Деструктивная git-операция** — сотрёт несохранённые изменения.

Убедись что нет незакоммиченной работы. Если есть — сначала stash или commit.
