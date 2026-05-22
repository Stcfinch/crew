# CREW 前置條件與系統需求

## 完整依賴矩陣

| 依賴 | 層級 | 用途 | 安裝方式 | 適用 Skill |
|------|------|------|---------|-----------|
| **Node.js ≥ 18** | 🔴 必要 | 所有 MCP Server 的執行環境 | [nodejs.org](https://nodejs.org/) | 全部 |
| **Git** | 🔴 必要 | 版本控制、專案識別 | 系統內建或安裝 | 全部（14/17 skills） |
| **Notion MCP** | 🔴 必要 | Notion 資料庫讀寫 | `claude plugin install notion`（推薦）或 notion-local | 15/17 skills |
| **Agent Teams** | 🔴 必要 | 多人協作程式碼產生與審查 | 設定環境變數（見下方） | plan-build、plan-review |
| **Playwright MCP** | 🟡 強烈建議 | 瀏覽器自動化驗收 | `claude mcp add playwright ...` | plan-verify、bug-fix |
| **Maven / Gradle** | 🟡 強烈建議 | 編譯驗證 | 專案本身自帶 | plan-build、bug-fix |
| **DBHub MCP** | 🟢 選配 | 資料庫直連（MSSQL/MySQL/PostgreSQL） | `claude mcp add dbhub ...` | plan-build、plan-review |
| **Chrome DevTools MCP** | 🟢 選配 | Console / Network 除錯 | `claude mcp add chrome-devtools ...` | plan-verify --deep |
| **minimax-skills Plugin** | 🟢 選配 | Word 驗收報告產出 | `claude plugin install minimax-skills` | plan-verify --word |
| **Node.js + ExcelJS** | 🟢 選配 | Excel 驗收報告產出 | ExcelJS 自動安裝（需 Node.js） | plan-verify --excel |
| **curl** | 🔵 標準工具 | API 測試 | 系統內建 | plan-verify、bug-fix |
| **python3** | 🔵 標準工具 | JSON 格式化 | 系統內建或安裝 | plan-verify |
| **grep / find** | 🔵 標準工具 | 安全掃描、日誌搜尋 | 系統內建 | plan-security、bug-investigate |

> 🔴 必要 = 缺少無法運作 ｜ 🟡 強烈建議 = 核心功能受限 ｜ 🟢 選配 = 有更好 ｜ 🔵 標準工具 = macOS/Linux 內建

> 💡 不確定環境完整性？跑 `/crew-doctor` 一次性檢查所有項目並給出修法建議。

---

## Notion Workspace

需有以下資料庫（或由 setup 引導建立）：

- **任務追蹤工具**：Bug / 功能 生命週期管理（兩個 Plugin 共用）
- **專案資料庫**：管理專案對應（兩個 Plugin 共用）
- **Bug 知識庫**（選用）：Bug 精簡索引
- **功能設計庫**（選用）：設計文件索引

詳細 Schema 與建立順序見 [notion-schema.md](./notion-schema.md)。

---

## Agent Teams 環境變數

`/plan-build`（多人產碼）和 `/plan-review`（3 人審查）需要啟用 Agent Teams：

```jsonc
// ~/.claude/settings.json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

> `/plan-setup` 會自動檢查並引導設定。

---

## 瀏覽器驗證工具（plan-verify / bug-fix）

`/plan-verify` 使用瀏覽器自動化工具驗證驗收條件，產出 Health Score 和截圖證據。
`/bug-fix` 在修復前端 Bug 時也會使用瀏覽器驗證。以下工具擇一安裝即可：

### 方式 A：Playwright MCP（推薦）

```bash
claude mcp add playwright --scope user -- \
  npx @anthropic-ai/mcp-server-playwright@latest
```

Anthropic 官方維護，支援截圖、元素互動、表單填寫、頁面導航等。安裝後重啟 Claude Code。

### 方式 B：chrome-devtools-mcp

```bash
claude mcp add chrome-devtools --scope user -- \
  npx chrome-devtools-mcp@latest --autoConnect
```

Google 官方維護，可連接已登入的 Chrome session，適合需要 SSO/VPN 的內部系統。
額外提供 console log 串流、network 請求分析、performance trace（`--deep` 模式）。

> 💡 兩者可同時安裝：Playwright 負責 QA 驗收，chrome-devtools 負責除錯診斷（console/network）。

---

## Windows 使用者

CREW 完整支援 Windows，但有環境差異需注意。詳見 [windows.md](./windows.md)。
