---
name: plan-close
description: 一次性批次同步 .spec/ 設計文件到 Notion（含 deploy.sql）、更新狀態、同步知識庫、提交 Git，用於 feature/.spec 任務結案。當使用者輸入 /plan-close，或提到「feature 結案」、「同步 spec 到 Notion 並結案」時觸發此 Skill。
---

# plan-close — 統一結案（批次 Notion 同步）

將 `.spec/{slug}/` 中的所有設計文件一次性批次同步到 Notion，更新狀態，同步到知識庫，並提交設計文件到 Git。**整個流程僅 3-5 次 Notion API 呼叫**。

---

## 設定目錄

依 plugin 根目錄 `references/config-resolver.md`（相對 SKILL.md 為 `../../references/`）的漸進式載入邏輯讀取設定。本 Skill 需要：
- **第 1 層**：`config.md`（Notion IDs — 功能設計庫 / 專案資料庫）
- **第 2 層**：`projects/{repo-id}.md`（專案對應、技術棧 ID）
- **第 3 層**：`stacks/{id}.md`（技術棧定義，用於設計庫同步）

Bug 類型還需 bug-workflow 設定檔（`~/.claude-company/bug-workflow-config.md` 或 `~/.claude/bug-workflow-config.md`）。

---

## 前置條件

- 已使用 `/plan-start` 建立任務
- 已完成規劃和開發（`.spec/{slug}/` 下有設計文件）
- 程式碼已 commit

> **前置檢查**：參照 plugin 根目錄 `references/prerequisites.md`（相對 SKILL.md 為 `../../references/`）執行完整前置檢查（CLAUDE.md + 設定目錄 + 專案註冊）。

---

## 流程

### 1. 定位活躍任務

與 `/plan` 相同邏輯。讀取 `.spec/{slug}/README.md` 取得 `type`、`notion_page_id`、`notion_url`。

### 2. 收集所有本地設計文件

掃描 `.spec/{slug}/` 目錄，列出所有可用文件：

**Feature 類型**：

| 檔案 | Notion 區塊 | 存在？ |
|------|------------|--------|
| spec.md | 📐 技術規格 | ✅/❌ |
| db.md | 🗄️ 資料庫設計 | ✅/❌ |
| arch.md | 🏗️ 架構設計 | ✅/❌ |
| deploy-checklist.md | 🚀 上線前置作業 | ✅/❌ |
| deploy.sql | 🗄️ 資料庫設計 → 「部署 SQL」子區塊 ＋ 🚀 部署狀態（初始化，每筆預設「待執行」） | ✅/❌ |
| files.md | 📁 程式碼清單 | ✅/❌ |
| review.md | 📋 程式碼審查（新增區塊） | ✅/❌ |
| verify.md | 🧪 驗證報告（新增區塊） | ✅/❌ |
| log.md | 📝 開發日誌 | ✅/❌ |

**Bug 類型**：

| 檔案 | Notion 區塊 | 存在？ |
|------|------------|--------|
| investigation.md | 🔍 調查過程 | ✅/❌ |
| root-cause.md | 🧠 根因分析 | ✅/❌ |
| fix.md | ✅ 修復方案 | ✅/❌ |
| log.md | 📝 經驗教訓 | ✅/❌ |

### 3. 從 Git 擷取變更摘要

從專案設定檔讀取 `prod_branch`（PROD 分支），用作 merge-base 計算 diff：

```bash
# {prod_branch} 從 projects/{repo-id}.md 的 prod_branch 欄位讀取
git branch --show-current
git log --oneline $(git merge-base HEAD {prod_branch})..HEAD
git diff $(git merge-base HEAD {prod_branch})..HEAD --stat
git diff $(git merge-base HEAD {prod_branch})..HEAD
```

> 若 `prod_branch` 未設定（舊專案），回退邏輯：先取 `origin/HEAD` 指向的分支，若無則依序嘗試 `production` → `master` → `main`。

