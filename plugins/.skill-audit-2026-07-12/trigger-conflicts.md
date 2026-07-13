# CREW 觸發衝突矩陣（29 skills × 使用者環境）

> 產出日期：2026-07-13
> 資料來源：`company-marketplace.bak/plugins/*/skills/*/SKILL.md` frontmatter（29 個，全數讀取）＋
> `~/.claude/skills/*/SKILL.md`（97 個）＋ `~/.claude/plugins/marketplaces/*/plugins/*/skills/*/SKILL.md`（65 個，含 company-marketplace 正本、forge/git-tools、minimax、openai-codex、claude-plugins-official）＋
> 目前 session 實際載入的 skill 清單（superpowers、內建 code-review / security-review / verify / init 等）。
> 註：apify / everything-claude-code / fullstack-dev-skills / impeccable / recur-skills 等 marketplace 有下載但未見於載入清單，僅列為潛在來源，不計入主要衝突。

---

## 一、衝突組矩陣（同一句話撞多個 skill）

| # | 使用者語句範例 | 會同時匹配的 skills | 嚴重度 |
|---|---------------|--------------------|--------|
| C1 | 「幫我修這個 bug」 | **bug-fix**（修 bug/修復）、**bug-start**（開始修 bug）、**bug-investigate**（investigate）、個人 `investigate`（"fix this bug"＋proactive）、`superpowers:systematic-debugging`（any bug） | 高 |
| C2 | 「幫我 code review 這次的改動」 | **plan-review**（code review/程式碼審查）、個人 `java-code-review`、個人 `review`（gstack）、`codex`（review 模式）、內建 `code-review`、`superpowers:requesting-code-review` | 高（6 條路） |
| C3 | 「檢查一下有沒有 security 問題」 | **plan-security**（單字「security」）、內建 `security-review`、個人 `cso`（security audit/security check） | 高 |
| C4 | 「幫我 plan 一下這個功能」 | **plan**（單字「plan」）、內建 Plan mode/Plan agent、`superpowers:writing-plans`、`superpowers:brainstorming`（MUST before any creative work）、個人 `planning-with-files` | 高 |
| C5 | 「verify／驗證一下這個修改有沒有生效」 | **plan-verify**（驗證/verify/驗收）、內建 `verify`、`superpowers:verification-before-completion` | 高 |
| C6 | 「這個任務結案吧」 | **bug-close**（結案）、**plan-close**(任務結案) — 兩個 CREW skill 自己互撞 | 高（CREW 內部） |
| C7 | 「幫我分析一下這個問題」 | **plan-explore**（分析一下）、個人 `model-thinking`（幫我分析）、`superpowers:brainstorming` | 中 |
| C8 | 「我要新增一張資料表」 | **plan-db**（設計資料表）、個人 `java-migration-helper`（新增表/schema 變更）、個人 `db-optimization-review`（index design） | 中 |
| C9 | 「這個專案的架構幫我 review」 | **plan-arch**（架構/arch）、**plan-review**、個人 `java-design-advisor`（architecture）、個人 `plan-eng-review`（review the architecture） | 中 |
| C10 | 「開一個新任務記錄這個 bug」 | **plan-start**（新任務，支援 bug 類型）、**bug-start**（建立 bug/記錄 bug）— CREW 內部重疊 | 中（CREW 內部） |
| C11 | 「幫我初始化／setup 這個專案」 | **plan-setup**（setup/初始化）、**crew-init**（初次設定）、**project-add**（設定專案）、內建 `init`、`repo-atlas:atlas`（init 模式） | 中 |
| C12 | 「更新 plugin」 | **crew-upgrade**（更新 plugin — 但使用者可能指任何 plugin）、個人 `gstack-upgrade`（update the tools） | 中 |
| C13 | 「為什麼壞了？」（指程式） | **crew-doctor**（為什麼壞了 — 實際只查 CREW 環境）、個人 `investigate`、`superpowers:systematic-debugging` | 中 |
| C14 | 「把進度同步到 Notion」 | **plan-sync**（同步到 Notion）、**plan-close**（同步到 Notion 並結案）、**bug-update**（更新 Notion 頁面） | 低（CREW 內部，語意相近） |
| C15 | 「幫我寫 commit」＋ CREW 流程收尾 | `git-tools:diff-summary`（寫 commit）、個人 `git-smart-commit`（拆分 commit）— 非 CREW 但常在 plan-build 後撞 | 低 |

---

## 二、CREW 過廣觸發詞（單字級 / 日常語級）

