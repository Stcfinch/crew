# 技術規格書 — plan-verify 進化

## Phase 1：萃取 + 內建（所有專案受益）

### 1.1 截圖穩定化策略

**來源**：SmartRobotE2ETest `tests/global-hooks.js`

新增 `references/verify-stability.md`，SKILL.md 的「截圖前準備」段落引用此 reference。

每次截圖前強制執行：

```
1. evaluate: press Escape × 2（關閉 modal / dropdown / tooltip，間隔 300ms）
2. evaluate: 若 #testPanel 可見，點擊 toggle 關閉
3. evaluate: window.scrollTo(0, 0)（回到頁面頂部）
4. waitForLoadState('networkidle', timeout: 3000).catch(() => {})
5. waitForTimeout(1500)（等動畫結束）
6. take fullPage screenshot
```

截圖失敗時的 retry：最多重試 3 次，每次多等 1s。若仍失敗，標記「(截圖不可用)」繼續。

### 1.2 元素定位 Fallback 策略

**來源**：SmartRobotE2ETest `tests/rob0002-sidebar-nav.spec.js`、`tests/helpers/i18n-helper.js`

SKILL.md 新增「元素定位策略」段落，定義嘗試順序：

| 優先級 | 策略 | 範例 | 適用場景 |
|--------|------|------|---------|
| 1 | 穩定 selector（ID/name/class） | `#searchKeyword`, `input[name="code"]` | 有明確 ID/name 的元素 |
| 2 | Role + 翻譯文字 | `getByRole('link', { name: getText('myRobot') })` | 選單、按鈕 |
| 3 | CSS 屬性 selector | `a[href*="/push/stat"]` | 連結類元素 |
| 4 | 直接 URL 導航 | `browser_navigate({ url: baseUrl + path })` | 最終 fallback |

每次 fallback 觸發時，記錄到驗證記憶（見 §5）。

### 1.3 軟斷言 + WARN 狀態

**來源**：SmartRobotE2ETest 的 soft assertion 模式

verify.md 新增 `⚠️ WARN` 狀態（介於 PASS 和 FAIL 之間）：

| 狀態 | 意義 | 場景 |
|------|------|------|
| ✅ PASS | 完全通過 | 驗證結果符合預期 |
| ⚠️ WARN | 通過但有疑慮 | 環境差異導致的預期外行為；功能正常但 selector 不穩定 |
| ❌ FAIL | 未通過 | 驗證結果不符合預期 |
| ⏭️ SKIP | 略過 | 無法自動化或不適用 |
| 👤 MANUAL | 待人工確認 | 需要外部系統比對 |

### 1.4 Excel 報告格式

**來源**：SmartRobotE2ETest `tests/excel-reporter.js`（ExcelJS）

新增 `references/verify-excel-template.md`，定義 Excel 報告規格。

#### Sheet 1: 驗收總表

- 標題區：專案名稱、功能名稱、驗收報告（合併儲存格，深藍背景）
- 資訊區：驗證日期、驗測人員、測試環境 URL、測試語系、驗測工具
- 明細表：

| 欄位 | 寬度 | 內容 |
|------|------|------|
| # | 6 | 序號 |
| 驗收條件 | 40 | 條件文字 |
| 結果 | 10 | ✅/❌/⚠️/⏭️/👤，背景色區分 |
| 截圖 | 12 | 超連結到步驟 Sheet |
| 備註 | 30 | FAIL 原因或 WARN 說明 |
| 測試日期 | 14 | YYYY-MM-DD |

- 簽核區：製作人 / 審核人 / 客戶確認（底部表格）
- 凍結標題列

#### Sheet 2~N: 各驗收項目步驟

- 標頭：驗收條件名稱、結果
- 操作步驟：編號 + 人話敘述（from verify.md 的 `<!-- human_steps -->`）
- 預期結果 / 實際結果
- 嵌入截圖（讀取 PNG 寬高，縮放到 800px 寬）
- API 測試紀錄（若有 `<!-- evidence -->` 區塊）
- 底部：超連結回驗收總表

