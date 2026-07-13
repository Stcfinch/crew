# CREW Skills 優化清單（2026-07-12）

> 涵蓋範圍：bug-workflow（10 skills）＋ feature-workflow（19 skills），共 29 個 SKILL.md、7,512 行。
> 資料來源：29 份逐 skill 已驗證發現（findings/*.json，共 181 條）＋ 3 份跨 skill 分析（duplication.md、trigger-conflicts.md、consistency.md）。
> 用法：每個優化項（C 編號＝跨 skill、S 編號＝逐 skill）可獨立核准或否決；核准後依「五、建議執行順序」執行。

---

## 一、總覽統計

### 1.1 維度 × 嚴重度計數表（共 181 條）

| 維度 | 高 | 中 | 低 | 小計 |
|------|----|----|----|------|
| reference | 22 | 34 | 16 | 72 |
| trigger | 2 | 20 | 7 | 29 |
| structure | 1 | 22 | 33 | 56 |
| token | 0 | 10 | 14 | 24 |
| **合計** | **25** | **86** | **70** | **181** |

- **reference（72 條）為最大宗**，其中 22 條高嚴重度——主因是 SKILL.md 以相對路徑引用 `references/*.md`，但實體檔案在 plugin 根目錄而非 skill 目錄（見 C12 批次修法）。
- **structure（56 條）** 集中在步驟編號跳號／指涉腐化與段落集合不一致（見 C14、C15）。
- **trigger（29 條）** 集中在單字級過廣觸發詞與 CREW 內部互撞（見 C10、C11）。
- **token（24 條）** 多為跨檔重複樣板可抽共用（見 C1–C9）。

### 1.2 各 skill 發現數排行

| 排名 | Skill | Plugin | 發現數 | 高 | 中 | 低 | 行數 |
|------|-------|--------|--------|----|----|----|------|
| 1 | plan-verify | feature-workflow | 12 | 2 | 6 | 4 | 563 |
| 2 | bug-close | bug-workflow | 8 | 1 | 4 | 3 | 307 |
| 3 | plan-build | feature-workflow | 8 | 0 | 4 | 4 | 401 |
| 4 | plan-close | feature-workflow | 8 | 3 | 3 | 2 | 291 |
| 5 | plan-demo | feature-workflow | 8 | 1 | 5 | 2 | 213 |
| 6 | plan-setup | feature-workflow | 8 | 0 | 5 | 3 | 228 |
| 7 | bug-fix | bug-workflow | 7 | 1 | 3 | 3 | 285 |
| 8 | bug-start | bug-workflow | 7 | 1 | 2 | 4 | 403 |
| 9 | crew-doctor | bug-workflow | 7 | 1 | 3 | 3 | 210 |
| 10 | crew-init | bug-workflow | 7 | 1 | 3 | 3 | 235 |
| 11 | plan-browse | feature-workflow | 7 | 0 | 3 | 4 | 286 |
| 12 | plan-deploy-confirm | feature-workflow | 7 | 2 | 3 | 2 | 242 |
| 13 | bug-update | bug-workflow | 6 | 1 | 2 | 3 | 250 |
| 14 | crew-upgrade | bug-workflow | 6 | 2 | 3 | 1 | 179 |
| 15 | plan-explore | feature-workflow | 6 | 1 | 2 | 3 | 322 |
| 16 | plan-next | feature-workflow | 6 | 2 | 2 | 2 | 137 |
| 17 | plan-review | feature-workflow | 6 | 0 | 4 | 2 | 267 |
| 18 | plan-stack | feature-workflow | 6 | 0 | 4 | 2 | 119 |
| 19 | plan-start | feature-workflow | 6 | 0 | 3 | 3 | 420 |
| 20 | project-add | bug-workflow | 6 | 1 | 3 | 2 | 482 |
| 21 | bug-investigate | bug-workflow | 5 | 1 | 3 | 1 | 415 |
| 22 | plan-security | feature-workflow | 5 | 1 | 2 | 2 | 267 |
| 23 | plan-status | feature-workflow | 5 | 0 | 2 | 3 | 182 |
| 24 | plan-sync | feature-workflow | 5 | 1 | 1 | 3 | 135 |
| 25 | bug-setup | bug-workflow | 4 | 1 | 3 | 0 | 357 |
| 26 | plan-arch | feature-workflow | 4 | 0 | 3 | 1 | 56 |
| 27 | plan-db | feature-workflow | 4 | 0 | 1 | 3 | 82 |
| 28 | plan-spec | feature-workflow | 4 | 0 | 3 | 1 | 115 |
| 29 | plan | feature-workflow | 3 | 1 | 1 | 1 | 63 |

---

## 二、跨 skill 優化項（C1–C16）

### A. 重複抽共用（來源：duplication.md，合計約 211 行 SKILL.md 內文＋258 行整檔重複可省）

#### C1｜bug-workflow「## 設定檔」區塊逐字重複 5 次（~50 行）
- **問題**：11 行設定檔路徑說明在 5 個 skill 逐字重複；且 `references/prerequisites.md:125-126` 已含同一路徑清單、5 個 skill 都已引用該檔——與既有 reference 完全冗餘。
- **建議改法**：整段刪除，併入既有的「> 前置檢查：參照 `references/prerequisites.md`」一行；project-add 變體保留 6 行差異說明。
- **影響的 skills**：bug-close、bug-fix、bug-investigate、bug-start、bug-update（＋project-add 變體）。
- **風險**：低。內容已有單一來源，刪除不損失資訊；需確認各檔引用行仍在。

#### C2｜「## 紀律護欄」樣板 11 份僅 skill 名不同（~33 行）
- **問題**：同一 5–6 行樣板出現在 11 個 skill，只差「{skill 名} 專用」一詞；全文已在 `references/discipline-preamble.md`。
- **建議改法**：各 SKILL.md 壓成單行「> 紀律護欄：讀 `references/discipline-preamble.md`＋anti-rationalizations.md／boundaries.md 的『{skill 名}』段」。**前置條件**：先修 S8／S15／S16／S20（4 個 skill 宣稱的專用段實際不存在），否則指標指向空段落。
- **影響的 skills**：bug-fix、bug-investigate、crew-doctor、crew-init、plan-build、plan-demo、plan-deploy-confirm、plan-review、plan-security、plan-next、plan-verify。
- **風險**：中。壓縮後弱模型可能不去讀 reference；建議保留「停下查表」一句關鍵指令在行內。

#### C3｜「定位目標 Bug」14 行邏輯逐字複製（~26 行）
- **問題**：bug-fix、bug-investigate 開頭寫「與 /bug-update 相同邏輯：」後仍把 14 行步驟全文貼一遍。
- **建議改法**：抽到 `bug-workflow/references/locate-bug.md`，三個 skill 各留 1 行指標。
- **影響的 skills**：bug-fix、bug-investigate、bug-update。
- **風險**：低。

#### C4｜環境快照／證據收集流程高度相似（~25 行）
- **問題**：bug-start:176-224 與 bug-investigate:106-170 的 git 指令、知識庫搜尋、學習檔 grep、Notion 寫入格式同構（bug-investigate:160-163 ≡ bug-start:215-218）。
- **建議改法**：抽 `bug-workflow/references/evidence-collection.md`（收集指令＋寫入格式），兩 skill 各留差異描述。
- **影響的 skills**：bug-start、bug-investigate。
- **風險**：低。

#### C5｜「本地檔案 ↔ Notion 區塊」對應表雙份（~24 行）
- **問題**：plan-close:44-66 與 plan-sync:76-99 兩張對應表幾乎相同，同步骨架（Fetch → update content → update properties）也相同；新增文件類型要改兩處。
- **建議改法**：對應表抽到 `feature-workflow/references/plan-common.md`（既有共用檔），兩 skill 引用。
- **影響的 skills**：plan-close、plan-sync。
- **風險**：低。注意 plan-close 多 verify.md 一列，抽出時以聯集為準並標注適用者。

#### C6｜「建立新專案條目」引導文案重複（~15 行）
- **問題**：bug-setup:268-287 與 project-add:259-276 引導區塊高度相似，後續 Notion 欄位表也重疊。
- **建議改法**：抽到 `bug-workflow/references/project-page-templates.md`（既有檔案，本就放專案頁模板），兩 skill 引用。
- **影響的 skills**：bug-setup、project-add。
- **風險**：低。project-add 多技術棧、PROD/UAT 分支三欄，需以超集承載。

#### C7｜「偵測負責人」流程跨 plugin 逐字相同（~13 行）
- **問題**：bug-start:82-96 與 plan-start:82-96 完全相同 15 行（git config user.email → notion-get-users → email 比對 → 填負責人）。
- **建議改法**：plugin 隔離下各自 references/ 放一份（同 discipline-preamble.md 現行做法），SKILL.md 留 1 行指標；跨包同步靠 C9 的單一來源機制。
- **影響的 skills**：bug-start、plan-start。
- **風險**：低。

#### C8｜MCP 安裝指令片段 3 檔重複（~10 行）
- **問題**：chrome-devtools 安裝指令 plan-setup:159-165 ≡ plan-verify:43-49；playwright 安裝 plan-verify:35-36 ≡ crew-doctor:120-121。安裝指令是最容易改版走鐘的內容。**前置條件**：其中 playwright 套件名本身是錯的（S7／S24：`@anthropic-ai/mcp-server-playwright` npm 404），先修正確名再抽。
- **建議改法**：feature-workflow/references/ 新增 `mcp-install.md`（或併入 config-resolver.md），三處引用；bug-workflow 側 crew-doctor 對應同步。
- **影響的 skills**：plan-setup、plan-verify、crew-doctor。
- **風險**：低。單一來源價值高於省行數。

#### C9｜跨 plugin references/ 整檔重複（258 行逐 byte 相同＋約 300 行近似）
- **問題**：discipline-preamble.md（44 行）、db-templates.md（214 行）兩 plugin 逐 byte 相同；anti-rationalizations.md、boundaries.md、prerequisites.md、config.template.md 近似重複，prerequisites.md 已出現 1 行漂移。
- **建議改法**：在 marketplace repo 以單一來源＋建置時複製（或 symlink）維護；不影響執行期行為。
- **影響的 skills**：兩 plugin 全部 29 個（間接）。
- **風險**：中。涉及 marketplace 建置流程改動，需要有 build script 承載；若無建置步驟，退而求其次：在兩份檔頭加「鏡像檔，修改請同步」註記＋crew-doctor 加 cmp 漂移檢查。

### B. 觸發衝突解法（來源：trigger-conflicts.md）

#### C10｜單字級／日常語級觸發詞整批收斂（18 個 skill）
- **問題**：plan（"plan"）、plan-build（"build"）、plan-spec（"spec"）、plan-verify（"驗證/verify"）、plan-explore（"想一下/討論一下/分析一下"）、plan-next（"下一步/接下來"）、bug-fix（"修復"）、crew-doctor（"為什麼壞了"）等 18 個 skill 用通用詞當觸發詞，日常對話即誤觸發；且與內建功能名（Plan mode、verify、code-review、security-review、init）直接相撞（衝突組 C1–C5、C11–C13）。
- **建議改法**：(a) 單字級觸發詞全部改為帶 `/` 前綴的指令名或組合詞（如「從 spec 產生程式碼」）；(b) 通用中文短語（想一下、下一步、分析一下、修復、結案、demo、setup…）整批移除；(c) description 句式從「當使用者提到…時觸發」降為「使用者輸入 /指令 時執行；提及完整組合詞時可建議」。
- **影響的 skills**：plan、plan-build、plan-spec、plan-arch、plan-security、plan-verify、plan-browse、plan-explore、plan-next、plan-demo、plan-setup、plan-status、bug-fix、bug-close、bug-update、crew-doctor、crew-upgrade、plan-deploy-confirm。
- **風險**：中。收斂過度會降低自然語言可發現性；建議每個 skill 保留 1–2 個「不會出現在日常對話」的組合詞。

#### C11｜CREW 內部互撞：close／start／sync 三組邊界標注
- **問題**：不需外部因素就互撞——「結案」同時命中 bug-close 與 plan-close（衝突組 C6）；「開一個新任務記錄 bug」同時命中 plan-start 與 bug-start（C10）；「同步到 Notion」命中 plan-sync／plan-close／bug-update（C14）。
- **建議改法**：在 description 與新增的「何時不用」段（C15）互相標注邊界，例：bug-close 註明「僅 bug 型任務；feature 結案用 /plan-close」；plan-sync 註明「中途同步；結案用 /plan-close」。
- **影響的 skills**：bug-close、plan-close、bug-start、plan-start、plan-sync、bug-update。
- **風險**：低。

#### C12｜references/ 相對路徑整批修正（reference 維度最大宗根源）
- **問題**：29 個 skill 目錄下都沒有 references/，實體檔在 plugin 根目錄；SKILL.md 內全部以 `references/…` 相對路徑書寫，agent 就地解析會失敗。這是 72 條 reference findings 中最大宗的共同根源（S1、S2、S3、S5、S6、S25 等高嚴重度＋大量中低嚴重度）。
- **建議改法**：統一改為 `${CLAUDE_PLUGIN_ROOT}/references/…`，或至少統一句式「plugin 根目錄 `references/…`（相對 SKILL.md 為 `../../references/`）」；寫進 C14 模板的通用書寫規則，一次修 29 檔。
- **影響的 skills**：全部 29 個。
- **風險**：低。先實測 `${CLAUDE_PLUGIN_ROOT}` 在本環境的展開行為再套用（實測 1 個 skill 通過後批次套用）。

### C. 統一模板（來源：consistency.md）

#### C13｜前置檢查句式收斂為每 plugin 一種
- **問題**：同一個 prerequisites.md 引用出現 4 種句式（「完整前置檢查」／「檢查 CLAUDE.md 是否存在」／「設定目錄」變體／「只檢查第 2 項」），弱模型無法判斷檢查範圍差異是刻意還是筆誤。
- **建議改法**：bug-workflow 統一為「完整前置檢查（CLAUDE.md + 設定檔 + 專案註冊）」；feature-workflow 統一輕量版「檢查 CLAUDE.md 是否存在」，需完整檢查者（plan-start/plan-close/plan-sync）改用完整句式；只檢查部分項時明列項次。
- **影響的 skills**：引用 prerequisites.md 的 18 個 skill。
- **風險**：低。

#### C14｜導入統一 SKILL.md 模板（模板 A：bug-workflow／模板 B：feature-workflow）
- **問題**：段落集合、段落順序（3 種以上排列）、使用方式段有無（17/29）、Gotchas＋邊界情況段有無（24/29）不一致；7 條通用書寫規則（完整相對根路徑、四反引號巢狀 fence、禁時效性字面值、中性假例、單一資訊源、Gotcha 需有落點、旗標需有對應步驟）散落各檔各自違反。
- **建議改法**：採用 consistency.md 第二節的模板 A／B 與通用書寫規則；固定段落順序為「何時不用→鐵律→護欄→設定→前置→使用方式→流程→模式段→Gotchas→邊界情況」。保留合理個別差異：plan-explore persona 形態、plan-browse 模式制、「鐵律」段僅 bug-fix/bug-investigate、「設定檔 vs 設定目錄」命名、Gotchas 英文標題。
- **影響的 skills**：全部 29 個（plan-explore、plan-browse 部分豁免）。
- **風險**：中。一次大改動易引入回歸；建議按 plugin 分兩批，每批改完抽 3 檔逐行比對＋grep 舊句式確認 0 殘留。

#### C15｜補「何時不用」反向指引段（0/29 存在）
- **問題**：grep 全 29 檔零命中「何時不用」；6 檔被 findings 點名（bug-close、bug-fix、crew-doctor、plan-arch、plan-setup、plan-explore）；CREW 內部指令重疊多，這是最便宜的防誤用手段。
- **建議改法**：依 C14 模板為全 29 檔補 2–3 行「何時不用」段，內容與 C11 的邊界標注互相呼應。
- **影響的 skills**：全部 29 個。
- **風險**：低。

#### C16｜步驟編號整數連續化＋具名引用
- **問題**：小數插入步驟氾濫且跳號（bug-start 6.5→6.7→6.8、plan-build 7→7.3→7.5→8）；編號重複（bug-update:78-79 兩個「3.」）；編號指涉腐化（plan-build:374、plan-status:167）；plan-start:243,251 跨 plugin 引用 bug-start「步驟 6.7/6.8」鎖死重編。已實際造成至少 4 條 findings。
- **建議改法**：整數連續重編；步驟間指涉改「具名引用」（如「見『退出驗證』一節」）；跨檔引用同步更新。
- **影響的 skills**：bug-start、bug-close、bug-fix、bug-update、plan-build、plan-close、plan-db、plan-start、plan-status、plan-verify（＋跨檔引用的 plan-start↔bug-start）。
- **風險**：中。重編必須同步更新所有指涉（含跨 plugin），漏改會製造新的指涉腐化；改完 grep「步驟 [0-9]」逐一核對。

---

## 三、逐 skill 優化項（S1–S181，依嚴重度 高→中→低 排序）

> 說明：location 以 `plugins/` 為基準的相對路徑＋行號。部分項目屬跨 skill 批次項的個別實例（如 references 路徑類 → C12、觸發詞類 → C10、重複樣板類 → C1–C8），核准對應 C 項即隱含核准該批 S 項；表內仍逐條保留以供單獨否決。

| 編號 | Skill | 維度 | 嚴重度 | Location | 問題 | 建議改法 | 證據 |
|------|-------|------|--------|----------|------|----------|------|
| S1 | bug-close | reference | 高 | `bug-workflow/skills/bug-close/SKILL.md:27` | 引用 references/prerequisites.md，但 skill 目錄下無 references/，實際檔案在 plugin 根層 | 改為 ${CLAUDE_PLUGIN_ROOT}/references/prerequisites.md 或明示 plugin 根相對路徑；同一寫法出現在全部 6 個 bug-workflow skills，應整批一致修正 | ls 實測：skill 目錄僅 SKILL.md+examples/；find 確認檔案在 plugin 根 references/ |
| S2 | bug-fix | reference | 高 | `bug-workflow/skills/bug-fix/SKILL.md:21` | 引用 references/discipline-preamble.md 與 references/prerequisites.md（行42），但 skill 目錄下無 references/，實際檔案在 plugin 根目錄 references/，相對路徑無法解析 | 改用 ${CLAUDE_PLUGIN_ROOT}/references/ 或明確標注相對 plugin 根目錄的路徑 | ls 實測：skill 目錄僅 SKILL.md；find 證實兩檔在 plugin 根 references/ |
| S3 | bug-investigate | reference | 高 | `bug-workflow/skills/bug-investigate/SKILL.md:21` | SKILL.md 引用 references/discipline-preamble.md（:21）、prerequisites.md（:42）、bug-patterns.md（:174），但 skill 目錄下無 references/，實際檔案在 plugin 根目錄 | 改用 ${CLAUDE_PLUGIN_ROOT}/references/ 或 ../../references/ 明確路徑 | ls 實測：skill 目錄僅 SKILL.md；plugin 根 references/ 被引用五檔皆存在 |
| S4 | bug-setup | reference | 高 | `bug-workflow/skills/bug-setup/SKILL.md:332` | 完成訊息列出 /bug-search 指令，但 plugin 內無 bug-search skill（skills/ 僅 10 個，grep 全 plugin 只此一處） | 刪除該行，或改為指向實際存在的 /bug-investigate 或知識庫查詢方式 | grep -rn bug-search 全 plugin 僅命中 SKILL.md:332；ls skills/ 10 個目錄無 bug-search |
| S5 | bug-start | reference | 高 | `bug-workflow/skills/bug-start/SKILL.md:24` | 引用 references/prerequisites.md，但 skill 目錄下無 references/，檔案實際在 plugin 根層；此斷鏈同時使 prerequisites.md §0.5 的 Notion 後端偵測與 notion-backend.md 映射表失聯 | 改為 ${CLAUDE_PLUGIN_ROOT}/references/prerequisites.md；引用 prerequisites.md 的 sibling 有 5 個（bug-investigate/bug-close/bug-fix/bug-update/project-add），若含其他 references/*.md 相對引用則共 8 個 sibling 需一併修正 | ls skill 目錄僅 SKILL.md；find 命中 plugin 根層；grep 計 5 個 sibling 引用 prerequisites.md、8 個引用 references/ |
| S6 | bug-update | reference | 高 | `bug-workflow/skills/bug-update/SKILL.md:28` | 引用 references/prerequisites.md，但 skill 目錄下無此檔；實際位於 plugin 根目錄 references/。同一寫法出現在 6 個 skill（bug-start/bug-investigate/bug-close/bug-fix/project-add），宜整包修正。 | 改寫為 ${CLAUDE_PLUGIN_ROOT}/references/prerequisites.md 或明確的 plugin 根目錄相對路徑；不建議複製到各 skill 目錄——prerequisites.md 內部又引用 references/notion-backend.md，複製會再斷鏈且產生 6 份副本。 | ls skill 目錄僅 SKILL.md＋examples/；plugin 根 references/prerequisites.md 存在；grep 確認 6 skill 同寫法 |
| S7 | crew-doctor | reference | 高 | `bug-workflow/skills/crew-doctor/SKILL.md:121` | npm 套件 @anthropic-ai/mcp-server-playwright 不存在（npm view 回 404），修法指令照抄必失敗 | 改為實際存在的 @playwright/mcp（已驗證 npm view 回 0.0.78） | 實跑 npm view：前者 E404，@playwright/mcp 回 0.0.78 |
| S8 | crew-init | reference | 高 | `bug-workflow/skills/crew-init/SKILL.md:25` | 宣稱 anti-rationalizations.md 有「crew-init 專用」段、boundaries.md 有「crew-init」段落，grep 兩檔均無任何 crew 字樣，為死引用 | 補上兩檔對應段落，或改為只引用 discipline-preamble.md 通用紀律 | grep -i crew 兩檔均 0 hit；discipline-preamble.md 確實存在 |
| S9 | crew-upgrade | reference | 高 | `bug-workflow/skills/crew-upgrade/SKILL.md:164` | Gotchas 斷言原始碼在 ~/.claude-company/、installed_plugins.json 在 cache/ 目錄，兩者皆與實況不符（實測：檔案在 ~/.claude/plugins/ 根層，非 cache/；~/.claude-company/plugins 不存在） | 更正為實際路徑：marketplace 原始碼 ~/.claude/plugins/marketplaces/，installed_plugins.json 在 ~/.claude/plugins/ 根層 | find cache/ 無 installed_plugins.json；該檔實在 ~/.claude/plugins/ 根層；.claude-company/plugins 不存在 |
| S10 | crew-upgrade | reference | 高 | `bug-workflow/skills/crew-upgrade/SKILL.md:52` | MARKETPLACE_DIR 指向 ~/.claude-company/plugins/marketplaces/company-marketplace，實測不存在（ls 回 No such file），且無 fallback，步驟 2 的 grep 必失敗，BW_NEW/FW_NEW 取不到值 | 改為以 ~/.claude/plugins/marketplaces/company-marketplace 為主路徑，並比照步驟 1 加上兩路徑 fallback | ls 實測 .claude-company 路徑不存在；~/.claude/plugins/marketplaces/company-marketplace/plugins/*/plugin.json 存在 |
| S11 | plan | trigger | 高 | `skills/plan/SKILL.md:3` | 觸發詞「plan」為單字級且過廣，與其他 18 個 plan-* skill 名稱重疊，日常提到 plan 一詞即可能誤觸發 | 移除單字「plan」，改為「/plan」「完整規劃」「全部規劃」等指令級或片語級觸發詞 | Read 確認第 3 行含「plan」單字觸發詞；ls skills/ 計 19 個 skill（其他 18 個皆 plan-*）。移除後 /plan 斜線指令與既有片語觸發不受影響 |
| S12 | plan-close | reference | 高 | `feature-workflow/skills/plan-close/SKILL.md:140` | plan-deploy-confirm:38 宣稱 plan-close 會自動建立「🚀 部署狀態」區塊，但本檔全文無此區塊（grep 0 hit） | 步驟 5-2 同步 deploy.sql 時一併建立「🚀 部署狀態」區塊並預設「待執行」 | grep 部署狀態 plan-close SKILL.md exit 1；plan-deploy-confirm:38 原文屬實 |
| S13 | plan-close | reference | 高 | `feature-workflow/skills/plan-close/SKILL.md:233` | .gitignore 用 `.spec/` 排除整個目錄後，`!.spec/{slug}/` 無效，git add 會被拒（已實測驗證） | 改為 plan-start 寫 `.spec/*`＋此處加 `!.spec/{slug}/`，或改用 `git add -f .spec/{slug}/` | temp repo 實測：.spec/+! 時 git add exit 1；.spec/* 變體與 -f 均成功。plan-start:146-150 確寫 .spec/ |
| S14 | plan-close | reference | 高 | `feature-workflow/skills/plan-close/SKILL.md:241` | 步驟 9 只更新 _index.md，未寫回 README.md 的 status；plan-deploy-confirm:49 靠 README「status: 已結案」掃描任務 | 步驟 9 增加更新 `.spec/{slug}/README.md` 的 status 欄位為結案狀態 | grep status plan-close 0 hit（不寫 README）；deploy-confirm:49 確依 status: 已結案 掃描 |
| S15 | plan-demo | reference | 高 | `feature-workflow/skills/plan-demo/SKILL.md:17` | 宣稱 anti-rationalizations.md 與 boundaries.md 有「plan-demo 專用」段落，grep 實測兩檔皆無 demo 字樣（exit=1） | 在兩個 reference 檔補上 plan-demo 段落，或刪除此引用改為通用紀律 | 親自重跑 grep -in demo 兩檔均 exit=1、0 hit，段落確不存在 |
| S16 | plan-deploy-confirm | reference | 高 | `feature-workflow/skills/plan-deploy-confirm/SKILL.md:18` | 引用 anti-rationalizations.md「plan-deploy-confirm 專用」與 boundaries.md「plan-deploy-confirm」段落，兩檔實際皆無此段 | 在兩個 reference 檔補上對應段落，或刪除本行引用 | grep plan-deploy-confirm 兩檔 0 hit；段落標題僅有 plan-build/review/verify/security |
| S17 | plan-deploy-confirm | reference | 高 | `feature-workflow/skills/plan-deploy-confirm/SKILL.md:38` | 宣稱 plan-close 會自動建立「🚀 部署狀態」區塊，但全 plugin 僅本 skill（及 README.md 對本 skill 的描述）提及此名；plan-close 實建「🚀 上線前置作業」與「🗄️ 資料庫設計 → 部署 SQL」子區塊，步驟 5 寫入目標不存在 | 統一區塊名：改寫入 plan-close 實建的區塊，或讓 plan-close 明文建立「🚀 部署狀態」區塊 | grep 全 plugin：「部署狀態」僅本 skill 與 README:98；plan-close:50-51,140-142 建的是上線前置作業＋部署 SQL 子區塊 |
| S18 | plan-explore | trigger | 高 | `feature-workflow/skills/plan-explore/SKILL.md:3` | 觸發詞「想一下」「討論一下」「分析一下」為日常用語，極易在非規劃情境誤觸發 | 刪除單詞級口語觸發詞，改為情境限定詞如「規劃前探索」「釐清需求」「比較技術方案」；保留 /plan-explore、「探索」等明確詞 | Read SKILL.md:3 確認三個口語詞原文存在於 description |
| S19 | plan-next | reference | 高 | `feature-workflow/skills/plan-next/SKILL.md:128` | 結案偵測比對 README 的「status: closed」，但 plan-start/plan-close 全用中文狀態（需求分析/進行中/已完成），全 plugin 無 closed 值，此規則永不命中 | 改判 status: 已完成，或改讀 _index.md 的「已完成」區段 | grep -r closed 全 skills 僅 plan-next 自身；plan-close:85 寫「已完成」、:246 _index 用「已完成」區段 |
| S20 | plan-next | reference | 高 | `feature-workflow/skills/plan-next/SKILL.md:19` | 宣稱 anti-rationalizations.md 有「plan-next 專用」、boundaries.md 有「plan-next」段落，實際兩檔 grep 'plan-next' 均 0 命中 | 在兩個 references 檔補上 plan-next 段落，或刪除此指標句只留通用 preamble | 重跑 grep 'plan-next' 於兩檔均 exit=1（0 命中），檔案存在但無該段落 |
| S21 | plan-security | reference | 高 | `feature-workflow/skills/plan-security/SKILL.md:78` | L1-SQL-1 pattern '\\$\\{' 照抄執行匹配不到任何 ${}（實測 BSD grep exit 1、ugrep 直接報錯），SQL injection 主規則失效 | 改為 grep -rn -F '${'（已實測可匹配 MyBatis ${id}），並補「pattern 需實測」註記 | 自建 ${id} 測試檔：BSD grep 照抄 exit=1；-F '${' exit=0 命中 |
| S22 | plan-sync | reference | 高 | `feature-workflow/skills/plan-sync/SKILL.md:43` | 引用「/plan-start 步驟 5」建立 Notion 條目，但 plan-start 中建立 Notion 條目實為步驟 6，步驟 5 是偵測負責人 | 改為「/plan-start 步驟 6（建立 Notion 條目）」，或改引用段落名稱避免編號腐化 | grep plan-start/SKILL.md：行 82「### 5. 偵測負責人」、行 97「### 6. 建立 Notion 條目」 |
| S23 | plan-verify | structure | 高 | `skills/plan-verify/SKILL.md:183` | 自稱預設 Playwright MCP，但 MCP 模式工具名全是 chrome-devtools 的（click/take_snapshot/list_pages） | 統一改用 Playwright 的 browser_* 工具名，或明寫兩套 MCP 各自的工具對照 | L183/240 用 click、take_snapshot、list_pages（chrome-devtools 名）；L524 Gotchas 反用 browser_* 名，自相矛盾 |
| S24 | plan-verify | reference | 高 | `skills/plan-verify/SKILL.md:36` | 安裝指令套件 @anthropic-ai/mcp-server-playwright 不存在（npm 404 實測） | 改為 @playwright/mcp（實測 0.0.78 存在），並修正「Anthropic 官方維護」為 Microsoft | npm view 重跑：@anthropic-ai/mcp-server-playwright 回 E404；@playwright/mcp 回 0.0.78 |
| S25 | project-add | reference | 高 | `bug-workflow/skills/project-add/SKILL.md:14` | 引用 references/prerequisites.md 為相對路徑，但 skill 目錄下無 references/（實際在 plugin 根層；find 驗證 skill 目錄僅 SKILL.md） | 改用 ${CLAUDE_PLUGIN_ROOT}/references/prerequisites.md；line 298 的 project-page-templates.md 同步修正。注意：全 plugin 10 個 skill 皆用同一相對路徑慣例，建議一併修正而非只改此 skill | ls 證實 skill 目錄僅 SKILL.md，references/ 在 plugin 根層；grep 見 :14、:298 |
| S26 | bug-close | reference | 中 | `bug-workflow/skills/bug-close/SKILL.md:110` | notion-search/notion-update-page 未用完整 Server:tool 名；環境有 notion-local 與 claude.ai Notion 兩套，名稱僅對應後者 | 寫完整 MCP 工具名並註明用哪套 server；update_content/replace_content（176、283）非頂層工具名，應註明其為 notion-update-page 的參數或改寫 | 比對環境工具清單：notion-local 全為 API-* 命名；update_content/replace_content 無對應頂層工具 |
| S27 | bug-close | reference | 中 | `bug-workflow/skills/bug-close/SKILL.md:229` | 學習寫入路徑硬編碼 ~/.claude-company/，但設定檔（14-16 行）支援 ~/.claude/ 個人環境雙路徑 fallback | 改為與設定檔相同的雙路徑 fallback；references/learnings-schema.md:6,53 同樣硬編碼，需一併修正 | ls 實測：~/.claude/bug-workflow-config.md 存在、~/.claude-company/ 無 config；grep 證實 learnings-schema.md 同樣硬編碼 |
| S28 | bug-close | trigger | 中 | `bug-workflow/skills/bug-close/SKILL.md:3` | 觸發詞「結案」與 plan-close（任務結案/功能完成結案）重疊；「修完了」單詞過廣易誤觸發 | 收斂為「bug 結案」「關閉 bug」等帶 bug 語境的詞組，description 補「僅適用已用 /bug-start 建檔的 Bug」以區隔 plan-close | 比對兩 skill description：「結案」為 plan-close 觸發詞「任務結案」之子字串，確有撞詞 |
| S29 | bug-close | token | 中 | `bug-workflow/skills/bug-close/SKILL.md:53` | Step 1.5 Merge 引導約 50 行（53-104），且與 Gotchas（288-291）、邊界情況（304-307）三處重複敘述 merge 規則 | 下放到 references/merge-guide.md（路徑寫法需配合發現 1 的修正），SKILL.md 只留觸發條件與入口指標，重複的 gotcha/邊界條目合併 | 讀檔核對：行 89↔290↔304（衝突）、90↔291（不 push）、100-104↔289↔305（dev_branch）三處重述 |
| S30 | bug-fix | structure | 中 | `bug-workflow/skills/bug-fix/SKILL.md:141` | 編譯檢查只偵測 pom.xml/build.gradle（Java），非 Java 專案（Node/前端）無對應指令，流程出現缺口且無 fallback 說明 | 補「偵測不到 build 指令時」的分支：讀 package.json scripts 或標記跳過並在 Notion 註明 | 行143-144 僅兩條 Java 指令；邊界情況段（273-285）無此分支；config.template.md:47 根因分類含「前端UI」證明非 Java 在範圍內 |
| S31 | bug-fix | reference | 中 | `bug-workflow/skills/bug-fix/SKILL.md:22` | anti-rationalizations.md、boundaries.md 無任何路徑前綴，agent 無法定位（檔案與段落實測存在於 plugin 根 references/） | 補上完整路徑前綴，與行 21 一致 | grep 實測：anti-rationalizations.md:22「## bug-fix 專用」、boundaries.md:25「## bug-fix」皆存在 |
| S32 | bug-fix | trigger | 中 | `bug-workflow/skills/bug-fix/SKILL.md:3` | 觸發詞含單字級「修復」，任何提到修復（設定、文件、資料）的對話都可能誤觸發；「修 bug」「fix bug」也與 investigate skill 觸發範圍重疊 | 刪除單字「修復」，改描述情境：根因已調查完成、要開始修復並產迴歸測試時使用 | Read 行3 確認「修復」為獨立觸發詞；investigate skill 描述含 fix this bug |
| S33 | bug-investigate | structure | 中 | `bug-workflow/skills/bug-investigate/SKILL.md:150` | ```markdown 範例區塊內再嵌 ``` 內層 fence，外層 fence 提前閉合，Markdown 結構壞損 | 兩處（150-170、283-298）外層改用四個反引號包住含內層 fence 的範例 | grep fence：L150 外層被 L154 內層 ``` 提前閉合；L283 被 L297 誤閉、L298 開出流浪區塊 |
| S34 | bug-investigate | trigger | 中 | `bug-workflow/skills/bug-investigate/SKILL.md:3` | 觸發詞含單字級「investigate」，與環境中 gstack investigate、superpowers:systematic-debugging 觸發範圍重疊，易誤觸發 | 移除裸字 investigate，保留 bug-investigate 與中文觸發詞；補「有 Notion Bug 條目、需根因調查時」情境限定 | SKILL.md:3 含裸字；本環境技能清單同時存在 investigate(gstack) 與 systematic-debugging |
| S35 | bug-investigate | reference | 中 | `bug-workflow/skills/bug-investigate/SKILL.md:93` | 要求用 rtk proxy 指令且稱「遵循 CLAUDE.md 規範」（:92-93、:398），但 rtk 不存在，全域 CLAUDE.md/rules/hooks 皆無 RTK 條目 | 刪除 RTK 相關指示（含 :398 Gotcha），或改為「偵測到 rtk 存在時才使用」的條件式寫法 | which rtk → not found；grep -i rtk 於 CLAUDE.md/rules/settings/hooks 0 命中 |
| S36 | bug-setup | token | 中 | `bug-workflow/skills/bug-setup/SKILL.md:122` | 步驟 2-3 的 15 列欄位表與 db-templates.md「A. 專案資料庫」Schema 重複，且已出現漂移（Name vs 專案名稱） | 內文只留「必要/建議/選用」分級清單（db-templates 無此分級資訊，須保留），完整 schema 下放 references 單一來源 | 逐欄比對兩表：15 欄位同構重複，Title 欄名已漂移 |
| S37 | bug-setup | structure | 中 | `bug-workflow/skills/bug-setup/SKILL.md:124` | 專案資料庫 Title 欄位在內文表寫「專案名稱」，db-templates.md:49 寫「Name」，兩處 schema 不一致會導致欄位驗證/補齊分歧；SKILL.md:161 View 排序又用「Name」，內文自身也矛盾 | 統一以 db-templates.md 為單一權威，內文改為引用並修正欄位名 | SKILL.md:124=「專案名稱\|Title」、:161=「Name 降序」；db-templates.md:49=「\| Name \| title \|」 |
| S38 | bug-setup | reference | 中 | `bug-workflow/skills/bug-setup/SKILL.md:83` | 引用 references/db-templates.md、config.template.md（共 6 處：83/109/158/168/201/296），實檔在 plugin 根目錄 references/；skills/bug-setup/ 下無 references/，相對路徑無明確錨定（執行時 cwd 是使用者專案） | 改用 ${CLAUDE_PLUGIN_ROOT}/references/... 明確錨定；注意全 plugin 10 個 skill 皆同此寫法，宜一併修正 | ls：skills/bug-setup/ 僅 SKILL.md；db-templates.md 等 10 檔實在 plugin 根 references/ |
| S39 | bug-start | token | 中 | `bug-workflow/skills/bug-start/SKILL.md:231-360` | 6.7 自動關聯 Feature 與 6.8 偵測 Feature Branch 兩節共 130 行細節流程佔全檔 403 行約 1/3，兩節皆有「不阻擋流程」降級設計，屬選配增強而非主流程 | 下放至 references/feature-linking.md（以 ${CLAUDE_PLUGIN_ROOT} 引用），SKILL.md 留 5 行摘要與觸發條件；注意 feature-workflow/plan-start/SKILL.md:243,251 跨 plugin 引用「/bug-start Step 6.7/6.8」需同步改指向新位置 | L231-360 共 130 行/403 行；兩節皆標「不阻擋流程」；grep 發現 plan-start 跨 plugin 引用 |
| S40 | bug-start | trigger | 中 | `bug-workflow/skills/bug-start/SKILL.md:3` | 觸發詞「開始修 bug」與 bug-fix 的「修 bug／修復」語意重疊（「修 bug」為其子字串），使用者說這句時多半想直接修而非建 Notion 條目，易誤觸發 | 移除「開始修 bug」改用建檔語意詞（開 bug 單、通報 bug、bug 立案），或在 description 註明與 bug-fix 的分工（較保守，不影響既有觸發） | bug-fix description 觸發詞含「修 bug」「修復」，與「開始修 bug」碰撞屬實 |
| S41 | bug-update | reference | 中 | `bug-workflow/skills/bug-update/SKILL.md:45` | notion-search/notion-fetch/notion-update-page 共 8 處用短名（原報告誤計 7），未寫完整 Server:tool 名；notion-local MCP 無這些工具（其為 API-* 系列），短名僅存在於 claude.ai Notion 連接器，headless/排程環境會失效。 | 改用完整 MCP 工具名並標明依賴 claude.ai Notion 連接器，或提供 notion-local（API-*）對應工具映射。 | grep 計數 search 2＋fetch 2＋update-page 4＝8 處；工具清單實查 notion-local 僅 API-*，短名屬 claude_ai_Notion |
| S42 | bug-update | reference | 中 | `bug-workflow/skills/bug-update/examples/update-patterns.md:1` | examples/update-patterns.md（120 行）在 SKILL.md 乃至整個 plugin 零引用，永遠不會被載入。 | 在「判斷更新類型」段加一行指標連到此檔，或直接刪除。 | wc -l 確認 120 行；grep -rn update-patterns 於 plugin 全目錄 0 hits（exit=1） |
| S43 | crew-doctor | reference | 中 | `bug-workflow/skills/crew-doctor/SKILL.md:16` | 宣稱 anti-rationalizations.md 與 boundaries.md 有「crew-doctor 專用」段落，實際 grep -i doctor 兩檔皆 0 hit | 在兩個 reference 檔補 crew-doctor 段落，或刪除此引用句 | grep -in doctor 兩檔（37/79 行）皆 0 hit，exit 1 |
| S44 | crew-doctor | trigger | 中 | `bug-workflow/skills/crew-doctor/SKILL.md:3` | 觸發詞「為什麼壞了」「sanity check」過廣，使用者回報程式壞掉時易誤觸發環境健診而非 bug-investigate/investigate | 收斂為「CREW 為什麼壞了」「CREW 環境檢查」等帶限定詞的觸發句 | description 確含該二詞；investigate skill 觸發詞含 why is this broken，確有重疊 |
| S45 | crew-doctor | structure | 中 | `bug-workflow/skills/crew-doctor/SKILL.md:95` | 進階檢查前置條件自相矛盾：61 行寫「紅燈全綠時才跑」，95 行寫「僅當 #3 通過時」跑 | 統一為一種條件（建議：#3 Notion 通過即可跑 #15-17，與 98 行邏輯一致） | Read 確認 61 行與 95/98 行條件不同；185 行輸出範例採 #3 邏輯，建議方向一致 |
| S46 | crew-init | trigger | 中 | `bug-workflow/skills/crew-init/SKILL.md:3` | 觸發詞「首次設定」同時出現在 bug-setup 與 plan-setup 的 description（原報告稱 plan-demo 也有，經查其 description 無此詞），三個 skill 觸發範圍重疊易誤觸發 | crew-init 保留「一鍵設定」「crew-init」等獨有詞，說明與單一 setup 的分工差異 | bug-setup:3、plan-setup:3 含「首次設定」；plan-demo description 無，僅內文 |
| S47 | crew-init | structure | 中 | `bug-workflow/skills/crew-init/SKILL.md:44-50` | 前置檢查表只列 3 項，內文卻寫「只跑必要 5 項」，且 crew-doctor 定義必要項為 8 項，三處數字互相矛盾 | 統一數字：表格列滿實際要檢查的項目，行 50 改為與表格一致的項數 | 表列 3 項（44-48）、行 50 寫 5 項、crew-doctor:32 定義必要 8 項 |
| S48 | crew-init | reference | 中 | `bug-workflow/skills/crew-init/SKILL.md:93-98` | 階段 2a 只檢查兩個階層式 config 路徑，漏掉 plan-setup 明列的舊單一檔格式（feature-workflow-config.md），舊使用者會被誤判未設定而重跑（plan-setup 會轉入遷移提示，非全新設定） | 偵測清單補上兩個舊格式路徑，或改為引用 config-resolver.md 的解析順序 | plan-setup:27-31、config-resolver.md:32-33 均列舊路徑，crew-init 未列 |
| S49 | crew-upgrade | reference | 中 | `bug-workflow/skills/crew-upgrade/SKILL.md:29` | 步驟 1 主路徑 ~/.claude-company/plugins/installed_plugins.json 不存在（實測 No such file），每次都靠 fallback 救回，主路徑是死碼 | 把 ~/.claude/plugins/installed_plugins.json 改為主路徑；.claude-company 若為公司機需求則加註說明 | ls 實測主路徑不存在（~/.claude-company 只有 bug-workflow/learnings）；fallback 路徑存在且含目標 key |
| S50 | crew-upgrade | trigger | 中 | `bug-workflow/skills/crew-upgrade/SKILL.md:3` | 觸發詞「更新 plugin」過廣，使用者要更新 superpowers、playwright 等任何非 CREW plugin 時會誤觸發本 skill | 改為「更新 CREW plugin」或刪除該泛用觸發詞，保留 crew-upgrade／更新 crew 等具體詞 | 重讀第 3 行 description 確含「更新 plugin」；本機另裝 16 個 marketplace，誤觸發面大；其餘觸發詞已足夠覆蓋 |
| S51 | crew-upgrade | structure | 中 | `bug-workflow/skills/crew-upgrade/SKILL.md:53-55` | 步驟 2 目錄不存在時只 echo「嘗試 git fetch...」，實際未給任何 fetch 或替代指令，隨後仍對缺失路徑 grep，錯誤處理是死路 | 目錄不存在時明確中止並指示執行 claude plugin marketplace add（與 175 行邊界情況一致），不要繼續往下 grep | 重讀 53-59 行：if 區塊僅 echo 無動作，58-59 行照常 grep；175 行邊界情況與之矛盾 |
| S52 | plan | reference | 中 | `skills/plan/SKILL.md:26` | 引用 references/plan-common.md，但檔案實際位於 plugin 根目錄而非 skill 目錄，從 skills/plan/ 相對解析不到（find 驗證：僅 feature-workflow/references/plan-common.md 存在，skills/plan/ 下無 references/） | 改用 ${CLAUDE_PLUGIN_ROOT}/references/plan-common.md 或 ../../references/plan-common.md 明確路徑（全 plugin 17 個 skill 同病，宜統一修） | ls 確認 skills/plan/ 僅有 SKILL.md；find 僅在 plugin 根 references/ 找到 plan-common.md；grep 統計 19 個 skill 中 17 個引用 references/（plan-browse、plan-explore 除外），故同病數修正為 17 |
| S53 | plan-arch | reference | 中 | `feature-workflow/skills/plan-arch/SKILL.md:14` | 引用 references/prerequisites.md 與 plan-common.md 為相對路徑，skill 目錄下無 references/，實際檔案在 plugin 根目錄 | 改為 ${CLAUDE_PLUGIN_ROOT}/references/... 或明確絕對定位說明；全 plugin 至少 6 個 skill 同寫法，宜統一修 | 重跑 ls：skills/plan-arch/ 僅 SKILL.md、無 references/；plugin 根 references/ 兩檔皆在。grep 證實 6 個 skill 同用相對路徑、全 plugin 無 CLAUDE_PLUGIN_ROOT |
| S54 | plan-arch | structure | 中 | `feature-workflow/skills/plan-arch/SKILL.md:29` | 步驟 2 宣稱「prompt 指示如下」但僅給輸入/輸出來源；arch.md 規格只有 :37 一行括號列 4 元素，無各段最低要求與驗收/自檢清單，opus subagent 產出形狀不受控 | 補 arch.md 章節契約（Mermaid 圖、類別清單、介面定義、設計模式各段的最低要求）與交付前自檢清單，比照 plan-spec 的「Agent 額外指示」區塊 | Read :29-39 屬實；對照 plan-spec:38-63 有「Agent 額外指示」契約而 plan-arch 無；build-context-layers.md:21-26 依「類別清單/介面定義」段落擷取 arch.md，形狀不控會影響下游 |
| S55 | plan-arch | trigger | 中 | `feature-workflow/skills/plan-arch/SKILL.md:3` | 觸發詞「架構」「arch」單字級過廣，日常討論架構或使用 java-design-advisor（同樣以 architecture 觸發）時易誤觸發 | 收斂為組合詞（如「架構設計文件」「產出 arch.md」），保留「plan-arch」「架構設計」精確觸發，並補「已有 .spec/ 任務」情境限定 | Read 確認 :3 含單字「架構」「arch」；skill 清單中 java-design-advisor 確以 architecture 觸發，重疊屬實。/plan-arch 顯式呼叫不受收斂影響 |
| S56 | plan-browse | trigger | 中 | `SKILL.md:3` | 觸發詞含單字級「browse」，環境有多套瀏覽器工具，講「browse 網頁」時易誤觸發 | 移除單字「browse」或改為「plan browse」「browse spec」等組合詞 | Read SKILL.md:3 確認 description 含獨立「browse」；其餘觸發詞仍在，移除無漏觸發風險 |
| S57 | plan-browse | token | 中 | `SKILL.md:41` | 模式 1 要求讀取每個任務的 README 與所有設計文件才產總覽，任務多時 token 成本高 | 總覽只讀 README frontmatter 與 spec.md 開頭摘要，選定後才深讀；總覽範本的 DB/架構欄位（來自 db.md/arch.md）需同步簡化，否則填不出來 | Read SKILL.md:41 屬實；但 49-56 行總覽框含 DB/架構欄位，故 suggestion 補註範本需同步調整 |
| S58 | plan-browse | token | 中 | `SKILL.md:44-251` | 六個模式各附完整 ASCII 輸出範本，約 180 行佔全文六成，觸發即載入昂貴 | 每模式留 3-5 行格式要點，完整範例下放 references/examples.md | 實測全文 286 行，六個範本區塊合計約 181 行（63%）；plan-spec 已有 references/ 慣例可循 |
| S59 | plan-build | structure | 中 | `feature-workflow/skills/plan-build/SKILL.md:188` | 流程編號不連續：7（行 156）→ 7.3（行 188）→ 7.5（行 230）→ 8（行 306），缺 7.1/7.2/7.4，agent 可能誤判有遺漏步驟 | 重新編號為連續步驟（7、8、9、10）或明註為插入式子步驟 | Read 確認標題序列 7→7.3→7.5→8，無 7.1/7.2/7.4 |
| S60 | plan-build | trigger | 中 | `feature-workflow/skills/plan-build/SKILL.md:3` | 觸發詞「build」與「產生程式碼」過廣：npm build、gradle build、一般寫碼請求都可能誤觸發，且未走 .spec/ 流程的情境不適用 | 改為「plan-build」「從 spec 產生程式碼」等組合詞，並加「需已有 .spec/ 設計文件」限定 | Read 行 3 確認含「build」「產生程式碼」；保留 plan-build 觸發詞無漏觸發副作用 |
| S61 | plan-build | token | 中 | `feature-workflow/skills/plan-build/SKILL.md:308-364` | 步驟 8 兩個回傳模板（含測試/跳過測試）約 90% 重複，僅統計行與 test-engineer 行不同，浪費約 25 行 | 合併為單一模板，test-engineer 那行用 {條件} 標記切換 | 逐行比對行 310-335 與 339-364，僅 2 行內容差異 |
| S62 | plan-build | reference | 中 | `feature-workflow/skills/plan-build/SKILL.md:36` | 8 處引用 references/*.md 以相對路徑書寫（行 36/42/83/117/121/140/152/372），但 skills/plan-build/ 下無 references/ 目錄（僅 SKILL.md 與 examples/），7 個被引用檔實際在 plugin 根目錄 references/ | 改用 ${CLAUDE_PLUGIN_ROOT}/references/ 或明註「plugin 根目錄下」避免解析失敗 | grep -n references/ 得 8 行；ls 確認 skill 目錄無 references/，7 檔皆在 ../../references/ |
| S63 | plan-close | reference | 中 | `feature-workflow/skills/plan-close/SKILL.md:128` | notion-fetch 等工具名僅對應 plugin 後端；prerequisites.md:106 指向的映射表 references/notion-backend.md 不存在（ls 驗證） | 補建 notion-backend.md 映射表，或在內文附 notion-local（API-*）對應工具名 | find . -name 'notion-backend*' 全 plugin 0 hit；prerequisites.md:106 確引用該檔 |
| S64 | plan-close | reference | 中 | `feature-workflow/skills/plan-close/SKILL.md:14` | `references/config-resolver.md` 為相對路徑，skill 目錄下無此檔（實際在 plugin 根 references/），agent 需自行猜測位置 | 改用 `${CLAUDE_PLUGIN_ROOT}/references/config-resolver.md` 絕對化（行 29 prerequisites.md 同理）；注意全 plugin 皆同此寫法，宜整批修 | ls skill 目錄僅 SKILL.md；檔案在 plugin 根 references/；全 plugin 無 CLAUDE_PLUGIN_ROOT 用例 |
| S65 | plan-close | structure | 中 | `feature-workflow/skills/plan-close/SKILL.md:267` | 步驟 10 後續事項未提示 deploy.sql 存在時應執行 /plan-deploy-confirm，部署回流鏈在此斷掉 | deploy.sql 存在時於後續事項加一行「執行 SQL 後跑 /plan-deploy-confirm 回報」 | grep plan-deploy-confirm plan-close SKILL.md exit 1；行 267-269 僅列測試驗證與 Git 合併 |
| S66 | plan-db | reference | 中 | `feature-workflow/skills/plan-db/SKILL.md:14,25,43,51,57` | 引用路徑 references/plan-common.md、references/prerequisites.md 相對 skill 目錄不存在；實際檔案在 plugin 根層 references/，且全 plugin 無 ${CLAUDE_PLUGIN_ROOT} 用法可依循 | 改寫為 ${CLAUDE_PLUGIN_ROOT}/references/... 或 ../../references/...；注意同 plugin 6 個 skill（plan/plan-start/plan-verify/plan-spec/plan-arch/plan-db）皆同模式，宜一併修 | ls 實證 skills/plan-db/ 僅有 SKILL.md；grep 確認行號與全 plugin 零 CLAUDE_PLUGIN_ROOT |
| S67 | plan-demo | reference | 中 | `feature-workflow/skills/plan-demo/SKILL.md:136` | 引導指令 ls plugins/feature-workflow/skills/ 只在 marketplace repo 內有效，評估者專案目錄不存在此路徑 | 改為實際安裝路徑或改用 /help、skill 清單等與 cwd 無關的指引 | L136 確有此指令；plugin 實裝於 ~/.claude/plugins/，評估者專案 cwd 無 plugins/ |
| S68 | plan-demo | reference | 中 | `feature-workflow/skills/plan-demo/SKILL.md:151` | 宣稱 /plan-status 會標示 [DEMO] 並排末尾、分組顯示（L202 同），但 plan-status SKILL.md grep demo 為 0 hit | 在 plan-status 補 demo 分組邏輯，或改寫為「demo 條目照常列出」不做承諾 | 親自重跑 grep -in demo skills/plan-status/SKILL.md exit=1 |
| S69 | plan-demo | structure | 中 | `feature-workflow/skills/plan-demo/SKILL.md:26` | --keep 說明「預設清理會在 demo 結束時清除」與 §4「預設不自動清理」直接矛盾 | 統一為「預設不清理」，修改第 26 行 --keep 的括號說明或移除該旗標 | 重讀 L26 vs L150/L153：L153 自承 --keep 效果與預設相同，矛盾成立 |
| S70 | plan-demo | trigger | 中 | `feature-workflow/skills/plan-demo/SKILL.md:3` | description 觸發詞含單字級「demo」「示範」「試跑」「dry-run」，使用者提無關 demo（如做 demo 頁面）易誤觸發 | 改為組合詞：「CREW demo」「評估 CREW」「plan-demo」，刪除單字級觸發詞 | L3 實含 4 個單字級觸發詞；保留 plan-demo／評估 CREW 仍涵蓋原始情境 |
| S71 | plan-demo | structure | 中 | `feature-workflow/skills/plan-demo/SKILL.md:91` | 2c–2f（db/arch/files/verify 範本）僅一句話描述，L196 稱「prompt 內 inline」但實際只有 spec.md 有範本，產出品質不穩 | 為 db/arch/files/verify 各補最小範本，或下放到 references/demo-templates.md | 重讀 L91-105 各節僅一行；「範例內容」節 L157-196 只含 spec.md 範本 |
| S72 | plan-deploy-confirm | reference | 中 | `feature-workflow/skills/plan-deploy-confirm/SKILL.md:228` | Gotcha 建議「用 /plan-sync 重新同步補上區塊」，但 plan-sync 無建立「🚀 部署狀態」區塊的邏輯，修法不可執行 | 與第 1 條一併修正：在 plan-sync/plan-close 加入該區塊邏輯後再指向 | grep plan-sync/SKILL.md「部署狀態」0 hit；其映射表僅 deploy.sql→資料庫設計子區塊、deploy-checklist→上線前置作業 |
| S73 | plan-deploy-confirm | structure | 中 | `feature-workflow/skills/plan-deploy-confirm/SKILL.md:39` | 前置條件要求設定檔含「任務追蹤工具」資料庫 ID，但未指引如何讀取（plan-sync/plan-close/plan-stack/plan-start/plan-setup 均引用 references/config-resolver.md） | 比照 plan-close 加一行「依 references/config-resolver.md 讀取設定」 | grep config-resolver：5 個 skill 有引用，本 skill 0 hit |
| S74 | plan-deploy-confirm | reference | 中 | `feature-workflow/skills/plan-deploy-confirm/SKILL.md:49` | 本地偵測依 README.md `status: 已結案`，但 plan-close 只更新 _index.md 與 Notion 狀態，無任何把 README status 寫為已結案的步驟，條件恐永不成立 | 改以 Notion 狀態或 _index.md「已完成」區段為準，或在 plan-close 增加寫回 README status 的步驟 | grep：plan-close 無「已結案」「更新 README status」；其步驟 9 僅移 _index.md；其他 skill 寫的 status 值皆非已結案 |
| S75 | plan-explore | token | 中 | `feature-workflow/skills/plan-explore/SKILL.md:180-278` | 「不同進入情境的處理」四段完整範例對話近 100 行含大型 ASCII 圖，對執行幫助有限 | 保留一個最短範例，其餘下放 references/examples.md 延遲載入 | Read 確認 180-278 為四段範例共 99 行；skill 目錄僅 SKILL.md 一檔，無 references/ |
| S76 | plan-explore | trigger | 中 | `feature-workflow/skills/plan-explore/SKILL.md:3` | 觸發範圍與 model-thinking（幫我分析）、superpowers:brainstorming（creative work 前必用）明顯重疊 | description 明示適用邊界：限 CREW 規劃流程（.spec/ 任務）前後的探索，其餘不觸發 | 比對本 session 可用 skill 清單，兩者觸發語意確實與「分析一下」重疊 |
| S77 | plan-next | reference | 中 | `feature-workflow/skills/plan-next/SKILL.md:124` | 推薦重跑「/plan-start --resume」，但 plan-start SKILL.md 不支援 --resume 旗標 | 改為推薦重跑 /plan-start <任務名>，或先在 plan-start 實作 --resume | grep -rn -- --resume 全 skills 僅 plan-next:124 一處命中，plan-start 無此旗標 |
| S78 | plan-next | trigger | 中 | `feature-workflow/skills/plan-next/SKILL.md:3` | description 觸發詞「下一步」「接下來」「該做什麼」為日常高頻詞，任何對話說「接下來…」都可能誤觸發 | 限定情境：改為「詢問 CREW/plan 任務流程的下一步」並保留 plan-next 等專名觸發詞 | Read SKILL.md:3 確認三個裸觸發詞存在；保留專名觸發詞則無漏觸發副作用 |
| S79 | plan-review | structure | 中 | `feature-workflow/skills/plan-review/SKILL.md:16` | 環境變數只寫「同 plan-build」未給變數名；行 264 說「顯示設定指引」但本文無指引，單獨觸發時不自足，且未提未設定會靜默失敗 | 明寫 CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 與靜默失敗警告，或指向 references 檔 | grep：變數名與靜默失敗警告僅在 plan-build/SKILL.md:20,384；plan-review 本文 0 hit |
| S80 | plan-review | structure | 中 | `feature-workflow/skills/plan-review/SKILL.md:211` | 報告模板 Reviewer 欄枚舉為 {logic/quality/security}，與實際三軸（logic/quality/performance）不符，security 屬 plan-security | 改為 {logic/quality/performance} | Read 行 211 確為 {logic/quality/security}；行 94/116/131 三軸為邏輯/品質/效能 |
| S81 | plan-review | trigger | 中 | `feature-workflow/skills/plan-review/SKILL.md:3` | 觸發詞「code review」「程式碼審查」與環境內建 code-review、java-code-review skill 明顯重疊，非 .spec 流程的一般審查請求會誤觸發 | description 加情境限定，如「審查 .spec/ 任務產出的程式碼時使用」，保留 plan-review 專名觸發 | 行 3 含該二觸發詞；本環境 skill 清單確有 code-review 與 java-code-review |
| S82 | plan-review | structure | 中 | `feature-workflow/skills/plan-review/SKILL.md:57` | prod_branch 回退邏輯兩處不一致：行 57 直接嘗試 production→master→main，行 257 多了先取 origin/HEAD 的步驟 | 統一為含 origin/HEAD 的完整回退邏輯，只在一處寫死、另一處引用 | Read 行 57 與 257 逐字比對，行 257 確實多「先取 origin/HEAD」步驟 |
| S83 | plan-security | reference | 中 | `feature-workflow/skills/plan-security/SKILL.md:14` | references/prerequisites.md、discipline-preamble.md 等路徑自 SKILL.md 目錄解析不存在（skills/plan-security/ 下只有 SKILL.md，實際檔案在 plugin 根 references/） | 改用 ${CLAUDE_PLUGIN_ROOT}/references/… 或 ../../references/…；此為全 plugin 共通問題，宜統一修 | ls 證實 skill 目錄僅 SKILL.md；4 檔均在 plugin 根 references/；8+ skills 同寫法 |
| S84 | plan-security | trigger | 中 | `feature-workflow/skills/plan-security/SKILL.md:3` | 單字級觸發詞「security」過廣，與內建 security-review skill 及一般 Spring Security 討論重疊，易誤觸發 | 移除單字「security」，收斂為「掃描安全漏洞」等片語，並在 description 限定 .spec/ 工作流情境 | description 含單字「security」；本環境確有內建 security-review skill 並存 |
| S85 | plan-setup | token | 中 | `SKILL.md:119-136` | 3-4 段的工作區頁面更新步驟與 db-templates.md:203「更新步驟（plan-setup 追加功能設計庫時）」重複（兩處並存） | SKILL.md 保留一句指標指向 db-templates.md E 段，刪除重複的 markdown 片段與排版順序清單（保留 :135-136 兩條跳過條件） | Read db-templates.md:203-214：更新步驟與排版順序兩段與 SKILL.md 3-4 內容重複 |
| S86 | plan-setup | reference | 中 | `SKILL.md:146` | Agent 名稱寫 spec-analyst 等 4 個，實際檔案為 feature-spec-analyst.md 等，且未寫來源路徑與安裝目的地 | 改用實際檔名 feature-*，並補「從 plugin agents/ 複製到 ~/.claude/agents/」等明確安裝步驟 | 重跑 ls agents/：4 檔皆為 feature-*.md；line 146 無任何來源/目的地路徑 |
| S87 | plan-setup | reference | 中 | `SKILL.md:23` | 內文引用 references/config-resolver.md 等三檔（另見 :92 db-templates.md、:168 config.template.md），但 skill 目錄下無 references/；實際位於 plugin 根目錄 | 改用 ${CLAUDE_PLUGIN_ROOT}/references/... 或明注「路徑相對於 plugin 根目錄」 | 重跑 ls：skill 目錄僅 SKILL.md；三檔確在 plugin 根 references/。原報告行號 22 校正為 23 |
| S88 | plan-setup | trigger | 中 | `SKILL.md:3` | 觸發詞「setup」「初始化」為單字級過廣，與 bug-setup（初始化 bug）、crew-init（首次設定）及一般 /init 場景重疊，易誤觸發 | 改為具體詞：「plan-setup」「設定 feature workflow」「初始化 feature workflow」，刪去裸詞 setup／初始化 | Read line 3 屬實；與 bug-setup「初始化 bug」、crew-init「初次設定」觸發詞比對重疊 |
| S89 | plan-setup | reference | 中 | `SKILL.md:71` | 全篇 MCP 工具用短名（notion-fetch、notion-update-data-source），環境同時有 claude.ai Notion 與 notion-local 兩套 Notion MCP，agent 可能選錯 | 依 checklist D 用完整 Server:tool 名或明注「指 claude.ai Notion 連接器工具，非 notion-local API-*」 | grep 確認 11 處短名；本環境工具清單同時載有 claude.ai Notion 與 notion-local API-* 兩套 |
| S90 | plan-spec | reference | 中 | `feature-workflow/skills/plan-spec/SKILL.md:14` | 引用 references/prerequisites.md 與 plan-common.md 為相對路徑，skill 目錄下不存在（實際在 plugin 根 references/）。SKILL.md:14、25、69 共三處。 | 改用 ${CLAUDE_PLUGIN_ROOT}/references/... 絕對定位；注意全 plugin 13 個 skill 皆同此寫法，宜一併修正保持一致 | 重跑 ls：skills/plan-spec/references 不存在；find 確認兩檔在 plugin 根 references/ |
| S91 | plan-spec | trigger | 中 | `feature-workflow/skills/plan-spec/SKILL.md:3` | description 觸發詞含單字級「spec」，提到 OpenAPI spec、.spec 檔、測試 spec 等情境皆可能誤觸發 | 移除單字級「spec」，保留「plan-spec」「技術規格」「規格書」即不漏觸發 | Read SKILL.md:3 確認含獨立觸發詞「spec」；其餘觸發詞已涵蓋正當情境 |
| S92 | plan-spec | structure | 中 | `feature-workflow/skills/plan-spec/examples/good-spec-output.md:106` | 範例檔「判斷」區塊缺 TASK_TYPE、CHANGE_SCOPE、NEW_API、EXISTING_API_CHANGE 與「任務屬性/技術需求」子標題，與 SKILL.md:48-63 指示不一致；plan-common.md:97 明言此區塊格式是 plan-build 入口，範例誤導有實害 | 補齊範例判斷區塊欄位與子標題，使其與 SKILL.md 指示完全對齊 | Read 兩檔比對：範例 106-111 行僅 4 欄位無子標題，SKILL.md 要求 8 欄位含兩子標題 |
| S93 | plan-stack | reference | 中 | `feature-workflow/skills/plan-stack/SKILL.md:14` | 引用 references/config-resolver.md 等相對路徑，但 skill 目錄下無 references/；實際位於 plugin 根目錄，相對路徑無法直接解析 | 改用 ${CLAUDE_PLUGIN_ROOT}/references/... 明確錨定 plugin 根目錄；注意同一模式存在於 5 個 skill（plan-close/setup/sync/start），宜整批修 | ls 確認 skills/plan-stack/ 僅 SKILL.md；references/ 在 plugin 根；grep 全 plugin 0 處用 CLAUDE_PLUGIN_ROOT |
| S94 | plan-stack | trigger | 中 | `feature-workflow/skills/plan-stack/SKILL.md:3` | description 宣稱通用技術棧設定，但內文以 Java 為前提（pom.xml/build.gradle:43、src/main/java:51、Java 分層規則:53-61），非 Java 僅一行邊界說明（:118），內建棧亦全為 Java（config.template.md「初始版本提供常見 Java ORM 技術棧」） | description 明講「主要支援 Java/Spring 專案」，或在內文補非 Java 的具體偵測規則 | 重讀 SKILL.md 全文與 config.template.md:74-86；references/dotnet/ 僅含 docx 工具，非 .NET 棧支援 |
| S95 | plan-stack | structure | 中 | `feature-workflow/skills/plan-stack/SKILL.md:47` | ID 覆蓋規則三處自相矛盾：步驟 1（:37）可確認後覆蓋、步驟 3（:47）不可與內建重複、Gotcha（:108）說衝突會靜默覆蓋；且 config-resolver.md:89 規定內建 ID 一律讀 _builtin.md，自訂檔實際會被忽略而非覆蓋 | 統一為單一規則：與內建 ID 相同時必須明確確認才覆蓋，並修正 Gotcha 敘述使其與 config-resolver 解析行為一致 | 重讀 SKILL.md:37/47/108 三處敘述互斥；config-resolver.md:89 證實 Gotcha 的「覆蓋」與解析邏輯不符 |
| S96 | plan-stack | token | 中 | `feature-workflow/skills/plan-stack/SKILL.md:71` | 步驟 6 內嵌技術棧檔案模板，與權威模板 config.template.md:92 起的「stacks/{custom-id}.md 模板」重複且已漂移（缺「⚠️ 技術棧陷阱」表與「{多模組說明，若適用}」） | 刪除內嵌模板，改為只引用 config.template.md 的「stacks/{custom-id}.md 模板」段落 | 比對 SKILL.md:71-89 與 config.template.md:92-120，內嵌版缺兩段；SKILL 本已引用該模板，刪除無副作用 |
| S97 | plan-start | reference | 中 | `feature-workflow/skills/plan-start/SKILL.md:14,26,118,120` | references/*.md 以 skill 目錄相對路徑書寫，實際檔案在 plugin 根目錄，路徑無法直接解析（已驗證 skill 目錄下無 references/） | 改用 ${CLAUDE_PLUGIN_ROOT}/references/... 或明寫 plugin 根路徑 | ls 實測：skill 目錄僅 SKILL.md；4 個被引用檔均在 plugin 根 references/，相對路徑不可解析 |
| S98 | plan-start | reference | 中 | `feature-workflow/skills/plan-start/SKILL.md:140,405` | Bug 模板僅寫「使用 bug-start 的標準模板」，無路徑；模板內嵌於另一 plugin 的 SKILL.md，Gotcha 自承有不同步風險 | 將 bug 頁面模板抽成共用 references 檔並在此給明確路徑 | grep 證實模板內嵌於 bug-workflow/skills/bug-start/SKILL.md:116-118，plan-start 未給任何路徑 |
| S99 | plan-start | trigger | 中 | `feature-workflow/skills/plan-start/SKILL.md:3` | 支援 bug 類型但與 bug-workflow:bug-start（開始修 bug／建立 bug）觸發範圍重疊，內文無「何時用哪個」指引 | 增加「何時用／何時不用」段落，欽定 bug 建單正典路徑 | 全文檢查無「何時用哪個」段落；bug-start 觸發詞「建立 bug／開始修 bug」與本 skill bug 類型重疊 |
| S100 | plan-status | reference | 中 | `feature-workflow/skills/plan-status/SKILL.md:10` | 引用 references/prerequisites.md，但 skill 目錄下無此檔（實際在 plugin 根目錄） | 改用 ${CLAUDE_PLUGIN_ROOT}/references/prerequisites.md（注意：全 plugin 12 個 skill 同一寫法，宜一併修） | ls 確認 skill 目錄僅 SKILL.md；檔案實在 plugin 根 references/；12 skill 同寫法 |
| S101 | plan-status | structure | 中 | `feature-workflow/skills/plan-status/SKILL.md:20` | --cleanup 說「清除超過 N 天」但未定義 N 如何指定；第 5 節範例寫死 30 天 | 明定預設 30 天與參數格式（如 --cleanup [天數]），消除 N 的歧義 | Read 確認 line 20 寫 N、line 139 範例寫 30 天，全文無 N 的定義或參數說明 |
| S102 | plan-sync | reference | 中 | `feature-workflow/skills/plan-sync/SKILL.md:14` | references/config-resolver.md 與 references/prerequisites.md 以相對路徑引用，但 skill 目錄下無 references/，實際在 plugin 根目錄 | 改用 ${CLAUDE_PLUGIN_ROOT}/references/ 或明寫「plugin 根目錄的 references/」；注意全 plugin 5 個 skills 同一寫法，宜一併修改 | ls 確認 skill 目錄僅 SKILL.md；兩檔實在 plugin 根 references/；grep 全 plugin 無 CLAUDE_PLUGIN_ROOT 用例 |
| S103 | plan-verify | structure | 中 | `skills/plan-verify/SKILL.md:238` | 步驟 4 稱「MCP 的 --autoConnect 自動連本機 Chrome」，此為 chrome-devtools 旗標，Playwright 不適用 | 分開描述：Playwright 自啟瀏覽器用 browser_tabs；chrome-devtools 才有 --autoConnect | L238 原文屬實；--autoConnect 僅出現在 L46 chrome-devtools 安裝指令，@playwright/mcp 無此旗標 |
| S104 | plan-verify | structure | 中 | `skills/plan-verify/SKILL.md:26` | --from-e2e {dir} 只出現在用法清單，內文無任何執行步驟 | 補一節說明如何解析 E2E 結果目錄並更新 verify.md，或刪除該旗標 | grep from-e2e 全 skill 目錄僅 SKILL.md:26 一處 |
| S105 | plan-verify | trigger | 中 | `skills/plan-verify/SKILL.md:3` | 觸發詞「驗證」「verify」「驗收」單字級過廣，與內建 verify、verification-before-completion 重疊 | 限縮為「plan-verify」「驗收條件驗證」「.spec 驗收」等具情境的片語；slash 指令 /plan-verify 不受影響 | L3 原文含三個單字級觸發詞；本環境確有內建 verify 與 superpowers:verification-before-completion |
| S106 | plan-verify | reference | 中 | `skills/plan-verify/SKILL.md:314` | 「格式見 spec.md 的驗證記憶系統段落」為懸空引用；grep 全 plugin 僅 README.md 提及該詞 | 把記憶檔格式內嵌或抽成 references/verify-memory-format.md 並修正指向 | grep -rn 驗證記憶系統 全 plugin 僅 README.md:175 與本行；plan-spec 範本無此段落 |
| S107 | plan-verify | reference | 中 | `skills/plan-verify/phases/run-verification.md:43` | Bash 模式通篇使用 $CDP，但全 plugin grep 'CDP=' 無定義，照做必失敗 | 開頭定義 CDP="node {plugin}/scripts/cdp.mjs"（scripts/cdp.mjs 已實測存在） | grep -rn 'CDP=' 全 marketplace plugins 0 hit；ls scripts/cdp.mjs 存在 |
| S108 | plan-verify | reference | 中 | `skills/plan-verify/phases/word-report.md:434` | `npx --yes exceljs` 無法執行：exceljs 無 bin 欄位（npm view 實測為空），且 npx 安裝也無法讓後續 node 呼叫 require 到 | 改為 npm install exceljs --prefix {tmpdir} 後以 NODE_PATH={tmpdir}/node_modules 執行 generator | npm view exceljs bin 回空（4.4.0 無 bin）；原報告行號 432 實為 434 |
| S109 | project-add | structure | 中 | `bug-workflow/skills/project-add/SKILL.md:14` | 宣告只檢查 prerequisites 第 2 項，跳過 §0.5 Notion 後端偵測，但本 skill 大量呼叫 Notion；line 16 又寫死「claude plugin install notion」，與雙後端設計矛盾 | 前置檢查納入 §0.5 後端偵測；前置條件改寫為「任一 Notion MCP 後端」 | prerequisites.md:164 適用範圍表明列 project-add 需做 0.5（✅），與 SKILL.md:14 矛盾 |
| S110 | project-add | token | 中 | `bug-workflow/skills/project-add/SKILL.md:184-253` | Git Flow 分支偵測約 70 行（指令、兩張信號表、邊界情況）全放內文，SKILL.md 已 482 行逼近 500 行上限 | 下放至 references/git-flow-detection.md，內文留 5 行摘要＋引用 | wc -l = 482；§4-5 實測佔 :184-253 共 70 行，同 plugin 已有 references 下放模式 |
| S111 | project-add | structure | 中 | `bug-workflow/skills/project-add/SKILL.md:94` | 情境 A 直接「跳到步驟 7」，但步驟 7 新格式檔必填 stack/prod_branch/uat_branch，未說明資料來源，會產生缺值設定檔 | 明寫「從 Notion 專案欄位回讀技術棧與分支」或仍執行步驟 4 偵測 | :94 與 :110 皆跳到步驟 7；:394-401 frontmatter 必填欄位無來源，步驟 4 已跳過 |
| S112 | bug-close | structure | 低 | `bug-workflow/skills/bug-close/SKILL.md:129` | C3 檢查「grep test 目錄中含 Regression: {bug 相關關鍵字}」無具體指令，關鍵字定義模糊 | 給出明確 grep 指令模式，並引用 /bug-fix 的 attribution 註解慣例「// Regression: {Bug 標題}」（bug-fix SKILL.md:160）作為搜尋依據 | 行 129 核對屬實；grep 證實 bug-fix SKILL.md:160 定義 // Regression: {Bug 標題} 慣例 |
| S113 | bug-close | structure | 低 | `bug-workflow/skills/bug-close/SKILL.md:281` | Gotchas 與邊界情況兩段內容重疊（283 vs 301 的 replace_content、290 vs 304 的 merge 衝突），雙處維護易分歧 | 合併為單一段落，每個情況只寫一次 | 283 與 301 措辭已分歧（「讀取合併」vs「保留附加」）；290 與 304 幾乎逐字相同 |
| S114 | bug-close | structure | 低 | `bug-workflow/skills/bug-close/SKILL.md:6` | 缺「何時不用」段落（中途記錄應用 bug-update、功能任務應用 plan-close） | 開頭補 2-3 行「何時不用」反向案例，降低與 bug-update/plan-close 的誤用 | 全文 307 行讀畢，確無反向案例段；bug-update 確涵蓋中途記錄與 reopen |
| S115 | bug-fix | token | 低 | `bug-workflow/skills/bug-fix/SKILL.md:263` | Gotchas 段 3 條與正文重複（最小 diff 行130/263、update_content 行208/267、gstack 偵測 行176/266） | 每條規則只留一處，正文放操作、Gotchas 只留正文沒有的判準（263 的 revert 理由、267 的覆蓋語意可保留） | Read 逐行比對三組行號，核心指示重複屬實（最小 diff 另重複於 anti-rationalizations.md F4） |
| S116 | bug-fix | structure | 低 | `bug-workflow/skills/bug-fix/SKILL.md:6` | 缺「何時不用」段落：與 /bug-investigate（尚未有根因）、/bug-close（已驗證要結案）的分工只散落在流程中 | 開頭補 2 行「何時不用」：根因未明用 /bug-investigate，驗證完成用 /bug-close | 全文 Read 確認無此段落；分工僅出現在行111-114 BLOCK 訊息與行233 後續提示 |
| S117 | bug-fix | token | 低 | `bug-workflow/skills/bug-fix/SKILL.md:85` | 範例硬寫具體專案分支名（MOM01P2401_DEV、feature/qa-log-user-id-statistics），對他專案無意義且可能被照抄；行246 更混用 {dev_branch} 佔位符與硬寫分支名 | 改用 {current_branch}、{fix_branch} 佔位符 | 行85-91、244-246 實測硬寫；行246 同一行混用佔位符與實名 |
| S118 | bug-investigate | reference | 低 | `bug-workflow/skills/bug-investigate/SKILL.md:63` | 內文硬寫 notion-search/notion-fetch/notion-update-page（:63/70/125/146/399，claude.ai 連接器名），SKILL.md 全篇未提 NOTION_BACKEND 映射；映射僅能經 :42→prerequisites.md:106 兩跳間接取得（且該引用路徑本身壞損，見第一條），notion-local-only 環境照字面找不到工具 | 流程開頭註明依 NOTION_BACKEND 參照 references/notion-backend.md 映射 | grep NOTION_BACKEND/notion-backend SKILL.md 0 命中；prerequisites.md:106 有映射指引 |
| S119 | bug-start | structure | 低 | `bug-workflow/skills/bug-start/SKILL.md:1-4` | skill 接受位置引數（/bug-start <問題簡述> [環境] [優先順序]，見 L31、L77-80）但 frontmatter 未宣告 argument-hint | frontmatter 加 argument-hint: <問題簡述> [環境] [優先順序]；最壞情況為欄位被忽略，無破壞風險 | Read 確認 frontmatter 僅 name/description；L31、L79 示範位置引數用法 |
| S120 | bug-start | structure | 低 | `bug-workflow/skills/bug-start/SKILL.md:173` | 步驟編號跳號不一致：6.5 → 6.7 → 6.8（缺 6.6），弱模型可能誤以為漏了步驟 | 重編為連續編號（7、8、9），原 7 改為 10；須同步更新本檔內 Step 6.7/6.8 交叉引用（L275/307/311/357 等、Gotchas、邊界情況）及 feature-workflow/plan-start/SKILL.md:243,251 的跨 plugin 引用 | L173=6.5、L231=6.7、L309=6.8 確認無 6.6；grep 命中 plan-start 兩處外部引用 |
| S121 | bug-start | structure | 低 | `bug-workflow/skills/bug-start/SKILL.md:183-202` | 6.5 要寫入的「調查過程 > 最近變更／環境狀態／歷史參考／歷史學習」子標題不存在於步驟 6 的頁面模板（模板僅有 關鍵 Log／相關 SQL 查詢／初步判斷），與同節「寫入格式」（L206-225 整塊 append「### 初始環境快照」）表述不一致 | 統一表述：明寫「以 append『### [HH:mm] 初始環境快照』子區塊方式寫入調查過程」，刪除「寫入 調查過程 > X」誤導字樣，或在模板補上對應子標題 | L183/190/194/202 指向的子標題不在 L133-138 模板；L206-225 寫入格式為整塊 append |
| S122 | bug-start | reference | 低 | `bug-workflow/skills/bug-start/SKILL.md:67` | 第 67 行建議用 notion-search 以「Git Repo」欄位匹配專案，但 notion-search 是全文搜尋無法做欄位精確過濾；L385 Gotcha 更要求精確大小寫比對，全文搜尋無法保證。plugin 自己的 notion-backend.md 也標注 search 查詢「有限」 | notion-local 後端改用 API-query-data-source 以 property filter 精確查詢「Git Repo」欄位（與 L256 既有做法一致）；Notion Plugin 後端無對等查詢工具，保留 search 降級並以 notion-fetch 核對欄位值後才採信 | L67 屬實；notion-backend.md 查詢映射表明載 notion-search（有限）vs API-query-data-source（完整 filter） |
| S123 | bug-update | token | 低 | `bug-workflow/skills/bug-update/SKILL.md:209` | 「快捷用法彙整」與步驟 3「支援的輸入方式」範例重複：通報來源、初步判斷、log 檔案、stacktrace 四項兩處都有。 | 兩段合併保留一份（222-228 行 reopen 快捷無重複、須保留），或將範例下放到 examples/ 並加指標。 | 比對 166/170/186 行與 213/216/218/219 行，4 項範例重複 |
| S124 | bug-update | trigger | 低 | `bug-workflow/skills/bug-update/SKILL.md:3` | 觸發詞「reopen」「貼 log」為單字級，使用者談 reopen PR/issue 或一般貼 log 時可能誤觸發（本環境診斷#1 已記錄激進觸發詞干擾技能選擇）。 | 收斂為「reopen bug」「貼 log 到 bug」等雙詞組合。 | Read line 3 確認「貼 log」「reopen」以單詞列於觸發清單 |
| S125 | bug-update | structure | 低 | `bug-workflow/skills/bug-update/SKILL.md:78` | 1-B Step 2 清單編號重複：第 78、79 行都是「3.」，後續編號錯位。 | 重新連續編號為 3、4、5、6。 | Read 確認 78 行「3. 使用 notion-search…」與 79 行「3. 若當前在修復分支…」皆為 3 |
| S126 | crew-doctor | structure | 低 | `bug-workflow/skills/crew-doctor/SKILL.md:143` | 「退出碼」段落定義 0/1/2，但 skill 無任何腳本，LLM 驅動流程沒有退出碼可回傳 | 刪除退出碼表，或改為摘要中的「健診結果狀態」文字欄位 | ls skill 目錄僅 SKILL.md，無任何可執行腳本可回傳退出碼 |
| S127 | crew-doctor | reference | 低 | `bug-workflow/skills/crew-doctor/SKILL.md:15` | references/discipline-preamble.md 相對 skill 目錄不存在（實際位於 plugin 根層 references/；全 plugin 通病） | 改用 ${CLAUDE_PLUGIN_ROOT}/references/… 或 ../../references/… 明確路徑 | ls：skill 目錄僅 SKILL.md 無 references/；檔案在 plugin 根層 references/ 確認存在 |
| S128 | crew-doctor | structure | 低 | `bug-workflow/skills/crew-doctor/SKILL.md:8` | 缺「何時不用」段落：與 bug-investigate（查程式 bug）的分工未明示，弱模型易混用 | 在 Overview 後補一段「何時不用：程式錯誤請走 bug-investigate」 | Read 全文 210 行確認無任何「何時不用」或與 bug-investigate 分工說明 |
| S129 | crew-init | token | 低 | `bug-workflow/skills/crew-init/SKILL.md:201-204` | 結尾摘要「可用指令」與「進階」兩區重複列出 /crew-doctor | 刪除其中一處，crew-doctor 只在進階區列一次 | 行 201 與 204 均列 /crew-doctor，實讀確認 |
| S130 | crew-init | token | 低 | `bug-workflow/skills/crew-init/SKILL.md:3` | description 前半摘要執行流程（依序執行 /bug-setup → /plan-setup…），可能讓 agent 照 description 行事、不載入內文的跳過邏輯與 resume 機制 | description 只留觸發條件與用途一句話，流程細節留在內文；保留結尾觸發詞不影響觸發 | 行 3 原文確含流程摘要；觸發詞在句尾，修剪前半不影響觸發 |
| S131 | crew-init | structure | 低 | `bug-workflow/skills/crew-init/SKILL.md:31-36` | --skip-bug/--skip-plan 宣告用途（已執行 setup）與各階段 1a/2a 自動偵測跳過功能重複；行 216-217 又說 --resume 唯一差別只是省提示，三種等價路徑讓 agent 猶豫 | 只保留自動偵測＋--resume 一個預設做法，刪除或明確定義 --skip-* 的必要情境 | 行 33-34 框定 --skip-* 為已設定情境，1a/2a 偵測已涵蓋；216-217 屬實 |
| S132 | crew-upgrade | structure | 低 | `bug-workflow/skills/crew-upgrade/SKILL.md:167` | Gotcha 警告「版本比較是字串比較」，但內文從未定義任何比較邏輯（bash 或指示），agent 只能自行發明比較方式，警告無對應實作 | 在步驟 3 給明確比較指示（如 sort -V 或「不相等即視為可更新」），讓 Gotcha 有落點 | 重讀步驟 3（65-80 行）僅有輸出格式，無任何比較指令或規則；grep 全文無 sort/compare |
| S133 | plan | structure | 低 | `skills/plan/SKILL.md:45` | 「回傳結果」模板無條件列出 db.md + db.sql，但 plan-db 僅在 DB_REQUIRED=true 時執行，DB 不需要時回報與實況不符 | 在該行標注「（若 DB_REQUIRED=true）」，或指示依實際產出動態組回報 | Read 確認第 45 行無條件列 db.md + db.sql，第 31 行明載 plan-db 僅於 DB_REQUIRED=true 執行，兩處矛盾屬實 |
| S134 | plan-arch | structure | 低 | `feature-workflow/skills/plan-arch/SKILL.md:3` | 缺「何時不用」與 Common Mistakes 段落，與 java-design-advisor / plan-explore 觸發重疊時無反向指引 | 補一句反向案例（如：純討論架構不產文件時用 plan-explore）。原建議「description 移除『不呼叫 Notion API』」不採納：該片語是 plan/plan-spec/plan-db/plan-status 共用慣例，兼作與 plan-sync/plan-close 的區辨訊號，單改一檔反破壞一致性 | Read 全文確認無「何時不用」段；grep 確認 5 個 skill description 共用「不呼叫 Notion」慣例，刪除有副作用，故剔除該半項 |
| S135 | plan-browse | reference | 低 | `SKILL.md:180-182` | 文字說「在 .md 檔案中搜尋」但指令含 --include="*.sql"，敘述與指令不符 | 註解改為「搜尋 .md 與 .sql 檔案」 | Read 181-182 行確認不符；scratchpad 實跑 grep 雙 --include 語法有效 |
| S136 | plan-browse | structure | 低 | `SKILL.md:274` | 銜接表寫 /plan-spec「會進入編輯迴圈」，但 plan-spec 內實名為「規格確認迴圈」（plan-spec/SKILL.md:71），用詞不一致 | 統一改為「規格確認迴圈」 | grep plan-spec/SKILL.md:71 確認正式名稱為「規格確認迴圈」，274 行用詞確實不一致 |
| S137 | plan-browse | token | 低 | `SKILL.md:51-56` | box-drawing 框線混排全形中文，模型難精確對齊，重現成本高且易產出破版 | 改用 markdown 表格或縮排條列取代框線圖 | Read SKILL.md:51-56 確認框線內為全形中文混排，原檔對齊即已不齊 |
| S138 | plan-browse | reference | 低 | `SKILL.md:75-132` | 深度閱讀範本只列 README/spec/db/arch/log 五檔，遺漏其他 skill 實際產出的 verify.md、review.md、deploy.sql | 範本補列 verify.md、review.md、deploy.sql 區段或註明「其餘檔案一併摘要」 | 自行 grep：plan-verify/SKILL.md:338 寫 verify.md、plan-review/SKILL.md:187 寫 review.md、plan-build E7 產 deploy.sql |
| S139 | plan-build | token | 低 | `feature-workflow/skills/plan-build/SKILL.md:199-216` | 7.3b 設定檔模式表（13 列）與 E7 deploy.sql 模板（行 257-279）為執行期細節，佔本體約 45 行 | 下放到 references/（如 config-patterns.md），SKILL.md 留一句指標 | Read 確認行 201-215 為 13 列模式表、行 257-279 為 23 行 SQL 模板 |
| S140 | plan-build | trigger | 低 | `feature-workflow/skills/plan-build/SKILL.md:3` | description 摘要實作細節（E1~E7、DB_REQUIRED=insert-only、最多 5 人）而非觸發條件，agent 可能照 description 行事跳過內文 | description 只留觸發情境與一句核心價值，實作細節移入內文 | Read 行 3 確認含 E1~E7、DB_REQUIRED=insert-only、最多 5 人等實作細節 |
| S141 | plan-build | structure | 低 | `feature-workflow/skills/plan-build/SKILL.md:374` | 步驟指涉錯位：行 374 說「步驟 5 檢查 DB MCP 可用性」但步驟 5 是準備分層脈絡（DB 團隊判斷在步驟 3）；行 384 Gotcha 說「步驟 1 就要先檢查」環境變數但步驟 1 是定位任務（檢查規定在前置條件） | 修正兩處指涉至正確步驟編號（步驟 3、前置條件） | Read 行 119/62/374/384 對照：步驟 5/1 標題與指涉內容確實不符 |
| S142 | plan-build | structure | 低 | `feature-workflow/skills/plan-build/SKILL.md:87` | 「回退到 v4.9.0 邏輯」為時效性版本指涉（plugin.json 現版 4.23.0），版本號會隨演進腐化 | 改為描述性名稱如「回退到基本判斷（只看 FRONTEND_REQUIRED × DB_MCP）」 | Read 行 87 確認字樣；cat plugin.json 確認 version 4.23.0 |
| S143 | plan-close | trigger | 低 | `feature-workflow/skills/plan-close/SKILL.md:3` | 觸發詞「任務結案」與 bug-workflow:bug-close 的「結案」重疊，Bug 任務結案時兩 skill 可能競爭 | description 說明與 bug-close 的分工（.spec/ 管理的 Bug 用 plan-close） | bug-close:2 觸發詞含「結案」；plan-close 支援 Bug 類型，字面重疊屬實 |
| S144 | plan-close | structure | 低 | `feature-workflow/skills/plan-close/SKILL.md:8` | 開頭宣稱「僅 3-5 次 Notion API 呼叫」，與行 279 Gotcha 承認實際可達 7 次自相矛盾 | 行 8 改為「約 3-7 次（Bug 有關聯 Feature 時較多）」與 Gotcha 對齊 | Read 確認行 8「僅 3-5 次」與行 279「實際可達 7 次」並存 |
| S145 | plan-db | reference | 低 | `feature-workflow/references/plan-common.md:29` | 引用鏈兩層深：SKILL.md → plan-common.md → config-resolver.md，違反參考檔一層深原則；且該行寫 references/config-resolver.md，自 references/ 目錄內解讀字面會變成 references/references/，更不可達 | SKILL.md 直接列出會用到的第二層檔案，或將技術棧載入摘要上提至 plan-common.md | Read 實證 plan-common.md:29 引用該檔；ls 實證 config-resolver.md 存在於 references/ |
| S146 | plan-db | structure | 低 | `feature-workflow/skills/plan-db/SKILL.md:17,33,39` | 「README.md」三處未寫全路徑，可能被解讀為專案根 README 而非 .spec/{slug}/README.md（plan-common.md:17 慣例為後者）；行 33 位於 subagent prompt 內，fresh context 誤讀風險更高 | 統一寫成 .spec/{slug}/README.md 完整路徑 | grep 實證三處僅寫 README.md；plan-common.md:17 實證慣例為 .spec/{slug}/README.md |
| S147 | plan-db | structure | 低 | `feature-workflow/skills/plan-db/SKILL.md:29-39` | opus subagent 為 fresh context，但 prompt 指示未要求傳入步驟 1 讀到的設計準則（rules/database.md、專案 CLAUDE.md、技術棧），且 db.md 無必含段落契約（db.sql 契約已有：行 37 明定含 CREATE TABLE/INDEX/範例資料/Rollback SQL） | 在步驟 2 prompt 指示中加入「附上步驟 1 載入的技術棧與 DB 規範」與 db.md 最小段落清單；不需另拆 reference | 行 37 已含 db.sql 契約（原報告稱無 Rollback 格式不實）；準則載入在 plan-common 但未指示傳入 subagent |
| S148 | plan-demo | reference | 低 | `feature-workflow/skills/plan-demo/SKILL.md:16` | 路徑寫 references/discipline-preamble.md，實際位於 plugin 根目錄（相對 SKILL.md 為 ../../references/），路徑無法直接解析 | 改寫為 ${CLAUDE_PLUGIN_ROOT}/references/ 或明確相對路徑（全 plugin 統一修） | ls 確認檔在 plugin 根 references/；skills/plan-demo/ 下無 references；同寫法遍及 7 個 skill |
| S149 | plan-demo | reference | 低 | `feature-workflow/skills/plan-demo/SKILL.md:196` | 引用 references/demo-spec-template.md 並自承「如未來新增該檔」，find 實測不存在，屬死引用 | 刪除這句前瞻性引用，或真的建立該範本檔再引用 | find plugin 全目錄 0 hit，檔案確不存在；有 guard 句故僅低嚴重度 |
| S150 | plan-deploy-confirm | reference | 低 | `feature-workflow/skills/plan-deploy-confirm/SKILL.md:17` | 相對路徑 references/discipline-preamble.md 自 SKILL.md 目錄解析不到（檔案在 plugin 根目錄 references/，skill 目錄僅有 SKILL.md）；屬全 plugin 共通問題（7 個 skill 同寫法） | 改用 ${CLAUDE_PLUGIN_ROOT}/references/... 或明示「plugin 根目錄下」，建議全 plugin 一起改 | ls skill 目錄僅 SKILL.md；discipline-preamble.md 實位於 plugin 根 references/；grep 見 7 個 skill 同用相對路徑 |
| S151 | plan-deploy-confirm | reference | 低 | `feature-workflow/skills/plan-deploy-confirm/SKILL.md:51` | `notion-search` 未用完整 MCP Server:tool 名，環境同時有 notion-local（API-post-search）與 claude.ai Notion（notion-search）兩套，工具名有歧義；plan-setup 亦同 | 與全 plugin 一起統一為完整工具名，或在 config-resolver 明定使用哪套 Notion MCP | 本環境實有 mcp__claude_ai_Notion__notion-search 與 mcp__notion-local__API-post-search 並存；grep 僅本 skill 與 plan-setup 用 notion-search |
| S152 | plan-explore | structure | 低 | `feature-workflow/skills/plan-explore/SKILL.md:169` | 缺明確「何時不用」段落；僅第 10 行與護欄（315）提到實作需改用 /plan-start，修 bug、已有明確規格等反向案例不完整 | 在「你不必做的事」旁補「何時不用」：要實作、要修 bug、已有明確規格時各導向對應 skill | grep 全文僅 10、315 行提實作轉向；無 bug-workflow／plan-spec 反向導引段落 |
| S153 | plan-explore | structure | 低 | `feature-workflow/skills/plan-explore/SKILL.md:196-276` | 範例含特定專案敘事內容（AQI、防汛水費、LineBC、Solr apilog），對通用 plugin 不具可移植性 | 改用領域中性範例（如訂單、通知），避免使用者誤以為 skill 綁定特定系統 | grep 確認 AQI/防汛/LineBC/apilog 在 197-267；plugin.json 定位為通用 productivity 工作流 |
| S154 | plan-explore | token | 低 | `feature-workflow/skills/plan-explore/SKILL.md:93-107` | 「視覺化」示範框圖純裝飾（用 ASCII 框畫「自由使用 ASCII 圖表」），大半無資訊量 | 縮為一句條列：「可用 ASCII／Mermaid 畫系統圖、狀態機、資料流、架構草圖、依賴圖、比較表」 | Read 93-107 確認為裝飾框；唯一資訊（圖表類型清單）建議句已保留 |
| S155 | plan-next | structure | 低 | `feature-workflow/skills/plan-next/SKILL.md:2` | skill 支援 <slug> 與 --all 引數，但 frontmatter 缺 argument-hint，使用者輸入 /plan-next 時無自動完成提示 | frontmatter 補 argument-hint: "[slug] [--all]" | Read frontmatter 僅 name/description；grep argument-hint 全 plugin 0 命中（全 plugin 慣例性缺漏） |
| S156 | plan-next | structure | 低 | `feature-workflow/skills/plan-next/SKILL.md:79` | 決策表 first-match 順序：「files.md 但無 security.md」排在 verify.md=FAIL 之前，跳過 security 又 verify 失敗時會建議掃描而非先修 FAIL | 把 verify.md=FAIL 規則移到 security/verify 缺檔規則之前，或明文說明優先序理由 | Read 決策表 :79 vs :81 順序屬實；:137 邊界明定 FAIL 優先於 review PASS，現順序與此意圖矛盾 |
| S157 | plan-review | reference | 低 | `feature-workflow/skills/plan-review/SKILL.md:25` | references/*.md 路徑自 skill 目錄不可解析；skills/plan-review/ 只有 SKILL.md，檔案實際在 plugin 根 references/ | 改用 ${CLAUDE_PLUGIN_ROOT}/references/ 或 ../../references/ 明確路徑（全 plugin 同步修） | 自跑 ls：skill 目錄僅 SKILL.md；plugin 根 references/ 含 prerequisites 等 4 檔皆在 |
| S158 | plan-review | token | 低 | `feature-workflow/skills/plan-review/SKILL.md:91` | 66 行 Agent Team 派工 prompt 全文內嵌本文（行 91–157），佔本體約 1/4，觸發即載入 | 下放至 references/review-prompts.md（比照 build-prompts.md 慣例），本文留摘要與路徑 | awk 計行 91–157 共 67 行，全檔 267 行約 25%；references/build-prompts.md 存在 |
| S159 | plan-security | reference | 低 | `feature-workflow/skills/plan-security/SKILL.md:257` | Gotcha「需同步修改 plan-review 的 SKILL.md」已過時：實測 plan-review/SKILL.md:80,131 Reviewer 3 已是效能審查 | 刪除該待辦句，改為陳述現況「plan-review Reviewer 3 已專職效能」 | grep plan-review/SKILL.md:80,131 皆為「效能審查」，待辦已完成 |
| S160 | plan-security | structure | 低 | `feature-workflow/skills/plan-security/SKILL.md:83` | L1-SEC-2 的「指令」欄放的是描述文字非可執行指令，與同表其他列（皆為 grep）不一致，agent 無法照表執行；且該節標題聲稱「自動，無需 AI 判斷」 | 明示該列為「AI 讀碼檢查」或給出可執行的 grep/檢查步驟 | Read L83：欄內容為「掃描 Controller 方法，檢查…」，無指令；L72 節標題稱全自動 |
| S161 | plan-setup | structure | 低 | `SKILL.md:150-156` | 「29 種工具，持續維護」為時效性宣稱，工具數會隨版本變動；且步驟 6 建立時未提本環境已裝 chrome-devtools 時的跳過條件 | 刪除具體工具數，改「Google 官方維護」；補「已安裝 chrome-devtools MCP 則跳過」判斷 | line 154 屬實；現版恰 29 工具但隨版本變動；:150-164 無已安裝跳過判斷 |
| S162 | plan-setup | structure | 低 | `SKILL.md:6-8` | 缺「何時不用」段落（如：已設定完成想改單一專案應走 /project-add、只更新技術棧應走 /plan-stack） | Overview 後加 2-3 行「何時不用」反向指引，減少與 project-add/plan-stack 的誤用 | 全文 Read 確認無「何時不用」且零提及 plan-stack；步驟 1.4/4 僅部分涵蓋 project-add |
| S163 | plan-setup | token | 低 | `SKILL.md:83-102` | 情境 B 的建庫 7 步驟細節（Relation 補欄、is_inline、Views）與 db-templates.md 建立順序段重疊，佔本體約 20 行 | 濃縮為 3 行要點＋指向 db-templates.md「建立順序」與「D. 功能設計庫」 | 比對 db-templates.md:7-35 與 D 段：is_inline、ADD COLUMN Relation、Views 皆已完整記載 |
| S164 | plan-spec | structure | 低 | `feature-workflow/skills/plan-spec/SKILL.md:16` | 前置條件標明僅適用 Feature，但未定義活躍任務為 bug 型時的行為；plan-start 支援 bug 型任務，plan-common.md 定位活躍任務與共用邊界情況皆無 type 檢查 | 補一行：若活躍任務 type=bug，提示改用 /bug-fix 並中止 | Read SKILL.md:16 與 plan-common.md:7-17、101-106 確認無 bug 型分流指示 |
| S165 | plan-stack | trigger | 低 | `feature-workflow/skills/plan-stack/SKILL.md:3` | 觸發詞「tech stack」過廣，description 明文「提到 tech stack 即觸發」，使用者問「這專案的 tech stack 是什麼」會誤啟動設定寫檔流程 | 改為「設定 tech stack」「自訂 tech stack」等動作性片語，降低單詞級誤觸發 | SKILL.md:3 確有裸詞「tech stack」列於觸發清單；其餘觸發詞皆為動作性片語 |
| S166 | plan-stack | reference | 低 | `feature-workflow/skills/plan-stack/SKILL.md:98` | 回傳結果硬寫 ~/.claude/feature-workflow/stacks/{id}.md，但 config-resolver.md 支援舊路徑（~/.claude-company/feature-workflow/、舊單一檔案格式）且遷移前仍可讀舊格式，未遷移使用者顯示路徑與實際不符 | 改為顯示實際解析到的設定目錄路徑，不硬編預設位置 | config-resolver.md:26-52 確認多層解析含舊路徑相容；SKILL.md:98 硬編新路徑 |
| S167 | plan-start | structure | 低 | `feature-workflow/skills/plan-start/SKILL.md:2` | frontmatter 未用 argument-hint，skill 明確接受 <任務簡述> [選項] 引數 | 補 argument-hint: "<任務簡述> [feature\|bug] [--related <slug>]" | frontmatter 僅 name/description；第 33 行明示 /plan-start <任務簡述> [選項] |
| S168 | plan-start | token | 低 | `feature-workflow/skills/plan-start/SKILL.md:354,379` | 驗證報告格式在 9.5 與步驟 10 幾乎重複兩份（354-367 vs 379-387） | 保留一份，另一處引用「同 9.5 報告格式」 | 重讀確認 354-367 與 379-387 皆列 S1~S7 報告格式，重複約 14 行 |
| S169 | plan-start | trigger | 低 | `feature-workflow/skills/plan-start/SKILL.md:38` | 類型推斷單字級關鍵字「問題」易誤判（如「解決效能問題的新功能」被判為 bug），且無確認步驟 | 推斷結果在互動步驟向使用者確認類型，或收窄關鍵字 | 第 38 行確認含「問題」即判 bug；步驟 3 互動項目不含類型確認 |
| S170 | plan-status | structure | 低 | `feature-workflow/skills/plan-status/SKILL.md:151` | cleanup 步驟 3「還原 .gitignore 中的 !.spec/{slug}/ 排除規則」語意含糊，實際是刪除該行 | 改寫為「移除 .gitignore 中對應的 !.spec/{slug}/ 行」 | plan-close/SKILL.md:233 為「追加 !.spec/{slug}/」，cleanup 對應動作即刪除該行，「還原」易誤讀 |
| S171 | plan-status | structure | 低 | `feature-workflow/skills/plan-status/SKILL.md:167` | Gotchas 寫「自動修復（步驟 5）」，索引修復實為第 6 節，編號錯置 | 改為「步驟 6」，或將小節改具名引用避免重編號再壞 | Read 確認 line 167 寫步驟 5；索引修復為 line 153「### 6. 索引修復」，第 5 節是清理模式 |
| S172 | plan-status | trigger | 低 | `feature-workflow/skills/plan-status/SKILL.md:3` | 觸發詞「任務狀態」「任務列表」單字級過廣，環境有 Notion/Jira 任務，易誤觸發 | 觸發詞加限定語，如「.spec 任務狀態」「規劃任務列表」，並保留 plan-status 明確詞 | Read 確認 line 3 含該二詞；環境同時有 bug-workflow Notion 任務追蹤與 Jira MCP，語意衝突屬實 |
| S173 | plan-sync | token | 低 | `feature-workflow/skills/plan-sync/SKILL.md:100` | status→開發階段 對照表兩欄內容逐列完全相同，表格無資訊量 | 壓縮為一句：「開發階段直接取 README.md 的 status 值（合法值：需求分析、規格設計、DB 設計、架構設計、開發中、程式碼審查）」 | Read 行 100-107：六列兩欄逐列相同；壓縮後合法值清單仍保留，無功能損失 |
| S174 | plan-sync | trigger | 低 | `feature-workflow/skills/plan-sync/SKILL.md:3` | 觸發詞「同步到 Notion」與 plan-close 的「同步到 Notion 並結案」語意相近，可能誤觸發 | description 補反向條件：「結案同步請用 plan-close」以明確分流 | 比對兩 skill description：plan-sync 觸發詞是 plan-close 觸發詞的子字串；補反向條件不影響原觸發 |
| S175 | plan-sync | reference | 低 | `feature-workflow/skills/plan-sync/SKILL.md:66` | notion-fetch、notion-update-page 非完整 MCP 工具名，且環境有 claude.ai Notion 與 notion-local 兩套，未指明用哪個 server | 建議在前置檢查明定 Notion MCP 來源；不建議硬編完整 Server:tool 名（plugin 對外發布，server 名依安裝環境而異，硬編會壞可攜性） | 行 66/70 實用短名；本環境工具清單同時有 claude_ai_Notion 與 notion-local 兩套 |
| S176 | plan-verify | structure | 低 | `skills/plan-verify/SKILL.md:350` | verify.md 範本「驗證工具」選項只列 chrome-devtools-mcp/cdp.mjs，漏預設的 Playwright（415 行同） | 選項補上 Playwright MCP，與前置檢查的工具優先序一致 | sed 抽 L350/L415 皆為 {chrome-devtools-mcp / cdp.mjs}，無 Playwright |
| S177 | plan-verify | token | 低 | `skills/plan-verify/SKILL.md:522` | 本體 563 行超過官方建議 500 行；Gotchas/邊界情況中約半數為 Word/Excel 報告細節 | 將報告類 Gotchas 與邊界情況下放 phases/word-report.md，本體壓到 500 行內 | wc -l 實測 563；Gotchas 17 條中約 8 條、邊界 20 條中約 9 條屬報告類 |
| S178 | plan-verify | reference | 低 | `skills/plan-verify/SKILL.md:58` | references/*.md 實際位於 plugin 根層，非 skills/plan-verify/ 下，相對路徑不成立 | 改用 ${CLAUDE_PLUGIN_ROOT}/references/… 或 ../../references/… 明確路徑 | ls 確認 skills/plan-verify/references 不存在，discipline-preamble.md 等在 plugin 根層 references/ |
| S179 | plan-verify | reference | 低 | `skills/plan-verify/examples/verify-report-sample.md:1` | examples/verify-report-sample.md 未被 SKILL.md 或 phases 任何處引用（grep 實測 0 hit） | 在步驟 7 加連結作為 verify.md 範例。不建議刪檔：docs/superpowers/plans/2026-05-26-verify-docx-cli.md 以其為 smoke-test fixture | grep 全 plugin：SKILL.md/phases 0 hit，僅 docs/ 計畫文件引用 8 處，刪除有副作用 |
| S180 | project-add | token | 低 | `bug-workflow/skills/project-add/SKILL.md:128-141` | 專案類型判斷表與 references/project-page-templates.md:9-22 重複，雙源易漂移（措辭已略有差異） | 保留 SKILL.md 一處為權威，模版檔改為引用不複製 | 兩檔比對：判斷表＋確認提示雙份，措辭已漂移（5+ -D 參數 vs 超過 5 個） |
| S181 | project-add | structure | 低 | `bug-workflow/skills/project-add/SKILL.md:450-452` | 步驟 9 結果範例只列舊格式 feature-workflow-config.md 路徑，與步驟 7／Gotchas「新格式優先、忽略舊格式」不一致 | 範例改列新格式 projects/{repo-id}.md 路徑，或標注依實際更新檔案列出 | :451-452 範例列舊格式路徑；:392 新格式優先、:465 Gotcha 明言忽略舊格式 |

---

## 四、診斷缺口與無法驗證項

- **診斷缺口：無。** 29 個 skills（bug-workflow 10 ＋ feature-workflow 19）全數完成診斷，findings/*.json 共 29 份、181 條發現。
- **無法驗證項：無。** 181 條發現每條均附實測證據（ls／find／grep／cmp／npm view／逐行比對）；全量掃描 findings 的 issue 與 evidence 欄位，零筆含「未驗證」「推測」「無法驗證」標注。
- **兩點保留事項**（非缺口，執行前需確認）：
  1. C12 的 `${CLAUDE_PLUGIN_ROOT}` 展開行為未在本 session 實測，套用前先以 1 個 skill 驗證。
  2. 跨 skill 分析的「可省行數」為估算值（duplication.md 自述），實際節省以執行後 diff 為準。

---

## 五、建議執行順序

依「先修錯誤 → 再定規範 → 最後抽共用」原則分四梯次；括號內為依賴關係。

### 梯次 1：高嚴重度事實錯誤（獨立可做，25 條高嚴重度 S 項）
1. **S7／S24**：修正不存在的 npm 套件名 `@anthropic-ai/mcp-server-playwright`（crew-doctor、plan-verify）——照抄必失敗。
2. **S23**：plan-verify 自稱 Playwright MCP 但工具名全是 chrome-devtools——擇一修正。
3. **S4**：bug-setup 完成訊息指向不存在的 /bug-search。
4. **S9／S10**：crew-upgrade 兩處路徑斷言錯誤。
5. **S12／S14／S17**：plan-close ↔ plan-deploy-confirm 的「🚀 部署狀態」區塊契約不成立——兩檔對齊。
6. **S13**：plan-close .gitignore 排除規則無效。
7. **S19**：plan-next 結案偵測比對錯誤字串（status: closed vs 中文）。
8. **S21**：plan-security L1-SQL-1 pattern 匹配不到任何目標。
9. **S22**：plan-sync 指涉 plan-start 錯誤步驟。
10. **S8／S15／S16／S20**：4 個 skill 宣稱的 anti-rationalizations／boundaries 專用段不存在——補段或改指標（**C2 的前置**）。

### 梯次 2：規範層（決定後續所有改動的形狀）
1. **C14** 統一模板定稿（含通用書寫規則）——是 C13、C15、C16、C12 的載體。
2. **C12** references 路徑寫法定案並批改 29 檔（先實測 ${CLAUDE_PLUGIN_ROOT}）——一次消掉 reference 維度最大宗。
3. **C13** 前置檢查句式收斂（依賴 C14 定稿）。
4. **C16** 步驟編號整數化（依賴 C14；與 C12 同批改可省一輪全檔掃描）。

### 梯次 3：觸發詞與邊界（可與梯次 2 並行）
1. **C10** 單字級觸發詞收斂（18 skills 的 description 批改）。
2. **C11＋C15** CREW 內部邊界標注＋「何時不用」段（兩者內容互相呼應，同批做）。

### 梯次 4：抽共用（依賴梯次 2 的模板與路徑規範定案，否則抽出的 reference 又是錯路徑）
1. **C1**（設定檔區塊，省最多且零風險）→ **C3**（定位 Bug）→ **C5**（Notion 對應表）→ **C4**（證據收集）→ **C6**（專案引導）→ **C7**（偵測負責人）→ **C8**（MCP 安裝，依賴梯次 1 的 S7/S24 修正）→ **C2**（紀律護欄，依賴梯次 1 的 S8/S15/S16/S20）→ 最後 **C9**（跨 plugin 單一來源機制，涉建置流程、單獨提案）。
2. 其餘中低嚴重度 S 項：多數會被梯次 2–4 的批次修法覆蓋；收尾時對照本表逐條勾銷，殘餘者單獨處理。

### 驗收方式（每梯次完成後）
- 抽 3 檔逐行比對＋全量 grep 舊 pattern 確認 0 殘留（批次修改標準）。
- 跑 crew-doctor 健診確認 plugin 仍可載入。
- 派 fresh agent read-back 修改後的 SKILL.md 抽樣，確認引用路徑真實存在。
