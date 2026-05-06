---
name: plan-start
description: 建立 Notion 條目 + .spec/ 本地規劃目錄 + Git branch 的統一入口，含退出驗證（S1~S7）確保必填欄位完整。支援 feature 和 bug 兩種類型。當使用者提到「plan-start」、「新任務」、「開始規劃」時觸發此 Skill。
---

# plan-start — 統一任務入口（本地規劃模式）

在 Notion「任務追蹤工具」建立條目，同時在專案根目錄建立 `.spec/{slug}/` 本地規劃目錄，並可選建立 Git branch。支援 Feature 和 Bug 兩種類型。

---

## 設定目錄

依 `references/config-resolver.md` 的漸進式載入邏輯讀取設定。本 Skill 需要：
- **第 1 層**：`config.md`（Notion IDs）
- **第 2 層**：`projects/{repo-id}.md`（專案對應、技術棧 ID）

Bug 類型還需檢查 bug-workflow 設定檔（`~/.claude-company/bug-workflow-config.md` 或 `~/.claude/bug-workflow-config.md`）。

若設定目錄不存在，提示使用者先執行 `/plan-setup` 或 `/bug-setup`。

---

## 流程

> **前置檢查**：參照 bug-workflow plugin 的 `references/prerequisites.md` 執行完整前置檢查（CLAUDE.md + 設定檔 + 專案註冊）。

### 1. 解析使用者輸入

使用者會以以下格式觸發：

```
/plan-start <任務簡述> [選項]
```

**類型推斷**：
- 明確指定：`/plan-start feature 推播標籤查詢` 或 `/plan-start bug SSO 登入錯誤`
- 關鍵字推斷：輸入含「bug」、「錯誤」、「問題」、「修復」、「異常」→ type=bug
- 預設為 feature

**Bug 關聯選項**：
- `--related <feature-slug>`：手動指定關聯的 feature

### 2. 偵測環境資訊（自動專案對應）

自動偵測環境：

```bash
git branch --show-current 2>/dev/null || echo ""
pwd
git remote get-url origin 2>/dev/null || echo ""
```

Git Repo 識別碼解析規則：
- Git host 含 `intumit`（公司 GitLab）→ 只取 `{group}/{repo}`
- 其他（GitHub 等）→ 加上 host：`{host}/{group}/{repo}`
- 去除 `.git` 後綴

自動專案對應：用 Git Repo 識別碼轉換為檔名（`/` → `--`），檢查 `projects/{sanitized-id}.md` 是否存在。匹配失敗則進入互動式選擇。

### 3. 互動式補充資訊

#### Feature 類型

1. **所屬專案**（若自動偵測失敗）
2. **優先順序**（預設「中」）：`高` / `中` / `低`
3. **難度**（預設「中」）：`小` / `中` / `大`

#### Bug 類型

1. **所屬專案**（若自動偵測失敗）
2. **環境**（預設「正式」）：`測試` / `UAT` / `正式`
3. **優先順序**（預設「中」）：`高` / `中` / `低`

### 4. 產生 slug

從任務簡述產生英文 slug：
- 中文 → 翻譯為簡短英文（如「推播標籤查詢」→ `push-tag-query`）
- 已經是英文 → 轉為 kebab-case
- 確認 `.spec/{slug}/` 不存在，若存在則加數字後綴

### 5. 偵測負責人

在建立 Notion 條目前，自動偵測負責人以填入「負責人」（people 類型）欄位：

1. 取得 Git 提交 email：
   ```bash
   git config user.email 2>/dev/null || echo ""
   ```
2. 呼叫 `notion-get-users` 取得 Notion 工作區使用者列表
3. 比對 Git email 與 Notion 使用者的 email 欄位（case-insensitive）
4. 若匹配成功 → 記錄該使用者的 Notion user ID，後續填入「負責人」欄位
5. 若匹配失敗或 API 呼叫失敗 → 跳過，不阻塞流程，在回傳結果中提示「負責人未自動設定，請至 Notion 手動指派」

