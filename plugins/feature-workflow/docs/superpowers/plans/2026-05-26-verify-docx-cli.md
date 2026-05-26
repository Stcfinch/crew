# verify-docx-cli Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 feature-workflow plugin 內新建 verify-docx-cli .NET 子專案，把 plan-verify step 10 Word 報告產出從「呼叫 minimax-docx CLI 不存在的 run-script 命令」改成「呼叫自家 .NET CLI」，並順手統一過時的 config 路徑。

**Architecture:** feature-workflow 自帶 `references/dotnet/verify-docx-cli/`（multi-target net8.0;net10.0 + `RollForward=LatestMajor`）。ProjectReference 到 minimax-skills 的 `MiniMaxAIDocx.Core`（透過 `$(MinimaxCorePath)` env var override + `$(HOME)/.claude/plugins/...` fallback），共用 OpenXML helpers + XSD validator。plan-verify 流程加 preflight 偵測 + 改寫 step 10.4a 抽象描述為具體 `dotnet run` 指令。

**Tech Stack:** C# / .NET 8/10、System.CommandLine、Markdig、DocumentFormat.OpenXml（via Core ProjectReference）、bash for phase docs。

**Spec:** `docs/superpowers/specs/2026-05-26-verify-docx-cli-design.md`

**Repo root** (本 plan 所有相對路徑以此為基準): `~/.claude/plugins/marketplaces/company-marketplace/`

**Plugin root**: `plugins/feature-workflow/`

---

## File Structure

新建檔案：

```
plugins/feature-workflow/references/dotnet/verify-docx-cli/
├── VerifyDocxCli.csproj
├── Program.cs
├── README.md
├── assets/
│   └── intumit-logo.png
├── Markdown/
│   ├── VerifySection.cs
│   └── VerifyMarkdownParser.cs
├── Styles/
│   ├── IBrandStyle.cs
│   ├── BrandColors.cs
│   ├── IntumitStyle.cs
│   ├── TechDarkStyle.cs
│   └── SwissStyle.cs
├── Rendering/
│   ├── DocumentBuilder.cs
│   ├── CoverRenderer.cs
│   ├── SignoffRenderer.cs
│   ├── EnvRenderer.cs
│   ├── SummaryRenderer.cs
│   ├── DetailRenderer.cs
│   ├── PendingRenderer.cs
│   ├── AppendixRenderer.cs
│   └── TocInserter.cs
├── Sanitization/
│   └── SensitiveDataMasker.cs
└── Validation/
    └── XsdGateCheck.cs
```

修改檔案：

| 檔案 | 用途 |
|------|------|
| `plugins/feature-workflow/skills/plan-verify/phases/word-report.md` | F4 新增 step 10.0c preflight；F5 改寫 step 10.4a；F7 改 L84 路徑 |
| `plugins/feature-workflow/skills/plan-verify/SKILL.md` | F6 引擎偵測邏輯；F7 改 L527 路徑 |
| `plugins/feature-workflow/references/config-resolver.md` | F7 統一路徑 + 加遷移說明 |
| `plugins/feature-workflow/references/config.template.md` | F7 |
| `plugins/feature-workflow/references/prerequisites.md` | F7 |
| `plugins/feature-workflow/README.md` | F7 |
| `plugins/feature-workflow/skills/plan-setup/SKILL.md` | F7 多處 |
| `plugins/feature-workflow/skills/plan-stack/SKILL.md` | F7 |
| `plugins/feature-workflow/skills/plan-close/SKILL.md` | F7 |
| `plugins/feature-workflow/skills/plan-start/SKILL.md` | F7 |

**Acceptance：完整 plan-verify 跑完後，產出三套 style 的 docx，TOC 欄位 + Logo + XSD 驗證皆通過。**

---

## Phase F1: .NET 子專案骨架 + Program.cs entry

**目的**：先把可 build 可跑（即使只是印 help）的骨架立起來，後續每個 phase 都能 incremental build。

**Files:**
- Create: `plugins/feature-workflow/references/dotnet/verify-docx-cli/VerifyDocxCli.csproj`
- Create: `plugins/feature-workflow/references/dotnet/verify-docx-cli/Program.cs`
- Create: `plugins/feature-workflow/references/dotnet/verify-docx-cli/.gitignore`

### Steps

- [ ] **F1.1 建目錄結構**

```bash
cd ~/.claude/plugins/marketplaces/company-marketplace
mkdir -p plugins/feature-workflow/references/dotnet/verify-docx-cli/{assets,Markdown,Styles,Rendering,Sanitization,Validation}
```

- [ ] **F1.2 寫 VerifyDocxCli.csproj**

檔案：`plugins/feature-workflow/references/dotnet/verify-docx-cli/VerifyDocxCli.csproj`

```xml
<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFrameworks>net8.0;net10.0</TargetFrameworks>
    <RollForward>LatestMajor</RollForward>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
    <NeutralLanguage>zh-TW</NeutralLanguage>
    <RootNamespace>FeatureWorkflow.VerifyDocxCli</RootNamespace>
    <AssemblyName>verify-docx-cli</AssemblyName>
  </PropertyGroup>

  <PropertyGroup>
    <!-- ProjectReference 解析：env var override 優先，否則用 $HOME fallback -->
    <MinimaxCoreDefault>$(HOME)/.claude/plugins/marketplaces/minimax-skills/skills/minimax-docx/scripts/dotnet/MiniMaxAIDocx.Core/MiniMaxAIDocx.Core.csproj</MinimaxCoreDefault>
    <MinimaxCorePath Condition="'$(MinimaxCorePath)' == ''">$(MinimaxCoreDefault)</MinimaxCorePath>
  </PropertyGroup>

  <ItemGroup>
    <ProjectReference Include="$(MinimaxCorePath)" />
  </ItemGroup>

  <ItemGroup>
    <PackageReference Include="System.CommandLine" Version="2.0.0-beta4.22272.1" />
    <PackageReference Include="Markdig" Version="0.37.0" />
  </ItemGroup>

  <ItemGroup>
    <None Include="assets/**/*" CopyToOutputDirectory="PreserveNewest" />
  </ItemGroup>

</Project>
```

**注意**：System.CommandLine 用 beta 版（2.0.0-beta4.22272.1），與 minimax-skills 的 Cli 對齊（避免雙重 Roslyn 版本衝突）。實作前用 `dotnet add package System.CommandLine --prerelease` 確認最新可用 beta 號。

- [ ] **F1.3 寫 .gitignore**

檔案：`plugins/feature-workflow/references/dotnet/verify-docx-cli/.gitignore`

```
bin/
obj/
*.user
```

- [ ] **F1.4 寫 Program.cs（CLI 骨架，先把 arg 都解析好但暫不實作渲染）**

檔案：`plugins/feature-workflow/references/dotnet/verify-docx-cli/Program.cs`

```csharp
using System.CommandLine;

var verifyOpt = new Option<FileInfo>("--verify") { Description = "verify.md 路徑", Required = true };
var screenshotsOpt = new Option<DirectoryInfo?>("--screenshots") { Description = "截圖目錄" };
var evidenceOpt = new Option<DirectoryInfo?>("--evidence") { Description = "evidence 目錄" };
var outputOpt = new Option<FileInfo>("--output") { Description = "輸出 docx 路徑", Required = true };
var styleOpt = new Option<string>("--style") { Description = "intumit | tech-dark | swiss", DefaultValueFactory = _ => "intumit" };
var logoOpt = new Option<FileInfo?>("--logo") { Description = "覆寫 logo 路徑（不給走三層偵測）" };
var coverOpt = new Option<string>("--cover") { Description = "封面資訊 JSON", Required = true };

var root = new RootCommand("verify-docx-cli: 將 verify.md 渲染為品牌 Word 驗收報告");
root.Options.Add(verifyOpt);
root.Options.Add(screenshotsOpt);
root.Options.Add(evidenceOpt);
root.Options.Add(outputOpt);
root.Options.Add(styleOpt);
root.Options.Add(logoOpt);
root.Options.Add(coverOpt);

root.SetAction(parseResult =>
{
    var verify = parseResult.GetValue(verifyOpt)!;
    var output = parseResult.GetValue(outputOpt)!;
    var style = parseResult.GetValue(styleOpt)!;
    var cover = parseResult.GetValue(coverOpt)!;

    Console.WriteLine($"[verify-docx-cli] verify={verify.FullName}");
    Console.WriteLine($"[verify-docx-cli] output={output.FullName}");
    Console.WriteLine($"[verify-docx-cli] style={style}");
    Console.WriteLine($"[verify-docx-cli] cover length={cover.Length}");
    Console.WriteLine("(渲染邏輯尚未實作，將於 F2 接上)");
    return 0;
});

return await root.Parse(args).InvokeAsync();
```

**注意**：System.CommandLine 2.0 beta4 的 API 與 1.x / 2.0.0-beta2 不同，動詞是 `parseResult.GetValue(option)`、`root.Options.Add(opt)`。若 build 失敗請按錯誤訊息調整 API 形態。

- [ ] **F1.5 驗證 build**

```bash
cd ~/.claude/plugins/marketplaces/company-marketplace/plugins/feature-workflow/references/dotnet/verify-docx-cli
dotnet build
```

預期：0 errors。warning 可暫忽略。

- [ ] **F1.6 驗證 --help 可跑**

```bash
cd ~/.claude/plugins/marketplaces/company-marketplace/plugins/feature-workflow/references/dotnet/verify-docx-cli
dotnet run -- --help
```

預期：印出 6 個 option 說明。**這驗證 RollForward 在 dotnet 10 上 work**。

- [ ] **F1.7 驗證 --cover 與 --verify 參數可吃**

```bash
echo "# test" > /tmp/test-verify.md
cd ~/.claude/plugins/marketplaces/company-marketplace/plugins/feature-workflow/references/dotnet/verify-docx-cli
dotnet run -- --verify /tmp/test-verify.md --output /tmp/test.docx --style intumit --cover '{"project":"X"}'
```

預期 stdout 包含「verify=/tmp/test-verify.md」「style=intumit」「(渲染邏輯尚未實作...)」。

---

## Phase F2-A: Markdown 解析層

**目的**：把 verify.md 七段式（封面表/簽核表/環境表/摘要表/明細小節/待處理表/附錄）轉成 in-memory model，後續 renderer 從 model 渲染。

**Files:**
- Create: `plugins/feature-workflow/references/dotnet/verify-docx-cli/Markdown/VerifySection.cs`
- Create: `plugins/feature-workflow/references/dotnet/verify-docx-cli/Markdown/VerifyMarkdownParser.cs`

### Steps

- [ ] **F2-A.1 寫 VerifySection.cs（data model）**

檔案：`Markdown/VerifySection.cs`

