#!/usr/bin/env python3
"""
Stop hook: C# 5 compat check.
Правило CS-1/CS-2 (lessons_universal.md): csc.exe .NET 4.x = C# 5.
Expression-bodied members, auto-property init, $"", nameof() — всё C# 6+.
"""
import sys, json, re

CS_BLOCK_RE    = re.compile(r'```(?:csharp|cs|c#)\n(.*?)```', re.DOTALL | re.IGNORECASE)
EXPR_BODY_RE   = re.compile(r'\b\w[\w<>[\]]+\s+\w+\s*\([^)]*\)\s*=>\s*\S')  # Foo() => val
AUTO_INIT_RE   = re.compile(r'\{\s*get;\s*set;\s*\}\s*=\s*\S')               # { get; set; } = X
INTERPOLAT_RE  = re.compile(r'\$"')                                            # $"..."
NAMEOF_RE      = re.compile(r'\bnameof\s*\(')                                 # nameof(X)

try:
    data = json.load(sys.stdin)
    if data.get('stop_hook_active', False):
        sys.exit(0)

    text   = data.get('last_assistant_message', '')
    blocks = CS_BLOCK_RE.findall(text)
    if not blocks:
        sys.exit(0)

    issues = []
    for block in blocks:
        if EXPR_BODY_RE.search(block):
            issues.append("expression-bodied `Foo() => value` → C# 6+, не csc.exe")
        if AUTO_INIT_RE.search(block):
            issues.append("auto-property init `{ get; set; } = X` → C# 6+")
        if INTERPOLAT_RE.search(block):
            issues.append('string interpolation `$"..."` → C# 6+, используй string.Format()')
        if NAMEOF_RE.search(block):
            issues.append("`nameof()` → C# 6+")

    if issues:
        print(json.dumps({
            "decision": "warn",
            "reason": (
                "⚠️ C# 5 несовместимо (csc.exe .NET 4.x):\n"
                + "\n".join(f"  · {i}" for i in issues) +
                "\nПравило CS-1/CS-2 (lessons_universal.md)"
            )
        }, ensure_ascii=False))

except Exception:
    pass

sys.exit(0)
