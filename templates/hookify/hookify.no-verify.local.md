---
name: no-verify-warn
enabled: true
event: bash
action: warn
pattern: "--no-verify"
---

⚠️ **--no-verify** — скип pre-commit хуков.

Правило: не использовать без явного запроса. Если хук падает — разобраться с причиной, не обходить.
