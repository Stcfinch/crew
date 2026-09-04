---
name: crew-upgrade
description: 更新已安裝的 CREW Codex plugin；適用使用者明確要求升級 CREW。
---

# crew-upgrade

先讀 [Codex 執行契約](../../codex/references/runtime.md)，確認專案根目錄、工具路徑與既有授權。使用者指示優先於本技能。

先找到使用者的 CREW 原始碼 checkout 與安裝來源，確認 `git status`、remote 和目前 branch。
只在來源乾淨且追蹤分支已確認時使用 fast-forward 更新；來源有改動則保留並解釋。
從 checkout 執行 `python scripts/install-codex.py --update`；此程式建立備份和版本快取識別，再重新安裝 personal marketplace 的 crew。
若是其他 marketplace，依實際來源的 Codex 更新指令操作，不覆蓋成 personal。
顯示 CHANGELOG 的實際差异，成功後提示開啟新 Codex 任務載入新版。
