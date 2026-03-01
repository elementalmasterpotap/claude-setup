---
name: warn-ci-infra
enabled: true
event: file
action: warn
tool_matcher: Edit|Write
conditions:
  - field: file_path, operator: regex_match, pattern: "(^|[/\\\\])(CI|infra|\.github)[/\\\\]|\.ya?ml$"
---

⚠️ **CI / infra / .yml** — изменение требует явного подтверждения.

Правило Permissions: эти файлы трогать только по запросу пользователя.
