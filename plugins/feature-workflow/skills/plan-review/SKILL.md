---
name: plan-review
description: 以 Agent Teams 3 人並行審查 .spec 任務的程式碼（邏輯/品質/效能）並交叉審查，報告寫入 .spec/ 目錄。當使用者提到 /plan-review、「Agent Teams 程式碼審查」、「plan-review 審查」時觸發此 Skill。
---

# plan-review — Agent Teams 程式碼審查

以 **Agent Teams** leader-delegate 模式，3 位 Reviewer 並行審查程式碼，完成後**互相分享發現並交叉審查**，Leader 彙整報告寫入 `.spec/{slug}/review.md`。

---

## 前置條件

### 環境變數

必須啟用 Agent Teams 實驗功能（同 plan-build，擇一設定）：

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

> ⚠️ 未設定時，建立 Agent Team 的指令會**靜默失敗**（不報錯但不產出 Reviewer 結果），難以 debug，務必在此先確認已設定。

### 程式碼

建議已執行 `/plan-build` 產生程式碼，或已有開發中的程式碼。

> 💡 plan-review 從 .spec/ 和程式碼檔案讀取所有輸入，不依賴對話歷史。
>    若剛執行完 /plan-build，建議先 /clear 再執行，確保有足夠 context 空間。

> **前置檢查**：參照 plugin 根目錄 `references/prerequisites.md`（相對 SKILL.md 為 `../../references/`）檢查 CLAUDE.md 是否存在。

---

## 紀律護欄

> 紀律護欄：`../../references/discipline-preamble.md`（通用紀律）＋ `../../references/anti-rationalizations.md`「plan-review 專用」＋ `../../references/boundaries.md`「plan-review」段＋ `../../references/handoff-discipline.md`「plan-review」段（斷點保險，進度即寫）；有「可以跳過」「應該夠了」的衝動時，停下查表確認是否為已知偏離模式。

---

## 使用方式

```
/plan-review               # 完整 3 人審查
/plan-review --quick       # 快速審查（僅 logic-reviewer，用 Subagent）
```

---

## 流程

### 1. 定位活躍任務

與 `/plan` 相同邏輯：從 Git branch 或 `_index.md` 匹配活躍任務。

### 2. 收集審查範圍

確定要審查的程式碼範圍：

1. 若 `.spec/{slug}/files.md` 存在 → 從中取得檔案清單
2. 否則，從 Git diff 取得（`{prod_branch}` 從專案設定讀取；未設定時，先取 `origin/HEAD` 指向的分支，若無則依序嘗試 `production` → `master` → `main`）：
   ```bash
   git diff $(git merge-base HEAD {prod_branch})..HEAD --name-only
   ```
3. 若都沒有 → 提示使用者指定檔案

### 3. 讀取設計文件

讀取 `.spec/{slug}/` 下的可用文件作為審查基準：
- `spec.md`（技術規格 — 驗證功能正確性）
- `db.md`（DB 設計 — 驗證 SQL 正確性）
- `arch.md`（架構設計 — 驗證分層一致性）
- `verify.md`（運行時驗證結果 — 供 Reviewers 參考）— 選讀

### 4. 確認執行計畫

```
即將啟動 Agent Teams 程式碼審查：

📁 審查範圍：N 個檔案
📊 Reviewer 配置：
  • Reviewer 1 — 邏輯正確性（Opus）
  • Reviewer 2 — 程式碼品質（Sonnet）
  • Reviewer 3 — 效能審查（Opus）

確認開始？[Y/n]
```

### 5. 啟動 Agent Teams

#### 完整審查（Agent Teams）

使用自然語言要求 Claude 建立 Agent Team，生成 3 個 Reviewer：
- **Reviewer 1：邏輯正確性**（Opus）— 讀取 spec.md/arch.md/verify.md 與變更檔案，檢查 API 參數驗證、業務邏輯、查詢條件、例外處理、邊界條件、回傳格式
- **Reviewer 2：程式碼品質**（Sonnet）— 比對專案既有檔案風格，檢查命名規範、package 結構、Lombok、註解、error handling、edge case
- **Reviewer 3：效能審查**（Opus）— 讀取 db.md 與變更檔案，檢查 N+1、分頁、索引、迴圈內 DB 呼叫、快取、連線池

三位 Reviewer 完成後互相分享發現、交叉審查，Lead 只負責協調（delegate mode，不自己寫 code）彙整產出 Review Report，全程繁體中文。

