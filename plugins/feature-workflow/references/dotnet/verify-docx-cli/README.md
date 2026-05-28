# verify-docx-cli

Plugin 內建 .NET 子專案，將 `verify.md` 渲染為品牌 Word 驗收報告。

## 為什麼自帶？

- 不依賴 minimax-skills 的 CLI（避免 upstream 變動風險）
- ProjectReference 共用 `MiniMaxAIDocx.Core` 的 OpenXML helper（圖片嵌入、TOC field、Drawing 建構）
- 結構驗證用 OpenXML SDK 內建的 `OpenXmlValidator`（完整 OOXML schema），不依賴外部 XSD

## 環境需求

- .NET SDK 8.0+（9.x / 10.x 也支援，靠 `RollForward=LatestMajor`）
- minimax-skills plugin 已安裝（提供 `MiniMaxAIDocx.Core.csproj`），或設定 `MinimaxCorePath` env var 指向 Core.csproj 絕對路徑

## Build & Run

本專案 multi-target（`net8.0;net10.0`），`dotnet run` **必須指定 `--framework`**，否則會報錯要求選 TFM。
建議用 `net8.0`（下限 TFM）；搭配 `RollForward=LatestMajor`，在只安裝較新 runtime（net9/net10）的機器上也能 roll-forward 執行。

```bash
cd ~/.claude/plugins/marketplaces/company-marketplace/plugins/feature-workflow/references/dotnet/verify-docx-cli
dotnet run --framework net8.0 -- \
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
| `--cover` | ✓ | 封面資訊 JSON（project / feature / author / date / company / version） |
| `--style` | | `intumit`（預設）/ `tech-dark` / `swiss` |
| `--logo` | | 覆寫 logo path |
| `--screenshots` | | 截圖目錄（明細中的 `![](screenshots/x.png)` 從此處取檔名） |
| `--evidence` | | evidence 目錄（API response 截斷後引用原檔處） |

退出碼：產出成功且結構驗證通過 → `0`；docx 已產出但 `OpenXmlValidator` 驗證失敗 → `1`。

## 環境變數

| 變數 | 用途 | 預設 |
|------|------|-----|
| `MinimaxCorePath` | Core.csproj 絕對路徑 | `$HOME/.claude/plugins/marketplaces/minimax-skills/skills/minimax-docx/scripts/dotnet/MiniMaxAIDocx.Core/MiniMaxAIDocx.Core.csproj` |

設定範例：

```bash
export MinimaxCorePath=/custom/path/to/MiniMaxAIDocx.Core.csproj
dotnet run --framework net8.0 -- ...
```

## Logo 三層偵測

CLI 啟動時依序檢查 logo 來源（`LogoResolver`）：

1. `--logo {path}` 參數
2. `$HOME/.claude/feature-workflow/assets/intumit-logo.png`（使用者全域覆寫）
3. `{plugin}/references/dotnet/verify-docx-cli/assets/intumit-logo.png`（內建）

`--style swiss` 不需要 logo（找不到不算錯，回傳 null）。其餘 style 三層都找不到 → 丟 `FileNotFoundException`。

## 渲染特性

- **TOC field**：插入 `TOC \o "1-3"` 複雜功能變數 + `UpdateFieldsOnOpen`，Word 開檔自動提示更新目錄
- **敏感資訊遮蔽**：API headers 的 Cookie / Authorization / X-Api-Key / X-Token 自動遮蔽
- **長回應截斷**：API response > 20 行時切首尾各 10 行 + 「省略 N 行」+ 引用 evidence 完整檔
- **截圖**：依 `--screenshots` 目錄嵌入；找不到檔則插入「（截圖不可用）」文字段，不中斷

## 開發

| 加什麼 | 改哪 |
|--------|------|
| 新 brand style | `Styles/` 加新類別實作 `IBrandStyle`，更新 `BrandStyleFactory.Resolve`，並在 `Program.cs` 的 `--style` `AcceptOnlyFromAmong` 加值 |
| 新段落 | `Markdown/VerifySection.cs` 加 record，`Markdown/VerifyMarkdownParser.cs` 加 extractor，`Rendering/` 加 Renderer，`Rendering/DocumentBuilder.cs` 接上 |

## 已知限制

- 未測試 Windows 環境（`$(HOME)` MSBuild 變數在 Windows 可用，但 `\` vs `/` 分隔符未驗證）
- 無單元測試，僅 smoke test
