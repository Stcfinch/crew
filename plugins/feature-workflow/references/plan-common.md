# plan-* 共用邏輯

所有 `plan-spec`、`plan-db`、`plan-arch` 共用以下邏輯。

---

## 定位活躍任務

按優先順序匹配：

1. 從 Git branch 匹配：讀取 `.spec/_index.md`，找「分支」欄位與當前 `git branch --show-current` 匹配的任務
2. 若匹配到的任務 status 為 `暫停` → 提示「此任務已暫停，是否恢復？[Y/n]」，確認後執行 unpark 流程（見 `/plan-status --unpark`）再繼續
3. 若只有一個進行中任務 → 自動選定
4. 若多個進行中 → 列出供選擇
5. 若無進行中 → 提示先執行 `/plan-start`

選定後讀取 `.spec/{slug}/README.md`，取得 `type`、`name`、`status`、`tech_stack` 等元資訊。

---

## 讀取專案上下文

### 專案 CLAUDE.md

讀取 `pwd` 下最近的 CLAUDE.md（向上搜尋），取得技術棧、架構模式、分層規則、命名慣例。

### 技術棧資訊

從 `.spec/{slug}/README.md` 的 `tech_stack` 欄位取得技術棧 ID，依 `references/config-resolver.md` 的第 3 層載入邏輯讀取對應定義：
- 內建技術棧 → `stacks/_builtin.md`
- 自訂技術棧 → `stacks/{id}.md`

### 現有程式碼參考

使用 Glob/Grep 掃描與需求相關的現有程式碼（1-2 個 Controller、Service、Entity），了解 API 風格、命名慣例。

### 規範檔案

讀取可用的規範檔案：
- `~/.claude/rules/database.md`（DB 設計時）
- `~/.claude/rules/design-patterns.md`（架構設計時）
- `~/.claude/rules/java-performance.md`（效能相關）

---

---

## 一致性驗證（自動）

每個 Skill 完成後，**自動**執行交叉比對，使用者無需手動觸發。

### 檢查項目

| 檢查項目 | 比對來源 | 具體檢查 |
|---------|---------|---------|
| API-DB 一致性 | spec.md ↔ db.md | spec 中每個 API 的請求/回應欄位，db.md 是否有對應表欄位 |
| DB-Arch 一致性 | db.md ↔ arch.md | db.md 的每個表，arch.md 是否有對應 POJO 和 Mapper |
| API-Arch 一致性 | spec.md ↔ arch.md | spec 的每個 API 端點，arch.md 是否有對應 Controller 方法 |
| 判斷區塊完整性 | spec.md | FRONTEND_REQUIRED / DB_REQUIRED 是否為 true/false |
| DB_TABLES 對應 | spec.md ↔ db.md | 判斷區塊的 DB_TABLES 是否與 db.md 表清單一致 |

> **觸發條件**：僅在比對的兩端檔案都存在時才執行該項檢查。例如執行 `/plan-spec` 時，因 db.md 和 arch.md 不存在，僅檢查「判斷區塊完整性」。

### 分類

- 🔴 **不一致**：文件間矛盾（如 spec 定義的 API 欄位在 db.md 找不到對應表欄位）
- 🟡 **遺漏**：缺少預期內容（如 db.md 有表但缺少索引建議）
- 🟢 **良好**：交叉比對通過

### 自動修復流程

發現問題時：
1. 顯示「發現 N 個不一致，修復中...（第 1/2 輪）」
2. 備份受影響的文件（`{file}.bak`）
3. 直接修改受影響的文件，補齊遺漏或修正矛盾
4. 重新執行檢查（最多 **2 輪**）
5. 2 輪後仍有問題 → 列出剩餘摘要，**不阻擋流程**

---

## 更新日誌

每次規劃完成，在 `.spec/{slug}/log.md` 追加一筆紀錄：

```markdown
### [{日期}] {Skill 名稱}完成
- 產出檔案：{檔案路徑}
- 摘要：{一句話描述}
```

若 `log.md` 不存在則建立。

---

## 共用 Gotchas

- **spec.md「判斷」區塊格式是 plan-build 的入口**：`FRONTEND_REQUIRED` 和 `DB_REQUIRED` 的值直接決定 plan-build 的團隊組成。格式錯誤（如用中文「是/否」而非 `true/false`）會 fallback 到預設值。
- **Agent subagent 的 model 參數**：prompt 中寫「使用 Opus 模型」只是自然語言指示，不保證生效。必須在 Agent tool 的 `model` 參數實際設定 `"opus"`。
- **重新執行覆蓋已有檔案**：覆蓋前會備份到 `{file}.bak`，但 `.bak` 只保留一份。

## 共用邊界情況