#### 敏感資訊遮罩

與 Word 報告相同規則：Cookie `JSES****f456`、Authorization `Bearer eyJh****`

#### 產出方式

`references/verify-excel-generator.js` — 獨立 Node.js 腳本，內建在 plugin 中。

呼叫方式：
```bash
node {plugin_path}/references/verify-excel-generator.js \
  --verify .spec/{slug}/verify.md \
  --screenshots .spec/{slug}/screenshots/ \
  --evidence .spec/{slug}/evidence/ \
  --output .spec/{slug}/verify-report.xlsx \
  --cover '{"project":"SmartRobot","feature":"推播統計","author":"Cheng"}'
```

依賴：`npx --yes exceljs`（自動安裝，不污染專案 node_modules）

### 1.5 i18n 驗證指引

**來源**：SmartRobotE2ETest `tests/helpers/i18n-helper.js`

新增 `references/verify-i18n.md`，定義多語系驗證策略。

#### 先支援 4 語系

| 語系 | 代碼 | 優先順序 |
|------|------|---------|
| 繁體中文 | zh-TW | 1（預設） |
| 簡體中文 | zh-CN | 2 |
| 英文 | en-US | 3 |
| 日文 | ja-JP | 4 |

#### 語系偵測順序

1. spec.md 指定語系（驗收條件可能寫「測試英文版」）
2. 瀏覽器頁面的 `<html lang="...">`（evaluate 取得）
3. 產品知識庫的預設語系
4. 預設 zh-TW

#### 驗證策略

**產品模式**（有 product_id）：
- 載入 products/{id}.md 的 i18n 對照表
- 用翻譯文字做元素定位（如 getText('myRobot') → "My Robot"）
- 截圖反映實際測試語系，報告永遠繁體中文

**通用模式**（無 product_id）：
- 優先用穩定 selector（ID/name/class），不依賴文字
- Snapshot → AI 解讀 a11y tree（語言無關）
- evaluate DOM 查詢（語言無關）

---

## Phase 2：產品知識庫（產品專案加速）

### 2.1 產品定義檔

新增 `products/` 目錄，存放產品操作知識。

#### products/smartrobot.md

```markdown
---
name: SmartRobot
stack: spring-boot-jpa
i18n_locales: [zh-TW, zh-CN, en-US, ja-JP]
login_types: [subadmin, admin]
---

## 頁面導航地圖

| 功能 | URL 路徑 | 登入方式 | 選單路徑 |
|------|----------|---------|----------|
| 一般問答 | /qa/list | subadmin | 我的機器人 → 一般問答 |
| 推播統計 | /push/stat | subadmin | 推播 → 統計 |
| 使用者管理 | /user/list | admin | 系統 → 使用者 |
| Dashboard | /dashboard | subadmin | Dashboard |
...（從 SmartRobotE2ETest 的 SIDEBAR_GROUPS 萃取）

## 常用 Selector

| 元素 | Selector | 備註 |
|------|----------|------|
| 搜尋框 | #searchKeyword | 全站通用 |
| 送出表單 | #submitForm | 全站通用 |
| 匯出按鈕 | a.btn.btnBlue.btnExport | class-based |
| 匯入按鈕 | a.btn.btnBlue.btnImport | class-based |
| 分頁下一頁 | .pagination .next a | 全站通用 |
| 刪除確認 | .swal2-confirm | SweetAlert2 |

## i18n 關鍵字對照（高頻操作用）

| Key | zh-TW | en-US | zh-CN | ja-JP |
|-----|-------|-------|-------|-------|
| myRobot | 我的機器人 | My Robot | 我的机器人 | マイロボット |
| generalQA | 一般問答 | General QA | 一般问答 | 一般Q&A |
| add | 新增 | Add | 新增 | 追加 |
| edit | 編輯 | Edit | 编辑 | 編集 |
| delete | 刪除 | Delete | 删除 | 削除 |
| search | 搜尋 | Search | 搜索 | 検索 |
| save | 儲存 | Save | 保存 | 保存 |
| confirm | 確認 | Confirm | 确认 | 確認 |
| cancel | 取消 | Cancel | 取消 | キャンセル |
| export | 匯出 | Export | 导出 | エクスポート |
| import | 匯入 | Import | 导入 | インポート |
...（從 i18n-helper.js 的 KEY_MAPPING 萃取導航+操作類約 40 個）

## 特殊操作 Recipe

### CKEditor 富文字編輯器
回答欄位使用 CKEditor，不能直接 fill，必須用 JS API：
```js
window.CKEDITOR.instances[name].setData(content);
window.CKEDITOR.instances[name].updateElement();
```

### SweetAlert2 確認框
刪除等危險操作使用 SweetAlert2，確認按鈕 selector：`.swal2-confirm`

### 表單提交
部分頁面使用 AJAX 提交而非 form submit，需要等 networkidle 而非頁面跳轉。

## API 回傳格式（Spring Boot JPA）

### 列表查詢（Pageable）
```json
{
  "content": [...],
  "totalElements": 100,
  "totalPages": 10,
  "size": 10,
  "number": 0
}
```
驗證分頁時檢查：totalElements > 0、content.length == size、number 正確遞增

### 儲存/更新
```json
{ "code": "0000", "message": "success", "data": {...} }
```

### 刪除
```json
{ "code": "0000", "message": "success" }
```
```

