---
name: plan-verify
description: 透過 Playwright MCP 操作瀏覽器，逐條驗證 .spec/ 中的驗收條件，產出 verify.md 驗證報告與 Health Score。可選搭配 chrome-devtools-mcp 查 console/network（--deep 模式）。驗證完成後可選擇產出 Word 驗收報告。當使用者提到「plan-verify」、「驗證」、「verify」、「驗收」時觸發此 Skill。
---

# plan-verify — 瀏覽器驗收驗證

透過 **Playwright MCP** 操作瀏覽器，逐條驗證驗收條件，產出 `.spec/{slug}/verify.md` 驗證報告、Health Score 與截圖。

可選搭配 **chrome-devtools-mcp** 做 console log 和 network 除錯分析（`--deep` 模式）。

---

## 使用方式

```
/plan-verify                    # 完整驗證所有驗收條件（Playwright）
/plan-verify --deep             # + chrome-devtools 查 console/network
/plan-verify --manual           # 互動模式，每步驟等待確認
/plan-verify <URL>              # 指定目標頁面
/plan-verify --api-only         # 只驗證 API（不操作 UI，不需瀏覽器）
/plan-verify --recheck          # 僅重新驗證上次失敗的項目
```

---

## 前置條件

### Playwright MCP（必要，預設驗證工具）

```bash
claude mcp add playwright --scope user -- \
  npx @anthropic-ai/mcp-server-playwright@latest
```

Anthropic 官方維護，支援截圖、元素互動、表單填寫、頁面導航。安裝後**重啟 Claude Code**。

### chrome-devtools-mcp（選配，--deep 模式除錯用）

```bash
claude mcp add chrome-devtools --scope user -- \
  npx chrome-devtools-mcp@latest --autoConnect
```

Google 官方維護，提供 console log 串流、network 請求分析、performance trace。
可連接已登入的 Chrome session，適合需要 SSO/VPN 的內部系統。

> 💡 兩者定位不同可同時安裝：Playwright 做 QA 驗收，chrome-devtools 做除錯診斷。

---

## 紀律護欄

> **反合理化**：執行前閱讀 `references/anti-rationalizations.md` 的「通用」和「plan-verify 專用」段落。在任何步驟中感到「可以跳過」的衝動時，查表確認是否為已知偏離模式。
> **動作邊界**：遵循 `references/boundaries.md` 的「plan-verify」段落。🟢 自動做、🟡 先問、🔴 絕不。

---

## 前置檢查流程

執行前**依序檢查**，決定使用工具：

```
1. 檢查 claude mcp list 是否含 "playwright"
   → 有 → 使用 Playwright MCP（預設）
   → 沒有 → 進入步驟 2

2. 檢查 claude mcp list 是否含 "chrome-devtools"
   → 有 → 退回使用 chrome-devtools-mcp
   → 沒有 → 提示安裝 Playwright MCP（推薦）

3. --deep 模式額外檢查 chrome-devtools-mcp 是否可用
   → 可用 → 驗證後追加 console/network 分析
   → 不可用 → 跳過 --deep 功能，僅提示

4. --api-only 模式跳過瀏覽器檢查，只需 curl 可用
```

偵測完成後顯示摘要：

```
🔧 驗證工具：Playwright MCP
🔍 除錯工具：chrome-devtools-mcp（--deep 可用）
```

> **前置檢查**：參照 bug-workflow plugin 的 `references/prerequisites.md` 檢查 CLAUDE.md 是否存在。

---

## 流程

### 1. 定位活躍任務

與 `/plan` 相同邏輯：從 Git branch 或 `.spec/_index.md` 匹配活躍任務。

讀取 `.spec/{slug}/README.md` 取得 `type`（feature/bug）和元資訊。

### 2. 讀取驗收條件

根據任務類型讀取：

| 類型 | 檔案 | 區塊 |
|------|------|------|
| Feature | `.spec/{slug}/spec.md` | 「驗收條件」區塊（通常為 checkbox 清單） |
| Bug | `.spec/{slug}/fix.md` | 「驗證方式」區塊 |

若找不到驗收條件 → 提示使用者手動輸入驗收條件清單。

### 3. 建構驗證計畫

AI 分析每條驗收條件，將其分類並規劃驗證方式：

**MCP 模式工具對照：**