| Skill | 過廣觸發詞 | 誤觸發情境範例 |
|-------|-----------|----------------|
| plan | 「plan」 | 「What's the plan?」「照原 plan 繼續」— 任何含 plan 的英文句都可能匹配，實際只是對話 |
| plan-build | 「build」 | 「build 一下專案看會不會編譯錯」— 使用者要 `mvn/npm build`，卻被導去 Agent Teams 產 code |
| plan-spec | 「spec」 | 「這台機器的 spec 是什麼」「照 API spec 改」— spec 是通用詞 |
| plan-arch | 「架構」「arch」 | 「這專案架構長怎樣？」— 使用者想「了解」，skill 卻會去「產出架構設計文件」 |
| plan-security | 「security」 | 「幫我設定 Spring Security」— 完全無關安全掃描 |
| plan-verify | 「驗證」「verify」「驗收」 | 「驗證一下這段 SQL 對不對」— 會啟動 Playwright 開瀏覽器跑驗收流程 |
| plan-browse | 「browse」 | 「browse 一下這個網站」— 使用者要開瀏覽器，skill 是讀 .spec/ 文件 |
| plan-explore | 「探索」「想一下」「討論一下」「分析一下」「explore」 | 「我想一下再決定」「討論一下這個 error」— 幾乎任何對話開場都會命中 |
| plan-next | 「下一步」「接下來」「該做什麼」 | 對話中「好，接下來呢？」— 日常銜接語，非指令 |
| plan-demo | 「demo」「示範」 | 「寫個 demo 頁面給客戶看」— 與 CREW 評估模式無關 |
| plan-setup | 「setup」「初始化」 | 「初始化 git repo」「setup CI」— 通用動詞 |
| plan-status | 「任務狀態」「目前有哪些任務」 | 「目前有哪些任務在跑？」— 可能問 background task 或 Jira，不是 .spec/ |
| bug-fix | 「修復」 | 「修復這個 typo」「網路修復了」— 修復是通用動詞 |
| bug-close | 「結案」「修完了」 | 「Jira 那張單結案了」— 非 Notion bug 流程 |
| bug-update | 「貼 log」「reopen」 | 「我貼 log 給你看」— 使用者只是提供資訊，不是要寫 Notion |
| crew-doctor | 「為什麼壞了」「sanity check」 | 「這個測試為什麼壞了」— 指程式不是 CREW 環境 |
| crew-upgrade | 「更新 plugin」 | 「更新 playwright plugin」— 指別的 plugin |
| plan-deploy-confirm | 「deploy 完成」 | 「deploy 完成後通知我」— 一般部署對話 |

---

## 三、激進觸發語盤點

**CREW 29 個 frontmatter：未發現「必須使用我」「MUST」「1% 可能就 invoke」級別的激進語。**
統一句式為「當使用者提到「X」時觸發此 Skill」— 屬斷言式（宣告必然觸發），配合上表的單字級觸發詞，實際效果接近激進：弱模型會把「提到＝觸發」當成義務。

環境中真正的激進觸發語（CREW 的競爭者，會搶走或蓋過 CREW 觸發）：

| 來源 | 激進語句 | 影響 |
|------|----------|------|
| superpowers:using-superpowers | "requiring skill invocation before ANY response" | 每回合都先搶路由權 |
| superpowers:brainstorming | "You MUST use this before any creative work" | 與 plan / plan-explore / plan-start 直接搶「規劃前」時機 |
| 個人 investigate | "Proactively invoke this skill (do NOT debug directly)" | 與 bug-investigate / bug-fix 搶所有錯誤回報情境 |
| superpowers:systematic-debugging | "Use when encountering any bug ... before proposing fixes" | 同上 |
| 個人 ship | "Proactively invoke (do NOT push/PR directly)" | 與 plan-close 的 Git 提交步驟衝突 |
| 個人 office-hours | "Proactively invoke (do NOT answer directly)" 當使用者描述新想法 | 與 plan-explore 搶「探索想法」情境 |
| smartrobot-traceid-charset 等長描述 skill | 描述極長、關鍵字密集 | 稀釋注意力，間接提高誤選率 |

---

## 四、結論與建議（供上層診斷彙整）

1. **最危險的三組**：C1（修 bug 五搶一）、C2（code review 六搶一）、C4/C5（plan/verify 撞內建功能名）。這三組的共通根因：CREW 用「產品功能的通用名」當觸發詞，而環境同名內建工具/skill 已存在。
2. **CREW 內部互撞**（C6、C10、C14）不需外部因素就會發生，應優先在 description 中互相標注邊界（例：bug-close 註明「僅 bug 型任務；feature 結案用 plan-close」）。
3. **修法方向**：(a) 單字級觸發詞全部改為帶 `/` 前綴的指令名（plan-build、verify → 只認 `/plan-verify`）；(b) 通用中文短語（想一下、下一步、分析一下）整批移除；(c) 依全域 CLAUDE.md 指令優先序第 5 條，CREW 的「提到即觸發」句式本就不構成義務 — 可在 description 明寫「使用者輸入 /指令 時執行」降低斷言強度。
