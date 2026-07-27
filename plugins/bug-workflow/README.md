# Bug Workflow Plugin `v3.13.0`

整合 Notion 與 Claude Code，自動化 Bug 生命週期管理。

## 功能

| 指令 | 說明 |
|------|------|
| `/bug-setup` | 首次設定引導，自動偵測 Notion 資料庫並產出設定檔 |
| `/bug-start <問題簡述>` | 在 Notion 建立 Bug 條目，自動關聯來源 Feature + 偵測 Feature Branch |
| `/bug-investigate` | 假說驅動根因調查 — 證據收集、模式比對、假說驗證、3-Strike 升級 |
| `/bug-fix` | 修復紀律 — 分支檢查 + 鐵律檢查 + 迴歸測試 + merge 引導 |
| `/bug-update <內容>` | 調查過程中更新 Bug 頁面（Log、SQL、判斷等） |
| `/bug-update reopen <Bug>` | 重新開啟已結案的 Bug（復發處理） |
| `/bug-close` | 結案前引導 merge 回 DEV + 從 Git diff 擷取修復細節 + 同步知識庫 |
| `/project-add` | **偵測專案架構**（簡單型/產品型）→ Notion 註冊 → 可選安裝 DB MCP |
| `/crew-doctor` | CREW 環境健診 — 18 項依賴與設定檢查，含 `--quick` / `--fix` 模式 |
| `/crew-init` | CREW 一鍵首次設定 — 統合 /bug-setup + /plan-setup + 提示 /init 與 /project-add，含 `--resume` |
| `/crew-upgrade` | 一次更新 bug-workflow + feature-workflow，顯示 CHANGELOG 摘要 |

## 前置條件

