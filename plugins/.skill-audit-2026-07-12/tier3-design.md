# CREW 觸發詞收斂設計（C10 / C11 / C15）

> 產出日期：2026-07-13
> 用途：29 個 SKILL.md 的 frontmatter `description` 與新增「何時不用」段的全局設計，供逐檔套用。
> 依據：`scratchpad/cross/trigger-conflicts.md`（15 衝突組＋18 過廣詞）＋ `c-items.md` C10/C11/C15 ＋ `docs/SKILL-TEMPLATE.md`。
> 讀法：每個 skill 一節。`action` 全為 change（29/29 現況觸發詞皆含過廣詞）。`new_description` 為單行 YAML 安全字串（≤400 字、繁中、無換行、不以冒號開頭）。「何時不用」寫進各檔新增段（C15），內容與 `boundary_note`（C11 互撞組）呼應。

---

## 一、全局設計原則（逐檔套用時遵循）

1. **description 三段式**：`{一句功能摘要（含情境限定詞）}。當使用者輸入 /{指令名}，或提到「{組合詞1}」、「{組合詞2}」時觸發此 Skill。`
   - 尾句從「提到即觸發」降為「輸入 /指令 或提及完整組合詞」，降低斷言強度（C10-c）。
2. **保留**：`/斜線指令`（唯一最可靠觸發，每檔必列為第 1 觸發）＋明確組合片語（「從 spec 產生程式碼」「自訂技術棧」）。使用者習慣用語不全刪，改加情境限定。
3. **刪除**：單字級英文詞（plan / build / verify / spec / security / browse / demo / arch / doctor / explore / setup / reopen）、日常口語（想一下 / 下一步 / 接下來 / 分析一下 / 討論一下 / 修復 / 結案 / 修完了 / 貼 log / 為什麼壞了 / 該做什麼 / next step / what's next / sanity check）。
4. **情境限定詞（差異化）**：與環境 skills 搶觸發的情境，一律加限定詞標明適用場景 —— `CREW`、`.spec/`、`.spec 任務`、`Notion 任務追蹤`、`Agent Teams`。
5. **每檔保留 1–2 個「不會出現在日常對話」的組合詞**維持自然語言可發現性（C10 風險緩解）。
6. **互撞邊界**寫在「何時不用」段與 `boundary_note`，不塞進 description（C11）。

## 二、環境競爭者對照（差異化限定詞據此設計）

| CREW skill | 搶觸發的環境 skill / 內建 | CREW 差異化限定詞 |
|---|---|---|
| bug-fix / bug-investigate | 個人 `investigate`、`superpowers:systematic-debugging` | 「CREW bug 流程」「同步 Notion 任務追蹤」「根因確認」 |
| plan-review | 內建 `code-review`、個人 `java-code-review`/`review`、`codex`、`superpowers:requesting-code-review` | 「Agent Teams 並行」「.spec 任務」 |
| plan-security | 內建 `security-review`、個人 `cso` | 「CREW 三層掃描」「.spec」 |
| plan-verify | 內建 `verify`、`superpowers:verification-before-completion` | 「Playwright 瀏覽器」「.spec 驗收條件」 |
| plan / plan-spec / plan-arch | 內建 Plan mode、`superpowers:writing-plans`/`brainstorming`、個人 `planning-with-files` | 「.spec/ 目錄」「零 Notion 呼叫」 |
| plan-explore | 個人 `model-thinking`、`superpowers:brainstorming`、個人 `office-hours` | 「CREW 規劃前」「思考夥伴」 |
| plan-db | 個人 `java-migration-helper`、`db-optimization-review` | 「.spec 資料庫設計文件」（非執行 migration） |
| plan-arch（了解類） | 個人 `java-design-advisor` | 「產出架構設計文件」（非給建議） |
| crew-doctor | 個人 `investigate`、`systematic-debugging` | 「CREW 環境依賴」（非程式除錯） |
| crew-upgrade | 個人 `gstack-upgrade`、任意 plugin 更新 | 「CREW plugins（bug/feature-workflow）」 |
| project-add / *-setup / crew-init | 內建 `init`、`repo-atlas:atlas` | 「Notion 專案資料庫」「CREW 設定」 |
| plan-close（Git 提交） | 個人 `ship` | 「.spec 結案批次同步 Notion」 |
| plan-build 後 commit | 個人 `git-smart-commit`、`git-tools` | 不搶 commit：本 skill 只產碼，收尾交給 commit skill |