```csharp
namespace FeatureWorkflow.VerifyDocxCli.Markdown;

// 從 --cover JSON 解出來
public record CoverInfo(
    string Project, string Feature, string Author,
    string Date, string Company, string Version);

// step 10.3.5 每條驗收明細
public record DetailItem(
    int Number,
    string Title,
    DetailStatus Status,
    List<string> HumanSteps,        // <!-- human_steps --> 區塊
    string ExpectedResult,
    string ActualResult,
    List<ApiCall> ApiCalls,         // 來自 <!-- evidence --> 或 inline
    List<string> ScreenshotPaths);  // ![desc](screenshots/...)

public enum DetailStatus { Pass, Fail, Skip, Manual }

public record ApiCall(
    string Method, string Url, Dictionary<string,string> Headers,
    int HttpStatus, string ResponseBody, string? EvidenceFileName);

// step 10.3.4
public record SummaryStats(int Pass, int Fail, int Skip, int Manual, string Conclusion);

// step 10.3.6
public record PendingItem(int Number, string Title, DetailStatus Status, string Suggestion);

// step 10.3.3
public record EnvInfo(
    string Url, string Browser, string Role,
    string DataDescription, string Prerequisites);

// step 10.3.7
public record AppendixVersionEntry(string Date, string Version, string Description);

// 整份 verify.md 解析結果
public record VerifyReport(
    CoverInfo Cover,
    EnvInfo Env,
    SummaryStats Summary,
    List<DetailItem> Details,
    List<PendingItem> Pending,
    List<AppendixVersionEntry> Versions);
```

- [ ] **F2-A.2 寫 VerifyMarkdownParser.cs（用 Markdig）**

檔案：`Markdown/VerifyMarkdownParser.cs`

實作要點：
1. `Parse(string verifyMdContent, CoverInfo cover) → VerifyReport`
2. 用 Markdig `Markdown.Parse(content)` 拿 `MarkdownDocument`
3. 走訪 block，按 H2/H3 標題分段：「測試環境」「驗收摘要」「驗收明細」「待處理事項」「附錄」
4. 「驗收明細」section 下每個 H3 子段轉成一個 `DetailItem`
5. 抽 `<!-- human_steps -->` 與 `<!-- evidence -->` HTML comment block 內容（Markdig 透過 `HtmlBlock` 暴露）
6. 圖片 `![desc](screenshots/...)` 用 `LinkInline` 識別，path 收集到 `ScreenshotPaths`
7. 狀態圖示對應：✅→Pass / ❌→Fail / ⏭️→Skip / 🔍→Manual / 👤→Manual

骨架：

```csharp
using Markdig;
using Markdig.Syntax;
using Markdig.Syntax.Inlines;

namespace FeatureWorkflow.VerifyDocxCli.Markdown;

public static class VerifyMarkdownParser
{
    public static VerifyReport Parse(string verifyMdContent, CoverInfo cover)
    {
        var doc = Markdown.Parse(verifyMdContent);
        var env = ExtractEnvInfo(doc);
        var summary = ExtractSummary(doc);
        var details = ExtractDetails(doc);
        var pending = ExtractPending(doc);
        var versions = ExtractAppendixVersions(doc);
        return new VerifyReport(cover, env, summary, details, pending, versions);
    }

    // 範例完整實作：ExtractSummary。其他 Extract* method 依此模式
    private static SummaryStats ExtractSummary(MarkdownDocument doc)
    {
        var section = FindSectionTable(doc, headingText: "驗收摘要");
        if (section == null) return new SummaryStats(0, 0, 0, 0, "（無驗收摘要段落）");

        int pass = 0, fail = 0, skip = 0, manual = 0;
        foreach (var (key, value) in IterateTableRows(section))
        {
            if (!int.TryParse(value.Trim(), out var n)) continue;
            switch (key.Trim())
            {
                case "通過":       pass = n; break;
                case "未通過":     fail = n; break;
                case "略過":       skip = n; break;
                case "待人工確認": manual = n; break;
            }
        }

        // 結論段：通常是 table 之後的第一個粗體段
        var conclusion = FindFirstBoldParagraphAfter(doc, section)
            ?? GenerateConclusion(pass, fail, skip, manual);

        return new SummaryStats(pass, fail, skip, manual, conclusion);
    }

    private static string GenerateConclusion(int pass, int fail, int skip, int manual)
    {
        var total = pass + fail + skip + manual;
        if (fail == 0 && manual == 0) return $"共 {total} 項驗收條件全數通過，建議進入正式上線流程。";
        if (fail > 0) return $"共 {total} 項驗收條件，{fail} 項未通過，需修正後重新驗證。";
        return $"共 {total} 項驗收條件，{pass} 項通過、{manual} 項待人工確認。";
    }

    // 以下 helper（由你實作）
    private static Table? FindSectionTable(MarkdownDocument doc, string headingText) => throw new NotImplementedException();
    private static IEnumerable<(string Key, string Value)> IterateTableRows(Table t) => throw new NotImplementedException();
    private static string? FindFirstBoldParagraphAfter(MarkdownDocument doc, Block after) => throw new NotImplementedException();

    private static EnvInfo ExtractEnvInfo(MarkdownDocument doc)
    {
        // 同 ExtractSummary 的 IterateTableRows 模式
        // 鍵: 測試 URL / 瀏覽器 / 測試帳號角色 / 測試資料說明 / 前置條件
        throw new NotImplementedException();
    }

    private static List<DetailItem> ExtractDetails(MarkdownDocument doc)
    {
        // 找「## 驗收明細」section，逐 H3 子段：
        // 標題: 「驗收項目 {N}：{title}」→ Number, Title
        // 「**結果：{status}**」段 → ParseStatusIcon
        // 「**操作步驟**：」後的 ordered list → HumanSteps
        // 「**預期結果**：」/ 「**實際結果**：」 → ExpectedResult / ActualResult
        // 「**測試紀錄**：」後的 code block → 用 ApiCallParser 解 GET/POST/Headers/JSON → ApiCall
        // 「**截圖**：」後的 image inline → ScreenshotPaths
        throw new NotImplementedException();
    }

    private static List<PendingItem> ExtractPending(MarkdownDocument doc)
    {
        // 找「## 待處理事項」section table
        // 欄位: # / 驗收條件 / 狀態 / 建議處理方式
        throw new NotImplementedException();
    }

    private static List<AppendixVersionEntry> ExtractAppendixVersions(MarkdownDocument doc)
    {
        // 找「### 版本紀錄」section table
        // 欄位: 日期 / 版本 / 說明
        throw new NotImplementedException();
    }

    private static DetailStatus ParseStatusIcon(string text)
    {
        if (text.Contains("✅")) return DetailStatus.Pass;
        if (text.Contains("❌")) return DetailStatus.Fail;
        if (text.Contains("⏭️")) return DetailStatus.Skip;
        if (text.Contains("🔍") || text.Contains("👤")) return DetailStatus.Manual;
        return DetailStatus.Manual; // fallback
    }
}
```

**注意**：實作五個 Extract* 方法時，請參考 spec section 4 的 fixture sample（或 `plugins/feature-workflow/skills/plan-verify/examples/verify-report-sample.md`）逐 section 對照欄位。

- [ ] **F2-A.3 暫接 Program.cs（手動驗證）**

修改 `Program.cs` 的 `SetAction` 內，在「(渲染邏輯尚未實作...)」前加：

```csharp
using FeatureWorkflow.VerifyDocxCli.Markdown;
using System.Text.Json;

// 解 cover JSON
var coverInfo = JsonSerializer.Deserialize<CoverInfo>(cover,
    new JsonSerializerOptions { PropertyNamingPolicy = JsonNamingPolicy.CamelCase })!;

// 解 verify.md
var verifyContent = File.ReadAllText(verify.FullName);
var report = VerifyMarkdownParser.Parse(verifyContent, coverInfo);

Console.WriteLine($"[verify-docx-cli] 解析完成: {report.Details.Count} 個驗收項目, {report.Pending.Count} 個待處理");
```

- [ ] **F2-A.4 手動 smoke：用既有 verify-report-sample.md 試解**

```bash
cd ~/.claude/plugins/marketplaces/company-marketplace/plugins/feature-workflow/references/dotnet/verify-docx-cli
dotnet run -- \
  --verify ../../../skills/plan-verify/examples/verify-report-sample.md \
  --output /tmp/out.docx \
  --cover '{"project":"X","feature":"Y","author":"Z","date":"2026-05-26","company":"Intumit","version":"v1.0"}'
```

預期 stdout：印出「解析完成: N 個驗收項目, M 個待處理」，數字與 sample 內容對得上。如果報 `NotImplementedException`，回去把對應的 Extract* method 實作完。

**Acceptance F2-A**：跑上面 smoke，五個 Extract* 都實作完，計數正確。

---

## Phase F2-B: Style system

**目的**：抽出三套 brand style（顏色、字型、裝飾），renderer 不耦合具體風格。

**Files:**
- Create: `plugins/feature-workflow/references/dotnet/verify-docx-cli/Styles/BrandColors.cs`
- Create: `plugins/feature-workflow/references/dotnet/verify-docx-cli/Styles/IBrandStyle.cs`
- Create: `plugins/feature-workflow/references/dotnet/verify-docx-cli/Styles/IntumitStyle.cs`
- Create: `plugins/feature-workflow/references/dotnet/verify-docx-cli/Styles/TechDarkStyle.cs`
- Create: `plugins/feature-workflow/references/dotnet/verify-docx-cli/Styles/SwissStyle.cs`

### Steps

- [ ] **F2-B.1 寫 BrandColors.cs**

檔案：`Styles/BrandColors.cs`

```csharp
namespace FeatureWorkflow.VerifyDocxCli.Styles;

// OpenXML 顏色用 6-char hex（不含 #）
public static class BrandColors
{
    public const string IntumitBlue   = "1F4E79";
    public const string IntumitOrange = "ED7D31";
    public const string TechDarkBg    = "0D1B2A";
    public const string TechDarkAccent= "00C6A2";
    public const string SwissBlack    = "1A1A1A";
    public const string SwissGray     = "707070";
    public const string StatusPass    = "228B22";
    public const string StatusFail    = "CC0000";
    public const string StatusWarn    = "FF8C00";
    public const string StatusSkip    = "808080";
    public const string StatusManual  = "1F4E79";
}
```

- [ ] **F2-B.2 寫 IBrandStyle.cs**

檔案：`Styles/IBrandStyle.cs`

```csharp
namespace FeatureWorkflow.VerifyDocxCli.Styles;

public interface IBrandStyle
{
    string Id { get; }                  // "intumit" | "tech-dark" | "swiss"
    bool ShowLogo { get; }              // swiss = false
    string TitleColor { get; }          // hex
    string AccentColor { get; }
    string TableHeaderBg { get; }
    string TableHeaderFg { get; }
    string LatinFont { get; }           // 西文字型
    string CjkFont { get; }             // 中文字型
    string CoverDecorationHint { get; } // 給 CoverRenderer 用的提示字串：「orange-line」「code-bar」「none」
}

public static class BrandStyleFactory
{
    public static IBrandStyle Resolve(string id) => id switch
    {
        "intumit"   => new IntumitStyle(),
        "tech-dark" => new TechDarkStyle(),
        "swiss"     => new SwissStyle(),
        _ => throw new ArgumentException($"未知 style: {id}（可用：intumit | tech-dark | swiss）")
    };
}
```

