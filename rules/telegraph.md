# Telegraph — публикация статей

Токен в env: `$TELEGRAPH_TOKEN` (задан в settings.json глобально).
Аккаунт: `potap` · author_url: https://t.me/potap_attic

---

## Создать страницу

⚠️ Кириллица через curl ломается (`CONTENT_TEXT_REQUIRED`). Всегда использовать Python:

```python
import urllib.request, json

TOKEN = os.environ["TELEGRAPH_TOKEN"]

content = [
    {"tag": "h3", "children": ["Заголовок"]},
    {"tag": "p",  "children": ["Первый параграф"]},
    {"tag": "p",  "children": ["Второй параграф"]},
]

data = json.dumps({
    "access_token": TOKEN,
    "title": "Заголовок страницы",
    "author_name": "Potap",
    "author_url": "https://t.me/potap_attic",
    "content": content,
    "return_content": False
}).encode("utf-8")

req = urllib.request.Request(
    "https://api.telegra.ph/createPage",
    data=data,
    headers={"Content-Type": "application/json"}
)
result = json.loads(urllib.request.urlopen(req).read())
print(result["result"]["url"])
```

Возвращает `result.url` — ссылка на опубликованную страницу.

## Структура content (JSON-массив нод)

```json
[
  {"tag": "h3", "children": ["Заголовок раздела"]},
  {"tag": "p",  "children": ["Обычный текст"]},
  {"tag": "p",  "children": [{"tag": "b", "children": ["Жирный"]}, " обычный"]},
  {"tag": "p",  "children": [{"tag": "i", "children": ["Курсив"]}]},
  {"tag": "p",  "children": [{"tag": "a", "href": "https://...", "children": ["Ссылка"]}]},
  {"tag": "pre","children": ["код блок"]},
  {"tag": "blockquote", "children": ["Цитата"]},
  {"tag": "hr"},
  {"tag": "figure", "children": [
    {"tag": "img", "attrs": {"src": "https://..."}},
    {"tag": "figcaption", "children": ["Подпись к фото"]}
  ]}
]
```

Доступные теги: `p` `h3` `h4` `br` `b` `i` `a` `pre` `code` `blockquote` `hr` `figure` `img` `figcaption` `ul` `ol` `li`

## Редактировать существующую страницу

⚠️ curl ломает кириллицу так же как при createPage. Только Python:

```python
data = json.dumps({
    "access_token": TOKEN,
    "path": "page-path-after-telegra-ph",
    "title": "Заголовок",
    "author_name": "Potap",
    "author_url": "https://t.me/potap_attic",
    "content": content,
    "return_content": False
}).encode("utf-8")

req = urllib.request.Request(
    "https://api.telegra.ph/editPage/page-path-after-telegra-ph",
    data=data,
    headers={"Content-Type": "application/json"}
)
result = json.loads(urllib.request.urlopen(req).read())
print(result["result"]["url"])
```

`path` — часть URL после `telegra.ph/` (например `Kak-ya-kastomiziruyu-Claude-03-01`).

## Лонгрид про кастомизации — фиксированный файл

Лонгрид: `https://telegra.ph/Kak-ya-kastomiziruyu-Claude-pravila-pamyat-i-moduli-03-01`
Скрипт обновления: `~/.claude/update_telegraph.py`

Правила:
- Только `editPage`, никогда `createPage` (не плодить новые версии)
- Один и тот же файл — обновляется в месте, не пересоздаётся
- Писать только про фичи, не про баг-фиксы
- Обновлять при каждом добавлении или удалении глобальной кастомизации

## Получить список своих страниц

```bash
curl -s "https://api.telegra.ph/getPageList?access_token=$TELEGRAPH_TOKEN&limit=10"
```

## Стиль постов

Тот же что для Telegram канала → `communication.md`.
Коротко: чувак-гик, не ассистент. Неформально, без канцелярита. Отсылки органично по смыслу.
Telegraph даёт форматирование — использовать `h3` для разделов, `pre` для кода, `blockquote` для акцентов.

## Псевдографика в лонгридах

Использовать в `pre` блоках — только где реально информативнее текста, не ради красоты.

**Когда уместна:**
- Дерево файловой структуры
- Маршрутизатор задача → файл (ветки с `├─` `└─`)
- Таблица сравнения двух вариантов
- Цепочка шагов / pipeline (`A → B → C`)
- Два уровня чего-то рядом (`prev` vs `backup`)

**Когда НЕ нужна:**
- Просто список — обычный `ul`/`ol` читабельнее
- Одиночная строка — незачем оборачивать в рамку
- Где текст и так понятен без схемы

**Символы box-drawing для `pre`:**
```
├─  └─  │   ─   →   ←   ⇒
╔═  ╗   ╚═  ╝   ║   ═
┌─  ┐   └─  ┘   │   ─
```

## Воркфлоу публикации

1. Сформировать текст в стиле `communication.md`
2. Разбить на ноды (p / h3 / pre / blockquote / hr)
3. Добавить псевдографику где помогает читаемости
4. `createPage` → получить URL
5. Вернуть пользователю ссылку

Для длинных постов с форматированием — Telegraph предпочтительнее Telegram (нет лимита 4096 символов).
