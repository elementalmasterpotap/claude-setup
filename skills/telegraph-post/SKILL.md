---
name: telegraph-post
description: Создать или обновить статью на Telegraph. Для нового лонгрида — createPage. Для существующего — только editPage (не createPage!). Кириллица только через Python.
disable-model-invocation: true
argument-hint: [URL страницы для редактирования] или [название новой статьи]
---

Опубликуй / обнови Telegraph статью: $ARGUMENTS

## Правила (telegraph.md):

```
кириллица → ТОЛЬКО Python urllib, НИКОГДА curl
существующая страница → editPage (не createPage!)
лонгрид кастомизаций → только через update_telegraph.py (не трогать напрямую)
```

## Структура content (JSON-ноды):

```python
content = [
    {"tag": "h3", "children": ["Заголовок"]},
    {"tag": "p",  "children": ["Текст"]},
    {"tag": "p",  "children": [{"tag": "b", "children": ["Жирный"]}, " обычный"]},
    {"tag": "pre","children": ["код / псевдографика"]},
    {"tag": "blockquote", "children": ["Цитата"]},
    {"tag": "hr"},
]
```

## Python шаблон:

```python
import urllib.request, json, os

TOKEN = os.environ["TELEGRAPH_TOKEN"]

data = json.dumps({
    "access_token": TOKEN,
    "path": "page-path-here",        # или убрать для createPage
    "title": "Заголовок",
    "author_name": "Potap",
    "author_url": "https://t.me/potap_attic",
    "content": content,
    "return_content": False
}).encode("utf-8")

req = urllib.request.Request(
    "https://api.telegra.ph/editPage/page-path-here",  # или createPage
    data=data, headers={"Content-Type": "application/json"}
)
result = json.loads(urllib.request.urlopen(req).read())
print(result["result"]["url"])
```

Напиши скрипт для задачи и запусти его. Верни URL страницы.