- [ ] **F2-B.3 寫三個實作（每個 ≤ 25 行）**

`Styles/IntumitStyle.cs`：

```csharp
namespace FeatureWorkflow.VerifyDocxCli.Styles;

public sealed class IntumitStyle : IBrandStyle
{
    public string Id => "intumit";
    public bool ShowLogo => true;
    public string TitleColor => BrandColors.IntumitBlue;
    public string AccentColor => BrandColors.IntumitOrange;
    public string TableHeaderBg => BrandColors.IntumitBlue;
    public string TableHeaderFg => "FFFFFF";
    public string LatinFont => "Calibri";
    public string CjkFont => "Microsoft JhengHei"; // 微軟正黑體
    public string CoverDecorationHint => "orange-line";
}
```

`Styles/TechDarkStyle.cs`：

```csharp
namespace FeatureWorkflow.VerifyDocxCli.Styles;

public sealed class TechDarkStyle : IBrandStyle
{
    public string Id => "tech-dark";
    public bool ShowLogo => true;
    public string TitleColor => BrandColors.TechDarkAccent;
    public string AccentColor => BrandColors.TechDarkAccent;
    public string TableHeaderBg => BrandColors.TechDarkBg;
    public string TableHeaderFg => BrandColors.TechDarkAccent;
    public string LatinFont => "Consolas";
    public string CjkFont => "Microsoft JhengHei";
    public string CoverDecorationHint => "code-bar";
}
```

`Styles/SwissStyle.cs`：

```csharp
namespace FeatureWorkflow.VerifyDocxCli.Styles;

public sealed class SwissStyle : IBrandStyle
{
    public string Id => "swiss";
    public bool ShowLogo => false;
    public string TitleColor => BrandColors.SwissBlack;
    public string AccentColor => BrandColors.SwissGray;
    public string TableHeaderBg => "EEEEEE";
    public string TableHeaderFg => BrandColors.SwissBlack;
    public string LatinFont => "Helvetica Neue";
    public string CjkFont => "Microsoft JhengHei";
    public string CoverDecorationHint => "none";
}
```

- [ ] **F2-B.4 驗證 build**

```bash
cd ~/.claude/plugins/marketplaces/company-marketplace/plugins/feature-workflow/references/dotnet/verify-docx-cli
dotnet build
```

預期：0 errors。

---

## Phase F2-C: Document builder + 8 個 renderer + TOC

**目的**：把 VerifyReport + IBrandStyle 渲染成 docx。

**Files:**
- Create: `Rendering/DocumentBuilder.cs`
- Create: `Rendering/CoverRenderer.cs`
- Create: `Rendering/SignoffRenderer.cs`
- Create: `Rendering/EnvRenderer.cs`
- Create: `Rendering/SummaryRenderer.cs`
- Create: `Rendering/DetailRenderer.cs`
- Create: `Rendering/PendingRenderer.cs`
- Create: `Rendering/AppendixRenderer.cs`
- Create: `Rendering/TocInserter.cs`

### Steps

- [ ] **F2-C.1 寫 DocumentBuilder.cs（主流程）**

檔案：`Rendering/DocumentBuilder.cs`

```csharp
using DocumentFormat.OpenXml;
using DocumentFormat.OpenXml.Packaging;
using DocumentFormat.OpenXml.Wordprocessing;
using FeatureWorkflow.VerifyDocxCli.Markdown;
using FeatureWorkflow.VerifyDocxCli.Styles;

namespace FeatureWorkflow.VerifyDocxCli.Rendering;

public sealed class DocumentBuilder
{
    public void Build(VerifyReport report, IBrandStyle style, string? logoPath,
        DirectoryInfo? screenshotsDir, DirectoryInfo? evidenceDir, FileInfo outputFile)
    {
        using var doc = WordprocessingDocument.Create(outputFile.FullName,
            WordprocessingDocumentType.Document);
        var mainPart = doc.AddMainDocumentPart();
        mainPart.Document = new Document(new Body());
        var body = mainPart.Document.Body!;

        // 樣式定義（H1/H2/H3 OutlineLevel，TOC 必需）
        StyleRegistrar.Register(mainPart, style);

        new CoverRenderer(mainPart, style, logoPath).Render(body, report.Cover);
        new SignoffRenderer(style).Render(body, report.Cover.Author);
        TocInserter.Insert(body);
        new EnvRenderer(style).Render(body, report.Env);
        new SummaryRenderer(style).Render(body, report.Summary);
        new DetailRenderer(mainPart, style, screenshotsDir, evidenceDir).Render(body, report.Details);
        if (report.Pending.Count > 0)
            new PendingRenderer(style).Render(body, report.Pending);
        new AppendixRenderer(style).Render(body, report.Versions);

        // 最後一定要 sectPr（OpenXML 規定 body 最後一個 child）
        body.AppendChild(new SectionProperties(
            new PageSize { Width = 11906, Height = 16838 },           // A4
            new PageMargin { Top = 1440, Bottom = 1440, Left = 1440, Right = 1440, Header = 720, Footer = 720, Gutter = 0 }
        ));
    }
}
```

**注意 `StyleRegistrar`**：這個 helper 還沒寫。它要產 `styles.xml` 註冊 Heading1/2/3（含 `OutlineLevel`，TOC 才能 work）+ Normal + TableHeader 等 styles。在 F2-C.2 寫。

- [ ] **F2-C.2 寫 StyleRegistrar.cs（OpenXML styles.xml 註冊）**

檔案：`Rendering/StyleRegistrar.cs`

```csharp
using DocumentFormat.OpenXml;
using DocumentFormat.OpenXml.Packaging;
using DocumentFormat.OpenXml.Wordprocessing;
using FeatureWorkflow.VerifyDocxCli.Styles;

namespace FeatureWorkflow.VerifyDocxCli.Rendering;

public static class StyleRegistrar
{
    public static void Register(MainDocumentPart mainPart, IBrandStyle style)
    {
        var stylesPart = mainPart.AddNewPart<StyleDefinitionsPart>();
        stylesPart.Styles = new Styles(
            BuildHeadingStyle("Heading1", "標題 1", outlineLevel: 0, sizeHalfPt: 32, style),
            BuildHeadingStyle("Heading2", "標題 2", outlineLevel: 1, sizeHalfPt: 28, style),
            BuildHeadingStyle("Heading3", "標題 3", outlineLevel: 2, sizeHalfPt: 24, style),
            BuildNormalStyle(style),
            BuildCodeStyle(style)
        );
    }

    private static Style BuildHeadingStyle(string id, string name, int outlineLevel, int sizeHalfPt, IBrandStyle style)
    {
        return new Style(
            new StyleName { Val = name },
            new BasedOn { Val = "Normal" },
            new NextParagraphStyle { Val = "Normal" },
            new StyleParagraphProperties(
                new OutlineLevel { Val = outlineLevel },
                new SpacingBetweenLines { Before = "240", After = "120" }
            ),
            new StyleRunProperties(
                new RunFonts { Ascii = style.LatinFont, EastAsia = style.CjkFont },
                new Bold(),
                new FontSize { Val = sizeHalfPt.ToString() },
                new Color { Val = style.TitleColor }
            )
        ) { Type = StyleValues.Paragraph, StyleId = id };
    }

    private static Style BuildNormalStyle(IBrandStyle style)
    {
        return new Style(
            new StyleName { Val = "Normal" },
            new StyleRunProperties(
                new RunFonts { Ascii = style.LatinFont, EastAsia = style.CjkFont },
                new FontSize { Val = "20" } // 10pt
            )
        ) { Type = StyleValues.Paragraph, StyleId = "Normal", Default = true };
    }

    private static Style BuildCodeStyle(IBrandStyle style)
    {
        return new Style(
            new StyleName { Val = "Code" },
            new BasedOn { Val = "Normal" },
            new StyleRunProperties(
                new RunFonts { Ascii = "Consolas", EastAsia = style.CjkFont },
                new FontSize { Val = "16" } // 8pt
            )
        ) { Type = StyleValues.Paragraph, StyleId = "Code" };
    }
}
```

- [ ] **F2-C.3 寫 CoverRenderer.cs（含 Logo 嵌入）**

檔案：`Rendering/CoverRenderer.cs`

```csharp
using DocumentFormat.OpenXml.Packaging;
using DocumentFormat.OpenXml.Wordprocessing;
using FeatureWorkflow.VerifyDocxCli.Markdown;
using FeatureWorkflow.VerifyDocxCli.Styles;

namespace FeatureWorkflow.VerifyDocxCli.Rendering;

public sealed class CoverRenderer
{
    private readonly IBrandStyle _style;
    private readonly string? _logoPath;

    public CoverRenderer(IBrandStyle style, string? logoPath)
    {
        _style = style;
        _logoPath = logoPath;
    }

    public void Render(Body body, CoverInfo cover)
    {
        // 1. Logo（若 ShowLogo 且 logoPath 存在）
        if (_style.ShowLogo && _logoPath != null && File.Exists(_logoPath))
        {
            // 用 minimax-skills 的 ImageSamples 模式：AddImagePart + Drawing
            // 詳見：MiniMaxAIDocx.Core/Samples/ImageSamples.cs 第 ~80 行「InlineImage」範例
            body.AppendChild(BuildLogoParagraph(_logoPath));
        }

        // 2. 標題
        body.AppendChild(BuildTitle(cover.Project, sizeHalfPt: 48));
        body.AppendChild(BuildTitle($"{cover.Feature} — 驗收報告", sizeHalfPt: 32));

        // 3. 資訊表
        body.AppendChild(BuildInfoTable(cover));

        // 4. 裝飾線（intumit / tech-dark 各自不同）
        body.AppendChild(BuildDecorationLine());

        // 5. 分頁
        body.AppendChild(new Paragraph(new Run(new Break { Type = BreakValues.Page })));
    }

    // TODO 實作：
    // - BuildLogoParagraph: 用 OpenXML Drawing 嵌 PNG（參考 ImageSamples.cs）
    // - BuildTitle: 置中、用 style.TitleColor、字級 sizeHalfPt
    // - BuildInfoTable: 2 欄表（項目/值），帶風格表頭
    // - BuildDecorationLine: orange-line=橘底細表格列、code-bar=Consolas font 加 ">>>" 字串、none=空段
    private Paragraph BuildLogoParagraph(string logoPath) => throw new NotImplementedException();
    private Paragraph BuildTitle(string text, int sizeHalfPt) => throw new NotImplementedException();
    private Table BuildInfoTable(CoverInfo cover) => throw new NotImplementedException();
    private Paragraph BuildDecorationLine() => throw new NotImplementedException();
}
```

