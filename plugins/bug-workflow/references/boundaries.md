# Bug Workflow 動作邊界

## bug-investigate

### 🟢 ALWAYS
- 收集證據（log、git、環境）
- 搜尋 Bug 知識庫和本地學習
- 比對已知 bug 模式
- 每個假說都記錄驗證過程到 Notion
- 假說否定時記錄原因

### 🟡 ASK FIRST
- 3-Strike 後是否繼續調查
- 需要在測試/正式環境執行查詢時
- 需要讀取敏感設定檔時

### 🔴 NEVER
- 修改程式碼（investigate 只讀取和查詢）
- 在沒有證據的情況下確認根因
- 跳過 Phase 2 模式比對
- 忽略知識庫中的相關歷史

---

## bug-fix

### 🟢 ALWAYS
- 檢查根因分析是否已填寫（鐵律）
- 遵循最小 diff 原則
- 修復後執行編譯檢查
- 產出迴歸測試

### 🟡 ASK FIRST
- 修改超過 5 個檔案時
- 迴歸測試無法自動產出時
- 需要 gstack browse 進行 UI 驗證時

### 🔴 NEVER
- 在根因分析空白時開始修復
- 修復時順便重構旁邊的程式碼
- 跳過編譯檢查
- 產出 workaround 代替根因修復

---

## bug-close

### 🟢 ALWAYS
- 執行退出驗證門檻
- 擷取 git diff 填入 Notion
- 同步知識庫（若已設定）
- 嘗試捕捉學習

### 🟡 ASK FIRST
- 退出驗證有 WARN 項目時的處理
- commit 範圍的選擇（非預設 HEAD~1）
- 根因分類的自動推斷結果

### 🔴 NEVER
- 退出驗證有 BLOCK 項目時強行結案
- 覆蓋使用者手動填寫的 Notion 內容
- 在「根因分析」空白時結案為「已完成」（只能「測試中」）

---

## bug-update

### 🟢 ALWAYS
- 每次更新附加時間戳
- 附加而非覆蓋（先 fetch 再合併）
- 自動判斷更新區塊

### 🟡 ASK FIRST
- 無法自動判斷更新區塊時
- 使用者輸入超過 200 行時的截斷策略

### 🔴 NEVER
- 覆蓋已有的調查記錄
- Reopen 時刪除原有的修復方案

---

## crew-init

### 🟢 ALWAYS
- 依序檢查四階段（bug-workflow 設定 / feature-workflow 設定 / CLAUDE.md / 專案註冊）的設定檔是否存在
- 每階段結束後才進下一階段，不可跳過偵測直接假設已完成
- 失敗或中斷時提示 `/crew-init --resume` 續跑方式

### 🟡 ASK FIRST
- `/bug-setup`、`/plan-setup` 中需要使用者互動的部分（選資料庫、確認 ID）
- 使用者選擇跳過某階段（顯示 `s` 選項）時
- CLAUDE.md 或專案已存在但內容疑似不完整時，是否仍視為該階段完成

### 🔴 NEVER
- 自行修改 `/bug-setup`、`/plan-setup` 產出的設定檔內容
- 略過某階段的偵測就把該階段標示為 ✅ 完成
- 嘗試清理或回滾 `/bug-setup`、`/plan-setup` 中斷後留下的半成品設定檔
