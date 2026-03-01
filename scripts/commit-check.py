#!/usr/bin/env python3
"""
Stop hook: commit message format check.
Правило CLAUDE.md §Commits: type(scope): desc + Co-Authored-By Claude + Happy
"""
import sys, json, re

COMMIT_CMD_RE = re.compile(r'git\s+commit\s+-m', re.IGNORECASE)
TYPE_SCOPE_RE = re.compile(
    r'(feat|fix|refactor|docs|style|chore|test|build|ci|perf)\([^)]+\):\s+\S',
    re.IGNORECASE
)
CO_CLAUDE_RE  = re.compile(r'Co-Authored-By:\s*Claude', re.IGNORECASE)
CO_HAPPY_RE   = re.compile(r'Co-Authored-By:\s*Happy', re.IGNORECASE)

try:
    data = json.load(sys.stdin)
    if data.get('stop_hook_active', False):
        sys.exit(0)

    text = data.get('last_assistant_message', '')

    if not COMMIT_CMD_RE.search(text):
        sys.exit(0)

    issues = []
    if not TYPE_SCOPE_RE.search(text):
        issues.append("формат «type(scope): description» (feat/fix/refactor/docs/style/chore)")
    if not CO_CLAUDE_RE.search(text):
        issues.append("Co-Authored-By: Claude <noreply@anthropic.com>")
    if not CO_HAPPY_RE.search(text):
        issues.append("Co-Authored-By: Happy <yesreply@happy.engineering>")

    if issues:
        print(json.dumps({
            "decision": "block",
            "reason": (
                "⚠️ Коммит не по правилам:\n"
                + "\n".join(f"  · нет {i}" for i in issues)
            )
        }, ensure_ascii=False))

except Exception:
    pass

sys.exit(0)