**實作 BuildLogoParagraph 時參考**：
- `~/.claude/plugins/marketplaces/minimax-skills/skills/minimax-docx/scripts/dotnet/MiniMaxAIDocx.Core/Samples/ImageSamples.cs` 的 `InlineImage` 範例
- Logo 嵌入時用 `Inline` (隨段落) 而非 `Anchor`（浮動）

**實作 BuildDecorationLine 時參考** `style.CoverDecorationHint`：
- `"orange-line"`：高度 60 EMU 的單列單格 table，背景填 `style.AccentColor`
- `"code-bar"`：段落內含 `Run` 字串 ">>> verification report >>>"，Consolas 字、`style.AccentColor`
- `"none"`：返回空段（`new Paragraph()`）

- [ ] **F2-C.4 寫 SignoffRenderer.cs**

檔案：`Rendering/SignoffRenderer.cs`

```csharp
using DocumentFormat.OpenXml.Wordprocessing;
using FeatureWorkflow.VerifyDocxCli.Styles;

namespace FeatureWorkflow.VerifyDocxCli.Rendering;

public sealed class SignoffRenderer
{
    private readonly IBrandStyle _style;
    public SignoffRenderer(IBrandStyle style) { _style = style; }

    public void Render(Body body, string defaultAuthor)
    {
        body.AppendChild(BuildH2("簽核"));
        body.AppendChild(BuildTable(new[]
        {
            new[] { "角色", "姓名", "簽章", "日期" },
            new[] { "製作人", defaultAuthor, "", "" },
            new[] { "審核人", "", "", "" },
            new[] { "客戶確認", "", "", "" },
        }));
    }

    // TODO 實作 helpers（與 CoverRenderer 共用 TableBuilder 抽出去也可以）
    private Paragraph BuildH2(string text) => throw new NotImplementedException();
    private Table BuildTable(string[][] rows) => throw new NotImplementedException();
}
```

**注意**：`BuildH2` 與 `BuildTable` 是所有 renderer 都會用到的共用 helper。建議實作時抽到 `Rendering/TableBuilder.cs` + `Rendering/ParagraphBuilder.cs`，避免每個 renderer 都重複。命名與簽章：

```csharp
// Rendering/ParagraphBuilder.cs
public static class ParagraphBuilder
{
    public static Paragraph Heading(string text, string styleId);  // styleId = "Heading1" | "Heading2" | "Heading3"
    public static Paragraph Body(string text);
    public static Paragraph Code(string text);
    public static Paragraph Empty();
}

// Rendering/TableBuilder.cs
public static class TableBuilder
{
    // headerBg/headerFg 用 style.TableHeaderBg / style.TableHeaderFg
    public static Table BuildSimple(string[][] rows, IBrandStyle style, bool firstRowIsHeader = true);
}
```

把這兩個 helper 補成 F2-C.5。

- [ ] **F2-C.5 抽 ParagraphBuilder + TableBuilder helpers**

按上面 signature 實作。Code 風格：
- `ParagraphBuilder.Heading` 套 `pStyle` 指向 `"Heading1"` / `"Heading2"` / `"Heading3"`，OutlineLevel 已由 StyleRegistrar 處理
- `TableBuilder.BuildSimple` header row 加 `Shading` 填 `style.TableHeaderBg`、Run color = `style.TableHeaderFg`

- [ ] **F2-C.6 寫 EnvRenderer.cs**

檔案：`Rendering/EnvRenderer.cs`

```csharp
using DocumentFormat.OpenXml.Wordprocessing;
using FeatureWorkflow.VerifyDocxCli.Markdown;
using FeatureWorkflow.VerifyDocxCli.Styles;

namespace FeatureWorkflow.VerifyDocxCli.Rendering;

public sealed class EnvRenderer
{
    private readonly IBrandStyle _style;
    public EnvRenderer(IBrandStyle style) { _style = style; }

    public void Render(Body body, EnvInfo env)
    {
        body.AppendChild(ParagraphBuilder.Heading("測試環境", "Heading1"));
        body.AppendChild(TableBuilder.BuildSimple(new[]
        {
            new[] { "項目", "說明" },
            new[] { "測試 URL", env.Url },
            new[] { "瀏覽器", env.Browser },
            new[] { "測試帳號角色", env.Role },
            new[] { "測試資料說明", env.DataDescription },
            new[] { "前置條件", env.Prerequisites },
        }, _style));
    }
}
```

- [ ] **F2-C.7 寫 SummaryRenderer.cs**

檔案：`Rendering/SummaryRenderer.cs`

```csharp
using DocumentFormat.OpenXml.Wordprocessing;
using FeatureWorkflow.VerifyDocxCli.Markdown;
using FeatureWorkflow.VerifyDocxCli.Styles;

namespace FeatureWorkflow.VerifyDocxCli.Rendering;

public sealed class SummaryRenderer
{
    private readonly IBrandStyle _style;
    public SummaryRenderer(IBrandStyle style) { _style = style; }

    public void Render(Body body, SummaryStats s)
    {
        body.AppendChild(ParagraphBuilder.Heading("驗收摘要", "Heading1"));
        body.AppendChild(TableBuilder.BuildSimple(new[]
        {
            new[] { "狀態", "數量" },
            new[] { "通過",       s.Pass.ToString() },
            new[] { "未通過",     s.Fail.ToString() },
            new[] { "略過",       s.Skip.ToString() },
            new[] { "待人工確認", s.Manual.ToString() },
        }, _style));

        // 結論段（粗體）
        var conclusion = new Paragraph(new Run(
            new RunProperties(new Bold()),
            new Text($"結論：{s.Conclusion}")));
        body.AppendChild(conclusion);
    }
}
```

- [ ] **F2-C.8 寫 DetailRenderer.cs（最複雜：截圖嵌入 + API 紀錄 + 截斷規則）**

檔案：`Rendering/DetailRenderer.cs`

實作要點：
1. 每個 `DetailItem` 是一個 H3 段
2. 結果用 status icon + 中文（✅ 通過 / ❌ 未通過 / ⏭️ 略過 / 🔍 待人工確認），文字色彩用 `BrandColors.Status*`
3. 操作步驟用 ordered list
4. API 紀錄：呼叫 `SensitiveDataMasker.Mask(headers)` 遮蔽 Cookie/Authorization，response > 20 行則切首尾 10 行 + 「... （省略 M 行，共 N 行）...」
5. 截圖：路徑 = `screenshotsDir / fileName`（fileName 從 `![desc](screenshots/foo.png)` 抽出），嵌入用 ImageSamples.cs 的 `InlineImage`，寬 5.5 in
6. 找不到截圖檔：插入文字段「（截圖不可用：{path}）」，不中斷

骨架：

```csharp
using DocumentFormat.OpenXml.Packaging;
using DocumentFormat.OpenXml.Wordprocessing;
using FeatureWorkflow.VerifyDocxCli.Markdown;
using FeatureWorkflow.VerifyDocxCli.Sanitization;
using FeatureWorkflow.VerifyDocxCli.Styles;

namespace FeatureWorkflow.VerifyDocxCli.Rendering;

public sealed class DetailRenderer
{
    private readonly IBrandStyle _style;
    private readonly DirectoryInfo? _screenshotsDir;
    private readonly DirectoryInfo? _evidenceDir;
    public DetailRenderer(IBrandStyle style, DirectoryInfo? screenshotsDir, DirectoryInfo? evidenceDir)
    {
        _style = style; _screenshotsDir = screenshotsDir; _evidenceDir = evidenceDir;
    }

    public void Render(Body body, IReadOnlyList<DetailItem> details)
    {
        body.AppendChild(ParagraphBuilder.Heading("驗收明細", "Heading1"));
        foreach (var d in details)
        {
            body.AppendChild(ParagraphBuilder.Heading($"驗收項目 {d.Number}：{d.Title}", "Heading2"));
            body.AppendChild(BuildResultParagraph(d.Status));
            body.AppendChild(BuildStepsList(d.HumanSteps));
            body.AppendChild(ParagraphBuilder.Body($"預期結果：{d.ExpectedResult}"));
            body.AppendChild(ParagraphBuilder.Body($"實際結果：{d.ActualResult}"));

            foreach (var call in d.ApiCalls)
                BuildApiCallBlock(body, call);

            foreach (var path in d.ScreenshotPaths)
                BuildScreenshot(body, path);
        }
    }

    private Paragraph BuildResultParagraph(DetailStatus status) => throw new NotImplementedException();
    private Paragraph BuildStepsList(IReadOnlyList<string> steps) => throw new NotImplementedException();
    private void BuildApiCallBlock(Body body, ApiCall call) => throw new NotImplementedException();
    private void BuildScreenshot(Body body, string relativePath) => throw new NotImplementedException();
}
```

實作 `BuildApiCallBlock` 的截斷規則：

```csharp
private void BuildApiCallBlock(Body body, ApiCall call)
{
    var maskedHeaders = SensitiveDataMasker.Mask(call.Headers);
    var headerLines = string.Join("\n", maskedHeaders.Select(kv => $"  {kv.Key}: {kv.Value}"));
    var requestText = $"請求：\n  {call.Method} {call.Url}\nHeaders:\n{headerLines}";

    var responseLines = call.ResponseBody.Split('\n');
    string responseText;
    if (responseLines.Length <= 20)
    {
        responseText = call.ResponseBody;
    }
    else
    {
        var head = string.Join("\n", responseLines.Take(10));
        var tail = string.Join("\n", responseLines.TakeLast(10));
        var omitted = responseLines.Length - 20;
        responseText = $"{head}\n\n... （省略 {omitted} 行，共 {responseLines.Length} 行）\n\n{tail}";
        if (call.EvidenceFileName != null)
            responseText += $"\n\n> 完整回應請見：evidence/{call.EvidenceFileName}";
    }

    body.AppendChild(ParagraphBuilder.Code(requestText));
    body.AppendChild(ParagraphBuilder.Code($"回應（HTTP {call.HttpStatus}）：\n{responseText}"));
}
```

實作 `BuildScreenshot`：

```csharp
private void BuildScreenshot(Body body, string relativePath)
{
    if (_screenshotsDir == null)
    {
        body.AppendChild(ParagraphBuilder.Body($"（截圖不可用：{relativePath}）"));
        return;
    }
    var fileName = Path.GetFileName(relativePath);
    var fullPath = Path.Combine(_screenshotsDir.FullName, fileName);
    if (!File.Exists(fullPath))
    {
        body.AppendChild(ParagraphBuilder.Body($"（截圖不可用：{relativePath}）"));
        return;
    }
    // 嵌入圖片，寬 5.5 inch = 5.5 * 914400 EMU = 5,029,200
    // 詳見 MiniMaxAIDocx.Core/Samples/ImageSamples.cs
    body.AppendChild(ImageInserter.InlineImage(body.Parent!.GetType()!.Assembly /* fix: 用 mainPart */, fullPath, widthEmu: 5_029_200));
}
```

