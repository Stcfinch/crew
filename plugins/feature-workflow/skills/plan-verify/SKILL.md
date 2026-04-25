---
name: plan-verify
description: 透過 Playwright MCP 操作瀏覽器，逐條驗證 .spec/ 中的驗收條件，產出 verify.md 驗證報告與 Health Score。可選搭配 chrome-devtools-mcp 查 console/network（--deep 模式）。驗證完成後可選擇產出 PDF 或 Word 報告。當使用者提到「plan-verify」、「驗證」、「verify」、「驗收」時觸發此 Skill。
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

- `PASS`：驗證通過
- `FAIL`：驗證失敗（含原因）
- `SKIP`：`--api-only` 跳過 UI 驗證，或使用者手動跳過
- `MANUAL`：需人工確認的項目（如視覺效果）

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

### [2] ❌ 支援匯出 Excel
- **類型**：UI
- **驗證**：點擊匯出按鈕 `#exportBtn`
- **失敗原因**：按鈕不存在（snap 中未找到匹配元素）
- **截圖**：screenshots/verify-2-export.png

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

### 10. 報告產出（選項）

驗證完成後，詢問使用者是否產出正式報告：

```
是否需要產出正式驗證報告？
  1. PDF 格式（適合歸檔和列印）
  2. Word 格式（適合編輯和簽核）
  3. 不需要（只保留 verify.md）
```

#### PDF 報告

使用 `/minimax-pdf` 或 `/make-pdf` Skill 產出：
- 來源：`.spec/{slug}/verify.md`
- 輸出：`.spec/{slug}/verify-report.pdf`
- 含：摘要表格、Health Score、逐條驗證結果、截圖嵌入

#### Word 報告

使用 `/minimax-docx` Skill 產出：
- 來源：`.spec/{slug}/verify.md`
- 輸出：`.spec/{slug}/verify-report.docx`
- 含：同 PDF，但可編輯，適合加簽核欄位

#### 報告內容結構

```
1. 封面（專案名稱、驗證日期、驗證工具）
2. 摘要（Health Score、統計表、結論）
3. 驗證結果明細（每條驗收條件 + 截圖）
4. {若 --deep} 除錯分析（console、network）
5. 後續建議
```

使用者選擇後，呼叫對應 Skill 產出報告，回傳檔案路徑。
若使用者選「不需要」→ 跳過，結束流程。

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
- **PDF/Word 報告依賴外部 Skill**：`/minimax-pdf`、`/make-pdf`、`/minimax-docx` 需要對應的 plugin 已安裝。若不可用，提示使用者安裝或跳過報告產出。

---

## 邊界情況

- **無驗收條件**：提示使用者手動輸入，或建議先執行 `/plan-spec`
- **Playwright MCP 未安裝**：提示安裝指令（`claude mcp add playwright --scope user -- npx @anthropic-ai/mcp-server-playwright@latest`）
- **Playwright 操作失敗**（如 selector 不存在）：標記該條為 FAIL，記錄錯誤訊息，繼續下一條
- **PDF/Word Skill 不可用**：跳過報告產出，提示使用者安裝對應 plugin
- **--api-only 跳過 UI**：UI 類型標記為 SKIP，不影響其他驗證
- **截圖失敗**：記錄警告，不阻斷流程
- **verify.md 已存在**：詢問覆蓋或追加（--recheck 自動合併）
- **驗證過程中使用者中斷**：已完成的結果仍寫入 verify.md（部分報告）
