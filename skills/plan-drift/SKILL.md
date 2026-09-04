---
name: plan-drift
description: 檢查與修正 CREW plan.md 中失效的程式碼/SQL 錨點與過時決策。
---

# plan-drift

先讀 [Codex 執行契約](../../codex/references/runtime.md)，確認專案根目錄、工具路徑與既有授權。使用者指示優先於本技能。

執行 drift --spec <project>/.spec/<slug>/plan.md --root <project> --format json。
退出碼 0=通過、1=FAIL、2=WARN、3=環境問題；3 不可說成沒有漂移。
讀引用程式碼，確認決策仍正確；有修復需求時 `--fix` 只修可證實的檔案改名/行號移動。
符號消失或內容變更涉及語意，先查證並依使用者決策局部修改，不能只改錨點讓檢查變綠。
完整讀過受影響內容後才能更新 verified_at_commit 為實際 HEAD，再重跑檢查。
不靠 drift_policy off 或忽略記號掩蓋缺失。