**注意**：`ImageInserter` 還沒寫，需要從 mainPart 拿。修正：把 `MainDocumentPart mainPart` 傳進 `DetailRenderer` 建構子（用 `body.Parent` 反推太繞）。修正後簽章：

```csharp
public sealed class DetailRenderer
{
    private readonly MainDocumentPart _mainPart;
    // ...
    public DetailRenderer(MainDocumentPart mainPart, IBrandStyle style,
        DirectoryInfo? screenshotsDir, DirectoryInfo? evidenceDir) { /* ... */ }
}
```

DocumentBuilder 對應改：

```csharp
new DetailRenderer(mainPart, style, screenshotsDir, evidenceDir).Render(body, report.Details);
```

CoverRenderer 同理（要嵌 Logo）：

```csharp
public CoverRenderer(MainDocumentPart mainPart, IBrandStyle style, string? logoPath) { /* ... */ }
```

DocumentBuilder：

```csharp
new CoverRenderer(mainPart, style, logoPath).Render(body, report.Cover);
```

- [ ] **F2-C.9 寫 ImageInserter.cs**

檔案：`Rendering/ImageInserter.cs`

實作要點：
1. `InlineImage(MainDocumentPart mainPart, string imagePath, long widthEmu) → Paragraph`
2. 內部 `mainPart.AddImagePart(ImagePartType.Png)` → `relId = mainPart.GetIdOfPart(imagePart)`
3. 用 stream 寫進 imagePart
4. 構造 `Drawing` 包 `Inline` 包 `Graphic`，r:embed = relId
5. 高度按原圖比例算

直接從 `~/.claude/plugins/marketplaces/minimax-skills/skills/minimax-docx/scripts/dotnet/MiniMaxAIDocx.Core/Samples/ImageSamples.cs` 抄 `InlineImage` 範例段（~80-150 行），改成 static method 形態。

- [ ] **F2-C.10 寫 PendingRenderer.cs**

檔案：`Rendering/PendingRenderer.cs`

```csharp
using DocumentFormat.OpenXml.Wordprocessing;
using FeatureWorkflow.VerifyDocxCli.Markdown;
using FeatureWorkflow.VerifyDocxCli.Styles;

namespace FeatureWorkflow.VerifyDocxCli.Rendering;

public sealed class PendingRenderer
{
    private readonly IBrandStyle _style;
    public PendingRenderer(IBrandStyle style) { _style = style; }

    public void Render(Body body, IReadOnlyList<PendingItem> items)
    {
        body.AppendChild(ParagraphBuilder.Heading("待處理事項", "Heading1"));
        var rows = new List<string[]> { new[] { "#", "驗收條件", "狀態", "建議處理方式" } };
        foreach (var p in items)
            rows.Add(new[] { p.Number.ToString(), p.Title, StatusToText(p.Status), p.Suggestion });
        body.AppendChild(TableBuilder.BuildSimple(rows.ToArray(), _style));
    }

    private static string StatusToText(DetailStatus s) => s switch
    {
        DetailStatus.Fail => "未通過",
        DetailStatus.Manual => "待人工確認",
        _ => s.ToString()
    };
}
```

- [ ] **F2-C.11 寫 AppendixRenderer.cs**

檔案：`Rendering/AppendixRenderer.cs`

```csharp
using DocumentFormat.OpenXml.Wordprocessing;
using FeatureWorkflow.VerifyDocxCli.Markdown;
using FeatureWorkflow.VerifyDocxCli.Styles;

namespace FeatureWorkflow.VerifyDocxCli.Rendering;

public sealed class AppendixRenderer
{
    private readonly IBrandStyle _style;
    public AppendixRenderer(IBrandStyle style) { _style = style; }

    public void Render(Body body, IReadOnlyList<AppendixVersionEntry> versions)
    {
        body.AppendChild(ParagraphBuilder.Heading("附錄", "Heading1"));
        body.AppendChild(ParagraphBuilder.Heading("版本紀錄", "Heading2"));

        var rows = new List<string[]> { new[] { "日期", "版本", "說明" } };
        foreach (var v in versions)
            rows.Add(new[] { v.Date, v.Version, v.Description });
        body.AppendChild(TableBuilder.BuildSimple(rows.ToArray(), _style));

        body.AppendChild(ParagraphBuilder.Heading("參考文件", "Heading2"));
        body.AppendChild(ParagraphBuilder.Body("- 技術規格書：.spec/{slug}/spec.md"));
        body.AppendChild(ParagraphBuilder.Body("- 驗證技術紀錄：.spec/{slug}/verify.md"));
    }
}
```

- [ ] **F2-C.12 寫 TocInserter.cs（python-docx 沒有的關鍵功能）**

檔案：`Rendering/TocInserter.cs`

```csharp
using DocumentFormat.OpenXml;
using DocumentFormat.OpenXml.Wordprocessing;

namespace FeatureWorkflow.VerifyDocxCli.Rendering;

public static class TocInserter
{
    // 插入「目錄」標題 + TOC complex field
    // 開啟 docx 時 Word 會 prompt「是否更新目錄？」
    public static void Insert(Body body)
    {
        body.AppendChild(ParagraphBuilder.Heading("目錄", "Heading1"));

        // TOC field 三段：begin / instruction / separate / 暫存值 / end
        var p = new Paragraph();
        p.AppendChild(new Run(new FieldChar { FieldCharType = FieldCharValues.Begin }));
        p.AppendChild(new Run(new FieldCode(@" TOC \o ""1-3"" \h \z \u ") { Space = SpaceProcessingModeValues.Preserve }));
        p.AppendChild(new Run(new FieldChar { FieldCharType = FieldCharValues.Separate }));
        p.AppendChild(new Run(new Text("(請在 Word 開啟後按 F9 或右鍵『更新功能變數』來填入目錄)")));
        p.AppendChild(new Run(new FieldChar { FieldCharType = FieldCharValues.End }));
        body.AppendChild(p);
        body.AppendChild(new Paragraph(new Run(new Break { Type = BreakValues.Page })));
    }
}
```

**注意**：完整 `TOC` field 寫法可參考 `~/.claude/plugins/marketplaces/minimax-skills/skills/minimax-docx/scripts/dotnet/MiniMaxAIDocx.Core/Samples/FieldAndTocSamples.cs`。

- [ ] **F2-C.13 接到 Program.cs**

修改 `Program.cs` 的 `SetAction`，渲染呼叫：

```csharp
// 用 Logo 偵測（F3 會擴充）
var logoPath = parseResult.GetValue(logoOpt)?.FullName; // 暫時只支援明示

new DocumentBuilder().Build(report, BrandStyleFactory.Resolve(style),
    logoPath, parseResult.GetValue(screenshotsOpt), parseResult.GetValue(evidenceOpt), output);

Console.WriteLine($"[verify-docx-cli] ✅ 已產出 {output.FullName}");
```

把暫時的 `Console.WriteLine` 行刪掉。

- [ ] **F2-C.14 第一份 docx smoke**

```bash
cd ~/.claude/plugins/marketplaces/company-marketplace/plugins/feature-workflow/references/dotnet/verify-docx-cli
dotnet run -- \
  --verify ../../../skills/plan-verify/examples/verify-report-sample.md \
  --output /tmp/smoke-intumit.docx \
  --style intumit \
  --cover '{"project":"測試專案","feature":"範例功能","author":"cheng","date":"2026-05-26","company":"Intumit","version":"v1.0"}'

# 開 docx 視覺驗證（macOS）
open /tmp/smoke-intumit.docx
```

預期：docx 開啟有封面、簽核、TOC field（按 F9 後出現目錄）、環境表、摘要表、明細、附錄。Logo 暫時沒有（F3 才接），不影響本 phase。

---

## Phase F2-D: 敏感資訊遮蔽 + XSD 驗證

**Files:**
- Create: `Sanitization/SensitiveDataMasker.cs`
- Create: `Validation/XsdGateCheck.cs`

### Steps

- [ ] **F2-D.1 寫 SensitiveDataMasker.cs**

檔案：`Sanitization/SensitiveDataMasker.cs`

按 word-report.md 規則：

```csharp
namespace FeatureWorkflow.VerifyDocxCli.Sanitization;

public static class SensitiveDataMasker
{
    public static Dictionary<string, string> Mask(IReadOnlyDictionary<string, string> headers)
    {
        var result = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
        foreach (var (k, v) in headers)
        {
            result[k] = k.ToLowerInvariant() switch
            {
                "cookie"        => MaskCookie(v),
                "authorization" => MaskAuthorization(v),
                "x-api-key"     => MaskShortToken(v),
                "x-token"       => MaskShortToken(v),
                _ => v
            };
        }
        return result;
    }

    private static string MaskCookie(string v) =>
        v.Length <= 8 ? "****" : $"{v[..4]}****{v[^4..]}";

    private static string MaskAuthorization(string v)
    {
        var parts = v.Split(' ', 2);
        if (parts.Length < 2) return MaskShortToken(v);
        var scheme = parts[0];
        var token = parts[1];
        return token.Length <= 4 ? $"{scheme} ****" : $"{scheme} {token[..4]}****";
    }

    private static string MaskShortToken(string v) =>
        v.Length <= 4 ? "****" : $"{v[..4]}****";
}
```

- [ ] **F2-D.2 寫 XsdGateCheck.cs（呼叫 Core 的 XsdValidator）**

檔案：`Validation/XsdGateCheck.cs`

```csharp
namespace FeatureWorkflow.VerifyDocxCli.Validation;

public static class XsdGateCheck
{
    // 回傳 true = 通過，false = 失敗（並印錯誤到 stderr）
    public static bool Check(string docxPath)
    {
        try
        {
            // MiniMaxAIDocx.Core.Validation.XsdValidator 用法
            // 詳見 ~/.claude/plugins/marketplaces/minimax-skills/.../Core/Validation/XsdValidator.cs
            var result = MiniMaxAIDocx.Core.Validation.XsdValidator.Validate(docxPath);
            if (result.IsValid) return true;
            Console.Error.WriteLine($"[verify-docx-cli] XSD 驗證失敗：{result.Errors.Count} 個錯誤");
            foreach (var err in result.Errors.Take(10))
                Console.Error.WriteLine($"  - {err}");
            return false;
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine($"[verify-docx-cli] XSD 驗證例外：{ex.Message}");
            return false;
        }
    }
}
```

**注意**：上面假設了 `XsdValidator.Validate(string) → ValidationResult { IsValid, Errors }`。實際 API 名與簽章請打開 `~/.claude/plugins/marketplaces/minimax-skills/skills/minimax-docx/scripts/dotnet/MiniMaxAIDocx.Core/Validation/XsdValidator.cs` 確認後對齊。

- [ ] **F2-D.3 接到 Program.cs**

在 `Build()` 完成後：

```csharp
if (!Validation.XsdGateCheck.Check(output.FullName))
{
    Console.Error.WriteLine("[verify-docx-cli] ⚠️  docx 已產出但 XSD 驗證失敗，請檢查上方錯誤訊息");
    return 1;
}
Console.WriteLine($"[verify-docx-cli] ✅ XSD 驗證通過");
return 0;
```

