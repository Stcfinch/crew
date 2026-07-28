# plan-browse 輸出範本

本檔收錄 `plan-browse` 六種模式各自的完整 ASCII 輸出範本，供實作時對照格式。SKILL.md 只保留各模式的功能簡述。

> 一個任務的規劃只有 `plan.md`（六章節）＋ `deploy.sql`（唯一 SQL 事實來源）；階段與進度唯讀 `state.json`。
> 範本中出現的 `@code:` / `@sql:` 錨點**照原樣呈現**，不要展開成程式碼原文。

## 模式 1：互動式瀏覽（無參數）

只讀每個任務 `plan.md` 的 frontmatter 與標題下那句需求摘要，階段取自 `crew-state.py list`：

```
📚 規劃瀏覽器

找到 {N} 個規劃：

### 1. 🔧 推播標籤查詢（push-tag-query）
   階段：arch | 分支：feature/push-tag-query | deploy.sql：✅ 3 步
   ┌──────────────────────────────────────────────┐
   │ 摘要：新增標籤查詢 API，支援多條件篩選推播對象   │
   │ 驗收條件：4 條 | 決策：D-1…D-7 | 指路：5 個錨點 │
   └──────────────────────────────────────────────┘

### 2. 🐞 SSO 登入異常（sso-login-fix）
   階段：build | 分支：hotfix/sso-login-fix | deploy.sql：❌（DB_REQUIRED=false）
   ┌──────────────────────────────────────────────┐
   │ 摘要：Spring Security 過濾鏈順序導致 SSO 失效   │
   │ 驗收條件：2 條 | 決策：D-1…D-3 | 指路：2 個錨點 │
   └──────────────────────────────────────────────┘

輸入編號深入閱讀，或使用：
  • --compare 1 2  比較兩個規劃
  • --search <關鍵字>  搜尋設計內容
```

## 模式 2：深度閱讀（指定 slug）

讀 `plan.md` 全文 ＋ `deploy.sql` ＋ 唯讀 `state.json`，逐章節產出結構化摘要：

```
📖 深度閱讀：推播標籤查詢（push-tag-query）

═══════════════════════════════════════════════
  📊 流程狀態（state.json，唯讀）
═══════════════════════════════════════════════
  階段：arch｜分支：feature/push-tag-query｜Notion：{有 page_id 才附連結}
  步驟：start ✅  spec ✅  db ✅  arch ✅  build ⬜  security ⬜  verify ⬜  review ⬜  close ⬜
  部署：0 / 3 步已回報

═══════════════════════════════════════════════
  🎯 目標與範圍（crew:goal）
═══════════════════════════════════════════════
  為何做：{原文摘要}
  In Scope：{列出}
  Out of Scope：{列出}

═══════════════════════════════════════════════
  ✅ 驗收條件（crew:ac）
═══════════════════════════════════════════════
  AC-1 {一句話}
  AC-2 {一句話}
  …共 {N} 條，{M} 條已勾選

═══════════════════════════════════════════════
  🧭 決策紀錄（crew:dec，{N} 條）
═══════════════════════════════════════════════
  D-7 [arch] 取代 D-3：{決策}｜理由：{…}
  D-5 [db]  {決策}｜理由：{…}｜否決：{方案}（{否決理由}）
  D-3 [db]  {決策}  ⚠️ 已被 D-7 取代
  …
  （supersede 鏈連同舊條目一起列出 —— 決策為何改變是這份文件最有價值的部分）

═══════════════════════════════════════════════
  ⚖️ 已知取捨與風險（crew:risk）
═══════════════════════════════════════════════
  • {明知的技術債／邊界外情境}

═══════════════════════════════════════════════
  🗺️ 指路（crew:map）
═══════════════════════════════════════════════
  • 資料表：`@sql:deploy.sql#push_tags`
  • 進入點：`@code:src/main/java/com/x/action/PushTagAction.java#query` (L112)
  （錨點照原樣列出；使用者追問某個錨點時才去讀它指到的程式碼）

═══════════════════════════════════════════════
  📋 檢查報告摘要（crew:rep）
═══════════════════════════════════════════════
  • [2026-03-18] review 通過｜🔴0 🟡2
  • [2026-03-18] security 通過｜🔴0 🟡1
  （逐條發現不落檔；完整報告是 .cache/ 一次性暫存）

═══════════════════════════════════════════════
  🚀 部署 SQL（deploy.sql，若存在）
═══════════════════════════════════════════════
  Step 數：3（CREATE TABLE ×2、CREATE INDEX ×1）
  回報進度：0 / 3（state.json 的 deploy 欄位）
  Rollback 段：✅ 有
```

> 章節為空（該 pass 還沒跑）則略過該區塊（見 SKILL.md「邊界情況」）。

深度閱讀後，提供互動選項：

```
後續操作：
  • 「D-5 為什麼否決本機快取？」— 進入探索討論
  • 「跟 XXX 比較一下」— 比較模式
  • 「繼續規劃」— 回到 /plan spec、/plan db 或 /plan arch
  • 「錨點跟程式碼對不上」— /plan-drift
