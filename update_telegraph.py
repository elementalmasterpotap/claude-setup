"""
Обновление лонгрида про кастомизации Claude.
Единственный файл — всегда editPage, не пересоздавать.
Путь: Kak-ya-kastomiziruyu-Claude-pravila-pamyat-i-moduli-03-01
"""
import urllib.request, json, os, sys, subprocess, shutil, re
from datetime import datetime, timezone, timedelta

TOKEN = os.environ.get("TELEGRAPH_TOKEN")
if not TOKEN:
    print("Error: TELEGRAPH_TOKEN not set", file=sys.stderr); sys.exit(1)

PATH = "Kak-ya-kastomiziruyu-Claude-pravila-pamyat-i-moduli-03-01"
_CLAUDE = os.path.join(os.path.expanduser("~"), ".claude")
REPO    = os.path.join(_CLAUDE, "claude-setup")

tz_msk = timezone(timedelta(hours=3))   # Воронеж = МСК = UTC+3
now    = datetime.now(tz_msk)
ts     = now.strftime("%d.%m.%Y %H:%M МСК")

content = [
    # ── Дата обновления ──────────────────────────────────────────
    {"tag": "p", "children": [{"tag": "i", "children": [f"Обновлено: {ts}"]}]},

    # ── Предисловие ──────────────────────────────────────────────
    {"tag": "p", "children": [{"tag": "i", "children": [
        "Лонгрид обновляется автоматически — каждый раз когда я добавляю или убираю кастомизацию, "
        "Claude редактирует эту страницу. То что здесь написано = актуальное состояние системы."
    ]}]},
    {"tag": "p", "children": [
        "Накопил приличный стек правил, памяти и плагинов для Claude Code. "
        "Разбираю как всё это устроено — только механика, без воды."
    ]},

    # ── Оглавление ───────────────────────────────────────────────
    {"tag": "pre", "children": [
        "├─ settings.json ─────── фундамент, разрешения, токены\n"
        "├─ CLAUDE.md ─────────── алгоритм сессии, маршрутизатор\n"
        "├─ MEMORY.md ─────────── долговременная память\n"
        "├─ hookify ───────────── block/warn хуки\n"
        "├─ rules/ ────────────── 8 модульных md-правил\n"
        "├─ Проектный CLAUDE.md ─ контекст репо\n"
        "└─ GitHub + Telegraph ── инфраструктура автообновления"
    ]},
    {"tag": "hr"},

    # ── 1. settings.json ─────────────────────────────────────────
    {"tag": "h3", "children": ["settings.json — фундамент"]},
    {"tag": "p", "children": [
        "Глобальный конфиг Claude Code. Живёт в ", {"tag": "code", "children": ["~/.claude/settings.json"]},
        ". Определяет что Claude может делать без запроса и что у него подключено."
    ]},
    {"tag": "pre", "children": [
        "settings.json\n"
        "├── permissions\n"
        "│   ├── allow       → [Bash(*), Edit(*), Write(*), Read(*), WebSearch, WebFetch(*)]\n"
        "│   └── defaultMode → dontAsk  (работает автономно, не спрашивает каждый раз)\n"
        "├── enabledPlugins  → [commit-commands, claude-md-management, hookify, github]\n"
        "├── env             → {GITHUB_TOKEN, TELEGRAPH_TOKEN, TELEGRAM_BOT_TOKEN}\n"
        "└── language        → Russian"
    ]},
    {"tag": "p", "children": [
        {"tag": "b", "children": ["Главное"]}, " — ",
        {"tag": "code", "children": ["defaultMode: dontAsk"]},
        ". Claude не просит разрешения на каждый вызов инструмента. "
        "Работает сам, только для критичных необратимых действий уточняет."
    ]},
    {"tag": "p", "children": [
        "Токены в ", {"tag": "code", "children": ["env"]},
        " — Claude видит их как переменные окружения в любом проекте. "
        "Не нужно вставлять в каждый скрипт вручную."
    ]},
    {"tag": "hr"},

    # ── 2. CLAUDE.md глобальный ───────────────────────────────────
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
        "  добавлена/удалена кастомизация?    → ~/.claude/update_telegraph.py\n"
        "  новое правило?                     → карта владения → проверить дубли\n"
        "  изменён CLAUDE/MEMORY?             → синхронизировать копии\n"
        "  готово?                            → доказать что работает"
    ]},
    {"tag": "p", "children": [
        "Ещё там: принципы (минимальный импакт, root cause не симптом, не хакать), "
        "правила коммитов, аудит правил, карта владения — что в каком файле хранится."
    ]},
    {"tag": "hr"},

    # ── 3. MEMORY.md ──────────────────────────────────────────────
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

    # ── 4. hookify ────────────────────────────────────────────────
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

    # ── 5. Модульные md-файлы ─────────────────────────────────────
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
        "стиль, тон, отсылки, мемы. Читается первым делом в каждой сессии."
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

    # ── 6. Проектный CLAUDE.md ────────────────────────────────────
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

    # ── 7. GitHub + Telegraph ─────────────────────────────────────
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
        "├── update_telegraph.py        скрипт обновления этого лонгрида\n"
        "├── rules/                     8 модульных md-файлов\n"
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
        "  ├── git push    → GitHub (rules/, CLAUDE.md, templates/)\n"
        "  └── editMessage → Telegram-пост (рефетч превью + дата)"
    ]},
    {"tag": "hr"},

    # ── Итог ─────────────────────────────────────────────────────
    {"tag": "h3", "children": ["Итог — компоненты системы"]},
    {"tag": "pre", "children": [
        "Компонент              Файл                           Что делает\n"
        "────────────────────────────────────────────────────────────────────\n"
        "Фундамент              settings.json                  разрешения, плагины, токены\n"
        "Мозг сессии            ~/.claude/CLAUDE.md            алгоритм, принципы, маршрутизатор\n"
        "Память                 memory/MEMORY.md               факты между сессиями\n"
        "Enforcement            hookify.*.local.md             block/warn хуки\n"
        "Стиль / тон            rules/communication.md         как разговаривать\n"
        "GitHub без gh CLI      rules/github_ops.md            API через PowerShell\n"
        "GitHub оформление      rules/github_formatting.md     README, бейджи, чеклист\n"
        "Telegram посты         rules/lessons_universal.md     TG-лимиты, Bot API\n"
        "Telegraph публикации   rules/telegraph.md             лонгриды, editPage\n"
        "Windows / C# / PS      rules/windows_dev.md           installer, WinForms\n"
        "Вайбкодинг             rules/vibe_coding.md           человеческий язык → параметры\n"
        "Ловушки / антипат.     rules/lessons_universal.md     баги из практики\n"
        "Проектный контекст     .claude/CLAUDE.md              специфика репо"
    ]},
    {"tag": "p", "children": [
        "Всё это — не разовая настройка. Живая система: каждая сессия дополняет правила, "
        "каждая поломка уходит в ", {"tag": "code", "children": ["lessons.md"]},
        ", каждый паттерн — в MEMORY.md."
    ]},
]

