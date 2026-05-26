# Design — verify-docx-cli 整合到 plan-verify

**日期**：2026-05-26
**狀態**：Approved（待 writing-plans 產實作計畫）
**Scope**：feature-workflow plugin（不動 minimax-skills）

---

## 1. 問題背景

`feature-workflow:plan-verify` 的 step 10（Word 驗收報告產出）依賴 minimax-docx skill，但實際使用上有三個阻礙：

1. **minimax-docx CLI 沒有 SKILL.md 文件描述的 `run-script` 子命令**。Program.cs 只註冊 `create / edit / apply-template / validate / merge-runs / fix-order / analyze / diff`，沒有 `run-script`。
2. **CLI build artifact 是 .NET 8 target，但本機只裝 .NET 10 runtime → launch 階段失敗**。`dotnet build` 通過（cross-compile 可用），但執行時 runtime probe 找不到 `Microsoft.NETCore.App 8.0.x`，回報 `app launch failed`。
3. **feature-workflow 沒有 verify.md → docx 的 .csx 範本**。`references/` 只有 python 版本（`verify-docx-generator.py`，618 行），對應的 OpenXML/.csx 不存在，導致 word-report.md 10.4a「使用 /minimax-docx Skill 產出」的描述沒法 zero-shot 落地。

額外發現：**minimax-skills 的 git remote 是 MiniMax-AI 官方 upstream，本機沒有 push 權限**，直接改 minimax-skills 的方案不可行。

---

## 2. 決策摘要（4 個關鍵抉擇）

| # | 抉擇點 | 決議 | 否決選項 |
|---|--------|------|---------|
| D1 | 修改 minimax-skills 的策略 | **不改**，把所需功能完全搬到 feature-workflow | Fork + PR / 本地 patch |
| D2 | `run-script` 實作技術路線 | feature-workflow 自帶 .NET 子專案 + ProjectReference 到 Core | Roslyn CSharpScript / dotnet-script |
| D3 | ProjectReference 路徑解析 | `$(MinimaxCorePath)` env var override + `$(HOME)/.claude/plugins/...` fallback + plan-verify preflight | 動態生成 .csproj / PackageReference 重寫 helper |
| D4 | Logo 來源策略 | Plugin 自帶 PNG fallback + `~/.claude/feature-workflow/assets/intumit-logo.png` 使用者覆寫 | 線上下載 / 強制 `--logo` |

連帶 D5：順手把 `~/.claude-company/feature-workflow/` 過時路徑全面改為 `~/.claude/feature-workflow/`。

---

## 3. 實作清單

| # | 元件 | 位置 |
|---|------|------|
| F1 | 新建 `verify-docx-cli` .NET 子專案 | `feature-workflow/references/dotnet/verify-docx-cli/` |
| F2 | 七段式 verify.md → docx renderer（封面/簽核/環境/摘要/明細/待處理/附錄 + TOC + 截圖 + 三套 style） | 同上 |
| F3 | Logo 三層偵測（CLI 參數 → 使用者覆寫目錄 → plugin 內建） | F1 子專案 + `phases/word-report.md` |
| F4 | Preflight 偵測 minimax-skills（找不到 Core 提示安裝） | `phases/word-report.md` step 10.0c（新增） |
| F5 | 改寫 `word-report.md` step 10.4a 抽象描述為具體 `dotnet run` 指令 | `skills/plan-verify/phases/word-report.md` |
| F6 | 改 `plan-verify/SKILL.md` 引擎偵測：以 `dotnet ≥ 8` + Core 存在判定 minimax-docx 可用 | `skills/plan-verify/SKILL.md` |
| F7 | 統一 config 路徑：`~/.claude-company/feature-workflow/` → `~/.claude/feature-workflow/` | `config-resolver.md`、`plan-verify/SKILL.md`、`word-report.md`、相關 `plan-*/SKILL.md` |
| F8 | `verify-docx-cli/README.md`：build、env var、開發指引 | F1 子專案 |
| F9 | Smoke test：三套 style × 完整 plan-verify | 本地驗證 |
| F10 | Commit 策略：4 個獨立 commit | feature-workflow git（mark22013333/crew）|

