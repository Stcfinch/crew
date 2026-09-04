---
name: bug-update
description: 更新 CREW Bug 調查證據，或重新開啟已結案 Bug。
---

# bug-update

先讀 [Codex 執行契約](../../codex/references/runtime.md)，確認專案根目錄、工具路徑與既有授權。使用者指示優先於本技能。

定位 task；在 plan.md 的決策/風險章節追加新的證據與結論，不覆蓋歷史判斷。
單純 log/SQL 更新不代表根因已確認。
`reopen`：保留原 task、page ID、歷史與部署紀錄，將 close/spec/build/security/verify/review 重設 pending；清空 work_unit，並將舊 review/security/verify result 狀態標為 STALE，critical 重設 0。
明確標註先前驗證已失效，重新調查後才能再結案。
Notion 同步僅在使用者要求的範圍進行；工具失敗保留本機更新。

