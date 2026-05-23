---
slug: crew-improvement
type: refactor
name: CREW Plugin 套件改進計畫
created: 2026-05-22
closed: 2026-05-23
status: 已結案（22/23 完成，A2 移至 P3 觀察項）
scope: 全 marketplace（bug-workflow + feature-workflow + 根目錄文件）
author: Cheng
---

# CREW 套件改進計畫

> 全面盤點 CREW marketplace（bug-workflow v3.8.0 + feature-workflow v4.17.0）的可改進之處，
> 列舉具體缺點、為什麼值得修、修法建議與優先級。
>
> **結案狀態**：2026-05-23，22/23 項完成，A2 因高風險移至 P3 長期觀察。

---

## 結案摘要

| 階段 | 項目 | 狀態 | PR |
|------|------|------|-----|
| **P0** | C1 版本同步腳本 / A1 跨 plugin 解耦 / C2 基礎 CI | ✅ 3/3 | #9 |
| **P1** | A1+ 防漂移 / D1 紀律集中 / B2 /crew-doctor / A4 拆 plan-verify Step 10 | ✅ 6/6 | #9-#11 |
| **P2** | C5 gitignore / C4 CHANGELOG 順序 / E1 README 拆解 / D2 model lint / F2 last_verified / B1 /plan-next / B3 /crew-init / E2 ADR / E3 /plan-demo / C3 contract lint / A4 進階 / F1 /plan-deploy-confirm | ✅ 11/12 | #9-#14 |
| **P2** | A2 config 機制統一 | ⏭️ P3 觀察項 | — |

**版本演進**：
- bug-workflow 3.8.0 → 3.10.1（+2 minor +1 patch，新增 /crew-doctor + /crew-init）
- feature-workflow 4.17.0 → 4.22.0（+5 minor +1 patch，新增 /plan-next + /plan-demo + /plan-deploy-confirm + 多項內部重構）

**plan-verify 主檔減量**：1094 → 560 行（**-49%**，拆 Step 5 與 Step 10 到 phases/）

**marketplace 工程基建建立**：
- `scripts/`：bump-version.sh / lint-skills.py / check-shared-refs.py / lint-changelog.py / lint-agent-model.py / lint-skill-contract.py
- `.github/workflows/lint.yml`：6 個 CI job（含 1 個 advisory）
- `docs/`：prerequisites / windows / dbhub / notion-schema + adr/ 5 篇
- `CONTRIBUTING.md`：版本升級、.spec/ 規範、共用 reference 同步流程

---

## P3 觀察項（不在本輪範圍）

### A2 兩 plugin config 機制統一 🔴

- **現況**：bug-workflow 用單檔，feature-workflow 用階層目錄
- **為何不做**：要動使用者既有的 `~/.claude-company/bug-workflow-config.md`，需 migration，失敗會破壞使用者環境
- **觸發條件**：當「雙套設定機制」真的造成維護痛苦（例如要加第三個 plugin 共用設定）時才動
- **預估**：2-3 小時 + migration 腳本 + 向下相容測試
- **追蹤**：本檔案結案後，A2 仍記錄在此供未來決策

---

## 0. 背景與動機

CREW marketplace 從 2026-04 初版至今已迭代數十次（bug-workflow 跨 8 個 minor、feature-workflow 跨 17 個 minor），
功能持續擴張，但伴隨以下系統性訊號：

- 25 個 skills 合計 7004 行，最大單檔 1093 行（超過自家 `ecc-common/coding-style.md` 的 800 行上限）
- `marketplace.json` 中 feature-workflow 版本 `4.8.0`，實際 plugin.json 已到 `4.17.0`，落後 9 個 minor
- 12 個 feature-workflow skills 跨引用 bug-workflow 的 `references/prerequisites.md`
- 升版需手動同步 4 處（plugin.json / 兩份 README / CHANGELOG），CONTRIBUTING.md 自己標註「易錯點」
- 無 CI、無 lint、無測試、無 doctor 指令

