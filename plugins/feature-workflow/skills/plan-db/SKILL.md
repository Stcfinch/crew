---
name: plan-db
description: 產出資料庫設計文件寫入 .spec/ 目錄（零 Notion 呼叫）。當使用者提到 /plan-db、「產出 DB 設計文件」、「.spec 資料庫設計」時觸發此 Skill。
---

# plan-db — 資料庫設計（零 Notion 呼叫）

讀取技術規格，啟動 Agent 產出資料庫表結構設計與 SQL 檔案。

---

## 前置條件

> **前置檢查**：參照 plugin 根目錄 `references/prerequisites.md`（相對 SKILL.md 為 `../../references/`）檢查 CLAUDE.md 是否存在。

- 適用類型：**Feature**
- 前置檔案：`spec.md`（建議但非必要，若不存在則從 README.md 需求描述直接設計）

---

## 流程

### 1. 定位活躍任務 + 讀取專案上下文

參照 plugin 根目錄 `references/plan-common.md`（相對 SKILL.md 為 `../../references/`）。

### 2. 產出 DB 設計

使用 **Agent tool** 啟動 subagent（model: opus），prompt 指示如下：

**輸入來源**：
- 技術規格從 `.spec/{slug}/spec.md` 讀取
- 若 spec.md 不存在，提示建議先執行 `/plan-spec`，但允許從 README.md 需求描述直接設計

**輸出目標**：
- 設計文件 → `.spec/{slug}/db.md`
- SQL 檔案 → `.spec/{slug}/db.sql`（含 CREATE TABLE / INDEX / 範例資料 / Rollback SQL）

完成後更新 README.md 的 `status: DB 設計`。

### 3. 一致性驗證 + 更新日誌

參照 plugin 根目錄 `references/plan-common.md`（相對 SKILL.md 為 `../../references/`）。

### 4. 產出 deploy-checklist.md（僅本地）

完成 DB 設計後，自動從 `.spec/{slug}/db.sql` 擷取上線必做項目，寫入 `.spec/{slug}/deploy-checklist.md`。

#### 4a. 擷取 SQL 項目

從 `db.sql` 中擷取 DDL/DML 語句，依照 plugin 根目錄 `references/plan-common.md`（相對 SKILL.md 為 `../../references/`）的「deploy-checklist.md 格式規範 > SQL 擷取規則」處理。

每個項目格式：`- [ ] \`{SQL 類型} {表名/索引名}\` — {說明}`

#### 4b. 建立 deploy-checklist.md

依照 plugin 根目錄 `references/plan-common.md`（相對 SKILL.md 為 `../../references/`）的「deploy-checklist.md 格式規範」建立檔案。SQL 遷移區段填入擷取結果，設定檔變更區段留空（待 plan-build 填入）。

#### 4c. db.sql 不存在時

若 `db.sql` 不存在但 `db.md` 中描述了表結構：
- 仍建立 deploy-checklist.md
- SQL 遷移區段填入「請依 db.md 手動建立 SQL 並執行」提示

若 `db.md` 描述為「無 DB 變更」→ 不建立 deploy-checklist.md。

### 5. 回傳結果

```
DB 設計完成！

📁 產出檔案：.spec/{slug}/db.md, .spec/{slug}/db.sql
📋 上線前置作業：.spec/{slug}/deploy-checklist.md（{N} 個 SQL 項目）
📊 狀態：DB 設計
💡 提示：可用 /plan-sync 同步到 Notion，或等 /plan-close 結案時統一同步

後續可使用：
  • /plan-arch  — 架構設計
  • /plan-build — Agent Teams 產生程式碼
```

若未建立 deploy-checklist.md（無 DB 變更），「📋 上線前置作業」和「💡 提示」行不顯示。

---

## 何時不用

- 建立 / 執行 migration 檔（Flyway / Liquibase）→ 改用個人 `java-migration-helper` skill
- 查詢 / 索引 / 連線池效能優化 → 改用個人 `db-optimization-review` skill
- 需要完整規劃（技術規格＋DB 設計＋架構設計一次到位）→ 改用 `/plan`
- 只需要技術規格，不需 DB 設計 → 改用 `/plan-spec`