根據 CLAUDE.md 的架構描述，產出分層變更摘要。

### 4. 智慧判斷目標狀態

狀態推斷邏輯：
- 使用者輸入含「完成」、「done」、「上線」、「結案」→ `已完成`
- 含「測試」、「QA」→ `測試中`
- 無法判斷 → 詢問，預設 `測試中`

### 5. deploy-checklist 勾選檢查

#### 觸發條件

- `.spec/{slug}/deploy-checklist.md` 存在
- 任務類型為 Feature（Bug 類型跳過）

#### 檢查流程

1. 讀取 `.spec/{slug}/deploy-checklist.md`
2. 解析所有 checkbox 行（格式：`- [ ]` 未完成 / `- [x]` 已完成）
3. 統計 checked / total
4. 全部勾完（或無 checkbox）→ 繼續流程
5. 有未勾選項目 → 顯示警告：

```
⚠️ 上線前置作業未完成！

📋 deploy-checklist.md 狀態：{checked}/{total} 項已完成

未完成項目：
  ❌ {未勾選項目 1}
  ❌ {未勾選項目 2}

是否仍要繼續結案？
  1. 繼續（我已確認這些項目不需要，或已透過其他方式完成）
  2. 中止，先完成前置作業
```

- 選 1 → 在 log.md 記錄「使用者確認跳過未完成的 deploy-checklist 項目」，繼續『一次性 Notion 批次更新』一節
- 選 2 → 終止 plan-close

#### deploy-checklist 不存在時

- 若 db.md 或 db.sql 存在（有 DB 變更但未產生 checklist）→ 提示：「偵測到 DB 設計文件但無 deploy-checklist.md，建議先執行 /plan-db 重新產出」
- 若無 DB 相關文件 → 靜默跳過

### 6. 一次性 Notion 批次更新

**5-1. Fetch 現有頁面**（1 次 `notion-fetch`）

使用 `notion_page_id`（從 README.md 取得）fetch 頁面。

**5-2. 更新頁面內容**（1 次 `notion-update-page` content）

將所有設計文件內容組合成一次 `update_content` 操作：

**Feature 類型**：

```
📐 技術規格 區塊 ← spec.md 內容
🗄️ 資料庫設計 區塊 ← db.md 內容 + deploy.sql 內容（若存在，以「部署 SQL」子區塊追加）
🏗️ 架構設計 區塊 ← arch.md 內容
🚀 上線前置作業 區塊 ← deploy-checklist.md 內容（含 checkbox 勾選狀態）
🚀 部署狀態 區塊 ← 若 deploy.sql 存在則建立（見下方 5-2a），每筆 SQL Step 預設「待執行」，供 /plan-deploy-confirm 後續回報執行狀態時讀寫
📁 程式碼清單 區塊 ← files.md 內容 + Git diff 產出的分層變更摘要
📝 開發日誌 區塊 ← 附加結案紀錄：
  ### [{日期}] 開發完成
  - **分支**：{branch}
  - **Commit 數**：{N}
  - **變更摘要**：{分層變更摘要}

若 review.md 存在，在「📝 開發日誌」前插入：
📋 程式碼審查 區塊 ← review.md 內容

若 verify.md 存在，在「📋 程式碼審查」後（或「📝 開發日誌」前）插入：
🧪 驗證報告 區塊 ← verify.md 內容
```

**5-2a. 建立「🚀 部署狀態」區塊**（僅 Feature 且 deploy.sql 存在）

`deploy.sql` 寫入「部署 SQL」子區塊後，一併建立「🚀 部署狀態」追蹤區塊，作為 `/plan-deploy-confirm` 回流機制的寫入標的。此處只**初始化**（每筆預設「待執行」），實際執行結果由 `/plan-deploy-confirm` 之後覆寫。

依 `-- Step N：{描述}` 註解切割 deploy.sql，每個 Step 產生一列，狀態一律填「⏳ 待執行」：

