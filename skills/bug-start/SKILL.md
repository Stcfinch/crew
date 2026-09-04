---
name: bug-start
description: 建立 CREW Bug 任務與重現紀錄；尚不調查或修復程式碼。
---

# bug-start

先讀 [Codex 執行契約](../../codex/references/runtime.md)，確認專案根目錄、工具路徑與既有授權。使用者指示優先於本技能。

執行 `crew-project.py start --type bug --slug <slug> --name <title> --project <root>`。
在 plan.md 寫入預期/實際行為、環境、重現步驟與影響範圍；未知資訊標示未知。
初始 db/arch 為 skipped，設計影響歸入調查的 spec；發現 schema/架構變動再重新開啟該階段。
Notion 模式依 [Notion 整合](../../codex/references/notion.md) 去重並建立 task。
回報 slug 和 `$bug-investigate <slug>`。

