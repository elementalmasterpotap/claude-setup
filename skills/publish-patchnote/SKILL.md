# publish-patchnote

Публикует первый (свежий) патчнот из `docs/PATCHNOTES.md` как отдельную Telegraph страницу.

<!-- user-invocable: true -->
<!-- action: run-script -->

## Когда использовать

После написания патчнота — опубликовать его на Telegraph для последующей ссылки из Telegram канала.

## Как вызвать

```
/publish-patchnote
/publish-patchnote [путь к PATCHNOTES.md]
```

## Что делает

1. Берёт первый блок из PATCHNOTES.md (последний патч — он вверху)
2. Конвертирует Markdown → Telegraph nodes
3. Создаёт новую страницу через `createPage`
4. Возвращает URL опубликованной страницы

## Команда запуска

```bash
python3 ~/.claude/scripts/publish-patchnote.py [args]
```

Аргументы:
- без аргумента → ищет `docs/PATCHNOTES.md` в CWD
- с аргументом → `python3 ~/.claude/scripts/publish-patchnote.py путь/к/PATCHNOTES.md`

## Требования

- `TELEGRAPH_TOKEN` в env (задан в settings.json)
- `docs/PATCHNOTES.md` существует в текущем проекте (или передан путь явно)
- Структура патчнота: `## Патч vX.X.X — YYYY-MM-DD` в начале блока

## Связанные скрипты

- `~/.claude/scripts/publish-patchnote.py` — исполняемый скрипт
- `~/.claude/update_telegraph.py` — обновление лонгрида (другое, не патчноты)
