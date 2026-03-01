<div align="center">

  **Как я кастомизирую Claude: правила, память и модули**

  Авто-обновляемая документация моей настройки Claude Code

  <br>

  [![](https://img.shields.io/badge/Python-3.x-3776AB?style=flat-square&logo=python&logoColor=white)](update_telegraph.py)
  [![](https://img.shields.io/badge/лицензия-MIT-22AA44?style=flat-square)](LICENSE)
  [![](https://img.shields.io/badge/Telegram-канал-26A5E4?style=flat-square&logo=telegram&logoColor=white)](https://t.me/potap_attic)
  [![](https://img.shields.io/badge/Telegraph-лонгрид-009999?style=flat-square)](https://telegra.ph/Kak-ya-kastomiziruyu-Claude-pravila-pamyat-i-moduli-03-01)

  <br>

  **[📖 Читать лонгрид →](https://telegra.ph/Kak-ya-kastomiziruyu-Claude-pravila-pamyat-i-moduli-03-01)**

</div>

---

`update_telegraph.py` авто-обновляет [Telegraph-статью](https://telegra.ph/Kak-ya-kastomiziruyu-Claude-pravila-pamyat-i-moduli-03-01) с документацией по моей настройке Claude Code.

Каждый раз когда я добавляю или убираю кастомизацию — Claude запускает скрипт и статья обновляется. То что в статье = актуальное состояние системы.

---

## Что в документации

| Компонент | Что делает |
|---|---|
| `settings.json` | разрешения, плагины, глобальные токены |
| `~/.claude/CLAUDE.md` | алгоритм сессии, маршрутизатор задач |
| `rules/*.md` | модули по доменам (GitHub, Telegram, Windows, вайбкодинг...) |
| `memory/MEMORY.md` | долговременная память между сессиями |
| `hookify.*.local.md` | block/warn хуки для деструктивных действий |
| Проектный `CLAUDE.md` | специфика отдельных репозиториев |

---

## Запуск

```bash
TELEGRAPH_TOKEN=your_token python update_telegraph.py
```

Получить токен: [telegra.ph API createAccount](https://api.telegra.ph/createAccount?short_name=YourName&author_name=YourName)

---

## Как устроено

`update_telegraph.py` вызывает Telegraph API `editPage` — перезаписывает содержимое существующей статьи. Единственный файл, не пересоздаётся. Claude автоматически запускает его после каждого изменения кастомизаций.

```
кастомизация изменена
        ↓
Claude запускает update_telegraph.py
        ↓
editPage → Telegraph статья обновлена
        ↓
лонгрид отражает актуальное состояние
```

---

## Требования

- Python 3.x (stdlib only, без зависимостей)
- Telegraph access token

---

## Разработка

- [Читать лонгрид](https://telegra.ph/Kak-ya-kastomiziruyu-Claude-pravila-pamyat-i-moduli-03-01) — полная документация системы
- [Telegram-канал](https://t.me/potap_attic) — обновления и посты
