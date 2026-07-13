---
name: crew-init
description: CREW 一鍵首次設定 —— 依序執行 /bug-setup → /plan-setup 並提示 /init 與 /project-add，含跳過邏輯與斷點續跑。當使用者提到 /crew-init、「CREW 一鍵設定」、「初始化 CREW」時觸發此 Skill。
---

# crew-init — CREW 一鍵首次設定

統合首次設定流程，讓新使用者只記得一個指令：

```
/crew-init
```

依序執行：
1. `/bug-setup`（建立 Notion 資料庫 + bug-workflow 設定檔）
2. `/plan-setup`（匯入共用 ID + feature-workflow 設定）
3. 提示 `/init`（如當前專案無 CLAUDE.md）
4. 提示 `/project-add`（如當前專案未註冊）

---

## 紀律護欄

> 紀律護欄：`../../references/discipline-preamble.md`（通用紀律）＋ `../../references/anti-rationalizations.md`「crew-init 專用」＋ `../../references/boundaries.md`「crew-init」段。

---

## 使用方式

```
/crew-init                    # 完整跑首次設定流程
/crew-init --skip-bug         # 已執行 /bug-setup，跳過該步
/crew-init --skip-plan        # 已執行 /plan-setup，跳過該步
/crew-init --resume           # 從中斷點續跑（自動判斷已完成步驟）
```

---

## 前置檢查

執行前自動檢查（不通過則先處理）：

| 項目 | 不通過時 |
|------|---------|
| Node.js ≥ 18 | 顯示對應 OS 安裝指令並終止 |
| Git | 顯示對應 OS 安裝指令並終止 |
| Notion MCP 已安裝 | 提示 `claude plugin install notion`，等使用者完成後重跑 |

進階檢查交由 `/crew-doctor`（完整 18 項，含必要 8 項），本 skill 只跑上表必要 3 項即可開始。

---

## 流程

### 階段 1：bug-workflow 設定

#### 1a. 偵測是否已設定

檢查設定檔是否存在（依序）：
1. `~/.claude-company/bug-workflow-config.md`
2. `~/.claude/bug-workflow-config.md`

**已存在** → 標示為 ✅ 跳過，進階段 2。
**不存在** → 進 1b。

#### 1b. 觸發 /bug-setup

提示使用者：

```
階段 1/4：建立 bug-workflow 設定
即將執行 /bug-setup，這會：
  - 偵測 Notion Workspace 中的「任務追蹤工具」「專案資料庫」資料庫
  - 若不存在則引導從零建立（含標準欄位 + Views + Relation）
  - 產出設定檔到 ~/.claude-company/bug-workflow-config.md

需要你的互動（選資料庫、確認 ID 等）

[Enter 繼續，Ctrl+C 終止]
```

呼叫 `/bug-setup` 流程（同 plugin 內可直接觸發），完成後驗證設定檔存在。

#### 1c. 失敗處理

bug-setup 失敗或使用者中斷 → 停止 crew-init，提示「下次可用 `/crew-init --resume` 從這裡續跑」。

### 階段 2：feature-workflow 設定

#### 2a. 偵測是否已設定

檢查設定目錄（新版階層式）：
1. `~/.claude-company/feature-workflow/config.md`
2. `~/.claude/feature-workflow/config.md`

若以上皆不存在，再檢查舊單一檔格式（向下相容，同 `/plan-setup` 的偵測邏輯）：
3. `~/.claude-company/feature-workflow-config.md`
4. `~/.claude/feature-workflow-config.md`

**新版或舊版任一存在** → 標示為 ✅ 跳過，進階段 3（偵測到舊版時附註：可執行 `/plan-setup --migrate` 遷移到新階層式目錄，非必要）。
**皆不存在** → 進 2b。

#### 2b. 觸發 /plan-setup

提示：

```
階段 2/4：建立 feature-workflow 設定
即將執行 /plan-setup，這會：
  - 自動匯入 bug-workflow 共用的 Notion ID（任務追蹤工具、專案資料庫）
  - 提示是否建立「功能設計庫」資料庫（選填）
  - 偵測或設定常用技術棧
  - 產出 ~/.claude-company/feature-workflow/config.md + stacks/

[Enter 繼續]
```

呼叫 `/plan-setup`，完成後驗證 config.md 存在。

### 階段 3：當前專案 CLAUDE.md

#### 3a. 偵測

讀取當前 working directory 是否有 `CLAUDE.md`：

```bash
test -f CLAUDE.md
```

