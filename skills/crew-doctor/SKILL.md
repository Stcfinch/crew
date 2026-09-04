---
name: crew-doctor
description: 檢查 CREW 的 Python、Git、設定與任務狀態；用於環境健診或工作流故障排查。
---

# crew-doctor

先讀 [Codex 執行契約](../../codex/references/runtime.md)，確認專案根目錄、工具路徑與既有授權。使用者指示優先於本技能。

執行 `crew-project.py doctor --project <root>`，以實際輸出報告成功、警告與失敗。
`--quick` 僅做上述本機檢查；完整檢查再對每個 task 跑 state validate，並檢查目前可呼叫的 Notion、瀏覽器、報告技能。
未連接服務標為 unavailable；不可把工具名稱存在當成帳號或資料庫可達。
`--fix` 只修已診斷的本機設定問題；保留使用者原值。缺乏外部授權時仍完成其他檢查。