本計畫不主張全部立即重做，而是建立優先級，先處理高風險、低成本、高槓桿的項目。

---

## 1. 缺點清單（22 項，6 大類）

### A. 架構與耦合

#### A1. 跨 plugin 強耦合，違反獨立性 🔴

- **現象**：12 個 feature-workflow skills 全部引用 `bug-workflow plugin 的 references/prerequisites.md`
- **影響半徑**：feature-workflow 在 bug-workflow 缺席時功能受損
- **為什麼值得修**：違反 marketplace「plugin 可獨立安裝」核心假設
- **修法**：
  - 方案 A（推薦）：抽出共用 plugin `crew-common`，prerequisites/notion-backend/anti-rationalizations 全放這裡
  - 方案 B：兩個 plugin 各自帶一份 prerequisites（DRY 退讓給獨立性）

#### A2. 兩個 plugin 設定檔機制不一致 🟡

- **現象**：bug-workflow 用單檔 `bug-workflow-config.md`；feature-workflow 用階層目錄 `feature-workflow/{config.md,stacks/,projects/}`
- **為什麼值得修**：學習成本、雙套讀寫邏輯、未來新 plugin 不知該抄哪個
- **修法**：bug-workflow 升級為階層式 `~/.claude-company/bug-workflow/config.md`，附 migration 腳本

#### A3. references 散落，沒有共享層 🟡

- **現象**：anti-rationalizations、boundaries、plan-common 只在 feature-workflow；bug-workflow 有自己的反合理化
- **為什麼值得修**：規則散落多處，更新易不一致
- **修法**：搭配 A1 共用 plugin 一起處理

#### A4. SKILL.md 過大，違反公司自家規範 🔴

- **現象**：
  | Skill | 行數 |
  |-------|------|
  | plan-verify | 1093 |
  | project-add | 482 |
  | plan-start | 420 |
  | bug-investigate | 414 |
  | bug-start | 403 |
  | plan-build | 400 |

- **為什麼值得修**：
  1. Skill 載入佔大量 context tokens
  2. AI 在中段失準（注意力衰減在 ~500 行後明顯）
  3. 維護時找不到段落
  4. 公司規範 `ecc-common/coding-style.md` 明訂 800 max
- **修法**：
  - `plan-verify` 拆 SKILL.md（入口 + 流程骨架）+ `phases/playwright.md` / `api-only.md` / `excel-report.md` / `word-report.md` / `e2e-runner.md`
  - 其他 >400 行同樣拆，目標每檔 ≤ 300 行

#### A5. plan-verify 一檔承擔 9 個模式旗標 🟡

- **現象**：`--deep / --manual / --api-only / --excel / --word / --e2e / --from-e2e / --recheck / <URL>` 九種模式同檔
- **為什麼值得修**：違反 SRP；新增模式影響半徑大；測試難聚焦
- **修法**：主檔做 dispatcher 職責，各模式單檔（與 A4 合併處理）

---

### B. DX 與使用者體驗

#### B1. 指令多達 25 個但無學習導覽 🟡

- **現象**：使用者要記得執行順序（plan-start → spec → db → arch → build → security → verify → review → close），無指令告訴你「目前該做哪步」
- **為什麼值得修**：新人上手陡峭；`/plan-status` 只列任務不指引下一步
- **修法**：新增 `/plan-next`，根據 `.spec/{slug}/` 內已有檔案動態推薦下一步指令

#### B2. 缺 doctor / 健診指令 🟡

- **現象**：環境壞掉（Notion MCP / Agent Teams env / Playwright / config 損毀）只能等執行時噴錯
- **為什麼值得修**：使用者體驗類似「踩雷再修」；首次使用最痛
- **修法**：新增 `/crew-doctor`，一次性檢查所有依賴 + config 完整性 + Notion DB 可讀

#### B3. 首次設定 8 步流程 🟢

