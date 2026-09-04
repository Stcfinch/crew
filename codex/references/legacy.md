# 舊版移轉

原 plugins/bug-workflow 和 plugins/feature-workflow 保留供原平台使用；
Codex 不自動載入其技能或讀其全域設定。
既有 schema_version=1 state.json 可以保留；Codex 版額外使用 $skill 語法顯示下一步。

移轉舊 spec.md/db.md/arch.md 任務時：
- 先確認 task slug、root、現有內容和備份目的地，在 task 內建立唯一時間戳 backup 目錄。
- 複製原始文件，逐檔 hash 驗證；不刪除或覆蓋原檔案。
- 建立六章節 plan.md，保留連往原文件的相對路徑；人為決策和驗收條件由原文確認後逐項移入。
- 不使用摘要憑空重建歷史決策；未確認項目明寫「待確認」。
- db.sql 與 deploy.sql 有衝突時先列差异，依使用者選擇合併，保留單一執行來源。
- 用 state rebuild 建立 inferred 狀態；檔案存在僅是推測，不代表驗收/審查成功。
- 回驗資料與實際 Git 歷史後才解除 inferred。狀態恢復和語意移轉分開報告。

