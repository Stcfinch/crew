---
name: bug-investigate
description: 假說驅動的 Bug 根因調查 — 自動收集證據、模式比對、假說驗證，全程同步更新 Notion。當使用者提到「bug-investigate」、「調查 bug」、「查原因」、「根因分析」、「investigate」時觸發此 Skill。
---

# bug-investigate — 假說驅動根因調查

AI 主動調查 Bug 根因：收集證據、比對已知模式、建立假說、驗證假說，全程自動更新 Notion「任務追蹤工具」的 Bug 頁面。

---

## 鐵律

> **沒有根因確認，不能開始修復。**
> 假設不等於根因。「我覺得是 XXX」不夠，需要證據支持。

---

## 紀律護欄

> **反合理化**：執行前閱讀 `references/anti-rationalizations.md` 的「通用」和「bug-investigate 專用」段落。
> **動作邊界**：遵循 `references/boundaries.md` 的「bug-investigate」段落。

---

## 設定檔

執行前依序檢查以下路徑，讀取第一個找到的設定檔：
1. `~/.claude-company/bug-workflow-config.md`（公司環境）
2. `~/.claude/bug-workflow-config.md`（個人環境）

若都不存在，提示使用者先執行 `/bug-setup`。

---

## 前置條件

- 已使用 `/bug-start` 建立 Bug 條目（Notion 有「進行中」的 🐞 錯誤）
- 或使用者直接描述 bug 症狀（此時先執行 /bug-start 再進入調查）

> **前置檢查**：參照 `references/prerequisites.md` 執行完整前置檢查（CLAUDE.md + 設定檔 + 專案註冊）。

---

## 使用方式

```
/bug-investigate                        # 調查當前進行中的 bug
/bug-investigate NullPointerException   # 帶症狀描述開始調查
/bug-investigate --resume               # 繼續上次的調查（讀取 Notion 已有內容）
```

---

## 流程

### 1. 定位目標 Bug

與 `/bug-update` 相同邏輯：

1. 從設定檔讀取「任務追蹤工具」Data Source ID，精確查詢該資料庫
2. 使用 `notion-search` 搭配 `data_source_url: collection://{任務追蹤工具 Data Source ID}` 搜尋：
   - 狀態為「進行中」
   - 任務類型包含「🐞 錯誤」
3. 同時取得 Git Repo 識別碼（從 `git remote get-url origin` 解析），用於輔助篩選同一專案下的 Bug
4. Git branch 匹配 → 自動選定
5. 多個候選 → 列出選擇

選定後使用 `notion-fetch` 讀取頁面完整內容。

若使用 `--resume`：讀取已有的「調查過程」區塊，從中斷點繼續。

### 2. Phase 1：證據收集（自動）

AI 根據 bug 描述自動收集初始證據，不需使用者介入。

#### 2.1 錯誤 Log 搜集

根據專案類型決定搜集方式：

```bash
# 搜尋專案中的 log 檔案
find . -name "*.log" -mmin -60 -type f 2>/dev/null | head -5

# 若有 Docker 容器
docker ps --format '{{.Names}}' 2>/dev/null | head -5
```

找到 log 來源後：

- **log 檔案在磁碟** → 使用 Read tool 讀取（避免 RTK 壓縮，遵循 CLAUDE.md 規範）
- **需要 shell 指令** → 精確除錯場景一律用 `rtk proxy <cmd>`

搜集策略：
- grep ERROR / Exception / FATAL（最近 30 分鐘）
- 擷取完整 stacktrace（從 Exception 行到下一個非 `at` 行）
- 記錄時間戳和頻率

#### 2.2 Git 歷史分析

```bash
# 最近 10 筆 commit
git log --oneline -10

# 最近修改的檔案
git log --since="3 days ago" --name-only --format="" | sort | uniq -c | sort -rn | head -10

# 若 stacktrace 提到特定檔案，查該檔案的最近變更
git log --oneline -5 -- <affected-file>
git diff HEAD~5..HEAD -- <affected-file>
```

#### 2.3 環境狀態

```bash
git branch --show-current
git status --short
```

#### 2.4 知識庫搜尋

