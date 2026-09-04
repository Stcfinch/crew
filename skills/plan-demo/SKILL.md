---
name: plan-demo
description: 建立不依賴 Notion 的 CREW 功能規劃示範，便於評估套件。
---

# plan-demo

先讀 [Codex 執行契約](../../codex/references/runtime.md)，確認專案根目錄、工具路徑與既有授權。使用者指示優先於本技能。

執行 `crew-project.py demo --project <root>`，建立唯一 demo-* 任務、六章節 plan.md 與真實狀態檔。
如使用者提供題目，局部改寫目標、驗收與示範決策，清楚標註尚未實作。
呼叫 state next 顯示下一步；不要將示範文件當作已驗證程式。
demo 不建立 Notion 頁面、不切分支、不修改產品程式碼；沒有 Git commit 的專案明確說明 drift 檢查限制。
