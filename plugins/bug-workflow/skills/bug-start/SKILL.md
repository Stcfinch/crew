---
name: bug-start
description: 在 Notion 任務追蹤工具建立 Bug 條目並填入標準化模板（僅建條目，不含 .spec/ 目錄與 Git branch）。當使用者輸入 /bug-start，或提到「建立 bug 條目」、「記錄 bug 到 Notion」、「bug 通報」時觸發此 Skill。
---

# Bug Start — 建立 Bug 條目與標準化文件

在 Notion「任務追蹤工具」資料庫建立一筆 Bug 條目，自動填入標準化頁面模板，並關聯對應專案。

---

## 流程

> **前置檢查**：參照 plugin 根目錄 `references/prerequisites.md`（相對 SKILL.md 為 `../../references/`）執行完整前置檢查（CLAUDE.md + 設定檔 + 專案註冊）。

### 1. 解析使用者輸入

使用者會以以下格式觸發：

```
/bug-start <問題簡述>
```

從使用者輸入中擷取：
- **問題簡述**（必填）：作為「任務名稱」

### 2. 偵測環境資訊（自動專案對應）

取得 branch 名稱、當前工作目錄與 Git Repo 識別碼：

```bash
# 分支名稱
git branch --show-current 2>/dev/null || echo ""

# 當前工作目錄
pwd

# Git 遠端 URL（用於自動對應 Notion 專案）
git remote get-url origin 2>/dev/null || echo ""
```

**Git Repo 識別碼解析規則**：

從 `git remote get-url origin` 取得遠端 URL 後，解析為識別碼：
- Git host 含 `intumit`（公司 GitLab）→ 只取 `{group}/{repo}`，例如 `FUB03P2402/PushAPIService`
- 其他（GitHub 等）→ 加上 host：`{host}/{group}/{repo}`，例如 `github.com/mark22013333/crew`
- 解析時去掉 `.git` 後綴，支援 HTTPS / SSH 格式

**自動專案對應邏輯**：

1. 執行 `git remote get-url origin` 取得 Git 遠端 URL
2. 解析為 Git Repo 識別碼（host 含 `intumit` → `{group}/{repo}`，其他 → `{host}/{group}/{repo}`，去除 `.git` 後綴）
3. 讀取設定檔中「專案對應」表，精確匹配「Git Repo」欄位
4. 若匹配成功 → 自動選定該專案，不再詢問
5. 若不在 Git repo 或匹配失敗 → 進入互動式選擇

若設定檔中無對應，也可用 `notion-search` 搜尋 Notion「專案資料庫」（Data Source ID 見設定檔），找「Git Repo」欄位與識別碼匹配的專案。

### 3. 互動式補充資訊

若使用者未在初始輸入中提供以下資訊，依序詢問：

1. **所屬專案**（若自動偵測失敗）：搜尋 Notion「專案資料庫」，列出「進行中」的專案供選擇
2. **環境**（預設「正式」）：`測試` / `UAT` / `正式`
3. **優先順序**（預設「中」）：`高` / `中` / `低`

使用者可在初始輸入中直接指定，例如：
```
/bug-start SSO登入找不到使用者 正式 高
```

### 4. 偵測負責人

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

### 5. 建立 Notion 條目

使用 `notion-create-pages` 在「任務追蹤工具」資料庫建立新條目：

**Data Source ID**：從設定檔的「任務追蹤工具」取得

**Properties**：

| 欄位 | 值 |
|------|-----|
| 任務名稱 | 使用者提供的問題簡述 |
| 任務類型 | `["🐞 錯誤"]` |
| 狀態 | `進行中` |
| 優先順序 | 使用者選擇（預設「中」） |
| 環境 | 使用者選擇（預設「正式」） |
| 修復分支 | Git branch 名稱（若有） |
| 專案資料庫 | 關聯的專案頁面 URL |
| 負責人 | 「偵測負責人」一節偵測到的 Notion 使用者（若有） |

### 6. 填入頁面模板

頁面的 content 使用以下標準模板：

```
## 🔴 問題描述
- **通報來源**：
- **發生時間**：{當前日期時間}
- **重現步驟**：
  1. ...
  2. ...
- **預期行為**：
- **實際行為**：
- **錯誤截圖**：

---

## 🔍 調查過程
### 關鍵 Log

### 相關 SQL 查詢

### 初步判斷

---

## 🧠 根因分析
- **問題根因**：
- **問題檔案**：
- **問題程式碼**：

---

## ✅ 修復方案
- **修改檔案清單**：
- **修改說明**：
- **修改後程式碼**：
- **修復 Commit**：
- **修復分支**：

---

## 🧪 驗證
- [ ] 本地測試通過
- [ ] UAT 驗證通過
- [ ] 正式環境確認
- [ ] 通報者確認問題已解決

---

## 📝 經驗教訓
- **學到什麼**：
- **如何預防**：
```

若使用者在初始輸入中已提供問題描述內容，將其預填入「問題描述」區塊的「實際行為」欄位。

