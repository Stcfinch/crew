---
name: bug-investigate
description: 調查 CREW Bug 的重現條件與根因，以假說和證據定位問題。
---

# bug-investigate

先讀 [Codex 執行契約](../../codex/references/runtime.md)，確認專案根目錄、工具路徑與既有授權。使用者指示優先於本技能。

若尚無 task，先依 bug-start 建立本機紀錄；已有 slug 則讀 plan/state，續接未完成的假說。
读 [Bug 調查](../../codex/references/bugs.md)。蒐集重現輸入、log 和相關程式碼，列出可被推翻的假說，一次驗證一個。
調查期間不混入修復；以精確檔案/符號、輸入與觀察證據連接根因。
三次失敗的同類假說後重新檢視問題模型，避免重複猜測。
根因已證實且修復驗收條件清楚時，state set spec done；否則保持 in_progress 並用 unit 保存證據、剩餘項目與歧義。
將 schema 或架構影響記入決策紀錄；需要獨立設計時將 db/arch 改為 pending。

