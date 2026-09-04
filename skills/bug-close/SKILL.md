---
name: bug-close
description: 確認 Bug 修復與迴歸驗證後結案，選用同步 Notion Bug 知識庫。
---

# bug-close

先讀 [Codex 執行契約](../../codex/references/runtime.md)，確認專案根目錄、工具路徑與既有授權。使用者指示優先於本技能。

讀 [結案契約](../../codex/references/closure.md)。
另外確認原始重現已解除、根因與修復有對應證據、影響範圍與迴歸結果已記錄。
若使用者要求同步，讀 [Notion 整合](../../codex/references/notion.md)，更新 task 與 bug_knowledge，回讀後保存 synced-now。
Git 操作依既有授權執行；失敗保留斷點且不可宣稱 merge/push 成功。
完整完成才 set close done；保留紀錄以供 bug-update reopen。