| 類型 | MCP 工具 | 範例 |
|------|---------|------|
| API | curl + Bash | 「可依日期範圍查詢」→ `curl GET /api/xxx?startDate=...&endDate=...` |
| UI 操作 | `click` / `type_text` / `fill` / `take_snapshot` / `take_screenshot` | 「支援分頁」→ 點擊下一頁按鈕，確認表格更新 |
| UI 檢查 | `take_snapshot` → AI 分析 | 「表格顯示正確欄位」→ 讀取無障礙樹檢查欄位 |
| 等待非同步 | `wait_for` | 「搜尋結果載入」→ 等待文字出現 |
| 表單填寫 | `fill_form` | 「表單驗證」→ 批次填入所有欄位 |
| 前端錯誤 | `list_console_messages` | 「頁面無 JS 錯誤」→ 檢查 console |
| 資料驗證 | API + UI 交叉比對 | 「統計數據一致」→ API 回傳值與頁面顯示比對 |

**Bash 模式工具對照：**

| 類型 | 工具 | 範例 |
|------|------|------|
| API | curl + Bash | 同 MCP 模式 |
| UI 操作 | `$CDP click` / `$CDP type` / `$CDP snap` / `$CDP shot` | 同上 |
| UI 檢查 | `$CDP snap` → AI 分析 | 同上 |
| 資料驗證 | API + UI 交叉比對 | 同上 |

讀取 `.spec/{slug}/arch.md` 推斷 API 路徑和頁面 URL（若有）。

展示計畫給使用者確認：

```
即將驗證 {N} 條驗收條件：

| # | 驗收條件 | 類型 | 驗證方式 |
|---|---------|------|---------|
| 1 | 可依日期範圍查詢 | API | GET /api/xxx |
| 2 | 支援分頁顯示 | UI | 點擊下一頁 |
| 3 | 支援匯出 Excel | UI | 點擊匯出按鈕 |

驗證模式：{MCP 工具 / Bash cdp.mjs}
{--api-only: 將跳過 UI 類型驗證}
{--manual: 每步驟等待確認}

確認開始？[Y/n]
```

### 4. 連接 Chrome（非 --api-only 時）

#### MCP 模式

MCP 的 `--autoConnect` 會自動連接本機 Chrome，不需手動處理連線。

使用 `list_pages` 列出所有開啟的分頁，智慧匹配目標 URL：

1. 使用者透過參數指定的 URL
2. 從 `arch.md` 或 `spec.md` 推斷的頁面路徑（如 `/admin/xxx`）
3. 包含 `localhost` 的分頁

匹配後使用 `select_page` 切換到目標分頁。

找不到 → 提示使用者在 Chrome 開啟目標頁面，然後重新 `list_pages`。

#### Bash 模式

```bash
$CDP list
```

從 tab 清單中智慧匹配目標頁面，優先順序同上。

記錄匹配到的 `target_id` 供後續操作。

找不到 → 提示使用者在 Chrome 開啟目標頁面，然後重新 `$CDP list`。

### 5. 逐條驗證

依序對每條驗收條件執行驗證。

#### API 驗證

**MCP 模式：**
```
# 若需登入態，從 Chrome 取 cookie
evaluate_script({ expression: "document.cookie" })

# 呼叫 API（仍用 curl）
curl -s "http://localhost:8080/api/xxx" -H "Cookie: {cookie}" | head -100
```

**Bash 模式：**
```bash
$CDP eval {target} "document.cookie"
curl -s "http://localhost:8080/api/xxx" -H "Cookie: {cookie}" | head -100
```

檢查：HTTP 狀態碼、回應格式、資料筆數、欄位完整性。

#### UI 驗證

**MCP 模式：**
```
# 步驟 1：了解頁面結構
take_snapshot()

# 步驟 2：操作（點擊、輸入等）
click({ selector: "{selector}" })
type_text({ text: "{text}" })
# 或批次填入表單
fill({ selector: "{selector}", value: "{value}" })
fill_form({ fields: [{ selector: "...", value: "..." }, ...] })

# 步驟 3：等待載入完成（MCP 獨有）
wait_for({ text: "搜尋結果" })

# 步驟 4：操作後快照，確認結果
take_snapshot()

# 步驟 5：截圖存證
take_screenshot()

# 額外：偵測前端錯誤（MCP 獨有）
list_console_messages()
```

**Bash 模式：**
```bash
# 步驟 1：了解頁面結構
$CDP snap {target}

# 步驟 2：操作（點擊、輸入等）
$CDP click {target} "{selector}"
$CDP type {target} "{text}"

# 步驟 3：操作後快照，確認結果
$CDP snap {target}

# 步驟 4：截圖存證
$CDP shot {target}
```