**有** → 標示為 ✅ 跳過，進階段 4。
**無** → 進 3b。

#### 3b. 提示

```
階段 3/4：當前專案 CLAUDE.md
偵測當前目錄：{pwd}
此目錄無 CLAUDE.md，無法執行 plan-* / bug-* 指令。

請執行（Claude Code 內建指令，非本 plugin）：

  /init

執行後建議將 CLAUDE.md commit 到 Git，讓團隊共用：
  git add CLAUDE.md && git commit -m "docs: 新增 CLAUDE.md" && git push

[Enter 我已執行 /init，或 s 跳過此步驟]
```

使用者選擇 Enter 後重新檢查；選 s 則標示為 ⚠️ 跳過。

### 階段 4：專案註冊

#### 4a. 偵測

讀取 Git remote 取得 repo identifier：

```bash
git remote get-url origin
# 解析為 {owner}/{repo} 或 {project}/{repo}
```

檢查 `~/.claude-company/feature-workflow/projects/{repo-id}.md` 是否存在。

**已存在** → 標示為 ✅ 跳過，進結尾摘要。
**不存在** → 進 4b。

#### 4b. 提示

```
階段 4/4：專案註冊
當前專案：{repo-id}
此專案尚未註冊，無法用 plan-* / bug-* 指令。

請執行：

  /project-add

這會：
  - 偵測專案類型（簡單型 / 產品型）
  - 偵測建置工具、技術棧、DB 類型
  - 註冊到 Notion 專案資料庫
  - 可選安裝 DB MCP（DBHub）

[Enter 我已執行 /project-add，或 s 跳過]
```

### 5. 結尾摘要

```
═══════════════════════════════════════════
🎉 CREW 一鍵設定完成
═══════════════════════════════════════════

階段 1/4 bug-workflow 設定        ✅
階段 2/4 feature-workflow 設定    ✅
階段 3/4 當前專案 CLAUDE.md       ✅
階段 4/4 專案註冊                  ✅

可用指令：
  /bug-investigate              開始調查 Bug
  /plan-start <任務簡述>        建立功能任務
  /plan-next                    查看下一步建議
  /crew-doctor                  健診環境

進階：
  /crew-doctor                  18 項依賴完整檢查
  /crew-upgrade                 更新 CREW plugins
```

若有跳過步驟，摘要會顯示 ⚠️ 並提示對應的單獨指令補做。

---

## --resume 模式

省略階段 1-4 中已 ✅ 的部分，直接進到第一個未完成階段。

實作上 `--resume` = 跑每階段的偵測（1a/2a/3a/4a），自動跳過 ✅，從第一個未完成處執行。
與不加 `--resume` 的差別：不加時每階段都顯示提示「即將執行 X」；加 `--resume` 時跳過提示直接執行。

---

## 何時不用

- 只想設定 bug 側 → 改用 `/bug-setup`
- 只想設定 feature 側 → 改用 `/plan-setup`
- 只想註冊專案到 Notion → 改用 `/project-add`
- 只想初始化 CLAUDE.md → 改用內建 `/init`
- 只想做 CREW 環境檢查 → 改用 `/crew-doctor`

---

## Gotchas

- **/bug-setup 或 /plan-setup 中斷不會自動回滾**：使用者選 Ctrl+C 後可能留下半成品設定檔。crew-init 不嘗試清理，由使用者下次用 `--resume` 接續
- **Notion OAuth 未完成**：bug-setup 第一次使用 Notion MCP 會觸發 OAuth，使用者必須切瀏覽器完成授權。crew-init 不能加速這部分
- **同名 Notion Workspace**：bug-setup 偵測 Workspace 時若使用者有多個同名 → 由 bug-setup 內部處理，crew-init 不介入
- **路徑空格**：當前目錄含空格時 `git remote` 不受影響，但專案路徑要正確引用

---

## 邊界情況

- **CLAUDE.md 存在但不完整**：本 skill 只檢查存在，不解析內容。內容不完整由 plan-* / bug-* 各自處理
- **使用者跳過所有步驟（連按 s）**：摘要顯示全部 ⚠️，提示「至少需完成階段 1+2 才能用大部分 Skill」
- **非 Git 專案**：階段 4 偵測 `git remote` 失敗時，標示為 ⏭️ 不適用（非 git 專案不需註冊）
- **WSL2 / Windows 桌面版混用**：設定檔路徑共享 `~/.claude-company/`，重複設定會偵測為已存在自動跳過