```markdown
## 🚀 部署狀態

### 最後執行：（尚未執行）

| Step | 描述 | 狀態 | 執行時間 | 備註 |
|------|------|------|---------|------|
| 1 | 建立 users 表 | ⏳ 待執行 | — | — |
| 2 | 建立 email 唯一索引 | ⏳ 待執行 | — | — |

### 執行紀錄

（尚無執行紀錄，執行後由 /plan-deploy-confirm 追加）

### 備註
（無）
```

> **契約**：區塊標題固定為「🚀 部署狀態」、狀態詞固定用「待執行」，與 `/plan-deploy-confirm` 讀寫的名稱一致。若 deploy.sql 無 `-- Step N` 註解無法分段，退回單一列（Step 1 = 整個 deploy.sql，狀態「待執行」）。

**Bug 類型**：

```
🔍 調查過程 區塊 ← investigation.md 內容
🧠 根因分析 區塊 ← root-cause.md 內容
✅ 修復方案 區塊 ← fix.md 內容 + Git diff 分層摘要
📝 經驗教訓 區塊 ← log.md 或自動產生的經驗教訓
```

**5-3. 更新 Properties**（1 次 `notion-update-page` properties）

**Feature**：

| 欄位 | 值 |
|------|-----|
| 狀態 | 『智慧判斷目標狀態』判斷結果 |
| 開發階段 | `測試中` |
| 修復分支 | 當前 Git branch |

**Bug**：

| 欄位 | 值 |
|------|-----|
| 狀態 | 『智慧判斷目標狀態』判斷結果 |
| 根因分類 | 從 root-cause.md 推斷（邏輯錯誤/資料異常/設定問題/第三方API/效能/權限/前端UI） |
| 修復分支 | 當前 Git branch |

### 7. 同步到知識庫

**Feature → 功能設計庫**（1 次 `notion-create-pages`）

同步邏輯：

| 欄位 | 值 |
|------|-----|
| Name | 功能標題 |
| Tags | 自動推測（API/報表/標籤/推播/排程 等） |
| 設計類型 | 依文件齊全度判斷 |
| 技術棧 | 設定檔中的技術棧 ID |
| 參考連結 | Notion 頁面 URL |
| 專案資料庫 | 同一專案 |

**Bug → Bug 知識庫**（1 次 `notion-create-pages`）

複用 `bug-close` 的同步邏輯：

| 欄位 | 值 |
|------|-----|
| Name | Bug 標題 |
| Tags | 自動推測 |
| 難易度 | 依修改檔案數和行數判斷 |
| 專案資料庫 | 同一專案 |
| 參考連結 | Notion 頁面 URL |

### 8. Feature-Bug 關聯（僅 Bug 且有 related_feature）

若 README.md 中 `related_feature` 不為空：

1. 從 `.spec/{related_feature}/README.md` 取得 `notion_page_id`
2. `notion-fetch` 取得關聯 Feature 的 Notion 頁面（1 次）
3. 在「📝 開發日誌」區塊追加：

```
### [{日期}] 🔴 相關 Bug
- Bug: {Bug 名稱}（{Bug Notion URL}）
- 根因: {root-cause.md 摘要}
- 修復: {fix.md 摘要}
```

4. `notion-update-page` 更新 Feature 頁面（1 次）

### 9. 提交 .spec/ 設計文件到 Git

將最終版本的設計文件提交。`plan-start` 在 `.gitignore` 寫入的是整個 `.spec/`（排除目錄），此時用 `!.spec/{slug}/` 反向取消忽略**無效**（Git 不會遞迴進入已被排除的目錄），因此改用 `git add -f` 強制加入：

```bash
# -f 強制加入被 .gitignore 忽略的檔案；一旦加入即為 tracked，
# 之後的修改 Git 會正常追蹤，不需再次 -f。
git add -f .spec/{slug}/
git commit -m "docs: 新增 {slug} 設計文件"
```