---

## 4. 子專案內部結構（F1 + F2 詳設計）

### 4.1 目錄樹

```
feature-workflow/references/dotnet/verify-docx-cli/
├── VerifyDocxCli.csproj
├── Program.cs
├── README.md
├── assets/
│   └── intumit-logo.png              # 內建 fallback
├── Markdown/
│   ├── VerifyMarkdownParser.cs       # 解析 verify.md 七段式 + human_steps/evidence 註解
│   └── VerifySection.cs              # 段落 model
├── Rendering/
│   ├── DocumentBuilder.cs            # 組裝主流程
│   ├── CoverRenderer.cs
│   ├── SignoffRenderer.cs
│   ├── EnvRenderer.cs
│   ├── SummaryRenderer.cs
│   ├── DetailRenderer.cs             # 含截圖嵌入、API 紀錄、敏感資訊遮蔽
│   ├── PendingRenderer.cs
│   ├── AppendixRenderer.cs
│   └── TocInserter.cs                # python-docx 沒有的核心差異點
├── Styles/
│   ├── IBrandStyle.cs
│   ├── IntumitStyle.cs               # 藍+橘 + Logo + 橘色裝飾線
│   ├── TechDarkStyle.cs              # 深藍 + 青綠
│   └── SwissStyle.cs                 # 黑灰極簡（無 Logo）
├── Sanitization/
│   └── SensitiveDataMasker.cs        # Cookie/Auth/API Key 遮蔽
└── Validation/
    └── XsdGateCheck.cs               # 呼叫 Core.Validation.XsdValidator
```

### 4.2 VerifyDocxCli.csproj 核心配置

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFrameworks>net8.0;net10.0</TargetFrameworks>
    <RollForward>LatestMajor</RollForward>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
    <MinimaxCoreDefault>$(HOME)/.claude/plugins/marketplaces/minimax-skills/skills/minimax-docx/scripts/dotnet/MiniMaxAIDocx.Core/MiniMaxAIDocx.Core.csproj</MinimaxCoreDefault>
    <MinimaxCorePath Condition="'$(MinimaxCorePath)' == ''">$(MinimaxCoreDefault)</MinimaxCorePath>
  </PropertyGroup>
  <ItemGroup>
    <ProjectReference Include="$(MinimaxCorePath)" />
    <PackageReference Include="System.CommandLine" Version="2.0.5" />
    <PackageReference Include="Markdig" Version="0.37.0" />
  </ItemGroup>
</Project>
```

**設計理由**：
- `TargetFrameworks` multi-target → dotnet 8 與 dotnet 10 環境都可 build
- `RollForward=LatestMajor` → 即使只 build 出 net8.0 artifact，runtime 也會 fall forward 到 net10
- `$(MinimaxCorePath)` env var override → 給 MiniMax 改 repo 結構時的應急通道
- `$(HOME)/.claude/plugins/...` fallback → 一般情境零設定

### 4.3 CLI 介面（與 python 版簽章對齊）

```bash
dotnet run --project {plugin}/references/dotnet/verify-docx-cli -- \
  --verify .spec/{slug}/verify.md \
  --screenshots .spec/{slug}/screenshots/ \
  --evidence .spec/{slug}/evidence/ \
  --output .spec/{slug}/verify-report.docx \
  --style intumit \                  # intumit | tech-dark | swiss
  --logo {optional-path} \           # 沒給就走自動偵測
  --cover '{"project":"...","feature":"...","author":"...","date":"...","company":"...","version":"..."}'
