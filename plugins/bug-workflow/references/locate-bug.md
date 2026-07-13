# 定位目標 Bug（共用邏輯）

`/bug-update`（一般更新模式）、`/bug-fix`、`/bug-investigate` 皆使用本邏輯定位當前要操作的 Bug 頁面。

---

## 查詢邏輯

從設定檔讀取「任務追蹤工具」Data Source ID，精確查詢該資料庫：

使用 `notion-search` 搭配 `data_source_url: collection://{任務追蹤工具 Data Source ID}` 搜尋：
- 狀態為「進行中」
- 任務類型包含「🐞 錯誤」

同時取得 Git Repo 識別碼（從 `git remote get-url origin` 解析），用於輔助篩選同一專案下的 Bug。

## 優先匹配邏輯

1. 若只有 1 筆進行中的 bug → 自動選定
2. 若「修復分支」欄位與當前 Git branch 完全匹配 → 自動選定
3. 若有多筆候選，優先顯示與當前 Git Repo 所屬專案相關的條目
4. 若有多筆候選 → 列出清單讓使用者選擇
5. 若無候選 → 提示使用者先用 `/bug-start` 建立

選定後，使用 `notion-fetch` 取得頁面完整內容，以便後續操作（更新內容、修復、調查）。