### 2.2 產品偵測邏輯

projects/{repo-id}.md 新增 `product_id` 欄位：

```yaml
---
notion_name: "WiSe"
git_repo: "FUB03P2402/WiSe"
stack: "spring-boot-jpa"
product_id: "smartrobot"      # 指向 products/smartrobot.md
prod_branch: "main"
---
```

plan-verify 啟動時：
1. 讀取 projects/{repo-id}.md
2. 有 product_id → 載入 products/{product_id}.md 作為驗證 context
3. 無 product_id → 通用模式

### 2.3 project-add 擴充

`/project-add` 新增產品關聯步驟：

```
偵測 git remote → 建立 projects/{id}.md
→ 「是否屬於某個產品？」
→ YES → 選擇或新增產品 → 寫入 product_id
→ NO → 通用模式
```

---

## Phase 3：E2E 橋接（可選進階整合）

### 前提

團隊已有 SmartRobotE2ETest repo（或其他 E2E repo）。此 Phase 為「錦上添花」，不是核心功能。

### 3.1 Runner 模式（--e2e）

projects/{repo-id}.md 可選欄位：

```yaml
e2e_repo: "/Users/cheng/IdeaProjects/SmartRobotE2ETest"
e2e_profile: "c"
```

#### 條件匹配引擎

E2E repo 內新增 `tests/verify-map.json`（外部映射檔）：

```json
{
  "rob0027": {
    "describe": "一般問答完整測試",
    "mappings": [
      { "condition": "QA 新增", "steps": "1-12", "key_screenshot": "step-10-save" },
      { "condition": "QA 搜尋", "steps": "13-14", "key_screenshot": "step-13-search" },
      { "condition": "QA 編輯", "steps": "15-18", "key_screenshot": "step-18-edited" },
      { "condition": "QA 測試觸發", "steps": "19-21", "key_screenshot": "step-21-trigger" },
      { "condition": "QA 刪除", "steps": "22-25", "key_screenshot": "step-25-deleted" }
    ]
  }
}
```

匹配策略：
1. 關鍵字比對（驗收條件文字 vs mappings[*].condition）
2. URL 路徑比對（spec.md 的 API → spec.js 的 URL）
3. AI 語意比對（最終手段）

#### 混合執行流程

- 有匹配：`PROFILE={p} npx playwright test {file}` → 收集 JSON 結果 + 截圖 → 轉換成 verify.md 條目
- 無匹配：退回 Playwright MPC 模式（Phase 1+2 強化版）

