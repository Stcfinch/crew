---
name: plan-browse
description: 瀏覽與探索已有的 .spec/ 規劃文件 —— 深度閱讀、跨任務比較、模式搜尋。當使用者提到 /plan-browse、「瀏覽 .spec 規劃」、「看之前的規劃設計」時觸發此 Skill。
---

# plan-browse — 規劃瀏覽器（零 Notion 呼叫）

深度瀏覽 `.spec/` 目錄中的規劃文件。不只是列出任務（那是 `/plan-status` 的工作），而是**讀取、理解、比較、搜尋**設計內容。

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
| 深度 | 列出名稱、狀態、分支 | 讀取並摘要設計文件內容 |
| 比較 | 不支援 | 支援跨任務比較 |
| 搜尋 | 不支援 | 支援關鍵字搜尋 |
| 模式 | 不支援 | 分析共通設計模式 |

---

## 流程

### 模式 1：互動式瀏覽（無參數）

1. 掃描 `.spec/` 目錄，**只讀每個任務 README.md 的 frontmatter 與首段摘要**（不逐一讀取 spec/db/arch 等設計文件全文，避免任務數多時 token 成本過高）
2. 呈現豐富的總覽（不只是名稱和狀態）：每個任務附一句話摘要與 README frontmatter 揭示的 API/DB/架構重點；frontmatter 未涵蓋的細節留待深度閱讀時再讀
3. 輸入編號深入閱讀（進入模式 2 才讀取該任務所有設計文件全文），或使用 `--compare 1 2` 比較兩個規劃、`--search <關鍵字>` 搜尋設計內容

輸出範本見 `references/browse-examples.md`（相對 SKILL.md 為 `../../references/`）。

### 模式 2：深度閱讀（指定 slug）

讀取 `.spec/{slug}/` 下**所有**設計文件（README/spec/db/arch/log，以及存在時的 verify/review/deploy.sql），逐區塊產出結構化摘要，並在最後提供「進入探索討論／比較模式／回到 plan-spec 或 plan-arch」等後續操作選項。

> 深度閱讀應涵蓋 `.spec/{slug}/` 下實際存在的所有設計文件，不限於 README/spec/db/arch/log 五檔；若某文件不存在則略過該區塊（見「邊界情況」）。

輸出範本見 `references/browse-examples.md`（相對 SKILL.md 為 `../../references/`）。

### 模式 3：比較模式（--compare）

讀取兩個任務的所有設計文件，逐層比較（類型、API 數量、DB 表數量、設計模式、前端需求、複雜度等），並列出共通點、差異點、可復用的設計。

輸出範本見 `references/browse-examples.md`（相對 SKILL.md 為 `../../references/`）。

### 模式 4：搜尋模式（--search）

跨所有 `.spec/` 目錄搜尋設計文件內容（`grep -r "<關鍵字>" .spec/ --include="*.md" --include="*.sql"`），格式化列出命中的檔案位置與上下文摘錄，並標注相關任務與共通模式。

輸出範本見 `references/browse-examples.md`（相對 SKILL.md 為 `../../references/`）。

### 模式 5：模式分析（--patterns）

分析所有規劃中的共通設計模式：API 設計模式、DB 設計模式、架構模式、可復用元件，各附出現次數與相關任務列表。

輸出範本見 `references/browse-examples.md`（相對 SKILL.md 為 `../../references/`）。

### 模式 6：時間軸（--timeline）

按時間順序展示規劃演進，樹狀列出每個任務的建立日期、狀態，以及底下各設計文件的完成時間點。

輸出範本見 `references/browse-examples.md`（相對 SKILL.md 為 `../../references/`）。

---

## 與其他指令的銜接

瀏覽後使用者可能想：

| 意圖 | 建議指令 |
|------|---------|
| 「這個設計有問題，想討論一下」 | `/plan-explore <slug>` |
| 「想修改這個規格書」 | `/plan-spec`（會進入規格確認迴圈） |
| 「這個可以開始寫了」 | `/plan-build` |
| 「想建立類似的新任務」 | `/plan-start` |
| 「暫停這個任務」 | `/plan-status --park <slug>` |

---

## 何時不用

- 開瀏覽器看網站 → claude-in-chrome / playwright
- 看任務清單與狀態 → `/plan-status`
- 要推薦下一步 → `/plan-next`
- 產出新規劃 → `/plan` 或 `/plan-spec`

---

## Gotchas

- **不要修改設計文件**：plan-browse 是唯讀模式。如果使用者想修改，引導到對應的 plan-* 指令或 `/plan-explore`
- **大量規劃時的效能**：如果 `.spec/` 下有超過 20 個目錄，互動式瀏覽只顯示最近 10 個（按修改時間排序），並提示使用 `--search` 或 `--timeline` 瀏覽全部
- **摘要品質**：深度閱讀的摘要應忠於原文，不要添加原文沒有的推測
- **比較時保持中立**：不自動判定哪個設計「更好」，除非使用者問

---

## 邊界情況

- **`.spec/` 不存在**：提示「還沒有任何規劃，使用 `/plan-start` 建立第一個」
- **`.spec/` 為空**：同上
- **指定的 slug 不存在**：列出可用的 slug 供選擇
- **設計文件不完整**（例如只有 README.md 沒有 spec.md）：顯示已有的文件，標記缺少的
- **搜尋無結果**：提示「未找到匹配結果」，建議更換關鍵字或使用 `/plan-explore` 探索
- **只有一個規劃**：比較模式不可用，提示改用深度閱讀
- **README.md frontmatter 損壞**：顯示警告，嘗試從檔案內容推斷資訊
