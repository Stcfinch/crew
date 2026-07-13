# CREW 29 個 Skills 跨檔重複分析

> 分析日期：2026-07-13
> 掃描範圍：`plugins/bug-workflow/skills/*/SKILL.md`（10 個）＋ `plugins/feature-workflow/skills/*/SKILL.md`（19 個），共 29 檔、7,512 行。
> 方法：4–5 行滑動視窗雜湊比對（精確重複）＋ 主題式人工比對（高度相似段落）。
> 路徑省略前綴：`/Users/cheng/.claude/plugins/marketplaces/company-marketplace.bak/plugins/`

## 總覽

共找到 **9 組**跨 skill 重複（G1–G9），合計約 **240 行**可省。另有 1 項跨 plugin 的 references/ 重複（附註 A）。兩個 plugin 已有 `references/` 共用機制（prerequisites.md、plan-common.md、config-resolver.md、discipline-preamble.md），多數重複是「已有 reference 卻仍在 SKILL.md 內文重複展開」造成。

---

## G1：bug-workflow「## 設定檔」區塊（5 份完全相同，最大宗之一）

11 行的設定檔路徑說明逐字重複 5 次：

| Skill | 行號範圍 |
|-------|---------|
| bug-workflow/skills/bug-close/SKILL.md | 12–22 |
| bug-workflow/skills/bug-fix/SKILL.md | 27–39 |
| bug-workflow/skills/bug-investigate/SKILL.md | 27–39 |
| bug-workflow/skills/bug-start/SKILL.md | 12–22 |
| bug-workflow/skills/bug-update/SKILL.md | 14–24 |

內容：「執行前依序檢查以下路徑…1. `~/.claude-company/bug-workflow-config.md` 2. `~/.claude/bug-workflow-config.md`…若都不存在提示 `/bug-setup`」。另 project-add/SKILL.md:21–33 是擴充變體（多列 feature-workflow 路徑）。

**關鍵**：`bug-workflow/references/prerequisites.md:125–126` 已含同一路徑清單，且 5 個 skill 都已引用 prerequisites.md（例：bug-fix/SKILL.md:42）——此區塊與既有 reference 完全冗餘。

- 重複量：約 11 行 × 5 ＝ 55 行
- 建議：整段刪除，併入既有的「> 前置檢查：參照 `references/prerequisites.md`」一行。**可省約 50 行**（project-add 變體另留 6 行差異說明）。

## G2：「定位目標 Bug」邏輯（bug-fix / bug-investigate 逐字複製 bug-update）

| Skill | 行號範圍 |
|-------|---------|
| bug-workflow/skills/bug-fix/SKILL.md | 58–71 |
| bug-workflow/skills/bug-investigate/SKILL.md | 58–73 |
| bug-workflow/skills/bug-update/SKILL.md | 42–60（原始出處） |

bug-fix 與 bug-investigate 開頭都寫「與 `/bug-update` 相同邏輯：」，**然後仍把 14 行步驟全文貼一遍**（notion-search + data_source_url、狀態進行中、🐞 錯誤、Git Repo 識別碼、branch 匹配…）。

- 重複量：約 14 行 × 2 ＝ 28 行
- 建議：抽到 `bug-workflow/references/`（如 `locate-bug.md`），三個 skill 各留 1 行指標；或保留 bug-update 為承載者、其餘兩檔只留「與 /bug-update 相同邏輯（見該 skill 步驟 1-A）」。**可省約 26 行**。

## G3：「## 紀律護欄」樣板（11 份，僅 skill 名不同）

同一 5–6 行樣板（「執行前必讀 discipline-preamble.md…本 skill 專用條目…停下查表」）出現在 11 個 skill，只差 `「{skill 名} 專用」` 一詞：

bug-investigate:19、bug-fix:19、crew-doctor:13、crew-init:22（以上 bug-workflow）；plan-build:40、plan-demo:14、plan-deploy-confirm:15、plan-review:29、plan-security:21、plan-next:16、plan-verify:56（以上 feature-workflow）。
佐證（逐字相同行）：bug-fix/SKILL.md:23 與 plan-deploy-confirm/SKILL.md:20「在感到『可以跳過』『應該夠了』的衝動時，**停下查表**…」。

