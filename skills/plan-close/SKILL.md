---
name: plan-close
description: 在驗收、審查和漂移檢查完成後結束 CREW 功能任務，按授權提交或同步。
---

# plan-close

先讀 [Codex 執行契約](../../codex/references/runtime.md)，確認專案根目錄、工具路徑與既有授權。使用者指示優先於本技能。

讀 [結案契約](../../codex/references/closure.md)，先完成其檢查。
需同步 Notion 時先依 [Notion 整合](../../codex/references/notion.md) 建立可回讀的摘要；同步成功才記錄 synced-now。
Git commit/merge/push 依使用者授權與 repo 工作方式完成；只包含本任務檔案，不以 git add . 把無關改動帶入。
有未完成外部動作且使用者要求時，保存 remaining，不標 close done。
已授權工作完成才 set close done，保留 state、plan、deploy.sql，輸出驗證結果與剩餘部署事項。
