# Windows Dev — паттерны для PowerShell и C# WinForms

---

## settings.json — читать/писать только через Python

**Проблема:** `Edit(settings.json)` → "File has not been read yet" даже после чтения.
`cat ~/.claude/settings.json | python3 -c "..."` → путь `/c/Users/...` не раскрывается в Windows.
**Решение:** всегда `os.path.expanduser('~/.claude/settings.json')` через Python-heredoc:
```python
import json, os
path = os.path.expanduser('~/.claude/settings.json')
with open(path) as f: data = json.load(f)
# ... изменения ...
with open(path, 'w') as f: json.dump(data, f, indent=2, ensure_ascii=False)
```
**Правило:** settings.json — только Python, никогда Edit/cat/pipe.

---

## PowerShell installer — структура

Проверенный паттерн установщика с псевдо-GUI, RU/EN, backup+manifest, -NoPrompt.

### Скелет
```powershell
param([switch]$NoPrompt, [switch]$Quiet)
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# ── ПУТИ ────────────────────────────────────────────────────
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$sourceFile  = Join-Path $projectRoot "src\MainFile.ext"
$targetDir   = Join-Path $env:APPDATA "AppName"
$manifest    = Join-Path $targetDir "InstallManifest.json"

# ── ЯЗЫК ────────────────────────────────────────────────────
$Lang = if ((Get-WinSystemLocale).TwoLetterISOLanguageName -eq 'ru') { 'ru' } else { 'en' }
$T = if ($Lang -eq 'ru') { @{
    Done    = "Готово."
    Error   = "Файл не найден"
    WaitMsg = "Закроется через {0} сек  ·  любая клавиша — выйти"
}} else { @{
    Done    = "Done."
    Error   = "File not found"
    WaitMsg = "Closing in {0} sec  ·  any key to exit"
}}

# ── BOX DRAWING ──────────────────────────────────────────────
$cTL=[char]0x2554; $cTR=[char]0x2557; $cBL=[char]0x255A; $cBR=[char]0x255D
$cH=[char]0x2550;  $cV=[char]0x2551;  $cML=[char]0x2560; $cMR=[char]0x2563
$cHs=[char]0x2500; $cVs=[char]0x2502
$W = 68

function Write-BoxLine {
    param([string]$inner="",[ConsoleColor]$fc='DarkCyan',[ConsoleColor]$tc='Gray')
    Write-Host $cV -ForegroundColor $fc -NoNewline
    Write-Host $inner.PadRight($W) -ForegroundColor $tc -NoNewline
    Write-Host $cV -ForegroundColor $fc
}
function Write-BoxTop    { Write-Host ($cTL+([string]$cH*$W)+$cTR) -ForegroundColor DarkCyan }
function Write-BoxBottom { Write-Host ($cBL+([string]$cH*$W)+$cBR) -ForegroundColor DarkCyan }
function Write-BoxDiv    { Write-Host ($cML+([string]$cH*$W)+$cMR) -ForegroundColor DarkCyan }
function Write-BoxEmpty  { Write-BoxLine }
function Pad-Center { param([string]$s,[int]$w) $p=$w-$s.Length; if($p-le 0){return $s}; (' '*[math]::Floor($p/2))+$s+(' '*($p-[math]::Floor($p/2))) }

# ── ТАЙМЕР ЗАКРЫТИЯ ──────────────────────────────────────────
function Wait-KeyOrTimeout {
    param([int]$Seconds=8)
    try { [Console]::CursorVisible=$true } catch {}
    for ($i=$Seconds; $i-gt 0; $i--) {
        Write-Host ("`r  "+($T.WaitMsg -f $i)+"  ") -NoNewline -ForegroundColor DarkGray
        for ($ms=0; $ms-lt 10; $ms++) {
            if ([Console]::KeyAvailable) { [Console]::ReadKey($true)|Out-Null; Write-Host ""; return }
            Start-Sleep -Milliseconds 100
        }
    }
    Write-Host ""
}

# ── ЯДРО УСТАНОВКИ ──────────────────────────────────────────
function Run-Install {
    if (-not (Test-Path $sourceFile)) { throw $T.Error }
    New-Item -ItemType Directory -Path $targetDir -Force | Out-Null

    # Бэкап предыдущей версии
    $prev = Join-Path $projectRoot "docs\AppFile.prev.ext"
    Copy-Item $sourceFile -Destination $prev -Force

    # Копирование
    Copy-Item $sourceFile -Destination (Join-Path $targetDir "AppFile.ext") -Force

    # Манифест
    @{ installedAt=(Get-Date).ToString("s"); version="1.0.0"; files=@("AppFile.ext") } |
        ConvertTo-Json -Depth 3 | Set-Content -Path $manifest -Encoding UTF8
}

# ── ТИХИЙ РЕЖИМ ─────────────────────────────────────────────
if ($NoPrompt) {
    Run-Install
    Write-Host $T.Done -ForegroundColor Green
    exit 0
}