```

### 4.4 關鍵設計選擇

1. **Markdown 解析用 Markdig**：成熟、原生支援 HTML 註解（`<!-- human_steps -->`、`<!-- evidence -->`）
2. **Renderer 一段一個 class**：對應 word-report.md 七段式，新增段落只動一個檔
3. **IBrandStyle 介面 + 三實作**：對應三種 `--style`，未來加新風格只實作介面、不動 renderer
4. **XSD 驗證重用 Core**：Core 已寫好 `XsdValidator`，ProjectReference 直接拿來用
5. **TOC field**：用 `FieldAndTocSamples.cs` 的模式插入 `BEGIN TOC \o "1-3" \h \z \u END`，Word 開啟時自動 prompt 更新——這是 python-docx 做不到、必須走 OpenXML 的核心理由
6. **測試紀錄截斷規則**：放在 `DetailRenderer.cs`。> 20 行的 API response：報告內顯示前 10 行 + 省略提示 + 後 10 行，原檔寫到 `evidence/verify-{N}-response.json`

---

## 5. Logo 偵測（F3 詳設計）

### 5.1 偵測順序

| 優先 | 來源 | 用途 |
|-----|------|------|
| 1 | `--logo {path}` CLI 參數明示 | 單次覆寫（測試/特殊報告）|
| 2 | `$HOME/.claude/feature-workflow/assets/intumit-logo.png` | 使用者全域覆寫（公司專屬版本、不同尺寸）|
| 3 | `{plugin}/references/dotnet/verify-docx-cli/assets/intumit-logo.png` | Plugin 內建預設 |

### 5.2 邏輯

`Program.cs` 啟動時依序檢查，第一個存在的就用。都沒有時：

- `--style swiss` → 跳過 Logo（Swiss 風本來就不放 Logo，照 word-report.md step 10.0a 規格）
- `--style intumit / tech-dark` → 失敗並提示放置位置

### 5.3 不下載網路資源

避免離線環境失效、避免每次 build 對外請求。

**Plugin 內建 PNG 的取得（F1 開發者任務，非 runtime 行為）**：
- 來源：`https://www.intumit.com/wp-content/uploads/logo-Intumit.png`（一次性手動下載）
- 體積限制：< 100KB，commit 前用 `optipng -o7` 壓縮
- 位置：`references/dotnet/verify-docx-cli/assets/intumit-logo.png`
- 一旦 commit 進 plugin，後續所有使用者都可用，不需要再下載

---

## 6. Preflight 偵測（F4 詳設計）

新增 `phases/word-report.md` step **10.0c**（在 10.0a 選風格、10.0b 選引擎之前）：

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
    echo "⚠️  minimax-docx Core 未安裝（路徑：$CORE_PATH）"
    echo ""
    echo "請選擇："
    echo "  A) 安裝 minimax-skills plugin（在 Claude Code 內執行 /plugin install minimax-skills）"
    echo "  B) 已從別處安裝，請設定環境變數：export MinimaxCorePath=<path-to-MiniMaxAIDocx.Core.csproj>"
    echo "  C) 改用 python-docx fallback（基礎排版，無 TOC/XSD）"
    echo "  D) 跳過 Word 報告"
    # AskUserQuestion 收 A/B/C/D
  else
    report_engine="minimax-docx"
  fi
fi
```

**目的**：把錯誤拉到流程最前面（在收集封面資訊前），避免使用者填完一大堆東西最後才 build 失敗。

---

## 7. Config 路徑統一（F7 詳設計）

| 檔案 | 行 | 動作 |
|------|---|------|
| `references/config-resolver.md` | L9, L22, L30, L33, L35 | `~/.claude-company/feature-workflow/` → `~/.claude/feature-workflow/`；移除「公司環境（優先）」/「個人環境（備用）」階層描述，改成「統一位置」 |
| `skills/plan-verify/SKILL.md` | L527 | 同上 |
| `skills/plan-verify/phases/word-report.md` | L84 | 同上 |
| `README.md` | L305 附近 | 連帶檢查 |
| 其他 `plan-*/SKILL.md` 出現處 | grep 確認 | 一併同步 |

**向下相容**：在 `config-resolver.md` 加一段「舊路徑遷移」說明——若 `~/.claude-company/feature-workflow/` 存在但 `~/.claude/feature-workflow/` 不存在，提示使用者執行 `mv` 指令搬移（不自動搬，避免破壞使用者既有 setup）。

---

## 8. word-report.md step 10.4a 新版（F5 詳設計）

替換現狀 L287-294 的抽象描述為：

```
#### 10.4a 使用 minimax-docx 產出（report_engine = minimax-docx）

