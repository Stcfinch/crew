# CREW SKILL.md 統一模板

> 產出日期：2026-07-13
> 適用範圍：bug-workflow（10 skills）＋ feature-workflow（19 skills），共 29 個 SKILL.md。
> 用途：本檔是 C12/C13/C15/C16 批次修改的規範載體，也是未來新增 skill 的撰寫依據。修改既有 skill 時逐段對照本檔；本檔僅規範結構與書寫，不規範各 skill 的業務邏輯。
> 依據來源：`scratchpad/cross/consistency.md`（一致性分析與模板草案）＋ `scratchpad/c-items.md`（C1–C16 優化項）。
> 標注規則：**[必要]** 每個 skill 都要有；**[條件必要]** 符合括號條件時必須有；**[選用]** 依需要。段落順序一律照下列骨架由上而下排列。

---

## 一、段落順序（兩份模板共用，統一固定）

現況有 3 種以上排列且無語意理由，一律收斂為下列順序（缺的段落跳過，不得改變相對次序）：

```
frontmatter → H1 標題 → 摘要 → 何時不用 → 鐵律 → 紀律護欄 → 設定（檔/目錄）
→ 前置條件 → 使用方式 → 流程 → {特殊模式段} → Gotchas → 邊界情況
```

- 尾段固定 `Gotchas` 在前、`邊界情況` 在後（現況僅 plan-browse 反序，須改正）。
- 特殊模式段（`--list`／`--resume`／模式制查詢等）緊接流程之後、Gotchas 之前。

---

## 二、模板 A：bug-workflow（適用 bug-* / crew-* / project-add）

```markdown
---
name: {skill-name}                                      # [必要]
description: {一句功能摘要}。當使用者提到「{詞1}」、「{詞2}」…時觸發此 Skill。   # [必要，尾句固定]
argument-hint: "{<必填引數> [選填引數] [--旗標]}"          # [條件必要：接受任何引數/旗標時]
---

# {skill-name} — {中文標題}                               # [必要，格式固定 `# {name} — {中文標題}`]

{1-3 行功能摘要：做什麼＋產出什麼}                            # [必要]

## 何時不用                                              # [必要，2-3 行；與重疊指令互相標注邊界（C11/C15）]
- {反向案例 → 導向的指令}（例：中途記錄用 /bug-update；feature 結案用 /plan-close）

## 鐵律                                                  # [條件必要：有不可違反的硬前提時（如 bug-fix 根因必填）]

## 紀律護欄                                              # [條件必要：會寫 Notion／改檔案／易被「跳過」誘惑的 skill]

## 設定檔                                                # [必要；純本地 skill（如 crew-upgrade）可免]

## 前置條件                                              # [必要]
- {條件清單}
> **前置檢查**：{見第五節標準句式}                          # [句式統一，見第五節]

## 使用方式                                              # [條件必要：接受引數/旗標時；每個旗標一行，且內文須有對應執行步驟]

## 流程                                                  # [必要]
### 1. {步驟}                                            # 整數連續編號；步驟間指涉用段落名稱不用編號（見第六節）
### 2. {步驟}
…
### N. 回傳結果                                          # [必要，固定為最後一步，附回報區塊範例]

## {特殊模式}                                            # [選用：模式各自成段，緊接流程之後]

## Gotchas                                              # [必要，固定在邊界情況之前]

## 邊界情況                                              # [必要，固定最後一段]
```

段落用途速查：

| 段落 | 標注 | 一句用途 |
|------|------|----------|
| frontmatter | 必要 | 只放 `name`＋`description`（＋接受引數時 `argument-hint`）；不加其他欄位 |
| H1 標題 | 必要 | `# {name} — {中文標題}`，後接 1-3 行摘要 |
| 何時不用 | 必要 | 反向指引，防止與重疊指令誤觸發 |
| 鐵律 | 條件必要 | 宣告不可違反的硬前提，僅真有硬前提者才寫 |
| 紀律護欄 | 條件必要 | 指向 discipline-preamble 等共用紀律，防跳步 |
| 設定檔 | 必要 | 說明設定檔查找順序與缺檔導向 |
| 前置條件 | 必要 | 執行條件清單＋前置檢查句式 |
| 使用方式 | 條件必要 | 列引數/旗標，須與流程步驟對應 |
| 流程 | 必要 | 整數編號步驟，末步固定「回傳結果」 |
| 特殊模式 | 選用 | 非線性模式各自成段 |
| Gotchas | 必要 | 陷阱提醒，每條須在流程有落點 |
| 邊界情況 | 必要 | 異常/邊界處理，固定末段 |

---

## 三、模板 B：feature-workflow（適用 plan-*）

與模板 A 相同骨架與段落順序，僅下列差異：

