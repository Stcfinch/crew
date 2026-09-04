---
name: plan
description: 執行 CREW 功能規劃的 spec、db、arch 三階段，產出單一 plan.md 與必要 deploy.sql。
---

# plan

先讀 [Codex 執行契約](../../codex/references/runtime.md)，確認專案根目錄、工具路徑與既有授權。使用者指示優先於本技能。

讀 [規劃契約](../../codex/references/planning.md)。
`spec` 明確化目標、範圍與可觀察驗收條件；`db` 檢查資料影響與遷移/回滾，SQL 只寫 deploy.sql；`arch` 記錄現有程式整合方式與有理由的設計決策。
帶參數只做指定 pass，否則依 spec → db → arch 執行。
寫入前先讀最新文件並局部修改，保留其他章節與使用者決策。
每個完成 pass 用 state set <step> done；不需 DB 時標 skipped 並記錄理由。
未解決且會影響實作的決策放進 unit ambiguity，不假裝已完成。
規劃本身不等於授權執行正式資料庫 SQL。
