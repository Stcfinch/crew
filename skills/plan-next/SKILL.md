---
name: plan-next
description: 根據 CREW state.json 推薦下一步或續接中斷工作。
---

# plan-next

先讀 [Codex 執行契約](../../codex/references/runtime.md)，確認專案根目錄、工具路徑與既有授權。使用者指示優先於本技能。

有 slug 時執行 state next --slug <slug> --project <root>。
`--all` 或無法唯一定位時用 state list，不擅自選擇第一個任務。
輸出工具計算的 command、reason 和證據缺口；inferred 狀態需標明。
使用者只詢問下一步時不執行該步；已要求繼續工作時讀對應 skill 並續做。
