"""
Telegraph-контент лонгрида «Как я кастомизирую Claude».

Хранит ТОЛЬКО контент-ноды. Механика (HTTP, GitHub sync, Telegram) — в update_telegraph.py.

Структура секций — маркеры вида # ═══ СЕКЦИЯ: xxx ═══
При редактировании: читать этот файл, найти нужную секцию, сделать Edit только в ней.
Нет подходящей секции → добавить новую (маркер + переменная + включить в return).
"""


def get_content(ts: str) -> list:
    """
    ts — строка метки времени вида "02.03.2026 14:23 МСК"
    Возвращает список Telegraph-нод для editPage.
    """

    # ═══ СЕКЦИЯ: шапка ═══════════════════════════════════════════════════
    header = [
        {"tag": "p", "children": [{"tag": "i", "children": [f"Обновлено: {ts}"]}]},
        {"tag": "p", "children": [{"tag": "i", "children": [
            "Лонгрид обновляется по команде /sync — когда накапливается несколько изменений или явно прошу. "
            "То что здесь написано = актуальное состояние системы на момент последнего /sync."
        ]}]},
        {"tag": "p", "children": [
            "Накопил приличный стек правил, памяти и плагинов для Claude Code. "
            "Разбираю как всё это устроено — только механика, без воды."
        ]},
    ]

    # ═══ СЕКЦИЯ: оглавление ══════════════════════════════════════════════
    toc = [
        {"tag": "pre", "children": [
            "├─ settings.json ─────── фундамент, разрешения, deny, MCP, хуки\n"
            "├─ CLAUDE.md ─────────── алгоритм сессии, маршрутизатор\n"
            "├─ MEMORY.md ─────────── долговременная память\n"
            "├─ hookify ───────────── block/warn хуки (проектный уровень)\n"
            "├─ rules/ ────────────── 14 модульных md-правил\n"
            "├─ agents/ ───────────── 3 кастомных субагента (все на Haiku)\n"
            "├─ skills/ ───────────── 11 action + 8 knowledge скиллов\n"
            "├─ /review ───────────── система самообучения\n"
            "├─ Проектный CLAUDE.md ─ контекст репо\n"
            "├─ Оптимизация токенов ─ Haiku пак, веб, кэш, SOS\n"
            "└─ GitHub + Telegraph ── инфраструктура (/sync)"
        ]},
        {"tag": "hr"},
    ]

    # ═══ СЕКЦИЯ: settings.json ═══════════════════════════════════════════
    settings = [
        {"tag": "h3", "children": ["settings.json — фундамент"]},
        {"tag": "p", "children": [
            "Глобальный конфиг Claude Code. Живёт в ", {"tag": "code", "children": ["~/.claude/settings.json"]},
            ". Определяет что Claude может делать без запроса и что у него подключено."
        ]},
        {"tag": "pre", "children": [
            "settings.json\n"
            "├── permissions\n"
            "│   ├── allow       → Bash(*), Edit(*), Write(*), Read(*), WebSearch, WebFetch(*)\n"
            "│   ├── deny        → ~/.ssh/**, ~/.aws/**, ~/.gnupg/**, ~/.kube/**, ~/.npmrc...\n"
            "│   └── defaultMode → dontAsk  (работает автономно)\n"
            "├── alwaysThinkingEnabled → true  (extended thinking по умолчанию)\n"
            "├── mcpServers      → {context7}  (живая документация библиотек)\n"
            "├── .claudeignore   → ~/.claude/.claudeignore  (node_modules/lock = −30-80K токенов)\n"
            "├── enabledPlugins  → commit-commands, hookify, github, context7, feature-dev...\n"
            "└── hooks\n"
            "    ├── UPS          → haiku-suggest.py        complexity scoring → [HAIKU_ELIGIBLE]\n"
            "    ├── SessionStart → head CLAUDE.md           реинжект после компакции\n"
            "    ├── PreCompact   → precompact-smart.py      jsonl + LLM summary (Haiku)\n"
            "    ├── PreToolUse   → pretool-safety.py        --no-verify/reset--hard/push-f/rm-rf\n"
            "    ├── PostToolUse  → skills-sync + checkpoint + pattern-logger  (3 хука)\n"
            "    ├── UPS×2        → haiku-suggest + window-tracker  (Pro 5h окно)\n"
            "    └── Stop         → 14 хуков (+ session-length-check: /compact hint)"
        ]},
        {"tag": "p", "children": [
            {"tag": "b", "children": ["deny"]},
            " — Claude физически не может прочитать ~/.ssh, ~/.aws, ~/.gnupg и другие папки с секретами. "
            "Не advisory-правило, а hardware block на уровне permissions."
        ]},
        {"tag": "p", "children": [
            {"tag": "b", "children": ["context7"]},
            " — MCP-сервер, инжектирует актуальную документацию библиотек прямо в контекст. "
            "Решает галлюцинации по API — Claude видит реальные сигнатуры, а не придумывает их."
        ]},
        {"tag": "pre", "children": [
            "UPS (1):        haiku-suggest.py      scoring → [HAIKU_ELIGIBLE] или suppress thinking\n"
            "PreCompact (1): precompact-smart.py   jsonl + Haiku summary (30 exchanges)\n"
            "PreToolUse (1): pretool-safety.py     --no-verify/reset--hard/push-f/rm-rf/logo\n"
            "PostToolUse(3): skills-sync           напоминание /sync если skills/ изменены\n"
            "                checkpoint            лог файлов в SESSION.md\n"
            "                pattern-logger        паттерны для /review\n"
            "Stop (14):      anti-ration           отмазки «за рамками» заблокированы\n"
            "                pseudo-check          4+ пунктов без псевдографики\n"
            "                commit-check          type(scope) + Co-Authored обязательны\n"
            "                token-leak            реальный ghp_/TG/Telegraph токен — стоп\n"
            "                tone-check            канцелярит и подобострастие\n"
            "                deploy-check          без -NoPrompt / --yes — warn\n"
            "                ps-unicode            PS JSON + кириллица в двойных кавычках\n"
            "                patchnote-check       tagline + первое лицо обязательны\n"
            "                csharp-compat         C# 6+ синтаксис в .NET 4.x — warn\n"
            "                github-upload         api.github vs uploads.github\n"
            "                telegraph-edit        createPage лонгрида / curl+кириллица\n"
            "  learning-suggest.py   → обнаружен паттерн/ловушка — предложи /learn\n"
            "  session-stop.py       → сохранение контекста сессии при разрыве соединения\n"
            "  heavy-files-check.py  → warn: node_modules/lock-файл без .claudeignore"
        ]},
        {"tag": "p", "children": [
            "Токены в ", {"tag": "code", "children": ["env"]},
            " — Claude видит их как переменные окружения в любом проекте."
        ]},
    ]

    # ═══ СЕКЦИЯ: CLAUDE.md ═══════════════════════════════════════════════
    claude_md = [
        {"tag": "h3", "children": ["CLAUDE.md — алгоритм сессии"]},
        {"tag": "p", "children": [
            "Глобальный ", {"tag": "code", "children": ["~/.claude/CLAUDE.md"]},
            " — главный файл инструкций. Загружается в каждую сессию."
        ]},
        {"tag": "p", "children": [
            "Главная часть — маршрутизатор: каждый тип задачи направляет Claude к нужному модулю."
        ]},
        {"tag": "pre", "children": [
            "ЗАДАЧА ПОЛУЧЕНА:\n"
            "  ├── разговор / вопрос       → отвечать напрямую\n"
            "  ├── GitHub / релиз / API    → github_ops.md\n"
            "  ├── GitHub оформление       → github_formatting.md\n"
            "  ├── Telegram / бот / пост   → lessons_universal.md\n"
            "  ├── Telegraph / статья      → telegraph.md\n"
            "  ├── деплой / патчнот        → workflow_universal.md\n"
            "  ├── Windows / C# / PS       → lessons_universal.md + windows_dev.md\n"
            "  ├── вайбкодинг              → vibe_coding.md\n"
            "  ├── правило / память        → карта владения → проверить дубли\n"
            "  └── новый проект            → templates/CLAUDE_BASE.md"
        ]},
        {"tag": "p", "children": ["После задачи — автоматические действия:"]},
        {"tag": "pre", "children": [
            "ПОСЛЕ ЗАДАЧИ:\n"
            "  поломка / урок?                    → lessons.md\n"
            "  новый паттерн?                     → MEMORY.md\n"
            "  визуальное изменение?              → PATCHNOTES.md\n"
            "  добавлена/удалена кастомизация?    → сверить лонгрид → update_telegraph.py\n"
            "  новое правило?                     → карта владения → проверить дубли\n"
            "  изменён CLAUDE/MEMORY?             → синхронизировать копии\n"
            "  готово?                            → доказать что работает"
        ]},
        {"tag": "p", "children": [
            "Ещё там: принципы (минимальный импакт, root cause не симптом, не хакать), "
            "правила коммитов, аудит правил, карта владения — что в каком файле хранится."
        ]},
    ]

    # ═══ СЕКЦИЯ: MEMORY.md ═══════════════════════════════════════════════
    memory_md = [
        {"tag": "h3", "children": ["MEMORY.md — долговременная память"]},
        {"tag": "p", "children": [
            "Claude Code не запоминает ничего между сессиями. MEMORY.md — решение: "
            "файл читается в начале каждой сессии и активирует контекст."
        ]},
        {"tag": "p", "children": [
            "Живёт в ", {"tag": "code", "children": ["~/.claude/memory/MEMORY.md"]},
            ". Копия в каждом проекте: ", {"tag": "code", "children": [".claude/universal-memory.md"]}, "."
        ]},
        {"tag": "pre", "children": [
            "Что пишется в MEMORY.md:\n"
            "  ✓  уникальные паттерны и характер пользователя\n"
            "  ✓  долгосрочные факты из практики: решения, поломки, инсайты\n"
            "  ✓  новые мемы и локальные отсылки\n"
            "  ✗  стиль/тон → это в communication.md\n"
            "  ✗  workflow/деплой → это в CLAUDE.md\n"
            "  ✗  дубли того что уже есть где-то ещё"
        ]},
        {"tag": "p", "children": [
            "Claude сам ведёт MEMORY.md во время работы — дописывает новые паттерны, "
            "исправляет устаревшие. Первые строки всегда в контексте, дальше — по необходимости."
        ]},
    ]

    # ═══ СЕКЦИЯ: hookify ═════════════════════════════════════════════════
    hookify = [
        {"tag": "h3", "children": ["hookify — система хуков"]},
        {"tag": "p", "children": [
            "Плагин hookify добавляет точки перехвата до/после действий Claude. "
            "Правила в файлах ", {"tag": "code", "children": [".claude/hookify.*.local.md"]},
            " в папке проекта."
        ]},
        {"tag": "pre", "children": [
            "4 типа событий:\n"
            "  UserPromptSubmit → при получении сообщения от пользователя\n"
            "  PreToolUse       → перед вызовом инструмента (Edit, Bash, Write...)\n"
            "  PostToolUse      → после вызова инструмента\n"
            "  Stop             → перед завершением ответа"
        ]},
        {"tag": "p", "children": ["Каждое правило — отдельный md-файл с YAML-шапкой:"]},
        {"tag": "pre", "children": [
            "---\n"
            "name:         no-rm-rf\n"
            "enabled:      true\n"
            "event:        bash          # bash или file\n"
            "action:       block         # block или warn\n"
            "pattern:      rm\\s+(-rf|-fr)  # regex для bash\n"
            "---\n"
            "⛔ rm -rf — необратимое удаление. Заблокировано."
        ]},
        {"tag": "p", "children": ["Текущие глобальные правила:"]},
        {"tag": "pre", "children": [
            "BLOCK — запрещено без исключений:\n"
            "  rm -rf / rm -fr            необратимое удаление файлов\n"
            "  git push --force main      затирание истории на main/master\n"
            "  редактирование logo/       ассеты заморожены\n"
            "  редактирование assets/     ассеты заморожены\n"
            "\n"
            "WARN — требует осознанного решения:\n"
            "  --no-verify                скип pre-commit хуков\n"
            "  git reset --hard           деструктивная git-операция\n"
            "  git checkout -- .          деструктивная git-операция\n"
            "  git restore .              деструктивная git-операция\n"
            "  git clean -f               деструктивная git-операция\n"
            "  CI / infra / *.yml         изменения требуют подтверждения"
        ]},
        {"tag": "p", "children": [
            "Шаблоны для новых проектов — ",
            {"tag": "code", "children": ["templates/hookify/"]},
            " (6 файлов, скопировать в ", {"tag": "code", "children": [".claude/"]},
            " нового проекта). К глобальным правилам добавляются проектно-специфичные — "
            "например запрет менять конкретную функцию в конкретном файле."
        ]},
    ]

    # ═══ СЕКЦИЯ: rules/ ══════════════════════════════════════════════════
    rules = [
        {"tag": "h3", "children": ["rules/ — модульные md-файлы"]},
        {"tag": "p", "children": [
            "CLAUDE.md держится коротким (<150 строк). Детали выносятся в модули ",
            {"tag": "code", "children": ["~/.claude/rules/"]},
            ". Claude читает нужный только когда задача попадает в его домен."
        ]},
        {"tag": "pre", "children": [
            "~/.claude/rules/\n"
            "├── communication.md         стиль/тон/мемы — БЛОКЕР, читать до первого ответа\n"
            "├── workflow_universal.md    патч → деплой → патчнот → коммит\n"
            "├── github_ops.md            GitHub API через PowerShell без gh CLI\n"
            "├── github_formatting.md     README, бейджи, topics, чеклист репо\n"
            "├── telegraph.md             публикация на Telegraph, editPage\n"
            "├── windows_dev.md           PS installer, C# WinForms тёмная тема\n"
            "├── vibe_coding.md           вайбкодинг — концепция и маппинг\n"
            "├── lessons_universal.md     ловушки: PS / C# / Telegram / GitHub\n"
            "├── token-budget.md          Pro лимит, compact тактика, Haiku пак\n"
            "├── preferences.md           структура файлов, цвет, CSS dropdown\n"
            "├── hlsl.md                  HLSL принципы, откат, что не трогать\n"
            "├── haiku-economy.md         ультимативный пак: когда Haiku, советы сайты/TG/кэш\n"
            "├── subagent-context.md      контекст субагентам только по необходимости\n"
            "└── bilingual.md             двуязычность GitHub (EN/RU details)"
        ]},
        {"tag": "p", "children": [
            {"tag": "b", "children": ["communication.md"]},
            " — единственный модуль с флагом БЛОКЕР. Без него Claude не знает как разговаривать: "
            "стиль, тон, отсылки, мемы. Читается первым делом в каждой сессии. "
            "Псевдографика (таблицы, ASCII-деревья, box-drawing) — дефолтный режим: "
            "любое перечисление 4+ пунктов → таблица/дерево. Stop hook pseudo-check.py блокирует нарушения."
        ]},
        {"tag": "p", "children": [
            {"tag": "b", "children": ["github_ops.md"]},
            " — весь GitHub через PowerShell + Invoke-RestMethod. Ни одного gh CLI. "
            "Создание репо, релизы, загрузка ассетов, кириллица через \\uXXXX."
        ]},
        {"tag": "p", "children": [
            {"tag": "b", "children": ["lessons_universal.md"]},
            " — накопленные ловушки из практики: PS ConvertTo-Json двойное экранирование, "
            "csc.exe C# 5 ограничения, Telegram Bot API лимиты, GitHub upload endpoint."
        ]},
        {"tag": "p", "children": [
            {"tag": "b", "children": ["vibe_coding.md"]},
            " — концепция: говоришь на человеческом языке что хочешь увидеть, "
            "Claude находит нужные параметры и меняет, ты смотришь результат. "
            "Шаблон-заготовка для любого проекта с настраиваемым выходом."
        ]},
        {"tag": "p", "children": [
            {"tag": "b", "children": ["haiku-economy.md"]},
            " — ультимативный пак экономии токенов. Таблица задач Haiku vs Sonnet, "
            "советы для веб-разработки (разбивка html/css/js экономит токены в 5×), "
            "паттерны кэширования для Telegram-ботов, prompt caching для Claude API. "
            "Плюс SOS-пак когда токены кончаются: /compact-smart → субагент → .claudeignore → Haiku."
        ]},
        {"tag": "p", "children": [
            {"tag": "b", "children": ["subagent-context.md"]},
            " — правила передачи контекста субагентам. Дефолт: субагент работает автономно, "
            "контекст не передаётся. Передавать только когда задача требует знания текущего состояния. "
            "После выполнения — только summary в main context, verbose output остаётся в субагенте."
        ]},
        {"tag": "p", "children": [
            {"tag": "b", "children": ["bilingual.md"]},
            " — двуязычность GitHub репозиториев. HTML ",
            {"tag": "code", "children": ["<details>"]},
            " секции с EN/RU версиями README (RU открыта по умолчанию). "
            "Description репо всегда на английском для лучшей индексации."
        ]},
    ]

    # ═══ СЕКЦИЯ: agents/ ═════════════════════════════════════════════════
    agents = [
        {"tag": "h3", "children": ["agents/ — кастомные субагенты"]},
        {"tag": "p", "children": [
            "Субагенты живут в ", {"tag": "code", "children": ["~/.claude/agents/"]},
            " (глобально) или в ", {"tag": "code", "children": [".claude/agents/"]},
            " (проектно). Каждый — md-файл с YAML-шапкой: модель, инструменты, системный промпт."
        ]},
        {"tag": "pre", "children": [
            "~/.claude/agents/\n"
            "├── codebase-explorer.md\n"
            "│     model:  claude-haiku\n"
            "│     tools:  Read, Glob, Grep, LS, Bash(read-only)\n"
            "│     когда:  найти/перечислить/проанализировать — без правок\n"
            "│     пометка: [→ Haiku] перед делегированием\n"
            "├── code-reviewer.md\n"
            "│     model:  claude-haiku\n"
            "│     tools:  Read, Glob, Grep\n"
            "│     output: 🔴 КРИТИЧНО / 🟡 ВНИМАНИЕ / 🟢 МЕЛОЧЬ\n"
            "└── shader-expert.md\n"
            "      model:  claude-haiku\n"
            "      tools:  Read, Glob, Grep\n"
            "      знает:  ps_3_0 бюджет, детектор, что нельзя трогать\n"
            "      output: Диагноз / Причина / Риск для детектора"
        ]},
        {"tag": "p", "children": [
            "Субагент изолирован — работает в отдельном контексте, не засоряет main context. "
            "Haiku дешевле Sonnet в 10–20 раз. Скилл ",
            {"tag": "code", "children": ["haiku-router"]},
            " описывает маппинг задача → агент: поиск/анализ/аудит → Haiku, правки/архитектура → Sonnet. "
            "Контекст субагенту — только когда задача требует знания текущего состояния. "
            "По умолчанию субагент автономен. Правило: ", {"tag": "code", "children": ["subagent-context.md"]}, "."
        ]},
    ]

    # ═══ СЕКЦИЯ: skills/ ═════════════════════════════════════════════════
    skills = [
        {"tag": "h3", "children": ["skills/ — пользовательские команды"]},
        {"tag": "p", "children": [
            "Скиллы — slash-команды и фоновые знания. Живут в ",
            {"tag": "code", "children": ["~/.claude/skills/<name>/SKILL.md"]},
            ". Вызывать командой ",
            {"tag": "code", "children": ["/skill-name"]},
            " или Claude подгружает автоматически когда тема релевантна."
        ]},
        {"tag": "pre", "children": [
            "Action-скиллы (вызывать явно /командой):\n"
            "  /review    [hooks|rules|...]  анализ сессии → хуки/правила/скиллы/память/плагины\n"
            "  /patchnote [vX.X.X]          написать патчнот по workflow_universal.md формату\n"
            "  /gh-setup  [owner/repo]      оформить репо по чеклисту github_formatting.md\n"
            "  /vibe      [описание]        вайбкодинг — изменить параметры по желаемому результату\n"
            "  /sync                        обновить Telegraph + GitHub + Telegram одной командой\n"
            "  /lessons                     таблица всех уроков PS/C#/TG/GH из практики\n"
            "  /hooks-status               аудит: какие правила захукированы, какие нет\n"
            "  /telegraph-post [URL]        создать или обновить Telegraph статью\n"
            "  /new-rule  [название]        создать правило с хуком и скиллом\n"
            "  /learn     [описание]        зафиксировать паттерн из сессии\n"
            "  /compact-smart               умный compact: summary → инструкции → сжатие\n"
            "\n"
            "Knowledge-скиллы (Claude подгружает сам когда задача подходит):\n"
            "  haiku-router     маппинг задача → Haiku-агент, правило пометки [→ Haiku]\n"
            "  ps-cookbook      PowerShell: PS-1/PS-2/PS-3 ловушки, upload endpoint\n"
            "  csharp-cookbook  C# 5: expression-bodied, auto-init, $\"\", nameof — что не работает\n"
            "  gh-ops-ref       GitHub API: релизы, ассеты, topics, кириллица через \\uXXXX\n"
            "  tg-ref           Telegram: лимиты, sendPhoto vs sendMessage, parse_mode\n"
            "  lessons          таблица всех уроков из lessons_universal.md\n"
            "  hooks-status     аудит покрытия правил хуками — какие захукированы, какие нет\n"
            "  vibe             вайбкодинг: промпт → параметры → деплой → смотришь"
        ]},
        {"tag": "hr"},
    ]

    # ═══ СЕКЦИЯ: /review (система самообучения) ══════════════════════════
    review = [
        {"tag": "h3", "children": ["/review — система самообучения"]},
        {"tag": "p", "children": [
            "Ключевая фича — система которая следит за паттернами и предлагает улучшения."
        ]},
        {"tag": "pre", "children": [
            "По ходу сессии (PostToolUse, пассивно):\n"
            "  session-pattern-logger.py → ловит повторяющиеся Edit, Bash-команды,\n"
            "                              новые файлы → пишет в SESSION_PATTERNS.md\n"
            "\n"
            "По запросу /review (активно):\n"
            "  читает SESSION_PATTERNS.md + SESSION.md + текущий диалог\n"
            "  формирует таблицу предложений по 5 категориям:\n"
            "    [ХУК]    — Claude ошибался 2+ раз → Stop hook\n"
            "    [ПРАВИЛО] — новые соглашения из диалога → rules/*.md\n"
            "    [СКИЛЛ]  — команда 3+ раз → новый /скилл\n"
            "    [ПАМЯТЬ]  — предпочтения Потапа → MEMORY.md\n"
            "    [ПЛАГИН]  — чего не хватало → рекомендация MCP\n"
            "  → мультиселект: выбираешь что применять\n"
            "  → рекомендует: глобально (~/.claude/) или локально (.claude/)\n"
            "  → применяет выбранное и напоминает запустить /sync"
        ]},
    ]

    # ═══ СЕКЦИЯ: проектный CLAUDE.md ════════════════════════════════════
    project_claude = [
        {"tag": "h3", "children": ["Проектный CLAUDE.md — контекст репо"]},
        {"tag": "p", "children": [
            "Помимо глобального, в каждом репозитории есть свой CLAUDE.md. "
            "Добавляет специфику: архитектуру, активные файлы, что нельзя трогать, команды деплоя."
        ]},
        {"tag": "pre", "children": [
            "Типичное содержимое:\n"
            "  ├── что за проект (1-2 строки)\n"
            "  ├── активный файл / точка входа\n"
            "  ├── критические правила (что ЗАПРЕЩЕНО)\n"
            "  ├── команда деплоя одной строкой\n"
            "  ├── команды отката (prev / backup)\n"
            "  └── метафоры проекта"
        ]},
        {"tag": "p", "children": [
            "Дополнительно — проектные правила в ", {"tag": "code", "children": [".claude/rules/"]},
            ": тот же принцип что глобальные модули, только специфика одного репо. "
            "Плюс проектные hookify-правила поверх глобальных."
        ]},
    ]

    # ═══ СЕКЦИЯ: инфраструктура (GitHub + Telegraph) ═════════════════════
    infra = [
        {"tag": "h3", "children": ["GitHub + Telegraph — инфраструктура автообновления"]},
        {"tag": "p", "children": [
            "Вся система лежит на GitHub и синхронизируется через /sync — после накопления изменений или по явному запросу:"
        ]},
        {"tag": "p", "children": [{"tag": "a",
            "href": "https://github.com/elementalmasterpotap/potap-claude-setup",
            "children": ["github.com/elementalmasterpotap/potap-claude-setup"]
        }]},
        {"tag": "pre", "children": [
            "claude-setup/\n"
            "├── CLAUDE.md                  глобальный алгоритм сессии\n"
            "├── update_telegraph.py        механика: Telegraph API, GitHub sync, Telegram\n"
            "├── telegraph_content.py       контент лонгрида по секциям (только данные)\n"
            "├── rules/                     14 модульных md-файлов\n"
            "├── agents/                    субагенты: code-reviewer, codebase-explorer, shader-expert\n"
            "├── scripts/                   хуки: 2 UPS + 1 PreToolUse + 14 Stop + 3 PostToolUse + 1 PreCompact\n"
            "├── skills/                    11 action + 8 knowledge (детали в секции skills/)\n"
            "└── templates/\n"
            "    ├── CLAUDE_BASE.md  MEMORY_TEMPLATE.md  и др.\n"
            "    └── hookify/        6 шаблонов хуков"
        ]},
        {"tag": "p", "children": [
            "Telegraph нужен для длинных публикаций с форматированием — "
            "Telegram Bot API обрезает на 4096 символах, Telegraph нет. "
            "Команда ", {"tag": "code", "children": ["/sync"]}, " запускает update_telegraph.py и делает три вещи:"
        ]},
        {"tag": "pre", "children": [
            "/sync  →  python3 ~/.claude/update_telegraph.py\n"
            "  ├── editPage    → Telegraph (контент + дата обновления)\n"
            "  ├── git push    → GitHub potap-claude-setup (rules/, CLAUDE.md, scripts/, skills/, agents/)\n"
            "  └── editMessage → Telegram-пост в @potap_attic (рефетч превью + дата)\n"
            "\n"
            "Фильтр перед push: убирает auth-ссылки telegraph.md, проверяет нет ли токенов в файлах."
        ]},
    ]

    # ═══ СЕКЦИЯ: итоговая таблица ════════════════════════════════════════
    summary = [
        {"tag": "pre", "children": [
            "Компонент          Файл/Скилл               Что делает\n"
            "───────────────────────────────────────────────────────\n"
            "Фундамент          settings.json            deny, MCP, хуки, env-токены\n"
            "Алгоритм           CLAUDE.md                маршрутизатор + принципы\n"
            "Память             memory/MEMORY.md         паттерны между сессиями\n"
            "Самообучение       /review                  сессия → хуки/правила/скиллы\n"
            "Haiku (авто)       haiku-suggest.py         scoring → [HAIKU_ELIGIBLE]\n"
            "Субагенты (3)      agents/*.md              Haiku: explore·review·shader\n"
            "Stop хуки (14)    scripts/*-check.py       псевдо·коммит·тон·PS·C#·TG·GH\n"
            "Безопасность       deny + token-leak        кредсы и секреты заблокированы\n"
            "Context            .claudeignore            −30–80K токенов на node_modules\n"
            "Skills action(11)  /sync /review /patchnote /learn /gh-setup + ещё 6\n"
            "Skills know (8)    haiku-router tg-ref ps-cookbook csharp gh-ops + ещё 4\n"
            "Rules (14 файлов)  rules/*.md               comm·workflow·github·TG·PS·C#·\n"
            "                                            haiku·subagent·bilingual·hlsl\n"
            "Sync               /sync                    Telegraph + GitHub + Telegram\n"
            "Проект             .claude/CLAUDE.md        специфика репо"
        ]},
        {"tag": "p", "children": [
            "Всё это — не разовая настройка. Живая система: каждая сессия дополняет правила, "
            "каждая поломка уходит в ", {"tag": "code", "children": ["lessons.md"]},
            ", каждый паттерн — в MEMORY.md. /review автоматически предлагает следующий шаг."
        ]},
    ]

    # ═══ СЕКЦИЯ: оптимизация токенов ════════════════════════════════════
    haiku_opt = [
        {"tag": "h3", "children": ["Оптимизация токенов — ультимативный пак"]},
        {"tag": "p", "children": [
            "Система заточена под Pro тариф (rolling 5h окно, ~44K токенов). "
            "Несколько слоёв экономии работают автоматически, остальные — по запросу."
        ]},
        {"tag": "pre", "children": [
            "Автоматически (хуки):\n"
            "  haiku-suggest.py    → complexity scoring → [HAIKU_ELIGIBLE] → Haiku субагент\n"
            "  bash-output-check   → warn если >3K символов вывода в main context\n"
            "  heavy-files-check   → warn lock-файл / node_modules без .claudeignore\n"
            "  session-length-check → hint /compact при длинной сессии\n"
            "  precompact-smart    → LLM summary через Haiku перед сжатием\n"
            "\n"
            "По запросу (SOS когда токены кончаются):\n"
            "  /compact-smart  → сжать с сохранением изменённых файлов и задач\n"
            "  /clear          → полный сброс если задача сменилась\n"
            "  /mcp            → отключить Linear и другие неиспользуемые серверы\n"
            "  Alt+T           → отключить thinking для простых задач\n"
            "\n"
            "Структурная экономия (build once):\n"
            "  .claudeignore   → node_modules/lock/dist = −30-80K токенов\n"
            "  Haiku субагенты → 10-20x дешевле для поиска/анализа\n"
            "  skills lazy-load → 82% vs все правила в CLAUDE.md\n"
            "  context-mode    → verbose ops в sandbox, main context чист"
        ]},
        {"tag": "pre", "children": [
            "Haiku vs Sonnet — таблица задач:\n"
            "  Найти файл / grep по коду          → Haiku  (~70% дешевле)\n"
            "  Прочитать и суммаризировать файл   → Haiku\n"
            "  Code review (поверхностный)        → Haiku\n"
            "  Написать новую фичу                → Sonnet\n"
            "  Архитектурное решение              → Sonnet (с thinking)\n"
            "  Multi-file рефакторинг             → Sonnet\n"
            "\n"
            "Советы для веб-разработки:\n"
            "  index.html + css/style.css + js/main.js  вместо монолита\n"
            "  При правке CSS — читается только style.css (~400 строк)\n"
            "  vs монолит — читается всё (~2000 строк) → 5× токенов лишних\n"
            "\n"
            "Prompt caching (Claude API):\n"
            "  cache_control: ephemeral  → кэш 5 минут → -90% при повторе\n"
            "  Применять к: RAG документы, few-shot примеры, системные правила"
        ]},
        {"tag": "hr"},
    ]

    # ── Сборка ───────────────────────────────────────────────────────────
    return (
        header
        + toc
        + settings
        + claude_md
        + memory_md
        + hookify
        + rules
        + agents
        + skills
        + review
        + project_claude
        + haiku_opt
        + infra
        + summary
    )
