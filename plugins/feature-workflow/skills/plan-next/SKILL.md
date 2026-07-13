---
name: plan-next
description: 智慧推薦當前任務的下一步指令。讀取 .spec/{slug}/ 既有檔案、Git 狀態、verify.md 結果，判斷流程位置並建議下一個 /plan-* 或 /bug-* 指令。當使用者提到「plan-next」、「下一步」、「接下來」、「next step」、「該做什麼」、「what's next」時觸發此 Skill。
---

# plan-next — 智慧推薦下一步

讀取當前任務 `.spec/{slug}/` 的既有檔案、Git 狀態、verify.md 結果，
判斷流程目前在哪一步，並建議下一個指令與理由。

省去使用者記得「plan-start → spec → db → arch → build → security → verify → review → close」
完整 9 步流程的負擔，特別適合新使用者或久未碰專案的回鍋。

---

## 紀律護欄

> 通用紀律見 plugin 根目錄 `references/discipline-preamble.md`（相對 SKILL.md 為 `../../references/`）。
> 本 skill 專用條目：plugin 根目錄 `references/anti-rationalizations.md`「plan-next 專用」+ `references/boundaries.md`「plan-next」段落。

---

## 使用方式

```
/plan-next               # 推薦當前活躍任務的下一步
/plan-next <slug>        # 明確指定任務 slug
/plan-next --all         # 列出所有活躍任務 + 各自下一步
```

---

## 流程

### 1. 定位活躍任務

與 `/plan` 相同邏輯：

1. Git branch 匹配 → 自動選定
2. 多個活躍任務 → 列出選擇
3. 無活躍任務 → 推薦 `/plan-start <任務名>`

### 2. 掃描 `.spec/{slug}/` 既有檔案

依序檢查：

| 檔案 | 代表意義 |
|------|---------|
| `README.md` | plan-start 完成 |
| `spec.md` | plan-spec 完成（含「判斷」區塊） |
| `db.md` | plan-db 完成 |
| `db.sql` / `deploy.sql` | DB 設計含 SQL 產物 |
| `arch.md` | plan-arch 完成 |
| `files.md` | plan-build 完成 |
| `verify.md` | plan-verify 完成（解析狀態） |
| `review.md` | plan-review 完成 |
| `security.md` | plan-security 完成 |

### 3. 解析 verify.md 狀態（若存在）

讀取 `verify.md` 的「## 摘要」或「## 統計」段落：

- 「全部 PASS」「✅ 全部通過」→ 視為 PASS
- 含 `❌ FAIL` 項目 → 視為 FAIL
- 含 `⚠️ WARN` 項目（無 FAIL）→ 視為 WARN

### 4. 推薦邏輯

按以下決策表推薦下一步（**第一個匹配的規則勝出**）：

| 條件 | 推薦 | 理由 |
|------|------|------|
| 無 `.spec/{slug}/` | `/plan-start <任務名>` | 還沒開始 |
| README.md 但無 spec.md | `/plan-spec` | 需先產出技術規格 |
| spec.md 但無 db.md（且 spec 判斷區塊 DB_REQUIRED ≠ false） | `/plan-db` | DB 設計缺 |
| spec.md 但無 db.md（DB_REQUIRED = false） | `/plan-arch` | 不需 DB，跳過 |
| db.md 但無 arch.md | `/plan-arch` | 架構設計缺 |
| arch.md 但無 files.md | `/plan-build` | 可以開始產 code |
| files.md 但無 security.md | `/plan-security` | 安全掃描缺 |
| security.md 但無 verify.md | `/plan-verify` | 驗收驗證缺 |
| verify.md = FAIL | `/plan-build`（修正） or `/plan-verify --recheck` | 有失敗項目要處理 |
| verify.md = WARN | `/plan-verify --recheck` 或 `/plan-review` | WARN 可選擇處理或繼續 |
| verify.md = PASS 但無 review.md | `/plan-review` | 程式碼審查缺 |
| review.md 有 🔴 嚴重發現 | `/plan-build`（依審查修正） | 審查發現嚴重問題 |
| review.md 通過 | `/plan-close` | 全部完成可結案 |
| 已 `/plan-close` 完成 | 無建議（任務結束） | — |

### 5. 額外檢查（補強建議）

獨立於主決策，這些情況附加為「順帶建議」：

| 條件 | 順帶建議 |
|------|---------|
| 當前 branch ≠ README.md 中記錄的開發分支 | 提示切換分支 `git checkout <branch>` |
| CLAUDE.md 不存在 | 提示 `/init` |
| 專案未在 `projects/` 註冊 | 提示 `/project-add` |
| `.spec/{slug}/deploy-checklist.md` 存在且有未勾選項目 | 提示「上線前確認部署清單」 |

### 6. 輸出格式

```
📋 任務：{slug}（{name}）
🌿 分支：{branch}
📂 進度：spec ✅  db ✅  arch ✅  build ⏳ ...

══════════════════════════════════════════
💡 下一步建議

  /plan-build

理由：arch.md 已產出，可進入 Agent Teams 程式碼產生階段。
══════════════════════════════════════════

📌 順帶提醒（如有）：
  • 部署清單 deploy-checklist.md 有 2 個未勾選項目
```

`--all` 模式：列出所有活躍任務各自的「下一步建議」摘要，不顯示順帶提醒。

---

## Gotchas

- **`.spec/{slug}/README.md` 缺失**：若任務目錄存在但 README 缺 → 視為 plan-start 未完成，推薦重跑 `/plan-start --resume`
- **verify.md 解析失敗**：若摘要段落格式變動 → 退回「verify.md 存在但狀態不明」處理，推薦 `/plan-review`
- **多階段並進**：使用者可能跳過某步（如 DB_REQUIRED=false 跳 plan-db），按決策表第一匹配規則處理即可，不視為缺失
- **bug 類型任務**：本 skill 主要服務 feature 任務；bug 流程的下一步建議由 `/bug-investigate` / `/bug-fix` 內建邏輯處理，不在本 skill 範圍
- **任務已 close**：若 `_index.md` 中該任務列於「已完成」區段（`/plan-close` 的『更新 _index.md 與 README.md status』一節會將任務從「進行中」移至此區段）→ 不推薦任何指令，提示「任務已結案，可用 /plan-start 開新任務」

---

## 邊界情況

- **無 `.spec/` 目錄**：提示 `/plan-start` 開新任務
- **`_index.md` 不存在但 `.spec/{slug}/` 存在**：跳過 index 直接掃 `.spec/*/`，列出可選任務
- **使用者明確 `/plan-next <slug>`**：略過 Git branch 匹配，直接用 slug
- **同時有 verify.md FAIL + review.md PASS**：以 verify.md FAIL 為準（先解決失敗驗收），review 結果保留
