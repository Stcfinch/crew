# CREW 29 Skills 結構一致性分析與統一模板建議

> 產出日期：2026-07-13
> 資料來源：findings/*.json 中 dimension=structure 的 58 條已驗證發現（29 檔全數）＋全 29 個 SKILL.md 的 frontmatter/標題結構掃描＋6 個深讀樣本（bug-start 403 行、bug-fix 285 行、crew-upgrade 179 行／plan-build 401 行、plan-deploy-confirm 242 行、plan-arch 56 行）。
> 路徑基準：`/Users/cheng/.claude/plugins/marketplaces/company-marketplace.bak/plugins/`，以下行號皆為 SKILL.md 內行號。

---

## 一、現況差異清單

### 1. Frontmatter 欄位使用

| 現況 | 佐證 |
|------|------|
| 29/29 一律只有 `name` + `description` 兩欄，無其他欄位 | 全檔掃描（awk frontmatter 欄位名），零例外 |
| 接受位置引數/旗標的 skill 全部缺 `argument-hint` | bug-start（引數見 `bug-workflow/skills/bug-start/SKILL.md:31`、frontmatter :1-4 無宣告）、plan-next（`feature-workflow/skills/plan-next/SKILL.md:2`，支援 `<slug>`/`--all`）、plan-start（`feature-workflow/skills/plan-start/SKILL.md:2`） |
| description 尾句 29/29 統一為「當使用者提到「…」時觸發此 Skill」 | 全檔掃描一致（此點**已一致**，模板照抄即可） |

### 2. 段落命名與存在性（段落集合不一致）

| 段落 | 有 | 無（或變體） | 佐證 |
|------|-----|------|------|
| `## 鐵律` | 僅 bug-fix、bug-investigate | 其餘 27 檔 | `bug-workflow/skills/bug-fix/SKILL.md:12`、`bug-investigate/SKILL.md:12` |
| `## 紀律護欄` | 11 檔（bug-fix:19、bug-investigate:19、crew-doctor:13、crew-init:22、plan-build:40、plan-review:29、plan-security:21、plan-demo:14、plan-deploy-confirm:15、plan-next:16、plan-verify:56），措辭為同一 boilerplate | 其餘 18 檔，含同樣會寫 Notion 的 bug-start、bug-close、plan-close、plan-start；選取標準無處說明 | 各檔行號如左 |
| `## 設定檔` vs `## 設定目錄` | bug-workflow 6 檔用「設定檔」（bug-close:12、bug-fix:27、bug-investigate:27、bug-start:12、bug-update:14、project-add:21）；feature-workflow 4 檔用「設定目錄」（plan-close:12、plan-stack:12、plan-start:12、plan-sync:12） | 其餘檔案無此段，靠 prerequisites/config-resolver 引用；plan-deploy-confirm 需讀設定卻兩者皆無（finding：`plan-deploy-confirm/SKILL.md:39` 未指引如何讀取，其他 5 個 skill 均引 config-resolver.md） | |
| `## 使用方式` | 17 檔 | bug-start、bug-close、bug-setup、project-add、plan-arch、plan-close、plan-db、plan-setup、plan-spec、plan-start 無；bug-update 改放文末「快捷用法彙整」（:209）、plan-stack 用「## 參數」（:20） | 標題掃描 |
| `## Gotchas` + `## 邊界情況` | 24 檔有兩者 | plan-arch、plan-db、plan-spec、plan（4 檔皆無）；plan-explore 用「## 護欄」（:313）替代 | 標題掃描 |
| 「何時不用」反向指引段 | **0/29**（grep 零命中） | structure findings 有 6 檔明確建議補：bug-close:6、bug-fix:6、crew-doctor:8、plan-arch:3、plan-setup:6-8、plan-explore:169 | |

### 3. 段落順序（同樣的段落，三種以上排列）

- bug-fix：鐵律 → 紀律護欄 → 設定檔 → 前置條件 → 使用方式 → 流程（:12/19/27/37/46/56）
- plan-build：前置條件 → 紀律護欄 → 使用方式 → 流程（:12/40/48/60）
- plan-deploy-confirm：紀律護欄 → 使用方式 → 前置條件 → 流程（:15/23/35/43）
- 尾段慣例為 Gotchas → 邊界情況（24 檔），唯 plan-browse 反序且中插一段：邊界情況(:255) → 與其他指令的銜接(:267) → Gotchas(:281)。

### 4. 步驟編號風格

- **小數插入步驟氾濫且跳號**：bug-start `6.5 → 6.7 → 6.8`（:173/231/309，缺 6.6，finding 指出弱模型會誤以為漏步驟）；plan-build `7 → 7.3 → 7.5 → 8`（:156/188/230/306，缺 7.1/7.2/7.4）；另有 1.5（bug-close:53、bug-fix:72）、2.5（bug-close:121、plan-verify:131/142）、3.5（plan-db:45）、4.5（plan-close:89）、5.5（plan-verify:298）、6.5（bug-close:214）、9.5（plan-start:301）。
- **編號重複**：bug-update:78-79 兩行都是「3.」，後續錯位。
- **編號指涉腐化**：plan-build:374 說「步驟 5 檢查 DB MCP」但實為步驟 3；plan-status:167 寫「步驟 5」實為第 6 節——用編號互相指涉，一重編就壞。
- **變體風格**：bug-update 用 `0 / 1-A / 1-B`（:34/41/60）；plan-browse 用「模式 1~6」（:39/73/143/176/203/232）。
- **交叉引用鎖死重編**：feature-workflow/plan-start/SKILL.md:243,251 跨 plugin 引用 bug-start 的「步驟 6.7/6.8」，重編需同步改。

### 5. 前置檢查（觸發詞段之外的固定引言）寫法

同一個 `references/prerequisites.md` 引用出現 4 種句式：
1. 「執行完整前置檢查（CLAUDE.md + 設定檔 + 專案註冊）」— bug-workflow 5 檔 + plan-close:29、plan-start:26
2. 「檢查 CLAUDE.md 是否存在」— feature-workflow 9 檔（plan-arch:14、plan-db:14 等）
3. 「（CLAUDE.md + 設定**目錄** + 專案註冊）」— plan-sync:18 獨有變體
4. 「本 Skill 只檢查第 2 項」— project-add:14（且 finding 指出與其大量呼叫 Notion 的行為矛盾）

另外全部以 `references/…` 相對路徑書寫，但 29 個 skill 目錄下**都沒有** references/，實檔在 plugin 根目錄（`bug-workflow/references/`、`feature-workflow/references/`）——這是 reference 維度最大宗 finding（bug-close:27、bug-fix:21、plan-build:36 等 8 處、plan-db:14,25,43,51,57…），但根源是結構慣例，應由模板統一路徑寫法解決。

### 6. 語言混用與內容風格

- 段落標題中英混用但**全體一致**：`Gotchas` 用英文、其餘段落中文，29 檔一致 → 不算問題。
- 範例情境不一致：plan-explore:196-276 內嵌特定專案敘事（AQI、防汛水費、LineBC、Solr apilog），而 plan-browse:49-58 與 plan-status:77-89 用同一組中性假例（推播標籤查詢、SSO 登入異常）→ 後者才是該遵循的慣例。
- Markdown 結構壞損：bug-investigate:150-170、283-298 在 ```` ```markdown ```` 範例內再嵌 ``` fence，外層提前閉合。
- 時效性字串寫死：plan-build:87「回退到 v4.9.0 邏輯」、plan-setup:150-156「29 種工具」、plan-close:8「僅 3-5 次」與 :279 Gotcha 自相矛盾。

### 7. 已一致、值得寫入模板固定下來的既有慣例

- H1 格式 29/29 一致：`# {name} — {中文標題}`，後接 1-3 行摘要。
- 流程最後一步固定「回傳結果」＋固定回報區塊（25/29；例 plan-arch:45、bug-close:263、plan-close:255）。
- plan 系列標題後綴「（零 Notion 呼叫）」是與 plan-sync/plan-close 的區辨訊號（plan-arch finding 明確裁定保留，勿單檔移除）。

---

## 二、統一模板

標注規則：**[必要]** 每個 skill 都要有；**[條件必要]** 符合括號條件時必須有；**[選用]** 依需要。

### 模板 A：bug-workflow（適用 bug-* / crew-* / project-add）

```markdown
---
name: {skill-name}                                      # [必要]
description: {一句功能摘要}。當使用者提到「{詞1}」、「{詞2}」…時觸發此 Skill。   # [必要，尾句固定]
argument-hint: "{<必填引數> [選填引數] [--旗標]}"          # [條件必要：接受任何引數/旗標時]
---

# {skill-name} — {中文標題}                               # [必要，格式固定]

{1-3 行功能摘要，說明做什麼＋產出什麼}                        # [必要]

## 何時不用                                              # [必要，2-3 行]
- {反向案例 1 → 導向的指令}（例：中途記錄用 /bug-update；功能任務結案用 /plan-close）

## 鐵律                                                  # [條件必要：有不可違反的硬前提時（如 bug-fix 根因必填）]

## 紀律護欄                                              # [條件必要：會寫 Notion/改檔案/易被「跳過」誘惑的 skill；boilerplate 三行照抄，並確認 anti-rationalizations.md／boundaries.md 真的有對應專用段]

## 設定檔                                                # [必要（純本地 skill 如 crew-upgrade 可免）]
依序檢查：1. ~/.claude-company/bug-workflow-config.md 2. ~/.claude/bug-workflow-config.md
若都不存在，提示先執行 /bug-setup。

## 前置條件                                              # [必要]
- {條件清單}
> **前置檢查**：參照 plugin 根目錄 `references/prerequisites.md`（相對 SKILL.md 為 `../../references/`）執行完整前置檢查（CLAUDE.md + 設定檔 + 專案註冊）。   # [句式統一為此一種；只檢查部分項時明列項次]

## 使用方式                                              # [條件必要：接受引數/旗標時；每個旗標一行＋內文必須有對應執行步驟]

## 流程                                                  # [必要]
### 1. {步驟}                                            # 整數連續編號；插入新步驟時重編並全檔（含跨檔）更新指涉；
### 2. {步驟}                                            # 步驟間互相指涉用「具名引用」（如「見『退出驗證』一節」）而非編號
…
### N. 回傳結果                                          # [必要，固定為最後一步，附回報區塊範例]

## {特殊模式}                                            # [選用：--list、--resume 等模式各自成段，緊接流程之後]

## Gotchas                                              # [必要，順序固定在邊界情況之前]

## 邊界情況                                              # [必要，固定最後一段]
```

### 模板 B：feature-workflow（適用 plan-*）

與模板 A 差異處：

```markdown
## 設定目錄                                              # [條件必要：直接讀寫設定的 skill（plan-close/plan-stack/plan-start/plan-sync/plan-deploy-confirm）；
                                                        #  其他 skill 一律寫一行「依 references/config-resolver.md 讀取設定」即可]

## 前置條件                                              # [必要]
> **前置檢查**：參照 plugin 根目錄 `references/prerequisites.md` 檢查 CLAUDE.md 是否存在。   # [feature 側統一為此句式（輕量版）；需完整檢查者（plan-start/plan-close/plan-sync）改用模板 A 句式並統一寫「設定目錄」]
- 適用類型：Feature / Bug / 兩者                          # [必要：plan-start 支援 bug 型，各 skill 必須明示 type 不符時的導向（如 type=bug → /bug-fix）]
- 前置檔案：{spec.md / db.md / arch.md…＋缺檔時的行為}

## 流程
### 1. 定位活躍任務 + 讀取專案上下文                        # [必要，統一參照 references/plan-common.md]
### 2. {主體步驟}                                        # 產出型 skill（spec/db/arch）必附「產出檔章節契約」：各段最低要求＋subagent 交付前自檢清單（比照 plan-spec 的做法；plan-arch/plan-db findings 均因缺此而產出形狀不受控]
…
### N. 回傳結果                                          # [必要；回報內容需依旗標/條件動態組裝（如 DB_REQUIRED=false 不列 db.md）]

## Gotchas / ## 邊界情況                                  # [必要——plan-arch、plan-db、plan-spec、plan 目前缺，需補；內容至少涵蓋：缺前置檔、type 不符、subagent 失敗三種]
```

### 模板通用書寫規則（兩份模板共用）

1. 檔內路徑一律寫完整相對根路徑：`.spec/{slug}/README.md`（不可只寫 `README.md`，plan-db:17,33,39 教訓）；references 一律註明在 plugin 根目錄。
2. 範例內嵌 code fence 時外層用四個反引號（bug-investigate:150 教訓）。
3. 禁止時效性字面值：版本號（plan-build:87）、工具數（plan-setup:150）、API 呼叫次數上限（plan-close:8）改為描述性文字或範圍。
4. 範例情境統一用中性假例「推播標籤查詢／SSO 登入異常」（plan-browse、plan-status 既有慣例），不得寫入特定客戶專案名。
5. 同一資訊只在一處寫死、他處引用（plan-review:57 vs :257 prod_branch 兩套回退邏輯的教訓；bug-setup:124 欄位名以 db-templates.md 為權威）。
6. Gotcha 必須有落點：警告的行為要在流程中有對應實作或指示（crew-upgrade:167 版本比較警告無實作的教訓）。
7. 每個宣告的旗標在內文必須有對應執行步驟（plan-verify:26 `--from-e2e` 只出現在用法清單的教訓）。

---

## 三、哪些差異值得統一、哪些是合理個別差異

### 值得統一（依影響排序）

| # | 差異 | 理由 |
|---|------|------|
| 1 | 步驟編號改整數連續＋具名引用 | 小數跳號（bug-start:173、plan-build:188）與編號指涉腐化（plan-build:374、plan-status:167）已實際造成 4 條 findings；是弱模型誤判「漏步驟」的直接來源 |
| 2 | 前置檢查句式收斂為每 plugin 一種＋路徑註明 plugin 根 | 4 種句式×錯誤相對路徑是全 29 檔 reference findings 的最大宗根源 |
| 3 | 補「何時不用」段為必要段 | 0/29 存在、6 檔被點名；CREW 內部指令重疊多（bug-update/bug-close、plan-close/plan-sync），這是最便宜的防誤用手段 |
| 4 | plan-arch/plan-db/plan-spec/plan 補 Gotchas＋邊界情況 | 唯 4 個缺尾段的檔恰是「產出形狀不受控」被點名的檔，非巧合 |
| 5 | `argument-hint` 補齊 | 3 條 findings、零風險（最壞被忽略） |
| 6 | 尾段順序固定 Gotchas → 邊界情況 | 只有 plan-browse 反序，改一檔即全體一致 |
| 7 | 段落順序固定（何時不用→鐵律→護欄→設定→前置→使用方式→流程→模式段→Gotchas→邊界） | 現有 3 種排列無任何語意理由，統一零成本 |
| 8 | 紀律護欄的**選取準則**明文化（寫進 references/discipline-preamble.md 開頭） | 11/29 有此段但標準不明；bug-start、plan-close 同樣寫 Notion 卻沒有，該有沒有比措辭更重要 |

### 合理個別差異（不要為統一而統一）

| 差異 | 保留理由 |
|------|----------|
| plan-explore 整檔 persona 形態（姿態/你可能會做的事/護欄） | 它是思考夥伴模式，不是流程型 skill；套流程模板反而破壞其設計 |
| plan-browse 用「模式 1~6」而非步驟編號 | 多模式查詢工具本質非線性，模式制比硬編步驟更準確（僅尾段順序需修） |
| 「鐵律」段僅 bug-fix/bug-investigate 有 | 只有真正存在硬前提（根因必填）的 skill 才需要，擴散到全體會稀釋其權威性 |
| 「設定檔」（bug）vs「設定目錄」（feature） | 兩 plugin 的設定機制實際不同（單檔 vs 目錄＋config-resolver），名稱如實反映即可，只需各自內部一致 |
| 檔案長度差異（plan-arch 56 行 vs plan-verify 563 行） | 長度反映複雜度，不是結構問題；plan-arch 的問題是缺契約段，不是太短 |
| 標題後綴「（零 Notion 呼叫）」與 description 中「不呼叫 Notion API」 | plan/plan-spec/plan-db/plan-arch/plan-status 共用的區辨訊號（plan-arch finding 已裁定保留），單檔移除反破壞一致性 |
| Gotchas 用英文標題 | 29 檔已一致，改中文是無收益的攪動 |