data = json.dumps({
    "access_token": TOKEN,
    "path": PATH,
    "title": "Как я кастомизирую Claude: правила, память и модули",
    "author_name": "Potap",
    "author_url": "https://t.me/potap_attic",
    "content": content,
    "return_content": False
}).encode("utf-8")

req = urllib.request.Request(
    "https://api.telegra.ph/editPage/" + PATH,
    data=data,
    headers={"Content-Type": "application/json"}
)
result = json.loads(urllib.request.urlopen(req).read())
print(result["result"]["url"])

# ── GitHub sync ───────────────────────────────────────────────────
def _sync_github():
    rules_src  = os.path.join(_CLAUDE, "rules")
    tpl_src    = os.path.join(_CLAUDE, "templates")
    claude_src = os.path.join(_CLAUDE, "CLAUDE.md")

    shutil.copy(os.path.abspath(__file__), os.path.join(REPO, "update_telegraph.py"))
    shutil.copy(claude_src, os.path.join(REPO, "CLAUDE.md"))

    for f in os.listdir(rules_src):
        src, dst = os.path.join(rules_src, f), os.path.join(REPO, "rules", f)
        if f == "telegraph.md":
            txt = re.sub(r'.*Auth \(войти в браузере\).*\n', '', open(src).read())
            txt = re.sub(r'TOKEN = "[^"]{10,}"', 'TOKEN = os.environ["TELEGRAPH_TOKEN"]', txt)
            open(dst, 'w', encoding='utf-8').write(txt)
        else:
            shutil.copy(src, dst)

    for f in os.listdir(tpl_src):
        p = os.path.join(tpl_src, f)
        if os.path.isfile(p):
            shutil.copy(p, os.path.join(REPO, "templates", f))
    hk = os.path.join(tpl_src, "hookify")
    if os.path.isdir(hk):
        for f in os.listdir(hk):
            shutil.copy(os.path.join(hk, f), os.path.join(REPO, "templates", "hookify", f))

    # ── Pre-push аудит токенов ────────────────────────────────────
    _REAL_TOKEN_RE = re.compile(
        r'ghp_[A-Za-z0-9]{36}'                   # GitHub token
        r'|[0-9]{10}:AA[A-Za-z0-9_\-]{33}'       # Telegram bot token
        r'|475c06[a-f0-9]{50}'                    # Telegraph token
    )
    leaks = []
    for root, _, fnames in os.walk(REPO):
        if ".git" in root:
            continue
        for fn in fnames:
            path = os.path.join(root, fn)
            try:
                text = open(path, encoding="utf-8", errors="ignore").read()
                for m in _REAL_TOKEN_RE.finditer(text):
                    leaks.append(f"{path}: {m.group()[:12]}...")
            except Exception:
                pass
    if leaks:
        raise RuntimeError("⛔ SECRET LEAK DETECTED — git push отменён:\n" + "\n".join(leaks))

    token = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN", "")
    repo_url = f"https://{token}@github.com/elementalmasterpotap/potap-claude-setup.git"
    subprocess.run(["git", "-C", REPO, "remote", "set-url", "origin", repo_url], capture_output=True)
    subprocess.run(["git", "-C", REPO, "add", "."], capture_output=True)
    diff = subprocess.run(["git", "-C", REPO, "diff", "--cached", "--quiet"])
    if diff.returncode != 0:
        subprocess.run(["git", "-C", REPO, "commit", "-m", f"chore: sync — {ts}"], capture_output=True, check=True)
        subprocess.run(["git", "-C", REPO, "push"], capture_output=True, check=True)
        subprocess.run(["git", "-C", REPO, "remote", "set-url", "origin",
                        "https://github.com/elementalmasterpotap/potap-claude-setup.git"], capture_output=True)
        print(f"GitHub synced ({ts})")
    else:
        print("GitHub: no changes")

