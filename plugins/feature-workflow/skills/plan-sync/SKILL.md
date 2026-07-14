---
name: plan-sync
description: 手動中途同步 .spec/ 目錄當前進度到 Notion（含 deploy.sql），按需使用、不在常規流程、任務尚未結案。當使用者提到 /plan-sync、「中途同步 spec 進度」、「同步 spec 進度到 Notion」時觸發此 Skill。
---

# plan-sync — 手動中途同步

將 `.spec/{slug}/` 目錄的當前進度同步到 Notion。用於需要在結案前查看 Notion 頁面、或與團隊成員分享進度的場景。**不在常規流程中**，按需使用。

---

## 設定目錄

依 plugin 根目錄 `references/config-resolver.md`（相對 SKILL.md 為 `../../references/`）的漸進式載入邏輯讀取設定。本 Skill 需要：
- **第 1 層**：`config.md`（Notion IDs）
- **第 2 層**：`projects/{repo-id}.md`（專案對應）

> **前置檢查**：參照 plugin 根目錄 `references/prerequisites.md`（相對 SKILL.md 為 `../../references/`）執行完整前置檢查（CLAUDE.md + 設定目錄 + 專案註冊）。

---

## 使用方式

```
/plan-sync                 # 同步當前任務的所有文件
/plan-sync spec            # 只同步 spec.md
/plan-sync db              # 只同步 db.md + db.sql
/plan-sync arch            # 只同步 arch.md
```

---

## 流程

### 1. 定位活躍任務

與 `/plan` 相同邏輯。讀取 `.spec/{slug}/README.md` 取得 `type` 和 `notion_page_id`。

### 2. 檢查 Notion 頁面

若 `notion_page_id` 為空（例如 `/plan-start` 時 Notion 建立失敗）：
- 詢問使用者是否要補建 Notion 條目
- 若是，執行與 `/plan-start` 的「建立 Notion 條目」步驟相同的建立邏輯
- 建立後更新 README.md 的 `notion_page_id` 和 `notion_url`

### 3. 確定同步範圍

掃描 `.spec/{slug}/` 目錄，列出可同步的檔案：

```
可同步的文件：
  ✅ spec.md → 📐 技術規格
  ✅ db.md   → 🗄️ 資料庫設計
  ❌ arch.md → 🏗️ 架構設計（不存在）
  ✅ deploy.sql → 🗄️ 資料庫設計 → 部署 SQL
  ✅ deploy-checklist.md → 🚀 上線前置作業
  ✅ review.md → 📋 程式碼審查

同步所有？[Y/n] 或輸入要同步的項目（如 spec db）
```

若使用者指定了子命令（如 `/plan-sync spec`），只同步指定項目。

### 4. 執行同步

**4-1. Fetch 現有頁面**（1 次 `notion-fetch`）

取得頁面現有內容，避免覆蓋其他區塊。

**4-2. 更新內容**（1 次 `notion-update-page` content）

將選定的本地文件內容寫入對應 Notion 區塊。對應關係依 plugin 根目錄 `references/plan-common.md`（相對 SKILL.md 為 `../../references/`）「本地檔案 ↔ Notion 區塊對應表」；本 skill 只同步使用者選定的項目，且不建立「🚀 部署狀態」區塊（該區塊僅由 `/plan-close` 初始化）。

**4-3. 更新 Properties**（1 次 `notion-update-page` properties）

根據 README.md 的 `status` 更新「開發階段」屬性：status 值即開發階段值，一對一對應（例：`status: 開發中` → 開發階段設為「開發中」）。

### 5. 回傳結果

```
同步完成！

📊 Notion 頁面：{URL}
📄 已同步：spec.md, db.md
📊 Notion API 呼叫：{N} 次

提示：此為中途同步，結案時請使用 /plan-close 做完整同步。
```

---

## 何時不用

sync 組——本 skill 是「未結案的中途同步」；結案批次同步用 /plan-close；單一 bug 頁更新用 /bug-update。

- 要結案（最終同步）→ /plan-close
- 更新單一 bug 頁 → /bug-update
- 部署 SQL 執行回報 → /plan-deploy-confirm

---

## Gotchas

- **中途同步不更新知識庫**：`plan-sync` 只更新 Notion 任務頁面的內容和 Properties，知識庫同步是 `plan-close` 的工作。回傳結果中需明確提示「知識庫將在結案時同步」。
- **notion_page_id 為空時的模板選擇**：補建 Notion 條目時，需從 `README.md` 的 `type` 欄位（`feature` / `bug`）判斷套用哪個模板。若 frontmatter 解析失敗讀不到 `type`，應詢問使用者而非預設。

---

## 邊界情況

- **notion_page_id 為空**：引導補建 Notion 條目
- **無文件可同步**：提示先執行 `/plan` 產出文件
- **Notion 頁面內容與模板不符**：嘗試模糊匹配區塊標題，找不到則附加在頁面最後
- **Notion API 失敗**：顯示具體錯誤，建議檢查網路或稍後重試
