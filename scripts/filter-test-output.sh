#!/bin/bash
# PreToolUse хук: фильтрует вывод тестов — только ошибки вместо полного лога.
# Официальный паттерн Anthropic: вместо 10K строк → только FAIL/ERROR строки.
# Экономия: -95% токенов на тест-запросы.
#
# Правило: hook вмешивается только если команда — тест-раннер.
# Все остальные Bash команды пропускаются без изменений.

input=$(cat)
cmd=$(echo "$input" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('command',''))" 2>/dev/null)

# Если не тест-команда — пропустить без изменений
if ! echo "$cmd" | grep -qE '^(npm test|npm run test|pytest|go test|jest|vitest|cargo test|dotnet test|ruby -Itest|bundle exec rspec|./gradlew test|mvn test)'; then
    echo "{}"
    exit 0
fi

# Тест-команда: оборачиваем в фильтр — только строки с ошибками
filtered="${cmd} 2>&1 | grep -A 5 -E '(FAIL|FAILED|ERROR|error:|AssertionError|TypeError|SyntaxError|✗|✕|×)' | head -120"

echo "{\"hookSpecificOutput\":{\"hookEventName\":\"PreToolUse\",\"permissionDecision\":\"allow\",\"updatedInput\":{\"command\":\"${filtered}\"}}}"
