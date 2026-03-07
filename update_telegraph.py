"""
Обновление лонгрида про кастомизации Claude + GitHub sync + Telegram refresh.

КОНТЕНТ: telegraph_content.py → get_content(ts)  ← редактировать только его
МЕХАНИКА: этот файл                               ← редактировать только для API/логики

Путь лонгрида: Kak-ya-kastomiziruyu-Claude--pravila-pamyat-i-moduli-03-07
"""
import urllib.request, json, os, sys, subprocess, shutil, re
from datetime import datetime, timezone, timedelta

# ── Импорт контента ───────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from telegraph_content import get_content

TOKEN = os.environ.get("TELEGRAPH_TOKEN")
if not TOKEN:
    print("Error: TELEGRAPH_TOKEN not set", file=sys.stderr); sys.exit(1)

PATH    = "Kak-ya-kastomiziruyu-Claude--pravila-pamyat-i-moduli-03-07"
_CLAUDE = os.path.expanduser("~/.claude")
REPO    = os.path.join(_CLAUDE, "claude-setup")

tz_msk = timezone(timedelta(hours=3))
now    = datetime.now(tz_msk)
ts     = now.strftime("%d.%m.%Y %H:%M МСК")

# ── Telegraph editPage ────────────────────────────────────────────────────────
data = json.dumps({
    "access_token": TOKEN,
    "path": PATH,
    "title": "Как я кастомизирую Claude: правила, память и модули",
    "author_name": "Potap",
    "author_url": "https://t.me/potap_attic",
    "content": get_content(ts),
    "return_content": False
}).encode("utf-8")

req = urllib.request.Request(
    "https://api.telegra.ph/editPage/" + PATH,
    data=data,
    headers={"Content-Type": "application/json"}
)
result = json.loads(urllib.request.urlopen(req).read())
print(result["result"]["url"])

# ── GitHub sync ───────────────────────────────────────────────────────────────
def _copy_dir(src, dst, *, file_filter=None):
    """Рекурсивно копирует директорию src → dst.
    file_filter(filename) → (content | None): если None — пропустить/не писать.
    """
    os.makedirs(dst, exist_ok=True)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            _copy_dir(s, d, file_filter=file_filter)
        elif os.path.isfile(s):
            if file_filter:
                content = file_filter(item, s)
                if content is not None:
                    open(d, "w", encoding="utf-8").write(content)
            else:
                shutil.copy(s, d)


def _rules_filter(filename, filepath):
    """Фильтр для rules/: из telegraph.md убирает Auth-ссылку и хардкод токена."""
    text = open(filepath, encoding="utf-8").read()
    if filename == "telegraph.md":
        text = re.sub(r'.*Auth \(войти в браузере\).*\n', '', text)
        text = re.sub(r'TOKEN = "[^"]{10,}"', 'TOKEN = os.environ["TELEGRAPH_TOKEN"]', text)
    return text


def _sync_github():
    # Директории с простым рекурсивным копированием
    for dirname in ("agents", "skills", "scripts", "templates"):
        src = os.path.join(_CLAUDE, dirname)
        dst = os.path.join(REPO, dirname)
        if os.path.isdir(src):
            _copy_dir(src, dst)

    # rules/ — с фильтрацией секретов
    _copy_dir(
        os.path.join(_CLAUDE, "rules"),
        os.path.join(REPO, "rules"),
        file_filter=_rules_filter
    )

    # Отдельные файлы верхнего уровня
    for filename in ("CLAUDE.md", "update_telegraph.py", "telegraph_content.py"):
        src = os.path.join(_CLAUDE, filename)
        if os.path.isfile(src):
            shutil.copy(src, os.path.join(REPO, filename))

    # Pre-push аудит токенов
    _TOKEN_RE = re.compile(
        r'ghp_[A-Za-z0-9]{36}'
        r'|[0-9]{10}:AA[A-Za-z0-9_\-]{33}'
        r'|475c06[a-f0-9]{50}'
    )
    leaks = []
    for root, _, fnames in os.walk(REPO):
        if ".git" in root:
            continue
        for fn in fnames:
            path = os.path.join(root, fn)
            try:
                text = open(path, encoding="utf-8", errors="ignore").read()
                for m in _TOKEN_RE.finditer(text):
                    leaks.append(f"{path}: {m.group()[:12]}...")
            except Exception:
                pass
    if leaks:
        raise RuntimeError("⛔ SECRET LEAK — git push отменён:\n" + "\n".join(leaks))

    # Git commit + push
    token = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN", "")
    repo_url = f"https://{token}@github.com/elementalmasterpotap/potap-claude-setup.git"
    clean_url = "https://github.com/elementalmasterpotap/potap-claude-setup.git"

    subprocess.run(["git", "-C", REPO, "remote", "set-url", "origin", repo_url], capture_output=True)
    subprocess.run(["git", "-C", REPO, "add", "."], capture_output=True)
    diff = subprocess.run(["git", "-C", REPO, "diff", "--cached", "--quiet"])
    if diff.returncode != 0:
        subprocess.run(["git", "-C", REPO, "commit", "-m", f"chore: sync — {ts}"], capture_output=True, check=True)
        subprocess.run(["git", "-C", REPO, "push"], capture_output=True, check=True)
        print(f"GitHub synced ({ts})")
    else:
        print("GitHub: no changes")
    subprocess.run(["git", "-C", REPO, "remote", "set-url", "origin", clean_url], capture_output=True)


try:
    _sync_github()
except Exception as e:
    print(f"GitHub sync failed: {e}", file=sys.stderr)

# ── Telegram preview refresh ──────────────────────────────────────────────────
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
