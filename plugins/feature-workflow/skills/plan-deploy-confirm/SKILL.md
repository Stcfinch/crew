---
name: plan-deploy-confirm
description: 部署 SQL 執行回報 — DBA 或執行者在實際跑完 deploy.sql 後，用此指令勾選每筆執行狀態並寫回 Notion「🚀 部署狀態」區塊，補上 plan-close 後沒有的執行回流機制，避免 Notion 永遠顯示「未執行」。當使用者提到「plan-deploy-confirm」、「確認部署」、「SQL 執行回報」、「deploy 完成」、「DBA 確認」時觸發此 Skill。
---

# plan-deploy-confirm — 部署 SQL 執行回報

`/plan-close` 把 `deploy.sql` 寫進 Notion 後，DBA / 部署者實際執行需手動回報。
本指令提供標準化流程：列出待回報 SQL、互動確認、記錄執行時間/環境/執行者、寫回 Notion。

解決原本 deploy-checklist 機制「文件寫了沒人勾，永遠顯示『未執行』」的問題。

---

## 紀律護欄

> **執行前必讀**：`references/discipline-preamble.md`（通用紀律 — 反合理化、動作邊界、鐵律）。
> 本 skill 專用條目：`anti-rationalizations.md` 「plan-deploy-confirm 專用」+ `boundaries.md` 「plan-deploy-confirm」段落。
> 在感到「可以跳過」「應該夠了」的衝動時，**停下查表**確認是否為已知偏離模式。

---

## 使用方式

```
/plan-deploy-confirm                      # 互動選擇任務 + 逐筆確認
/plan-deploy-confirm <slug>               # 明確指定任務 slug
/plan-deploy-confirm <slug> --env prod    # 指定環境（dev/staging/prod，預設詢問）
/plan-deploy-confirm <slug> --all-done    # 所有 SQL 都確認執行成功（批次模式）
/plan-deploy-confirm --list               # 列出所有「待部署回報」任務
```

---

## 前置條件

- 任務必須已執行過 `/plan-close` 並產出 `deploy.sql`
- Notion 條目已存在且含「🚀 部署狀態」可寫入區塊（plan-close 會自動建立）
- 設定檔含「任務追蹤工具」資料庫 ID

---

## 流程

### 1. 定位待回報任務

兩種來源（合併去重）：

**本地**：掃 `.spec/*/` 含 `deploy.sql` 且 README.md 標示 `status: 已結案` 的任務。

**Notion**（更新鮮）：用 `notion-search` 搜尋同 Git Repo 下狀態為「已結案」、含「🚀 部署狀態」區塊但部署狀態為「待執行」的條目。

合併後呈現：

```
偵測到 {N} 個任務有待回報的 deploy.sql：

  1. user-management-api（feature） — 2 筆 SQL，已結案 3 天
  2. permission-refresh（feature） — 1 筆 SQL，已結案 1 天

請選擇任務編號（或輸入 slug）：
```

### 2. 讀取 deploy.sql

從 `.spec/{slug}/deploy.sql` 解析 SQL 區塊：

按註解 `-- Step N：{描述}` 切割，得到每個 Step 的：
- 序號
- 描述
- 實際 SQL 內容（DDL / DML）
- 驗證 SQL（若有 `驗證 SQL` 區塊）
- 回滾 SQL（若有 `回滾 SQL` 區塊，預設註解）

### 3. 互動確認每筆執行狀態

對每個 Step 詢問：

```
═══════════════════════════════════════════
🗄️  Step 1：建立 users 表
═══════════════════════════════════════════

SQL：
  CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(100) UNIQUE NOT NULL,
    ...
  );

執行狀態？
  [1] ✅ 成功執行
  [2] ⚠️  執行成功但有警告（如索引建立慢、警告訊息）
  [3] ❌ 執行失敗（需附原因）
  [4] ⏭️  暫時跳過（之後再確認）

選擇：
```

**選 1**：直接記錄成功 + 詢問執行時間（預設「剛剛」/ 「{datetime}」/ 手動輸入）
**選 2**：記錄成功但附警告訊息
**選 3**：要求填入失敗原因（5-200 字），不視為完成
**選 4**：保留此 Step 為「待確認」，繼續下一筆

### 4. 收集執行環境資訊

完成所有 Step 後（或 `--all-done` 模式）詢問：

```
執行環境？
  [1] dev
  [2] staging
  [3] prod
  [4] 其他（請輸入）

執行者？（預設取 OS 使用者：{whoami}）

備註？（選填，描述任何需要記錄的情境）
```

`--env` 參數可預先指定環境，跳過此問。

### 5. 寫回 Notion「🚀 部署狀態」區塊