## 三、三組 CREW 內部互撞（C11，對稱指名分工）

- **close 組**：`bug-close` ↔ `plan-close` —— bug 型任務結案用 bug-close；feature/.spec 任務結案用 plan-close。
- **start 組**：`bug-start` ↔ `plan-start` —— 只建 Notion bug 條目用 bug-start；需完整入口（Notion + .spec/ + Git branch）用 plan-start。
- **sync 組**：`plan-sync` ↔ `plan-close` ↔ `bug-update` —— 未結案的 .spec 中途同步用 plan-sync；結案批次同步用 plan-close；單一 bug 頁更新用 bug-update。

---

# 四、逐檔設計（29 節）

## bug-workflow（10）

### bug-workflow:bug-close
- action: change
- new_description: 修復 Bug 後從 Git diff 自動擷取修復細節並更新 Notion 任務追蹤頁面（僅限 bug 型任務）。當使用者輸入 /bug-close，或提到「關閉 bug」、「bug 結案並補修復細節」時觸發此 Skill。
- when_not_to_use:
  - feature/.spec 任務結案 → /plan-close
  - 尚未修完、只想中途補調查資訊 → /bug-update
  - Jira 單結案（非 Notion bug 流程）→ 用 jira MCP / jira-from-pm
  - 未建立 Notion bug 條目就想結案 → 先 /bug-start
- boundary_note: close 組 —— 本 skill 只結 bug 型任務；feature/.spec 任務結案用 /plan-close。

### bug-workflow:bug-fix
- action: change
- new_description: CREW bug 修復紀律 —— 根因確認才能改（鐵律）、產出修復建議與迴歸測試、瀏覽器驗證，隸屬 CREW bug 流程。當使用者輸入 /bug-fix，或提到「進行 CREW bug 修復」、「開始修復這個 bug」時觸發此 Skill。
- when_not_to_use:
  - 根因尚未確認 → 先 /bug-investigate（或 investigate / superpowers:systematic-debugging）
  - 一般錯誤排查、非 CREW 任務 → 個人 investigate / superpowers:systematic-debugging
  - 只想記錄修復結果並結案 → /bug-close
  - typo 或瑣碎改動 → 直接改，無需本 skill

### bug-workflow:bug-investigate
- action: change
- new_description: 假說驅動的 CREW Bug 根因調查 —— 自動收集證據、模式比對、假說驗證，全程同步 Notion 任務追蹤。當使用者輸入 /bug-investigate，或提到「調查 bug 根因」、「CREW bug 根因分析」時觸發此 Skill。
- when_not_to_use:
  - 非 CREW、未建 Notion 任務的一般除錯 → 個人 investigate / superpowers:systematic-debugging
  - 根因已確認、要開始修 → /bug-fix
  - 只把新證據補進既有頁面 → /bug-update
  - CREW 環境本身為何不能用 → /crew-doctor

### bug-workflow:bug-setup
- action: change
- new_description: bug-workflow 首次設定引導 —— 自動偵測 Notion 資料庫、建立設定檔、設定專案對應。當使用者輸入 /bug-setup，或提到「設定 bug workflow」、「初始化 bug workflow」時觸發此 Skill。
- when_not_to_use:
  - 想一鍵完成 bug + feature 全部設定 → /crew-init
  - 只設定 feature 側 → /plan-setup
  - 初始化程式專案 / git repo / CLAUDE.md → 內建 /init 或 git
  - 註冊專案到 Notion 專案庫 → /project-add

