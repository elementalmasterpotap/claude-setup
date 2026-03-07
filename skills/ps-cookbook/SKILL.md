---
name: ps-cookbook
description: PowerShell паттерны и антипаттерны. Автоматически подгружается при задачах с PowerShell, Windows, GitHub API через PS, установщиками.
user-invocable: false
---

## PS-1 — JSON + кириллица → одинарные кавычки

```
ПЛОХО:  $body = "@{key='значение'}" | ConvertTo-Json   ← \u → \\u, GitHub видит буквальный текст
ХОРОШО: $body = '{"key":"\u0437\u043d\u0430\u0447"}'   ← одинарные кавычки, \uXXXX как есть
```

Сгенерировать \uXXXX:
```powershell
$text = "Что нового"
-join ($text.ToCharArray() | % { $c=[int][char]$_; if($c -gt 127){'\u{0:X4}' -f $c}else{[string]$_} })
```

## PS-2 — Кракозябры в консоли ≠ повреждённые данные

Windows консоль (cp866/cp1251) показывает UTF-8 как мусор. Данные в порядке.
Проверять результат через браузер / WebFetch — не доверять консольному выводу.

## PS-3 — Сложные скрипты → файл

```
ПЛОХО:  powershell.exe -Command "длинный скрипт с кириллицей"
ХОРОШО: $script | Set-Content "_tmp.ps1" -Encoding UTF8
         powershell.exe -File "_tmp.ps1"
         Remove-Item "_tmp.ps1"
```

## GitHub upload endpoint

```
API:    api.github.com/repos/.../releases/{id}/assets     ← читать/листать
Upload: uploads.github.com/repos/.../releases/{id}/assets ← загружать файлы
```

```powershell
$bytes = [System.IO.File]::ReadAllBytes($file)
Invoke-RestMethod -Method POST "https://uploads.github.com/repos/$repo/releases/$id/assets?name=$name" `
    -Headers @{ Authorization='Bearer '+$token; 'Content-Type'='application/zip' } -Body $bytes
```

## Кириллица в скриптах — энкодинг

```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "Stop"
```