AI 分析 snapshot 輸出（無障礙樹）來判斷：
- 元素是否存在
- 內容是否正確
- 操作是否成功

#### `--manual` 模式

每個驗證步驟前後都詢問使用者確認：

```
[2/5] 驗證「支援分頁顯示」
  → 即將點擊下一頁按鈕：#nextPage
  確認執行？[Y/n/skip]
```

#### 記錄結果

每條記錄：

| 欄位 | 說明 |
|------|------|
| 狀態 | `PASS` / `FAIL` / `SKIP` / `MANUAL` |
| 證據 | API 回應摘要 / snap 關鍵節點 / 截圖路徑 |
| 失敗原因 | 僅 FAIL 時記錄 |
| 操作敘述 | 人話描述的操作步驟清單（用於 Word 報告） |

- `PASS`：驗證通過
- `FAIL`：驗證失敗（含原因）
- `SKIP`：`--api-only` 跳過 UI 驗證，或使用者手動跳過
- `MANUAL`：需人工確認的項目（如視覺效果）

#### 操作敘述記錄

每條驗證項目執行時，AI **同步**產生一份「人話操作步驟」。此敘述：
- 用非技術人員可讀的語言撰寫
- 描述「做了什麼」而非「用了什麼指令」
- 包含預期結果與實際結果的比對

此資料暫存於 AI 工作記憶中，寫入 verify.md 的 `<!-- human_steps -->` 註解區塊，
並在步驟 10 產出 Word 報告時使用。

**翻譯對照表**：

| Playwright 操作 | 人話敘述 |
|----------------|---------|
| `browser_navigate({ url })` | 開啟「{頁面名稱}」頁面 |
| `browser_click({ element })` | 點擊「{元素描述}」按鈕/連結 |
| `browser_type({ element, text })` | 在「{欄位名稱}」欄位輸入 {值} |
| `browser_fill_form({ fields })` | 依序填入表單：{欄位1}={值1}、{欄位2}={值2} |
| `browser_select_option({ element, value })` | 在「{欄位名稱}」下拉選單選擇「{選項}」 |
| `browser_snapshot()` | 觀察頁面內容 |
| `browser_take_screenshot()` | 截取畫面存證 |
| `browser_wait_for({ text })` | 等待頁面顯示「{文字}」 |
| `browser_press_key({ key })` | 按下 {按鍵} 鍵 |
| `curl GET /api/xxx?params` | 透過系統 API 查詢{功能描述}（參數：{參數說明}） |
| `curl POST /api/xxx` | 透過系統 API 新增{功能描述} |
| HTTP 狀態碼回傳 | 系統回應{狀態描述} |

**翻譯原則**：
1. 不出現程式碼（selector、URL path、HTTP method）
2. 使用頁面上的實際文字（「查詢」不是 `#queryBtn`）
3. 合併連續操作（`click` → `wait_for` → `snapshot` → 「點擊 XX 按鈕，等待頁面載入完成」）
4. 結果用白話（「HTTP 200, 15 rows」→「系統成功回傳 15 筆資料」）
5. 省略技術診斷操作（`evaluate_script`、`list_console_messages` 不納入）

### 6. 收集截圖

```bash
mkdir -p .spec/{slug}/screenshots
```

將驗證過程中的截圖複製到 `.spec/{slug}/screenshots/`：

**MCP 模式**：`take_screenshot` 回傳截圖內容，直接儲存。

**Bash 模式**：
```bash
# cdp.mjs 截圖預設輸出至 ~/.cache/cdp/ 或目前目錄
cp {screenshot_path} .spec/{slug}/screenshots/verify-{N}-{desc}.png
```

命名規則：`verify-{序號}-{簡述}.png`，如 `verify-1-query-result.png`。

### 7. 產出 verify.md

寫入 `.spec/{slug}/verify.md`：