### bug-workflow:bug-start
- action: change
- new_description: 在 Notion 任務追蹤工具建立 Bug 條目並填入標準化模板（僅建條目，不含 .spec/ 目錄與 Git branch）。當使用者輸入 /bug-start，或提到「建立 bug 條目」、「記錄 bug 到 Notion」、「bug 通報」時觸發此 Skill。
- when_not_to_use:
  - 需同時建 .spec/ 目錄 + Git branch → /plan-start（type=bug）
  - 條目已建、要開始修 → /bug-fix
  - 補充既有 bug 資訊 → /bug-update
  - 建立 feature 新任務 → /plan-start
- boundary_note: start 組 —— 本 skill 只建 Notion bug 條目；需完整入口（Notion + .spec/ + branch）用 /plan-start。

### bug-workflow:bug-update
- action: change
- new_description: 調查 Bug 過程中隨時將 log、SQL、判斷、截圖更新到該 Bug 的 Notion 頁面，並支援重新開啟已結案 Bug。當使用者輸入 /bug-update，或提到「更新 bug 頁面」、「補充 bug 資訊」、「reopen bug」、「bug 復發」時觸發此 Skill。
- when_not_to_use:
  - 修完要結案 → /bug-close
  - feature/.spec 進度同步 Notion → /plan-sync（中途）或 /plan-close（結案）
  - 只是貼 log 給我看、非寫入 Notion → 直接貼，無需本 skill
  - 建立新 bug → /bug-start
- boundary_note: sync 組 —— 本 skill 更新「單一 bug 頁面」；.spec 中途同步用 /plan-sync、結案批次同步用 /plan-close。

### bug-workflow:crew-doctor
- action: change
- new_description: CREW 環境健診 —— 一次性檢查 CREW 所有必要與選配依賴（Node/Git/Notion MCP/Agent Teams/瀏覽器 MCP/config/專案註冊/CLAUDE.md），列出綠黃紅燈與修法。當使用者輸入 /crew-doctor，或提到「CREW 環境健診」、「CREW 為什麼不能用」時觸發此 Skill。
- when_not_to_use:
  - 程式 / 測試為何壞 → 個人 investigate / superpowers:systematic-debugging
  - CREW 首次設定 → /crew-init
  - 更新 CREW → /crew-upgrade
  - 一般專案環境問題（非 CREW 依賴）→ 自行排查

### bug-workflow:crew-init
- action: change
- new_description: CREW 一鍵首次設定 —— 依序執行 /bug-setup → /plan-setup 並提示 /init 與 /project-add，含跳過邏輯與斷點續跑。當使用者輸入 /crew-init，或提到「CREW 一鍵設定」、「初始化 CREW」時觸發此 Skill。
- when_not_to_use:
  - 只設定 bug 側 → /bug-setup
  - 只設定 feature 側 → /plan-setup
  - 註冊專案到 Notion → /project-add
  - 初始化 CLAUDE.md → 內建 /init
  - CREW 環境檢查 → /crew-doctor

### bug-workflow:crew-upgrade
- action: change
- new_description: 更新 CREW plugins（bug-workflow + feature-workflow）到最新版本並顯示更新摘要。當使用者輸入 /crew-upgrade，或提到「更新 CREW」、「升級 CREW plugin」時觸發此 Skill。
- when_not_to_use:
  - 更新其他 plugin（如 playwright）→ 該 plugin 管道 / claude plugin 指令
  - 更新 gstack → 個人 gstack-upgrade
  - CREW 首次設定 → /crew-init
  - CREW 環境健診 → /crew-doctor

### bug-workflow:project-add
- action: change
- new_description: 將當前專案新增或更新到 Notion 專案資料庫 —— 自動偵測 Git Repo、技術棧、專案類型，產生 Notion 頁面，可選裝 DB MCP。當使用者輸入 /project-add，或提到「新增專案到 Notion」、「註冊專案」時觸發此 Skill。
- when_not_to_use:
  - 首次整體設定 → /crew-init（或 /bug-setup + /plan-setup）
  - 建立任務條目（非專案）→ /plan-start 或 /bug-start
  - virtual monorepo / 跨 repo workspace → repo-atlas:atlas
  - 初始化 CLAUDE.md → 內建 /init

## feature-workflow（19）

