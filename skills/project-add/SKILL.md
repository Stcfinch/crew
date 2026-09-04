---
name: project-add
description: 偵測專案技術棧、建置方式與 Git remote，選用註冊至 Notion 專案庫。
---

# project-add

先讀 [Codex 執行契約](../../codex/references/runtime.md)，確認專案根目錄、工具路徑與既有授權。使用者指示優先於本技能。

讀取建置檔、服務入口、既有開發文件與 Git remote。
將不含認證資訊的專案識別、建置/測試指令、架構摘要寫入 .crew/project.md；設定以 [執行契約](../../codex/references/runtime.md) 為準。
技術棧不限定 Java；遵循現有分層與資料存取方式。
使用者要求 Notion 註冊時讀 [Notion 整合](../../codex/references/notion.md)，依正規化的 host/owner/repo 去重後建立/更新正確 project，回讀確認。
DB 連線整合只在任務需要時設定，不將密碼寫入文件或版本控制。