> **注意**：`notion-get-users` 回傳的使用者物件包含 `id`、`name`、`person.email` 等欄位。比對時使用 `person.email`。

### 6. 建立 Notion 條目

#### Feature 類型

使用 `notion-create-pages` 在「任務追蹤工具」建立，Properties：

| 欄位 | 值 |
|------|-----|
| 任務名稱 | 使用者提供的任務簡述 |
| 任務類型 | `["💬 功能要求"]` |
| 狀態 | `進行中` |
| 優先順序 | 使用者選擇 |
| 難度 | 使用者選擇 |
| 開發階段 | `需求分析` |
| 專案資料庫 | 關聯的專案頁面 URL |
| 負責人 | 步驟 5 偵測到的 Notion 使用者（若有） |

#### 兩步法建立頁面

**Step A**：使用 `post-page` 建立頁面（僅 properties，不帶 children）。

> **database_id 解析**：`config.md` 中的 Data Source ID 不能直接用於 `post-page` 的 `parent.database_id`。需先依照 `references/plan-common.md` 的「Notion database_id 解析」邏輯，呼叫 `retrieve-a-data-source` 取得底層 `database_id`。

**Step B**：取得 `page_id` 後，使用 `patch-block-children` 追加 `references/notion-page-template.md` 的標準 8 區塊模板。

**錯誤處理**：
- Step A 失敗 → 本地 `.spec/` 目錄照常建立，`notion_page_id` 留空
- Step B 失敗 → 頁面已建立（有 properties 無 body），記錄到 log.md

#### Bug 類型

使用 `notion-create-pages`，Properties 同 `bug-start`：

| 欄位 | 值 |
|------|-----|
| 任務名稱 | 使用者提供的任務簡述 |
| 任務類型 | `["🐞 錯誤"]` |
| 狀態 | `進行中` |
| 優先順序 | 使用者選擇 |
| 環境 | 使用者選擇 |
| 專案資料庫 | 關聯的專案頁面 URL |
| 負責人 | 步驟 5 偵測到的 Notion 使用者（若有） |

頁面 content 使用 bug-start 的標準模板。建立方式同 Feature 的兩步法（Step A + Step B），但模板內容改用 bug-start 的區塊。

### 7. 建立 .spec/ 本地規劃目錄

#### 7-1. 確保 .gitignore 包含 .spec/

檢查專案根目錄的 `.gitignore`，若不包含 `.spec/` 則追加：

```
# Local spec files (managed by plan-* skills)
.spec/
```

#### 7-2. 建立目錄結構

**Feature 類型**：

```bash
mkdir -p .spec/{slug}
```

建立 `README.md`：

```markdown
---
type: feature
name: {任務簡述}
slug: {slug}
status: 需求分析
notion_url: {Notion 頁面 URL}
notion_page_id: {Notion 頁面 ID}
branch: {Git branch 名稱，若後續建立}
tech_stack: {技術棧 ID，從 projects/{repo-id}.md 的 stack 欄位取得}
created: {當前日期 YYYY-MM-DD}
---

# {任務簡述}

## 需求描述

{使用者提供的描述，或待填寫}
```

**Bug 類型**：

```bash
mkdir -p .spec/{slug}
```

建立 `README.md`：

```markdown
---
type: bug
name: {任務簡述}
slug: {slug}
status: 調查中
notion_url: {Notion 頁面 URL}
notion_page_id: {Notion 頁面 ID}
branch: {Git branch 名稱，若後續建立}
related_feature: {關聯的 feature slug，若有}
related_feature_notion: {關聯 feature 的 Notion URL，若有}
created: {當前日期 YYYY-MM-DD}
---

# {任務簡述}

## 問題描述

{使用者提供的描述，或待填寫}
```

#### 7-3. Bug 自動關聯 Feature

