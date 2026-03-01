# GitHub Formatting — оформление репо

Чеклист и шаблоны для полного оформления репо в стиле Потапа.

---

## Чеклист нового репо

```
[ ] Описание репо (1 строка, на английском — GitHub лучше индексирует)
[ ] Homepage → ссылка на Telegram канал / сайт
[ ] Topics: 6-10 штук (технология + область + платформа)
[ ] README.md: лого + бейджи + описание + установка + таблица фич
[ ] .gitignore: архивы, бэкапы, IDE, OS, .claude локальное
[ ] LICENSE: MIT (если открытый проект)
[ ] docs/PATCHNOTES.md: история изменений
[ ] Релиз с тегом + правильным описанием + ассет (архив, не просто .exe)
```

---

## README — структура

```markdown
<div align="center">
  <img src="logo/[файл]" width="460" alt="[название] — [слоган]" />

  <br><br>

  **[Слоган одной строкой]**<br>
  [Три фичи через · ]

  <br>

  [![](https://img.shields.io/badge/v1.0.0-0099CC?style=flat-square)](https://github.com/[user]/[repo]/releases)
  [![](https://img.shields.io/badge/Windows-0078D6?style=flat-square&logo=windows&logoColor=white)](...)
  [![](https://img.shields.io/badge/[технология]-FF7B00?style=flat-square)]([ссылка])
  [![](https://img.shields.io/badge/лицензия-MIT-22AA44?style=flat-square)](LICENSE)
  [![](https://img.shields.io/badge/Telegram-канал-26A5E4?style=flat-square&logo=telegram&logoColor=white)](https://t.me/potap_attic)

  <br>

  **[⬇ Название.v1.0.0.zip](https://github.com/.../releases/download/v1.0.0/...)** — [что внутри]
</div>

---

[Одна строка — суть проекта, зачем он нужен]

[2-3 строки — что делает, чем отличается от очевидных решений]

---

## Установка

[Минимальные шаги — только то что нужно]

---

## Что делает

| [Функция] | [Что видишь] |
|---|---|
| ... | ... |

---

## [Опционально: Кастомизация / Настройка]

[Ссылка на VIBE.md или аналог]

---

## Требования

- [ОС]
- [Зависимость 1]
- [Зависимость 2]

---

## Удаление / Откат

[Команды]

---

## Разработка

- [`docs/PATCHNOTES.md`](docs/PATCHNOTES.md) — история изменений
- [`docs/DEVELOPMENT_RULES.md`](docs/DEVELOPMENT_RULES.md) — архитектурные решения
```

---

## Бейджи — шпаргалка

```markdown
# Версия
[![](https://img.shields.io/badge/v1.0.0-0099CC?style=flat-square)](URL)

# Платформы
[![](https://img.shields.io/badge/Windows-0078D6?style=flat-square&logo=windows&logoColor=white)](URL)
[![](https://img.shields.io/badge/Linux-FCC624?style=flat-square&logo=linux&logoColor=black)](URL)
[![](https://img.shields.io/badge/macOS-000000?style=flat-square&logo=apple&logoColor=white)](URL)

# Технологии
[![](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)](URL)
[![](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)](URL)
[![](https://img.shields.io/badge/C%23-239120?style=flat-square&logo=csharp&logoColor=white)](URL)
[![](https://img.shields.io/badge/Rust-000000?style=flat-square&logo=rust&logoColor=white)](URL)
[![](https://img.shields.io/badge/Go-00ADD8?style=flat-square&logo=go&logoColor=white)](URL)

# Лицензия
[![](https://img.shields.io/badge/лицензия-MIT-22AA44?style=flat-square)](LICENSE)

# Telegram
[![](https://img.shields.io/badge/Telegram-канал-26A5E4?style=flat-square&logo=telegram&logoColor=white)](https://t.me/potap_attic)

# Произвольный
[![](https://img.shields.io/badge/[ТЕКСТ]-[ЦВЕТ_HEX]?style=flat-square)](URL)
# style варианты: flat-square · flat · for-the-badge · plastic
```

---

## Topics — подбор

Принцип: технология + что делает + платформа + ключевые слова для поиска.
6-10 штук — оптимально. Только строчные буквы, дефисы вместо пробелов.

Примеры по категориям:
```
Язык:      python, typescript, csharp, rust, hlsl, powershell
Платформа: windows, linux, macos, cross-platform
Область:   shader, post-processing, media-player, game-tool, cli-tool, gui
Тема:      ambilight, color-grading, automation, ai-generated
Фреймворк: winforms, electron, tauri, fastapi
```

---

## Описание репо (description field)

- На английском (GitHub индексирует и рекомендует на английском)
- 1 строка, до 120 символов
- Суть без воды: что это + для чего

Примеры:
```
Software Ambilight for MPC-BE - HLSL post-processing shader
CLI tool for automated deployment with rollback support
Dark-theme GUI installer for Windows applications
```

---

## Описание релиза — структура

```markdown
### Что внутри архива

- `[файл]` — [назначение]
- `[файл]` — [назначение]

---

**Установка:** [одна строка как запустить]
**Включение:** [одна строка как активировать]

---

**[Полная история изменений](ссылка)**  ·  **[README](ссылка)**
```

⚠️ Кириллица в релизе — только через `\uXXXX` в сыром JSON. Подробно в `github_ops.md`.

---

## Полный флоу оформления нового репо

```
1. git init + первый коммит
2. Создать репо через API (github_ops.md §1)
3. git remote + push (github_ops.md §2)
4. Задать description + homepage (github_ops.md §3)
5. Задать topics (github_ops.md §3)
6. Создать релиз (github_ops.md §4)
7. Загрузить ассет-архив (github_ops.md §5)
8. Обновить описание релиза с кириллицей (github_ops.md §7)
9. Проверить через WebFetch что всё отображается
```
