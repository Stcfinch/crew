# plan-browse 輸出範本

本檔收錄 `plan-browse` 六種模式各自的完整 ASCII 輸出範本，供實作時對照格式。SKILL.md 只保留各模式的功能簡述。

## 模式 1：互動式瀏覽（無參數）

```
📚 規劃瀏覽器

找到 {N} 個規劃：

### 1. 🔧 推播標籤查詢（push-tag-query）
   狀態：架構設計 | 分支：feature/push-tag-query
   ┌──────────────────────────────────────────┐
   │ 摘要：新增標籤查詢 API，支援多條件篩選推播對象 │
   │ API：3 個端點（GET/POST/DELETE）           │
   │ DB：2 個新表 + 3 個索引                    │
   │ 架構：Strategy 模式處理不同查詢類型         │
   └──────────────────────────────────────────┘

### 2. 🐞 SSO 登入異常（sso-login-fix）
   狀態：調查中 | 分支：hotfix/sso-login-fix
   ┌──────────────────────────────────────────┐
   │ 摘要：Spring Security 過濾鏈順序導致 SSO 失效 │
   │ 根因：FilterChainProxy 載入順序錯誤          │
   │ 影響範圍：所有 SSO 登入使用者                │
   └──────────────────────────────────────────┘

輸入編號深入閱讀，或使用：
  • --compare 1 2  比較兩個規劃
  • --search <關鍵字>  搜尋設計內容
```

## 模式 2：深度閱讀（指定 slug）

讀取 `.spec/{slug}/` 下**所有**設計文件，產出結構化摘要：

```
📖 深度閱讀：推播標籤查詢（push-tag-query）

═══════════════════════════════════════════════
  📋 需求（README.md）
═══════════════════════════════════════════════
  • 目標：{一句話摘要}
  • 類型：Feature
  • 建立日期：2026-03-16
  • Notion：{URL}

═══════════════════════════════════════════════
  📐 技術規格（spec.md）
═══════════════════════════════════════════════
  範圍：
    ✅ In：{列出}
    ❌ Out：{列出}

  API 端點：
    ┌──────────┬────────────────────┬──────────┐
    │ 方法     │ 路徑               │ 說明     │
    ├──────────┼────────────────────┼──────────┤
    │ GET      │ /api/push/tags     │ 查詢標籤 │
    │ POST     │ /api/push/tags     │ 新增標籤 │
    │ DELETE   │ /api/push/tags/{id}│ 刪除標籤 │
    └──────────┴────────────────────┴──────────┘

  業務規則：{N} 條
  判斷：DB_REQUIRED=true, FRONTEND_REQUIRED=true

═══════════════════════════════════════════════
  🗄️ 資料庫設計（db.md）
═══════════════════════════════════════════════
  表清單：
    • push_tags（主表，{N} 個欄位）
    • push_tag_conditions（條件表，{N} 個欄位）

  關聯：
    push_tags 1──N push_tag_conditions

  索引：{N} 個

═══════════════════════════════════════════════
  🏗️ 架構設計（arch.md）
═══════════════════════════════════════════════
  設計模式：Strategy
  類別清單：{N} 個
  分層：Controller → Service → Repository → Entity

═══════════════════════════════════════════════
  📝 開發日誌（log.md）
═══════════════════════════════════════════════
  • [2026-03-16] plan-spec 完成
  • [2026-03-16] plan-db 完成
  • [2026-03-17] plan-arch 完成

═══════════════════════════════════════════════
  ✅ 驗收驗證（verify.md，若存在）
═══════════════════════════════════════════════
  Health Score：{分數}
  通過/失敗：{N} / {M} 條驗收條件

═══════════════════════════════════════════════
  🔍 程式碼審查（review.md，若存在）
═══════════════════════════════════════════════
  Reviewer 發現：{N} 筆（高/中/低優先各 {N} 筆）

═══════════════════════════════════════════════
  🚀 部署 SQL（deploy.sql，若存在）
═══════════════════════════════════════════════
  SQL 筆數：{N}
  執行狀態：{未執行 / 已執行}
```

