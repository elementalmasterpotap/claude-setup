# Token Budget — управление Pro лимитом

## Pro тариф — факты

```
Окно:      ~44K токенов · ~45 сообщений
Сброс:     rolling 5 часов от ПЕРВОГО сообщения (не полночь)
Модели:    Sonnet — основная · Opus — дороже → тратит лимит быстрее
Мышление:  alwaysThinkingEnabled=true + MAX_THINKING_TOKENS=12000
           (дефолт был 31 999 → -62% thinking-токенов)
```

## Модельная политика

```
Задача                              Модель
──────────────────────────────────────────────────────────────
найти/перечислить/проанализировать  → Haiku субагент (codebase-explorer)
типичный код/исправление/объяснение → Sonnet (default)
сложная архитектура / multi-file    → Sonnet (с thinking)
критическое архит. решение          → Opus (явно, не для кода)
```

## Команды контекста

```
/stats          → использование Pro/Max (не /cost — он для API billing)
/context        → что именно жрёт место прямо сейчас
/cost           → для API-пользователей
/compact [фокус] → сжать с инструкцией: "сохрани: изменённые файлы, задачи, решения"
/clear          → полный сброс (другая задача)
/rewind         → откат к предыдущей точке (или Escape+Escape)
/compact-smart  → скилл: /compact с правильными инструкциями
/mcp            → отключить ненужные серверы
```

## MCP серверы — токены в холостую

```
Linear MCP     → ~14 000 токенов (даже когда не используешь!)
context7       → минимальный, ок
Каждый сервер  → +N токенов всегда, даже idle

ENABLE_TOOL_SEARCH=auto:5  → грузит MCP on-demand (>5% контекста)
→ уже включено в env settings.json
```

## Verbose операции → субагент

```
Тесты, большие логи, fetch документации, find по всему репо
        ↓
Task(subagent_type='codebase-explorer', prompt='...')
        ↓
Verbose output остаётся в субагенте
Main context получает только summary

Автоматически: bash-output-check.py предупредит при >3K символов вывода
```

## Extended thinking — настройки

```
MAX_THINKING_TOKENS=12000           → лимит budget (вместо 31 999)
DISABLE_ADAPTIVE_THINKING=1         → фиксированный budget, не плавающий
alwaysThinkingEnabled=true          → thinking включён (но в 12K бюджете)
→ все три уже в env settings.json

Выключить thinking вручную: Alt+T (Toggle) или /config
Для простых задач haiku-suggest.py не инжектирует thinking
```

## Когда compact

```
/compact  → задача продолжается, нужен контекст
/clear    → задача сменилась, контекст не нужен
```

Compact триггеры:
- Сессия > 45 минут активной работы
- Меняешь задачу/фичу в том же проекте
- Видишь предупреждение session-length-check.py (каждые 5 длинных ответов)

## Тактика Pro окон

```
Паттерн 3 окна в день:
  07:00  первое сообщение (активирует окно) — можно просто "start"
  07:00–12:00  первое окно  → тяжёлая работа
  12:00–17:00  второе окно  → продолжение
  17:00–22:00  третье окно  → финализация

Если лимит близко:
  → compact нынешнюю задачу
  → запиши что делать дальше в .claude/tasks/SESSION.md
  → дождись сброса → /resume
```

## Context size best practices

```
.claudeignore   → исключить node_modules, *.lock, dist, build
                  node_modules = 30–100K токенов
                  package-lock.json = 30–80K токенов
CLAUDE.md       → < 150 строк (у нас выполнено)
Skills          → lazy-load: 82% vs всё в CLAUDE.md
MCP серверы     → только нужные включены · /mcp для toggle
Субагенты       → verbose ops → субагент, main context чист
Промпты         → конкретные: "добавь rate limit в auth.ts" не "улучши код"
```

## Сигналы что тратишь лимит зря

```
· Читаешь node_modules / *.lock без .claudeignore
· Sonnet думает над "найди файл" — нужен Haiku (haiku-suggest.py напомнит)
· Bash вернул >3K символов в main context — нужен субагент (bash-output-check.py)
· Длинные ответы без compact (session-length-check.py)
· MCP серверы включены которые не нужны в текущей задаче
· Opus для рутинных задач
· Субагент получил весь контекст когда нужен был только summary
· Синхронизация Telegraph/GitHub запускается при каждой правке (нужно только по /sync)
```

## Ультимативный пак: SOS когда токены кончаются

```
1. /compact-smart    → сжать с сохранением изменённых файлов и задач
2. /clear            → полный сброс если задача сменилась
3. Субагент Haiku    → verbose ops в субагент, main context чист (subagent-context.md)
4. .claudeignore     → исключить node_modules/lock/dist (уже создан: ~/.claude/.claudeignore)
5. /mcp              → отключить Linear и другие неиспользуемые MCP
6. Haiku для поиска  → [HAIKU_ELIGIBLE] задачи ~70% дешевле (haiku-economy.md)
7. Разбить задачу    → независимые подзадачи, /compact между ними
8. Отключить thinking → Alt+T (для простых задач thinking не нужен)
```

## Prompt Caching (API)

```python
# Для Claude API: кэшировать длинные системные промпты
content = [
    {
        "type": "text",
        "text": длинный_контекст,             # >1024 токенов
        "cache_control": {"type": "ephemeral"} # кэш 5 минут → -90% при повторе
    },
    {"type": "text", "text": конкретный_вопрос}
]
# RAG документы, few-shot примеры, системные правила — всё кэшируемо
# Не кэшировать: динамические промпты, мелкие (<1024 токенов)
```

Подробно: `haiku-economy.md` §Кэширование токенов
