---
name: tg-ref
description: Telegram Bot API паттерны — отправка, лимиты, медиа. Автоматически подгружается при задачах с Telegram, Bot API, каналом @potap_attic.
user-invocable: false
---

## Лимиты (TG-1)

| Метод | Лимит | Решение при превышении |
|-------|-------|----------------------|
| sendMessage | 4096 символов | разбить на части |
| sendPhoto caption | **1024** символа | sendPhoto (краткая) + sendMessage (полный текст) |
| Bot API caption | 1024 (Premium не помогает) | это лимит API, не приложения |

## sendMessage

```powershell
$botToken = $env:TELEGRAM_BOT_TOKEN
$chatId   = '@potap_attic'

Invoke-RestMethod "https://api.telegram.org/bot$botToken/sendMessage" -Method POST -Body @{
    chat_id    = $chatId
    text       = $text
    parse_mode = 'HTML'   # HTML надёжнее Markdown v1
}
```

## sendPhoto из файла

```powershell
$form = @{ chat_id=$chatId; parse_mode='HTML'; caption=$caption }
Invoke-RestMethod "https://api.telegram.org/bot$botToken/sendPhoto" -Method POST `
    -Form ($form + @{ photo=Get-Item $photoPath })
```

## parse_mode HTML vs Markdown

```
HTML:     <b>жирный</b>  <i>курсив</i>  <a href="url">ссылка</a>  <code>код</code>
Markdown: *жирный*       _курсив_       [текст](url)              `код`
```
HTML предпочтительнее — меньше конфликтов с символами в тексте.

## editMessage (обновить существующий пост)

```powershell
Invoke-RestMethod "https://api.telegram.org/bot$botToken/editMessageText" -Method POST -Body @{
    chat_id    = $chatId
    message_id = $messageId
    text       = $newText
    parse_mode = 'HTML'
    link_preview_options = @{ url = $previewUrl }
}
```
