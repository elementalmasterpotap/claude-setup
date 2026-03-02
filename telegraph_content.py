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
            "Лонгрид обновляется автоматически — каждый раз когда я добавляю или убираю кастомизацию, "
            "Claude редактирует эту страницу. То что здесь написано = актуальное состояние системы."
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
            "├─ rules/ ────────────── 8 модульных md-правил\n"
            "├─ agents/ ───────────── кастомные субагенты\n"
            "├─ skills/ ───────────── 10 action + 5 knowledge скиллов\n"
            "├─ /review ───────────── система самообучения\n"
            "├─ Проектный CLAUDE.md ─ контекст репо\n"
            "└─ GitHub + Telegraph ── инфраструктура автообновления"
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
            "    └── Stop         → 13 хуков (псевдографика/тон/токены/коммит/деплой/...)"
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
            "UserPromptSubmit (1 хук на каждое сообщение):\n"
            "  haiku-suggest.py      → complexity scoring: h_score/s_score → inject [HAIKU_ELIGIBLE]\n"
            "                          если задача read-only (найти/перечислить/структура) — Haiku\n"
            "\n"
            "PreCompact (1 хук перед авто-сжатием):\n"
            "  precompact-smart.py   → сырой .jsonl + LLM summary через Haiku (30 exchanges)\n"
            "                          авто-fallback на text-extraction если claude CLI недоступен\n"
            "\n"
            "PreToolUse (1 хук на каждый вызов инструмента):\n"
            "  pretool-safety.py     → --no-verify, reset --hard, push -f main, rm -rf, logo/assets\n"
            "\n"
            "PostToolUse (3 хука после каждого Edit/Write/Bash):\n"
            "  posttool-skills-sync.py    → напоминание о /sync если изменены skills/\n"
            "  checkpoint.py              → лог изменённых файлов в SESSION.md\n"
            "  session-pattern-logger.py  → паттерны для /review (repeated-edit, repeated-command)\n"
            "\n"
            "Stop (12 проверок каждого ответа):\n"
            "  anti-ration.py        → отмазки «за рамками», «нужно контекст», «баг до меня»\n"
            "  pseudo-check.py       → 4+ пунктов без псевдографики\n"
            "  commit-check.py       → коммит без type(scope): + Co-Authored Claude + Happy\n"
            "  token-leak-check.py   → реальный ghp_ / TG / Telegraph токен в тексте\n"
            "  tone-check.py         → канцелярит и ассистент-подобострастие\n"
            "  deploy-check.py       → деплой-команда без -NoPrompt / --yes\n"
            "  ps-unicode-check.py   → PowerShell JSON + кириллица в двойных кавычках\n"
            "  patchnote-check.py    → патчнот без tagline / не от первого лица\n"
            "  csharp-compat-check.py → C# 6+ синтаксис в csc.exe .NET 4.x контексте\n"
            "  github-upload-check.py → api.github.com вместо uploads.github.com для ассетов\n"
            "  telegraph-edit-check.py → createPage лонгрида / curl + кириллица в Telegraph\n"
            "  session-stop.py       → сохранение контекста сессии при разрыве соединения\n"
            "  heavy-files-check.py  → warn: node_modules/lock-файл без .claudeignore"
        ]},
        {"tag": "p", "children": [
            "Токены в ", {"tag": "code", "children": ["env"]},
            " — Claude видит их как переменные окружения в любом проекте."
        ]},
        {"tag": "hr"},
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
        {"tag": "hr"},
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
        {"tag": "hr"},
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
        {"tag": "hr"},
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
            "└── lessons_universal.md     ловушки: PS / C# / Telegram / GitHub"
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
        {"tag": "hr"},
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
            " описывает маппинг задача → агент: поиск/анализ/аудит → Haiku, правки/архитектура → Sonnet."
        ]},
        {"tag": "hr"},
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
            "\n"
            "Knowledge-скиллы (Claude подгружает сам когда задача подходит):\n"
            "  haiku-router     маппинг задача → Haiku-агент, правило пометки [→ Haiku]\n"
            "  ps-cookbook      PowerShell: PS-1/PS-2/PS-3 ловушки, upload endpoint\n"
            "  csharp-cookbook  C# 5: expression-bodied, auto-init, $\"\", nameof — что не работает\n"
            "  gh-ops-ref       GitHub API: релизы, ассеты, topics, кириллица через \\uXXXX\n"
            "  tg-ref           Telegram: лимиты, sendPhoto vs sendMessage, parse_mode\n"
            "  lessons          таблица всех уроков из lessons_universal.md"
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
            "  → применяет выбранное и запускает update_telegraph.py"
        ]},
        {"tag": "hr"},
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
        {"tag": "hr"},
    ]

    # ═══ СЕКЦИЯ: инфраструктура (GitHub + Telegraph) ═════════════════════
    infra = [
        {"tag": "h3", "children": ["GitHub + Telegraph — инфраструктура автообновления"]},
        {"tag": "p", "children": [
            "Вся система лежит на GitHub и обновляется автоматически при каждом изменении кастомизаций:"
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
            "├── rules/                     8 модульных md-файлов\n"
            "├── agents/                    субагенты: code-reviewer, shader-expert\n"
            "├── scripts/                   хуки: 1 UPS + 1 PreToolUse + 13 Stop + 3 PostToolUse + 1 PreCompact\n"
            "├── skills/                    10 action + 5 knowledge скиллов\n"
            "│   ├── /review                система самообучения — анализ сессии\n"
            "│   ├── /patchnote             написать патчнот по формату\n"
            "│   ├── /gh-setup              оформить репо по чеклисту\n"
            "│   ├── /vibe                  вайбкодинг по описанию\n"
            "│   ├── /sync                  синхронизировать кастомизации\n"
            "│   ├── /lessons               таблица всех уроков из практики\n"
            "│   ├── /hooks-status          аудит хуков vs правила\n"
            "│   ├── /telegraph-post        создать/обновить Telegraph статью\n"
            "│   ├── /new-rule, /learn      создать/зафиксировать правило\n"
            "│   ├── ps-cookbook            [авто] PowerShell паттерны\n"
            "│   ├── csharp-cookbook        [авто] C# 5 паттерны и ограничения\n"
            "│   ├── gh-ops-ref             [авто] GitHub API через PS\n"
            "│   ├── tg-ref                 [авто] Telegram Bot API\n"
            "│   └── lessons                [авто] таблица уроков из практики\n"
            "└── templates/\n"
            "    ├── CLAUDE_BASE.md  MEMORY_TEMPLATE.md  и др.\n"
            "    └── hookify/        6 шаблонов хуков"
        ]},
        {"tag": "p", "children": [
            "Telegraph нужен для длинных публикаций с форматированием — "
            "Telegram Bot API обрезает на 4096 символах, Telegraph нет. "
            "Один запуск ", {"tag": "code", "children": ["update_telegraph.py"]}, " делает три вещи:"
        ]},
        {"tag": "pre", "children": [
            "python3 ~/.claude/update_telegraph.py\n"
            "  ├── editPage    → Telegraph (контент + дата)\n"
            "  ├── git push    → GitHub (rules/, CLAUDE.md, scripts/, skills/, agents/)\n"
            "  └── editMessage → Telegram-пост (рефетч превью + дата)"
        ]},
        {"tag": "hr"},
    ]

    # ═══ СЕКЦИЯ: итоговая таблица ════════════════════════════════════════
    summary = [
        {"tag": "h3", "children": ["Итог — компоненты системы"]},
        {"tag": "pre", "children": [
            "Компонент             Файл                         Что делает\n"
            "──────────────────────────────────────────────────────────────────\n"
            "Фундамент             settings.json                разрешения, deny, MCP, хуки\n"
            "Мозг сессии           ~/.claude/CLAUDE.md          алгоритм, принципы, маршрутизатор\n"
            "Память                memory/MEMORY.md             факты между сессиями\n"
            "Самообучение          /review + pattern-logger     паттерны → хуки/правила/скиллы\n"
            "Haiku-анализатор      haiku-suggest.py (UPS)       scoring → [HAIKU_ELIGIBLE] + suppress thinking\n"
            "Haiku-роутер          skills/haiku-router          маппинг задач на дешёвые субагенты\n"
            "Исследование кода     codebase-explorer.md         haiku, поиск/анализ без правок\n"
            "Ревью кода            code-reviewer.md             haiku, только чтение, быстро\n"
            "HLSL диагностика      shader-expert.md             анализ шейдера, детектор, бюджет\n"
            "Безопасность          deny rules + Stop hook       кредсы недоступны, отмазки блокируются\n"
            "Псевдографика         pseudo-check.py              блок 4+ пунктов без псевдографики\n"
            "Коммит-формат         commit-check.py              type(scope) + Co-Authored обязательны\n"
            "Токены в ответе       token-leak-check.py          блок реальных секретов в тексте\n"
            "Тон общения           tone-check.py                блок канцелярита и подобострастия\n"
            "Деплой флаги          deploy-check.py              warn без -NoPrompt / --yes\n"
            "PS Unicode            ps-unicode-check.py          блок JSON + кириллица в двойных кавычках\n"
        ]},
        {"tag": "pre", "children": [
            "Компонент             Файл                         Что делает\n"
            "──────────────────────────────────────────────────────────────────\n"
            "Патчнот формат        patchnote-check.py           tagline + первое лицо обязательны\n"
            "C# 5 совместимость    csharp-compat-check.py       warn C# 6+ синтаксис в .NET 4.x\n"
            "GitHub upload         github-upload-check.py       warn api.github вместо uploads\n"
            "Telegraph editPage    telegraph-edit-check.py      блок createPage / curl + кириллица\n"
            "Сохранение сессии     session-stop.py              контекст при разрыве соединения\n"
            "Тяжёлые файлы         heavy-files-check.py         warn lock-файл без .claudeignore\n"
            "Умный бэкап           precompact-smart.py          jsonl + LLM summary перед compaction\n"
            "Чекпоинт              checkpoint.py                лог изменённых файлов в SESSION.md\n"
            "Логгер паттернов      session-pattern-logger.py    пишет кандидатов для /review\n"
            "PreToolUse safety     pretool-safety.py            --no-verify/reset--hard/rm-rf/logo\n"
            "Живая документация    mcpServers.context7          актуальные API без галлюцинаций\n"
            "Compact реинжект      hooks.SessionStart[compact]  критические правила после сжатия\n"
            "Pre-compact бэкап     hooks.PreCompact             jsonl + LLM summary до сжатия\n"
            "Context isolation     ~/.claude/.claudeignore       node_modules/lock = −30–80K токенов\n"
            "Task gate             hooks.TaskCompleted          блок 'готово' без коммита\n"
            "Статусбар             statusLine + statusline.sh   git ветка + diff в нижней строке\n"
            "Enforcement           hookify.*.local.md           block/warn хуки\n"
            "Skills action (10)    skills/review,patchnote,...  /команды для workflow\n"
            "Skills knowledge (5)  skills/haiku-router,tg-ref   авто-подгрузка справки\n"
            "Стиль / тон           rules/communication.md       как разговаривать\n"
            "GitHub API            rules/github_ops.md          Invoke-RestMethod без gh CLI\n"
            "Вайбкодинг            rules/vibe_coding.md         человеческий язык → параметры\n"
            "Ловушки               rules/lessons_universal.md   PS / C# / TG / GH антипаттерны\n"
            "Проектный контекст    .claude/CLAUDE.md            специфика репо"
        ]},
        {"tag": "p", "children": [
            "Всё это — не разовая настройка. Живая система: каждая сессия дополняет правила, "
            "каждая поломка уходит в ", {"tag": "code", "children": ["lessons.md"]},
            ", каждый паттерн — в MEMORY.md. /review автоматически предлагает следующий шаг."
        ]},
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
        + infra
        + summary
    )
