---
name: plan-verify
description: 驗證 CREW 任務的驗收條件，支援瀏覽器、E2E 與選用 Word/Excel 報告。
---

# plan-verify

先讀 [Codex 執行契約](../../codex/references/runtime.md)，確認專案根目錄、工具路徑與既有授權。使用者指示優先於本技能。

讀 [驗證與審查](../../codex/references/verification.md)。
把每項驗收條件對應測試輸入、操作、預期、實際與證據；不能執行的項目標未驗證。
瀏覽器使用目前可用且允許的 browser 工具，遵守其指示，不假設 CDP/Chrome DevTools MCP 或改用其他方式繞過限制。
`--e2e` 使用專案 E2E runner；`--recheck` 聚焦失敗項與其影響範圍。
`--excel` 使用可用 spreadsheets 技能輸出報告；要求 Word 時使用 documents 技能；沒有相應能力則提供 Markdown，清楚說明未產出原格式。
產物放 .spec/<slug>/.cache/，plan.md 只留摘要及證據路徑。
全部驗證完成才 set verify done；result status 依實際輸出為 PASS/WARN/FAIL，不把缺少工具改為 PASS。

