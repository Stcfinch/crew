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

> 通用紀律見 `references/discipline-preamble.md`。
> 本 skill 專用條目：`anti-rationalizations.md` 「bug-fix 專用」+ `boundaries.md` 「bug-fix」段落。

---

## 設定檔

執行前依序檢查以下路徑，讀取第一個找到的設定檔：
1. `~/.claude-company/bug-workflow-config.md`（公司環境）
2. `~/.claude/bug-workflow-config.md`（個人環境）

若都不存在，提示使用者先執行 `/bug-setup`。

---

## 前置條件

- 已使用 `/bug-start` 建立 Bug 條目（Notion 有「進行中」的 🐞 錯誤）
- 修復程式碼已 commit 或即將 commit

> **前置檢查**：參照 `references/prerequisites.md` 執行完整前置檢查（CLAUDE.md + 設定檔 + 專案註冊）。

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

與 `/bug-update` 相同邏輯：

1. 從設定檔讀取「任務追蹤工具」Data Source ID，精確查詢該資料庫
2. 使用 `notion-search` 搭配 `data_source_url: collection://{任務追蹤工具 Data Source ID}` 搜尋：
   - 狀態為「進行中」
   - 任務類型包含「🐞 錯誤」
3. 同時取得 Git Repo 識別碼（從 `git remote get-url origin` 解析），用於輔助篩選同一專案下的 Bug
4. Git branch 匹配 → 自動選定
5. 多個候選 → 列出選擇

選定後使用 `notion-fetch` 讀取頁面完整內容。

### 1.5 分支檢查

確保修復在正確的分支上進行（依 Git-flow 規定：修改應在 feature branch 提交，再 merge 回 DEV）。

1. 從 Bug Notion 頁面讀取「修復分支」欄位
2. 取得當前分支：`git branch --show-current`
3. 比對：

**修復分支有值 且 ≠ 當前分支**：

```
⚠️ 分支不一致

當前分支：MOM01P2401_DEV
修復分支：feature/qa-log-user-id-statistics

依 Git-flow 規定，修改應在 feature branch 提交，再 merge 回 DEV。

要切換嗎？
  1. 是，切換到 feature/qa-log-user-id-statistics
  2. 否，繼續在當前分支修復
```

- 選 1 → 執行 `git checkout <修復分支>`，繼續流程
- 選 2 → 繼續，不改變分支

**修復分支無值 或 = 當前分支**：跳過，繼續原流程。

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

**重要**：使用 `update_content` 前，必須先 `notion-fetch` 取得現有內容，將新內容附加到現有內容後面再寫回，避免覆蓋。

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

**分支引導**（若當前在 feature branch 且不是 DEV/PRD 分支）：

讀取 feature-workflow 的 `projects/{repo-id}.md` 取得 `dev_branch`。若取得成功，額外顯示：

```
🔀 分支引導：
  目前在 feature/qa-log-user-id-statistics
  修復已 commit，後續請 merge 回 DEV：

  git checkout {dev_branch} && git merge feature/qa-log-user-id-statistics --no-ff

  或使用 /bug-close 時自動引導 merge。
```

若 `dev_branch` 未設定，顯示通用提示：

```
🔀 分支引導：
  目前在 feature branch，記得修復完成後 merge 回開發分支。
```

---

## Gotchas

- **根因分析空白的判斷**：Notion 頁面的「根因分析」區塊可能存在但內容只有模板佔位符（如「待填寫」、空白 bullet）。這種情況也算「空白」，應觸發 BLOCK。判斷標準是：去掉模板佔位符和空白行後，是否有實質內容。
- **最小 diff 原則**：bug-fix 只修改與根因直接相關的程式碼。其他改善（如 code style、重構旁邊的邏輯）應在另一個 commit 完成，否則 revert 時會連帶。
- **迴歸測試風格匹配**：產出的測試檔案要與專案現有測試使用相同的框架（JUnit 5 / TestNG）、assertion library（AssertJ / Hamcrest）、命名風格（`should_xxx_when_yyy` / `testXxxWhenYyy`）。先搜尋 `src/test` 目錄中的現有測試作為範本。
- **--skip-test 的使用場景**：僅限以下情況：環境問題（如無法在本地跑測試）、設定類修復（如改 properties 檔）、純 SQL 修復（如改 DB 資料）。其他場景不應跳過。
- **gstack browse 可用性**：不是所有環境都有安裝 gstack。先偵測 `$HOME/.claude/skills/gstack/browse/dist/browse` 是否存在且可執行，再決定是否進行 UI 驗證。
- **update_content 語意是覆蓋不是附加**：`notion-update-page` 的 `update_content` 對同一區塊寫入時會覆蓋該區塊內容。寫入「驗證」區塊時，必須先 `notion-fetch` 取得現有內容，串接新內容後再寫回。
- **分支檢查是引導不是強制**：Step 1.5 的分支不一致提示是建議性的，使用者可以選擇繼續在當前分支修復。不要因為分支不一致就 BLOCK 整個流程。
- **dev_branch 取得路徑**：分支引導需要讀取 feature-workflow 的 `projects/{repo-id}.md`，但 bug-fix 是 bug-workflow 的 skill。需跨 plugin 讀取設定：先嘗試 `~/.claude-company/feature-workflow/projects/{repo-id}.md`，再嘗試 `~/.claude/feature-workflow/projects/{repo-id}.md`。讀取失敗時顯示通用提示。

---

## 邊界情況

- **設定檔不存在**：提示使用者先執行 `/bug-setup` 完成初始設定
- **根因分析空白**：BLOCK，引導使用者用 `/bug-investigate` 或手動填寫
- **無 commit 可檢查**：若使用者尚未 commit，提示先 commit 修復程式碼再執行 `/bug-fix`
- **編譯失敗**：顯示錯誤訊息，要求使用者修正後重新執行
- **迴歸測試無法產出**：某些修復（如純設定變更）難以寫自動化測試，標記為 WARN 並在 Notion 說明原因
- **gstack 不可用**：跳過 UI 驗證，在 Notion 標記「UI 驗證：⏭️ 跳過（gstack 不可用）」
- **API 驗證服務未啟動**：跳過 API 驗證，在 Notion 標記「API 驗證：⏭️ 跳過（服務未啟動）」
- **--verify-only 模式**：跳過步驟 3（修復建議），直接從步驟 4（修復後驗證）開始
- **diff 過大（> 500 行）**：提示使用者確認是否所有變更都與 bug 修復相關，遵循最小 diff 原則
- **Bug 無「修復分支」欄位**：Step 1.5 跳過分支檢查
- **feature-workflow 未安裝或未設定**：分支引導顯示通用提示，不阻擋流程