### 7. 初始證據收集（自動，不需使用者介入）

建立 Notion 頁面後，自動收集環境資訊寫入「調查過程」區塊。

#### 收集項目

1. **最近 commit**（bug-start 專屬）：
   ```bash
   git log --oneline -5
   ```
   寫入「調查過程 > 最近變更」

2–4. **環境狀態／知識庫快速搜尋／學習快速搜尋**：與 `/bug-investigate` 共用收集指令，參照 plugin 根目錄 `references/evidence-collection.md`（相對 SKILL.md 為 `../../references/`）「共用收集項目」段。

#### 寫入格式

使用 `notion-update-page` 的 `update_content`，在「調查過程」區塊寫入，標題為「### [HH:mm] 初始環境快照」，先列本 skill 專屬的「最近 5 筆 commit」，再接 `references/evidence-collection.md`「共用 Notion 寫入格式」段的三段共用區塊：

```markdown
### [HH:mm] 初始環境快照

**最近 5 筆 commit**：
- abc1234 fix: 修正推播排程的 cron 表達式
- def5678 feat: 新增推播統計 API
- ...

（接續共用區塊：環境狀態／歷史參考／歷史學習，見 references/evidence-collection.md）
```

#### 不阻擋流程

參照 `references/evidence-collection.md`「不阻擋流程」段。

### 8. 自動關聯來源 Feature

建立 Bug 條目後，嘗試在同一資料庫中找到相關的 Feature 條目，透過「相關任務」self-relation 建立關聯。

#### 前置條件

- Bug Notion 頁面已建立（「建立 Notion 條目」一節成功）
- 「相關任務」欄位存在（由 `/bug-setup` 建立）

#### 關鍵字擷取

從 Bug 標題擷取搜尋關鍵字，依優先順序：

1. **SRS 編號**：正則 `SRS[-]?\d+`（如 `SRS-042`、`SRS042`）→ 最精確，直接搜尋
2. **功能模組名**：去除停詞後的實詞（如「SSO」、「推播」、「Rich Menu」、「標籤」）
3. **完整標題**：作為最後手段的 broadest match

**停詞表**（從標題中剔除）：
- 錯誤類：錯誤、異常、失敗、問題、故障、無法、找不到、空白、延遲、超時、不正確、不顯示
- 動作類：修復、修正、處理、調整、更新
- 環境類：正式、UAT、SIT、測試
- 技術類：API、回傳、500、404、null、NPE、Exception

#### 查詢同專案 Feature

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

#### 標題比對

對查詢結果逐一比對：

1. 先用 SRS 編號精確匹配 Feature 標題
2. 再用功能模組名做 `title.includes(keyword)` 比對
3. 多個匹配時，取**匹配關鍵字最多**的；若仍平手，取**建立時間最近**的

#### 設定 Relation

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

#### 不阻擋流程

- query-data-source 失敗 → 靜默跳過
- 查詢結果為空（專案無 Feature）→ 跳過
- 關鍵字擷取為空（標題太短或全是停詞）→ 跳過
- patch-page 失敗（如「相關任務」欄位不存在）→ 跳過，提示使用者可手動關聯或執行 `/bug-setup` 更新 schema
- 匹配不成功 → 在回傳結果中提示：「未自動關聯 Feature，可至 Notion 手動設定『相關任務』欄位」

### 9. 偵測來源 Feature Branch

若「自動關聯來源 Feature」一節成功關聯到 Feature，進一步從 Feature 條目取得原始開發分支，作為 Bug 的修復分支。

#### 前置條件

- 「自動關聯來源 Feature」一節成功關聯到至少一個 Feature

#### 流程

1. 使用 `notion-fetch` 讀取被關聯 Feature 的 Notion 頁面
2. 取得 Feature 的「修復分支」欄位值（如 `feature/qa-log-user-id-statistics`）
3. 若「修復分支」欄位為空 → 跳過此步驟
4. 驗證該分支是否存在：
   ```bash
   git branch -a | grep -F "<branch-name>"
   ```

5. **分支存在**：
   ```
   偵測到來源 Feature 的開發分支：feature/qa-log-user-id-statistics
   依 Git-flow 規定，Bug 修復應在此分支上進行。

   已將「修復分支」設定為此分支。

   要切換到此分支嗎？
     1. 是，git checkout feature/qa-log-user-id-statistics
     2. 否，稍後手動切換
   ```
   - 更新 Bug Notion 條目的「修復分支」欄位為 feature branch 名稱
   - 選 1 → 執行 `git checkout <branch>`
   - 選 2 → 僅更新 Notion 欄位，不切換

6. **分支不存在**：
   ```
   ⚠️ 來源 Feature 的分支 feature/qa-log-... 不存在（可能已被刪除或 merge 後清理）

   請選擇：
     1. 從目前分支建立新的 fix branch
     2. 直接在當前分支修復
     3. 手動指定分支
   ```
   - 選 1 → 建立 `hotfix/{slug}` 分支
   - 選 2 → 修復分支設為當前分支
   - 選 3 → 使用者輸入分支名稱

