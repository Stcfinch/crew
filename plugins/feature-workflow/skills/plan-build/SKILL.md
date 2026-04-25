---
name: plan-build
description: 從 .spec/ 讀取設計文件，以 Agent Teams leader-delegate 模式（最多 5 人團隊）產生程式碼。Leader 只協調不寫 code。當使用者提到「plan-build」、「build」、「產生程式碼」時觸發此 Skill。
---

# plan-build — Agent Teams 程式碼產生

從 `.spec/{slug}/` 讀取設計文件（spec.md、db.md、arch.md），以 **Agent Teams** leader-delegate 模式產生程式碼。Leader 只負責協調，不直接寫程式碼。

---

## 前置條件

### 環境變數

必須啟用 Agent Teams 實驗功能（擇一設定）：

**方式 A**：加入 shell profile（`~/.zshrc` 或 `~/.bashrc`）
```bash
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
```

**方式 B**：加入 settings.json 的 `env` 區塊
```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

### 設計文件

**必須**至少完成 `/plan-arch`（arch.md 存在）。若 arch.md 不存在，**禁止繼續**，直接告知使用者先執行 `/plan-arch` 產生架構設計。

> **前置檢查**：參照 bug-workflow plugin 的 `references/prerequisites.md` 檢查 CLAUDE.md 是否存在。

---

## 紀律護欄

> **反合理化**：執行前閱讀 `references/anti-rationalizations.md` 的「通用」和「plan-build 專用」段落。在任何步驟中感到「可以跳過」的衝動時，查表確認是否為已知偏離模式。
> **動作邊界**：遵循 `references/boundaries.md` 的「plan-build」段落。🟢 自動做、🟡 先問、🔴 絕不。

---

## 使用方式

```
/plan-build                # 完整產生（後端 + 前端 + API + 測試）
/plan-build --dry-run      # 預覽不建立檔案
/plan-build --backend-only # 只產後端
```

---

## 流程

### 1. 定位活躍任務

與 `/plan` 相同邏輯：從 Git branch 或 `_index.md` 匹配活躍任務。

讀取 `.spec/{slug}/README.md` 取得元資訊。

### 2. 讀取設計文件

讀取以下 `.spec/{slug}/` 下的檔案：

| 檔案 | 用途 | 必要性 |
|------|------|--------|
| `spec.md` | 技術規格（API 設計、業務邏輯） | 建議 |
| `db.md` | DB 設計（表結構） | 建議 |
| `db.sql` | SQL 檔案 | 選讀 |
| `arch.md` | 架構設計（類別清單、介面定義） | **必要** |

若 arch.md 不存在，**停止流程**，告知使用者必須先執行 `/plan-arch` 產生架構設計後再回來執行 `/plan-build`。不提供跳過選項。

### 3. 判斷團隊組成

依據 `references/team-composition.md` 的判斷規則決定團隊配置。

讀取 spec.md 的「判斷」區塊，取得 TASK_TYPE、CHANGE_SCOPE、FRONTEND_REQUIRED、DB_MCP_AVAILABLE 等欄位，按規則判斷。

若判斷區塊缺少 TASK_TYPE / CHANGE_SCOPE → 回退到 v4.9.0 邏輯（只看 FRONTEND_REQUIRED × DB_MCP）。

### 4. 確認執行計畫

```
即將啟動 Agent Teams 產生程式碼：

📄 設計來源：.spec/{slug}/
📊 Teammate 配置：
  {• db-engineer       — DB 遷移/索引/效能優化（需 DB MCP）}
  • backend-engineer  — 後端核心（POJO/Mapper/Service）
  • api-engineer      — API 層（Controller/DTO/驗證）
  {• frontend-engineer — 前端頁面（{FRONTEND_TECH}）}
  • test-engineer     — 測試程式碼（單元測試/整合測試）

{--dry-run: 預覽模式，不建立檔案}

