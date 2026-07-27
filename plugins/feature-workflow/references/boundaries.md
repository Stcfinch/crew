# 動作邊界參考

## plan-build

### 🟢 ALWAYS（自動執行，不詢問）
- 讀取 .spec/{slug}/ 下所有設計文件
- 載入技術棧定義和掃描規則
- 掃描現有程式碼範本
- 產出 files.md
- 執行退出驗證門檻
- 在 log.md 記錄執行結果

### 🟡 ASK FIRST（顯示計畫，等使用者確認）
- 啟動 Agent Teams（步驟 4 的確認提示；探索官 `model: sonnet`、實作者 `model: opus`）
- Teammate 失敗時的處理策略（重試 / 跳過 / 終止）
- API 契約不一致時的調整方向
- 退出驗證中 WARN 項目的處理

### 🔴 NEVER（禁止，即使使用者要求也應警告）
- Leader 自己寫應用程式碼
- 跳過 arch.md 不存在的 hard block
- 自動產出 arch.md 來繞過 hard block
- 修改其他任務（非當前 slug）的 .spec/ 文件
- 跳過退出驗證中的 BLOCK 項目

---

## plan-review

### 🟢 ALWAYS
- 從 files.md 或 git diff 收集審查範圍
- 讀取 .spec/ 設計文件作為審查基準
- 產出 review.md
- 執行交叉審查合併步驟

### 🟡 ASK FIRST
- 3 人完整審查（預設）vs --quick 單人審查
- 發現 🔴 嚴重問題後的處理策略

### 🔴 NEVER
- 跳過合併步驟
- 自動降級嚴重度（🔴 → 🟡）
- Reviewer 之間互相呼叫

---

## plan-verify

### 🟢 ALWAYS
- 連接 Chrome 前確認模式（MCP / Bash / api-only）
- 每條驗收條件都記錄結果（PASS / FAIL / SKIP / MANUAL）
- 收集截圖到 .spec/{slug}/screenshots/
- 產出 verify.md

### 🟡 ASK FIRST
- 第一次連接 Chrome（確認目標分頁）
- --manual 模式的每步驟確認
- FAIL 項目是否需要立即修正

### 🔴 NEVER
- 跳過 FAIL 項目不記錄
- 自動將 FAIL 標記為 SKIP
- 未驗證回應 body 就標記 PASS

---

## plan-security

### 🟢 ALWAYS
- 執行 Layer 1 靜態規則掃描
- 掃描 MyBatis ${} 使用
- 掃描硬編碼密碼/Token
- 檢查 Controller 參數驗證

### 🟡 ASK FIRST
- 發現 🔴 嚴重漏洞時是否立即修復
- 外部依賴 CVE 掃描結果（可能有 false positive）
- 需要新增安全 middleware 或 filter

### 🔴 NEVER
- 忽略 SQL Injection 發現（「只是內部 API」）
- 降級安全問題嚴重度
- 跳過 Layer 1 靜態掃描

---

## plan-demo

### 🟢 ALWAYS
- 產出目錄一律加 `demo-` 前綴，避免污染真實 `.spec/`
- README.md 標記 `demo: true`
- 全程本地寫入，不呼叫 Notion / Agent Teams / DB MCP

### 🟡 ASK FIRST
- `.spec/demo-{slug}/` 已存在時是否覆寫
- 使用者指定的題目過於複雜時，是否仍用簡化範本產出

### 🔴 NEVER
- 寫入 Notion 或觸發 Notion OAuth
- 啟動 Agent Teams 或連線 DB MCP
- 建立 Git branch

---

## plan-deploy-confirm

### 🟢 ALWAYS
- 逐筆列出 deploy.sql 的每個 Step 供確認
- 記錄執行時間、環境（dev/staging/prod）、執行者
- 確認後寫回 Notion「🚀 部署狀態」區塊

### 🟡 ASK FIRST
- 環境未指定時（未帶 `--env`）
- 部分 Step 執行失敗時的後續處理

### 🔴 NEVER
- 略過任一 Step 的確認直接標記全部完成（除非明確帶 `--all-done`）
- 覆蓋既有的部署狀態記錄而非附加
- 在沒有 deploy.sql 或未執行過 `/plan-close` 的任務上執行回報

---

## plan-next

### 🟢 ALWAYS
- 讀取 `.spec/{slug}/` 既有檔案清單、Git 狀態、verify.md 結果來判斷流程位置
- 給出具體的下一個指令與推薦理由
- 多個活躍任務時列出讓使用者選擇，或用 `--all` 全部列出

### 🟡 ASK FIRST
- 偵測到流程位置矛盾時（例如 verify.md 存在但 arch.md 缺）如何處理

### 🔴 NEVER
- 未經偵測就推薦固定指令
- 略過 Git 狀態只看檔案是否存在