呼叫 plugin 內建的 verify-docx-cli .NET 子專案：

# 1. 解析 plugin 路徑
PLUGIN_DIR="$HOME/.claude/plugins/marketplaces/company-marketplace/plugins/feature-workflow"
CLI_DIR="$PLUGIN_DIR/references/dotnet/verify-docx-cli"

# 2. 解析 Logo（三層偵測）
if [ -n "$USER_LOGO" ]; then
  LOGO="$USER_LOGO"
elif [ -f "$HOME/.claude/feature-workflow/assets/intumit-logo.png" ]; then
  LOGO="$HOME/.claude/feature-workflow/assets/intumit-logo.png"
else
  LOGO="$CLI_DIR/assets/intumit-logo.png"
fi

# 3. 跑 verify-docx-cli
dotnet run --project "$CLI_DIR" -- \
  --verify .spec/{slug}/verify.md \
  --screenshots .spec/{slug}/screenshots/ \
  --evidence .spec/{slug}/evidence/ \
  --output .spec/{slug}/verify-report.docx \
  --style {style} \
  --logo "$LOGO" \
  --cover '{json}'

優於 python-docx 之處：
- TOC field：Word 開啟時 prompt 自動更新目錄
- XSD 驗證：確保 docx 結構正確
- 精確控制 multi-section header/footer

**首次執行 UX 提示**：
verify-docx-cli 第一次跑會 trigger `dotnet restore`（拉 OpenXML、Markdig、System.CommandLine）+ build Core，整體耗時約 1–2 分鐘。Skill 在執行前要顯示：

  ⏳ 首次產出 Word 報告需要 build .NET 子專案（約 1-2 分鐘）...

後續執行只要幾秒（incremental build cache）。
```

---

## 9. plan-verify/SKILL.md 改動（F6 詳設計）

兩處：

1. **引擎偵測邏輯段落**：補上 `MinimaxCorePath` env var 說明 + Core 存在性檢查（與 F4 preflight 邏輯對齊）
2. **L527 路徑**：`~/.claude-company/feature-workflow/` → `~/.claude/feature-workflow/`（F7 連帶）

---

## 10. README 內容大綱（F8）

`verify-docx-cli/README.md` 結構：

```markdown
# verify-docx-cli

Plugin 內建 .NET 子專案，將 verify.md 渲染為品牌 Word 報告。

## 為什麼自帶？
- 不依賴 minimax-skills 的 CLI（避免 upstream 變動風險）
- ProjectReference 共用 MiniMaxAIDocx.Core 的 OpenXML helper

## 環境需求
- .NET SDK 8.0+（10.x 也支援，靠 RollForward=LatestMajor）
- minimax-skills plugin 已安裝（或設定 MinimaxCorePath env var 指向 Core.csproj）

## Build & Run
（範例指令）

## 環境變數
| 變數 | 用途 | 預設 |
|------|------|-----|
| MinimaxCorePath | Core.csproj 絕對路徑 | $HOME/.claude/plugins/marketplaces/minimax-skills/.../Core.csproj |