確認開始？[Y/n]
```

### 5. 準備分層脈絡

依據 `references/build-context-layers.md` 的四層策略，為每個 Teammate 準備定制化的脈絡。

#### 5a. 擷取共用核心（Layer 0）
從 CLAUDE.md 擷取技術棧、命名慣例、禁止事項，格式化為 5 行以內。

#### 5b. 準備角色脈絡（Layer 1）
按 Teammate 角色，從 .spec/ 文件中擷取該角色需要的段落（見 build-context-layers.md 的角色分配表）。

#### 5c. 預篩選範本（Layer 2）
1. 用 Glob 找到同層級的候選範本
2. 讀取每個候選，選出最簡單、最標準的
3. 擷取關鍵片段（class 宣告 + 1 個方法 + import 區塊）
4. 附帶學習重點指引

#### 5d. 預備交叉引用清單（Layer 3）
從設計文件中提取跨角色約束（NOT NULL、UNIQUE、必填參數、外鍵、分頁限制）。

### 6. 啟動 Agent Teams

讀取 `references/build-prompts.md` 取得 Teammate prompt 模板。

根據步驟 3 的團隊組成判斷，選擇對應的模板（Subagent / Agent Teams），將步驟 5 準備的分層脈絡嵌入各 Teammate 的 prompt 中。

> 模板中的 `{placeholder}` 需替換為實際值。見 build-prompts.md 的變數說明。

#### Teammate prompt 組裝規則

每個 Teammate 的最終 prompt = Layer 0 共用核心 + Layer 1 角色脈絡 + Layer 2 範本片段 + Layer 3 交叉引用 + build-prompts.md 的角色模板

#### Subagent vs Agent Teams 選擇

根據步驟 3 的判斷結果（見 `references/team-composition.md`）：
- 1 人 → Subagent 模式
- 2+ 人 → Agent Teams 模式（或多個 Subagent）

### 7. 更新 .spec/ 檔案

程式碼產生完成後：

1. 產生 `.spec/{slug}/files.md`：

```markdown
# 程式碼清單

## 新增檔案

| 檔案路徑 | 層級 | 說明 |
|---------|------|------|
| {path} | {Controller/Service/DAO/...} | {說明} |

## 修改檔案

| 檔案路徑 | 修改說明 |
|---------|---------|
```

2. 更新 `README.md` 的 `status: 開發中`
3. 在 `log.md` 追加紀錄

### 7.5 退出驗證（強制，不可跳過）

Leader 在回傳結果前，逐項檢查以下退出條件：

#### 自動驗證項目

| # | 檢查項目 | 驗證方式 | 失敗處理 |
|---|---------|---------|---------|
| E1 | 所有 Teammate 都已完成 | 確認每個 Teammate 回報了完成訊息 | 等待或重試未完成的 Teammate |
| E2 | files.md 已產出 | 檢查 .spec/{slug}/files.md 存在且非空 | 從 Teammate 產出中彙整產出 files.md |
| E3 | 產出檔案真的存在 | 讀取 files.md，用 ls 或 Read 確認每個檔案路徑存在 | 列出缺失檔案，要求使用者決定：重試 / 移除 |
| E4 | 無編譯錯誤（若可驗證） | 若專案有 build 指令（mvn compile / gradle build），執行一次 | 顯示錯誤訊息，標記 ⚠️ 但不阻擋 |
| E5 | API 契約一致性 | 比對 Controller 的 @RequestMapping 與 spec.md 的 API 端點 | 列出不一致項目，標記 ⚠️ |
| E6 | spec.md 驗收條件有對應程式碼 | 讀取 spec.md 的驗收條件 checkbox，grep 產出檔案確認有相關實作 | 列出無對應的驗收條件，標記 ⚠️ |

#### 驗證結果分級

- **🔴 BLOCK**（E1, E2, E3）：必須解決後才能標記完成
- **⚠️ WARN**（E4, E5, E6）：記錄到 log.md，不阻擋但提醒使用者

#### 驗證報告格式

寫入 `.spec/{slug}/log.md` 並在回傳結果中顯示：

```
退出驗證結果：
  ✅ E1 所有 Teammate 完成
  ✅ E2 files.md 已產出（12 個檔案）
  ✅ E3 所有檔案存在
  ⚠️  E4 編譯未驗證（專案無標準 build 指令）
  ✅ E5 API 契約一致（4/4 端點吻合）
  ⚠️  E6 驗收條件 #3「支援匯出 Excel」無對應程式碼

  結論：可繼續，但建議處理 E6 後再進 plan-verify