搜尋 Notion Bug 知識庫中同專案的歷史 Bug：

- 用 `notion-search` 搭配 Bug 知識庫 Data Source ID
- 關鍵字：從 bug 描述和 stacktrace 擷取核心詞
- 若有匹配 → 讀取歷史根因和解法，作為調查線索

#### 2.5 學習搜尋

搜尋本地學習檔案中的相關記錄：

```bash
LEARN_FILE="$HOME/.claude-company/bug-workflow/learnings/{project-slug}.jsonl"
if [ -f "$LEARN_FILE" ]; then
  grep -i "<keywords>" "$LEARN_FILE" | tail -5
fi
```

若有匹配的歷史學習 → 顯示：「歷史學習：{insight}（{date}，confidence {N}/10）」

#### 2.6 寫入 Notion

將收集到的證據寫入 Notion 頁面「調查過程」區塊。

**重要**：使用 `update_content` 前，必須先 `notion-fetch` 取得現有內容，將新內容附加到現有內容後面再寫回，避免覆蓋。

寫入格式：

```markdown
### [HH:mm] 自動收集的證據

**錯誤 Log**：
```
{擷取的 ERROR/Exception，含 stacktrace}
```

**最近變更**（3 天內）：
- {commit hash} {message}（{affected files}）

**環境狀態**：
- 分支：{branch}
- 未提交變更：{N} 個檔案

**歷史參考**：
- {類似 bug 標題}：{根因摘要}（{日期}）

**歷史學習**：
- {insight}（confidence {N}/10）
```

### 3. Phase 2：模式比對

AI 根據收集到的證據，比對已知 bug 模式表（`references/bug-patterns.md`）。

讀取 `references/bug-patterns.md` 的 7 種模式定義，將證據中的症狀逐一比對：

```
依據證據比對結果：

  症狀：NullPointerException at PushService.java:235
  模式比對：NPE / NullPointer（confidence: 高）
  調查方向：追蹤 null 來源 — 參數傳入？DB 查詢回傳？API 回應？

  相關歷史：知識庫中有 2 筆同檔案的 NPE 記錄
```

寫入 Notion「調查過程 > 初步判斷」：

```markdown
### [HH:mm] 模式比對

**匹配模式**：NPE / NullPointer
**調查方向**：追蹤 null 來源
  - PushService.java:235 的 `accessToken` 可能為 null
  - 需確認 token 取得邏輯和過期處理
**歷史參考**：同檔案有 2 筆 NPE 歷史（2026-02-15、2026-01-20）
```

### 4. Phase 3：假說建立與驗證

#### 4.1 建立假說

AI 根據證據和模式比對，提出具體、可驗證的假說：

```
根因假說 #1：
  「PushService.getAccessToken() 在 token 過期後回傳 null，
   而 PushService.sendPush() 未檢查 null 就呼叫 token.getValue()」

驗證方式：
  1. 讀取 PushService.java 的 getAccessToken() 方法
  2. 確認 token 過期邏輯
  3. 檢查 sendPush() 是否有 null check
```

#### 4.2 執行驗證

AI 根據驗證方式執行具體操作：

```bash
# 讀取相關程式碼
grep -n "getAccessToken\|sendPush\|accessToken" src/main/java/.../PushService.java
```

使用 Read tool 讀取關鍵方法的完整實作。

若需要 DB 查詢驗證（且 DB MCP 可用）：

```
使用 execute_sql 查詢相關資料狀態
```

若需要 API 測試驗證：

```bash
curl -s "http://localhost:8080/api/xxx" -H "Authorization: Bearer <token>"
```

#### 4.3 判定結果

- **假說確認** → 進入 Phase 4
- **假說否定** → 記錄為什麼不對，修正假說

寫入 Notion：

```markdown
### [HH:mm] 假說 #1 驗證

**假說**：token 過期後 getAccessToken() 回傳 null
**驗證結果**：❌ 否定
**原因**：getAccessToken() 有 null check，過期時會自動 refresh
**新線索**：refresh 呼叫的 API endpoint 回傳 HTTP 401 時沒有 retry 邏輯
```