> 深度閱讀應涵蓋 `.spec/{slug}/` 下實際存在的所有設計文件，不限於 README/spec/db/arch/log 五檔；若某文件不存在則略過該區塊（見 SKILL.md「邊界情況」）。

深度閱讀後，提供互動選項：

```
後續操作：
  • 「這個 API 設計為什麼選 GET 而不是 POST？」— 進入探索討論
  • 「跟 XXX 比較一下」— 比較模式
  • 「繼續規劃」— 回到 /plan-spec 或 /plan-arch
```

## 模式 3：比較模式（--compare）

讀取兩個任務的所有設計文件，逐層比較：

```
⚖️  規劃比較：push-tag-query vs subscription-stats

┌─────────────────┬──────────────────┬──────────────────┐
│ 面向            │ push-tag-query   │ subscription-stats│
├─────────────────┼──────────────────┼──────────────────┤
│ 類型            │ Feature          │ Feature           │
│ API 數量        │ 3                │ 2                 │
│ DB 表數量       │ 2                │ 0（查詢既有表）    │
│ 設計模式        │ Strategy         │ Template Method   │
│ 前端需求        │ JSP              │ JSP               │
│ 複雜度          │ 中               │ 低                │
└─────────────────┴──────────────────┴──────────────────┘

共通點：
  • 都使用 Spring Data JPA Repository
  • 都有分頁查詢需求
  • Controller 都在 com.intumit.action 套件

差異點：
  • push-tag-query 需要新建表，subscription-stats 只查詢
  • push-tag-query 用 Strategy 模式，因為查詢條件多樣
  • subscription-stats 較簡單，可直接參考既有 Controller 模式

可復用的設計：
  • 分頁查詢的 DTO 結構可共用
  • Repository 的自訂查詢寫法一致
```

## 模式 4：搜尋模式（--search）

跨所有 `.spec/` 目錄搜尋設計文件內容：

```bash
# 在所有 .spec/ 下的 .md 與 .sql 檔案中搜尋
grep -r "<關鍵字>" .spec/ --include="*.md" --include="*.sql"
```

格式化搜尋結果：

```
🔍 搜尋「RabbitMQ」— 找到 {N} 筆

1. push-tag-query/spec.md:42
   「...透過 RabbitMQ 發送推播訊息到目標通道...」

2. push-tag-query/arch.md:78
   「...RabbitMqPushAdapter 實作非同步推播...」

3. subscription-notify/spec.md:15
   「...訂閱通知使用 RabbitMQ fanout exchange...」

相關任務：push-tag-query, subscription-notify
共通模式：兩者都使用 Spring AMQP + RabbitTemplate
```

## 模式 5：模式分析（--patterns）

分析所有規劃中的共通設計模式：

```
🔬 跨任務設計模式分析

掃描了 {N} 個規劃，發現以下模式：

## API 設計模式
  • RESTful CRUD：出現 {N} 次（push-tag-query, ...）
  • 查詢 + 匯出：出現 {N} 次（subscription-stats, ...）

## DB 設計模式
  • 主表 + 明細表：出現 {N} 次
  • 使用 NVARCHAR：所有任務一致
  • 索引命名：idx_{table}_{column}

## 架構模式
  • Strategy：{N} 次（多條件查詢場景）
  • Template Method：{N} 次（固定流程、可變步驟）
  • Adapter：{N} 次（外部 API 整合）

## 可復用元件
  • 分頁 DTO（PageRequest/PageResponse）— 已在 3 個任務出現
  • 通用 API Response 格式 — 所有任務一致
  • Solr 查詢工具類 — 2 個任務使用
```

## 模式 6：時間軸（--timeline）

按時間順序展示規劃演進：

```
📅 規劃時間軸

2026-03
├── 03-10 ✅ subscription-stats（已完成）
│         訂閱統計去重複計算
├── 03-15 ⏸️  data-export（暫停中）
│         資料匯出功能
├── 03-16 🔧 push-tag-query（架構設計）
│         推播標籤查詢
│         ├── 03-16 spec.md 完成
│         ├── 03-16 db.md 完成
│         └── 03-17 arch.md 完成
└── 03-17 🐞 sso-login-fix（調查中）
          SSO 登入異常
```