- **`.spec/` 目錄不存在**：提示先執行 `/plan-start`
- **找不到活躍任務**：提示先執行 `/plan-start` 或檢查 `_index.md`
- **前置檔案不存在**：提示建議先執行前置步驟，但不強制阻擋
- **重新執行同一 Skill**：覆蓋已有檔案（先備份舊版到 `{file}.bak`）

---

## Notion database_id 解析

### 使用場景

所有需要呼叫 `post-page` 建立 Notion 頁面的 Skill 都需要此解析：
- plan-start（建立任務頁面）
- plan-sync（補建 Notion 條目）
- plan-close（同步到知識庫：功能設計庫 / Bug 知識庫）

### 解析步驟

1. 從 config.md 讀取目標資料庫的 Data Source ID
2. 呼叫 `retrieve-a-data-source`，傳入 `data_source_id`
3. 從回傳結果的 `parent` 欄位中取得 `database_id`
4. 使用 `database_id` 作為 `post-page` 的 `parent.database_id`

### 快取策略

- 同一 Skill 執行期間，同一個 Data Source ID 只解析一次
- 解析結果不持久化到檔案（避免 database_id 變更時過期）

### 錯誤處理

- `retrieve-a-data-source` 失敗 → 嘗試直接用 Data Source ID 作為 database_id（向下相容）
- 回傳結果中無 `parent.database_id` 欄位 → 同上

---

## deploy-checklist.md 格式規範

### 檔案路徑

`.spec/{slug}/deploy-checklist.md`

### 檔案結構

```markdown
---
slug: {slug}
created: {YYYY-MM-DD}
last_synced: {最後一次同步到 Notion 的時間，初始為空}
notion_block_id: {🚀 區塊的 block ID，首次同步後回填}
---

# 上線前置作業

## SQL 遷移

- [ ] `CREATE TABLE {table_name}` — {說明}
- [ ] `CREATE INDEX {index_name} ON {table_name}` — {說明}

## 設定檔變更

- [ ] `{檔案路徑}` — {變更說明}

## 其他前置作業

（使用者手動新增）
```

### 生命週期

| 階段 | 動作 | 觸發者 |
|------|------|--------|
| plan-db 完成 | 建立檔案，填入 SQL 遷移項目 | plan-db 自動 |
| plan-build 完成 | 追加設定檔變更項目（若有偵測到） | plan-build 自動 |
| 開發中 | 使用者手動勾選已完成的項目 | 使用者 |
| plan-sync | 同步到 Notion 🚀 區塊 | 使用者手動觸發 |
| plan-close | 讀取並檢查所有 checkbox 狀態 + 同步 Notion | plan-close 自動 |

### SQL 擷取規則

從 `.spec/{slug}/db.sql` 中擷取以下 DDL/DML：

| SQL 類型 | 擷取內容 |
|---------|---------|
| CREATE TABLE | 表名 |
| ALTER TABLE | 表名 + 操作類型 |
| CREATE INDEX | 索引名 + 表名 |
| INSERT INTO | 表名（初始資料） |
| DROP TABLE | 表名（高風險標記 ⚠️） |

### 設定檔偵測模式

| 模式 | 說明 |
|------|------|
| `**/mapper/**/*.xml` | MyBatis Mapper XML |
| `**/web.xml` | Web 應用設定 |
| `**/application.properties` | Spring Boot 設定 |
| `**/application*.yml` | Spring Boot YAML 設定 |
| `**/pom.xml` | Maven 依賴 |
| `**/build.gradle` | Gradle 依賴 |
| `**/Dockerfile` | Docker 映像 |
| `**/docker-compose*.yml` | Docker Compose |
| `**/*nginx*.conf` | Nginx 設定 |
| `**/logback*.xml` | Log 設定 |

---

### 第 4 層：產品知識庫（需要產品操作知識時）

從 `projects/{id}.md` 的 `product_id` 欄位取得產品 ID：

- 有 product_id → 讀取 plugin 目錄的 `products/{product_id}.md`
- 無 product_id → 通用模式（不載入產品知識庫）

取得：頁面導航地圖、常用 Selector、i18n 對照表、特殊操作 Recipe、API 格式。

### 第 4.1 層：產品級記憶（需要驗證記憶時）

有 product_id 時，額外讀取 `products/{product_id}-memory.md`。

### projects/{id}.md 新增選填欄位

| 欄位 | 必要性 | 說明 |
|------|--------|------|
| product_id | 選填 | 指向 products/{id}.md 的產品知識庫 |
| e2e_repo | 選填 | E2E 測試 repo 的本機路徑（Phase 3 --e2e 模式用） |
| e2e_profile | 選填 | E2E 測試的預設 Profile ID |