#### 4.4 3-Strike 升級規則

若連續 3 次假說都被否定：

```
⚠️  已嘗試 3 次假說，全部被否定。

已排除的方向：
  1. Token 過期 — getAccessToken() 有自動 refresh
  2. API 回傳 401 — retry 邏輯存在但只 retry 1 次
  3. 網路超時 — timeout 設定正常（30s）

建議：
  • 需要更多資訊（log 時間範圍擴大？不同環境？）
  • 可能需要在測試環境重現
  • 或請熟悉此模組的同事協助

要繼續調查還是暫停？
```

若使用者選擇繼續 → 重置計數器，繼續調查。
若使用者選擇暫停 → 記錄當前進度到 Notion，結束。

### 5. Phase 4：根因確認

假說確認後，將根因寫入 Notion「根因分析」區塊：

```markdown
## 🧠 根因分析

- **問題根因**：LINE API 的 access token refresh 端點偶爾回傳 HTTP 503，
  而 getAccessToken() 的 retry 邏輯只重試 1 次且未處理 503 狀態碼，
  導致第二次推播時 accessToken 為 null。
- **問題檔案**：PushService.java:235
- **問題程式碼**：
  ```java
  // retry 只處理 401，未處理 503
  if (response.getStatusCode() == 401) {
      return refreshToken();
  }
  return null; // ← 503 時走到這裡
  ```
```

同時更新 Notion 頁面屬性：
- 根因分類 → 自動推斷（此例：「第三方API」）

### 6. Phase 5：調查報告

產出結構化調查報告，寫入 Notion 頁面底部：

```markdown
---

## 📋 調查報告

| 項目 | 值 |
|------|-----|
| 調查日期 | {YYYY-MM-DD} |
| 調查時長 | {N} 分鐘 |
| 假說嘗試 | {N} 次（確認第 {N} 次） |
| 證據來源 | Log + Git + 知識庫 |

### 時間線
1. [HH:mm] 收集證據 — stacktrace + 最近 commit
2. [HH:mm] 模式比對 — NPE 模式，追蹤 null 來源
3. [HH:mm] 假說 #1 否定 — token refresh 正常
4. [HH:mm] 假說 #2 確認 — 503 未處理
5. [HH:mm] 根因確認
```

### 7. 回傳結果

```
Bug 調查完成！

📋 根因：LINE API refresh 回傳 503 未處理
📊 調查過程：2 次假說，第 2 次確認
🔗 Notion：{頁面連結}

後續可使用：
  • /bug-fix          — 修復並驗證（會檢查根因是否已填寫）
  • /bug-update <補充> — 補充更多資訊
  • /bug-close         — 修復完成後結案
```

---

## Gotchas

- **Log 讀取遵循 RTK 規範**：精確除錯場景（追蹤 timestamp、request ID、事件順序）一律用 `rtk proxy <cmd>` 或 Read tool，避免被 RTK hook 有損壓縮。
- **notion-update-page 的 update_content 是覆蓋**：每次寫入調查過程時，必須先 `notion-fetch` 取得現有內容，附加新內容後再寫回。
- **假說驗證不要改 code**：investigate 階段只讀取和查詢，不修改程式碼。修改是 bug-fix 的職責。
- **知識庫搜尋可能回傳不相關結果**：Bug 知識庫的關鍵字搜尋粒度較粗，AI 需判斷歷史 bug 是否真的相關，不要盲目採用歷史根因。
- **3-Strike 不是硬限制**：使用者可選擇繼續。3-Strike 的目的是「停下來思考」而不是「強制停止」。

## 邊界情況

- **沒有 log 可收集**：跳過 log 收集，從 git 歷史和程式碼分析開始
- **Bug 知識庫未設定**：跳過知識庫搜尋，不阻擋流程
- **學習檔案不存在**：跳過學習搜尋，首次使用時自動建立
- **DB MCP 不可用**：跳過 DB 查詢驗證，提示使用者手動查詢
- **使用者中途提供新線索**：接受新資訊，調整假說方向
- **--resume 時 Notion 內容被手動修改**：以 Notion 現有內容為準，不覆蓋