- **現象**：notion install → marketplace add → install → /bug-setup → /plan-setup → /init → /project-add → /plan-stack
- **為什麼值得修**：任何中斷都要從頭排查
- **修法**：新增 `/crew-init` 一鍵跑完

#### B4. 錯誤訊息與選項說明不一致 🟢

- **現象**：CHANGELOG 顯示「bug-investigate 自 v3.8 為主入口」，但 README 主流程仍寫 `bug-start → bug-investigate`
- **為什麼值得修**：兩個版本歷史並存於文件，使用者困惑
- **修法**：README 流程圖標明「自 v3.8 起 investigate 為主入口」

---

### C. 工程品質與發版流程

#### C1. marketplace.json 版本與 plugin.json 嚴重不同步 🔴

- **現象**：marketplace.json 寫 feature-workflow `4.8.0`，plugin.json 已 `4.17.0`，落後 9 個 minor
- **為什麼值得修**：
  1. `claude plugin marketplace info` 顯示舊版描述
  2. 新功能對外不可見
  3. CONTRIBUTING.md 自己警告「易錯點」就是描述這個機制不可靠
- **修法**：
  - 新增 `scripts/bump-version.sh <plugin> <version>` 一次性同步：
    - `plugins/{plugin}/.claude-plugin/plugin.json`
    - `.claude-plugin/marketplace.json`（兩處 version 都改）
    - `plugins/{plugin}/README.md` 第一行
    - `CHANGELOG.md` 新增 header
  - PreCommit hook 檢查三處 version 一致

#### C2. 沒有任何 CI / 自動檢查 🔴

- **現象**：無 `.github/workflows/`；無 markdown lint、JSON schema 驗證、版本一致性檢查、SKILL.md 大小檢查、broken link 檢查
- **為什麼值得修**：C1 之所以發生就是因為沒有 CI；PR review 全靠人眼
- **修法**：建立 `.github/workflows/lint.yml`：
  - plugin.json / marketplace.json schema validation
  - SKILL.md frontmatter 必須有 `name` + `description`
  - SKILL.md 行數 ≤ 800
  - 三處 version 一致性
  - 內部 markdown link 必須可達

#### C3. 沒有測試 🟡

- **現象**：0 個 test
- **為什麼值得修**：
  - refactor 無安全網
  - CHANGELOG 上多次「降版補修」（3.5.0 → 3.5.1 修 Skill 未被安裝、3.5.2 修前置檢查）暗示品質波動
- **修法**：
  - 短期：對每個 SKILL.md 做靜態檢查（必要段落、引用檔案存在）
  - 中期：固定 fixtures 跑 AI 並比對輸出格式（prompt regression test）

#### C4. CHANGELOG 版本順序混亂 🟢

- **現象**：CHANGELOG 內為 3.5.0 → 3.6.0 → 3.5.2 → 4.11.x，違反「最新在上」原則
- **為什麼值得修**：`/crew-upgrade` 讀此檔顯示變更摘要時，使用者看到版本順序錯亂
- **修法**：嚴格時間倒序；CI lint 中強制版本號遞減檢查

#### C5. gitignore 與 untracked 雜訊 🟢

- **現象**：根目錄 untracked：`.playwright-mcp/`、`task_plan.md`、`.claude/`、`.spec/deploy-checklist-sync/`、`.spec/push-stat-query/`
- **為什麼值得修**：`git status` 永遠有雜訊；`.spec/` 是否入版控無明確規範
- **修法**：
  - 補 `.gitignore`：`.playwright-mcp/`、`task_plan.md`、`.claude/`、`.spec/` 內非 `crew-improvement` 的暫存目錄
  - CONTRIBUTING 寫清楚：`.spec/crew-improvement/` 等對外設計文件應入版控，其餘 dogfood 暫存不入

---

### D. AI 行為與護欄

#### D1. 反合理化與護欄段落每個 SKILL.md 重複 🟡

