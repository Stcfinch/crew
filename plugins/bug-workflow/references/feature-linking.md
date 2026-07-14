# 自動關聯來源 Feature ／ 偵測來源 Feature Branch（bug-start 專用）

> 本檔供 `bug-start` SKILL.md 步驟 8、9 引用，內容為完整流程細節。

## 步驟 8：自動關聯來源 Feature

建立 Bug 條目後，嘗試在同一資料庫中找到相關的 Feature 條目，透過「相關任務」self-relation 建立關聯。

### 前置條件

- Bug Notion 頁面已建立（「建立 Notion 條目」一節成功）
- 「相關任務」欄位存在（由 `/bug-setup` 建立）

### 關鍵字擷取

從 Bug 標題擷取搜尋關鍵字，依優先順序：

1. **SRS 編號**：正則 `SRS[-]?\d+`（如 `SRS-042`、`SRS042`）→ 最精確，直接搜尋
2. **功能模組名**：去除停詞後的實詞（如「SSO」、「推播」、「Rich Menu」、「標籤」）
3. **完整標題**：作為最後手段的 broadest match

**停詞表**（從標題中剔除）：
- 錯誤類：錯誤、異常、失敗、問題、故障、無法、找不到、空白、延遲、超時、不正確、不顯示
- 動作類：修復、修正、處理、調整、更新
- 環境類：正式、UAT、SIT、測試
- 技術類：API、回傳、500、404、null、NPE、Exception

### 查詢同專案 Feature

使用 `API-query-data-source`（Data Source ID = 任務追蹤工具）查詢，filter 條件：

```json
{
  "filter": {
    "and": [
      {
        "property": "任務類型",
        "multi_select": { "contains": "💬 功能要求" }
      },
      {
        "property": "專案資料庫",
        "relation": { "contains": "<同專案 page ID>" }
      }
    ]
  }
}
```

> 「同專案 page ID」來自「建立 Notion 條目」一節建立 Bug 時設定的「專案資料庫」relation 目標頁面 ID。

### 標題比對

對查詢結果逐一比對：

1. 先用 SRS 編號精確匹配 Feature 標題
2. 再用功能模組名做 `title.includes(keyword)` 比對
3. 多個匹配時，取**匹配關鍵字最多**的；若仍平手，取**建立時間最近**的

### 設定 Relation

匹配成功後，使用 `notion-update-page` 設定 Bug 的「相關任務」欄位：

```json
{
  "相關任務": {
    "relation": [
      {"id": "<feature-page-id>"}
    ]
  }
}
```

> 因為 Relation 是 DUAL，Notion 自動在 Feature 端的「被關聯任務」欄位加上反向連結。

### 不阻擋流程

- query-data-source 失敗 → 靜默跳過
- 查詢結果為空（專案無 Feature）→ 跳過
- 關鍵字擷取為空（標題太短或全是停詞）→ 跳過
- patch-page 失敗（如「相關任務」欄位不存在）→ 跳過，提示使用者可手動關聯或執行 `/bug-setup` 更新 schema
- 匹配不成功 → 在回傳結果中提示：「未自動關聯 Feature，可至 Notion 手動設定『相關任務』欄位」

## 步驟 9：偵測來源 Feature Branch

若「自動關聯來源 Feature」一節成功關聯到 Feature，進一步從 Feature 條目取得原始開發分支，作為 Bug 的修復分支。

### 前置條件

- 「自動關聯來源 Feature」一節成功關聯到至少一個 Feature

### 流程

1. 使用 `notion-fetch` 讀取被關聯 Feature 的 Notion 頁面
2. 取得 Feature 的「修復分支」欄位值（如 `feature/sample-fix`）
3. 若「修復分支」欄位為空 → 跳過此步驟
4. 驗證該分支是否存在：
   ```bash
   git branch -a | grep -F "<branch-name>"
   ```

5. **分支存在**：
   ```
   偵測到來源 Feature 的開發分支：feature/sample-fix
   依 Git-flow 規定，Bug 修復應在此分支上進行。

   已將「修復分支」設定為此分支。

   要切換到此分支嗎？
     1. 是，git checkout feature/sample-fix
     2. 否，稍後手動切換
   ```
   - 更新 Bug Notion 條目的「修復分支」欄位為 feature branch 名稱
   - 選 1 → 執行 `git checkout <branch>`
   - 選 2 → 僅更新 Notion 欄位，不切換

6. **分支不存在**：
   ```
   ⚠️ 來源 Feature 的分支 feature/sample-fix 不存在（可能已被刪除或 merge 後清理）

   請選擇：
     1. 從目前分支建立新的 fix branch
     2. 直接在當前分支修復
     3. 手動指定分支
   ```
   - 選 1 → 建立 `hotfix/{slug}` 分支
   - 選 2 → 修復分支設為當前分支
   - 選 3 → 使用者輸入分支名稱

### 不阻擋流程

- 「自動關聯來源 Feature」未關聯到 Feature → 跳過整個「偵測來源 Feature Branch」節
- notion-fetch 失敗 → 跳過
- Feature 的「修復分支」為空 → 跳過
- git 操作失敗 → 跳過，修復分支保持「建立 Notion 條目」一節設定的值
