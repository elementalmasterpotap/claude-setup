#!/usr/bin/env python3
"""
Stop hook: learning system — детектор новых паттернов.
Если в ответе найдена ловушка/инсайт без предложения /learn → warn.
"""
import sys, json, re

# Маркеры нового инсайта / ловушки / паттерна
INSIGHT_RE = re.compile(
    r'\bловушка\b'
    r'|антипаттерн'
    r'|не делай так'
    r'|избегай этого'
    r'|стоит запомнить'
    r'|важная особенность'
    r'|нашёл паттерн'
    r'|оказалось\s.{0,40}(что|:)'
    r'|выяснилось\s.{0,20}что'
    r'|второй раз\s.{0,30}(встреч|сталкива)'
    r'|снова та же'
    r'|уже встречал'
    r'|интересная особенность'
    r'|это баг\s'
    # EN
    r'|\bgotcha\b'
    r'|footgun'
    r'|\bantipattern\b',
    re.IGNORECASE
)

# Уже предложено
ALREADY_RE = re.compile(
    r'/learn|оформить.*правил|предлаг.*правил|запомни.{0,30}правил',
    re.IGNORECASE
)

FENCED_RE = re.compile(r'```.*?```', re.DOTALL)

try:
    data = json.load(sys.stdin)
    if data.get('stop_hook_active', False):
        sys.exit(0)

    text  = data.get('last_assistant_message', '')
    clean = FENCED_RE.sub('', text)

    if INSIGHT_RE.search(clean) and not ALREADY_RE.search(clean):
        print(json.dumps({
            "decision": "block",
            "reason": (
                "💡 Обнаружен паттерн/ловушка — предложи пользователю оформить как правило.\n"
                "Добавь в конец ответа:\n"
                "«💡 Могу зафиксировать это как правило — /learn если нужно»"
            )
        }, ensure_ascii=False))

except Exception:
    pass

sys.exit(0)
