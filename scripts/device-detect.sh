#!/bin/bash
# SessionStart hook: определяет телефон или ПК по ширине терминала
# Результат пишет в ~/.claude/device-type для других скриптов и statusline

DEVICE_FILE="$HOME/.claude/device-type"

# Ширина терминала: tput cols → env COLUMNS → fallback 999 (десктоп)
WIDTH="${COLUMNS:-}"
if [ -z "$WIDTH" ]; then
    WIDTH=$(tput cols 2>/dev/null) || WIDTH=999
fi

if [ "$WIDTH" -lt 60 ]; then
    echo "MOBILE:$WIDTH" > "$DEVICE_FILE"
    # Говорим Claude что мы на телефоне
    echo "📱 ТЕЛЕФОН (ширина: $WIDTH)"
    echo "Короткие ответы, без широкой псевдографики. Не просить 'открой и проверь'."
else
    echo "DESKTOP:$WIDTH" > "$DEVICE_FILE"
fi