## 開發
- 加新風格 → Styles/ 加 IBrandStyle 實作
- 加新段落 → Rendering/ 加 Renderer + DocumentBuilder 組裝
```

---

## 11. Smoke Test（F9 詳設計）

1. **選 fixture**：用一個現有 `.spec/{slug}/` 含 verify.md + screenshots + evidence
2. **三套 style 各跑一次**：`--style intumit / tech-dark / swiss`，產出三份 docx
3. **驗證項**：
   - [ ] docx 開啟不報錯
   - [ ] Word 開啟提示「此文件含目錄欄位，是否更新？」（證明 TOC field 工作）
   - [ ] Intumit 風含 Logo + 橘色裝飾線
   - [ ] Tech Dark 風含深藍 + 青綠
   - [ ] Swiss 風無 Logo、黑灰極簡
   - [ ] 截圖嵌入正確
   - [ ] Cookie / Authorization 已遮蔽
   - [ ] XSD 驗證通過（CLI 退出碼 0）
4. **環境組合**：在 dotnet 10 機器（本機）跑；若有 dotnet 8 環境補測

---

## 12. Commit 策略（F10）

| Commit | Scope | 訊息 |
|--------|-------|------|
| 1 | F1 + F2 + F3（含 logo 內建 PNG）| `feat(plan-verify): 新增 verify-docx-cli .NET 子專案與 logo 三層偵測` |
| 2 | F4 + F5 + F6 | `feat(plan-verify): 整合 verify-docx-cli 到 word-report 流程，新增 minimax-skills preflight` |
| 3 | F7 | `refactor(feature-workflow): 統一 config 路徑為 ~/.claude/feature-workflow/` |
| 4 | F8 | `docs(verify-docx-cli): 新增 README` |

**Push**：四個 commit 一次 `git push origin main`（mark22013333/crew，個人 fork、無 PR 流程需求）。

**Plugin 1（minimax-skills）**：完全不 touch、不 commit、不 push。

---

## 13. 風險與緩解

| 風險 | 機率 | 影響 | 緩解 |
|------|-----|------|------|
| MiniMax 改 repo 結構導致 Core 路徑失效 | 低 | 高 | `MinimaxCorePath` env var 應急 + preflight 提示 |
| 使用者只裝 feature-workflow 沒裝 minimax-skills | 中 | 中 | Preflight 偵測 + 安裝指令提示 |
| dotnet 10 + net8.0 multi-target build 出現相容性問題 | 低 | 中 | Smoke test 在 dotnet 10 環境驗證；RollForward 保底 |
| Markdig 解析 verify.md 邊緣 case（巢狀 list、code fence 內含 HTML 註解）出錯 | 中 | 低 | Renderer 加 graceful fallback：解析失敗就把段落以 plain text 嵌入並記 warning |
| Logo PNG 體積過大拖慢 plugin clone | 低 | 低 | 限制 < 100KB，commit 前 optipng 壓縮 |
| Config 路徑統一導致現有 `~/.claude-company/` 使用者 break | 中 | 中 | 向下相容偵測 + 提示手動 `mv`，不自動搬 |

---

## 14. 出 scope（明示不做）

1. **不發 PR 到 minimax-skills upstream**（D1 決議）
2. **不改 verify-docx-generator.py**（python-docx fallback 維持原狀）
3. **不改 verify-excel-generator.js**（Excel 報告獨立、不受影響）
4. **不重構 plan-verify 其他 step**（只動 step 10 Word 報告產出）
5. **不加 Windows 支援的特殊處理**（使用者環境為 macOS；`$(HOME)` MSBuild 變數在 Windows 雖可用但未測試）
6. **不做 i18n**（CLI 訊息維持繁中）
7. **不寫 verify-docx-cli 的單元測試**（C# parser/renderer 的 unit tests）。Smoke test（三套 style × 完整 plan-verify）作為唯一驗證。理由：CLI 工具邏輯相對線性，且 docx 視覺差異用單元測試難捕捉；smoke test 性價比更高

---

## 15. 後續（Out of Scope，留待未來）

- 若 MiniMax 後續真的加 `run-script` 命令，可考慮把 verify-docx-cli 改寫為 .csx 走 minimax-docx CLI（簡化部署）。但目前自帶子專案 + Core ProjectReference 已足夠。
- Excel 報告未來若也要 TOC/品牌風格，可仿照 verify-docx-cli 模式新建 verify-excel-cli（.NET ClosedXML 或 EPPlus）。
