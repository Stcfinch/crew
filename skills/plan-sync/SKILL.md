---
name: plan-sync
description: 將 CREW 任務進度與規劃摘要同步至已設定的 Notion。
---

# plan-sync

先讀 [Codex 執行契約](../../codex/references/runtime.md)，確認專案根目錄、工具路徑與既有授權。使用者指示優先於本技能。

讀 [Notion 整合](../../codex/references/notion.md)。
以本機 plan/state 和真實 Git 狀態組成更新；先讀遠端 page/schema，辨識使用者手動修改。
優先更新由 CREW 管理的區段，不覆蓋整頁；使用 page ID 或穩定關聯識別避免重複建立。
外部寫入成功後回讀核對，才 state set --synced-now。
本機模式或缺權限時保留摘要到 .spec/<slug>/.cache/notion-sync.md，明確標為待同步，不能標記成功。
