#!/bin/bash
# TaskCompleted hook — блокирует "готово" если есть staged-но-незакоммиченные файлы
# exit 2 = Claude не может пометить задачу завершённой

if git rev-parse --git-dir > /dev/null 2>&1; then
    STAGED=$(git diff --cached --name-only 2>/dev/null | wc -l | tr -d ' ')
    if [ "$STAGED" -gt 0 ]; then
        echo "⚠️ ${STAGED} файл(ов) в staging не закоммичены. Сделай коммит перед завершением задачи."
        exit 2
    fi
fi

exit 0
