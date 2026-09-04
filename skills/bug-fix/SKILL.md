---
name: bug-fix
description: 依 CREW 已確認根因實作 Bug 修復，執行重現與迴歸驗證。
---

# bug-fix

先讀 [Codex 執行契約](../../codex/references/runtime.md)，確認專案根目錄、工具路徑與既有授權。使用者指示優先於本技能。

讀 [Bug 調查](../../codex/references/bugs.md) 與現有根因證據；不足時先完成調查。
檢查實際工作分支，保留使用者既有改動。
按根因做最小必要修復，執行原重現案例；適合時建立能在舊行為失敗、修復後通過的迴歸測試。
用 unit 隨每個完成的修復單元保存進度，依現有技術棧建置，更新指向程式碼的錨點。
有 DB/架構改動需完成其設計；修復完成後 set build done，但實際驗收與審查由對應 skills 完成。
修改程式碼後把先前 security/verify/review 步驟重設 pending，舊 result 標為 STALE 並將 critical 重設 0；不得沿用舊 PASS。