格式：

```markdown
## 🚀 部署狀態

### 最後執行：{YYYY-MM-DD HH:MM}（{執行者} @ {環境}）

| Step | 描述 | 狀態 | 執行時間 | 備註 |
|------|------|------|---------|------|
| 1 | 建立 users 表 | ✅ 成功 | 14:23 | — |
| 2 | 建立 email 唯一索引 | ⚠️ 警告 | 14:24 | 索引建立耗時 3 秒 |
| 3 | 插入預設管理員 | ⏭️ 待確認 | — | DBA 排程未到 |

### 執行紀錄

- 2026-05-23 14:25 @ prod by cheng — Step 1, 2 成功；Step 3 排程未到
- 2026-05-20 10:15 @ staging by cheng — 全部成功

### 備註
（使用者填入的備註）
```

每次執行 `/plan-deploy-confirm` 都**追加**到「執行紀錄」（不覆蓋）。表格保持最新狀態。

### 6. 寫回本地 `.spec/{slug}/deploy.sql` 註解

在 SQL 檔頂端追加（不修改 SQL 本體）：

```sql
-- ================================================================
-- 部署回報
-- 2026-05-23 14:25 @ prod by cheng
-- Step 1, 2 成功；Step 3 待確認
-- ================================================================

-- {原本的 deploy.sql 內容}
```

每次回報新增一段，舊紀錄保留。

### 7. 更新 .spec/ 與回傳

更新 `.spec/{slug}/log.md`：

```markdown
### [2026-05-23 14:25] 部署回報
- 環境：prod
- 執行者：cheng
- Step 結果：1 ✅ / 2 ⚠️ / 3 ⏭️
- Notion 已同步：🔗 {頁面連結}
```

回傳：

```
✅ 部署回報已寫回 Notion

📋 任務：user-management-api
🌍 環境：prod
👤 執行者：cheng
📊 結果：2 ✅ 成功、1 ⏭️ 待確認

🔗 Notion：{頁面連結}

{若有 ⏭️ 待確認項目}：
💡 提示：3 個 Step 標為「待確認」。執行後可再次 /plan-deploy-confirm 補回。

{若全部 ✅}：
🎉 所有 Step 都已確認執行成功，任務真正完成。
```

---

## `--list` 模式

不選任務、不互動，純列出待回報清單：

```
偵測到 {N} 個任務有待回報的 deploy.sql：

| slug | 結案天數 | SQL 數 | 待確認 | 已執行 |
|------|---------|--------|-------|-------|
| user-management-api | 3 天 | 3 | 1 | 2 |
| permission-refresh | 1 天 | 1 | 1 | 0 |

執行 /plan-deploy-confirm <slug> 開始回報。
```

---

## Notion 呼叫次數

| 操作 | 呼叫 |
|------|------|
| 搜尋待回報任務（步驟 1） | 1-2 次 |
| 讀取目標頁面（取得區塊 ID） | 1 次 |
| 更新「🚀 部署狀態」區塊 | 1-2 次 |
| 總計 | **3-5 次** |

---

## Gotchas

- **舊任務無「🚀 部署狀態」區塊**：plan-close 在加入此機制前已結案的任務沒有對應區塊。提示「需要先用 /plan-sync 重新同步補上區塊」
- **deploy.sql 格式不標準**：若 SQL 檔沒有 `-- Step N` 註解，無法精確分段。退回「整個 deploy.sql 作為單一 Step」處理
- **回滾 SQL 不在本指令範圍**：執行回滾請由 DBA 用對應的 SQL 客戶端執行，本指令只記錄回滾事件（如 `--rollback` 選項，未實作）
- **跨環境順序**：建議按 dev → staging → prod 順序部署，本指令不強制檢查順序，但回報紀錄會顯示時序，後審視可發現
- **多人同時回報**：兩個 DBA 同時 /plan-deploy-confirm 同一任務 → 後寫入覆蓋前者的「最後執行」摘要，但「執行紀錄」段落兩筆都會留下（追加模式）

---

## 邊界情況

- **任務未結案**（status ≠ 已結案）：提示「此任務尚未結案，是否仍要回報部署？」（少數情境如 hotfix 直接上線）
- **無 deploy.sql**：提示「此任務無 deploy.sql 需要回報，無需執行本指令」
- **使用者中斷**：已確認的 Step 寫入 Notion 不回滾；未確認的維持原狀，下次可繼續
- **--all-done 模式無法區分失敗**：明示「批次模式假設全部成功」，若有失敗請使用互動模式
- **Notion API 失敗**：本地 log.md 仍寫入，提示「Notion 未同步，明天可用 /plan-sync 補上」
