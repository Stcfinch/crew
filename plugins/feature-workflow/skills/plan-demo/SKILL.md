---
name: plan-demo
description: 純本地產出範例 .spec/ 任務，不依賴 Notion / Agent Teams / DB MCP，讓評估者 5 分鐘看到 CREW 完整流程效果。預設範例：新增使用者管理 API（CRUD + 簡單 DB schema）。當使用者提到「plan-demo」、「dry-run」、「示範」、「試跑」、「demo」、「評估 CREW」、「沒設 Notion 也能用」時觸發此 Skill。
---

# plan-demo — 純本地評估模式

給未設定 Notion 但想評估 CREW 的人一個 5 分鐘看到完整流程的入口。
產出真實的 `.spec/demo-{task}/` 目錄含 spec / db / arch / files / verify 各檔範例，
但**不寫 Notion、不啟 Agent Teams、不連 DB MCP**。

---

## 紀律護欄

> 通用紀律見 plugin 根目錄 `references/discipline-preamble.md`（相對 SKILL.md 為 `../../references/`）。
> 本 skill 專用條目：plugin 根目錄 `references/anti-rationalizations.md`「plan-demo 專用」+ `references/boundaries.md`「plan-demo」段落（相對 SKILL.md 為 `../../references/`）。

---

## 使用方式

```
/plan-demo                       # 用內建預設範例「使用者管理 API」
/plan-demo <自訂題目>            # 簡短描述自訂任務（仍跑本地產出，不寫 Notion）
/plan-demo --keep                # 保留產出（預設清理會在 demo 結束時清除）
/plan-demo --cleanup             # 立即清除既有 demo 產物（.spec/demo-*/）
```

---

## 前置條件

**最低需求**：當前目錄有寫入權限即可。**不需要**：
- ❌ Notion MCP 安裝
- ❌ Notion 授權
- ❌ Agent Teams 環境變數
- ❌ DB MCP 安裝
- ❌ CLAUDE.md 或 /project-add 註冊
- ❌ `/bug-setup` 或 `/plan-setup`

若 CLAUDE.md 存在，demo 會用其中的技術棧資訊讓範例更貼合；若無，使用 `spring-boot-jpa` 預設範例。

---

## 流程

### 1. 確認題目

未指定 → 用內建範例：

```
題目：使用者管理 API
描述：提供使用者新增、查詢、更新、刪除（CRUD），含分頁與基本驗證
技術棧：Spring Boot + JPA（若 CLAUDE.md 偵測到其他棧則替換）
```

使用者指定 → 用該描述。

### 2. 產出 `.spec/demo-{slug}/` 目錄

`{slug}` 從題目自動產生（如「使用者管理 API」→ `user-management-api`）。
為避免污染真實 .spec，**前綴 `demo-`**：`.spec/demo-user-management-api/`。

產出檔案（全本地寫入，不啟 Agent）：

#### 2a. README.md（任務元資訊）

```markdown
---
slug: demo-user-management-api
type: feature
name: 使用者管理 API（DEMO）
created: {today}
status: 規劃中（DEMO）
demo: true
---

# 使用者管理 API（DEMO）

> ⚠️ 此為 `/plan-demo` 產生的示範任務，未同步到 Notion。
> 真實使用請先 `/crew-init` 完成首次設定，再用 `/plan-start <任務>` 開新任務。

...
```

#### 2b. spec.md（含標準「判斷」區塊）

範例規格含完整結構：API 設計、業務邏輯、驗收條件、判斷區塊（TASK_TYPE=feature、DB_REQUIRED=true 等）。

#### 2c. db.md（DB 設計範例）

users 表 schema + 索引建議。

#### 2d. arch.md（架構設計範例）

Controller / Service / Repository / Entity 類別清單與介面定義。

#### 2e. files.md（程式碼清單範例）

列出「會被 plan-build 產出的檔案」假想清單，不實際產 code。

#### 2f. verify.md（驗證報告範例）