### feature-workflow:plan
- action: change
- new_description: CREW 完整規劃串接器 —— 自動依序執行 plan-spec → plan-db → plan-arch，產出寫入 .spec/ 目錄（零 Notion 呼叫）。當使用者輸入 /plan，或提到「CREW 完整規劃」、「一次跑完 spec/db/arch」時觸發此 Skill。
- when_not_to_use:
  - 只要技術規格 → /plan-spec
  - 只要資料庫設計 → /plan-db
  - 只要架構設計 → /plan-arch
  - 規劃前發散討論 → /plan-explore
  - 建任務入口（Notion + branch）→ /plan-start
  - 一般寫實作計畫文件 → superpowers:writing-plans

### feature-workflow:plan-arch
- action: change
- new_description: 產出架構設計文件寫入 .spec/ 目錄（零 Notion 呼叫）。當使用者輸入 /plan-arch，或提到「產出架構設計文件」、「.spec 架構設計」時觸發此 Skill。
- when_not_to_use:
  - 想了解現有架構 / 要設計模式建議 → 個人 java-design-advisor
  - 完整規劃（spec + db + arch）→ /plan
  - 只要規格 → /plan-spec；只要 DB → /plan-db
  - 架構 / 程式碼審查 → /plan-review

### feature-workflow:plan-browse
- action: change
- new_description: 瀏覽與探索已有的 .spec/ 規劃文件 —— 深度閱讀、跨任務比較、模式搜尋。當使用者輸入 /plan-browse，或提到「瀏覽 .spec 規劃」、「看之前的規劃設計」時觸發此 Skill。
- when_not_to_use:
  - 開瀏覽器看網站 → claude-in-chrome / playwright
  - 看任務清單與狀態 → /plan-status
  - 要推薦下一步 → /plan-next
  - 產出新規劃 → /plan 或 /plan-spec

### feature-workflow:plan-build
- action: change
- new_description: 從 .spec/ 設計文件以 Agent Teams leader-delegate 模式產生程式碼，含退出驗證與 deploy.sql 自動產出，Leader 只協調不寫 code。當使用者輸入 /plan-build，或提到「從 spec 產生程式碼」、「plan-build 產碼」時觸發此 Skill。
- when_not_to_use:
  - 編譯專案（mvn / npm build）→ 直接跑 build 指令，非本 skill
  - 尚無 .spec 設計文件 → 先 /plan
  - 產完後審查 → /plan-review；驗收 → /plan-verify
  - 只要拆分 commit → git-smart-commit（本 skill 只產碼）

### feature-workflow:plan-close
- action: change
- new_description: 一次性批次同步 .spec/ 設計文件到 Notion（含 deploy.sql）、更新狀態、同步知識庫、提交 Git，用於 feature/.spec 任務結案。當使用者輸入 /plan-close，或提到「feature 結案」、「同步 spec 到 Notion 並結案」時觸發此 Skill。
- when_not_to_use:
  - bug 型任務結案 → /bug-close
  - 未結案的中途同步 → /plan-sync
  - 更新單一 bug 頁 → /bug-update
  - 部署 SQL 執行回報 → /plan-deploy-confirm
- boundary_note: close 組 + sync 組 —— feature/.spec 任務結案用本 skill；bug 型結案用 /bug-close；未結案的中途同步用 /plan-sync。

### feature-workflow:plan-db
- action: change
- new_description: 產出資料庫設計文件寫入 .spec/ 目錄（零 Notion 呼叫）。當使用者輸入 /plan-db，或提到「產出 DB 設計文件」、「.spec 資料庫設計」時觸發此 Skill。
- when_not_to_use:
  - 建立 / 執行 migration 檔（Flyway / Liquibase）→ 個人 java-migration-helper
  - 查詢 / 索引 / 連線池效能優化 → 個人 db-optimization-review
  - 完整規劃 → /plan
  - 只要技術規格 → /plan-spec

