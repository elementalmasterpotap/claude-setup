---
name: no-rm-rf
enabled: true
event: bash
action: block
pattern: "rm\s+(-rf|-fr)"
---

⛔ **rm -rf** — необратимое удаление. Заблокировано.

Если реально нужно — скажи явно что удаляешь и зачем.