```markdown
# 驗證報告

## 摘要

| 項目 | 值 |
|------|-----|
| 驗證日期 | {YYYY-MM-DD} |
| 環境 | {localhost:8080 或使用者指定} |
| 模式 | {完整 / api-only / manual / recheck} |
| 驗證工具 | {chrome-devtools-mcp / cdp.mjs} |

## 統計

| 狀態 | 數量 |
|------|------|
| ✅ PASS | {N} |
| ❌ FAIL | {N} |
| ⏭️ SKIP | {N} |
| 👤 MANUAL | {N} |

## 驗證結果

### [1] ✅ 可依日期範圍查詢
- **類型**：API
- **驗證**：`GET /api/xxx?startDate=2026-01-01&endDate=2026-03-16` → HTTP 200, 15 筆
- **截圖**：screenshots/verify-1-query-result.png
<!-- human_steps
- 操作：透過系統 API 查詢推播統計（日期範圍：2026-01-01 至 2026-03-16）
- 預期：系統回傳查詢結果，資料筆數大於 0
- 實際：系統成功回傳 15 筆資料，格式正確
-->

### [2] ❌ 支援匯出 Excel
- **類型**：UI
- **驗證**：點擊匯出按鈕 `#exportBtn`
- **失敗原因**：按鈕不存在（snap 中未找到匹配元素）
- **截圖**：screenshots/verify-2-export.png
<!-- human_steps
- 操作：在推播統計頁面尋找「匯出 Excel」按鈕
- 預期：頁面應有「匯出 Excel」按鈕，點擊後下載 .xlsx 檔案
- 實際：頁面上未找到「匯出」相關按鈕，功能尚未實作
-->

### [3] ⏭️ 支援分頁顯示
- **類型**：UI
- **跳過原因**：--api-only 模式

### [4] 👤 報表視覺呈現正確
- **類型**：UI 檢查
- **說明**：需人工確認圖表渲染效果
- **截圖**：screenshots/verify-4-chart.png
```

### 8. 更新 .spec/

1. 更新 `README.md`：`status: 驗證中`
2. 在 `log.md` 追加紀錄：

```markdown
### [{日期}] 驗收驗證
- **模式**：{完整/api-only/manual/recheck}
- **工具**：{chrome-devtools-mcp / cdp.mjs}
- **結果**：✅ {N} / ❌ {N} / ⏭️ {N} / 👤 {N}
- **報告**：verify.md
```

### 9. 回傳結果

```
驗收驗證完成！

📋 報告：.spec/{slug}/verify.md
📸 截圖：.spec/{slug}/screenshots/ ({N} 張)
📊 統計：✅ {PASS} / ❌ {FAIL} / ⏭️ {SKIP} / 👤 {MANUAL}
🔧 工具：Playwright MCP{，chrome-devtools-mcp（--deep）}

{若有 FAIL}
⚠️  發現 {N} 個驗收條件未通過，建議修復後執行 /plan-verify --recheck

{若全部 PASS}
🎉 所有驗收條件通過！

後續可使用：
  • /plan-verify --recheck — 重新驗證失敗項目
  • /plan-review          — Agent Teams 程式碼審查
  • /plan-close           — 結案並同步 Notion
```

### 10. 報告產出（Word 驗收報告）

驗證完成後，詢問使用者是否產出正式 Word 驗收報告：

```
是否產出 Word 驗收報告？[Y/n]
```

使用者輸入 `n` → 跳過，結束流程。
使用者輸入 `Y`（或直接 Enter）→ 進入報告產出流程。

#### 10.1 收集封面資訊

依以下優先順序取得每項封面資訊：

| 欄位 | 自動來源 | 備用來源 | 存檔位置 |
|------|---------|---------|---------|
| 專案名稱 | `projects/{id}.md` 的 `notion_name` | 詢問使用者 | `report-config.md` |
| 功能名稱 | `.spec/{slug}/README.md` 的 `name` | 詢問使用者 | — |
| 驗證日期 | verify.md 的驗證日期 | 當天日期 | — |
| 版本號 | `.spec/{slug}/README.md` 的 frontmatter | 詢問使用者（如 `v1.0`） | — |
| 承辦單位 | `report-config.md` 的 `company_name` | 詢問使用者 | `report-config.md` |
| 製作人 | `report-config.md` 的 `author` | 詢問使用者 | `report-config.md` |

**`report-config.md` 位置**：`~/.claude-company/feature-workflow/report-config.md`

**確認流程**：

1. 自動帶入所有能找到的欄位值
2. 展示給使用者確認：
   ```
   📋 報告封面資訊：
     專案名稱：{自動帶入或待填}
     功能名稱：{自動帶入}
     驗證日期：{自動帶入}
     版本號：{自動帶入或待填}
     承辦單位：{自動帶入或待填}
     製作人：{自動帶入或待填}

   確認？[Y/n] 或輸入欄位名稱修改（如「版本號 v2.0」）
   ```
3. 使用者確認後，將 `company_name` 和 `author` 存入 `report-config.md`（若不存在則建立）

#### 10.2 收集測試環境資訊

| 欄位 | 自動來源 | 備用來源 |
|------|---------|---------|
| 測試 URL | verify.md 摘要的「環境」欄位 | 詢問使用者 |
| 瀏覽器 | 自動偵測（Playwright 預設 Chromium） | `Chromium（Playwright 控制）` |
| 測試帳號角色 | 詢問使用者 | 「系統管理員」 |
| 測試資料說明 | 詢問使用者（可選） | 「使用測試環境既有資料」 |
| 前置條件 | `.spec/{slug}/spec.md` 的前置條件區塊 | 詢問使用者 |

展示後一次確認：

```
🔧 測試環境：
  URL：{自動帶入}
  瀏覽器：Chromium（Playwright 控制）
  測試帳號角色：（請輸入，如「系統管理員」）
  測試資料說明：（請輸入，或 Enter 跳過）
  前置條件：{自動帶入或待填}

