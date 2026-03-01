# Universal Rules
# Копия: .claude/universal-rules.md · Память: ~/.claude/memory/MEMORY.md → .claude/universal-memory.md

## Алгоритм сессии

```
ИНИТ (один раз):
  communication.md прочитан? НЕТ──► читать (БЛОКЕР — без него стоп)
  MEMORY.md прочитан?        НЕТ──► читать ──► активировать триггеры
                             ДА──► продолжать

ЗАДАЧА ПОЛУЧЕНА:
  ┌── разговор / вопрос       ──► отвечать напрямую
  ├── shaders/ + детектор     ──► lessons.md + DEVELOPMENT_RULES.md ──► [ВЫСОКИЙ РИСК]
  ├── shaders/ без детектора  ──► hlsl.md
  ├── деплой / патчнот        ──► workflow.md · workflow_universal.md
  ├── вайбкодинг              ──► VIBE.md + hlsl.md · vibe_coding.md
  ├── GitHub / релиз / API    ──► github_ops.md
  ├── GitHub оформление / README / бейджи ──► github_formatting.md
  ├── Telegram / бот / пост   ──► lessons_universal.md (TG-1..TG-3)
  ├── Telegraph / статья      ──► telegraph.md
  ├── C# / PowerShell / Windows ──► lessons_universal.md (PS-1..PS-3, CS-1..CS-3)
  ├── PS installer / WinForms тёмная тема ──► windows_dev.md
  ├── новый проект (старт с нуля) ──► templates/CLAUDE_BASE.md + templates/MEMORY_TEMPLATE.md
  ├── правило / память        ──► CLAUDE.md "Новые записи" ──► проверить дубли
  └── структура / цвет        ──► preferences.md

  3+ шагов или архит. решение? ──► Plan mode (включая верификацию, не только построение)
  Параллельный анализ нужен?   ──► Subagents — один subagent, одна задача; main context чистым
  Неоднозначность?             ──► допущение в ответ, не вопрос  [→ "Неоднозначность"]
  Риск потери работы / крит.?  ──► спросить перед действием

ВЫПОЛНЕНИЕ:
  [ВЫСОКИЙ РИСК]?      ──► озвучить план и допущения явно перед правкой
  Заблокирован?        ──► паттерн в коде ──► docs/ ──► альтернатива  [→ "Блокировка"]
  План пошёл не так?   ──► СТОП ──► перепланировать немедленно, не толкать дальше

ПОСЛЕ ЗАДАЧИ:
  поломка / урок?          ДА──► tasks/lessons.md
  новый паттерн Потапа?    ДА──► MEMORY.md
  визуальное изменение?    ДА──► docs/PATCHNOTES.md
  новое правило?           ДА──► карта владения ──► проверить дубли
  добавлена/удалена/изм. глоб. кастомизация? ДА──► сверить лонгрид с реальным состоянием:
    settings.json (deny/mcpServers/hooks/plugins/alwaysThinking) · rules/ · agents/ · templates/ · skills/
    ──► обновить контент update_telegraph.py ──► запустить скрипт АВТОМАТИЧЕСКИ без вопроса
    ──► скрипт пушит и в GitHub (github.com/elementalmasterpotap/potap-claude-setup) — тоже авто
    Кастомизация = rules/ · scripts/ · agents/ · templates/ · skills/ · settings.json · CLAUDE.md · MEMORY.md
  изменён CLAUDE/MEMORY?   ДА──► синхронизировать копии в проекте
  готово?                  ──► доказать что работает перед отметкой выполненным
```

## Блокировка → не стоп
1. Паттерн в коде  2. `docs/` / история решений  3. Альтернативный подход
Действовать, документировать допущения.

## Неоднозначность → допущения
Допущение в ответе, идти дальше. Спрашивать только при риске потери работы / крит. поломки.

## Деплой
NoPrompt/--yes, без интерактива. Перед "открой и проверь": `powershell -c '$Host.UI.RawUI.WindowSize.Width'`
≥80 = ПК, <80 = телефон → молча, "протестируй на ПК".

