---
name: crew-doctor
description: CREW 環境健診 —— 一次性檢查 CREW 所有必要與選配依賴（Node/Git/Notion MCP/Agent Teams/瀏覽器 MCP/config/專案註冊/CLAUDE.md），列出綠黃紅燈與修法。當使用者提到 /crew-doctor、「CREW 環境健診」、「CREW 為什麼不能用」時觸發此 Skill。
---

# crew-doctor — CREW 環境健診

一次性檢查 CREW 運作所需的所有依賴與設定，在執行 Skill 前先告訴你
什麼能跑、什麼缺什麼、缺的怎麼補。比「等噴錯再排查」省時得多。

---

## 紀律護欄

> 紀律護欄：`../../references/discipline-preamble.md`（通用紀律）＋ `../../references/anti-rationalizations.md`「crew-doctor 專用」＋ `../../references/boundaries.md`「crew-doctor」段。

---

## 使用方式

```
/crew-doctor              # 完整健診（所有 18 項）
/crew-doctor --quick      # 只跑紅燈項目（8 項必要）
/crew-doctor --fix        # 健診同時嘗試自動修復可修復項目
```

---

## 檢查清單

### 🔴 必要（8 項，缺則某些 Skill 無法運作）

| # | 項目 | 檢查方式 | 缺失時提示 |
|---|------|---------|-----------|
| 1 | Node.js ≥ 18 | `node --version` | 對應 OS 安裝指令 |
| 2 | Git | `git --version` | 對應 OS 安裝指令 |
| 3 | Notion MCP | `claude mcp list` 含 notion 或 notion-local | `claude plugin install notion` |
| 4 | Agent Teams 啟用 | `$CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` | 加入 `~/.claude/settings.json` 的 env |
| 5 | CLAUDE.md 在當前專案 | `ls CLAUDE.md` | `/init` |
| 6 | bug-workflow 設定檔 | `~/.claude-company/bug-workflow-config.md` | `/bug-setup` |
| 7 | feature-workflow 設定 | `~/.claude-company/feature-workflow/config.md` | `/plan-setup` |
| 8 | 專案註冊 | `~/.claude-company/feature-workflow/projects/{repo-id}.md` | `/project-add` |

### 🟡 強烈建議（2 項，影響核心功能）

| # | 項目 | 檢查方式 | 缺失時影響 |
|---|------|---------|-----------|
| 9 | Playwright MCP | `claude mcp list` 含 playwright | plan-verify 降級或無法執行 |
| 10 | Maven / Gradle | `which mvn` 或 `which gradle` | plan-build E4 編譯驗證跳過 |

### 🟢 選配（4 項，缺少限制部分功能）

| # | 項目 | 檢查方式 | 缺失時影響 |
|---|------|---------|-----------|
| 11 | chrome-devtools MCP | `claude mcp list` 含 chrome-devtools | plan-verify `--deep` 不可用 |
| 12 | DBHub MCP | `claude mcp list` 含 dbhub | DB 直連功能不可用，plan-build DB 工程師退場 |
| 13 | .NET SDK ≥ 8 | `dotnet --version` | Word 報告降級為 python-docx 排版 |
| 14 | python-docx | `python3 -c "import docx"` | 完全無 Word 報告能力（需先裝 .NET 或 docx） |

### 🔍 進階檢查（4 項，僅當 #3 Notion MCP 通過時才跑）

| # | 項目 | 檢查方式 |
|---|------|---------|
| 15 | Notion 可讀 | 用 `notion-search` 試查 1 個現有頁面 |
| 16 | 任務追蹤工具可達 | 從設定檔讀 ID，試 `retrieve-a-data-source` |
| 17 | 設定檔欄位完整 | bug-workflow-config.md 必含「任務追蹤工具」「專案資料庫」ID |
| 18 | 共用 reference 漂移 | 若 marketplace 原始碼在本機，跑 `check-shared-refs.py` |

---

## 流程

### 1. 偵測作業系統

```
case "$(uname)" in
  Darwin*) OS=macos ;;
  Linux*)  OS=linux ;;
  MINGW*|MSYS*|CYGWIN*) OS=windows ;;
esac
```

OS 決定缺失提示的指令（例如 `brew install node` vs `winget install Node`）。

### 2. 跑必要項目（#1-8）

依序執行，每項通過或失敗都立即顯示在輸出中。
紅燈項目**不阻擋**後續檢查（要把完整圖像給使用者）。

### 3. 跑強烈建議（#9-10）與選配（#11-14）

執行後標示為 🟡 警告或 🔵 選配。

### 4. 進階檢查（#15-18，僅當 #3 通過時）