```

## 模式 3：比較模式（--compare）

讀取兩個任務的 plan.md ＋ deploy.sql，逐層比較。比的是**決策與理由**，不是端點數或類別數：

```
⚖️  規劃比較：push-tag-query vs subscription-stats

┌─────────────────┬──────────────────┬───────────────────┐
│ 面向            │ push-tag-query   │ subscription-stats│
├─────────────────┼──────────────────┼───────────────────┤
│ 類型            │ Feature          │ Feature           │
│ 階段            │ arch             │ close             │
│ 驗收條件        │ 4 條             │ 2 條              │
│ 決策數          │ 7（含 1 次 supersede）│ 3            │
│ DB 表數量       │ 2（deploy.sql）  │ 0（查詢既有表）    │
│ 指路錨點        │ 5                │ 2                 │
└─────────────────┴──────────────────┴───────────────────┘

共通的決策取向：
  • 都選擇「先在 Service 層擋，不靠 DB 例外」（D-4 vs D-2）
  • 都把分頁交給既有 PageRequest DTO，沒有自建

差異點：
  • push-tag-query 需要新建表（見 `@sql:deploy.sql#push_tags`），subscription-stats 只查詢
  • push-tag-query 有一次 supersede（D-7 取代 D-3），原因是多節點部署改變了前提
  • subscription-stats 的「已知取捨」明寫不做即時性保證，push-tag-query 沒有這條

可復用的設計：
  • 兩者都指向同一個既有分頁元件：`@code:src/main/java/com/x/common/PageRequest.java`
```

## 模式 4：搜尋模式（--search）

跨所有 `.spec/` 目錄搜尋規劃內容（`state.json` 不納入搜尋 —— 機器狀態不是設計內容）：

```bash
# 只搜 plan.md 與 SQL
grep -rn "<關鍵字>" .spec/ --include="plan.md" --include="*.sql"
```

格式化搜尋結果：

```
🔍 搜尋「RabbitMQ」— 找到 {N} 筆

1. push-tag-query/plan.md:31（決策紀錄）
   「D-5 [arch] 推播改走 RabbitMQ｜理由：5 萬人同時觸發需要背壓｜否決：HTTP 直呼」

2. push-tag-query/plan.md:44（指路）
   「`@code:src/main/java/com/x/push/RabbitMqPushAdapter.java#send`」

3. subscription-notify/plan.md:22（目標與範圍）
   「In Scope：訂閱通知走 RabbitMQ fanout exchange」

相關任務：push-tag-query, subscription-notify
共通模式：兩者都選 RabbitMQ，理由都是「背壓與重試由 MQ 內建」
```

## 模式 5：模式分析（--patterns）

分析所有 plan.md 的「決策紀錄」「已知取捨與風險」「指路」三節：

```
🔬 跨任務設計模式分析

掃描了 {N} 份 plan.md，發現以下模式：

## 反覆出現的決策取向
  • 「驗證放 Service，不靠 DB 例外攔截」：{N} 次（要回可讀的錯誤訊息）
  • 「非同步走 MQ 不走 HTTP 直呼」：{N} 次（都提到背壓與重試）

## DB 設計慣例（從 deploy.sql 與 [db] 決策歸納）
  • 軟刪除一律 `deleted_at` 時間戳：{N} 次
  • 唯一性用複合索引（含 deleted_at）：{N} 次
  • 索引命名：idx_{table}_{column} / uk_{table}_{column}

## 被指最多次的既有元件（指路節錨點統計）
  • `@code:.../common/ApiResult.java` — {N} 個任務指向
  • `@code:.../common/PageRequest.java` — {N} 個任務指向

## 反覆出現的已知風險
  • 「軟刪除資料不清理，表單向成長」：{N} 次 —— 值得開一個共用的歸檔任務
```

## 模式 6：時間軸（--timeline）

按時間順序展示規劃演進。日期一律取 `state.json` 的 `created` 與 `steps.{step}.at`，🔴 不要用檔案 mtime 猜：

```
📅 規劃時間軸

2026-03
├── 03-10 ✅ subscription-stats（close）
│         訂閱統計去重複計算
├── 03-15 ⏸️  data-export（擱置中，擱置時階段 db）
│         資料匯出功能
├── 03-16 🔧 push-tag-query（arch）
│         推播標籤查詢
│         ├── 03-16 spec ✅
│         ├── 03-16 db ✅（deploy.sql 3 步）
│         └── 03-17 arch ✅
└── 03-17 🐞 sso-login-fix（build）
          SSO 登入異常
          ├── 03-17 spec ✅
          └── 03-17 db ⏭️ 跳過（DB_REQUIRED=false）
```
