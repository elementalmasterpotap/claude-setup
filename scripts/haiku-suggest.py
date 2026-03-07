#!/usr/bin/env python3
"""
UserPromptSubmit хук: complexity scoring → инъекция подсказки HAIKU_ELIGIBLE.

Анализирует промпт пользователя. Если задача выглядит как read-only анализ
(найти / перечислить / структура / что делает) — инжектирует в системный промпт
напоминание использовать codebase-explorer субагент.

Из haiku-router/SKILL.md правила:
  · prompt + ответ < 2000 токенов  →  Haiku
  · только читает, не меняет       →  Haiku
  · Edit/Write/решение нужно       →  Sonnet
"""
import sys, json, re

# ── Сигналы Haiku — read-only задачи ─────────────────────────────────────────
HAIKU_SIGNALS = [
    # Русские — поиск и анализ
    r'\bнайди\b', r'\bнайдите\b', r'\bнайти\b',
    r'\bищи\b', r'\bищу\b', r'\bпоищи\b',
    r'\bперечисли\b', r'\bперечисли\b', r'\bпокажи\b',
    r'\bпоказать\b', r'\bпосмотри\b', r'\bпосмотреть\b',
    r'\bсколько\b',
    r'\bструктура\b', r'\bструктуру\b',
    r'\bаудит\b', r'\bаудитить\b',
    r'\bдубли\b', r'\bдублирован', r'\bдублей\b',
    r'\bпроверь\b', r'\bпроверить\b',
    r'\bсписок\b', r'\bсписке\b',
    r'\bкакие файлы\b', r'\bгде используется\b', r'\bгде используют\b',
    r'\bчто делает\b', r'\bчто делают\b',
    r'\bкак устроен\b', r'\bкак устроено\b',
    r'\bесть ли\b',
    r'\bпокажи все\b',
    r'\bпоиск\b',
    r'\bпросмотри\b', r'\bпочитай\b', r'\bпрочитай\b',
    r'\bсчитай\b',
    r'\bвыведи\b', r'\bвыводи\b',
    r'\bперечисление\b',
    r'\bсравни\b',       # только анализ, не изменение
    r'\bопиши\b', r'\bопишите\b',
    r'\bчто находится\b', r'\bчто содержит\b',
    r'\bкакие.*есть\b',
    r'\bпроверка\b',
    r'\bобзор\b',

    # English — search/analysis
    r'\bfind\b', r'\blist\b', r'\bsearch\b',
    r'\bcount\b', r'\bshow\b', r'\bshow all\b',
    r'\baudit\b', r'\bstructure\b',
    r'\bwhat does\b', r'\bwhat is\b', r'\bhow is\b',
    r'\bcheck\b', r'\banalyze\b', r'\banalyse\b',
    r'\bscan\b', r'\bduplicate\b', r'\bduplicates\b',
    r'\bwhere is\b', r'\bwhere are\b',
    r'\bdescribe\b', r'\bsummarize\b',
    r'\bcompare\b',
    r'\bread\b', r'\breview\b',
]

# ── Сигналы Sonnet — нужно писать/менять ────────────────────────────────────
SONNET_SIGNALS = [
    # Русские — создание/изменение
    r'\bнапиши\b', r'\bнапишите\b', r'\bнаписать\b',
    r'\bсоздай\b', r'\bсоздайте\b', r'\bсоздать\b',
    r'\bисправь\b', r'\bисправьте\b', r'\bисправить\b',
    r'\bреализуй\b', r'\bреализуйте\b', r'\bреализовать\b',
    r'\bрефактори\b', r'\bрефактор',
    r'\bпочему\b',    # объяснение с рассуждением
    r'\bархитектура\b', r'\bархитектурн',
    r'\bреши\b', r'\bрешить\b',
    r'\bдобавь\b', r'\bдобавьте\b', r'\bдобавить\b',
    r'\bизмени\b', r'\bизменить\b',
    r'\bудали\b', r'\bудалить\b',
    r'\bпоправь\b', r'\bпоправить\b',
    r'\bсделай\b', r'\bсделайте\b',
    r'\bпомоги реализовать\b',
    r'\bобнови\b', r'\bобновить\b',
    r'\bзапусти\b', r'\bзапустить\b',

    # Рассуждение
    r'\bobject.*why\b',
    r'\bexplain why\b', r'\bstep.?by.?step\b', r'\breasoning\b',
    r'\bпошагово\b', r'\bпошагов', r'\bобъясни почему\b',

    # English — create/modify
    r'\bwrite\b', r'\bcreate\b', r'\bfix\b',
    r'\bimplement\b', r'\brefactor\b',
    r'\badd\b', r'\bchange\b', r'\bdelete\b', r'\bremove\b',
    r'\bmodify\b', r'\bbuild\b', r'\bdesign\b', r'\barchitect\b',
    r'\bupdate\b', r'\bgenerate\b', r'\bmake\b',
    r'\bdeploy\b', r'\brun\b', r'\bexecute\b',
]

# ── Смешанные (найди И исправь) → Sonnet ────────────────────────────────────
MIXED_RE = re.compile(
    r'(найди|ищи|find|search).{0,60}(исправь|измени|добавь|fix|modify|add|change)'
    r'|(исправь|fix).{0,60}(найди|find)',
    re.IGNORECASE
)

# ── Явные размерные признаки Haiku ──────────────────────────────────────────
QUICK_HAIKU = re.compile(
    r'\bкакие\s+файлы\b'
    r'|\bсколько\s+(строк|функций|файлов|классов)\b'
    r'|\bнайди\s+все\s+\w+\s+(где|в\s+которых|с)\b'
    r'|\bпокажи\s+структуру\b'
    r'|\bперечисли\s+все\b'
    r'|\blist\s+all\b'
    r'|\bshow\s+structure\b'
    r'|\bcount\s+all\b',
    re.IGNORECASE
)


def score(text: str):
    t = text.lower()
    h = sum(1 for p in HAIKU_SIGNALS if re.search(p, t))
    s = sum(1 for p in SONNET_SIGNALS if re.search(p, t))
    mixed = bool(MIXED_RE.search(t))
    quick = bool(QUICK_HAIKU.search(text))
    return h, s, mixed, quick


try:
    payload = json.loads(sys.stdin.read())
    prompt = payload.get("user_message") or payload.get("prompt") or ""

    h_score, s_score, is_mixed, is_quick = score(prompt)

    # Haiku eligible: чёткие haiku-сигналы, ноль sonnet-сигналов, не смешанная
    eligible = (
        (is_quick or h_score >= 2)
        and s_score == 0
        and not is_mixed
    )

    if eligible:
        hint = (
            f"[HAIKU_ELIGIBLE: h={h_score} s={s_score}] "
            "Эта задача — read-only анализ без правок кода. "
            "Используй Task(subagent_type='codebase-explorer') — Haiku субагент. "
            "Перед вызовом напиши в ответе: [→ Haiku] <что делаю>. "
            "ВАЖНО ДЛЯ ЭКОНОМИИ ТОКЕНОВ: "
            "1) НЕ используй extended thinking для этой задачи — она простая, прямой ответ без thinking-блока. "
            "2) Verbose результат оставь в субагенте, в главный контекст верни только summary. "
            "3) Правило из haiku-router skill."
        )
        print(json.dumps({"injectedSystemPrompt": hint}, ensure_ascii=False))

except Exception:
    pass

sys.exit(0)