**本地 `.spec/` 層關聯**：

若使用者指定 `--related <feature-slug>`：
- 驗證 `.spec/{feature-slug}/` 存在
- 讀取其 `README.md` 取得 `notion_url`、`notion_page_id`
- 填入 Bug README.md 的 `related_feature` 和 `related_feature_notion`

若未指定，嘗試智慧匹配：
1. 掃描 `.spec/` 下所有目錄的 `README.md`（type=feature 且 status 非「需求分析」）
2. 從 Bug 描述中擷取關鍵字（Controller 名稱、Service 名稱、表名等）
3. 比對各 feature 的 `spec.md`、`arch.md`、`db.md` 中的類別名和表名
4. 若匹配成功，提示使用者確認
5. 若無法判斷，跳過（使用者可後續手動指定）

**Notion 層 relation 關聯**：

本地關聯成功後，同步建立 Notion 的「相關任務」self-relation：

1. 從關聯 feature 的 `README.md` 取得 `notion_page_id`（已在本地關聯時讀取）
2. 使用 `notion-update-page` 設定 Bug 頁面的「相關任務」：
   ```json
   {
     "相關任務": {
       "relation": [{"id": "<feature-notion-page-id>"}]
     }
   }
   ```
3. 失敗 → 記錄到 `log.md`，不阻擋流程

若本地關聯未成功（`.spec/` 中無匹配 feature），嘗試 Notion 層盲搜（同 `/bug-start` Step 6.7 邏輯）：

1. 從 Bug 標題擷取關鍵字（去除停詞）
2. 使用 `API-query-data-source` 查詢同專案的 Feature 條目（任務類型 contains 💬 功能要求）
3. 標題比對，找到最相關的 Feature
4. 匹配成功 → patch-page 設定 relation
5. 匹配失敗 → 跳過，在回傳結果中提示可手動關聯

**Feature Branch 偵測**（同 `/bug-start` Step 6.8）：

若成功關聯到 Feature（本地或 Notion 層），進一步偵測 Feature 的開發分支：

1. 從 feature 的 `.spec/` README.md 取得 `branch` 欄位，或從 Notion 頁面讀取「修復分支」欄位
2. 驗證分支存在：`git branch -a | grep -F "<branch-name>"`
3. 分支存在 → 設定 Bug 的修復分支為 feature branch，詢問是否切換
4. 分支不存在 → 提示使用者選擇（建新分支 / 當前分支 / 手動指定）
5. 失敗 → 跳過，修復分支保持步驟 9 的設定

### 8. 更新 .spec/_index.md

讀取或建立 `.spec/_index.md`：

```markdown
# 任務索引

## 進行中

| slug | 類型 | 名稱 | 狀態 | 分支 | Notion | 建立日期 |
|------|------|------|------|------|--------|---------|
| {slug} | {feature/bug} | {名稱} | {狀態} | {branch} | [連結]({url}) | {日期} |

## 已完成

| slug | 類型 | 名稱 | 完成日期 | Notion |
|------|------|------|---------|--------|
```

在「進行中」表格新增一列。

### 9. 建立 Git branch

從專案設定檔讀取 `prod_branch`（PROD 分支），作為新分支的基準：

```
是否建立 Git branch？
1. 是，建立 {feature|hotfix}/{slug}（從 {prod_branch} 分支）
2. 是，自訂分支名稱
3. 否，稍後再建立
```

若選擇建立：
1. `git checkout {prod_branch} && git pull && git checkout -b {type}/{slug}`
   （feature → `feature/{slug}`，bug → `hotfix/{slug}`，從 PROD 分支建立）
2. 更新 Notion 條目的「修復分支」欄位
3. 更新 `.spec/{slug}/README.md` 的 `branch` 欄位

> 若 `prod_branch` 未設定（舊專案），回退到從當前分支建立，並提示使用者執行 `/project-add` 補充分支設定。