含 4 個驗收項目，3 PASS、1 ⚠️ WARN（展示三種狀態）。

#### 2g. log.md

```
### [{today}] plan-demo 產出
- 產出檔案：README、spec.md、db.md、arch.md、files.md、verify.md
- 摘要：CREW 評估模式，未實際呼叫 Agent Teams / DB MCP / Notion
```

### 3. 引導使用者體驗

產出後顯示：

```
═══════════════════════════════════════════
🎯 CREW Demo 完成

📂 產出目錄：.spec/demo-user-management-api/
📊 含 7 個範例檔，展示 plan-* 完整流程的產出格式

💡 接下來可以做什麼：

1. 看看設計文件長什麼樣：
   - cat .spec/demo-user-management-api/spec.md
   - cat .spec/demo-user-management-api/arch.md

2. 用 /plan-next 體驗智慧推薦：
   /plan-next demo-user-management-api

3. 看其他 skill 文件：
   ls plugins/feature-workflow/skills/

4. 真正開始用 CREW：
   /crew-init                  完成首次設定（含 Notion）
   /plan-start <你的任務>      建立真實任務
   /crew-doctor                檢查環境

5. 清理 demo 產物：
   /plan-demo --cleanup
═══════════════════════════════════════════
```

### 4. 自動清理時機

`/plan-demo` 預設**不自動清理**（使用者要主動 `--cleanup`）。
但會在 README.md 寫明「demo: true」，讓 `/plan-status` 顯示時標示「[DEMO]」並排在末尾。

`--keep` 旗標：明示「我之後會自己處理」，效果與預設相同（純 UX 信號）。

---

## 範例內容（內建）

### spec.md 範本片段

```markdown
# 使用者管理 API（DEMO）

## 判斷

| 欄位 | 值 | 說明 |
|------|-----|------|
| TASK_TYPE | feature | 全新功能 |
| CHANGE_SCOPE | medium | 4 個端點 + 1 個表 |
| FRONTEND_REQUIRED | false | 純後端 API |
| DB_REQUIRED | true | 新增 users 表 |
| NEW_API | true | 4 個端點 |

## API 設計

| Method | Path | 說明 |
|--------|------|------|
| POST | /api/users | 新增使用者 |
| GET | /api/users/{id} | 查詢單筆 |
| PUT | /api/users/{id} | 更新使用者 |
| DELETE | /api/users/{id} | 刪除使用者 |
| GET | /api/users?page=N&size=M | 分頁列表 |

## 業務邏輯
- 新增時 email 必須唯一
- 更新時 email 不可改成已存在者
- 刪除採軟刪除（deleted_at 時間戳）

## 驗收條件
- [ ] 可正確新增使用者，email 重複時回 409 Conflict
- [ ] 分頁參數 page/size 邊界處理（page < 0 / size > 100 拒絕）
- [ ] 軟刪除後查詢列表不會回傳已刪除使用者
- [ ] API 回應格式符合 ApiResult 標準
```

完整範本檔見 `references/demo-spec-template.md`（如未來新增該檔；目前 prompt 內 inline）。

---

## Gotchas

- **demo 產物會污染 `.spec/_index.md`**：若使用者已用 plan-start 建立過任務，index 會多一筆 demo 條目。/plan-status 會分組顯示讓使用者一眼分辨
- **CLAUDE.md 技術棧偵測不到** → 用 `spring-boot-jpa` 預設範本；不阻擋
- **重複跑 /plan-demo** → 若 `.spec/demo-{slug}/` 已存在，提示「是否覆寫？」
- **demo 不會建立 Git branch**：避免污染分支樹。真實 plan-start 會建分支

---

## 邊界情況

- **當前目錄無寫入權限** → 提示換目錄
- **使用者指定的題目過於複雜** → 仍按範本產出，但提醒「demo 模式不深入展開，建議 /plan-start 跑真實流程」
- **demo 已存在且使用者選不覆寫** → 跳過產出，僅顯示「查看現有 demo」指引
