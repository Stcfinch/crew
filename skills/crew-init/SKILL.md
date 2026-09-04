---
name: crew-init
description: 初始化 CREW for Codex 專案；建立本機設定、檢查環境，或接續未完成設定。
---

# crew-init

先讀 [Codex 執行契約](../../codex/references/runtime.md)，確認專案根目錄、工具路徑與既有授權。使用者指示優先於本技能。

執行 `crew-project.py init --project <root>`，再執行 `doctor`。
預設 local 模式；有設定時保留原值，`--resume` 只補未完成項目。
讀取 AGENTS.md；若使用者需要專案說明而檔案不存在，依實際程式碼建立精簡 AGENTS.md。
若使用者要求 Notion，讀 [Notion 整合](../../codex/references/notion.md) 完成資料庫選擇與欄位映射，再以 `crew-project.py mode --value notion` 切換。
輸出設定位置、實測依賴狀態與 `$plan-demo` / `$plan-start` 用法。

