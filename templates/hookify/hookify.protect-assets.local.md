---
name: protect-assets
enabled: true
event: file
action: block
tool_matcher: Edit|Write
conditions:
  - field: file_path, operator: regex_match, pattern: "(^|[/\\\\])(logo|assets)[/\\\\]"
---

⛔ **logo/ и assets/ — не трогать.**

Правило Permissions: эти папки заморожены. Редактирование заблокировано.
