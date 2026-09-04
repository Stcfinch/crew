---
name: bug-setup
description: 設定 CREW Bug 工作流的本機環境或 Notion 任務庫、Bug 知識庫。
---

# bug-setup

先讀 [Codex 執行契約](../../codex/references/runtime.md)，確認專案根目錄、工具路徑與既有授權。使用者指示優先於本技能。

執行 `crew-project.py init --project <root>`，保留現有 config。
本機模式即可開始 Bug 調查。
需要 Notion 時讀 [Notion 整合](../../codex/references/notion.md)，確認 task、project、bug_knowledge 的 ID、schema 與權限。
完成後以 `crew-project.py doctor` 回驗，明確區分本機可用與 Notion 可用。