- [ ] **F2-D.4 smoke 驗證 XSD 通過**

```bash
cd ~/.claude/plugins/marketplaces/company-marketplace/plugins/feature-workflow/references/dotnet/verify-docx-cli
dotnet run -- \
  --verify ../../../skills/plan-verify/examples/verify-report-sample.md \
  --output /tmp/smoke-xsd.docx \
  --style intumit \
  --cover '{"project":"X","feature":"Y","author":"Z","date":"2026-05-26","company":"Intumit","version":"v1.0"}'
echo "退出碼：$?"
```

預期：stdout 含「✅ XSD 驗證通過」，退出碼 0。

---

## Phase F3: Logo 三層偵測 + 內建 PNG

**Files:**
- Modify: `Program.cs`（補 Logo 偵測函式）
- Create: `assets/intumit-logo.png`（從 intumit.com 下載 + optipng 壓縮）

### Steps

- [ ] **F3.1 下載 Logo PNG**

```bash
cd ~/.claude/plugins/marketplaces/company-marketplace/plugins/feature-workflow/references/dotnet/verify-docx-cli
mkdir -p assets
curl -fsSL "https://www.intumit.com/wp-content/uploads/logo-Intumit.png" -o assets/intumit-logo.png
ls -lh assets/intumit-logo.png
```

預期：檔案存在。**如果 > 100KB**，跑下一步 optipng。

- [ ] **F3.2 optipng 壓縮（若需要）**

```bash
which optipng || brew install optipng
optipng -o7 ~/.claude/plugins/marketplaces/company-marketplace/plugins/feature-workflow/references/dotnet/verify-docx-cli/assets/intumit-logo.png
ls -lh ~/.claude/plugins/marketplaces/company-marketplace/plugins/feature-workflow/references/dotnet/verify-docx-cli/assets/intumit-logo.png
```

預期：壓縮後 < 100KB。

- [ ] **F3.3 加 LogoResolver.cs**

檔案：`Program.cs` 同目錄新增 `LogoResolver.cs`

```csharp
namespace FeatureWorkflow.VerifyDocxCli;

public static class LogoResolver
{
    public static string? Resolve(string? cliLogo, string styleId)
    {
        // 1. CLI 參數
        if (cliLogo != null && File.Exists(cliLogo)) return cliLogo;

        // 2. 使用者覆寫位置
        var userOverride = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.UserProfile),
            ".claude", "feature-workflow", "assets", "intumit-logo.png");
        if (File.Exists(userOverride)) return userOverride;

        // 3. Plugin 內建
        var assemblyDir = Path.GetDirectoryName(typeof(LogoResolver).Assembly.Location)!;
        var builtin = Path.Combine(assemblyDir, "assets", "intumit-logo.png");
        if (File.Exists(builtin)) return builtin;

        // 4. swiss style 不需要 logo → null 合法；其他 style 缺 logo → fail
        if (styleId == "swiss") return null;

        throw new FileNotFoundException(
            $"找不到 logo。請放置 PNG 到下列任一位置：\n" +
            $"  1. --logo {{path}} CLI 參數\n" +
            $"  2. {userOverride}\n" +
            $"  3. {builtin}");
    }
}
```

- [ ] **F3.4 改 Program.cs 用 LogoResolver**

```csharp
var logoPath = LogoResolver.Resolve(
    parseResult.GetValue(logoOpt)?.FullName,
    style);
```

- [ ] **F3.5 三套 style smoke**

```bash
cd ~/.claude/plugins/marketplaces/company-marketplace/plugins/feature-workflow/references/dotnet/verify-docx-cli
SAMPLE=../../../skills/plan-verify/examples/verify-report-sample.md
COVER='{"project":"測試","feature":"範例","author":"cheng","date":"2026-05-26","company":"Intumit","version":"v1.0"}'

dotnet run -- --verify $SAMPLE --output /tmp/smoke-intumit.docx --style intumit --cover "$COVER"
dotnet run -- --verify $SAMPLE --output /tmp/smoke-techdark.docx --style tech-dark --cover "$COVER"
dotnet run -- --verify $SAMPLE --output /tmp/smoke-swiss.docx --style swiss --cover "$COVER"

ls -lh /tmp/smoke-*.docx
open /tmp/smoke-*.docx
```

預期：三份 docx 都產出，intumit + tech-dark 有 Logo、swiss 無。每份按 F9 都能更新 TOC。

---

## Phase C1: Commit 1 (F1 + F2 + F3)

- [ ] **C1.1 stage 新檔**

```bash
cd ~/.claude/plugins/marketplaces/company-marketplace
git add plugins/feature-workflow/references/dotnet/
```

- [ ] **C1.2 確認 stage 內容**

```bash
git status -s
git diff --staged --stat
```

預期：只有 `plugins/feature-workflow/references/dotnet/verify-docx-cli/` 下的檔案 + assets/intumit-logo.png。**不能** stage `bin/` `obj/`（被 .gitignore 擋掉）。

- [ ] **C1.3 commit**

```bash
git commit -m "$(cat <<'EOF'
feat(plan-verify): 新增 verify-docx-cli .NET 子專案與 logo 三層偵測

新建 references/dotnet/verify-docx-cli/ multi-target net8.0;net10.0 子專案，
透過 ProjectReference 共用 minimax-docx Core 的 OpenXML helper。

子專案功能：
- 解析 verify.md 七段式（封面/簽核/環境/摘要/明細/待處理/附錄）
- 三套 brand style（intumit / tech-dark / swiss）
- TOC field（python-docx 不支援）
- 截圖嵌入 + 敏感資訊遮蔽（Cookie/Auth/API Key）
- API response > 20 行自動截斷首尾 10 + 引用 evidence
- XSD 驗證 gate-check

ProjectReference 解析：$(MinimaxCorePath) env var override + $(HOME) fallback
Logo 三層偵測：--logo > $HOME/.claude/feature-workflow/assets/ > plugin 內建
EOF
)"
```

---

## Phase F4: Preflight word-report.md 10.0c

**Files:**
- Modify: `plugins/feature-workflow/skills/plan-verify/phases/word-report.md`（新增 step 10.0c，10.0b 之前）

### Steps

- [ ] **F4.1 讀現況**

```bash
sed -n '27,65p' ~/.claude/plugins/marketplaces/company-marketplace/plugins/feature-workflow/skills/plan-verify/phases/word-report.md
```

對照 spec section 6 的 preflight 邏輯。

- [ ] **F4.2 在 10.0a 之前插入 step 10.0c（注意：spec 寫 10.0c 但建議用 10.0aa 或調整編號避免和 10.0a 衝突）**

實作建議：把 spec 的「10.0c」改成編號 **「10.-1 環境偵測」**（在 10.0a 之前），語義更清楚。或維持 spec 編號用「10.0c 環境偵測（在 10.0a 之前執行）」。實作時擇一即可，本 plan 用後者。

在 `phases/word-report.md` step 10.0a 之前新增段落：

```markdown
#### 10.0c 環境偵測（在 10.0a 選風格之前）

執行以下偵測決定 `report_engine`：

```bash
# 偵測 .NET SDK
if ! command -v dotnet &>/dev/null; then
  report_engine="python-docx-pending"
elif [ "$(dotnet --version | cut -d. -f1)" -lt 8 ]; then
  report_engine="python-docx-pending"
else
  # 偵測 minimax-skills Core
  CORE_PATH="${MinimaxCorePath:-$HOME/.claude/plugins/marketplaces/minimax-skills/skills/minimax-docx/scripts/dotnet/MiniMaxAIDocx.Core/MiniMaxAIDocx.Core.csproj}"
  if [ ! -f "$CORE_PATH" ]; then
    report_engine="minimax-skills-missing"
  else
    report_engine="minimax-docx"
  fi
fi
```

若 `report_engine = minimax-skills-missing`，使用 `AskUserQuestion` 詢問：

| 選項 | 動作 |
|-----|------|
| A) 安裝 minimax-skills plugin | 提示在 Claude Code 內執行 `/plugin install minimax-skills`，等使用者確認後重跑偵測 |
| B) 已從別處安裝 | 詢問 `MinimaxCorePath` 路徑，設定 env var 後重跑偵測 |
| C) 改用 python-docx fallback | 設 `report_engine="python-docx"` 進入 10.4b |
| D) 跳過 Word 報告 | 結束流程 |

若 `report_engine = python-docx-pending`，沿用既有 10.0b 流程（A/B/C 選項）。
```

- [ ] **F4.3 驗證 markdown 結構**

```bash
grep -n "^####" ~/.claude/plugins/marketplaces/company-marketplace/plugins/feature-workflow/skills/plan-verify/phases/word-report.md | head -20
```

預期：看到 `10.0a` `10.0b` `10.0c`（順序可能 10.0c 在 10.0a 之前），有插入 `10.0c`。

---

## Phase F5: 改寫 word-report.md step 10.4a

**Files:**
- Modify: `plugins/feature-workflow/skills/plan-verify/phases/word-report.md`（L287-294 改寫）

### Steps

- [ ] **F5.1 找定位**

```bash
grep -n "10.4a\|使用 minimax-docx" ~/.claude/plugins/marketplaces/company-marketplace/plugins/feature-workflow/skills/plan-verify/phases/word-report.md
```

- [ ] **F5.2 用 Edit 替換 L287-294 抽象描述為具體指令**

舊段（L287-294）：

```
#### 10.4a 使用 minimax-docx 產出（report_engine = minimax-docx）

```
使用 `/minimax-docx` Skill 產出：
- 輸入：AI 組裝的 Markdown 報告內容
- 輸出：`.spec/{slug}/verify-report.docx`
- 含：封面、簽核表、環境說明、摘要、逐條驗證明細（含截圖嵌入）、待處理事項、附錄
```
```

新段：

```
#### 10.4a 使用 minimax-docx 產出（report_engine = minimax-docx）

呼叫 plugin 內建的 verify-docx-cli .NET 子專案：

```bash
# 1. 解析 plugin 路徑
PLUGIN_DIR="$HOME/.claude/plugins/marketplaces/company-marketplace/plugins/feature-workflow"
CLI_DIR="$PLUGIN_DIR/references/dotnet/verify-docx-cli"

# 2. 解析 Logo（三層偵測，CLI 內部也會做一次）
if [ -n "$USER_LOGO" ]; then
  LOGO="$USER_LOGO"
elif [ -f "$HOME/.claude/feature-workflow/assets/intumit-logo.png" ]; then
  LOGO="$HOME/.claude/feature-workflow/assets/intumit-logo.png"
else
  LOGO="$CLI_DIR/assets/intumit-logo.png"
fi

# 3. 首次執行 UX 提示（dotnet restore + build 約 1-2 分鐘）
if [ ! -d "$CLI_DIR/bin" ]; then
  echo "⏳ 首次產出 Word 報告需要 build .NET 子專案（約 1-2 分鐘）..."
