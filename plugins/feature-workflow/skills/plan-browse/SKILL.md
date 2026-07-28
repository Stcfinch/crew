---
name: plan-browse
description: 瀏覽與探索已有的 .spec/ 規劃文件 —— 深度閱讀、跨任務比較、模式搜尋。當使用者提到 /plan-browse、「瀏覽 .spec 規劃」、「看之前的規劃設計」時觸發此 Skill。
---

# plan-browse — 規劃瀏覽器（零 Notion 呼叫）

深度瀏覽 `.spec/` 目錄中的規劃。不只是列出任務（那是 `/plan-status` 的工作），而是**讀取、理解、比較、搜尋**設計內容。

> 一個任務的規劃只有一份文件：`.spec/{slug}/plan.md`（六章節）＋ `deploy.sql`（唯一 SQL 事實來源）。
> 流程階段一律唯讀 `.spec/{slug}/state.json`（**只讀，不寫**）。本 skill 全程唯讀，不改任何檔。

> **v1 舊任務**：`.spec/{slug}/plan.md` 不存在 → 這是 v1 結構，依
> `../../references/legacy-v1.md` 的相容模式執行，並在開頭提示一次。
> 過渡期限定，到期本段連同該檔一併刪除。
---

## 使用方式

```
/plan-browse                         # 互動式瀏覽（列出所有規劃，選擇後深入）
/plan-browse <slug>                  # 深度閱讀指定任務的所有設計文件
/plan-browse --compare <slug1> <slug2>  # 比較兩個任務的設計
/plan-browse --search <關鍵字>        # 跨任務搜尋設計內容
/plan-browse --patterns              # 分析跨任務的共通模式
/plan-browse --timeline              # 按時間軸瀏覽規劃演進
```

---

## 與 plan-status 的差異

| | `/plan-status` | `/plan-browse` |
|--|----------------|----------------|
| 目的 | 任務管理（狀態、暫停/恢復） | 設計內容探索 |
| 深度 | 列出名稱、狀態、分支 | 讀取並摘要 plan.md 各章節內容 |
| 比較 | 不支援 | 支援跨任務比較 |
| 搜尋 | 不支援 | 支援關鍵字搜尋 |
| 模式 | 不支援 | 分析共通設計模式 |

---

## 流程

### 模式 1：互動式瀏覽（無參數）

1. 用 `crew-state.py list --all --format json` 取任務清單（`slug`／`name`／`type`／`phase`／`next` 等），再**只讀每個任務 plan.md 的 frontmatter 與標題下那句需求摘要**（🔴 不讀六章節全文，避免任務數多時 token 成本過高）
2. 呈現豐富的總覽（不只是名稱和狀態）：每個任務附一句話摘要 ＋ 階段 ＋ `deploy.sql` 是否存在；章節細節留待深度閱讀時再讀
3. 輸入編號深入閱讀（進入模式 2 才讀 plan.md 全文），或使用 `--compare 1 2` 比較兩個規劃、`--search <關鍵字>` 搜尋設計內容

輸出範本見 `references/browse-examples.md`（相對 SKILL.md 為 `../../references/`）。

### 模式 2：深度閱讀（指定 slug）

讀 `.spec/{slug}/plan.md` 全文（六章節）＋ `deploy.sql`（若存在）＋ 唯讀 `state.json`（階段、步驟、`results`、`deploy` 進度），逐章節產出結構化摘要，並在最後提供「進入探索討論／比較模式／回到 `/plan spec|db|arch` 補規劃」等後續操作選項。

> **錨點不展開**：「指路」節的 `@code:` / `@sql:` 錨點照原樣列出即可。使用者明確追問某個錨點時才去讀它指到的程式碼，不要預先把每個錨點的原始碼撈進摘要（那正是 plan.md 刻意不抄寫的東西）。
> 章節為空（該 pass 還沒跑）則略過該區塊（見「邊界情況」）。

輸出範本見 `references/browse-examples.md`（相對 SKILL.md 為 `../../references/`）。

### 模式 3：比較模式（--compare）

讀取兩個任務的 plan.md ＋ deploy.sql，逐層比較（類型、範圍、驗收條件數、決策數與關鍵取捨、DB 表數量、階段），並列出共通點、差異點、可復用的設計。**比較的是決策與理由**，不是端點數或類別數（那些不在文件裡）。

