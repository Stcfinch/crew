---
name: plan-setup
description: 設定 CREW 功能開發工作流與選用 Notion 功能設計庫。
---

# plan-setup

先讀 [Codex 執行契約](../../codex/references/runtime.md)，確認專案根目錄、工具路徑與既有授權。使用者指示優先於本技能。

執行 `crew-project.py init --project <root>`。
共用同一份 .crew/config.json，不建立另一套 Bug/Feature 設定。
需要 Notion 時讀 [Notion 整合](../../codex/references/notion.md)，沿用已確認的 task/project 映射並設定 feature_knowledge。
技術棧從實際專案偵測；必要時呼叫 `$plan-stack`，不安裝模型或其他 agent 設定。