```markdown
## 設定目錄                                              # [條件必要：直接讀寫設定的 skill
                                                        #  （plan-close/plan-stack/plan-start/plan-sync/plan-deploy-confirm）；
                                                        #  其他 skill 不寫此段，改在前置/流程寫一行「依 references/config-resolver.md 讀取設定」]

## 前置條件                                              # [必要]
> **前置檢查**：{見第五節，feature 輕量版句式}
- 適用類型：Feature / Bug / 兩者                          # [必要；type 不符時明示導向（如 type=bug → /bug-fix）]
- 前置檔案：{spec.md / db.md / arch.md…＋缺檔時的行為}

## 流程
### 1. 定位活躍任務 + 讀取專案上下文                        # [必要，統一參照 plugin 根目錄 references/plan-common.md]
### 2. {主體步驟}                                        # 產出型 skill（spec/db/arch）須附「產出檔章節契約」：
                                                        #  各段最低要求＋subagent 交付前自檢清單（比照 plan-spec）
…
### N. 回傳結果                                          # [必要；回報內容依旗標/條件動態組裝（如 DB_REQUIRED=false 不列 db.md）]

## Gotchas / ## 邊界情況                                  # [必要——plan-arch、plan-db、plan-spec、plan 目前缺，須補；
                                                        #  內容至少涵蓋：缺前置檔、type 不符、subagent 失敗三種]
```

段落用途差異速查：

| 段落 | 標注 | 一句用途 |
|------|------|----------|
| 設定目錄 | 條件必要 | 僅直接讀寫設定者用「設定目錄」（對應 feature 的目錄＋config-resolver 機制）；其餘引用 config-resolver.md |
| 前置條件（適用類型） | 必要 | 明示支援的 type 與不符時導向 |
| 流程首步 | 必要 | 一律「定位活躍任務 + 讀取專案上下文」並參照 plan-common.md |
| 產出檔章節契約 | 條件必要 | 產出型 skill 必附，控制產出形狀 |

---

## 四、觸發詞段格式（frontmatter description）

- 尾句固定：`當使用者提到「{詞1}」、「{詞2}」…時觸發此 Skill。`（29/29 已一致，照抄）。
- 觸發詞避免單字級／日常語級（如「plan」「build」「驗證」「想一下」「修復」），改帶完整組合詞或 `/指令名`（C10）；每個 skill 保留 1–2 個「不會出現在日常對話」的組合詞，維持自然語言可發現性。
- 與重疊指令的邊界寫在「何時不用」段，不塞進 description（C11）。
- `argument-hint`：凡接受位置引數或旗標者必補（bug-start、plan-next、plan-start 等現況缺）。

---

## 五、前置檢查標準句式（定稿，逐字照抄）

同一個 `prerequisites.md` 現況有 4 種句式，收斂為下列 3 種，依 skill 性質擇一（C13）。路徑一律指向 plugin 根目錄（見第七節）。

- **bug-workflow（全部，完整檢查）**：

  > **前置檢查**：參照 plugin 根目錄 `references/prerequisites.md`（相對 SKILL.md 為 `../../references/`）執行完整前置檢查（CLAUDE.md + 設定檔 + 專案註冊）。

- **feature-workflow（輕量版，多數 plan-*）**：

  > **前置檢查**：參照 plugin 根目錄 `references/prerequisites.md`（相對 SKILL.md 為 `../../references/`）檢查 CLAUDE.md 是否存在。

- **feature-workflow 需完整檢查者（plan-start / plan-close / plan-sync）**：

  > **前置檢查**：參照 plugin 根目錄 `references/prerequisites.md`（相對 SKILL.md 為 `../../references/`）執行完整前置檢查（CLAUDE.md + 設定目錄 + 專案註冊）。

規則：
1. bug 側用「設定檔」、feature 側用「設定目錄」，各自內部一致，不互換。
2. 只檢查部分項時（如 project-add 只檢查專案註冊）須在句中明列項次，不得含糊寫「只檢查第 2 項」而不說第 2 項是什麼。
3. 括號路徑提示 `（相對 SKILL.md 為 `../../references/`）` 為固定尾註；若本環境實測 `${CLAUDE_PLUGIN_ROOT}` 可展開，可改寫為 `${CLAUDE_PLUGIN_ROOT}/references/prerequisites.md`（先實測 1 檔通過再批次套用）。

---

## 六、步驟編號規則（C16）