### 9.5 退出驗證（強制，不可跳過）

在回傳結果前，逐項檢查以下退出條件，確保 Notion 條目與本地 `.spec/` 的完整性。

#### 驗證方式

對 Notion 欄位的驗證，**一律用 `notion-fetch` 讀回頁面確認欄位有值**，不信任 Agent 在步驟 6 的記憶。

#### 自動驗證項目

| # | 檢查項目 | 驗證方式 | 失敗處理 |
|---|---------|---------|---------|
| S1 | Notion 頁面已建立 | `.spec/{slug}/README.md` 的 `notion_page_id` 非空 | 若步驟 6 Step A 已失敗（走降級路徑）→ 降為 ⚠️ WARN，提示稍後用 `/plan-sync` 補建；否則重試建立 |
| S2 | 專案資料庫已設定 | `notion-fetch` 讀回頁面，確認「專案資料庫」relation 欄位非空 | 從 `projects/{repo-id}.md` 取得 `notion_page_id`，用 `notion-update-page` 補上 relation |
| S3 | 修復分支已設定 | `.spec/{slug}/README.md` 的 `branch` 欄位非空 **且** `notion-fetch` 確認「修復分支」欄位非空 | 見下方 S3 特殊處理 |
| S4 | 開發階段已設定（僅 Feature） | Feature → `notion-fetch` 確認「開發階段」欄位 = `需求分析`；Bug → 跳過此項 | 用 `notion-update-page` 補上 |
| S5 | 負責人已設定 | `notion-fetch` 確認「負責人」欄位非空 | 僅提示「負責人未自動設定，請至 Notion 手動指派」 |
| S6 | .spec/ 目錄已建立 | `.spec/{slug}/README.md` 存在 | 重試建立 |
| S7 | _index.md 已更新 | `.spec/_index.md` 包含新 slug | 重試寫入 |

> **S1 條件式降級**：步驟 6 的設計允許 Notion API 不可用時繼續建立本地 `.spec/`（offline-first）。若步驟 6 Step A 已失敗，S1 不應阻擋整個流程，改為 WARN 並記錄。僅在 Step A 成功（頁面應已建立）但 `notion_page_id` 為空時才視為 BLOCK。

#### S3 特殊處理（刻意 friction）

若步驟 9 使用者選擇了「否，稍後再建立」，退出驗證時 **必須再次確認**（即使在 auto mode 下，**強制詢問**）：

```
⚠️ 修復分支尚未建立。
   Notion 的「修復分支」欄位將為空，可能影響團隊協作（其他成員無法從 Notion 得知開發分支）。

   確定不建立分支嗎？
   1. 建立分支（回到步驟 9 流程）
   2. 確定跳過，我稍後自己建立
```

選 1 → 回到步驟 9 的建立流程。
選 2 → S3 標記為 ⚠️ WARN（不阻擋），繼續。

#### 驗證結果分級

- **🔴 BLOCK**（S1, S2, S3, S6, S7）：必須解決後才能回傳結果
- **⚠️ WARN**（S4, S5）：記錄提醒但不阻擋

> S1 在步驟 6 Step A 已失敗（Notion 不可用）時，降級為 ⚠️ WARN。
> S3 在使用者明確確認跳過後，降級為 ⚠️ WARN。
> S4 對 Bug 類型自動跳過（Bug 不設定開發階段）。

#### 失敗自動修復

驗證失敗時，Agent **自行修復**（補呼叫 `notion-update-page` 等），不要求使用者手動操作。僅在自動修復也失敗時才提示使用者。

#### 驗證報告格式

寫入 `.spec/{slug}/log.md` 並在回傳結果中顯示：

