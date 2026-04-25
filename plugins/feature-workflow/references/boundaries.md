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
- 啟動 Agent Teams（步驟 4 的確認提示）
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