#### 不阻擋流程

- 「自動關聯來源 Feature」未關聯到 Feature → 跳過整個「偵測來源 Feature Branch」節
- notion-fetch 失敗 → 跳過
- Feature 的「修復分支」為空 → 跳過
- git 操作失敗 → 跳過，修復分支保持「建立 Notion 條目」一節設定的值

### 10. 回傳結果

向使用者回傳：
- Notion 頁面連結
- 建立的條目摘要（任務名稱、專案、環境、優先順序）
- 關聯結果（若「自動關聯來源 Feature」成功）：「已關聯來源 Feature：{Feature 標題}」
- 修復分支（若「偵測來源 Feature Branch」調整過）：「修復分支：{branch}（來自關聯 Feature）」
- 提示後續可用指令：
  ```
  Bug 條目已建立！後續可使用：
  • /bug-investigate     — 開始調查根因（推薦下一步）
  • /bug-update <內容>  — 補充調查資訊（Log、SQL、判斷等）
  • /bug-fix             — 確認根因後修復
  • /bug-close          — 修復完成後結案
  ```

---

## 何時不用

start 組 —— 本 skill 只建 Notion bug 條目；需完整入口（Notion + .spec/ + branch）用 `/plan-start`。

- 需同時建 .spec/ 目錄 + Git branch → 使用 `/plan-start`（type=bug）
- 條目已建、要開始修 → 使用 `/bug-fix`
- 補充既有 bug 資訊 → 使用 `/bug-update`
- 建立 feature 新任務 → 使用 `/plan-start`

---

## Gotchas

- **專案資料庫 Relation 值是頁面 URL，不是名稱**：`notion-create-pages` 的 Relation 欄位需要填入「被關聯頁面的 URL」（如 `https://www.notion.so/xxx`），不是填專案名稱字串。填錯格式會靜默失敗，條目建立成功但 Relation 為空。
- **任務類型是 Multi-select 不是 Select**：值必須用陣列格式 `["🐞 錯誤"]`，不是字串 `"🐞 錯誤"`。用字串格式不會報錯但會建立新的標籤。
- **emoji 是欄位值的一部分**：「🐞 錯誤」、「💬 功能要求」、「💅 細調」中的 emoji 是必要的，不能省略，否則會建立一個新的 Select 選項。
- **Git Repo 識別碼比對必須精確**：`FUB03P2402/LineBC` 和 `FUB03P2402/linebc` 是不同的識別碼。比對時使用原始大小寫，不做 case-insensitive matching。
- **相關任務是 self-relation，用 patch 不是 create**：「自動關聯來源 Feature」設定「相關任務」時，Bug 頁面已在「建立 Notion 條目」一節建立，必須用 `notion-update-page`（patch）而非 `notion-create-pages`。`notion-update-page` 的 Relation 欄位使用 `{"relation": [{"id": "..."}]}` 格式，id 是 page ID 不是 URL。
- **同一個 Bug 可能關聯多個 Feature**：「相關任務」relation 是陣列，若標題比對匹配到多個 Feature，可以全部加入 relation 陣列。但建議限制最多 3 個，避免過度關聯。
- **Feature Branch 可能已被刪除**：「偵測來源 Feature Branch」驗證分支存在性時，Feature 可能已 merge 且分支被清理。這是正常情境，不應視為錯誤。
- **修復分支優先順序**：「偵測來源 Feature Branch」取得的 feature branch 會覆蓋「建立 Notion 條目」一節設定的「修復分支」（通常是當前分支）。若使用者不希望在 feature branch 上修復，「偵測來源 Feature Branch」的互動式選擇允許保留原分支。

---

## 邊界情況

- **設定檔不存在**：提示使用者先執行 `/bug-setup` 完成初始設定
- **不在 Git repo 中**：跳過分支與專案自動偵測，修復分支留空；進入互動式選擇專案；「偵測來源 Feature Branch」跳過
- **使用者未指定專案**：列出進行中的專案供選擇；若只有一個專案則自動選定
- **Notion API 失敗**：顯示錯誤訊息，建議使用者手動在 Notion 建立
- **「相關任務」欄位不存在**（舊版資料庫）：「自動關聯來源 Feature」的 patch-page 會失敗，靜默跳過並提示使用者執行 `/bug-setup` 更新 schema
- **專案無任何 Feature 條目**：「自動關聯來源 Feature」的 query 結果為空，跳過關聯
- **Bug 標題全是停詞**（如「錯誤修復」）：關鍵字擷取為空，跳過「自動關聯來源 Feature」
- **來源 Feature 的「修復分支」為空**：Feature 可能未設定分支（如手動建立的條目），「偵測來源 Feature Branch」跳過
- **來源 Feature 分支已刪除**：「偵測來源 Feature Branch」提供三個選項讓使用者決定修復分支
