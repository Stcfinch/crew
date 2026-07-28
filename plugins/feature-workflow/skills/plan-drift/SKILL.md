---
name: plan-drift
description: 檢查並修復 .spec/{slug}/plan.md 的程式碼錨點漂移 —— 機械型自動修、語意型逐條請使用者確認，通過後重新蓋章 verified_at_commit。當使用者提到 /plan-drift、「檢查文件漂移」、「plan.md 錨點失效」時觸發此 Skill。
argument-hint: "[<slug>] [--all] [--fix]"
---

# plan-drift — 文件漂移修復迴路

`plan.md` 只寫「為什麼」，「是什麼」一律用錨點（`@code:path#symbol`、`@sql:deploy.sql#table`）指向程式碼。錨點會隨程式碼變動失效，本 skill 是失效後的修復入口：**偵測交給 script，判斷交給使用者，本 skill 只負責串起來**。

> 紀律護欄：`../../references/discipline-preamble.md`（通用紀律）。

---

## 使用方式

```
/plan-drift             # 檢查當前活躍任務
/plan-drift <slug>      # 檢查指定任務
/plan-drift --all       # 檢查專案內所有任務
/plan-drift --fix       # 檢查並直接套用機械型自動修
```

---

## 流程

### 1. 跑檢查（先不修）

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/check-spec-drift.py" --spec .spec/<slug>/plan.md --format json
# --all 模式：
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/check-spec-drift.py" --all --format json
```

**走哪個步驟看 JSON 內容，不是看 exit code**（INFO 級的 D3 行號位移不影響 exit code，只看 exit 0 會漏掉該修的東西）：

- 有 `autofixable: true` 的項目 → 步驟 2
- 有 `autofixable: false` 的 D1–D6 項目 → 步驟 3
- 兩者皆無 → 步驟 4

exit code 決定的是「**能不能蓋章**」，這點不要自行改判：

| exit | 意義 | 蓋章 |
|------|------|------|
| 0 | 無 FAIL、無 WARN（可能仍有 INFO 待 `--fix`） | 可以 |
| 1 | 有 FAIL；**或** WARN 被 `--strict`／該份 `drift_policy: strict` 升級 | 不可 |
| 2 | 只有 WARN | 需使用者逐筆明示放行 |
| 3 | **環境問題**（非 git 工作區、`verified_at_commit` 不在歷史、檔案讀不到） | 不可 |

- exit 1 時先掃 JSON 的 `level`：**一個 FAIL 都沒有就是 WARN 被升級**（`--strict` 或 `drift_policy: strict`），照步驟 3 處理語意型即可，不要去找不存在的 FAIL。
- exit 3 一律回報「**無法檢查**」＋原因＋script 的「修法：」原文，**絕不可說成漂移**。

JSON 陣列每筆含 `code`／`level`／`spec`／`line`／`anchor`／`detail`／`fix`／`autofixable`。`level` 為 `ENV`（`code` = `E1`）的項目一律歸「無法檢查」；它可能與 FAIL 並存（此時 exit 為 1），所以**每次都要掃有無 ENV 項目**，不能只看 exit code。

### 2. 機械型 → 自動修

判準只有一個：**`autofixable` 為 `true`**（目前是 D1 偵測到 `git -M` 改名、D3 行號位移）。不要用自己記的碼表判斷。

```bash
cp .spec/<slug>/plan.md /tmp/plan-before-fix.md
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/check-spec-drift.py" --spec .spec/<slug>/plan.md --fix
diff /tmp/plan-before-fix.md .spec/<slug>/plan.md
```

用上面的 `diff` 取回實際改動（**不要用 `git diff`**：`.spec/` 預設被 gitignore、plan.md 到 `/plan-close` 才 `git add -f`，`git diff` 會是空的而讓你誤判沒修到）。逐條回報「錨點 X：舊路徑 → 新路徑」「行號提示 L88 → L102」。**沒出現在 `diff` 輸出裡的就不准說已修好。**

### 3. 語意型 → 逐條請使用者確認（不自動改）

`autofixable` 為 `false` 的全部歸這裡（D2 符號不在檔內、D4 hash 不符、D5 `@sql:` 表對不上、D6 文件落後程式碼、D7 缺錨點／缺蓋章）。對每一筆：

1. 讀該錨點指向的程式碼（D6 讀 `detail` 列出的變更檔案），確認符號是**改名**、**刪除**、還是**整個決策已作廢**
2. 提出建議，一次只問一條：

```
🔴 [D2] .spec/login-lock/plan.md:23 `@code:src/.../LoginAttemptService.java#recordFailure`
   檔內找不到 recordFailure。實際看到 recordAttempt(boolean success)（:91）—— 像是改名。
   建議：把錨點改指 #recordAttempt
   [1] 照建議改錨點  [2] 這個決策已作廢 → 改寫「決策紀錄」那一條  [3] 略過（本次不處理）
