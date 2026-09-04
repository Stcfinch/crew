---
name: plan-review
description: 審查 CREW 任務的程式邏輯、品質與效能；支援 quick 範圍審查。
---

# plan-review

先讀 [Codex 執行契約](../../codex/references/runtime.md)，確認專案根目錄、工具路徑與既有授權。使用者指示優先於本技能。

讀 [驗證與審查](../../codex/references/verification.md)，確認 diff 基底與任務範圍。
按邏輯/相容性、品質/可維護性、效能/資源三個角度審查；`--quick` 聚焦當前改動的高風險處。
執行 drift 檢查並回報結果，引用實際路徑/行號和能觸發問題的輸入。
以一位 agent 即可完成三個角度；不宣稱獨立審查或並行團隊，除非真的使用且已有委派授權。
state result review 保存 status、critical、warnings，set review done/failed；plan.md 保存一行摘要。