### feature-workflow:plan-demo
- action: change
- new_description: 純本地產出範例 .spec/ 任務，不依賴 Notion / Agent Teams / DB MCP，讓評估者快速看到 CREW 完整流程效果。當使用者輸入 /plan-demo，或提到「評估 CREW 流程」、「CREW 試跑範例」時觸發此 Skill。
- when_not_to_use:
  - 寫 demo 頁面給客戶看 → 直接開發，非本 skill
  - 正式建立任務 → /plan-start
  - 完整規劃 → /plan
  - CREW 環境檢查 → /crew-doctor

### feature-workflow:plan-deploy-confirm
- action: change
- new_description: 部署 SQL 執行回報 —— 實際跑完 deploy.sql 後勾選每筆執行狀態並寫回 Notion「部署狀態」區塊，補上 plan-close 後的執行回流。當使用者輸入 /plan-deploy-confirm，或提到「deploy.sql 執行回報」、「DBA 確認部署」時觸發此 Skill。
- when_not_to_use:
  - 產出 deploy.sql / 任務結案 → /plan-close
  - 未結案的中途同步 → /plan-sync
  - 一般部署完成通知 → 非本 skill
  - 實際執行 SQL 異動 → 由 DBA / 使用者執行，本 skill 只回報狀態

### feature-workflow:plan-explore
- action: change
- new_description: CREW 探索模式 —— 規劃前或規劃中的思考夥伴，自由探索想法、調查問題、釐清需求（零 Notion 呼叫）。當使用者輸入 /plan-explore，或提到「CREW 規劃前探索」、「規劃前討論需求」時觸發此 Skill。
- when_not_to_use:
  - 一般決策 / 多角度分析 / 思維模型 → 個人 model-thinking
  - 創作前需求發散 → superpowers:brainstorming
  - 已明確要產出文件 → /plan-spec 或 /plan
  - 除錯調查 → 個人 investigate

### feature-workflow:plan-next
- action: change
- new_description: 智慧推薦 CREW 當前任務下一步 —— 讀 .spec/{slug}/ 檔案、Git 狀態、verify.md 判斷流程位置並建議下一個 /plan-* 或 /bug-* 指令。當使用者輸入 /plan-next，或提到「CREW 下一步指令」、「這個 spec 接下來做什麼」時觸發此 Skill。
- when_not_to_use:
  - 一般對話「接下來呢」→ 非 skill，直接回答
  - 看任務清單 → /plan-status
  - 瀏覽規劃內容 → /plan-browse

### feature-workflow:plan-review
- action: change
- new_description: 以 Agent Teams 3 人並行審查 .spec 任務的程式碼（邏輯/品質/效能）並交叉審查，報告寫入 .spec/ 目錄。當使用者輸入 /plan-review，或提到「Agent Teams 程式碼審查」、「plan-review 審查」時觸發此 Skill。
- when_not_to_use:
  - 一般 diff code review → 內建 /code-review 或 codex
  - Java 最佳實務審查 → 個人 java-code-review
  - 提交前驗證需求覆蓋 → superpowers:requesting-code-review
  - 安全掃描 → /plan-security；架構設計建議 → 個人 java-design-advisor

### feature-workflow:plan-security
- action: change
- new_description: 專職安全掃描 —— CREW 三層架構（靜態規則/上下文感知/對抗性思維），涵蓋 OWASP Top 10、SQLi、XSS、權限控制、敏感資料。當使用者輸入 /plan-security，或提到「CREW 安全掃描」、「.spec 安全檢查」時觸發此 Skill。
- when_not_to_use:
  - 設定 Spring Security 等安全功能 → 直接開發，非掃描
  - 基礎設施 / 供應鏈 / 秘密外洩稽核 → 個人 cso
  - 當前分支變更安全審查 → 內建 /security-review
  - 一般程式碼審查 → /plan-review

### feature-workflow:plan-setup
- action: change
- new_description: feature-workflow 首次設定引導 —— 自動偵測 Notion 資料庫、匯入 bug-workflow 共用 ID、設定專案對應與技術棧、可選裝獨立 Agent。當使用者輸入 /plan-setup，或提到「設定 feature workflow」、「初始化 feature workflow」時觸發此 Skill。
- when_not_to_use:
  - 一鍵完成 bug + feature 全部設定 → /crew-init
  - 只設定 bug 側 → /bug-setup
  - 初始化程式專案 / CLAUDE.md → 內建 /init
  - 註冊專案 → /project-add；自訂技術棧 → /plan-stack

