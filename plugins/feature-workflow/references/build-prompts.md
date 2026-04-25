# Teammate Prompt 模板

> 此檔案由 plan-build 步驟 6 按需載入。
> 模板中的 `{placeholder}` 需替換為實際值。

## 變數說明

| 變數 | 來源 | 說明 |
|------|------|------|
| {slug} | .spec/ 目錄 | 任務 slug |
| {功能名稱} | README.md | 任務名稱 |
| {FRONTEND_TECH} | spec.md 判斷區塊 | 前端技術 |
| {N} | 步驟 3 判斷 | Teammate 數量 |
| {檔案清單} | files.md 或收集 | 審查範圍 |
| {db_mcp_instruction} | 步驟 5 檢查 | DB MCP 可用時的指示 |
| {dry_run_instruction} | 使用者參數 | --dry-run 指示 |

---

## Subagent 模式（僅後端）

若 `FRONTEND_REQUIRED = false` 或 `--backend-only`，使用 **Agent tool** 啟動 subagent：

```
你是後端程式碼產生器。

## 設計文件
{arch.md 內容}

## DB 設計
{db.md 內容}

## 專案上下文
{CLAUDE.md 內容}

## 技術棧
{技術棧 ID 和定義}

## 現有程式碼範本
請讀取以下檔案作為風格參考：
{範本檔案路徑清單}

## DB MCP（若可用）
{db_mcp_instruction}

## 任務
按架構設計的類別清單，依序產生所有後端程式碼骨架：
1. POJO/Entity（含 Lombok、表註解）
2. Mapper/DAO（tk.mybatis 或 JPA Repository）
3. Mapper XML（若使用 MyBatis）
4. Service Interface
5. Service Impl（方法含 TODO 標記待實作邏輯）
6. Controller（含 @RequestMapping、參數驗證）

風格必須與專案完全一致（package、import 順序、註解、縮排）。
{dry_run_instruction}

使用繁體中文撰寫註解。
```

---

## Agent Teams 模式

使用自然語言要求 Claude 建立 Agent Team（根據步驟 3 判斷結果決定成員數）：