try:
    _sync_github()
except Exception as e:
    print(f"GitHub sync failed: {e}", file=sys.stderr)

# ── Telegram preview refresh ──────────────────────────────────────
TG_BOT       = os.environ.get("TELEGRAM_BOT_TOKEN")
TG_CHAT      = "@potap_attic"
TG_POST_FILE = os.path.join(_CLAUDE, ".tg_post_id")
LONGREAD_URL = "https://telegra.ph/Kak-ya-kastomiziruyu-Claude-pravila-pamyat-i-moduli-03-01"
TG_TEXT = (
    "🗂 <b>potap-claude-setup — моя настройка Claude Code на GitHub</b>\n\n"
    "Выложил весь стек кастомизаций: правила, шаблоны, hookify-хуки, "
    "скрипт авто-обновления лонгрида.\n\n"
    "Лонгрид, GitHub и этот пост обновляются автоматически — "
    "актуальное состояние системы всегда там.\n\n"
    '<a href="https://github.com/elementalmasterpotap/potap-claude-setup">GitHub →</a>'
    "  ·  "
    f'<a href="{LONGREAD_URL}">Лонгрид →</a>'
    f"\n\n<i>обновлено {ts}</i>"
)

def _tg_api(method, payload):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{TG_BOT}/{method}",
        data=data, headers={"Content-Type": "application/json"}
    )
    return json.loads(urllib.request.urlopen(req).read())

def _refresh_tg_post():
    if not TG_BOT:
        return
    lp = {"url": LONGREAD_URL}
    post_id = open(TG_POST_FILE).read().strip() if os.path.exists(TG_POST_FILE) else None
    if post_id:
        r = _tg_api("editMessageText", {
            "chat_id": TG_CHAT, "message_id": int(post_id),
            "text": TG_TEXT, "parse_mode": "HTML", "link_preview_options": lp
        })
        if r.get("ok"):
            print(f"Telegram preview refreshed (message_id: {post_id})")
            return
    # Пост не найден — отправить новый
    r = _tg_api("sendMessage", {
        "chat_id": TG_CHAT, "text": TG_TEXT,
        "parse_mode": "HTML", "link_preview_options": lp
    })
    if r.get("ok"):
        new_id = str(r["result"]["message_id"])
        open(TG_POST_FILE, "w").write(new_id)
        print(f"Telegram post sent (message_id: {new_id})")

try:
    _refresh_tg_post()
except Exception as e:
    print(f"Telegram refresh failed: {e}", file=sys.stderr)
