#!/usr/bin/env python3
"""
pseudograph.py — генератор псевдографики для Claude ответов
Использование: python3 pseudograph.py --type [box|table|tree|arrow]
"""
import sys
import argparse

# ── BOX-DRAWING ──────────────────────────────────────────────
TL, TR, BL, BR = '╔', '╗', '╚', '╝'
H, V, ML, MR   = '═', '║', '╠', '╣'
tl, tr, bl, br = '┌', '┐', '└', '┘'
h, v, ml, mr   = '─', '│', '├', '┤'


def box(lines: list[str], title: str = '', width: int = 0, double: bool = True) -> str:
    """Рисует рамку вокруг списка строк."""
    if double:
        _TL, _TR, _BL, _BR, _H, _V, _ML, _MR = TL, TR, BL, BR, H, V, ML, MR
    else:
        _TL, _TR, _BL, _BR, _H, _V, _ML, _MR = tl, tr, bl, br, h, v, ml, mr

    w = max(width, max((len(l) for l in lines), default=0), len(title) + 2) + 2
    out = []

    if title:
        pad = w - len(title) - 2
        lp = pad // 2
        rp = pad - lp
        out.append(f"{_TL}{_H * lp} {title} {_H * rp}{_TR}")
    else:
        out.append(f"{_TL}{_H * w}{_TR}")

    for line in lines:
        out.append(f"{_V} {line:<{w - 2}} {_V}")

    out.append(f"{_BL}{_H * w}{_BR}")
    return '\n'.join(out)


def table(headers: list[str], rows: list[list[str]], sep: str = ' │ ') -> str:
    """Рисует таблицу с заголовками."""
    cols = len(headers)
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row[:cols]):
            widths[i] = max(widths[i], len(str(cell)))

    def fmt_row(cells, fill='─', cross='─┼─'):
        if fill != ' ':
            return '─' + cross.join('─' * w for w in widths) + '─'
        return sep.join(f"{str(c):<{widths[i]}}" for i, c in enumerate(cells[:cols]))

    divider = '─' + '─┼─'.join('─' * w for w in widths) + '─'
    header  = sep.join(f"{h:<{widths[i]}}" for i, h in enumerate(headers))

    out = [header, divider]
    for row in rows:
        out.append(sep.join(f"{str(c):<{widths[i]}}" for i, c in enumerate(row[:cols])))

    return '\n'.join(out)


def tree(items: dict | list, prefix: str = '', _last: bool = True) -> str:
    """Рисует дерево из dict (ключ→значение) или list."""
    out = []
    if isinstance(items, dict):
        entries = list(items.items())
    elif isinstance(items, list):
        entries = [(item, None) for item in items]
    else:
        return str(items)

    for i, (key, val) in enumerate(entries):
        last = i == len(entries) - 1
        connector = '└─' if last else '├─'
        out.append(f"{prefix}{connector} {key}")
        if val is not None:
            child_prefix = prefix + ('   ' if last else '│  ')
            if isinstance(val, (dict, list)):
                out.append(tree(val, child_prefix, last))
            else:
                out.append(f"{child_prefix}└─ {val}")

    return '\n'.join(out)


def arrow(steps: list[str], vertical: bool = False) -> str:
    """Рисует цепочку шагов со стрелками."""
    if vertical:
        return '\n    │\n    ▼\n'.join(f"  {s}" for s in steps)
    return ' → '.join(steps)


# ── CLI ──────────────────────────────────────────────────────
def demo():
    print("\n── BOX ─────────────────────────────────────")
    print(box(['Строка 1', 'Строка 2', 'Строка 3'], title='Заголовок'))

    print("\n── TABLE ────────────────────────────────────")
    print(table(
        ['Задача', 'Модель', 'Токены'],
        [
            ['Найти файл', 'Haiku', '~100'],
            ['Написать фичу', 'Sonnet', '~1000'],
            ['Архитектура', 'Opus', '~5000'],
        ]
    ))

    print("\n── TREE ─────────────────────────────────────")
    print(tree({
        '~/.claude': {
            'rules/': ['communication.md', 'token-budget.md'],
            'scripts/': ['haiku-suggest.py', 'pseudo-check.py'],
            'skills/': ['sync/', 'compact-smart/'],
        }
    }))

    print("\n── ARROW (horizontal) ───────────────────────")
    print(arrow(['правка', 'деплой', 'проверка', 'коммит']))

    print("\n── ARROW (vertical) ─────────────────────────")
    print(arrow(['получить задачу', 'оценить complexity', 'выбрать модель', 'выполнить'], vertical=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Генератор псевдографики')
    parser.add_argument('--demo', action='store_true', help='Показать примеры')
    parser.add_argument('--type', choices=['box', 'table', 'tree', 'arrow'], help='Тип элемента')
    args = parser.parse_args()

    if args.demo or not args.type:
        demo()
    else:
        print(f"Для программного использования: import pseudograph; pseudograph.{args.type}(...)")