```

### 8. 回傳結果

```
程式碼產生完成！

📁 產出清單：.spec/{slug}/files.md
📊 統計：N 個後端 + M 個前端 + K 個測試

已完成：
  {✅ db-engineer       — Migration SQL + 索引建議 + 效能報告}
  ✅ backend-engineer  — N 個檔案（POJO/Mapper/Service）
  ✅ api-engineer      — N 個檔案（Controller/DTO）
  {✅ frontend-engineer — M 個檔案（JSP/JS/CSS）}
  ✅ test-engineer     — K 個檔案（測試）
  {✅ API 契約確認 — 一致}

後續可使用：
  • /plan-verify  — 驗收驗證
  • /plan-review  — Agent Teams 3 人審查
  • /plan-close   — 結案並同步 Notion
```

---

## DB MCP 提示詞模版

> 完整的 DB MCP 提示詞模板見 `references/build-prompts.md` 的「DB MCP 提示詞模版」段落。

步驟 5 檢查 DB MCP 可用性（`claude mcp list` 是否有 `dbhub`）後，根據結果決定是否加入 DB 工程師：
- **已安裝**：Agent Teams 加入「成員 0：DB 工程師」；Subagent 模式嵌入 `{db_mcp_instruction}`
- **未安裝**：不加入 DB 工程師；`{db_mcp_instruction}` 替換為空字串

---

## Gotchas

- **Leader 不能自己寫 code**：Agent Teams 模式下，Leader（你自己）只負責協調和分配任務。如果 Leader 直接寫程式碼，會跟 Teammate 的產出衝突（寫同一個檔案）。所有產出必須由 Teammate 完成。
- **Teammate 之間的檔案衝突**：雖然設計上各 Teammate 負責不同目錄，但 API 工程師的 DTO 和後端工程師的 Entity 可能放在相近的 package 下。如果兩者同時寫同一個 DTO 類別，後寫的會覆蓋先寫的。確保在 prompt 中明確劃分 DTO 歸屬。
- **Agent Teams 環境變數未設定**：`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 不存在時，建立 Team 的指令會靜默失敗（不報錯但不產出），很難 debug。步驟 1 就要先檢查。
- **現有程式碼範本的選擇很關鍵**：給 Teammate 參考的 POJO/Mapper/Service 範本如果選到非典型的（如有特殊 annotation 或非標準命名），Teammate 會學到錯誤風格並複製到所有產出中。優先選最簡單、最標準的範本檔。
- **DB MCP Teammate 超時**：DB 工程師如果查詢的表很多或 DB 回應慢，可能花很長時間。設定合理的任務範圍（只查本功能相關的表，不要全表掃描）。
- **殘留 Team 問題**：如果上次 `plan-build` 中途失敗，可能留下殘留的 Team。在建新 Team 前先用 `TeamDelete` 清理，否則會報錯「已有活躍 Team」。

參考 `examples/leader-delegation.md` 了解 Leader 如何有效分配任務和協調 Teammate。

---

## 邊界情況

- **arch.md 不存在**：**hard block** — 停止流程，要求使用者先執行 `/plan-arch`
- **Agent Teams 未啟用**：顯示設定指引
- **--dry-run 模式**：不建立任何檔案，只展示清單和關鍵片段
- **Teammate 失敗**：提供選項：重試 / 跳過 / 終止
- **API 契約不一致**：以 API 工程師為準，其他成員調整
- **每個工作階段只能一個 Team**：建立新 Team 前確認無殘留 Team
- **僅後端模式**：不建立 Agent Teams，使用 Subagent 完成