- **現象**：「紀律護欄 → 反合理化 → 動作邊界」三句話幾乎每個 SKILL.md 都複製
- **為什麼值得修**：
  1. 加新規則時要改 25 個檔
  2. 重複內容稀釋核心流程的注意力佔比
- **修法**：寫進 plugin 級的 `references/discipline-preamble.md`，SKILL.md 只放一行 import 指示

#### D2. Agent model 參數靠自然語言而非結構化 🟡

- **現象**：`plan-common.md` 自己提醒「prompt 中寫『使用 Opus』只是自然語言，不保證生效，必須用 Agent tool 的 `model` 參數」——但 SKILL.md 仍是自然語言敘述
- **為什麼值得修**：已知陷阱沒被工程化解決；下一個維護者很可能踩同樣坑
- **修法**：把每個會起 Agent 的 skill 內寫成精確的 model 參數對照表，並把這個 gotcha 變成 lint rule

#### D3. 「反合理化」與「鐵律」風格分散 🟢

- **現象**：bug-workflow 用「鐵律」、feature-workflow 用「紀律護欄」、references 又叫「反合理化」
- **為什麼值得修**：同一概念三種名稱，AI 與人類都要重學
- **修法**：統一術語表 `docs/terminology.md`

---

### E. 文件與發現性

#### E1. README 過長（578 行）什麼都塞 🟡

- **現象**：根 README 同時講安裝、流程圖、指令表、Windows 指南、DB MCP TOML、Notion 設定、前置檢查、Schema ER 圖
- **為什麼值得修**：
  1. 新使用者找不到「Hello world」起點
  2. Windows 指南只有 1% 使用者需要卻佔大版面
- **修法**：根 README 精簡到 200 行（安裝 + 流程一圖 + 指令表 + 連結），其他拆到 `docs/{windows.md,dbhub.md,notion-setup.md,prerequisites.md}`

#### E2. 缺架構決策文件（ADR）🟢

- **現象**：核心決策（為何用 .spec/ 而非直接寫 Notion、為何採 leader-delegate、為何 verify 預設 Playwright）只在 CHANGELOG 散見
- **為什麼值得修**：未來想改架構時不知哪些決策有意圖、哪些只是歷史包袱
- **修法**：建 `docs/adr/` 寫 5-10 個關鍵決策

#### E3. 沒有 Quickstart「5 分鐘看到效果」路徑 🟢

- **現象**：第一次完整跑 plan 流程要設 Notion、設 Agent Teams env、註冊專案
- **為什麼值得修**：給 demo / 評估的人沒有 dry-run 路徑
- **修法**：`/plan-demo` 模式不寫 Notion，純本地產出範例 .spec

---

### F. 業務邏輯與功能盲點

#### F1. 部署 SQL 同步機制不可逆 🟡

- **現象**：`plan-close` 把 deploy.sql 寫進 Notion，但 DBA 執行後沒有回流機制，Notion 永遠顯示「未執行」
- **為什麼值得修**：deploy-checklist 本意是把關，缺執行回報就只是文件展示
- **修法**：`/plan-deploy-confirm` 由執行者勾選，寫回 Notion

#### F2. 驗證記憶系統沒有失效策略 🟢

- **現象**：v4.16.0 引入三層驗證記憶自動記錄並升級，但 selector / i18n / API 路徑會隨時間漂移
- **為什麼值得修**：「越做越快」的承諾建立在記憶仍正確；過時記憶比沒記憶更糟
- **修法**：每筆記憶帶 `last_verified_at`，超過 N 天自動降級為「需驗證」狀態

---

## 2. 優先級與路線圖

### P0（立即處理，預估 2 天）

| ID | 項目 | 估時 | 為何 P0 |
|----|------|------|---------|
| C1 | 版本同步腳本 | 半天 | 立即停止 marketplace 落後 |
| A1 | 跨 plugin 引用解耦 | 1 天 | 解開最危險的隱性 bug |
| C2 | 基礎 CI（3 條 lint） | 半天 | 從此防止 C1 復發 |

