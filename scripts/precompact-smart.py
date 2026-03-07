#!/usr/bin/env python3
"""
PreCompact хук: умный бэкап + LLM summary перед сжатием контекста.

Паттерн: mvara-ai/precompact-hook адаптированный.

Делает два файла:
  backups/pre-compact-TIMESTAMP.jsonl  — сырой транскрипт (как раньше)
  backups/pre-compact-TIMESTAMP.md     — структурированное резюме (LLM или auto-extract)

LLM summary: через `claude -p` (Haiku). Если claude недоступен — auto-extract.
"""
import sys, json, os, subprocess, re
from pathlib import Path
from datetime import datetime

BACKUP_DIR = Path.home() / ".claude" / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

# ── Читаем stdin ──────────────────────────────────────────────────────────────
try:
    payload = json.loads(sys.stdin.read())
except Exception:
    sys.exit(0)

transcript_path = payload.get("transcript_path") or payload.get("session_id")
session_id = payload.get("session_id", "unknown")

# ── Найти транскрипт ──────────────────────────────────────────────────────────
def find_transcript():
    if transcript_path and Path(transcript_path).exists():
        return Path(transcript_path)
    # Fallback: самый свежий .jsonl в ~/.claude/projects
    projects_dir = Path.home() / ".claude" / "projects"
    if not projects_dir.exists():
        return None
    files = list(projects_dir.rglob("*.jsonl"))
    if not files:
        return None
    return max(files, key=lambda f: f.stat().st_mtime)

transcript = find_transcript()
if not transcript:
    sys.exit(0)

ts = datetime.now().strftime("%Y%m%d_%H%M%S")

# ── Бэкап сырого транскрипта ──────────────────────────────────────────────────
raw_backup = BACKUP_DIR / f"pre-compact-{ts}.jsonl"
try:
    import shutil
    shutil.copy(transcript, raw_backup)
except Exception:
    pass

# ── Парсим транскрипт → извлекаем exchanges ───────────────────────────────────
messages = []
try:
    with open(transcript, encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                msg_type = obj.get("type", "")
                content = ""
                if isinstance(obj.get("message"), dict):
                    c = obj["message"].get("content", "")
                    if isinstance(c, str):
                        content = c
                    elif isinstance(c, list):
                        parts = []
                        for block in c:
                            if isinstance(block, dict):
                                if block.get("type") == "text":
                                    parts.append(block.get("text", ""))
                                elif block.get("type") == "tool_use":
                                    parts.append(f"[{block.get('name','')}({json.dumps(block.get('input',{}))[:80]})]")
                                elif block.get("type") == "tool_result":
                                    content_val = block.get("content", "")
                                    if isinstance(content_val, list):
                                        for item in content_val:
                                            if isinstance(item, dict) and item.get("type") == "text":
                                                parts.append(item.get("text","")[:200])
                                    elif isinstance(content_val, str):
                                        parts.append(content_val[:200])
                        content = " ".join(parts)
                if content and msg_type in ("user", "assistant"):
                    messages.append({"role": msg_type, "content": content[:500]})
            except Exception:
                continue
except Exception:
    pass

# Последние 40 messages
recent = messages[-40:] if len(messages) > 40 else messages

# ── Auto-extract без LLM ──────────────────────────────────────────────────────
def auto_summary(msgs):
    """Извлекает ключевые факты из транскрипта без LLM."""
    files_edited = set()
    commands_run = []
    tasks_done = []
    errors_seen = []

    file_re = re.compile(r'(?:Edit|Write|Read)\s*\(\s*["\']?([^"\')\s]+\.[a-z]{1,5})', re.IGNORECASE)
    bash_re = re.compile(r'\[Bash\(([^)]{0,80})\)\]')
    error_re = re.compile(r'(?:Error|ошибка|Failed|Traceback|KeyError|TypeError)', re.IGNORECASE)
    done_re  = re.compile(r'(?:готово|создан|обновлён|запущен|✓|done|created|updated)', re.IGNORECASE)

    for m in msgs:
        c = m["content"]
        files_edited.update(file_re.findall(c))
        commands_run.extend(bash_re.findall(c)[:2])
        if error_re.search(c):
            errors_seen.append(c[:120])
        if done_re.search(c) and m["role"] == "assistant":
            tasks_done.append(c[:120])

    lines = ["# PreCompact Auto-Summary\n"]
    if files_edited:
        lines.append(f"## Файлы ({len(files_edited)})\n" + "\n".join(f"  · {f}" for f in sorted(files_edited)[:15]))
    if commands_run:
        lines.append(f"## Команды\n" + "\n".join(f"  · {c}" for c in commands_run[:10]))
    if tasks_done:
        lines.append(f"## Завершено\n" + "\n".join(f"  · {t[:80]}" for t in tasks_done[-5:]))
    if errors_seen:
        lines.append(f"## Ошибки\n" + "\n".join(f"  · {e[:100]}" for e in errors_seen[-3:]))
    lines.append(f"\nТранскрипт: {transcript}\nСообщений всего: {len(msgs)}")
    return "\n\n".join(lines)

# ── LLM summary через claude CLI ─────────────────────────────────────────────
def llm_summary(msgs):
    """Умное резюме через Haiku. Fallback → auto_summary."""
    if not msgs:
        return auto_summary(msgs)

    dialog_text = "\n".join(
        f"[{m['role'].upper()}]: {m['content'][:300]}" for m in msgs[-30:]
    )

    prompt = (
        "Ты — система резюмирования контекста. Прочти последние сообщения сессии Claude Code "
        "и создай краткое структурированное резюме для восстановления контекста после compaction.\n\n"
        "Формат:\n"
        "## Задача сессии\n[1-2 строки что делали]\n\n"
        "## Что сделано\n[список файлов/изменений]\n\n"
        "## Незавершённое\n[если есть]\n\n"
        "## Ключевые решения\n[важные архитектурные решения или договорённости]\n\n"
        "Сообщения:\n\n" + dialog_text
    )

    try:
        result = subprocess.run(
            ["claude", "-p", prompt,
             "--model", "claude-haiku-4-5-20251001",
             "--max-tokens", "400"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and result.stdout.strip():
            return f"# LLM PreCompact Summary (Haiku)\n\n{result.stdout.strip()}\n\n---\nТранскрипт: {transcript}"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    return auto_summary(msgs)

# ── Генерируем и сохраняем summary ───────────────────────────────────────────
summary_text = llm_summary(recent)
summary_file = BACKUP_DIR / f"pre-compact-{ts}.md"
try:
    summary_file.write_text(summary_text, encoding="utf-8")
    print(f"PreCompact: {raw_backup.name} + summary.md ({len(recent)} msgs)")
except Exception as e:
    print(f"PreCompact backup error: {e}", file=sys.stderr)

sys.exit(0)