```

3. 使用者選定後才寫入，且用 Edit 對章節錨點插入／替換單一條目，**禁止整檔改寫 plan.md**

**符號消失常代表決策變了。** 此時該動的是「決策紀錄」章節（用 `D-n [階段] 取代 D-m：…` supersede，不刪舊條目），不是把指標硬改成能通過檢查 —— 硬改指標會讓文件變成「永遠通過但沒人信」的裝飾。這條沒有使用者確認一律不做。

若使用者判定某筆是誤報，可請他選擇逃生閥（**由使用者決定，不要自己塞**）：

- 行內：`<!-- drift-ignore: D2 reason=已改用新介面 -->`（`reason` 必填）
- 整份關閉：plan.md frontmatter 改 `drift_policy: off`（代價：該份文件此後完全不檢查）

### 4. 重新蓋章（只在真的乾淨時）

條件：重跑檢查得到 **exit 0**，或 exit 2 且每筆 WARN 都經使用者明示放行。exit 1 或有 ENV 項目 → **不蓋章**。

```bash
git rev-parse --short HEAD
```

用 Edit 更新 `.spec/<slug>/plan.md` frontmatter 兩個欄位（只改這兩行）：

```yaml
verified_at_commit: 3f2a91c
verified_at: 2026-07-28
```

日期用 `date +%F` 的實際輸出，不要憑印象填。

### 5. 回報

```
🔍 漂移檢查：login-lock（.spec/login-lock/plan.md）

🔧 已自動修（機械型）2 筆
  • L23 錨點路徑 LoginAttemptService.java → service/LoginAttemptService.java（git 改名）
  • L31 行號提示 L88 → L102

📝 已確認修正（語意型）1 筆
  • L45 D-3 標記為由 D-7 取代（決策已變：改走 Redis 計數）

⏭️ 使用者放行的 WARN 1 筆
  • [D6] 錨點檔案自 3f2a91c 後有變更 —— 使用者確認變更不影響決策

✅ 重跑檢查 exit 0 → 已蓋章 verified_at_commit: a91c3f2
```

`--all` 模式逐任務印上述摘要，並在最後給總計；每份任務的蓋章各自獨立判定。

---

## 何時不用

- 要知道下一步做什麼 → /plan-next
- 看任務清單 → /plan-status
- 讀規劃文件內容 → /plan-browse
- 結案（會自己跑同一支 script 當硬關卡）→ /plan-close

---

## Gotchas

- **exit 3 不是漂移**：環境問題代表「這次沒檢查成」，把它說成「文件有漂移」或「檢查通過」都是假資訊。原文照登 script 的「修法：」那行。
- **`drift_policy: off` 的任務是「沒檢查」**：script 會在總結明示未檢查份數，回報時不得寫成「全部通過」。
- **蓋章是承諾，不是儀式**：`verified_at_commit` 只有本 skill 與 `/plan-close` 能寫，且必須在檢查真的乾淨之後。剛改完程式碼就蓋章等於自己給自己蓋合格章。
- **語意型不自動修**：D2/D4/D5/D6 一律逐條問。批次「全部照建議改」等於繞過使用者判斷，禁止提供這個選項。
- **`--fix` 只動 plan.md**：它不會改程式碼。若使用者要的是「把程式碼改回文件寫的樣子」，那是 `/plan-build` 的工作，先問清楚。

---

## 邊界情況

- **找不到 `.spec/*/plan.md`**：script 回 exit 0 並印「找不到任何 plan.md」→ 回報無可檢查對象，提示 `/plan-start`
- **舊版 v1 任務（只有 README.md 沒有 plan.md）**：沒有錨點可檢查，明說「該任務仍是 v1 格式、本次未檢查」，不要當成通過
- **`.spec/` 被 gitignore 且 plan.md 未進 git**：D6 會靜默（無從比對時間先後），這是刻意設計，不是漏檢
- **同一份文件同時有 FAIL 與 ENV**：exit 為 1；兩者都要回報，且照 FAIL 處理流程走，蓋章仍禁止
