# Notion 後端偵測與工具映射

CREW 支援兩種 Notion MCP 後端。所有 Skill 在需要呼叫 Notion 時，依本文件的偵測結果選擇對應的工具。

---

## 偵測邏輯

每個 session 第一次需要 Notion 操作時執行一次偵測，結果在整個 session 中復用。

```
1. 檢查是否有 Notion Plugin 工具可用
   （嘗試呼叫任一 Notion Plugin 工具，如 notion-search 或 notion-fetch）
   → 可用 → NOTION_BACKEND = "plugin"

2. 若不可用，檢查是否有 notion-local 工具可用
   （嘗試呼叫 mcp__notion-local__API-post-search 或 API-get-self）
   → 可用 → NOTION_BACKEND = "local"

3. 都不可用 → 提示安裝：
   ⚠️ 未偵測到 Notion MCP。請安裝以下任一方式：

   方式 A（推薦）：Notion Plugin
     claude plugin install notion
     → OAuth 授權，零設定，功能最完整

   方式 B：notion-local（API Token）
     claude mcp add notion-local --scope user -- npx @anthropic-ai/notion-mcp-server
     → 需手動建立 Notion Integration 並設定 NOTION_TOKEN
     → 詳見下方「notion-local 設定指南」
```

**優先順序**：Notion Plugin > notion-local。兩者同時存在時，使用 Notion Plugin。

---

## 工具映射表

AI 在執行 Skill 時，依據偵測到的 `NOTION_BACKEND` 選擇對應的工具名稱和參數格式。

### 搜尋

| 操作 | Notion Plugin | notion-local |
|------|--------------|-------------|
| 搜尋頁面/資料庫 | `notion-search` | `API-post-search` |

**參數差異**：

```
# Notion Plugin
notion-search({ query: "任務追蹤工具", filter: { property: "object", value: "database" } })

# notion-local
API-post-search({ query: "任務追蹤工具", filter: { property: "object", value: "data_source" } })
```

> 注意：notion-local 使用 `"data_source"` 而非 `"database"`。

### 讀取

| 操作 | Notion Plugin | notion-local |
|------|--------------|-------------|
| 讀取頁面（屬性+內容） | `notion-fetch` （一次呼叫） | `API-retrieve-a-page` + `API-get-block-children`（兩次呼叫） |
| 讀取頁面（僅屬性） | `notion-fetch` | `API-retrieve-a-page` |
| 讀取資料庫 schema | `notion-fetch` | `API-retrieve-a-database` 或 `API-retrieve-a-data-source` |

**notion-local 讀取頁面的兩步驟**：

```
# 步驟 1：取得頁面屬性
API-retrieve-a-page({ page_id: "xxx" })

# 步驟 2：取得頁面內容（block children）
API-get-block-children({ block_id: "xxx" })  # block_id = page_id
```

### 建立

| 操作 | Notion Plugin | notion-local |
|------|--------------|-------------|
| 建立頁面 | `notion-create-pages` | `API-post-page` |
| 建立資料庫 | `notion-create-database` | `API-create-a-data-source` |

**建立頁面參數差異**：

```
# Notion Plugin（簡化格式）
notion-create-pages({
  parent: { database_id: "xxx" },
  properties: { "名稱": { title: [{ text: { content: "Bug: 登入失敗" } }] } },
  content: "## 問題描述\n\n..."
})

# notion-local（原生 Notion API 格式）
API-post-page({
  parent: { database_id: "xxx" },
  properties: { "名稱": { title: [{ text: { content: "Bug: 登入失敗" } }] } }
})
# 頁面內容需另外呼叫：
API-patch-block-children({
  block_id: "{新頁面的 page_id}",
  children: [
    { type: "heading_2", heading_2: { rich_text: [{ type: "text", text: { content: "問題描述" } }] } },
    { type: "paragraph", paragraph: { rich_text: [{ type: "text", text: { content: "..." } }] } }
  ]
})
```

### 更新

| 操作 | Notion Plugin | notion-local |
|------|--------------|-------------|
| 更新頁面屬性 | `notion-update-page` | `API-patch-page` |
| 更新頁面內容（追加 block） | `notion-update-page`（content 參數） | `API-patch-block-children` |
| 更新資料庫 schema | `notion-update-data-source` | `API-update-a-data-source` |

**更新頁面屬性（格式相同）**：