### P1（一個月內，預估 3-4 天）

| ID | 項目 | 估時 |
|----|------|------|
| A4 | 拆 plan-verify SKILL.md（含 A5） | 1 天 |
| B2 | `/crew-doctor` | 半天 |
| D1 | 紀律段落集中 | 半天 |
| C5 | gitignore + .spec 規範 | 1 小時 |
| C4 | CHANGELOG 排序修正 | 1 小時 |
| B4 | README 流程圖更新（v3.8 入口變更） | 1 小時 |

### P2（滾動處理）

A2、A3、B1、B3、C3、D2、D3、E1、E2、E3、F1、F2

---

## 3. 實作建議：先做 P0 三件，獲得即時穩定性

### 3.1 C1 — 版本同步腳本

```bash
#!/usr/bin/env bash
# scripts/bump-version.sh <plugin> <version>
# 一次性同步：plugin.json + marketplace.json + plugin README + CHANGELOG header
```

驗收：
- 跑 `./scripts/bump-version.sh feature-workflow 4.18.0` 後，4 處檔案 version 一致
- PreCommit hook 偵測不一致時 block commit

### 3.2 A1 — 跨 plugin 解耦

**採方案 B：兩個 plugin 各自帶 prerequisites**

| 方案 | 優點 | 缺點 |
|------|------|------|
| A：抽出 crew-common plugin | DRY、共用更新 | marketplace 多一個 plugin、使用者要多裝、增加維運單元 |
| B（採用）：兩個 plugin 各自帶 prerequisites | 真正獨立、安裝路徑簡單 | 兩份 prerequisites 需同步更新（成本可承受） |

**決策理由**：CREW 兩 plugin 雖常一起用，但保留「可獨立安裝」是 marketplace 模型的核心契約；DRY 是手段不是目的，當它與獨立性衝突時讓步。同步成本透過 C2 lint 自動偵測差異即可控制。

驗收標準：
1. `grep -r "bug-workflow plugin" plugins/feature-workflow/` 結果為空
2. 單獨安裝 feature-workflow（不裝 bug-workflow）後，所有 skill 可正常啟動
3. CI lint 偵測兩份 prerequisites 不一致時 warning

### 3.3 C2 — 基礎 CI

`.github/workflows/lint.yml` 三條規則：

1. 三處 version 一致（plugin.json / marketplace.json / README 第一行）
2. SKILL.md frontmatter 必須有 `name` + `description`
3. SKILL.md ≤ 800 行（warn）/ ≤ 1200 行（fail）

---

## 4. 不做的事（Out of Scope）

明確不在本計畫內：

- 完全重寫 SKILL.md prompt 內容（風險過大）
- 把 .spec/ 機制換成 SQLite / 資料庫（YAGNI）
- 多人協作鎖（單人使用情境居多）
- 國際化 SKILL.md（zh-TW 是定位）

---

## 5. 風險

- **R1**：A1 解耦會影響既有 prerequisites 邏輯，需先確保 bug-workflow 不依賴 feature-workflow 的任何 reference
- **R2**：A4 拆 plan-verify 後 AI 載入路徑變多，需確保 dispatcher 正確路由（用實際任務驗證 3-5 次）
- **R3**：C2 CI 上線後既有未過 lint 的 skill 會失敗，需先做一次大整理 PR 再啟用

---

## 6. 後續步驟

1. 使用者 review 本 spec.md
2. 確認優先級分組與方案選擇（特別是 A1 的 A/B 方案）
3. 若同意 P0，可進入 `/plan-build` 或人工逐項實作
4. P1/P2 滾動排程

---

## 變更歷史

| 日期 | 動作 | 作者 |
|------|------|------|
| 2026-05-22 | 初版盤點與設計 | Cheng + AI Brainstorming |
