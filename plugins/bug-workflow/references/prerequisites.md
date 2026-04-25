# 共用前置檢查

所有 CREW Skill（除 `bug-setup`、`plan-setup`、`project-add` 本身外）在流程開始前必須執行以下檢查。

Setup Skill（`bug-setup`、`plan-setup`）執行第 0 項基礎環境檢查，其餘項目跳過。

---

## 檢查項目

### 0. 基礎環境是否就緒？（僅 setup 時檢查）

`bug-setup` 和 `plan-setup` 在最開頭執行此檢查，確保後續所有 MCP 安裝能正常運作。

**檢查 Node.js：**

```bash
node --version 2>/dev/null
npx --version 2>/dev/null
```

- **兩者皆可用** → 繼續
- **不可用** → 提示並中止：

  **macOS / Linux：**
  ```
  ⚠️ 未偵測到 Node.js。CREW 的 MCP Server（Notion、Playwright、DBHub 等）皆需要 Node.js 執行。

  安裝方式（擇一）：
    • Homebrew：brew install node
    • nvm：curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash && nvm install --lts
    • 官網下載：https://nodejs.org/

  安裝完成後重新啟動終端，再次執行此指令。
  ```

  **Windows：**
  ```
  ⚠️ 未偵測到 Node.js。CREW 的 MCP Server（Notion、Playwright、DBHub 等）皆需要 Node.js 執行。

  安裝方式（擇一）：
    • 官網下載（推薦）：https://nodejs.org/ → 下載 LTS 版 → 安裝時勾選「Add to PATH」
    • winget：winget install OpenJS.NodeJS.LTS
    • WSL2 環境：sudo apt install nodejs npm

  安裝完成後重新啟動 Claude Code，再次執行此指令。
  ```

**檢查 Git：**

```bash
git --version 2>/dev/null
```

- **可用** → 繼續
- **不可用** → 提示並中止：

  **macOS：**
  ```
  ⚠️ 未偵測到 Git。

  安裝方式：xcode-select --install
  ```

  **Windows：**
  ```
  ⚠️ 未偵測到 Git。

  安裝方式：
    • 官網下載（推薦）：https://git-scm.com/download/win
    • winget：winget install Git.Git
  安裝時建議勾選「Git from the command line and also from 3rd-party software」。
  ```

  **Linux：**
  ```
  ⚠️ 未偵測到 Git。

  安裝方式：sudo apt install git（Ubuntu/Debian）或 sudo yum install git（CentOS/RHEL）
  ```

**偵測作業系統的方式：**

```bash
uname -s 2>/dev/null || echo "Windows"
# Darwin → macOS
# Linux → Linux
# MINGW* / MSYS* / CYGWIN* → Windows (Git Bash / MSYS2)
# 指令不存在 → Windows (CMD / PowerShell)
```

### 1. CLAUDE.md 是否存在？

檢查當前專案根目錄（`pwd` 或 Git root）是否有 `CLAUDE.md`。

- **存在** → 繼續
- **不存在** → 提示並中止：
  ```
  ⚠️ 當前專案尚未初始化。
  請先執行 /init 建立 CLAUDE.md，讓 Claude Code 了解專案架構。
  建立後建議 commit 並 push，讓團隊成員共用。
  ```

### 2. Workflow 設定是否存在？

依序檢查：
1. `~/.claude-company/bug-workflow-config.md`
2. `~/.claude/bug-workflow-config.md`
3. `~/.claude-company/feature-workflow/config.md`（新階層式格式）
4. `~/.claude/feature-workflow/config.md`（新階層式格式）
5. `~/.claude-company/feature-workflow-config.md`（舊格式，向下相容）
6. `~/.claude/feature-workflow-config.md`（舊格式，向下相容）

- **至少找到一個** → 繼續
- **全部不存在** → 提示並中止：
  ```
  ⚠️ 尚未完成 Workflow 初始設定。
  請先執行 /bug-setup（Bug 工作流）或 /plan-setup（功能開發工作流）。
  ```

> 若找到舊格式 feature-workflow 設定（第 5、6 項），在控制台顯示一次提示：
> `💡 偵測到舊版設定檔格式。建議執行 /plan-setup --migrate 遷移到階層式目錄結構。`

### 3. 當前專案是否已註冊？

從 `git remote get-url origin` 解析 Git Repo 識別碼，比對設定中的專案對應：
- bug-workflow：比對設定檔「專案對應」表
- feature-workflow（新格式）：檢查 `projects/{sanitized-repo-id}.md` 是否存在
- feature-workflow（舊格式）：比對設定檔「專案對應」表

- **已註冊** → 繼續，取得對應的 Notion 專案名稱
- **未註冊** → 提示（非中止，部分 Skill 仍可使用）：
  ```
  ⚠️ 當前專案尚未註冊到 Notion。
  建議執行 /project-add 將專案加入 Notion 專案資料庫。
  ```

---

## 適用範圍

| Skill | 需要前置檢查？ | 說明 |
|-------|:---:|------|
| `bug-setup` | ⚠️ | 只檢查第 0 項（基礎環境），其餘跳過 |
| `plan-setup` | ⚠️ | 只檢查第 0 項（基礎環境），其餘跳過 |
| `project-add` | ⚠️ | 只檢查第 2 項（設定檔），不檢查第 1、3 項 |
| `bug-start` | ✅ | 完整檢查 1 + 2 + 3 |
| `bug-update` | ✅ | 完整檢查 1 + 2 + 3 |
| `bug-close` | ✅ | 完整檢查 1 + 2 + 3 |
| `plan-start` | ✅ | 完整檢查 1 + 2 + 3 |
| `plan` | ✅ | 只檢查第 1 項 |
| `plan-build` | ✅ | 只檢查第 1 項 |
| `plan-verify` | ✅ | 只檢查第 1 項 |
| `plan-review` | ✅ | 只檢查第 1 項 |
| `plan-close` | ✅ | 完整檢查 1 + 2 + 3 |
| `plan-sync` | ✅ | 完整檢查 1 + 2 + 3 |
| `plan-status` | ✅ | 只檢查第 1 項 |
| `plan-stack` | ✅ | 只檢查第 1 項 |