fi

# 4. 跑 verify-docx-cli
dotnet run --project "$CLI_DIR" -- \
  --verify .spec/{slug}/verify.md \
  --screenshots .spec/{slug}/screenshots/ \
  --evidence .spec/{slug}/evidence/ \
  --output .spec/{slug}/verify-report.docx \
  --style {style} \
  --logo "$LOGO" \
  --cover '{"project":"{project}","feature":"{feature}","author":"{author}","date":"{date}","company":"{company}","version":"{version}"}'
```

優於 python-docx 之處：
- TOC field：Word 開啟時 prompt 自動更新目錄
- XSD 驗證：確保 docx 結構正確
- 精確控制 multi-section header/footer

**首次執行**：dotnet restore + build 約需 1-2 分鐘（拉 OpenXML / Markdig），後續 incremental build 只需數秒。
```

---

## Phase F6: 改 plan-verify SKILL.md 引擎偵測

**Files:**
- Modify: `plugins/feature-workflow/skills/plan-verify/SKILL.md`

### Steps

- [ ] **F6.1 找引擎偵測段**

```bash
grep -n "report_engine\|minimax-docx\|claude-company" ~/.claude/plugins/marketplaces/company-marketplace/plugins/feature-workflow/skills/plan-verify/SKILL.md | head -20
```

- [ ] **F6.2 在引擎偵測段補 MinimaxCorePath env var + Core 存在性檢查說明**

找到「引擎偵測」相關段落（用 F6.1 結果定位），用 Edit 加上：

```markdown
**引擎偵測**：

詳見 phases/word-report.md step 10.0c。偵測順序：

1. 偵測 `dotnet` 指令存在且 SDK ≥ 8.0
2. 偵測 `MiniMaxAIDocx.Core.csproj` 存在於：
   - `$MinimaxCorePath`（env var override，給 plugin 路徑非預設時用）
   - `$HOME/.claude/plugins/marketplaces/minimax-skills/skills/minimax-docx/scripts/dotnet/MiniMaxAIDocx.Core/MiniMaxAIDocx.Core.csproj`（fallback）
3. 兩者皆通過 → `report_engine = minimax-docx`
4. dotnet 缺失 → `python-docx-pending`
5. Core 缺失 → 詢問使用者（安裝 / 設 env var / 改用 python-docx / 跳過）
```

- [ ] **F6.3 處理 L527 路徑（F7 一起做時可跳過，但建議現在改保證一致性）**

L527 原文：

```
- **封面資訊快取**：`report-config.md` 儲存於 `~/.claude-company/feature-workflow/` 下，跨專案共用（公司名稱、作者）。首次產出報告時建立。
```

改成：

```
- **封面資訊快取**：`report-config.md` 儲存於 `~/.claude/feature-workflow/` 下，跨專案共用（公司名稱、作者）。首次產出報告時建立。
```

---

## Phase C2: Commit 2 (F4 + F5 + F6)

- [ ] **C2.1 stage**

```bash
cd ~/.claude/plugins/marketplaces/company-marketplace
git add plugins/feature-workflow/skills/plan-verify/SKILL.md
git add plugins/feature-workflow/skills/plan-verify/phases/word-report.md
```

- [ ] **C2.2 commit**

```bash
git commit -m "$(cat <<'EOF'
feat(plan-verify): 整合 verify-docx-cli 到 word-report 流程

- word-report.md 新增 step 10.0c 環境偵測（dotnet + minimax-skills Core 偵測）
- word-report.md step 10.4a 從抽象描述「使用 /minimax-docx Skill」改成
  具體 dotnet run 指令，含三層 Logo 偵測與首次 build UX 提示
- SKILL.md 引擎偵測段補上 MinimaxCorePath env var 與 Core 存在性檢查說明
- SKILL.md L527 連帶把 ~/.claude-company/feature-workflow/ 改為 ~/.claude/feature-workflow/
EOF
)"
```

---

## Phase F7: Config 路徑統一

**範圍**（spec 原列 5 處 + grep 新增 9 處，共 ~14 處改動）：

| 檔案 | 行 | 性質 |
|------|---|------|
| `references/config-resolver.md` | L9, L22, L30, L31, L35, L36 | 階層式新格式路徑 |
| `references/config.template.md` | L3 | 階層式新格式路徑 |
| `references/prerequisites.md` | L125-130 | 階層式新格式路徑（注意 L125, 129 是舊單一檔案格式，不動！只動 L127, 128 是新階層式）|
| `skills/plan-verify/SKILL.md` | L527 | F6 已處理 ✓ |
| `skills/plan-verify/phases/word-report.md` | L84 | 階層式 |
| `skills/plan-setup/SKILL.md` | L27, L28, L34, L35, L198 | 階層式 + 邏輯改寫（刪除「公司環境優先」分支）|
| `skills/plan-stack/SKILL.md` | L98 | 階層式 |
| `skills/plan-close/SKILL.md` | L19 | 注意：這行是 `bug-workflow-config.md` 舊單一檔案，**不動** |
| `skills/plan-start/SKILL.md` | L18 | 注意：這行是 `bug-workflow-config.md` 舊單一檔案，**不動** |
| `README.md` | L297 | 階層式 |

**規則**：
- 只改新階層式路徑 `~/.claude-company/feature-workflow/` → `~/.claude/feature-workflow/`
- **不動**舊單一檔案格式 `~/.claude-company/feature-workflow-config.md` 或 `~/.claude-company/bug-workflow-config.md`（這是另一層相容問題，超出 F7 scope）
- 刪除「公司環境優先 / 個人環境備用」的階層描述，改成「統一位置」
- 在 `config-resolver.md` 加遷移段落

### Steps

- [ ] **F7.1 改 config-resolver.md**

L9 區塊（目錄結構）：

```diff
-~/.claude-company/feature-workflow/     # 公司環境（優先）
+~/.claude/feature-workflow/             # 統一位置
```

L22：

```diff
-備用路徑：`~/.claude/feature-workflow/`（個人環境）
+
```

（整行刪除）

L30, L31（解析優先順序）：

```diff
-1. `~/.claude-company/feature-workflow/config.md`
-2. `~/.claude/feature-workflow/config.md`
+1. `~/.claude/feature-workflow/config.md`
```

L35, L36（舊格式 fallback）：

```diff
-3. `~/.claude-company/feature-workflow-config.md`（舊單一檔案）
-4. `~/.claude/feature-workflow-config.md`（舊單一檔案）
+2. `~/.claude/feature-workflow-config.md`（舊單一檔案，向下相容）
```

**新增**「舊路徑遷移」段落（在「解析優先順序」之後）：

```markdown
### 從 `~/.claude-company/` 遷移到 `~/.claude/`

舊版（2026-05 前）優先使用 `~/.claude-company/`。若 plan-* skill 偵測到舊路徑存在但新路徑不存在，會提示：

```
⚠️  偵測到舊版 config 路徑 ~/.claude-company/feature-workflow/，新版統一改用 ~/.claude/feature-workflow/。

建議手動執行：
  mv ~/.claude-company/feature-workflow ~/.claude/feature-workflow

執行完成後重跑 plan-* skill。
```

不會自動 `mv`，避免破壞使用者既有 setup。
```

- [ ] **F7.2 改 config.template.md L3**

```diff
-此目錄由 `/plan-setup` 自動產生，儲存於 `~/.claude-company/feature-workflow/`。
+此目錄由 `/plan-setup` 自動產生，儲存於 `~/.claude/feature-workflow/`。
```

- [ ] **F7.3 改 prerequisites.md（只動新階層式那兩行）**

```bash
sed -n '120,135p' ~/.claude/plugins/marketplaces/company-marketplace/plugins/feature-workflow/references/prerequisites.md
```

只改 L127, L128（新階層式）：

```diff
-3. `~/.claude-company/feature-workflow/config.md`（新階層式格式）
-4. `~/.claude/feature-workflow/config.md`（新階層式格式）
+3. `~/.claude/feature-workflow/config.md`（新階層式格式）
```

把兩行合併成一行（因為現在只剩一個位置）。順手把後續編號 5→4, 6→5。

- [ ] **F7.4 改 word-report.md L84**

```diff
-**`report-config.md` 位置**：`~/.claude-company/feature-workflow/report-config.md`
+**`report-config.md` 位置**：`~/.claude/feature-workflow/report-config.md`
```

- [ ] **F7.5 改 plan-setup/SKILL.md**

```bash
grep -n "claude-company\|claude/feature-workflow" ~/.claude/plugins/marketplaces/company-marketplace/plugins/feature-workflow/skills/plan-setup/SKILL.md
```

L27, L28（檢查順序）：

```diff
-1. 先檢查 `~/.claude-company/feature-workflow/config.md`（新階層式格式）
-2. 再檢查 `~/.claude/feature-workflow/config.md`（新階層式格式）
+1. 檢查 `~/.claude/feature-workflow/config.md`（新階層式格式）
```

L34, L35（建立邏輯）：

```diff
-   - `~/.claude-company/` 目錄存在 → 使用 `~/.claude-company/feature-workflow/`
-   - 否則 → 使用 `~/.claude/feature-workflow/`
+   - 統一使用 `~/.claude/feature-workflow/`（若使用者已有 `~/.claude-company/feature-workflow/`，提示手動 mv 遷移）
```

L44（bug-workflow 區塊）：**不動**（這行是舊單一檔案格式）。

L198（範例輸出路徑）：

```diff
-設定目錄：~/.claude-company/feature-workflow/
+設定目錄：~/.claude/feature-workflow/
```

- [ ] **F7.6 改 plan-stack/SKILL.md L98**

```diff
-  技術棧檔案：~/.claude-company/feature-workflow/stacks/{id}.md
+  技術棧檔案：~/.claude/feature-workflow/stacks/{id}.md
```

- [ ] **F7.7 改 README.md**

```bash
grep -n "claude-company" ~/.claude/plugins/marketplaces/company-marketplace/plugins/feature-workflow/README.md
```

L297 區塊改 `~/.claude-company/feature-workflow/` → `~/.claude/feature-workflow/`。其他若提到舊單一檔案，**不動**。

- [ ] **F7.8 全文 grep 確認沒漏網**

```bash
cd ~/.claude/plugins/marketplaces/company-marketplace/plugins/feature-workflow
grep -rn "\.claude-company/feature-workflow/" --include="*.md" .
```

預期：只剩下 `bug-workflow-config.md` `feature-workflow-config.md` 兩種舊單一檔案格式的引用（這是 scope 外的），其他都已改。如果還有新階層式格式漏網，補改。

- [ ] **F7.9 plan-close/SKILL.md L19 與 plan-start/SKILL.md L18 確認不動**

```bash
sed -n '17,20p' ~/.claude/plugins/marketplaces/company-marketplace/plugins/feature-workflow/skills/plan-close/SKILL.md
sed -n '16,20p' ~/.claude/plugins/marketplaces/company-marketplace/plugins/feature-workflow/skills/plan-start/SKILL.md
```

