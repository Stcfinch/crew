# 程式碼清單

## 新增檔案

| 檔案路徑 | 層級 | 說明 | 行數 |
|---------|------|------|------|
| `plugins/feature-workflow/references/verify-stability.md` | Reference | 截圖穩定化策略（from SmartRobotE2ETest global-hooks） | 93 |
| `plugins/feature-workflow/references/verify-i18n.md` | Reference | i18n 驗證指引（4 語系，產品/通用雙模式） | 165 |
| `plugins/feature-workflow/references/verify-excel-template.md` | Reference | Excel 報告規格定義（Sheet 結構、欄位、色彩） | 283 |
| `plugins/feature-workflow/references/verify-excel-generator.js` | Script | ExcelJS 獨立腳本（解析 verify.md → 產出 .xlsx） | 907 |
| `plugins/feature-workflow/products/smartrobot.md` | Product | SmartRobot 產品知識庫（導航地圖、Selector、i18n、Recipe） | 207 |
| `plugins/feature-workflow/products/smartrobot-memory.md` | Product | SmartRobot 產品級驗證記憶 Layer 3（初始模板） | 37 |

## 修改檔案

| 檔案路徑 | 修改說明 | 變更行數 |
|---------|---------|---------|
| `plugins/feature-workflow/skills/plan-verify/SKILL.md` | Phase 1+2+3 全部修改：截圖穩定化、元素 Fallback、WARN 狀態、Excel 報告、產品偵測、記憶系統、E2E Runner、測試骨架 | +161（821→982） |
| `plugins/feature-workflow/references/plan-common.md` | 新增第 4 層產品知識庫 + 第 4.1 層產品級記憶 + projects/{id}.md 新增選填欄位 | +25 |