確認？[Y/n]
```

#### 10.3 組裝報告內容

AI 依以下七段式結構組裝 Markdown 報告內容（作為 `/minimax-docx` 的輸入）：

**1. 封面**

```markdown
# {專案名稱}

## {功能名稱} — 驗收報告

| 項目 | 值 |
|------|-----|
| 驗證日期 | {YYYY-MM-DD} |
| 版本號 | {vX.Y} |
| 承辦單位 | {公司全名} |
```

**2. 簽核欄位**

```markdown
## 簽核

| 角色 | 姓名 | 簽章 | 日期 |
|------|------|------|------|
| 製作人 | {author} | | |
| 審核人 | | | |
| 客戶確認 | | | |
```

**3. 測試環境說明**

```markdown
## 測試環境

| 項目 | 說明 |
|------|------|
| 測試 URL | {URL} |
| 瀏覽器 | {瀏覽器} |
| 測試帳號角色 | {角色} |
| 測試資料說明 | {說明} |
| 前置條件 | {前置條件} |
```

**4. 驗收摘要**

```markdown
## 驗收摘要

| 狀態 | 數量 |
|------|------|
| 通過 | {N} |
| 未通過 | {N} |
| 略過 | {N} |
| 待人工確認 | {N} |

**結論**：{AI 依統計生成一句話結論}
```

結論生成規則：
- 全部 PASS → 「共 N 項驗收條件全數通過，建議進入正式上線流程。」
- 有 FAIL → 「共 N 項驗收條件，M 項未通過，需修正後重新驗證。」
- 有 MANUAL 無 FAIL → 「共 N 項驗收條件，M 項通過、K 項待人工確認。」

**5. 驗收明細**（每條一個段落，使用 `<!-- human_steps -->` 中的操作敘述）

```markdown
### 驗收項目 {N}：{驗收條件名稱}

**結果：{通過/未通過/略過/待人工確認}** {✅/❌/⏭️/🔍}

**操作步驟**：
1. {人話操作步驟 1}
2. {人話操作步驟 2}
...

**預期結果**：{人話預期}

**實際結果**：{人話實際}

**截圖**：
![{描述}](screenshots/verify-{N}-{desc}.png)
```

**6. 待處理事項**（僅 FAIL / MANUAL 時）

```markdown
## 待處理事項

| # | 驗收條件 | 狀態 | 建議處理方式 |
|---|---------|------|------------|
| {N} | {條件} | {未通過/待人工確認} | {建議} |
```

**7. 附錄**

```markdown
## 附錄

### 版本紀錄

| 日期 | 版本 | 說明 |
|------|------|------|
| {日期} | {版本} | 初次驗收 |

### 工具版本

| 工具 | 版本 |
|------|------|
| Playwright MCP | @anthropic-ai/mcp-server-playwright@latest |
| Claude Code | {版本} |

### 參考文件

- 技術規格書：.spec/{slug}/spec.md
- 驗證技術紀錄：.spec/{slug}/verify.md
```

#### 10.4 呼叫 /minimax-docx 產出

```
使用 `/minimax-docx` Skill 產出：
- 輸入：AI 組裝的 Markdown 報告內容
- 輸出：`.spec/{slug}/verify-report.docx`
- 含：封面、簽核表、環境說明、摘要、逐條驗證明細（含截圖嵌入）、待處理事項、附錄
```

#### 10.5 完成提示

```
📄 驗收報告已產出：.spec/{slug}/verify-report.docx