輸出範本見 `references/browse-examples.md`（相對 SKILL.md 為 `../../references/`）。

### 模式 4：搜尋模式（--search）

跨所有 `.spec/` 目錄搜尋（`grep -rn "<關鍵字>" .spec/ --include="plan.md" --include="*.sql"`），格式化列出命中的 `{slug}/plan.md:{行號}` 與上下文摘錄，並標注相關任務與共通模式。`state.json` 不納入搜尋（機器狀態不是設計內容）。

輸出範本見 `references/browse-examples.md`（相對 SKILL.md 為 `../../references/`）。

### 模式 5：模式分析（--patterns）

分析所有 plan.md「決策紀錄」「已知取捨與風險」「指路」三節的共通模式：反覆出現的決策取向、DB 設計慣例、被指向最多次的既有元件，各附出現次數與相關任務列表。

輸出範本見 `references/browse-examples.md`（相對 SKILL.md 為 `../../references/`）。

### 模式 6：時間軸（--timeline）

按時間順序展示規劃演進，樹狀列出每個任務的建立日期、階段，以及底下各流程步驟的完成時間點（唯讀 `state.json` 的 `created` 與 `steps.{step}.at`，🔴 不要用檔案 mtime 猜）。

輸出範本見 `references/browse-examples.md`（相對 SKILL.md 為 `../../references/`）。

---

## 與其他指令的銜接

瀏覽後使用者可能想：

| 意圖 | 建議指令 |
|------|---------|
| 「這個設計有問題，想討論一下」 | `/plan-explore <slug>` |
| 「想修改目標／驗收條件」 | `/plan spec`（會進入規格確認迴圈） |
| 「想重做 DB／架構設計」 | `/plan db` 或 `/plan arch` |
| 「文件跟程式碼對不上了」 | `/plan-drift` |
| 「這個可以開始寫了」 | `/plan-build` |
| 「想建立類似的新任務」 | `/plan-start` |
| 「暫停這個任務」 | `/plan-status --park <slug>` |

---

## 何時不用

- 開瀏覽器看網站 → claude-in-chrome / playwright
- 看任務清單與狀態 → `/plan-status`
- 要推薦下一步 → `/plan-next`
- 產出新規劃 → `/plan`（或 `/plan spec|db|arch` 單跑）
- 檢查 plan.md 錨點與程式碼是否漂移 → `/plan-drift`

---

## Gotchas

- **不要修改任何檔**：plan-browse 是唯讀模式 —— 不 Edit plan.md、不呼叫 `crew-state.py` 的任何寫入子命令（`set`／`unit`／`result`／`init`…）。使用者想修改就引導到對應的 plan-* 指令或 `/plan-explore`
- **大量規劃時的效能**：如果 `.spec/` 下有超過 20 個目錄，互動式瀏覽只顯示最近 10 個（按 `state.json` 的 `updated` 排序），並提示使用 `--search` 或 `--timeline` 瀏覽全部
- **摘要品質**：深度閱讀的摘要應忠於原文，不要添加原文沒有的推測。plan.md 刻意不寫的東西（端點、欄位、類別）就是不在裡面，🔴 **不要腦補補齊**
- **決策史不要壓縮掉**：`D-7 取代 D-3` 這種 supersede 條目要連同被取代的舊條目一起呈現 —— 決策為什麼改變正是這份文件最有價值的部分
- **比較時保持中立**：不自動判定哪個設計「更好」，除非使用者問

---

## 邊界情況

- **`.spec/` 不存在**：提示「還沒有任何規劃，使用 `/plan-start` 建立第一個」
- **`.spec/` 為空**：同上
- **指定的 slug 不存在**：列出可用的 slug 供選擇
- **規劃不完整**（例如只有骨架、六章節都空）：顯示已填的章節，標記空的，並附 `crew-state.py next` 算出的下一步
- **搜尋無結果**：提示「未找到匹配結果」，建議更換關鍵字或使用 `/plan-explore` 探索
- **只有一個規劃**：比較模式不可用，提示改用深度閱讀
- **plan.md frontmatter 損壞**：顯示警告，改用 `state.json` 的 `name`／`type` 補齊，並提示使用者修 frontmatter
- **`state.json` 缺失或壞掉**：提示跑 `crew-state.py rebuild --slug {slug}`（本 skill 唯讀，不代跑），階段資訊標「未知」而非用檔案存在與否猜