## Permissions
`src/` `shaders/` `lib/` — свободно · `docs/` `README` — дополнять, не переписывать · `CI` `infra/` `*.yml` — спрашивать · `logo/` `assets/` — не трогать
Enforcement через hookify: `logo/` `assets/` → block · `CI/` `infra/` `*.yml` → warn · `rm -rf` / `push -f main` → block · `--no-verify` / `reset --hard` → warn
Шаблоны для новых проектов: `templates/hookify/` (6 файлов, скопировать в `.claude/`)

## Commits
`type(scope): description` · feat/fix/refactor/docs/style/chore · не амендить опубликованные

## Pre-push аудит (ОБЯЗАТЕЛЬНО перед любым git push)
```
grep -rn "ghp_[A-Za-z0-9]\{36\}\|[0-9]\{10\}:AA[A-Za-z0-9_-]\{33\}\|475c06[a-f0-9]\{50\}\|edit\.telegra\.ph/auth" \
  . --include="*.py" --include="*.md" --include="*.json" --include="*.ps1" | grep -v ".git/"
```
Плейсхолдеры (XXXX, your_token, $TOKEN) — ок. Реальные значения — СТОП, не пушить.

## Принципы
Минимальный импакт · root cause не симптом · трогать только нужное · не хакать · не дублировать
Нетривиальная правка → спросить себя "есть более элегантный путь?" перед отправкой · объяснять изменения кратко на каждом шаге
Баг-репорт → фиксить автономно, без запроса доп. контекста у пользователя

## Предпочтения (визуал / UX)
Цвет: насыщенные, живые — склоняться к большей насыщенности, не зажимать без причины (артефакт, клиппинг)
UI: тёмная тема по умолчанию для Windows приложений · псевдографика ВЕЗДЕ как дефолт (Stop hook enforce)
Документация: неформально, мат ок, от первого лица — не корпоративно

## Аудит правил
"Без него крит-ошибка?" · Не удалять → универсальная формулировка · <150 строк, детали в .claude/rules/

## Новые записи (правила и память) — воркфлоу
Перед записью:
1. Прочитать целевой файл
2. Прочитать смежные по карте ниже — найти совпадения
3. Смысл уже есть → ссылка; нет → писать сжато (без воды, `·` вместо списков где нет иерархии)
4. После: изменён `CLAUDE.md` или `MEMORY.md` → синхронизировать копии в проекте

Карта правил:
- стиль/тон/мемы/отсылки → `communication.md`
- характер Потапа, правила правил, синхронизация → `MEMORY.md`
- workflow/permissions/деплой/commits/принципы → `CLAUDE.md` глобальный
- деплой/патчнот (универсально) → `workflow_universal.md`
- деплой шейдера, патчноты → `workflow.md` (проектный)
- GitHub API, релизы, ассеты, кодировки → `github_ops.md`
- GitHub оформление, README, бейджи, чеклист → `github_formatting.md`
- Telegram бот, посты, лимиты → `lessons_universal.md` (TG-раздел)
- Telegraph публикация статей → `telegraph.md`
- PowerShell/Windows/C# ловушки → `lessons_universal.md` (PS/CS-разделы)
- PS installer паттерн, C# WinForms тёмная тема → `windows_dev.md`
- вайбкодинг (универсально) → `vibe_coding.md`
- шаблоны (CLAUDE.md/MEMORY/PATCHNOTES/VIBE/Telegram) → `templates/`
- hookify блокировки/предупреждения → `.claude/hookify.*.local.md` · глобальные шаблоны → `templates/hookify/`
- скиллы / slash-команды → `~/.claude/skills/<name>/SKILL.md` (action: disable-model-invocation, knowledge: user-invocable: false)
- HLSL-специфика, константы, антипаттерны → `hlsl.md`
- структура файлов, цвет → `preferences.md`
- детектор, активный шейдер, метафоры проекта → проектный `CLAUDE.md`

Карта памяти (что писать в `MEMORY.md`):
- уникальные паттерны/характер Потапа (не стиль/тон — он в `communication.md`)
- долгосрочные факты из практики: решения, поломки, инсайты
- новые мемы и локальные отсылки
- НЕ писать: стиль/тон → `communication.md` · workflow/деплой/commits → `CLAUDE.md`
