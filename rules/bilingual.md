# Bilingual — двуязычность GitHub репозиториев

<!-- Stop hook: НЕВОЗМОЖНО — стилистическое правило, нет машинных паттернов -->
<!-- Skill: gh-setup/SKILL.md включает создание README -->

## Принцип

GitHub не поддерживает нативную локализацию. Решение — HTML `<details>` с языковыми секциями.

---

## Структура двуязычного README

```markdown
<div align="center">
  <!-- лого, бейджи -->

  <details>
  <summary>🇬🇧 English</summary>

  **One-line description in English.**
  What it does. Why it's useful.

  ## Installation
  [steps]

  ## Features
  | Feature | Description |
  |---------|-------------|
  | ... | ... |

  </details>

  <details open>
  <summary>🇷🇺 Русский</summary>

  **Описание одной строкой на русском.**
  Что делает. Зачем нужно.

  ## Установка
  [шаги]

  ## Что делает
  | Функция | Описание |
  |---------|----------|
  | ... | ... |

  </details>
</div>
```

**Правило:** `<details open>` — русская версия открыта по умолчанию (аудитория Потапа).

---

## Description поля репо

GitHub description — всегда на английском (GitHub лучше индексирует):
```
Software Ambilight for MPC-BE — HLSL post-processing shader
```

Topics — на английском, строчные, дефисы:
```python
["shader", "hlsl", "ambilight", "mpc-be", "post-processing", "windows"]
```

---

## Правило двуязычности при создании нового репо

1. README → две `<details>` секции (EN + RU), открыта RU
2. description → английский
3. topics → английский
4. Патчноты (`docs/PATCHNOTES.md`) → русский (это внутренняя документация)
5. Код, комментарии → английский (международный стандарт)

---

## Шаблон двуязычного бейдж-блока

```markdown
<div align="center">

[![](https://img.shields.io/badge/v1.0.0-0099CC?style=flat-square)](https://github.com/USER/REPO/releases)
[![](https://img.shields.io/badge/Windows-0078D6?style=flat-square&logo=windows&logoColor=white)](https://github.com/USER/REPO)
[![](https://img.shields.io/badge/license-MIT-22AA44?style=flat-square)](LICENSE)
[![](https://img.shields.io/badge/Telegram-channel-26A5E4?style=flat-square&logo=telegram&logoColor=white)](https://t.me/potap_attic)

</div>
```

Бейджи — только на английском (универсально).

---

## Обновление существующих репо

При следующем открытии любого проекта:
1. Проверить README на двуязычность
2. Если монолингвальный → добавить `<details>` обёртку
3. Если нет EN версии → создать сжатый перевод
4. description → перевести на английский если на русском

---

## Исключения

```
· README.md проектов где аудитория строго русская → только RU (но description EN)
· Внутренние доки (DEVELOPMENT_RULES, PATCHNOTES) → RU (не публичные)
· Комментарии в коде → EN всегда
```