1. **Node.js ≥ 18** — 所有 MCP Server 的執行環境
   - macOS：`brew install node` 或 [nodejs.org](https://nodejs.org/)
   - Windows：[nodejs.org](https://nodejs.org/) 下載 LTS 版（安裝時勾選 Add to PATH）
   - Linux：`sudo apt install nodejs npm`

2. **Notion Plugin** — 需先安裝 Notion MCP Server
   ```bash
   claude plugin install notion
   ```

3. **Notion Workspace** — 需有以下資料庫（或由 `/bug-setup` 引導建立）：
   - **任務追蹤工具**：Bug 生命週期管理（主要資料庫）
   - **Bug 知識庫**（選用）：精簡索引，結案時自動同步
   - **專案資料庫**：管理專案對應

4. **Notion 權限** — Claude Code 需授權以下 Notion 工具：
   - `notion-search`、`notion-fetch`（搜尋與讀取）
   - `notion-create-pages`（建立 Bug 條目）
   - `notion-update-page`（更新頁面內容與屬性）
   - `notion-update-data-source`（新增欄位，僅 setup 時使用）

> **Windows 使用者**：詳細的 Windows 環境設定指南請見[根目錄 README](../../README.md#windows-使用者指南)。`/bug-setup` 會自動偵測作業系統並顯示對應的安裝指令。

## 安裝

```bash
claude plugin marketplace add mark22013333/crew && \
claude plugin install bug-workflow
```

安裝後 Plugin 會自動啟用。若未自動啟用，手動執行：`claude plugin enable bug-workflow`

### 更新

```bash
claude plugin update bug-workflow@company-marketplace
```

更新完成後**重啟 Claude Code** 使新版生效。

> 若 `update` 顯示已是最新但功能未生效，可先移除再重裝：
> ```bash
> claude plugin uninstall bug-workflow@company-marketplace && \
> claude plugin install bug-workflow@company-marketplace
> ```

## 首次設定

安裝後執行 `/bug-setup`，自動完成：
1. 選擇設定檔儲存位置（公司環境或個人環境）
2. 偵測 Notion Workspace 中的資料庫
3. 驗證並補齊必要欄位（狀態、根因分類、修復分支、相關任務等）
4. 設定當前專案目錄與 Notion 專案的對應
5. 產出設定檔

## 工作流程

```mermaid
flowchart TD
    discover["發現 Bug"]
    investigate["/bug-investigate<br/><i>自動建立條目 + 假說驅動根因調查</i>"]
    clarify{"需要釐清？"}
    clarifyStep["列出釐清問題<br/><i>使用者回答後建議指令</i>"]
    fix["/bug-fix<br/><i>修復 + 鐵律檢查 + 迴歸測試</i>"]
    close["/bug-close<br/><i>merge 引導 + 結案 + 知識庫</i>"]
    reopen{上線後復發？}
    reopenCmd["/bug-update reopen<br/><i>重新開啟</i>"]
    startOpt["/bug-start<br/><i>僅建立條目（可選）</i>"]

    discover --> investigate
    investigate --> clarify
    clarify -- "是" --> clarifyStep --> fix
    clarify -- "否" --> fix
    fix --> close --> reopen
    reopen -- "是" --> reopenCmd --> investigate
    reopen -- "否" --> done(["完成"])

    discover -. "只想先建條目" .-> startOpt .-> investigate

    style discover fill:#fee,stroke:#f66
    style done fill:#efe,stroke:#6c6
    style investigate fill:#e3f2fd,stroke:#2196f3
    style fix fill:#e3f2fd,stroke:#2196f3
    style clarify fill:#fff3e0,stroke:#ff9800
    style startOpt fill:#f5f5f5,stroke:#bbb,stroke-dasharray: 5 5
```

### 模型分工

各階段的模型（含唯讀 vs 可改正式程式碼的邊界）一律以共用 reference
[`references/model-policy.md`](references/model-policy.md) 為準：

| 階段 | 工作 | model | 可改正式程式碼 |
|------|------|-------|----------------|
| `/bug-investigate` | 證據收集、log／stacktrace／Git 歷史分析、模式比對、假說驗證 | `sonnet` | ✗ |
| `/bug-investigate` | 深度根因推理（僅 3-Strike 等升級條件成立時） | `opus` | ✗ |
| `/bug-fix` | 定位、搜尋相似修正、找測試範本、分析編譯／測試輸出 | `sonnet` | ✗ |
| `/bug-fix` | 修復實作、迴歸測試撰寫 | `opus` | ✓ |

- 模型必須以 Agent tool 的結構化 `model` 參數傳入；只在 prompt 寫「請使用 Sonnet」不算（CI 的 `agent-model` job 會 block）。
- 沒有根因確認就不進修正（鐵律）；`--verify-only` 不改程式碼，預設 `model: sonnet`。

## 使用範例

### 調查 Bug（主入口）

```bash
/bug-investigate 推播排程發送失敗         # 帶症狀描述開始（自動建立 Notion 條目 + 調查）
/bug-investigate NullPointerException   # 帶 stacktrace 關鍵字開始
/bug-investigate                        # 調查已存在的進行中 bug
/bug-investigate --resume               # 繼續上次的調查
```

### 修復並驗證

```bash
/bug-fix                  # 標準修復流程（分支檢查 + 鐵律檢查 + 迴歸測試 + merge 引導）
/bug-fix --verify-only    # 已修復，只要驗證 + 產出測試
```

### 結案

```bash
/bug-close    # merge 引導 + 從 Git diff 擷取修復細節 + 結案 + 同步知識庫
```

### 輔助指令

```bash
/bug-start 推播排程發送失敗               # 只建立條目，不調查（適合先立案再安排）
/bug-update 關鍵 log：NPE at PushService.java:235  # 補充調查資訊
/bug-update log /opt/tomcat/logs/catalina.out       # 從檔案擷取 ERROR
```

### 重新開啟已結案 Bug

```bash
/bug-update reopen                                   # 顯示該專案近期已結案 Bug 清單，互動式選擇
/bug-update reopen SSO登入找不到使用者                  # 用關鍵字搜尋已結案 Bug
/bug-update reopen https://www.notion.so/abe41af9...  # 直接貼 Notion 頁面連結
```

> 不帶參數時會列出該專案近期已結案的 Bug，可輸入編號、關鍵字、或 Notion 連結來選擇。

> 搜尋過往 Bug 解法可直接在 Notion 的 Bug 知識庫中搜尋，不需額外指令。

### CREW meta 指令

```bash
/crew-init                 # 一鍵首次設定（4 階段含偵測跳過、--resume 中斷續跑）
/crew-doctor               # 環境健診 18 項（紅/黃/綠/選配）
/crew-doctor --quick       # 只跑紅燈必要項目
/crew-doctor --fix         # 健診同時自動修可修項
/crew-upgrade              # 檢查並更新所有 CREW plugins
/crew-upgrade --check      # 只檢查版本，不更新
```

---

## 跨專案支援

Plugin 透過 `git remote get-url origin` 自動偵測 Git Repo，比對 Notion 專案資料庫中的「Git Repo」欄位，自動關聯到正確的專案。

在不同專案目錄下執行 `/bug-start`，會自動對應不同的 Notion 專案，無需手動切換。

### 新增專案（/project-add）

在新專案目錄下執行 `/project-add`，自動完成：

1. **偵測 Git Repo** 識別碼（支援公司 GitLab 與 GitHub）
2. **偵測技術棧**（掃描 pom.xml / build.gradle）
3. **判斷專案類型**：
   - **簡單型** — 單 WAR/JAR、Maven 單模組
   - **產品型** — Gradle 多模組、`kernel/` 外部資源、Solr/Hazelcast 中介軟體
4. **偵測 DB 類型**（MSSQL / MySQL / PostgreSQL / H2）
5. **同步 Notion** — 建立或更新專案條目，套用對應頁面模版
6. **可選安裝 DB MCP**（[DBHub](https://github.com/bytebase/dbhub)）：
   ```bash
   # 專案級安裝（推薦）
   claude mcp add dbhub --scope project -- \
     npx @bytebase/dbhub --transport stdio \
     --dsn "sqlserver://user:pwd@host:1433/database"
   ```
7. **檢查 CLAUDE.md** — 提醒 commit + push 讓團隊共用
8. **同步更新**所有 Workflow 設定檔（bug-workflow + feature-workflow）

已存在的專案也可用 `/project-add` 更新資訊（主機、部署方式等）。

## 設定檔

設定檔儲存位置由使用者在 `/bug-setup` 時選擇：

| 環境 | 路徑 | 適用場景 |
|------|------|---------|
| 公司 | `~/.claude-company/bug-workflow-config.md` | 團隊共用 Notion Workspace |
| 個人 | `~/.claude/bug-workflow-config.md` | 私人 Notion Workspace |

Skill 執行時會依序檢查公司 → 個人路徑，讀取第一個找到的設定檔。

設定檔包含：
- Notion 資料庫 Data Source ID
- 專案對應表
- 欄位對照表

可手動編輯此檔案，或透過 `/bug-setup` 重新設定。