- 重複量：約 5 行 × 11 ＝ 55 行
- 建議：樣板全文已在 `references/discipline-preamble.md`，各 SKILL.md 壓成單行「> 紀律護欄：讀 `references/discipline-preamble.md`＋`anti-rationalizations.md`/`boundaries.md` 的「{skill 名}」段」。**可省約 33 行**（11 × 3）。

## G4：「偵測負責人」流程（跨 plugin 逐字相同）

| Skill | 行號範圍 |
|-------|---------|
| bug-workflow/skills/bug-start/SKILL.md | 82–96 |
| feature-workflow/skills/plan-start/SKILL.md | 82–96 |

15 行完全相同：git config user.email → notion-get-users → email 比對（case-insensitive）→ 填「負責人」→ 失敗不阻塞，含 `person.email` 註記。

- 重複量：15 行 × 2 ＝ 30 行
- 建議：跨 plugin 共用需各自 references/ 放一份（同 discipline-preamble.md 現行做法），或由 bug-workflow/references/notion-backend.md 承載、plan-start 引用。**可省約 13 行**（單 plugin 內看是 15 行 ×1）。

## G5：「建立新專案條目」引導文案（bug-setup / project-add）

| Skill | 行號範圍 |
|-------|---------|
| bug-workflow/skills/bug-setup/SKILL.md | 268–287 |
| bug-workflow/skills/project-add/SKILL.md | 259–276 |

「建立新專案，請填寫以下資訊：…SIT 主機／UAT 主機／正式環境主機／部署方式／說明」引導區塊高度相似（project-add 多了技術棧、PROD/UAT 分支三欄）。後續 Notion 欄位表也重疊。

- 重複量：約 15–20 行相同
- 建議：抽到 `bug-workflow/references/project-page-templates.md`（該檔已存在，本就是放專案頁模板的地方），兩個 skill 引用。**可省約 15 行**。

## G6：「本地檔案 ↔ Notion 區塊」對應表（plan-close / plan-sync）

| Skill | 行號範圍 |
|-------|---------|
| feature-workflow/skills/plan-close/SKILL.md | 44–66（Feature 9 列＋Bug 4 列） |
| feature-workflow/skills/plan-sync/SKILL.md | 76–99（同兩張表，plan-close 多 verify.md 一列） |

兩張對應表（spec.md→📐 技術規格、db.md→🗄️、…、investigation.md→🔍 調查過程…）幾乎相同；且兩者的「Fetch 現有頁面 → update content → update properties」三步同步骨架也相同（plan-close:120 起、plan-sync:70 起）。

- 重複量：約 24 行 × 2 ＝ 48 行
- 建議：對應表抽到 `feature-workflow/references/plan-common.md`（既有共用檔）或 `notion-page-template.md`，兩個 skill 引用。**可省約 24 行**，且未來新增文件類型只改一處。

## G7：環境快照／證據收集流程（bug-start / bug-investigate）

| Skill | 行號範圍 |
|-------|---------|
| bug-workflow/skills/bug-start/SKILL.md | 176–224（初始環境快照） |
| bug-workflow/skills/bug-investigate/SKILL.md | 106–170（Phase 1 證據收集） |

高度相似（非逐字）：git log/branch/status 指令、Bug 知識庫搜尋、學習檔 `learnings/{project-slug}.jsonl` grep、寫入 Notion「調查過程」的 markdown 格式（**環境狀態**：分支/未提交變更、**歷史參考**、**歷史學習** 段完全同構）。精確比對已抓到 bug-investigate:160–163 ≡ bug-start:215–218。

- 重複量：約 35 行相似
- 建議：抽 `bug-workflow/references/evidence-collection.md`（收集指令＋寫入格式），兩 skill 各留差異（bug-start 是快照、bug-investigate 是完整收集）。**可省約 25 行**。