# ── ИНТЕРАКТИВНЫЙ РЕЖИМ ──────────────────────────────────────
try { [Console]::CursorVisible=$false } catch {}
Clear-Host

Write-BoxTop
Write-BoxLine (Pad-Center "APP NAME" $W) DarkCyan Yellow
Write-BoxBottom

# ... меню, кнопки, Show-Progress
```

### Latin fallback для русской раскладки
```powershell
# Когда у = [Ц] на английской раскладке = 'u':
switch ([char]::ToLower($key.KeyChar)) {
    'u' { if ($Lang -eq 'ru') { $action = 'install' } }
    'i' { if ($Lang -eq 'ru') { $action = 'guide'   } }
    'o' { if ($Lang -eq 'ru') { $action = 'cancel'  } }
}
```

---

## C# WinForms — тёмная тема (csc.exe / .NET 4.x / C# 5)

### DWM тёмный заголовок окна
```csharp
using System.Runtime.InteropServices;

[DllImport("dwmapi.dll")]
static extern int DwmSetWindowAttribute(IntPtr hwnd, int attr, ref int attrValue, int attrSize);

protected override void OnHandleCreated(EventArgs e) {
    base.OnHandleCreated(e);
    int dark = 1;
    DwmSetWindowAttribute(Handle, 20, ref dark, 4);
}
```

### Цвета тёмной темы
```csharp
static readonly Color C_BG     = Color.FromArgb(28, 28, 28);   // основной фон
static readonly Color C_HEADER = Color.FromArgb(18, 18, 18);   // шапка
static readonly Color C_BORDER = Color.FromArgb(51, 51, 51);   // бордеры
static readonly Color C_TEXT   = Color.FromArgb(220, 220, 220);// текст
static readonly Color C_SUB    = Color.FromArgb(128, 128, 128);// подзаголовки
static readonly Color C_ACCENT = Color.FromArgb(0, 191, 255);  // cyan #00BFFF
static readonly Color C_DANGER = Color.FromArgb(204, 51, 51);  // красный
static readonly Color C_OK     = Color.FromArgb(40, 160, 80);  // зелёный
static readonly Color C_LOG_BG = Color.FromArgb(17, 17, 17);   // лог-панель
```

### Локализация
```csharp
// C# 5 — без auto-property initializers, инициализировать в конструкторе
bool isRu;

public MainForm() {
    isRu = System.Globalization.CultureInfo.InstalledUICulture
               .TwoLetterISOLanguageName == "ru";
    InitializeComponent();
}

// Хелпер — C# 5, блочный синтаксис (не =>)
string S(string ru, string en) { return isRu ? ru : en; }
```

### Кастомная кнопка с hover/press
```csharp
class DarkButton : Button {
    public Color AccentColor;   // инициализировать в конструкторе, не как auto-init
    bool _hover, _press;

    public DarkButton() {
        AccentColor = Color.FromArgb(50, 50, 50);
        SetStyle(ControlStyles.UserPaint | ControlStyles.AllPaintingInWmPaint, true);
        FlatStyle = FlatStyle.Flat;
        FlatAppearance.BorderSize = 0;
        Cursor = Cursors.Hand;
    }

    protected override void OnMouseEnter(EventArgs e) { base.OnMouseEnter(e); _hover=true; Invalidate(); }
    protected override void OnMouseLeave(EventArgs e) { base.OnMouseLeave(e); _hover=false; Invalidate(); }
    protected override void OnMouseDown(MouseEventArgs e) { base.OnMouseDown(e); _press=true; Invalidate(); }
    protected override void OnMouseUp(MouseEventArgs e) { base.OnMouseUp(e); _press=false; Invalidate(); }

    protected override void OnPaint(PaintEventArgs e) {
        var bg = _press ? ControlPaint.Dark(AccentColor, 0.2f)
               : _hover ? AccentColor
               : ControlPaint.Dark(AccentColor, 0.4f);
        e.Graphics.Clear(bg);
        var sf = new StringFormat { Alignment=StringAlignment.Center, LineAlignment=StringAlignment.Center };
        e.Graphics.DrawString(Text, Font, new SolidBrush(ForeColor), ClientRectangle, sf);
    }
}
```

### Компиляция через csc.exe
```powershell
$csc = "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
& $csc /target:winexe /out:"App.exe" `
       /reference:System.Windows.Forms.dll `
       /reference:System.Drawing.dll `
       /reference:System.dll `
       /optimize+ "src\App.cs"
```

### C# 5 ограничения (частые ошибки)
- `string Foo() => value` → `string Foo() { return value; }`
- `public Color X { get; set; } = Color.Red` → инициализировать в конструкторе
- `var x = new Foo { Prop = val }` — object initializers работают
- `string.IsNullOrWhiteSpace` — работает
- `nameof()` — НЕ работает (C# 6+)
- `$"..."` — интерполяция НЕ работает (C# 6+), использовать `string.Format`