```
退出驗證結果：
  ✅ S1 Notion 頁面已建立
  ✅ S2 專案資料庫：{專案名稱}
  ✅ S3 修復分支：{branch}
  ✅ S4 開發階段：需求分析
  ⚠️  S5 負責人未自動設定（email 不匹配）
  ✅ S6 .spec/{slug}/ 已建立
  ✅ S7 _index.md 已更新

  結論：{全部通過 / 有 N 項 WARN，建議處理後再進 plan-spec}
```

### 10. 回傳結果

```
任務已建立！

📋 Notion 頁面：{URL}
📁 本地規劃：.spec/{slug}/
🔀 Git branch：{branch}（若有）
📊 類型：{Feature / Bug}

退出驗證結果：
  {✅/⚠️} S1 Notion 頁面已建立
  {✅/⚠️} S2 專案資料庫：{專案名稱}
  {✅/⚠️} S3 修復分支：{branch}
  {✅/⚠️} S4 開發階段：{階段}
  {✅/⚠️} S5 負責人：{姓名 或 未設定}
  {✅/⚠️} S6 .spec/{slug}/ 已建立
  {✅/⚠️} S7 _index.md 已更新
  結論：{摘要}

後續可使用：
  • /plan-spec             — 技術規格
  • /plan-db               — DB 設計
  • /plan-arch             — 架構設計
  • /plan-build            — Agent Teams 產生程式碼
  • /plan-review           — Agent Teams 審查
  • /plan-status           — 查看所有任務狀態
  • /plan-close            — 結案並同步 Notion
```

---

## Gotchas

- **slug 翻譯品質影響全流程**：slug 會成為 `.spec/` 目錄名稱和 Git branch 名稱，一旦建立就很難改。中文翻譯成英文時，優先用專案中已有的術語（如 LineBC 專案中的「推播」→ `push` 而非 `broadcast`），保持與 codebase 一致。
- **_index.md 的 Markdown 表格格式脆弱**：如果使用者手動編輯了 `_index.md` 破壞了表格格式（缺少 `|` 或對齊跑掉），後續 `/plan-status` 讀取會解析失敗。寫入時確保表格格式正確。
- **Bug 類型的 Notion 模板與 bug-start 不同步**：plan-start 建立 Bug 時用的模板要和 `bug-start` 的完全一致。如果 bug-start 更新了模板但 plan-start 沒跟上，會導致 `/bug-close` 找不到預期的區塊標題。
- **.gitignore 追加位置**：追加 `.spec/` 到 `.gitignore` 時，如果檔案末尾沒有換行，新增的行會和最後一行黏在一起。追加前確認末尾有換行。
- **Notion 層 relation 用 page ID 不是 URL**：`notion-update-page` 設定「相關任務」relation 時，`id` 欄位要填 page ID（UUID 格式），不是頁面 URL。`.spec/` README.md 的 `notion_page_id` 就是正確的值。
- **本地關聯和 Notion 關聯可能不一致**：`.spec/` 中的 `related_feature` 和 Notion 的「相關任務」是兩個獨立的關聯。使用者在 Notion 手動刪除關聯不會更新 `.spec/`，反之亦然。這是已知的 offline-first 限制。
- **Bug 的 Feature Branch 偵測依賴關聯結果**：Feature Branch 偵測是步驟 7-3 的延伸邏輯，若關聯 Feature 失敗則整個分支偵測都跳過。不要獨立於關聯結果執行分支偵測。

---

## 邊界情況

- **設定目錄不存在**：提示先執行 `/plan-setup` 或 `/bug-setup`
- **不在 Git repo 中**：跳過分支和專案自動偵測
- **`.spec/` 目錄已存在同名 slug**：加數字後綴或詢問使用者
- **Notion API 失敗（Step A）**：仍建立本地 `.spec/` 目錄，`notion_page_id` 留空，提示使用者可稍後用 `/plan-sync` 補建
- **Notion API 失敗（Step B）**：頁面已建立但無 body 內容，記錄到 log.md，提示使用者可用 `/plan-sync` 補寫 body
- **分支名稱衝突**：提示自訂名稱
