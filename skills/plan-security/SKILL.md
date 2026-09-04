---
name: plan-security
description: 針對 CREW 任務變更執行安全審查，記錄具體可驗證的發現。
---

# plan-security

先讀 [Codex 執行契約](../../codex/references/runtime.md)，確認專案根目錄、工具路徑與既有授權。使用者指示優先於本技能。

以實際 diff 和輸入邊界定位變更，检查認證授權、注入、敏感資訊、依賴與錯誤處理。
使用專案已有的掃描/測試工具；先確認指令可用再執行，避免把未掃描當作通過。
只回報可具體指向的風險、利用前提、影響與修法。
用 state result --kind security --status PASS|WARN|FAIL --set critical=<n> 保存结果，並更新 security 步驟 done/failed。
掃描範圍或環境不足時保留未完成狀態，報告局限。