確認這兩處是「`bug-workflow-config.md` 舊單一檔案」格式，不是新階層式，**不改**。

---

## Phase C3: Commit 3 (F7)

- [ ] **C3.1 stage**

```bash
cd ~/.claude/plugins/marketplaces/company-marketplace
git add plugins/feature-workflow/references/config-resolver.md
git add plugins/feature-workflow/references/config.template.md
git add plugins/feature-workflow/references/prerequisites.md
git add plugins/feature-workflow/skills/plan-verify/phases/word-report.md
git add plugins/feature-workflow/skills/plan-setup/SKILL.md
git add plugins/feature-workflow/skills/plan-stack/SKILL.md
git add plugins/feature-workflow/README.md
```

- [ ] **C3.2 確認**

```bash
git status -s
git diff --staged | head -100
```

預期：只有 config 路徑相關改動。

- [ ] **C3.3 commit**

```bash
git commit -m "$(cat <<'EOF'
refactor(feature-workflow): 統一 config 路徑為 ~/.claude/feature-workflow/

把所有「新階層式」config 路徑從 ~/.claude-company/feature-workflow/
統一改為 ~/.claude/feature-workflow/，並在 config-resolver.md 加遷移說明。

不動「舊單一檔案」格式（feature-workflow-config.md / bug-workflow-config.md），
那是獨立的向下相容議題，超出本次 scope。

影響檔案：
- references/config-resolver.md（含新增遷移段落）
- references/config.template.md
- references/prerequisites.md
- README.md
- skills/plan-verify/phases/word-report.md
- skills/plan-setup/SKILL.md（含「公司環境優先」邏輯刪除）
- skills/plan-stack/SKILL.md
EOF
)"
```

---

## Phase F8: README

**Files:**
- Create: `plugins/feature-workflow/references/dotnet/verify-docx-cli/README.md`

### Steps

- [ ] **F8.1 寫 README.md**

檔案：`plugins/feature-workflow/references/dotnet/verify-docx-cli/README.md`

```markdown
# verify-docx-cli

Plugin 內建 .NET 子專案，將 `verify.md` 渲染為品牌 Word 驗收報告。

## 為什麼自帶？

- 不依賴 minimax-skills 的 CLI（避免 upstream 變動風險）
- ProjectReference 共用 `MiniMaxAIDocx.Core` 的 OpenXML helper（圖片嵌入、XSD 驗證）

## 環境需求

- .NET SDK 8.0+（10.x 也支援，靠 `RollForward=LatestMajor`）
- minimax-skills plugin 已安裝（提供 `MiniMaxAIDocx.Core.csproj`），或設定 `MinimaxCorePath` env var 指向 Core.csproj 絕對路徑

## Build & Run

```bash
cd ~/.claude/plugins/marketplaces/company-marketplace/plugins/feature-workflow/references/dotnet/verify-docx-cli
dotnet run -- \
  --verify ../../path/to/verify.md \
  --output /tmp/report.docx \
  --style intumit \
  --cover '{"project":"X","feature":"Y","author":"Z","date":"2026-05-26","company":"Intumit","version":"v1.0"}'
```

完整參數：

| 參數 | 必填 | 說明 |
|------|-----|------|
| `--verify` | ✓ | verify.md 路徑 |
| `--output` | ✓ | 輸出 docx 路徑 |
| `--cover` | ✓ | 封面資訊 JSON |
| `--style` | | `intumit`（預設）/ `tech-dark` / `swiss` |
| `--logo` | | 覆寫 logo path |
| `--screenshots` | | 截圖目錄（明細中的 `![](screenshots/x.png)` 從此處取） |
| `--evidence` | | evidence 目錄（API response 截斷後存原檔處） |

## 環境變數

| 變數 | 用途 | 預設 |
|------|------|-----|
| `MinimaxCorePath` | Core.csproj 絕對路徑 | `$HOME/.claude/plugins/marketplaces/minimax-skills/skills/minimax-docx/scripts/dotnet/MiniMaxAIDocx.Core/MiniMaxAIDocx.Core.csproj` |

設定範例：

```bash
export MinimaxCorePath=/custom/path/to/MiniMaxAIDocx.Core.csproj
dotnet run -- ...
```

## Logo 三層偵測

CLI 啟動時依序檢查 logo 來源：

1. `--logo {path}` 參數
2. `$HOME/.claude/feature-workflow/assets/intumit-logo.png`（使用者全域覆寫）
3. `{plugin}/references/dotnet/verify-docx-cli/assets/intumit-logo.png`（內建）

`--style swiss` 不需要 logo（找不到不算錯）。

## 開發

| 加什麼 | 改哪 |
|--------|------|
| 新 brand style | `Styles/` 加新類別實作 `IBrandStyle`，更新 `BrandStyleFactory.Resolve` |
| 新段落 | `Markdown/VerifySection.cs` 加 record，`Markdown/VerifyMarkdownParser.cs` 加 extractor，`Rendering/` 加 Renderer，`Rendering/DocumentBuilder.cs` 接上 |

## 已知限制

- 未測試 Windows 環境（`$(HOME)` MSBuild 變數在 Windows 可用，但 `\` vs `/` 分隔符未驗證）
- 無單元測試，僅 smoke test（spec section 14 出 scope 項 7）
```

---

## Phase C4: Commit 4 (F8)

- [ ] **C4.1 commit**

```bash
cd ~/.claude/plugins/marketplaces/company-marketplace
git add plugins/feature-workflow/references/dotnet/verify-docx-cli/README.md
git commit -m "docs(verify-docx-cli): 新增 README"
```

---

## Phase F9: Smoke Test（end-to-end 驗證）

**Files:** 不修改檔案，純執行驗證。

### Steps

- [ ] **F9.1 選 fixture**

```bash
ls ~/.claude/plugins/marketplaces/company-marketplace/plugins/feature-workflow/skills/plan-verify/examples/
```

預期看到 `verify-report-sample.md`。如果這個 sample 不含截圖/evidence 段，可以額外建一個含完整 fixture 的 `.spec/smoke-test/`。

- [ ] **F9.2 跑三套 style end-to-end**

```bash
SAMPLE=~/.claude/plugins/marketplaces/company-marketplace/plugins/feature-workflow/skills/plan-verify/examples/verify-report-sample.md
CLI_DIR=~/.claude/plugins/marketplaces/company-marketplace/plugins/feature-workflow/references/dotnet/verify-docx-cli
COVER='{"project":"smoke","feature":"verify-docx-cli","author":"cheng","date":"2026-05-26","company":"Intumit","version":"v0.1"}'

mkdir -p /tmp/verify-docx-smoke
for STYLE in intumit tech-dark swiss; do
  dotnet run --project "$CLI_DIR" -- \
    --verify "$SAMPLE" \
    --output "/tmp/verify-docx-smoke/$STYLE.docx" \
    --style "$STYLE" \
    --cover "$COVER"
  echo "Exit: $?"
done

ls -lh /tmp/verify-docx-smoke/
```

預期：三個 docx 都產出，退出碼都是 0，每個都印「XSD 驗證通過」。

- [ ] **F9.3 視覺驗證（macOS Preview / Word）**

```bash
open /tmp/verify-docx-smoke/intumit.docx
```

逐項目視覺檢查（intumit）：
- [ ] 封面：藍標題 + 橘色裝飾線
- [ ] Logo 出現在封面頂部
- [ ] 簽核四欄表
- [ ] **TOC field**：開啟時 Word 提示「此文件含目錄欄位，是否更新？」按 Yes 後出現目錄
- [ ] 摘要表 + 結論粗體
- [ ] 明細逐項：標題、結果圖示、操作步驟、預期/實際、API 請求/回應（Cookie 已遮蔽成 `XXXX****YYYY`）
- [ ] 截圖嵌入（若 sample 有引用）
- [ ] 附錄

對 tech-dark / swiss 同樣檢查（swiss 確認**無 Logo**）。

- [ ] **F9.4 試一次完整 plan-verify 流程**

選一個現有 `.spec/{slug}/`（含 verify.md + screenshots + evidence）：

```bash
# 進入專案目錄後，跑：
/plan-verify
# 走完流程到 step 10，選 minimax-docx 引擎、選 intumit style
```

預期：產出 `.spec/{slug}/verify-report.docx`，內容如 F9.3 所列。

- [ ] **F9.5 push 全部 commits**

```bash
cd ~/.claude/plugins/marketplaces/company-marketplace
git log --oneline -5
git push origin main
```

預期：4 個 commit + 之前的 design doc commit，總共 5 個 commits push 上去。

---

## Self-Review Checklist

跑 self-review 前，先打勾以下：

### Spec 覆蓋

- [ ] D1 不改 upstream → Phase 全程沒動 `~/.claude/plugins/marketplaces/minimax-skills/`
- [ ] D2 plugin 自帶 .csproj + ProjectReference → F1.2 已寫
- [ ] D3 MinimaxCorePath env var + fallback → F1.2 已寫，F4.2 preflight 也用到
- [ ] D4 Logo 三層偵測 → F3 已寫
- [ ] F1 .NET 子專案骨架 → Phase F1
- [ ] F2 七段式 renderer → Phase F2-A/B/C/D
- [ ] F3 Logo 三層 → Phase F3
- [ ] F4 Preflight → Phase F4
- [ ] F5 word-report.md 改寫 → Phase F5
- [ ] F6 SKILL.md 改 → Phase F6
- [ ] F7 config 路徑統一 → Phase F7（含 grep 出來的額外 9 處）
- [ ] F8 README → Phase F8
- [ ] F9 Smoke test → Phase F9
- [ ] F10 4-commit 策略 → Phase C1/C2/C3/C4

### Placeholder 掃描

無「TBD/TODO/implement later」（除了 F2-A.2 標 `TODO: 實作 table walker` 是在說明而非空 placeholder，可保留）。

### Type 一致性

- `CoverInfo`/`DetailItem`/`PendingItem` 等 record 簽章在 F2-A.1 定義，後續 F2-C.* 引用一致
- `IBrandStyle` 介面在 F2-B.2 定義，三實作 F2-B.3 對齊
- `MainDocumentPart` 從 F2-C.8 修正後加進 `DetailRenderer` / `CoverRenderer` 建構子（DocumentBuilder 呼叫處也對齊）
- `ParagraphBuilder` / `TableBuilder` helpers 在 F2-C.5 抽出後，F2-C.6/F2-C.7/F2-C.10/F2-C.11 一致使用

---

## Execution Handoff

Plan 完成並儲存到：

`plugins/feature-workflow/docs/superpowers/plans/2026-05-26-verify-docx-cli.md`

請選擇執行模式：

**1. Subagent-Driven（建議）** — 每個 task 派一個 fresh subagent，task 間我做 review，快速迭代

**2. Inline Execution** — 在本 session 內依序執行，按 phase 設 checkpoint 讓你 review

哪一個？