### 10. 更新 _index.md 與 README.md status

**9-1. 更新 `.spec/{slug}/README.md` 的 status 欄位**

將 README.md frontmatter 的 `status` 改為 `已結案`（原值為 plan-start 寫入的 `需求分析` / `調查中` 等）：

```yaml
status: 已結案
```

> **契約**：此值固定用「已結案」，與 `/plan-deploy-confirm` 『定位待回報任務』一節掃描本地待回報任務（`.spec/*/` 含 deploy.sql 且 `status: 已結案`）所讀取的狀態詞一致。缺這一步，deploy.sql 的執行回流機制永遠掃不到已結案任務。

**9-2. 更新 `_index.md`**

將任務從「進行中」移至「已完成」區段：

```markdown
## 已完成

| slug | 類型 | 名稱 | 完成日期 | Notion |
|------|------|------|---------|--------|
| {slug} | {type} | {name} | {日期} | [連結]({url}) |
```

**不刪除 `.spec/{slug}/` 目錄**，保留供未來 Bug 關聯匹配。

### 11. 回傳結果

```
結案完成！

📊 Notion 頁面：{URL}（已更新）
📚 知識庫：{知識庫條目 URL}（已同步）
{📎 Feature 關聯：已更新 {related_feature} 的開發日誌}
📁 設計文件：已提交到 Git

Notion API 呼叫統計：{N} 次（fetch: 1, update: 2, create: 1{, 關聯更新: 2}）

後續事項：
  📋 測試驗證：在 Notion 頁面勾選驗證項目
  🔀 Git 合併：{根據 CLAUDE.md Git Flow 產出合併建議}
```

---

## 何時不用

close 組 + sync 組 —— feature/.spec 任務結案用本 skill；bug 型結案用 /bug-close；未結案的中途同步用 /plan-sync。

- bug 型任務結案 → 改用 `/bug-close`
- 未結案的中途同步 → 改用 `/plan-sync`
- 更新單一 bug 頁 → 改用 `/bug-update`
- 部署 SQL 執行回報 → 改用 `/plan-deploy-confirm`

---

## Gotchas

- **一次 update_content 的大小限制**：Notion API request body 約 2MB 上限。大型功能的設計文件（spec.md + db.md + arch.md 合計）可能超過此限制，需分批呼叫 `update_content`。
- **Bug 類型需讀取兩個設定檔**：知識庫 ID（Bug 知識庫）在 bug-workflow 設定檔中，只讀 feature-workflow 設定檔會靜默跳過知識庫同步。Bug 類型結案時，兩個 workflow 的設定檔都要讀取。
- **提交 .spec/ 用 `git add -f`**：`plan-start` 在 `.gitignore` 忽略整個 `.spec/`，而 Git 無法用 `!.spec/{slug}/` 反向取消對「已排除目錄」的忽略（re-include 對已被排除目錄下的內容無效）。故一律用 `git add -f .spec/{slug}/`；力求不改動 `.gitignore`，避免規則順序踩坑。強制加入後檔案即成 tracked，後續修改 Git 會正常追蹤。
- **Notion 呼叫次數統計**：承諾 3-5 次，但 Bug 有 `related_feature` 時會多 2 次（fetch + update 關聯 Feature 頁面），實際可達 7 次。回傳結果的統計數字要如實反映。

---

## 邊界情況

- **notion_page_id 為空**：建議先用 `/plan-sync` 建立 Notion 條目
- **無設計文件**：僅更新 Properties 和開發日誌
- **diff 過大（> 500 行）**：僅摘要檔案清單和分層變更
- **知識庫 ID 為空**：跳過知識庫同步
- **related_feature 的 Notion 頁面不存在**：跳過關聯更新，提示使用者
- **Notion API 失敗**：顯示已完成和失敗的步驟，建議用 `/plan-sync` 重試
- **CLAUDE.md 無 Git Flow 描述**：使用通用提示
