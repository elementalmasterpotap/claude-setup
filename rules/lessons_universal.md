# Уроки — универсальные (не привязаны к домену)

Выкачано из MPC-BE Ambient Shaders. Применимо в любом проекте.

---

## PowerShell / Windows

### PS-1 — ConvertTo-Json двойное экранирование \uXXXX
**Проблема:** `@{body="текст"} | ConvertTo-Json` экранирует `\` в `\\` → `\u0427` становится `\\u0427` → GitHub/API получает буквальный текст `\u0427`.
**Решение:** сырая JSON-строка в одинарных кавычках `$body = '{"key":"value \u0427"}'` — PS не интерпретирует одинарные кавычки, `\u` попадает в JSON как есть.
**Правило:** для API с Unicode-escape — только сырые одинарные кавычки, никогда `ConvertTo-Json`.

### PS-2 — Кракозябры в консоли ≠ повреждённые данные
**Проблема:** PowerShell показывает `вЂ"` или `??` вместо кириллицы — кажется что данные испорчены.
**Причина:** консоль Windows работает в cp866/cp1251, данные UTF-8 — визуально мусор, но в памяти и на сервере всё правильно.
**Правило:** проверять результат через браузер или WebFetch, не доверять консольному выводу кириллицы.

### PS-3 — inline -Command ломается на сложных скриптах
**Проблема:** длинный скрипт в `powershell.exe -Command "..."` через bash — конфликты кавычек, потеря переносов строк.
**Решение:** писать в `.ps1` файл, запускать через `powershell.exe -File script.ps1`, удалять после.
**Правило:** сложнее 2 строк — всегда через файл.

---

## C# / csc.exe (.NET Framework 4.x / C# 5)

### CS-1 — Expression-bodied members не поддерживаются в C# 5
**Проблема:** `string S(string a, string b) => isRu ? a : b;` — синтаксис C# 6+, csc.exe из .NET 4.x не компилирует.
**Решение:** `string S(string a, string b) { return isRu ? a : b; }` — классический блочный синтаксис.

### CS-2 — Auto-property initializers не поддерживаются в C# 5
**Проблема:** `public Color AccentColor { get; set; } = Color.Gray;` — синтаксис C# 6+.
**Решение:** инициализировать в конструкторе: `AccentColor = Color.Gray;`

### CS-3 — csc.exe путь на Windows
```
C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe
```
Компиляция WinForms:
```powershell
& $csc /target:winexe /out:"App.exe" /reference:System.Windows.Forms.dll /reference:System.Drawing.dll /reference:System.dll /optimize+ "src\App.cs"
```

---

## Telegram Bot API

### TG-1 — Caption limit 1024 символа (Premium не помогает)
**Проблема:** фото + подпись через Bot API ограничены 1024 символами, даже если у владельца канала Telegram Premium.
**Причина:** Premium расширяет лимит для ручной отправки через приложение (до 2048), но Bot API — отдельный лимит, 1024 фиксировано.
**Решение варианты:**
- Два сообщения: `sendPhoto` (без caption или краткая) + `sendMessage` (полный текст)
- Пользователь постит вручную через приложение с Premium (2048 символов — влезает большинство постов)

### TG-2 — sendPhoto vs sendMessage
```
sendPhoto — photo + caption (≤1024)
sendMessage — только текст, но можно вставить preview картинку через URL
sendMediaGroup — несколько медиа, caption только на первый элемент
```

### TG-3 — Отправка через Bot API
```powershell
$botToken = '123456:ABC...'
$chatId   = '@channel_username'  # или числовой ID

# Текст
Invoke-RestMethod "https://api.telegram.org/bot$botToken/sendMessage" -Method POST -Body @{
    chat_id    = $chatId
    text       = $text
    parse_mode = 'Markdown'
}

# Фото из файла
$form = @{ chat_id=$chatId; parse_mode='Markdown'; caption=$caption }
Invoke-RestMethod "https://api.telegram.org/bot$botToken/sendPhoto" -Method POST `
    -Form ($form + @{ photo=Get-Item $photoPath })
```

---

## GitHub API

### GH-1 — Успешный деплой ≠ рабочий результат
Деплой/пуш/релиз могут завершиться без ошибок, но результат — не рабочий (runtime-компиляция, неверный файл, неверная ветка). Всегда проверять руками.

### GH-2 — Upload endpoint отличается от API endpoint
- API: `api.github.com/repos/.../releases`
- Upload ассетов: `uploads.github.com/repos/.../releases/{id}/assets`

### GH-3 — Release notes с кириллицей
Подробно в `rules/github_ops.md` раздел 7. Короткий вывод: сырая JSON-строка с `\uXXXX`, никакого `ConvertTo-Json`.

---

## Универсальные принципы из практики

### U-1 — Не добавлять несколько рискованных изменений за раз
Если поломка — непонятно что сломало. Одно изменение → проверка → следующее.

### U-2 — Всегда иметь откат до начала правки
`cp file.backup file` — 30 секунд, но спасает часы работы.

### U-3 — "Успешно установлено" ≠ "правильно работает"
Любой install/deploy скрипт только копирует файлы. Реальная проверка — запустить и посмотреть руками.

### U-4 — Не менять сигнатуры функций без обновления всех вызовов
Один несинхронизированный вызов → ошибка компиляции/runtime → всё перестаёт работать. Проще добавить параметр по умолчанию или передавать через closure/глобальную переменную.
