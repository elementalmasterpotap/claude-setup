#!/usr/bin/env python3
"""
Stop hook: no corporate tone.
Правило communication.md: чувак-друг-гик, не ассистент. Без канцелярита.
"""
import sys, json, re

CORP_PHRASES = [
    # Классический канцелярит
    'убедительно рекоменду',
    'настоятельно рекоменду',
    'следует отметить, что',
    'необходимо подчеркнуть',
    'в целях обеспечения',
    # Ассистент-стиль (подобострастие)
    'позвольте объяснить',
    'позвольте мне объяснить',
    'хотелось бы отметить',
    'рад помочь вам',
    'с удовольствием помогу',
    'буду рад помочь',
    'надеюсь это помогло',
    'надеюсь, что это поможет',
    'если у вас есть вопросы',
    'не стесняйтесь обращаться',
    # EN канцелярит
    'i hope this helps',
    'feel free to ask',
    'please let me know if',
    'happy to help',
    'certainly! here',
    'of course! here',
    'absolutely! here',
]

FENCED_RE  = re.compile(r'```.*?```', re.DOTALL)
QUOTED_RE  = re.compile(r'>.*')  # blockquote — не считать

try:
    data = json.load(sys.stdin)
    if data.get('stop_hook_active', False):
        sys.exit(0)

    text = data.get('last_assistant_message', '')
    # Вырезаем блоки кода и цитаты
    clean = FENCED_RE.sub('', text)
    clean = QUOTED_RE.sub('', clean).lower()

    found = [p for p in CORP_PHRASES if p.lower() in clean]

    if found:
        print(json.dumps({
            "decision": "block",
            "reason": (
                f"⚠️ Корпоративный тон: «{found[0]}»\n"
                "Правило: чувак-друг-гик, не ассистент. Без подобострастия и канцелярита."
            )
        }, ensure_ascii=False))

except Exception:
    pass

sys.exit(0)
