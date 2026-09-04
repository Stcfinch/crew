# 結案契約

先執行 crew-project.py close-check --slug <slug> --project <root>。
它要求 plan.md 存在、state schema 正確、所有前置步驟 done/skipped、
無未解決 FAIL/critical、且 drift 檢查可完成。
WARN 必須逐項呈現，只有已獲使用者接受時才帶 --allow-warnings。
不要修改 drift_policy 或更換 verified_at_commit 來隱藏尚未檢查的問題。
檢查通過並不代表 Git/Notion 已完成；此指令不執行那些外部動作，也不標記 close done。

檢視真實 Git diff 和未追蹤檔，確認本任務修改範圍與 repo 要求的驗證。
不以未通過 gate 的狀態宣稱任務完成。需要執行的 merge/commit/push 或同步，
按使用者既有授權操作；結果含糊時回讀確認再決定重試。

若是 local 模式，且使用者未要求外部同步，Notion 不作為結案前置條件。
若使用者已要求外部動作卻失敗，記入 unit remaining，保留未完成。
部署 SQL 可能在程式碼結案後由 DBA 執行；列出未部署狀態，不偽造執行結果。
完成所有要求後才 state set close done；保留任務資料供續查與 reopen。

