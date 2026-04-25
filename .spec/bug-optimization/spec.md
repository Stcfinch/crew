# Bug Workflow 深層優化 — 技術規格書

## 參考來源

- [gstack investigate](~/.claude/skills/gstack/investigate/SKILL.md) — 五階段除錯法、鐵律（根因確認才能修）、3-strike 升級、範圍鎖定、跨 session 學習
- [gstack qa](~/.claude/skills/qa/SKILL.md) — gstack browse ($B) 驗證、health score、snapshot diff
- [addyosmani/agent-skills debugging](https://github.com/addyosmani/agent-skills) — Stop-the-Line 規則、六步除錯法、反合理化表、強制驗證
- CREW bug-workflow v3.4.0 現有架構

---

## 優先級與實施階段

| 階段 | 優先級 | 項目 | 投入 | 收益 | 涉及檔案 |
|------|--------|------|------|------|---------|
| Phase 1 | P0 | bug-investigate Skill | 高 | 高 | 新增 skills/bug-investigate/SKILL.md + references/ |
| Phase 1 | P0 | 反合理化表 + 三層邊界 | 低 | 高 | 新增 references/anti-rationalizations.md + boundaries.md |
| Phase 2 | P1 | bug-fix Skill | 中 | 高 | 新增 skills/bug-fix/SKILL.md |
| Phase 2 | P1 | bug-close 強化 | 中 | 中 | 修改 skills/bug-close/SKILL.md |
| Phase 3 | P2 | bug-start 初始證據收集 | 低 | 中 | 修改 skills/bug-start/SKILL.md |
| Phase 3 | P2 | 學習系統完整化 | 中 | 中 | 新增 references/learnings-schema.md |

---

## Phase 1：調查方法論 + 紀律護欄（P0）

### 1.1 bug-investigate Skill

#### 定位

```
目前 bug-workflow 的流程缺口：

  /bug-start → 建立 Notion 頁面（框架很好，但內容空白）
       │
       ▼
  使用者自己調查 ← 🔴 這裡沒有 AI 參與
       │
       ▼
  /bug-update → 被動記錄（使用者貼什麼就記什麼）
       │
       ▼
  /bug-close → 事後擷取 diff

新增 bug-investigate 後：

  /bug-start → 建立 Notion + 初始證據
       │
       ▼
  /bug-investigate → AI 主動調查（假說驅動）  ← 🆕 填補缺口
       │
       ▼
  /bug-fix → 修復紀律（鐵律 + 迴歸測試）      ← 🆕
       │
       ▼
  /bug-close → 退出驗證 + 知識庫 + 學習
```

#### SKILL.md 規格

```markdown
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

## 前置條件

- 已使用 `/bug-start` 建立 Bug 條目（Notion 有「進行中」的 🐞 錯誤）
- 或使用者直接描述 bug 症狀（此時先執行 /bug-start 再進入調查）

> **前置檢查**：參照 `references/prerequisites.md`。

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
1. 搜尋「進行中」的 🐞 錯誤
2. Git branch 匹配 → 自動選定
3. 多個候選 → 列出選擇

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

將收集到的證據寫入 Notion 頁面「調查過程」區塊：

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

AI 根據收集到的證據，比對已知 bug 模式表（`references/bug-patterns.md`）：

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

若使用者選擇繼續 → 重置計數器，繼續調查
若使用者選擇暫停 → 記錄當前進度到 Notion，結束

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
```

#### 影響範圍

| 動作 | 檔案 |
|------|------|
| 新增 | `skills/bug-investigate/SKILL.md` |
| 修改 | `.claude-plugin/plugin.json` — skills 陣列新增 |

---

### 1.2 Bug 模式表

#### references/bug-patterns.md

```markdown
# 已知 Bug 模式表

bug-investigate 的 Phase 2 使用此表比對症狀，縮小調查方向。

## 模式定義

### NPE / NullPointer

| 項目 | 說明 |
|------|------|
| 症狀 | NullPointerException、cannot invoke method on null |
| 常見原因 | DB 查詢回傳 null、API 回應欄位缺失、Optional 未處理、Map.get() 回傳 null |
| 調查方向 | 從 stacktrace 定位 null 變數 → 逆向追蹤：參數傳入？DB 回傳？API 回應？設定值？ |
| 驗證方式 | 讀取相關方法，確認每個可能為 null 的來源是否有 null check |

### SQL 資料異常

| 項目 | 說明 |
|------|------|
| 症狀 | 查詢結果為空、資料不預期、count 不對 |
| 常見原因 | WHERE 條件錯誤、JOIN 遺漏、資料狀態不一致、時區問題、字元編碼 |
| 調查方向 | 取出實際執行的 SQL → 手動在 DB 執行 → 比對預期結果 |
| 驗證方式 | DB MCP 或手動 SQL 查詢，確認資料狀態 |

### 第三方 API 異常

| 項目 | 說明 |
|------|------|
| 症狀 | HTTP 4xx/5xx、timeout、回應格式改變、token 失效 |
| 常見原因 | Token 過期、API 版本變更、Rate limit、網路不穩、SSL 憑證過期 |
| 調查方向 | 檢查 request/response log → 確認 token 狀態 → 比對 API 文件 |
| 驗證方式 | curl 重現 API 呼叫，比對回應 |

### 併發 / 競爭條件

| 項目 | 說明 |
|------|------|
| 症狀 | 間歇性失敗、時序相關、多人同時操作時出錯 |
| 常見原因 | 缺少鎖、事務隔離級別不足、靜態變數競爭、快取一致性 |
| 調查方向 | 分析錯誤發生的時間模式 → 檢查共享狀態 → 檢查事務邊界 |
| 驗證方式 | 用 rtk proxy 讀取完整 log 分析時間戳和 request ID 順序 |

### 設定 / 環境問題

| 項目 | 說明 |
|------|------|
| 症狀 | 本地正常但環境異常、部署後出錯、特定環境才有問題 |
| 常見原因 | 設定檔差異、環境變數遺漏、版本不一致、路徑不同 |
| 調查方向 | 比對本地與環境的設定差異 → 檢查部署腳本 → 確認環境變數 |
| 驗證方式 | 逐項比對設定，在問題環境執行測試 |

### 快取問題

| 項目 | 說明 |
|------|------|
| 症狀 | 顯示舊資料、清快取後正常、重啟後正常 |
| 常見原因 | TTL 設定不當、快取 key 碰撞、失效策略不對、快取穿透 |
| 調查方向 | 確認快取層級（本地 Caffeine / 分散式 Redis）→ 檢查 key 和 TTL |
| 驗證方式 | 直接查詢快取狀態（Redis CLI / debug endpoint） |

### 前端 UI 問題

| 項目 | 說明 |
|------|------|
| 症狀 | 畫面顯示不正確、按鈕無反應、JS error |
| 常見原因 | DOM 操作錯誤、事件綁定遺漏、CSS 衝突、JSP 語法錯誤 |
| 調查方向 | gstack browse 截圖 + console error → 定位前端程式碼 |
| 驗證方式 | `$B goto <url>` → `$B console --errors` → `$B snapshot -i` |
```

#### 影響範圍

| 動作 | 檔案 |
|------|------|
| 新增 | `references/bug-patterns.md` |

---

### 1.3 反合理化表

#### references/anti-rationalizations.md

```markdown
# Bug Workflow 反合理化參考

## 通用（所有 bug-* Skill 適用）

| # | AI 的內心獨白 | 為什麼不行 |
|---|-------------|-----------|
| G1 | 「使用者很急，跳過一些步驟」 | 急的時候更需要流程。跳步驟省 5 分鐘，誤判根因浪費 5 小時。 |
| G2 | 「這個 bug 很明顯，不用走完整流程」 | 明顯的 bug 底下常藏著不明顯的根因。表面的 NPE 可能是資料一致性問題。 |
| G3 | 「Notion 更新太花時間，最後再補」 | 最後不會補。即時記錄是調查的一部分，不是額外工作。 |

## bug-investigate 專用

| # | AI 的內心獨白 | 為什麼不行 |
|---|-------------|-----------|
| I1 | 「我已經知道原因了，不需要調查」 | 假設不等於根因。必須有證據支持。你「知道」的原因有 40% 是錯的。 |
| I2 | 「先改了看看對不對」 | 沒有根因就改是在猜。猜錯會引入新 bug，而且不知道猜對了沒有。 |
| I3 | 「log 太多了，看不完」 | 用 grep 篩選 ERROR/Exception。或用 Read tool 讀檔避免 RTK 壓縮。不需要看全部。 |
| I4 | 「這個 bug 太簡單不需要走完整流程」 | 簡單的 bug 最危險 — 你覺得簡單是因為沒看到複雜的部分。30% 的「簡單 bug」有深層根因。 |
| I5 | 「知識庫搜尋浪費時間」 | 同專案 30% 的 bug 有相似模式。5 秒搜尋可能省 30 分鐘調查。 |
| I6 | 「假說被否定 3 次了，隨便挑一個最可能的結案」 | 3-Strike 是提醒你「停下來想」，不是「隨便選」。選錯根因 → 修錯地方 → bug 復發。 |

## bug-fix 專用

| # | AI 的內心獨白 | 為什麼不行 |
|---|-------------|-----------|
| F1 | 「根因還不確定，但我有個 workaround」 | Workaround 會變成永久方案。根因不除，bug 會復發。技術債就是這樣累積的。 |
| F2 | 「改的地方太少不需要迴歸測試」 | 一行程式碼就能造成事故。迴歸測試證明的是「修好了」而不是「改了」。 |
| F3 | 「這個 bug 只影響一個使用者」 | 一個使用者遇到的問題，其他使用者在相同條件下也會遇到。只是還沒回報。 |
| F4 | 「順便改一下旁邊的 code」 | bug-fix 只改導致 bug 的程式碼。其他改善用另一個 commit，否則 revert 時會連帶。 |

## bug-close 專用

| # | AI 的內心獨白 | 為什麼不行 |
|---|-------------|-----------|
| C1 | 「根因分析沒填也沒關係，diff 就是答案」 | diff 告訴你「改了什麼」，不告訴你「為什麼壞」。知識庫沒有根因，下次同樣問題幫不上忙。 |
| C2 | 「測試環境沒法驗，直接結案」 | 至少標記「測試中」而不是「已完成」。未驗證的修復不是完成。 |
| C3 | 「學習捕捉太主觀，不記了」 | 主觀也比沒有好。下次調查時多一條線索。confidence 分數就是用來標記主觀程度的。 |
```

#### 影響範圍

| 動作 | 檔案 |
|------|------|
| 新增 | `references/anti-rationalizations.md` |

---

### 1.4 三層邊界

#### references/boundaries.md

```markdown
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
```

#### 影響範圍

| 動作 | 檔案 |
|------|------|
| 新增 | `references/boundaries.md` |

---

## Phase 2：修復紀律 + 結案強化（P1）

### 2.1 bug-fix Skill

#### SKILL.md 規格

```markdown
---
name: bug-fix
description: Bug 修復紀律 — 鐵律檢查（根因確認才能修）、修復建議、迴歸測試產出、gstack browse 驗證。當使用者提到「bug-fix」、「修 bug」、「修復」、「fix bug」時觸發此 Skill。
---

# bug-fix — 修復紀律

修復 Bug 前確認根因已記錄，修復後產出迴歸測試並驗證，確保修復品質。

---

## 鐵律

> **根因分析必須有內容，才能開始修復。**
> 根因分析空白 = 還沒調查完 = 不知道要修什麼。

---

## 紀律護欄

> **反合理化**：執行前閱讀 `references/anti-rationalizations.md` 的「通用」和「bug-fix 專用」段落。
> **動作邊界**：遵循 `references/boundaries.md` 的「bug-fix」段落。

---

## 使用方式

```
/bug-fix                  # 標準修復流程
/bug-fix --skip-test      # 跳過迴歸測試（僅限無法測試的場景）
/bug-fix --verify-only    # 只驗證（已修復，只要驗證 + 產出測試）
```

---

## 流程

### 1. 定位目標 Bug

與 `/bug-update` 相同邏輯。

### 2. 鐵律檢查

讀取 Notion 頁面「根因分析」區塊：

- **有內容** → 繼續
- **空白** → 🔴 BLOCK

```
⚠️ 根因分析尚未填寫。

修復前必須確認根因，否則無法確定修的是對的地方。
  • /bug-investigate — AI 協助調查根因
  • 手動填寫 Notion 頁面的「根因分析」區塊後再回來

鐵律：沒有根因確認，不能開始修復。
```

### 3. 修復建議

AI 根據 Notion 頁面的根因分析，產出修復建議：

```
根據根因分析，建議修復方向：

📍 問題檔案：PushService.java:235
🔧 修復建議：
  1. 在 getAccessToken() 的 retry 邏輯中加入 503 狀態碼的處理
  2. retry 次數從 1 次增加到 3 次，含 exponential backoff
  3. 加入 accessToken null check（防禦性程式設計）

⚠️ 最小 diff 原則：只修改與根因直接相關的程式碼
```

使用者確認方向後自行修復（或請 AI 修復）。

### 4. 修復後驗證

使用者修復並 commit 後，執行驗證：

#### 4.1 編譯檢查

```bash
# 自動偵測 build 指令
[ -f pom.xml ] && mvn compile -q 2>&1 | tail -5
[ -f build.gradle ] && gradle compileJava 2>&1 | tail -5
```

- 通過 → ✅
- 失敗 → 顯示錯誤，要求修正

#### 4.2 迴歸測試產出

AI 根據根因分析和修復 diff，產出 1 個迴歸測試：

```
迴歸測試需滿足：
  1. 重現 bug 的前置條件（模擬觸發 bug 的狀態）
  2. 執行觸發 bug 的操作
  3. 斷言正確行為（不是「不拋異常」，是「回傳正確結果」）
  4. 包含 attribution 註解：
     // Regression: {Bug 標題}
     // Root cause: {根因摘要}
     // Date: {YYYY-MM-DD}
```

讀取專案現有測試風格（命名、框架、assertion style），產出風格一致的測試。

```bash
# 執行迴歸測試
mvn test -pl {module} -Dtest={TestClass} 2>&1 | tail -20
```

- 通過 → ✅ commit 測試：`git add {test-file} && git commit -m "test: 迴歸測試 — {bug 摘要}"`
- 失敗 → 修正一次，仍失敗 → 標記為 WARN，不阻擋

#### 4.3 UI 驗證（若為前端相關 bug 且 gstack 可用）

```bash
B="$HOME/.claude/skills/gstack/browse/dist/browse"
if [ -x "$B" ]; then
  echo "GSTACK_AVAILABLE=true"
fi
```

若 gstack 可用且 bug 涉及 UI：

```bash
$B goto <affected-url>
$B snapshot -i
# 操作重現步驟
$B click @eN
$B snapshot -D
$B screenshot .spec/{slug}/screenshots/bugfix-{N}-after.png
$B console --errors
```

#### 4.4 API 驗證（若為 API 相關 bug）

```bash
curl -s "http://localhost:8080/api/xxx" -H "Cookie: <cookie>" | head -50
```

檢查 HTTP 狀態碼 + 回應 body。

### 5. 驗證結果寫入 Notion

更新 Notion 頁面「驗證」區塊：

```markdown
## 🧪 驗證

- [x] 本地測試通過（{日期}）
  - 編譯：✅ 通過
  - 迴歸測試：✅ {TestClass} 通過（commit: {hash}）
  - UI 驗證：✅ 截圖確認（{截圖路徑}）
- [ ] UAT 驗證通過
- [ ] 正式環境確認
- [ ] 通報者確認問題已解決
```

### 6. 回傳結果

```
Bug 修復驗證完成！

📍 修復檔案：{N} 個
🧪 迴歸測試：{TestClass}（✅ 通過）
📸 UI 驗證：{✅ / ⏭️ 跳過}
🔗 Notion：{頁面連結}

後續：
  • /bug-close — 結案並同步知識庫
  • 部署到 UAT 後在 Notion 勾選「UAT 驗證通過」
```
```

#### 影響範圍

| 動作 | 檔案 |
|------|------|
| 新增 | `skills/bug-fix/SKILL.md` |
| 修改 | `.claude-plugin/plugin.json` — skills 陣列新增 |

---

### 2.2 bug-close 強化

#### 新增步驟 2.5：退出驗證門檻

插入在現有步驟 2（搜尋 Bug 條目）和步驟 3（互動式補充）之間：

```markdown
### 2.5 退出驗證門檻

| # | 檢查項 | 驗證方式 | 失敗處理 |
|---|--------|---------|---------|
| C1 | 根因分析已填寫 | Notion 頁面「根因分析」區塊非空 | WARN：提醒補填，允許繼續但狀態強制為「測試中」 |
| C2 | 修復 commit 存在 | `git log --oneline -10` 中有相關 commit | BLOCK：必須先 commit |
| C3 | 迴歸測試存在 | grep test 目錄中含 "Regression: {bug 相關關鍵字}" | WARN：建議用 /bug-fix 產出 |
| C4 | 驗證項目至少一項勾選 | Notion 頁面 checkbox 狀態 | WARN：提醒驗證 |

驗證結果顯示：

```
退出驗證：
  ✅ C1 根因分析已填寫
  ✅ C2 修復 commit 存在（abc1234）
  ⚠️  C3 無迴歸測試
  ⚠️  C4 驗證項目未勾選

結論：可結案，建議處理 C3 和 C4
```

若 C1 為 WARN → 目標狀態選項中移除「已完成」，只能選「測試中」。
```

#### 新增步驟 6.5：學習捕捉

插入在現有步驟 6（知識庫同步）之後：

```markdown
### 6.5 學習捕捉

AI 分析本次 bug 的根因、修復和調查過程，判斷是否有可複用的洞察。

#### 學習類型

| 類型 | 說明 | 範例 |
|------|------|------|
| pattern | 可複用的 bug 模式 | 「此專案的 token 過期 bug 常發生在推播模組」 |
| pitfall | 應避免的陷阱 | 「LINE API 的 503 需要特別處理，不能只處理 401」 |
| architecture | 架構層面的洞察 | 「PushService 和 TokenService 的耦合度太高」 |
| environment | 環境相關的知識 | 「正式環境的 LINE API rate limit 是 100 req/min」 |

#### 學習格式

寫入 `~/.claude-company/bug-workflow/learnings/{project-slug}.jsonl`：

```json
{
  "date": "2026-04-24",
  "skill": "bug-close",
  "bug_title": "推播排程發送失敗",
  "root_cause": "LINE API refresh 回傳 503 未處理",
  "pattern": "third-party-api",
  "type": "pitfall",
  "insight": "LINE API 的 refresh token 端點偶爾回傳 503，retry 邏輯必須涵蓋 503 且加入 exponential backoff",
  "confidence": 9,
  "files": ["PushService.java"],
  "notion_url": "https://www.notion.so/xxx"
}
```

#### 自動 vs 手動

AI 自動判斷是否有學習價值：
- **有明確洞察** → 自動寫入，在結案訊息中顯示「學習已捕捉：{insight}」
- **不確定** → 詢問使用者：「這次 bug 有什麼值得記下來的嗎？」
- **太泛/太明顯** → 不記錄（如「要注意 null check」太泛，不記）

#### 學習目錄建立

```bash
mkdir -p ~/.claude-company/bug-workflow/learnings
```

若目錄不存在，首次使用時自動建立。
```

#### 影響範圍

| 動作 | 檔案 |
|------|------|
| 修改 | `skills/bug-close/SKILL.md` — 新增步驟 2.5 和 6.5 |

---

## Phase 3：起點優化 + 學習系統（P2）

### 3.1 bug-start 初始證據收集

#### 新增步驟 6.5：初始證據收集

在現有步驟 6（填入頁面模板）之後，新增自動證據收集：

```markdown
### 6.5 初始證據收集（自動，不需使用者介入）

建立 Notion 頁面後，自動收集環境資訊寫入「調查過程」區塊。

#### 收集項目

1. **最近 commit**：
   ```bash
   git log --oneline -5
   ```
   寫入「調查過程 > 最近變更」

2. **當前環境狀態**：
   ```bash
   git branch --show-current
   git status --short
   ```
   寫入「調查過程 > 環境狀態」

3. **知識庫快速搜尋**：
   用 bug 標題關鍵字搜尋 Notion Bug 知識庫
   若有相似案例 → 寫入「調查過程 > 歷史參考」
   格式：「[{日期}] {類似 bug 標題} — 根因：{摘要}」

4. **學習快速搜尋**：
   ```bash
   LEARN_FILE="$HOME/.claude-company/bug-workflow/learnings/{project-slug}.jsonl"
   [ -f "$LEARN_FILE" ] && grep -i "<keywords>" "$LEARN_FILE" | tail -3
   ```
   若有匹配 → 寫入「調查過程 > 歷史學習」

#### 寫入格式

```markdown
### [HH:mm] 初始環境快照

**最近 5 筆 commit**：
- abc1234 fix: 修正推播排程的 cron 表達式
- def5678 feat: 新增推播統計 API
- ...

**環境狀態**：
- 分支：fix/push-schedule-failure
- 未提交變更：2 個檔案

**歷史參考**：
- [2026-02-15] 推播 token 過期未更新 — 根因：refresh 機制未觸發

**歷史學習**：
- LINE API 的 refresh token 端點偶爾回傳 503（confidence 9/10，2026-04-20）
```

#### 不阻擋流程

任何收集步驟失敗（如知識庫未設定、不在 Git repo 中）都靜默跳過，不影響 bug-start 的主流程。
```

#### 影響範圍

| 動作 | 檔案 |
|------|------|
| 修改 | `skills/bug-start/SKILL.md` — 新增步驟 6.5 |

---

### 3.2 學習系統 Schema

#### references/learnings-schema.md

```markdown
# Bug 學習系統

## 儲存位置

```
~/.claude-company/bug-workflow/learnings/
├── {project-slug-1}.jsonl    # 專案 A 的學習
├── {project-slug-2}.jsonl    # 專案 B 的學習
└── ...
```

project-slug 來自 Git Repo 識別碼（`/` 替換為 `-`）。

## JSONL 格式

每行一筆 JSON：

```json
{
  "date": "2026-04-24",
  "skill": "bug-close",
  "bug_title": "推播排程發送失敗",
  "root_cause": "LINE API refresh 回傳 503 未處理",
  "pattern": "third-party-api",
  "type": "pitfall",
  "insight": "LINE API 的 refresh token 端點偶爾回傳 503",
  "confidence": 9,
  "files": ["PushService.java"],
  "notion_url": "https://www.notion.so/xxx"
}
```

## 欄位定義

| 欄位 | 必要 | 說明 |
|------|:---:|------|
| date | ✅ | 學習日期 YYYY-MM-DD |
| skill | ✅ | 來源 Skill（bug-close / bug-investigate） |
| bug_title | ✅ | Bug 標題 |
| root_cause | ✅ | 根因摘要 |
| pattern | ✅ | 匹配的 bug 模式（npe / sql / third-party-api / concurrency / config / cache / frontend） |
| type | ✅ | 學習類型（pattern / pitfall / architecture / environment） |
| insight | ✅ | 可複用的洞察（一句話） |
| confidence | ✅ | 信心度 1-10（10=確認的事實，5=推論，1=猜測） |
| files | ✅ | 相關檔案路徑（用於過時偵測：檔案刪除時標記 stale） |
| notion_url | 選填 | Notion 頁面連結（可追溯原始 bug） |

## 搜尋邏輯（bug-investigate 使用）

### 基本搜尋

```bash
LEARN_FILE="$HOME/.claude-company/bug-workflow/learnings/{project-slug}.jsonl"
grep -i "<keyword>" "$LEARN_FILE" | tail -10
```

### 進階搜尋（AI 執行）

1. 從 bug 描述和 stacktrace 擷取關鍵字
2. grep 搜尋 `.jsonl`，取得候選學習
3. AI 判斷相關性，過濾 false positive
4. 檢查 files 欄位的檔案是否仍存在（過時偵測）
5. 按 confidence 降序排列，取前 5 筆

### 過時偵測

```bash
for file in $(echo "$learning" | jq -r '.files[]'); do
  [ ! -f "$file" ] && echo "STALE: $file"
done
```

若所有 files 都不存在 → 標記為可能過時，顯示時加 `⚠️ 檔案已不存在，可能過時` 提示。

## 寫入時機

| Skill | 何時寫入 | 條件 |
|-------|---------|------|
| bug-close | 步驟 6.5 | AI 判斷有學習價值 |
| bug-investigate | Phase 4 根因確認後 | 根因涉及非顯而易見的知識 |

## 容量管理

- 每個專案的 `.jsonl` 不主動清理
- 若超過 500 行 → 在搜尋時提示使用者「學習檔案較大，建議定期檢視」
- 未來可考慮依 confidence 和 date 自動淘汰
```

#### 影響範圍

| 動作 | 檔案 |
|------|------|
| 新增 | `references/learnings-schema.md` |

---

## 完整影響檔案清單

### 新增檔案

| 檔案 | Phase | 說明 |
|------|-------|------|
| `skills/bug-investigate/SKILL.md` | Phase 1 | 假說驅動根因調查 |
| `references/bug-patterns.md` | Phase 1 | 已知 bug 模式表（7 種模式） |
| `references/anti-rationalizations.md` | Phase 1 | 反合理化表（通用 + 4 個 skill 專用） |
| `references/boundaries.md` | Phase 1 | 三層邊界（4 個 skill） |
| `skills/bug-fix/SKILL.md` | Phase 2 | 修復紀律（鐵律 + 迴歸測試 + 驗證） |
| `references/learnings-schema.md` | Phase 3 | 學習系統格式定義 |

### 修改檔案

| 檔案 | Phase | 修改內容 |
|------|-------|---------|
| `.claude-plugin/plugin.json` | Phase 1-2 | skills 陣列新增 bug-investigate 和 bug-fix |
| `skills/bug-close/SKILL.md` | Phase 2 | 新增步驟 2.5 退出驗證 + 步驟 6.5 學習捕捉 |
| `skills/bug-start/SKILL.md` | Phase 3 | 新增步驟 6.5 初始證據收集 |

### 不修改（但有關聯）

| 檔案 | 說明 |
|------|------|
| `skills/bug-update/SKILL.md` | 保持不變，bug-investigate 和 bug-update 互補 |
| `skills/bug-setup/SKILL.md` | 不修改，learnings 目錄由首次寫入時自動建立 |
| `references/prerequisites.md` | 不修改，新 Skill 遵循同樣的前置檢查 |
| `references/db-templates.md` | 不修改，不需要新增 Notion 欄位 |

---

## plugin.json 修改

```json
{
  "name": "bug-workflow",
  "version": "3.5.0",
  "skills": [
    "./skills/bug-setup",
    "./skills/bug-start",
    "./skills/bug-investigate",
    "./skills/bug-update",
    "./skills/bug-fix",
    "./skills/bug-close",
    "./skills/project-add"
  ]
}
```

版本升至 3.5.0，skills 陣列中 bug-investigate 放在 bug-start 後（生命週期順序），bug-fix 放在 bug-update 後。

---

## 驗收條件

### Phase 1（P0）

- [ ] `skills/bug-investigate/SKILL.md` 存在，含五階段流程（證據收集 → 模式比對 → 假說驗證 → 根因確認 → 調查報告）
- [ ] bug-investigate 的 Phase 1 遵循 RTK 規範（log 讀取用 Read tool 或 rtk proxy）
- [ ] bug-investigate 的 Phase 2 引用 `references/bug-patterns.md` 的 7 種模式
- [ ] bug-investigate 的 Phase 3 實作 3-Strike 升級規則
- [ ] bug-investigate 的 Phase 1 包含知識庫搜尋和本地學習搜尋
- [ ] `references/bug-patterns.md` 存在，含 7 種已知 bug 模式
- [ ] `references/anti-rationalizations.md` 存在，含通用 + investigate + fix + close + update 共 5 段
- [ ] `references/boundaries.md` 存在，含 investigate + fix + close + update 共 4 段
- [ ] plugin.json 的 skills 陣列含 bug-investigate

### Phase 2（P1）

- [ ] `skills/bug-fix/SKILL.md` 存在，含鐵律檢查 + 修復建議 + 迴歸測試 + 驗證
- [ ] bug-fix 的鐵律檢查：根因分析空白時 BLOCK，不允許繼續
- [ ] bug-fix 的迴歸測試產出風格與專案現有測試一致
- [ ] bug-fix 偵測 gstack browse 可用性，前端 bug 時自動進行 UI 驗證
- [ ] bug-close 含步驟 2.5 退出驗證門檻（4 項檢查，BLOCK/WARN 分級）
- [ ] bug-close 含步驟 6.5 學習捕捉（寫入 learnings JSONL）
- [ ] bug-close 的 C1 WARN 時，目標狀態不允許選「已完成」
- [ ] plugin.json 的 skills 陣列含 bug-fix

### Phase 3（P2）

- [ ] bug-start 含步驟 6.5 初始證據收集（commit + 環境 + 知識庫 + 學習）
- [ ] bug-start 的初始證據收集任何步驟失敗都不阻擋主流程
- [ ] `references/learnings-schema.md` 存在，定義 JSONL 格式和搜尋邏輯
- [ ] 學習搜尋含過時偵測（檔案不存在時標記 ⚠️）
- [ ] learnings 目錄由首次寫入時自動建立

---

## 判斷

### 任務屬性
- TASK_TYPE: feature
- CHANGE_SCOPE: full

### 技術需求
- FRONTEND_REQUIRED: false
- FRONTEND_TECH: 無
- DB_REQUIRED: false
- DB_TABLES: []
- NEW_API: false
- EXISTING_API_CHANGE: false