一個 E2E 測試只跑一次，結果按 verify-map.json 的 steps 範圍分段給各驗收條件。

#### Profile 選擇

讀取 E2E repo 的 `tests/config/profile-*.js`，提取 name + baseUrl 顯示給使用者：

```
偵測到 E2E 測試 repo，以下 Profile 可用：
  A: SE 測試環境 (https://se.smartrobot...)
  B: Staging (https://staging.smartrobot...)
  C: 開發環境 (http://localhost:8080)  ← 預設
使用 Profile C？[Y/n/選擇其他]
```

### 3.2 測試骨架產出

plan-verify 完成後（所有 PASS），可選產出 E2E 測試骨架：

- 定位：**80% 完成度的骨架**，不追求直接可跑
- 包含：import 結構、describe/test 骨架、登入流程、基本 click/fill/assert、步驟截圖、i18n getText、console.log 步驟格式
- 標記：TODO/FIXME 註明需人工調整的地方（環境差異、特殊元件操作、等待策略）
- 流程：產出 → 試跑 → 人工 review + 修正 → 加入 verify-map.json → commit

### 3.3 E2E 結果回饋

```
plan-verify --from-e2e {test-results-dir}
```

讀取 Playwright JSON 結果 + 截圖 → 匹配到 spec.md 驗收條件 → 更新 verify.md

---

## 跨階段功能：驗證記憶系統

### 5.1 三層記憶架構

| 層級 | 存放位置 | 共享方式 | 生命週期 |
|------|---------|---------|---------|
| Layer 3 產品級 | plugin `products/{id}-memory.md` | plugin 升版自動同步 | 長期（跟隨 plugin） |
| Layer 2 專案級 | 專案 repo `.claude/verify-memory.md` | git 追蹤，push 後同事可用 | 中期（跟隨專案） |
| Layer 1 任務級 | `.spec/{slug}/verify-memory.md` | 不共享 | 短期（跟隨任務） |

載入順序：Layer 3 → Layer 2 → Layer 1（由通用到具體，後者覆蓋前者）
升級方向：Layer 1 → Layer 2 → Layer 3（由具體到通用，經驗匯聚）

### 5.2 記憶檔格式

```markdown
# verify-memory.md

---
project: FUB03P2402/WiSe
product: smartrobot
last_updated: 2026-05-15
---

## 頁面操作記憶

### /push/stat（推播統計）
- **導航**: sidebar「推播」→「推播統計」，或直接 URL
- **搜尋框**: `#searchKeyword`（穩定）
- **日期選擇器**: flatpickr，需要 click + 選日期 + click 外部關閉
- **分頁**: `.pagination .next a`，AJAX 載入需等 networkidle + 1s
- **匯出**: `a.btnExport`，觸發下載，需 download event listener
- **等待策略**: 查詢後等 networkidle + 1.5s
- **已知問題**: 資料量 > 1000 筆時載入慢，timeout 要設 10s

## Selector 記憶

| 元素 | 有效 Selector | 無效（別再試） | 備註 |
|------|--------------|---------------|------|
| 搜尋框 | #searchKeyword | .search-input | 全站通用 |
| 送出 | #submitForm | button[type=submit] | 全站通用 |

## API 回傳格式記憶

| API Pattern | 回傳格式 | 驗證要點 |
|-------------|---------|---------|
| GET /api/*/list | Spring Page | content, totalElements, size, number |
| POST /api/*/save | { code, message, data } | code == "0000" |

## 截圖策略記憶

- 全站 modal 關閉: ESC×2（SweetAlert2 + Bootstrap Modal）
- 表格截圖: scroll to table top，不要 fullPage（太長）

## 踩坑紀錄

