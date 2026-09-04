---
name: plan-deploy-confirm
description: 記錄使用者或 DBA 回報的 CREW SQL 部署進度，支援 env、list 與 all-done。
---

# plan-deploy-confirm

先讀 [Codex 執行契約](../../codex/references/runtime.md)，確認專案根目錄、工具路徑與既有授權。使用者指示優先於本技能。

讀 [部署紀錄](../../codex/references/deployment.md) 和 deploy.sql 的實際 Step。
`--list` 只列執行狀態；`--env` 選擇環境，未指定且有多環境時確認目標。
依使用者/DBA 明確提供的 Step 與結果寫入部署紀錄，不把產出 SQL 或點選確認視為已執行。
`--all-done` 僅在使用者回報目標環境全部執行成功時套用。
本入口只記錄執行結果；執行 SQL 是另一項需要相應授權的工作。
Notion 更新需回讀確認；遠端失敗保留本機部署證據。

