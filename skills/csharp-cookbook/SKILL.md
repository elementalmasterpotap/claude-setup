---
name: csharp-cookbook
description: C# 5 / .NET 4.x паттерны для csc.exe. Автоматически подгружается при задачах с C#, WinForms, csc.exe компиляцией.
user-invocable: false
---

## csc.exe = C# 5 — что НЕ работает

| C# 6+ (не компилируется) | C# 5 (правильно) |
|--------------------------|-----------------|
| `string Foo() => value;` | `string Foo() { return value; }` |
| `{ get; set; } = Color.Red` | инициализировать в конструкторе |
| `$"Hello {name}"` | `string.Format("Hello {0}", name)` |
| `nameof(MyProp)` | `"MyProp"` (литерал) |

## Компиляция WinForms

```powershell
$csc = "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
& $csc /target:winexe /out:"App.exe" `
       /reference:System.Windows.Forms.dll `
       /reference:System.Drawing.dll `
       /reference:System.dll `
       /optimize+ "src\App.cs"
```

## Тёмная тема WinForms

```csharp
[DllImport("dwmapi.dll")]
static extern int DwmSetWindowAttribute(IntPtr hwnd, int attr, ref int v, int size);

protected override void OnHandleCreated(EventArgs e) {
    base.OnHandleCreated(e);
    int dark = 1;
    DwmSetWindowAttribute(Handle, 20, ref dark, 4);
}
```

Цвета:
```csharp
static readonly Color C_BG     = Color.FromArgb(28, 28, 28);
static readonly Color C_ACCENT = Color.FromArgb(0, 191, 255);   // #00BFFF cyan
static readonly Color C_DANGER = Color.FromArgb(204, 51, 51);
static readonly Color C_OK     = Color.FromArgb(40, 160, 80);
```

## Локализация C# 5

```csharp
bool isRu;  // инициализировать в конструкторе!

public MainForm() {
    isRu = System.Globalization.CultureInfo.InstalledUICulture
               .TwoLetterISOLanguageName == "ru";
    InitializeComponent();
}

// C# 5 — блочный синтаксис (не =>)
string S(string ru, string en) { return isRu ? ru : en; }
```
