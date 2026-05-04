# 團隊組成判斷規則

## 判斷流程

### Step 1：讀取判斷區塊

從 spec.md 的「判斷」區塊取得 TASK_TYPE 和 CHANGE_SCOPE。
若判斷區塊不存在或缺少新欄位 → 回退到 v4.9.0 的邏輯（只看 FRONTEND_REQUIRED × DB_MCP）。

### Step 2：按 TASK_TYPE 分流

#### feature（新功能）
走完整判斷流程（Step 3）。

#### adjustment（功能調整）
按 CHANGE_SCOPE 決定：

| CHANGE_SCOPE | 團隊配置 | 模式 |
|-------------|---------|------|
| backend-only | 後端工程師 | Subagent |
| frontend-only | 前端工程師 | Subagent |
| api-only | 後端 + API 工程師 | 2 人 Team 或 2 個 Subagent |
| db-only | DB 工程師（需 DB MCP）| Subagent |
| full | 走 Step 3 完整判斷 | Agent Teams |

#### bugfix（修復）
預設：後端工程師（Subagent）
例外：若 CHANGE_SCOPE = full → 走 Step 3

#### refactor（重構）
預設：後端工程師（Subagent）
例外：若跨多層級 → 後端 + 測試（2 人 Team）

#### performance（效能優化）
預設：
- 若 DB_MCP_AVAILABLE → DB 工程師 + 後端（2 人 Team）
- 若無 DB MCP → 後端工程師（Subagent）

### Step 3：完整判斷（feature 或 CHANGE_SCOPE = full）

沿用 v4.9.0 邏輯，增加 NEW_API 判斷：

| FRONTEND | DB_MCP | NEW_API | 團隊組成 |
|----------|--------|---------|---------|
| true | true | true | 5 人（DB + 後端 + API + 前端 + 測試）|
| true | true | false | 4 人（DB + 後端 + 前端 + 測試）|
| true | false | true | 4 人（後端 + API + 前端 + 測試）|
| true | false | false | 3 人（後端 + 前端 + 測試）|
| false | true | true | 4 人（DB + 後端 + API + 測試）|
| false | true | false | 3 人（DB + 後端 + 測試）|
| false | false | true | 3 人（後端 + API + 測試）|
| false | false | false | 後端 + 測試（2 人 Team 或 Subagent）|

### Step 3.5：DB_REQUIRED 處理

spec.md 判斷區塊可能包含 `DB_REQUIRED` 欄位，影響團隊組成和退出驗證：

| DB_REQUIRED 值 | 團隊組成影響 | 退出驗證影響 |
|---------------|-------------|-------------|
| `true` | 加入 DB 工程師（若 DB MCP 可用） | 驗證 migration SQL 存在 |
| `insert-only` | **不加入** DB 工程師 | 退出驗證時強制產出 `deploy.sql`（E7） |
| `false`（預設） | 不加入 DB 工程師 | 無額外驗證 |

> **insert-only 的典型場景**：新增後台功能頁面需 INSERT auth_program / auth_menu（權限關聯），不需要 CREATE TABLE / ALTER TABLE，但部署時必須執行 INSERT SQL。這類 SQL 不需要 DB 工程師，但若沒有獨立 deploy.sql 檔案，上線時極易遺漏。

### Step 4：確認計畫

顯示判斷依據，讓使用者確認或覆寫：

```
📊 Teammate 配置：後端工程師（Subagent 模式）

判斷依據：
  - TASK_TYPE = bugfix → 預設 Subagent
  - CHANGE_SCOPE = backend-only
  - FRONTEND_REQUIRED = false
  - NEW_API = false

需要調整嗎？（如需完整 Agent Teams，輸入配置）[Y/n]
```

## Bug-workflow 相容

bugfix 任務可能從 bug-workflow（/bug-start）進入，此時有 fix.md 而非 spec.md。

判斷區塊讀取優先順序：
1. `.spec/{slug}/spec.md` 的「判斷」區塊
2. `.spec/{slug}/fix.md` — 從修復方案推斷（TASK_TYPE 固定為 bugfix，CHANGE_SCOPE 從修復範圍推斷）
3. 都沒有 → 詢問使用者