## G8：MCP 安裝指令片段（3 檔重複）

- chrome-devtools 安裝：feature-workflow/skills/plan-setup/SKILL.md:159–165 ≡ plan-verify/SKILL.md:43–49（`claude mcp add chrome-devtools --scope user -- npx chrome-devtools-mcp@latest --autoConnect`＋重啟提示）
- playwright 安裝：plan-verify/SKILL.md:35–36 ≡ bug-workflow/skills/crew-doctor/SKILL.md:120–121

- 重複量：約 16 行
- 建議：feature-workflow/references/ 新增 `mcp-install.md`（或併入 config-resolver.md），三處引用。**可省約 10 行**。安裝指令是最容易改版走鐘的內容，單一來源價值高於行數。

## G9：退出驗證框架（plan-build E1–E7 / plan-start S1–S7，結構同構）

| Skill | 行號範圍 |
|-------|---------|
| feature-workflow/skills/plan-build/SKILL.md | 230–300 |
| feature-workflow/skills/plan-start/SKILL.md | 301–370 |

檢查項目內容不同（E 系 vs S 系），但框架逐段同構：「### 退出驗證（強制，不可跳過）」→「#### 自動驗證項目」同欄位表格（#/檢查項目/驗證方式/失敗處理）→「#### 驗證結果分級」（🔴 BLOCK / ⚠️ WARN）→「#### 驗證報告格式」（寫入 log.md＋回傳顯示）。精確比對抓到 plan-build:234 ≡ plan-start:309、plan-build:291 ≡ plan-start:354。

- 重複量：框架部分約 18 行 × 2
- 建議：框架說明（分級定義、報告格式規範）抽到 `references/plan-common.md`，兩 skill 只留各自的檢查表。**可省約 15 行**。優先級低（內容主體本來就不同）。

---

## 附註 A：跨 plugin references/ 整檔重複（維護風險，非 skill 載入成本）

`cmp` 實測：
- `discipline-preamble.md`：兩 plugin **逐 byte 相同**（44 行）
- `db-templates.md`：兩 plugin **逐 byte 相同**（214 行）
- 近似重複：anti-rationalizations.md（37 vs 49 行）、boundaries.md（79 vs 83 行）、prerequisites.md（178 vs 177 行）、config.template.md（60 vs 158 行）

共 258 行完全相同＋約 300 行近似。plugin 隔離下無法直接跨包引用，屬「刻意複本」；風險是雙邊漂移（prerequisites.md 已出現 1 行差異）。建議：在 marketplace repo 以單一來源＋建置時複製（或 symlink）維護，不影響執行期。

## 附註 B：已做對的部分（不需再抽）

- 18 個 skill 以單行引用 `references/prerequisites.md`（前置檢查）——正確模式。
- plan-spec/plan-db/plan-arch/plan 的「定位活躍任務」都只寫「參照 `references/plan-common.md`」1 行。
- plan-review 的 Agent Teams 環境變數只寫「同 plan-build」（plan-review/SKILL.md:16），未重複展開 plan-build/SKILL.md:14–30 的 19 行設定塊。

## 可省行數彙總（估算）

| 組 | 主題 | 涉及檔數 | 可省行數 |
|----|------|---------|---------|
| G1 | 設定檔區塊（bug-*） | 5＋1 變體 | ~50 |
| G3 | 紀律護欄樣板 | 11 | ~33 |
| G2 | 定位目標 Bug | 3 | ~26 |
| G7 | 環境快照/證據收集 | 2 | ~25 |
| G6 | 檔案↔Notion 對應表 | 2 | ~24 |
| G5 | 建立新專案引導 | 2 | ~15 |
| G9 | 退出驗證框架 | 2 | ~15 |
| G4 | 偵測負責人 | 2（跨 plugin） | ~13 |
| G8 | MCP 安裝指令 | 3 | ~10 |
| **計** | | | **~211 行**（SKILL.md 內文；另附註 A 258 行整檔重複） |
