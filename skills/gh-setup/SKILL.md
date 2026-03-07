---
name: gh-setup
description: Полное оформление GitHub репозитория по чеклисту — описание, topics, README, бейджи, .gitignore, лицензия, релиз. Вызывать для нового репо или дооформления существующего.
disable-model-invocation: true
argument-hint: [owner/repo или текущий]
---

Выполни полный чеклист оформления GitHub репозитория: $ARGUMENTS
(если не указан — определи текущий из git remote)

## Шаг 1 — аудит (таблица)

Проверь каждый пункт и покажи статус:

| Пункт | Статус | Что делать |
|-------|--------|-----------|
| Описание репо (EN, ≤120 символов) | ? | |
| Homepage → t.me канал | ? | |
| Topics (6-10 штук) | ? | |
| README: лого + бейджи + описание + установка | ? | |
| .gitignore (архивы, IDE, OS, .claude local) | ? | |
| LICENSE (MIT) | ? | |
| docs/PATCHNOTES.md | ? | |
| Релиз с тегом + ассет-архив | ? | |

## Шаг 2 — выполнить каждый невыполненный пункт

Используй GitHub API через PowerShell (НЕ gh CLI):
```powershell
$token = $env:GITHUB_PERSONAL_ACCESS_TOKEN
$repo  = 'owner/repo'
$h     = @{ Authorization='Bearer '+$token; 'User-Agent'='PS'; Accept='application/vnd.github.v3+json' }
```

Кириллица в API — только \uXXXX через одинарные кавычки PS (правило PS-1).

## Бейджи (шаблон):
```
[![](https://img.shields.io/badge/v1.0.0-0099CC?style=flat-square)](releases)
[![](https://img.shields.io/badge/Windows-0078D6?style=flat-square&logo=windows&logoColor=white)](...)
[![](https://img.shields.io/badge/лицензия-MIT-22AA44?style=flat-square)](LICENSE)
[![](https://img.shields.io/badge/Telegram-канал-26A5E4?style=flat-square&logo=telegram&logoColor=white)](https://t.me/potap_attic)
```
