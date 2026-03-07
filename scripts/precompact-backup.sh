#!/bin/bash
# PreCompact hook — бэкап транскрипта перед авто-сжатием сессии

BACKUP_DIR="$HOME/.claude/backups"
mkdir -p "$BACKUP_DIR"

# Найти самый свежий .jsonl транскрипт
LATEST=$(find ~/.claude/projects -name "*.jsonl" -type f 2>/dev/null \
    | while read f; do echo "$(stat -c %Y "$f" 2>/dev/null || stat -f %m "$f" 2>/dev/null) $f"; done \
    | sort -rn | head -1 | awk '{print $2}')

if [ -n "$LATEST" ]; then
    TS=$(date +%Y%m%d_%H%M%S)
    cp "$LATEST" "$BACKUP_DIR/pre-compact-${TS}.jsonl" 2>/dev/null
    echo "Backup: pre-compact-${TS}.jsonl"
fi

exit 0
