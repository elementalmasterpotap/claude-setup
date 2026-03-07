#!/bin/bash
# SessionStart хук: автообновление Claude Code @next + плагины.
# Запускается раз в 24 часа (через маркер-файл), не блокирует старт.
#
# Claude Code: npm install @next — всегда самая свежая (включая pre-release)
# Плагины: claude plugin update — все из enabledPlugins
# Happy: мобильный клиент, обновляется через App Store (программно недоступно)

MARKER="$HOME/.claude/tasks/.last_update"
LOG="$HOME/.claude/tasks/.update_log"
INTERVAL=86400  # 24 часа

now=$(date +%s)
last=0
[ -f "$MARKER" ] && last=$(cat "$MARKER" 2>/dev/null || echo 0)
elapsed=$((now - last))

# Слишком рано — молча выходим, не тормозим старт
if [ "$elapsed" -lt "$INTERVAL" ]; then
    exit 0
fi

# Обновляем в фоне — не блокируем SessionStart
(
    ts=$(date '+%Y-%m-%d %H:%M')
    {
        echo "=== $ts ==="

        # ── Claude Code @next ───────────────────────────────────────────────
        old_ver=$(claude --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1 || echo "?")
        npm install -g @anthropic-ai/claude-code@next --silent 2>&1 | tail -1
        new_ver=$(claude --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1 || echo "?")
        if [ "$old_ver" != "$new_ver" ]; then
            echo "Claude Code: $old_ver → $new_ver"
        else
            echo "Claude Code: $new_ver (без изменений)"
        fi

        # ── Плагины ────────────────────────────────────────────────────────
        plugins=(
            "commit-commands@claude-plugins-official"
            "claude-md-management@claude-plugins-official"
            "hookify@claude-plugins-official"
            "github@claude-plugins-official"
            "qodo-skills@claude-plugins-official"
            "frontend-design@claude-plugins-official"
            "context7@claude-plugins-official"
            "feature-dev@claude-plugins-official"
            "semgrep@claude-plugins-official"
        )

        for plugin in "${plugins[@]}"; do
            result=$(claude plugin update "$plugin" 2>&1 | tail -1)
            # Логируем только если есть изменения (не "already up to date")
            if ! echo "$result" | grep -qi "already\|up.to.date\|no update"; then
                echo "Plugin $plugin: $result"
            fi
        done

        echo "done"
    } >> "$LOG" 2>&1

    # Обновляем маркер
    echo "$now" > "$MARKER"
) &

exit 0