### feature-workflow:plan-spec
- action: change
- new_description: 產出技術規格書寫入 .spec/ 目錄（零 Notion 呼叫）。當使用者輸入 /plan-spec，或提到「產出技術規格書」、「.spec 規格書」時觸發此 Skill。
- when_not_to_use:
  - 完整規劃（spec + db + arch）→ /plan
  - 資料庫設計 → /plan-db；架構設計 → /plan-arch
  - 規劃前探索 → /plan-explore
  - 查機器規格 / 讀既有 API spec → 非本 skill

### feature-workflow:plan-stack
- action: change
- new_description: 自動偵測或互動式建立自訂技術棧 —— 掃描專案分層結構產生範本掃描規則，寫入設定檔。當使用者輸入 /plan-stack，或提到「自訂技術棧」、「新增掃描技術棧」時觸發此 Skill。
- when_not_to_use:
  - 首次整體設定 → /plan-setup 或 /crew-init
  - 詢問專案用什麼技術 → 自行查看，非本 skill
  - 註冊專案 → /project-add

### feature-workflow:plan-start
- action: change
- new_description: 建立 Notion 條目 + .spec/ 規劃目錄 + Git branch 的統一任務入口（支援 feature 與 bug），含退出驗證確保必填欄位完整。當使用者輸入 /plan-start，或提到「開新 CREW 任務」、「建立規劃任務」時觸發此 Skill。
- when_not_to_use:
  - 只需 Notion bug 條目、不要 .spec/ 與 branch → /bug-start
  - 任務已建、要規劃內容 → /plan 或 /plan-spec
  - 規劃前探索 → /plan-explore
  - 註冊專案（非任務）→ /project-add
- boundary_note: start 組 —— 本 skill 是完整入口（Notion + .spec/ + branch）；只要建 Notion bug 條目用 /bug-start。

### feature-workflow:plan-status
- action: change
- new_description: 列出 .spec/ 目錄中所有活躍與已完成的任務（純本地操作，不呼叫 Notion）。當使用者輸入 /plan-status，或提到「.spec 任務狀態」、「CREW 任務列表」時觸發此 Skill。
- when_not_to_use:
  - 查 background task 執行狀態 → 非本 skill
  - 查 Jira 單狀態 → jira-from-pm 或 jira MCP
  - 要推薦下一步 → /plan-next
  - 看規劃文件內容 → /plan-browse

### feature-workflow:plan-sync
- action: change
- new_description: 手動中途同步 .spec/ 目錄當前進度到 Notion（含 deploy.sql），按需使用、不在常規流程、任務尚未結案。當使用者輸入 /plan-sync，或提到「中途同步 spec 進度」、「同步 spec 進度到 Notion」時觸發此 Skill。
- when_not_to_use:
  - 要結案（最終同步）→ /plan-close
  - 更新單一 bug 頁 → /bug-update
  - 部署 SQL 執行回報 → /plan-deploy-confirm
- boundary_note: sync 組 —— 本 skill 是「未結案的中途同步」；結案批次同步用 /plan-close；單一 bug 頁更新用 /bug-update。

### feature-workflow:plan-verify
- action: change
- new_description: 透過 Playwright MCP 操作瀏覽器逐條驗證 .spec/ 驗收條件，產出 verify.md 與 Health Score，可選 --deep 查 console/network。當使用者輸入 /plan-verify，或提到「.spec 驗收條件驗證」、「瀏覽器驗收 spec」時觸發此 Skill。
- when_not_to_use:
  - 驗證程式改動是否生效（非瀏覽器驗收）→ 內建 /verify
  - 宣稱完成前的一般驗證 → superpowers:verification-before-completion
  - 驗證 SQL 語法對不對 → 直接檢查，非本 skill
  - 審查程式碼 → /plan-review
