# 程式碼審查報告

## 複審結果（修復後）
2026-05-15 — 6/6 項修復全部通過驗證 ✅

| # | 原問題 | 修復狀態 |
|---|--------|---------|
| 🔴1 | verify-i18n.md product_id 來源路徑 | ✅ 已改為 projects/{repo-id}.md |
| 🔴2 | verify-excel-template.md 呼叫參數 | ✅ 已補 --evidence、--cover 改 JSON |
| 🔴3 | SKILL.md 步驟 5 缺 WARN | ✅ 已補上狀態和說明 |
| 🔴4 | verify-excel-template.md PNG 偏移量 | ✅ 已改為 readUInt32BE(20) |
| 🟡5 | SKILL.md MPC 拼字 | ✅ 已全部改為 MCP |
| 🟡6 | SKILL.md 10.Excel 標題 | ✅ 已改為 10.6 |

---

## 初次審查日期
2026-05-15

## 審查範圍
8 個檔案（6 新增 + 2 修改）

## 統計
| 類別 | 🔴 嚴重 | 🟡 建議 | 🟢 良好 |
|------|---------|---------|---------|
| 邏輯正確性 | 3 | 7 | 16 |
| 程式碼品質 | 0 | 8 | 9 |
| 腳本/完整性 | 1 | 9 | 18 |
| **合計** | **4** | **24** | **43** |

---

## 🔴 嚴重問題

### [1] verify-i18n.md product_id 來源路徑錯誤
- **檔案**：references/verify-i18n.md:37
- **Reviewer**：Logic
- **問題**：寫「`.spec/{slug}/README.md` 有 `product_id` 時」，但 product_id 的權威來源是 `projects/{repo-id}.md`，與 SKILL.md 和 plan-common.md 矛盾
- **建議**：改為「`projects/{repo-id}.md` 有 `product_id` 時」

### [2] verify-excel-template.md 呼叫參數不一致
- **檔案**：references/verify-excel-template.md:14
- **Reviewer**：Logic
- **問題**：缺少 `--evidence` 參數，`--cover` 格式為純字串而非 JSON，與 SKILL.md:890-895 不一致
- **建議**：補上 `--evidence {dir}` 參數，`--cover` 改為 JSON 格式

### [3] SKILL.md 步驟 5 記錄結果缺少 WARN 狀態
- **檔案**：skills/plan-verify/SKILL.md:400-414
- **Reviewer**：Logic
- **問題**：記錄結果的狀態列表只有 PASS/FAIL/SKIP/MANUAL 四種，缺少 WARN。但 verify.md 統計區和 spec.md 都有定義 WARN
- **建議**：在狀態列表補上 `WARN: 通過但有疑慮（環境差異、selector 不穩定）`

### [4] verify-excel-template.md PNG height 偏移量錯誤
- **檔案**：references/verify-excel-template.md:148
- **Reviewer**：Perf
- **問題**：規格寫偏移量 18，但 PNG 規範和實際程式碼都是偏移量 20。規格文件有誤（程式碼正確）
- **建議**：修正偏移量為 `readUInt32BE(20)`

---

## 🟡 改善建議（重點項目）

### [5] SKILL.md `MPC` 拼字錯誤（2 處）
- **檔案**：skills/plan-verify/SKILL.md:235, 981
- **建議**：`MPC 模式` → `MCP 模式`

### [6] SKILL.md 10.Excel 標題序號不一致
- **檔案**：skills/plan-verify/SKILL.md:881
- **建議**：`10.Excel` → `10.6` 保持與 10.1~10.5 風格一致

### [7] SKILL.md --excel 獨立使用時封面資訊流程不明
- **檔案**：skills/plan-verify/SKILL.md:898
- **建議**：明確寫出「若未經 10.1，先執行封面資訊收集」

### [8] SKILL.md 步驟 1.5 與 2.5 重複載入 Layer 3 記憶
- **檔案**：skills/plan-verify/SKILL.md:108 vs 127-128
- **建議**：步驟 1.5 只載入產品知識庫，Layer 3 記憶統一收歸步驟 2.5

