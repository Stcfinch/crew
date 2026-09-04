# Notion 整合

Notion 是選用服務；本機流程不需要帳號、API key 或網路。這個 plugin 不附帶 MCP server。
使用當前 Codex 已提供的 Notion 工具，先讀工具 schema；不從原平台的工具名稱推測可用能力。
缺少工具或連線時提供本機草稿，清楚說明尚未同步。

## 設定

.crew/config.json 的 mode 可為 local 或 notion；notion 物件包含已查證的
tasks、projects、bug_knowledge、feature_knowledge（可設 null）。
各項使用 { "id": "...", "kind": "database|data_source|page" }，保留 API 實際 ID 類型。
欄位映射記錄於 .crew/notion.md，與實際 schema 對照；勿將 access token 放在這些檔案。
授權由使用者的 Codex 連線/MCP 設定管理。

## Setup

1. 搜尋使用者指定 workspace 的既有資料庫並讀 schema；有多個同名候選時請使用者選擇。
2. 任務需要 title、status、type、priority、project relation；可選 environment、branch、root cause、related tasks。
3. project 包含名稱與 Git repo 識別；Bug 知識庫與功能設計庫包含名稱、tags、task URL、project relation。
4. 使用實際既有欄位名稱與選項。資料庫/資料來源/page ID 不互換。
5. 若使用者要求新建 workspace 結構，先建立四個資料庫基本欄位，再補關聯，避免循環依賴。
6. 工具不支援 View/schema 寫入時，清楚列出需手動完成的項目，保留可用的本機功能。

## 同步

- task state.notion.page_id 已存在時先讀該頁，核對它確實屬於當前 task。
- 首次寫入前以 project、slug 和任務來源搜尋去重；不能只用標題決定覆蓋誰。
- 只同步任務所需的非敏感摘要、驗收結論、决策與連結；不要上傳環境檔、密碼或原始機密 logs。
- 讀遠端目前內容，再針對 CREW 管理的章節更新，保留使用者段落。
- 標題、狀態、Relation 與日期用 API schema 的正確型別。
- 寫入後回讀核對；中途失敗保持尚未同步，重新執行前先查剛才是否已寫入，避免重複建立。
- 成功後才用 state set --notion-page-id / --mirrored-status / --synced-now 寫入本機。
- 選用知識庫同步，以精簡根因/方案摘要連回 task；成功寫 task 不等於知識庫也成功。