| 日期 | 情境 | 問題 | 解法 |
|------|------|------|------|
| 2026-05-15 | QA 編輯 | contenteditable 不同步到 hidden input | evaluate 手動同步 |
```

### 5.3 記憶生命週期

#### 驗證中：即時累積

plan-verify 執行每個步驟後，AI 判斷是否值得記錄：

| 觸發條件 | 記錄內容 |
|---------|---------|
| selector 第 1 次嘗試失敗 | 有效/無效 selector 對照 |
| 等待策略調整過 | 最終有效的等待策略 |
| 用了 evaluate 做特殊操作 | 特殊步驟 recipe |
| 發現環境差異 | 環境差異描述 |
| 順利完成（未觸發 fallback） | 不記錄 |

暫存在 `.spec/{slug}/verify-memory.md`（Layer 1）

#### 任務結案：升級判斷

plan-verify 完成或 plan-close 時：

1. 讀取 `.spec/{slug}/verify-memory.md`
2. AI 判斷哪些發現值得升級到專案級
3. 升級標準：
   - ✅ 升級：頁面通用的操作知識、全站共用 selector、專案統一的 API 格式
   - ❌ 不升級：任務特有的一次性操作、測試資料相關、Bug workaround
4. 提問使用者確認：「本次發現 {N} 個新操作模式，要升級到專案記憶嗎？[Y/n]」
5. 合併到 `.claude/verify-memory.md`（Layer 2）

#### Plugin 升版：產品級萃取

Plugin 維護者定期 review 各專案的 Layer 2 記憶，跨專案重複出現的模式升級到 `products/{id}-memory.md`（Layer 3），升版後所有人自動獲得。

### 5.4 SKILL.md 的記憶整合點

| 步驟 | 記憶操作 |
|------|---------|
| Step 2.5（驗證計畫前） | 載入 Layer 3 → 2 → 1 記憶，注入 AI context |
| Step 5.5（每步驟後） | 即時判斷是否記錄（僅記錄異常/fallback） |
| Step 9.5（驗證完成後） | 寫入 Layer 1，提議升級到 Layer 2 |

---

## 驗收條件

### Phase 1

- [ ] SKILL.md 新增截圖穩定化段落，引用 references/verify-stability.md
- [ ] SKILL.md 新增元素定位 Fallback 策略段落
- [ ] verify.md 支援 ⚠️ WARN 狀態
- [ ] 新增 references/verify-excel-template.md
- [ ] 新增 references/verify-excel-generator.js（ExcelJS 獨立腳本）
- [ ] plan-verify 新增 --excel 選項
- [ ] plan-verify 新增 --word --excel 同時產出選項
- [ ] 新增 references/verify-i18n.md
- [ ] plan-verify 偵測頁面語系，用穩定 selector 優先

### Phase 2

- [ ] 新增 products/ 目錄，含 smartrobot.md
- [ ] smartrobot.md 包含：頁面導航地圖、常用 Selector、i18n 對照表、特殊操作 Recipe、API 格式
- [ ] projects/{id}.md 支援 product_id 欄位
- [ ] plan-verify 偵測 product_id，載入產品知識庫
- [ ] /project-add 新增產品關聯步驟
- [ ] stacks/_builtin.md 補充 spring-boot-jpa 的驗證知識

### Phase 3

- [ ] projects/{id}.md 支援 e2e_repo / e2e_profile 可選欄位
- [ ] plan-verify --e2e 模式：讀取 verify-map.json，條件匹配 + Runner 執行
- [ ] 無匹配條件退回 MPC 模式
- [ ] Runner 結果轉換為 verify.md 格式
- [ ] Profile 選擇：讀 profile-*.js 顯示選項
- [ ] 測試骨架產出（plan-verify 完成後可選）
- [ ] plan-verify --from-e2e 模式

### 驗證記憶系統

- [ ] Layer 1：.spec/{slug}/verify-memory.md 自動產出
- [ ] Layer 2：.claude/verify-memory.md 升級機制
- [ ] Layer 3：products/{id}-memory.md 格式定義
- [ ] plan-verify 啟動時自動載入三層記憶
- [ ] 記錄觸發條件實作（selector 失敗、等待調整、特殊操作）
- [ ] 結案時升級提議 + 使用者確認