### [9] SKILL.md --from-e2e 只列在使用方式，無流程說明
- **檔案**：skills/plan-verify/SKILL.md:26
- **建議**：補充流程段落或標注「Phase 3 規劃中」

### [10] verify-excel-generator.js CLI 參數缺少越界檢查
- **檔案**：references/verify-excel-generator.js:62-86
- **建議**：每個 case 加入 `i + 1 >= args.length` 的越界檢查

### [11] verify-excel-generator.js 非 PNG 圖片 extension 硬編碼
- **檔案**：references/verify-excel-generator.js:719
- **建議**：根據副檔名判斷 extension（jpg → jpeg）

### [12] verify-excel-generator.js 行高單位 px vs pt 不一致
- **檔案**：references/verify-excel-generator.js:737-740
- **建議**：ExcelJS height 單位是 points，需做 px→pt 轉換（×0.75）

### [13] verify-excel-generator.js Cookie 短值遮罩不完整
- **檔案**：references/verify-excel-generator.js:368
- **建議**：Cookie 值 ≤ 8 字元時不匹配，需額外處理

### [14] verify-excel-generator.js X-Token/X-Access-Token 遮罩缺失
- **檔案**：references/verify-excel-generator.js:374
- **建議**：新增 `X-(?:Access-)?Token` regex

### [15] verify-excel-generator.js 二進位 evidence 檔案處理
- **檔案**：references/verify-excel-generator.js:787
- **建議**：.bin 副檔名跳過 UTF-8 讀取，顯示提示訊息

### [16] SKILL.md ExcelJS 安裝方式不正確
- **檔案**：skills/plan-verify/SKILL.md:887-888
- **建議**：`npx --yes exceljs` 無效（exceljs 無 bin entry），改用 `npm install --prefix $(mktemp -d) exceljs` + `NODE_PATH`

### [17] plan-common.md 第 4 層段落位置不理想
- **檔案**：references/plan-common.md:208
- **建議**：移到「讀取專案上下文」段落（第 22 行）之後，與第 2、3 層邏輯保持位置一致

---

## 🟢 良好實踐

- 步驟銜接順暢，1.5/2.5/5.5/9.5 與現有步驟無衝突
- 三層記憶架構設計合理，載入順序正確，升級邏輯清晰
- 產品模式 vs 通用模式分流清晰，降級處理完整
- SKILL.md 所有引用的 reference 路徑正確，無孤立文件
- verify-excel-generator.js 核心功能實作正確（verify.md 解析、截圖嵌入、狀態色彩）
- PNG 尺寸讀取偏移量正確（程式碼是對的，只是規格文件寫錯）
- ExcelJS API 使用正確（addImage、mergeCells、凍結窗格）
- 完整的錯誤處理（ExcelJS 不可用、verify.md 不存在、截圖缺失、輸出目錄不存在）
- Node.js 相容性好（CommonJS、基礎 API、無高版本依賴）
- smartrobot.md i18n 對照表 35 個關鍵字涵蓋主要操作場景
- CKEditor / SweetAlert2 / Flatpickr Recipe 與 E2ETest 實際模式吻合
- Spring Boot JPA API 回傳格式說明完整正確

## 交叉審查發現

- Logic Reviewer 和 Quality Reviewer 同時發現 `10.Excel` 命名問題 → 確認是真正的風格不一致
- Quality Reviewer 發現的 `MPC` 拼字錯誤在 Logic Reviewer 的流程審查中也有影響（讀者可能混淆 MPC 和 MCP）
- Perf Reviewer 發現的 PNG 偏移量問題只影響規格文件，程式碼本身正確 → 規格修正優先級低於程式碼修正
- Logic Reviewer 的 verify-i18n.md 路徑錯誤（[1]）和 Quality Reviewer 的風格審查互相佐證 → 同一處文字同時有邏輯錯誤和措辭問題
