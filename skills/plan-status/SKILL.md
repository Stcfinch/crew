---
name: plan-status
description: 列出 CREW 任務與狀態，恢復中斷工作或檢查舊版任務。
---

# plan-status

先讀 [Codex 執行契約](../../codex/references/runtime.md)，確認專案根目錄、工具路徑與既有授權。使用者指示優先於本技能。

執行 state list --project <root>，`--all` 包含已結案任務。
讀 state 的輸出，不從檔案存在與否猜完成。
缺少或損壞 state 時先備份，經使用者修復需求用 rebuild 重建；輸出 inferred 狀態供確認。
舊版沒有 plan.md 的任務保留原文件；`--migrate` 依 [舊版移轉](../../codex/references/legacy.md) 處理，不做不可驗證的語意壓縮。
只列狀態時不寫檔。
