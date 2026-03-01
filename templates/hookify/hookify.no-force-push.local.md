---
name: no-force-push-main
enabled: true
event: bash
action: block
pattern: "git push.*(--force|-f).*(main|master)|git push.*(main|master).*(--force|-f)"
---

⛔ **git push --force на main/master** — заблокировано.

Это перезапишет историю на основной ветке. Если уверен — делай руками.