報告包含：
  • 封面與簽核欄位
  • 測試環境說明
  • {N} 條驗收明細（含操作步驟與截圖）
  • {若有} 待處理事項 {M} 項

提示：可用 Word 開啟後自行調整格式或轉存 PDF。
```

#### 向下相容：舊版 verify.md

若 verify.md 中無 `<!-- human_steps -->` 註解（舊版產出）：
1. 進入降級模式：AI 從 verify.md 的技術驗證內容反推操作敘述
2. 在報告封面加註：「※ 操作步驟由系統自動轉譯，可能與實際操作有微差異」

---

## --recheck 模式

讀取既有 `.spec/{slug}/verify.md`，解析其中 `❌ FAIL` 的項目：

1. 只重跑 FAIL 項目
2. 結果合併回**同一份** verify.md（覆蓋對應項目的狀態）
3. 更新統計區塊
4. 在 log.md 追加 recheck 紀錄

---

## --deep 模式（chrome-devtools-mcp 除錯增強）

標準驗證（Playwright）完成後，`--deep` 模式額外使用 chrome-devtools-mcp 做除錯分析：

| 工具 | 用途 | 場景 |
|------|------|------|
| `list_console_messages` | console 完整掃描（含 warning） | 偵測前端錯誤和警告 |
| `list_network_requests` | network 請求分析 | 失敗/慢請求偵測 |
| `performance_start/stop_trace` | 效能追蹤 | 頁面載入效能驗證 |
| `lighthouse_audit` | Lighthouse 稽核 | 效能/可及性報告 |
| `emulate` | 裝置/網路模擬 | 行動裝置驗證 |

結果追加到 verify.md 的「除錯分析」段落。

---

## Gotchas

- **Playwright snapshot 是 accessibility tree**：`browser_snapshot` 回傳的是無障礙樹，隱藏的 `<input type="hidden">`、純裝飾的 `<div>` 不可見。需要查 DOM 時用 `browser_evaluate` 執行 `document.querySelector()`。
- **httpOnly cookie 無法用 document.cookie 取得**：session cookie 常設為 httpOnly。API 驗證若需登入態，用 Playwright 的 `browser_evaluate` 中 `fetch()` 直接發請求。
- **Playwright 和 chrome-devtools 的截圖路徑不同**：Playwright 的 `browser_take_screenshot` 存到指定路徑；chrome-devtools 的 `take_screenshot` 回傳 base64。收集截圖到 `.spec/{slug}/screenshots/` 時需注意。
- **--deep 模式需要 chrome-devtools-mcp**：若未安裝，`--deep` 功能不可用但不影響標準驗證。提示使用者安裝。
- **Word 報告依賴 `/minimax-docx` Skill**：需要 minimax-skills plugin 已安裝。若不可用，提示使用者安裝（`找不到 /minimax-docx Skill，請確認 minimax-skills plugin 已安裝`），並跳過報告產出。
- **截圖嵌入 Word**：`/minimax-docx` 接受 Markdown 格式的圖片引用（`![](path)`）。確保截圖路徑使用相對於 `.spec/{slug}/` 的相對路徑。
- **封面資訊快取**：`report-config.md` 儲存於 `~/.claude-company/feature-workflow/` 下，跨專案共用（公司名稱、作者）。首次產出報告時建立。

---

## 邊界情況

- **無驗收條件**：提示使用者手動輸入，或建議先執行 `/plan-spec`
- **Playwright MCP 未安裝**：提示安裝指令（`claude mcp add playwright --scope user -- npx @anthropic-ai/mcp-server-playwright@latest`）
- **Playwright 操作失敗**（如 selector 不存在）：標記該條為 FAIL，記錄錯誤訊息，繼續下一條
- **`/minimax-docx` 不可用**：跳過報告產出，提示使用者安裝 minimax-skills plugin
- **`report-config.md` 不存在**：首次詢問所有封面欄位，產出後自動建立
- **截圖路徑無效**：報告中標註「（截圖不可用）」，不阻斷報告產出
- **verify.md 無 `human_steps` 註解**（舊版 verify.md）：從 verify.md 技術內容反推操作敘述（降級模式）
- **--api-only 跳過 UI**：UI 類型標記為 SKIP，不影響其他驗證
- **截圖失敗**：記錄警告，不阻斷流程
- **verify.md 已存在**：詢問覆蓋或追加（--recheck 自動合併）
- **驗證過程中使用者中斷**：已完成的結果仍寫入 verify.md（部分報告）