Notion 相關檢查需要實際 API call，每項 1-3 秒。
若 #3 紅燈，跳過 #15-18（沒有 Notion 後端跑不了，含共用 reference 漂移檢查）。

### 5. 產出摘要

```
==========================================
CREW 環境健診摘要
==========================================

🔴 紅燈 0 項
🟡 黃燈 1 項
🟢 綠燈 13 項
🔵 選配 4 項（其中 2 項未安裝）

可用 Skill 評估：
  ✅ bug-investigate / bug-fix / bug-close 可用
  ✅ plan-spec / plan-db / plan-arch / plan-build 可用
  ⚠️  plan-verify 降級：Playwright 未裝，無法做瀏覽器驗收
  🔵 plan-verify --deep 不可用：chrome-devtools 未裝（影響有限）

建議下一步：
  1. 安裝 Playwright 解開 plan-verify：
     claude mcp add playwright --scope user -- \
       npx @playwright/mcp@latest
```

### 6. `--fix` 模式

對下列項目嘗試自動修復：

| 項目 | 修法 |
|------|------|
| ~/.claude-company/feature-workflow/ 缺失 | `mkdir -p` |
| ~/.claude-company/feature-workflow/projects/ 缺失 | `mkdir -p` |
| ~/.claude-company/feature-workflow/stacks/ 缺失 | `mkdir -p` |
| CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS 未設 | 寫入 `~/.claude/settings.json` 的 env（先備份原檔） |

**不會自動修復**（仍要使用者操作）：
- MCP 安裝（要 `claude plugin/mcp` 指令）
- Notion 授權（互動式 OAuth）
- CLAUDE.md 建立（要 `/init`）
- Notion 資料庫建立（要 `/bug-setup` 互動建立）

`--fix` 修了什麼會明確列出，並建議再跑一次 `/crew-doctor` 確認。

### 7. 退出碼

| 碼 | 意義 |
|----|------|
| 0 | 紅燈全綠（不論黃綠選配如何） |
| 1 | 有紅燈 |
| 2 | 健診本身執行錯誤（檔案 IO、permission） |

---

## 輸出範例

```
==========================================
🔍 CREW 環境健診（v3.9.0）
==========================================

🔴 必要項目（8）
   ✅ Node.js v18.20.4
   ✅ Git 2.45.0
   ❌ Notion MCP 未安裝
      → 修法：claude plugin install notion
      → 安裝後重啟 Claude Code
   ✅ Agent Teams 啟用（settings.json）
   ✅ CLAUDE.md 存在於 /Users/cheng/IdeaProjects/MyProject
   ✅ bug-workflow-config.md 存在
   ✅ feature-workflow/config.md 存在
   ❌ 專案未註冊（找不到 projects/{repo-id}.md）
      → 修法：/project-add

🟡 強烈建議（2）
   ✅ Playwright MCP 已安裝
   ⚠️  Maven / Gradle 未找到
      → 影響：plan-build E4 編譯驗證會跳過

🔵 選配（4）
   ⚫ chrome-devtools MCP 未安裝（--deep 模式不可用）
   ✅ DBHub MCP 已安裝
   ✅ .NET SDK 8.0.100
   ⚫ python-docx 未安裝（有 .NET 不影響）

🔍 進階檢查（4）
   ⏭️  跳過：紅燈未過（Notion MCP 缺失）

==========================================
摘要：紅燈 2、黃燈 1、綠燈 11、選配 4
建議：先 claude plugin install notion，再 /project-add
==========================================
```

---

## 何時不用

- 程式或測試為何壞掉（非 CREW 環境依賴）→ 個人 `investigate` skill 或 `superpowers:systematic-debugging`
- CREW 首次設定 → `/crew-init`
- 更新 CREW plugins → `/crew-upgrade`
- 一般專案環境問題（非 CREW 依賴）→ 自行排查

## Gotchas

- **`claude mcp list` 輸出格式**：不同版本可能變動，需用 grep / awk 適配
- **跨平台路徑**：Windows 用 `%USERPROFILE%`、Unix 用 `$HOME`
- **Notion API 速率限制**：#15-16 試查若被 throttle，標示為 ⚠️ 不算失敗
- **`--fix` 改 settings.json 風險**：先 cp settings.json.bak，失敗能還原
- **MCP 未啟用 vs 未安裝**：`claude plugin list` 顯示 `enabled` 才算可用

---

## 邊界情況

- **`claude` CLI 本身找不到**：跳出健診，提示「請確認 Claude Code 已安裝」
- **HOME 環境變數異常**：跳出健診，提示「無法定位設定檔目錄」
- **Notion 授權過期**：#15 失敗時提示「請在 Notion 中重新授權」
- **使用者在 plugin marketplace 原始碼裡跑**：#18 才會跑，否則跳過
