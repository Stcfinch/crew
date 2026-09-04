---
name: plan-build
description: 依 CREW plan.md 實作功能並維護可續接的工作單元；支援 dry-run 與 resume。
---

# plan-build

先讀 [Codex 執行契約](../../codex/references/runtime.md)，確認專案根目錄、工具路徑與既有授權。使用者指示優先於本技能。

讀 plan/state、.crew/stack.md（若存在）以及相關現有實作。
確認 spec/db/arch 已完成或有明確 skipped 理由；根據任務規模拆成可驗證的工作單元。
`--dry-run` 只回報實作順序、預期檔案與測試方式，不修改程式碼或 state。
一般模式逐單元實作並以 unit 立即記錄進度；`--resume` 先回驗已完成單元，不重做也不盲信狀態。
保留原本 UI/架構慣例，SQL 寫 deploy.sql；檢查建置與與變更直接相關的測試。
本技能不要求建立多代理團隊；僅在使用者或既有專案指示要求且 host 支援時，委派可獨立的工作，遵循 host 工具契約並繼承模型。
程式改動後把舊 security/verify/review 步驟改 pending、result 改 STALE 並將 critical 重設 0；最後 set build done，清空 work_unit。

