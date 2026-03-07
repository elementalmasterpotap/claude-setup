---
name: haiku-router
description: Правила маршрутизации задач на Haiku субагентов вместо Sonnet. Загружается автоматически при планировании задач исследования кода, поиска файлов, анализа без правок, аудитов структуры.
user-invocable: false
---

# Haiku Router — когда делегировать субагенту

Haiku 4.5: $1/$5 per 1M tokens. Sonnet: $3/$15. Разница 3-5x по цене, 2x по скорости.
Реальная экономия с субагентами: 85-96%.

## Быстрый критерий

```
prompt + ожидаемый ответ < 2000 токенов  →  Haiku без вопросов
содержит "explain why" / "reasoning" / "step by step"  →  Sonnet
задача только читает, не меняет  →  Haiku
нужен Edit/Write/решение  →  Sonnet
```

## Маппинг задача → агент

| Паттерн задачи | Агент | Инструменты |
|---|---|---|
| "найди все файлы где..." | **codebase-explorer** | Grep, Glob |
| "покажи структуру X" | **codebase-explorer** | LS, Glob |
| "перечисли все X в проекте" | **codebase-explorer** | Grep |
| "что делает этот файл/функция" | **codebase-explorer** | Read |
| "есть ли дубли / конфликты" | **codebase-explorer** | Read, Grep |
| "как устроен X" (только анализ) | **codebase-explorer** | Read |
| "проверь соответствие / аудит" | **codebase-explorer** | Read, Grep |
| "сколько строк / функций" | **codebase-explorer** | Bash(wc) |
| форматирование / трансформация | **codebase-explorer** | Read |
| summarization большого текста | **codebase-explorer** | Read |
| псевдографика > 30 строк (большая схема, итоговая таблица) | **codebase-explorer** | — (только генерация) |
| code review (баги, антипаттерны) | **code-reviewer** | Read, Grep |
| HLSL диагностика | **shader-expert** | Read, Grep |

## Граничные случаи → Sonnet

```
"найди И исправь"          → Sonnet  (нужен Edit)
"объясни И предложи"       → Sonnet  (нужны рассуждения)
многошаговая задача        → Sonnet  (зависимые действия)
нужен контекст диалога     → Sonnet  (агент его не видит)
архитектурное решение      → Sonnet  (сложный выбор)
слова: reasoning, step by step, explain why  → Sonnet
```

## Двойная экономия — главный инсайт

Subagent держит verbose результат у себя → main context получает только summary.
Экономится и цена модели (3-5x) И токены в основном контексте.
Это важнее чем просто "Haiku дешевле".

## Параллельный паттерн

Когда N независимых задач одного типа — запускать несколько Haiku параллельно:

```
[→ Haiku ×3 параллельно] анализирую три директории...

Task(subagent_type="codebase-explorer", prompt="анализируй rules/...")    # параллельно
Task(subagent_type="codebase-explorer", prompt="анализируй scripts/...")  # параллельно
Task(subagent_type="codebase-explorer", prompt="анализируй skills/...")   # параллельно
```

## Правило пометки

Перед каждым `Task(subagent_type=...)` с Haiku агентом — писать в ответе:

```
[→ Haiku] <что делаю>...
```

Примеры:
- `[→ Haiku] ищу все файлы где используется X...`
- `[→ Haiku ×2] параллельно анализирую A и B...`
- `[→ Haiku] проверяю дубли в rules/...`

## Шаблон вызова (одиночный)

```
[→ Haiku] <описание>...

Task(
  subagent_type="codebase-explorer",  # или "code-reviewer" / "shader-expert"
  description="<3-5 слов>",
  prompt="<конкретное задание с путями и критериями>"
)
```

Результат обработать и вернуть кратко, с псевдографикой.
