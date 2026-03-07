---
name: gh-ops-ref
description: GitHub API паттерны через PowerShell — репо, релизы, ассеты, topics. Автоматически подгружается при задачах с GitHub API, созданием релизов, загрузкой ассетов.
user-invocable: false
---

## Инициализация

```powershell
$token = $env:GITHUB_PERSONAL_ACCESS_TOKEN
$repo  = 'username/repo-name'
$h     = @{ Authorization='Bearer '+$token; 'User-Agent'='PS'; Accept='application/vnd.github.v3+json' }
```

## Создать релиз → получить ID

```powershell
$body = '{"tag_name":"v1.0.0","name":"v1.0.0","body":"Release","draft":false,"prerelease":false}'
$release = Invoke-RestMethod -Method POST "https://api.github.com/repos/$repo/releases" -Headers $h -Body $body -ContentType 'application/json'
$releaseId = $release.id
```

## Загрузить ассет (uploads.github.com — не api!)

```powershell
$bytes = [System.IO.File]::ReadAllBytes("C:\path\to\file.zip")
$uploadH = @{ Authorization='Bearer '+$token; 'User-Agent'='PS'; 'Content-Type'='application/zip' }
Invoke-RestMethod -Method POST "https://uploads.github.com/repos/$repo/releases/$releaseId/assets?name=App.v1.0.0.zip" `
    -Headers $uploadH -Body $bytes
```

## Установить topics и homepage

```powershell
Invoke-RestMethod -Method PUT "https://api.github.com/repos/$repo/topics" `
    -Headers $h -Body '{"names":["topic1","topic2"]}' -ContentType 'application/json'

Invoke-RestMethod -Method PATCH "https://api.github.com/repos/$repo" `
    -Headers $h -Body '{"homepage":"https://t.me/potap_attic"}' -ContentType 'application/json'
```

## Кириллица в релизе → одинарные кавычки + \uXXXX

```powershell
# Правило PS-1: одинарные кавычки, не ConvertTo-Json!
$body = '{"tag_name":"v1.0.0","name":"v1.0.0 \u2014 \u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435","body":"### \u0427\u0442\u043e \u043d\u043e\u0432\u043e\u0433\u043e"}'
Invoke-RestMethod -Method PATCH "https://api.github.com/repos/$repo/releases/$releaseId" `
    -Headers $h -Body $body -ContentType 'application/json' | Out-Null
```

## Pre-push аудит токенов (ОБЯЗАТЕЛЬНО)

```bash
grep -rn "ghp_[A-Za-z0-9]{36}\|[0-9]{10}:AA[A-Za-z0-9_-]{33}\|475c06[a-f0-9]{50}" \
  . --include="*.py" --include="*.md" --include="*.json" | grep -v ".git/"
```
Плейсхолдеры (XXXX, $TOKEN) — ок. Реальные значения — СТОП.
