---
name: plan-start
description: 建立 CREW 功能任務、plan.md、流程狀態與工作分支。
---

# plan-start

先讀 [Codex 執行契約](../../codex/references/runtime.md)，確認專案根目錄、工具路徑與既有授權。使用者指示優先於本技能。

從需求建立唯一英文 slug，先讀 .spec 清單，避免重複任務。
執行 `crew-project.py start --type feature --slug <slug> --name <title> --project <root>`。
讀 [規劃契約](../../codex/references/planning.md) 補目標與可觀察的驗收条件。
檢查工作區、目前分支和使用者選定基底，再建立 feature/<slug> 或沿用已指定的工作分支；將真實 branch/base/commit 用 state set 記錄。
需要 Notion 時讀 [Notion 整合](../../codex/references/notion.md)，建立或關聯 task，回讀後才記錄 page ID。
不在 start 階段提前把規劃或實作標為完成。

