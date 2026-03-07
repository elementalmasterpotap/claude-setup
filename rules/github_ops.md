# GitHub Operations — без gh CLI, чистый API

Весь GitHub через PowerShell + `Invoke-RestMethod`. gh CLI не нужен.

## Переменные (задавать в начале каждого скрипта)
```powershell
$token = 'ghp_XXXXXXXXXXXXXXXXXXXXXX'
$repo  = 'username/repo-name'
$h     = @{ Authorization='Bearer '+$token; 'User-Agent'='PS'; Accept='application/vnd.github.v3+json' }
```

---

## 1. Создать репозиторий
```powershell
$body = '{"name":"repo-name","description":"Описание","private":false}'
Invoke-RestMethod -Method POST 'https://api.github.com/user/repos' -Headers $h -Body $body -ContentType 'application/json'
```

## 2. Первый пуш
```powershell
git init
git add .
git commit -m "feat: initial commit"
git remote add origin "https://$token@github.com/$repo.git"
git branch -M main
git push -u origin main
# После пуша — убрать токен из remote:
git remote set-url origin "https://github.com/$repo.git"
```

## 3. Установить topics и homepage
```powershell
# Topics
$body = '{"names":["topic1","topic2","topic3"]}'
Invoke-RestMethod -Method PUT "https://api.github.com/repos/$repo/topics" -Headers $h -Body $body -ContentType 'application/json'

# Homepage (ссылка под описанием репо)
$body = '{"homepage":"https://t.me/your_channel"}'
Invoke-RestMethod -Method PATCH "https://api.github.com/repos/$repo" -Headers $h -Body $body -ContentType 'application/json'
```

## 4. Создать релиз
```powershell
$body = '{"tag_name":"v1.0.0","name":"v1.0.0","body":"Описание релиза","draft":false,"prerelease":false}'
$release = Invoke-RestMethod -Method POST "https://api.github.com/repos/$repo/releases" -Headers $h -Body $body -ContentType 'application/json'
$releaseId = $release.id
```

## 5. Загрузить ассет в релиз
```powershell
$file     = "C:\path\to\file.zip"
$fileName = "MyApp.v1.0.0.zip"
$uploadH  = @{ Authorization='Bearer '+$token; 'User-Agent'='PS'; 'Content-Type'='application/zip' }

$bytes = [System.IO.File]::ReadAllBytes($file)
Invoke-RestMethod -Method POST `
    "https://uploads.github.com/repos/$repo/releases/$releaseId/assets?name=$fileName" `
    -Headers $uploadH -Body $bytes
```
**Важно:** upload endpoint — `uploads.github.com`, не `api.github.com`.

## 6. Получить список ассетов / удалить ассет
```powershell
# Список
$assets = Invoke-RestMethod "https://api.github.com/repos/$repo/releases/$releaseId/assets" -Headers $h

# Удалить конкретный
foreach ($a in $assets) {
    if ($a.name -like '*.exe') {
        Invoke-RestMethod -Method DELETE "https://api.github.com/repos/$repo/releases/assets/$($a.id)" -Headers $h
    }
}
```

## 7. Обновить описание релиза

### ⚠️ ЛОВУШКА: двойное экранирование через ConvertTo-Json
`ConvertTo-Json` экранирует `\` → `\\`, поэтому `\uXXXX` становится `\\uXXXX` и GitHub показывает буквальный текст `\uXXXX` вместо символа.

**Правильно — сырая JSON-строка в одинарных кавычках:**
```powershell
# Одинарные кавычки PS — никакого интерпретирования escape-последовательностей
# \uXXXX в строке → \uXXXX в JSON → GitHub декодирует как Unicode
$body = '{"tag_name":"v1.0.0","name":"v1.0.0 \u2014 My App","body":"### \u0427\u0442\u043e \u043d\u043e\u0432\u043e\u0433\u043e\n\n- \u0424\u0438\u0447\u0430 1\n- \u0424\u0438\u0447\u0430 2"}'

Invoke-RestMethod -Method PATCH "https://api.github.com/repos/$repo/releases/$releaseId" `
    -Headers $h -Body $body -ContentType 'application/json' | Out-Null
```

**Сгенерировать \uXXXX для кириллицы:**
```powershell
$text = "Что нового"
$escaped = -join ($text.ToCharArray() | ForEach-Object {
    $code = [int][char]$_
    if ($code -gt 127) { '\u{0:X4}' -f $code } else { [string]$_ }
})
# Результат: \u0427\u0442\u043e \u043d\u043e\u0432\u043e\u0433\u043e
```

## 8. Запустить скрипт без проблем с кодировкой консоли

**Никогда не использовать inline `-Command` для сложных скриптов с кириллицей:**
```powershell
# ПЛОХО — inline -Command + кириллица = кракозябры
powershell.exe -Command "Write-Host 'Привет'"

# ХОРОШО — писать в .ps1, запускать через -File
$script | Set-Content "_tmp.ps1" -Encoding UTF8
powershell.exe -File "_tmp.ps1"
Remove-Item "_tmp.ps1"
```

**Кракозябры в выводе консоли ≠ данные повреждены.** Windows консоль часто показывает UTF-8 кириллицу как мусор (cp866/cp1251), но API получает правильные данные. Проверять результат через браузер / WebFetch, не по консольному выводу.

## 9. Структура .gitignore (стартер)
```
# Архивы
*.7z
*.zip
*.rar

# Бэкапы
docs/*.prev.*
docs/*.backup.*

# Claude локальное
.claude/settings.local.json
.claude/universal-rules.md
.claude/universal-memory.md

# IDE
.vscode/
.idea/

# OS
Thumbs.db
desktop.ini
.DS_Store
```