```
# Notion Plugin
notion-update-page({ page_id: "xxx", properties: { "狀態": { select: { name: "進行中" } } } })

# notion-local
API-patch-page({ page_id: "xxx", properties: { "狀態": { select: { name: "進行中" } } } })
```

### 查詢

| 操作 | Notion Plugin | notion-local |
|------|--------------|-------------|
| 查詢資料庫條目 | `notion-search`（有限） | `API-query-data-source`（完整 filter 支援） |
| 列出使用者 | `notion-get-users` | `API-get-users` |

**notion-local 的 query-data-source 更強大**：

```
# 可用 filter 精確查詢，Notion Plugin 的 search 做不到
API-query-data-source({
  data_source_id: "xxx",
  filter: {
    property: "狀態",
    select: { equals: "進行中" }
  },
  sorts: [{ property: "建立時間", direction: "descending" }]
})
```

### 不可用操作

| 操作 | Notion Plugin | notion-local | 影響 |
|------|--------------|-------------|------|
| 建立 View | `notion-create-view` | ❌ 不支援 | 僅 setup 時用 |

**降級處理**：當 `NOTION_BACKEND = "local"` 且需要建立 View 時：

```
💡 notion-local 不支援自動建立資料庫 View。
請手動在 Notion 中建立：
  1. 開啟資料庫「{資料庫名稱}」
  2. 點擊左上角的 ＋ 新增 View
  3. 選擇「表格」，命名為「{View 名稱}」
  4. 依需求設定篩選條件和排序

此步驟僅首次設定時需要，不影響後續日常使用。
```

---

## notion-local 設定指南

### 安裝 MCP Server

```bash
claude mcp add notion-local --scope user -- \
  npx @anthropic-ai/notion-mcp-server
```

### 建立 Notion Integration

1. 前往 [notion.so/my-integrations](https://www.notion.so/my-integrations)
2. 點擊「+ New integration」
3. 設定名稱（如 `CREW Bot`）、選擇 Workspace
4. 權限勾選：
   - ✅ Read content
   - ✅ Update content
   - ✅ Insert content
   - ✅ Read user information（用於 get-users）
5. 複製 Internal Integration Secret（`ntn_` 開頭）

### 設定環境變數

```jsonc
// ~/.claude/settings.json
{
  "env": {
    "NOTION_TOKEN": "ntn_xxxxxxxxxxxxx"
  }
}
```

### 授權存取頁面

**重要**：notion-local 使用 API Token，需要**手動將 Integration 加入每個要存取的頁面/資料庫**：

1. 開啟 Notion 中的目標頁面或資料庫
2. 點擊右上角 `···` → 「Connections」
3. 搜尋並加入你建立的 Integration（如 `CREW Bot`）

> 建議將 Integration 加入 CREW 工作區的**最上層頁面**，子頁面會自動繼承權限。

---

## Skill 中的使用方式

Skill 作者在 SKILL.md 中提到 Notion 操作時，**只需描述意圖**（如「搜尋資料庫」「建立頁面」），不需要指定具體工具名稱。AI 會參照本映射表自動選擇正確的工具。

若 Skill 中有具體的 Notion Plugin 工具名稱作為範例，AI 應理解為「概念性操作」，並依據偵測到的後端選擇對應工具。

**範例**：

```
SKILL.md 寫：「使用 notion-search 搜尋任務追蹤工具資料庫」

AI 執行時：
  NOTION_BACKEND = "plugin" → 呼叫 notion-search
  NOTION_BACKEND = "local"  → 呼叫 API-post-search
```

---

## 兩種後端的比較

| 項目 | Notion Plugin | notion-local |
|------|--------------|-------------|
| 認證方式 | OAuth（瀏覽器授權） | API Token（手動設定） |
| 設定難度 | 低（一鍵安裝 + 授權） | 中（建立 Integration + 設定 Token + 授權頁面） |
| 頁面存取 | 授權時選擇的 Workspace 全部可存取 | 需手動將 Integration 加入每個頁面 |
| create-view | ✅ 支援 | ❌ 不支援（手動建立） |
| 資料庫查詢 | 透過 search（有限） | query-data-source（完整 filter） |
| 讀取頁面 | 一次呼叫（fetch） | 兩次呼叫（retrieve + block-children） |
| 離線/CI 環境 | ❌ 需瀏覽器授權 | ✅ Token 即可（適合 CI/CD） |
| 安裝方式 | `claude plugin install notion` | `claude mcp add notion-local ...` |