完整派工 prompt 模板（含各 Reviewer 逐項檢查清單與標記符號）：plugin 根目錄 `references/review-prompts.md`（相對 SKILL.md 為 `../../references/`），套用時將 `{slug}`、`{檔案清單}` 換成實際值。

#### 快速審查（--quick，Subagent）

使用 Agent tool 啟動單一 subagent（model: opus），只做邏輯正確性審查：

```
你是資深程式碼審查員。

## 設計文件
{spec.md + arch.md 內容}

## 審查檔案
{檔案清單及內容}

## 專案上下文
{CLAUDE.md 內容}

## 任務
對以上程式碼進行快速審查，聚焦於：
1. 邏輯正確性
2. 明顯的安全問題
3. 風格一致性（與專案現有程式碼比對）

標記嚴重程度：🔴 嚴重 / 🟡 建議 / 🟢 良好
輸出使用繁體中文。
```

### 6. 彙整審查報告

Leader 收集所有 Reviewer 的發現（含交叉分享結果），彙整寫入 `.spec/{slug}/review.md`：

```markdown
# 程式碼審查報告

## 審查日期
{日期}

## 審查範圍
{N} 個檔案

## 統計
| 類別 | 🔴 嚴重 | 🟡 建議 | 🟢 良好 |
|------|---------|---------|---------|
| 邏輯正確性 | {N} | {N} | {N} |
| 程式碼品質 | — | {N} | {N} |
| 效能 | {N} | {N} | {N} |
| **合計** | **{N}** | **{N}** | **{N}** |

## 🔴 嚴重問題

### [{序號}] {問題標題}
- **檔案**：{路徑}:{行號}
- **Reviewer**：{logic/quality/performance}
- **問題**：{描述}
- **建議**：{修復建議}

## 🟡 改善建議

### [{序號}] {建議標題}
- **檔案**：{路徑}:{行號}
- **Reviewer**：{reviewer}
- **建議**：{描述}

## 🟢 良好實踐

{正面反饋清單}

## 交叉審查發現

{Reviewers 之間互相分享後發現的額外觀點}
```

### 7. 更新 .spec/

1. 更新 `README.md` 的 `status: 程式碼審查`
2. 在 `log.md` 追加紀錄

### 8. 回傳結果

```
程式碼審查完成！

📋 報告：.spec/{slug}/review.md
📊 統計：🔴 {N} 嚴重 / 🟡 {N} 建議 / 🟢 {N} 良好

{若有嚴重問題}
⚠️  發現 {N} 個嚴重問題，建議修復後再結案。

後續可使用：
  • 修正問題後再次 /plan-review
  • /plan-close   — 結案並同步 Notion
```

---

## 何時不用

分工邊界：本 skill 專責 CREW `.spec` 任務的 Agent Teams 多角色交叉審查，其餘審查需求請改用下列指令。

- 一般 diff code review → 內建 `/code-review` 或 `codex`
- Java 最佳實務審查 → 個人 `java-code-review`
- 提交前驗證需求覆蓋 → `superpowers:requesting-code-review`
- 安全掃描 → `/plan-security`；架構設計建議 → 個人 `java-design-advisor`

---

## Gotchas

- **3 人並行的 token 消耗約為單次的 5-6 倍**：3 位 Reviewer 各自讀取完整程式碼 + 設計文件，再加上交叉審查。小變更（< 5 個檔案）建議用 `--quick` 模式（單一 Subagent），節省 80% token。
- **交叉審查傾向「無中生有」**：三位 Reviewer 獨立審查都沒嚴重問題時，交叉審查階段不太可能突然冒出真正嚴重的問題。Leader 彙整時應對交叉審查新增的「嚴重」問題持保留態度，優先信任獨立審查的結果。
- **merge-base 的主分支名稱**：`{prod_branch}` 從專案設定檔的 `prod_branch` 欄位讀取（由 `/project-add` 設定）。若未設定，回退邏輯：先取 `origin/HEAD` 指向的分支，若無則依序嘗試 `production` → `master` → `main`。

---

## 邊界情況

- **無程式碼可審查**：提示先執行 `/plan-build` 或 commit 程式碼
- **Agent Teams 未啟用**：顯示設定指引，或建議用 `--quick` 模式
- **交叉審查發現嚴重問題**：提供選項：修正後重新審查 / 忽略繼續 / 終止
- **Reviewer 失敗**：提供選項：重試 / 跳過該 Reviewer / 終止
- **--quick 模式**：不建立 Agent Teams，只用 Subagent