1. **整數連續編號**：`### 1.` `### 2.` `### 3.` …，不得用小數插入步驟（禁止 `6.5`／`7.3`／`1.5` 這類跳號；現況 bug-start `6.5→6.7→6.8`、plan-build `7→7.3→7.5→8` 須重編為整數連續）。
2. **禁止編號重複**：同一數字不得出現兩次（現況 bug-update:78-79 兩個「3.」須修）。
3. **指涉用段落名稱、不用編號**：步驟之間、跨檔互相引用時一律寫段落名稱（例：「見『退出驗證』一節」「見流程『定位目標 Bug』步驟」），**不得**寫「見步驟 5」「如步驟 3 所述」。編號只用於當前步驟的序位，不用於互相指涉——這樣重編號時不會產生指涉腐化（現況 plan-build:374、plan-status:167 因編號指涉已腐化）。
4. **跨檔引用同步**：feature-workflow ↔ bug-workflow 的跨 plugin 引用（如 plan-start 引 bug-start）一律改為段落名稱引用，避免鎖死重編。
5. **末步固定**：流程最後一步固定為「回傳結果」，附回報區塊範例。
6. **非線性 skill 例外**：多模式查詢工具（plan-browse）可用「模式 1~6」，不強制改成流程步驟（見第八節）。
7. 改完以 `grep -nE '步驟 *[0-9]'` 逐一核對，確認無殘留的編號指涉。

---

## 七、通用書寫規則（兩份模板共用）

1. **references 路徑統一**：實體檔在 plugin 根目錄（`bug-workflow/references/`、`feature-workflow/references/`），29 個 skill 目錄下並無 references/。SKILL.md 內一律寫「plugin 根目錄 `references/…`（相對 SKILL.md 為 `../../references/`）」；本環境實測 `${CLAUDE_PLUGIN_ROOT}` 可展開時改用 `${CLAUDE_PLUGIN_ROOT}/references/…`（C12，先實測再批次）。
2. **檔內路徑寫完整相對根路徑**：如 `.spec/{slug}/README.md`，不可只寫 `README.md`。
3. **巢狀 code fence**：範例內含 code fence 時，外層用四個反引號 ```` ``` ````→```` ```` ````（避免 bug-investigate:150 那類外層提前閉合）。
4. **禁止時效性字面值**：版本號（「回退到 v4.9.0」）、工具數（「29 種工具」）、API 呼叫次數上限（「僅 3-5 次」）改為描述性文字或範圍，避免自相矛盾與過時。
5. **範例情境用中性假例**：統一用「推播標籤查詢／SSO 登入異常」（plan-browse、plan-status 既有慣例），不得寫入特定客戶專案名（如 AQI、防汛水費、LineBC、Solr apilog）。
6. **單一資訊源**：同一資訊只在一處寫死、他處引用（如 prod_branch 回退邏輯、Notion 欄位名以 db-templates.md 為權威）。
7. **Gotcha 必須有落點**：每條 Gotcha 警告的行為，須在流程中有對應實作或指示（避免 crew-upgrade:167 那類警告無實作）。
8. **旗標必須有對應步驟**：每個宣告的旗標在流程內文須有對應執行步驟（避免 plan-verify:26 `--from-e2e` 只出現在用法清單）。
9. **紀律護欄可壓縮但保留關鍵指令**：壓成指向 `references/discipline-preamble.md`＋anti-rationalizations.md／boundaries.md 的「{skill 名}」段時，行內須保留「停下查表」一句（C2）；並先確認該專用段真實存在，不得指向空段落。
10. **語言規範**：正文、標題、註解、回報區塊一律繁體中文；技術名詞、程式碼識別字、指令名、`Gotchas` 標題保持原文。

---

## 八、合理個別差異（不強制統一，勿為統一而統一）

以下 7 項為刻意保留的差異，批改時**不得**改動：

| # | 差異 | 保留理由 |
|---|------|----------|
| 1 | plan-explore 整檔 persona 形態（姿態／你可能會做的事／護欄），不套流程模板 | 它是思考夥伴模式，非流程型 skill；套流程模板反破壞設計 |
| 2 | plan-browse 用「模式 1~6」而非整數流程步驟（僅尾段順序須修正） | 多模式查詢工具本質非線性，模式制比硬編步驟更準確 |
| 3 | 「鐵律」段僅 bug-fix / bug-investigate 有 | 只有真有硬前提（根因必填）者才需要，擴散全體會稀釋權威性 |
| 4 | 「設定檔」（bug）vs「設定目錄」（feature）命名不同 | 兩 plugin 設定機制實際不同（單檔 vs 目錄＋config-resolver），名稱如實反映即可，各自內部一致即可 |
| 5 | 檔案長度差異（plan-arch 56 行 vs plan-verify 563 行） | 長度反映複雜度，非結構問題；plan-arch 要補的是契約段而非加長 |
| 6 | 標題後綴「（零 Notion 呼叫）」與 description「不呼叫 Notion API」 | plan/plan-spec/plan-db/plan-arch/plan-status 共用的區辨訊號，單檔移除反破壞一致性 |
| 7 | `Gotchas` 沿用英文標題 | 29 檔已一致，改中文是無收益的攪動 |
