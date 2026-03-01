#!/bin/bash
# Claude Code statusline — git ветка + изменения + тип устройства

# Тип устройства
DEVICE_FILE="$HOME/.claude/device-type"
DEVICE_ICON="🖥"
if [ -f "$DEVICE_FILE" ]; then
    RAW=$(cat "$DEVICE_FILE")
    case "$RAW" in
        MOBILE:*) DEVICE_ICON="📱" ;;
    esac
fi

BRANCH=$(git branch --show-current 2>/dev/null)
if [ -n "$BRANCH" ]; then
    MODIFIED=$(git diff --name-only 2>/dev/null | wc -l | tr -d ' ')
    STAGED=$(git diff --cached --name-only 2>/dev/null | wc -l | tr -d ' ')
    if [ "$STAGED" -gt 0 ] || [ "$MODIFIED" -gt 0 ]; then
        echo "${DEVICE_ICON} ${BRANCH} [${STAGED}↑ ${MODIFIED}~]"
    else
        echo "${DEVICE_ICON} ${BRANCH} ✓"
    fi
else
    echo "${DEVICE_ICON} no git"
fi
