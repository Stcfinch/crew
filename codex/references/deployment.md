# 部署紀錄

deploy.sql 使用穩定的編號，例如 -- Step 1: 建立索引，包含必要前置查核與回滾。
部署狀態和計畫完成是不同概念；只有 DBA/使用者提供的實際結果可標成功。

每個環境的證據記錄在 .spec/<slug>/deployment.md，按環境與 Step 保存：
時間、執行人提供的識別、結果、證據及失敗/回滾說明（不含認證資訊）。
保留每次紀錄，不覆蓋舊環境。
state.deploy 的 steps_total/steps_confirmed 是最近明確回報環境的摘要；
原 schema 沒有 per-environment 結構，因此必須同步在 deployment.md 標記摘要對應的環境。
不能將不同環境完成數相加。deploy-confirmed 不得大於 deploy-total。

收到 --all-done 但没有執行回報，先詢問是否已在該環境全部執行成功。
Notion 部署狀態依實際欄位映射更新，寫入後回讀；
失敗留待同步摘要，保持本機證據。