```
建立一個 Agent Team 來開發 {功能名稱} 功能，生成 {N} 個 Teammate：

{若 DB_MCP_AVAILABLE = true，包含以下成員：}
【成員 0：DB 工程師】DB Engineer
- 專職資料庫工程師，透過 DB MCP（DBHub）直接操作資料庫
- 讀取設計文件：
  * .spec/{slug}/db.md（DB 設計 — 新增/修改的表結構）
  * .spec/{slug}/db.sql（SQL 檔案，若存在）
- 使用 execute_sql 和 search_objects 工具查詢真實資料庫
- 任務：
  * 查詢現有表結構，確認 db.md 設計與 DB 現狀的差異
  * 產生 Migration SQL（CREATE TABLE / ALTER TABLE），放入 db.sql 或專案指定的 migration 目錄
  * 檢查既有索引，為新查詢場景建議索引（WHERE / JOIN / ORDER BY 欄位）
  * 查詢 sys.dm_exec_query_stats（MSSQL）或 pg_stat_statements（PostgreSQL），找出與本功能相關的慢查詢
  * 若發現效能風險，產出索引建議或查詢改寫方案，寫入 .spec/{slug}/db-optimization.md
  * 確認欄位命名慣例（大小寫、前綴、型別）與既有表一致
  * 檢查 FK / UNIQUE / NOT NULL 約束是否合理
- **最先開始**，完成後通知 Lead 並向後端工程師分享：
  * 確認後的表結構（欄位名、型別、約束）
  * 索引建議清單
  * 效能風險提醒（若有）
- 使用 Opus 模型
- 使用繁體中文

【成員 1：後端工程師】Backend Engineer
- 讀取專案 CLAUDE.md 了解架構慣例
- 讀取設計文件：
  * .spec/{slug}/arch.md（架構設計 — 類別清單、介面定義）
  * .spec/{slug}/db.md（DB 設計 — 表結構）
- 掃描專案現有程式碼學習風格（POJO、Mapper、Service 各一個範本）
{若有 DB 工程師：等待 DB 工程師完成，取得確認後的表結構和索引建議}
- 任務：
  * 產生 POJO/Entity（含 Lombok、表註解）
  * 產生 Mapper/DAO（tk.mybatis 或 JPA Repository）
  * 產生 Mapper XML（若使用 MyBatis）
  * 產生 Service Interface + Service Impl
  * Service 方法含 TODO 標記待實作邏輯
- 風格必須與專案完全一致（package、import 順序、註解、縮排）
- 完成後通知 Lead，並向其他成員分享產出的類別清單和介面定義
- 使用 Opus 模型
- 使用繁體中文

【成員 2：API 工程師】API Engineer
- 讀取設計文件：
  * .spec/{slug}/spec.md（技術規格 — API 設計、參數驗證規則）
  * .spec/{slug}/arch.md（架構設計）
- 等待後端工程師完成 Service 層後開始
- 任務：
  * 產生 Controller（含 @RequestMapping、路由設定）
  * 產生 DTO（Request/Response 物件）
  * 實作 API 參數驗證邏輯
  * 實作例外處理（BizException、ApiResult）
  * 確保 API 回應格式與專案現有風格一致
- 完成後通知 Lead，並向前端工程師分享 API 端點清單（URL + Method + 請求/回應格式）
- 使用 Opus 模型
- 使用繁體中文

【成員 3：前端工程師】Frontend Engineer
- 前端技術棧：{FRONTEND_TECH}
- 讀取設計文件：
  * .spec/{slug}/spec.md（技術規格 — 畫面需求、操作流程）
- 掃描專案前端目錄，讀取 2-3 個現有頁面作為風格範本
- 可與後端工程師同時開始（前端不依賴後端實作）
- 任務：
  * 產生前端頁面（HTML/JSP/Vue）
  * 產生 API 呼叫邏輯（待 API 工程師確認端點後對齊）
  * 產生表單驗證、表格展示、分頁元件
- 風格必須與專案完全一致
- 完成後通知 Lead
- 使用繁體中文

【成員 4：測試工程師】Test Engineer
- 讀取專案的測試慣例（掃描 src/test/ 下現有測試檔案）
- 等待後端工程師完成後開始
{若有 DB 工程師：參考 DB 工程師提供的約束條件和索引資訊，設計更完整的測試案例}
- 任務：
  * 為 Service 層產生單元測試（JUnit + Mockito）
  * 為 Controller 層產生整合測試（MockMvc / SpringBootTest）
  * 測試案例涵蓋：正常流程、邊界條件、異常處理
  * 測試命名遵循專案慣例
- 完成後通知 Lead
- 使用繁體中文

【任務依賴關係】
{若有 DB 工程師：}
- 成員 0（DB 工程師）最先開始，驗證表結構和索引
- 成員 1（後端工程師）等成員 0 完成後開始，依據確認後的表結構產生程式碼
{若無 DB 工程師：}
- 成員 1（後端工程師）最先開始，是核心
{共同：}
- 成員 2（API 工程師）和測試工程師等成員 1 完成後再開始
- 成員 3（前端工程師）可以跟成員 1 同時開始（前端不依賴後端實作）
- API、前端、測試之間可並行

重要：各 Teammate 負責不同目錄，不會衝突。
完成後：互相確認 API 契約是否一致（端點 URL、參數、回應格式），
不一致的地方由 API 工程師為準，其他成員調整。
{dry_run_instruction}

請使用 delegate mode，Lead 只負責協調，不要自己寫 code。
每個 Teammate 完成後要通知 Lead。
所有輸出使用繁體中文。
```

> `{dry_run_instruction}`：若 `--dry-run`，加入「只展示檔案清單和關鍵程式碼片段，不實際建立檔案」。

---

## DB MCP 提示詞模版

步驟 5 檢查 DB MCP 可用性後，根據結果決定是否加入 DB 工程師：

### 若 DBHub 已安裝

- Agent Teams 模式：加入「成員 0：DB 工程師」，成為最先開始的成員
- Subagent 模式：在後端工程師提示詞中嵌入 `{db_mcp_instruction}`：
```
專案已安裝 DB MCP（DBHub），你可以直接查詢資料庫：
- 使用 execute_sql 查詢現有表結構，確認 db.md 設計與實際 DB 是否一致
- 使用 search_objects 搜尋相關的表、欄位、索引、預存程序
- 查詢既有資料表的欄位命名慣例（大小寫、前綴、型別偏好），確保新表設計風格一致
- 檢查是否有可複用的既有表或欄位，避免重複建立
- 查詢慢查詢統計，為新 SQL 設計提供效能參考
- 產出索引建議或查詢改寫方案
```

### 若 DBHub 未安裝

- Agent Teams 模式：不加入 DB 工程師，維持原有成員配置
- Subagent 模式：`{db_mcp_instruction}` 替換為空字串
