# CREW 深層優化 — 技術規格書

## 參考來源

- [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) — 20 個 AI 工程紀律 Skill，核心創新：反合理化表、強制驗證退出條件、三層邊界系統、脈絡工程元技能
- [gstack qa skill](~/.claude/skills/qa/SKILL.md) — 結構化 QA 工作流，核心能力：gstack browse ($B) 快速瀏覽器、health score 量化品質、snapshot diff、@e ref 交互系統、regression baseline
- CREW feature-workflow v4.9.0 現有架構

---

## 優先級與實施階段

| 階段 | 優先級 | 項目 | 投入 | 收益 | 涉及檔案 |
|------|--------|------|------|------|---------|
| Phase 1 | P0 | 反合理化表 | 低 | 高 | 新增 references/anti-rationalizations.md + 修改 4 個 SKILL.md |
| Phase 1 | P0 | 退出驗證門檻 | 中 | 高 | 修改 plan-build SKILL.md |
| Phase 2 | P1 | 三層邊界系統 | 低 | 中 | 新增 references/boundaries.md + 修改 4 個 SKILL.md |
| Phase 2 | P1 | plan-security Skill | 中 | 高 | 新增 skills/plan-security/SKILL.md + 修改 plugin.json + 修改 plan-review |
| Phase 3 | P2 | 脈絡工程策略 | 中 | 中 | 新增 references/build-context-layers.md + 修改 plan-build 步驟 5-6 |
| Phase 2 | P1 | plan-verify 改造（gstack browse） | 高 | 高 | 重寫 plan-verify SKILL.md + 新增 references/verify-gstack.md |
| Phase 3 | P2 | 漸進式揭露重構 | 中 | 中 | 新增 references/ + 修改 plan-build |
| Phase 3 | P2 | 智慧團隊組成 | 中 | 中 | 新增 references/team-composition.md + 修改 plan-spec、plan-build |
| Phase 3 | P2 | 技術棧陷阱 | 低 | 中 | 修改 stacks/_builtin.md 結構 + 範本 |

---

## Phase 1：AI 紀律護欄（P0）

### 1.1 反合理化表

#### 概念

每個 SKILL.md 新增 `## 常見偏離與反駁` 段落，列出 AI 在執行該 Skill 時最可能的「偷懶藉口」和對應的反駁。這是 agent-skills 最具創新性的設計 — 不靠希望 AI 自律，而是預先列出並反駁它的藉口。

#### 架構決策：集中 + 引用

反合理化表的內容集中管理在 `references/anti-rationalizations.md`，各 SKILL.md 透過引用載入對應段落。原因：

1. 避免多個 SKILL.md 重複通用條目
2. 集中管理方便迭代更新
3. 按需載入 — Skill 只讀自己的段落

#### references/anti-rationalizations.md 結構

```markdown
# 反合理化參考

## 通用（所有 plan-* Skill 適用）

| # | AI 的內心獨白 | 為什麼不行 |
|---|-------------|-----------|
| G1 | 「先跳過這步，之後再補」 | 之後不會補。每個跳過的步驟都是下游的隱性債務。 |
| G2 | 「使用者趕時間，精簡一下」 | 使用者沒說精簡。精簡 = 品質下降 = 之後花更多時間修。 |
| G3 | 「這太簡單不需要完整流程」 | 簡單的事會變複雜。流程保護的是未來，不是現在。 |

## plan-build 專用

| # | AI 的內心獨白 | 為什麼不行 |
|---|-------------|-----------|
| B1 | 「arch.md 不存在，我先快速產一個再繼續 build」 | arch.md 是 hard block。自動補產的架構沒有經過使用者審閱，錯誤的類別清單和介面定義會傳遞給所有 Teammate，錯誤被放大 5 倍。 |
| B2 | 「只有 3 個檔案要改，開 Agent Teams 太重了，我自己寫比較快」 | Leader 自己寫 code 會跟 Teammate 產出衝突（寫同一個檔案）。即使只有 3 個檔案，Subagent 模式仍然是正確的選擇。 |
| B3 | 「spec.md 太長了，我只讀 arch.md 就好」 | arch.md 定義「怎麼做」，spec.md 定義「做什麼」。跳過 spec.md 意味著 Teammate 不知道業務規則、驗證邏輯、錯誤處理策略。產出的 Service Impl 會全是空 TODO。 |
| B4 | 「掃描現有範本太慢，我直接根據技術棧定義產生」 | 技術棧定義只有框架和 ORM 類型，沒有 package 結構、import 順序、annotation 風格、命名慣例。跳過範本掃描的產出需要大量手動修正。 |
| B5 | 「Teammate prompt 已經夠長了，不需要再塞技術棧定義」 | 沒有技術棧定義的 Teammate 會用 Spring Boot 的預設風格，對 Spring MVC 4.x 專案會產出完全錯誤的程式碼（annotation 不同、配置方式不同）。 |
| B6 | 「files.md 只是紀錄，跳過不影響功能」 | plan-review 從 files.md 讀取審查範圍。沒有 files.md，Reviewer 要從 git diff 取得，可能包含不相關的檔案，審查品質下降。 |
| B7 | 「DB MCP 查詢太慢，跳過 DB 工程師直接讓後端開始」 | DB 工程師驗證表結構一致性。跳過意味著後端工程師可能根據過期的 db.md 產生 Entity，欄位名/型別與實際 DB 不符。 |
| B8 | 「退出驗證太嚴格，這次先跳過」 | 退出驗證是防止假完成的最後防線。跳過意味著 plan-review 和 plan-verify 要處理本該在 build 階段就擋住的問題。 |

## plan-review 專用

| # | AI 的內心獨白 | 為什麼不行 |
|---|-------------|-----------|
| R1 | 「程式碼很簡單，用 --quick 就好」 | --quick 只有邏輯審查，沒有品質和效能軸。簡單的程式碼最容易有 N+1 查詢和不一致的風格。 |
| R2 | 「交叉審查沒新發現，跳過合併步驟」 | 合併步驟不只是匯總，還要去重和排優先級。跳過會讓 review.md 充斥重複問題。 |
| R3 | 「verify.md 有 FAIL 項目但那是環境問題，不需要在 review 中提」 | Reviewer 應該判斷 FAIL 是程式碼問題還是環境問題，不是 Leader。把判斷責任留給 Reviewer。 |

## plan-verify 專用

| # | AI 的內心獨白 | 為什麼不行 |
|---|-------------|-----------|
| V1 | 「API 回傳 200 就算 PASS」 | HTTP 200 只代表沒有伺服器錯誤。回應格式、資料筆數、欄位完整性都可能不對。必須驗證回應 body。 |
| V2 | 「snapshot 太長了，我只看前幾行」 | 表格的分頁按鈕、錯誤訊息通常在 snapshot 的下半部。只看前幾行會漏掉 UI 問題。 |
| V3 | 「這條驗收條件需要登入，太複雜了，標 SKIP」 | plan-verify 的核心價值就是使用已登入的 Chrome session。標 SKIP 等於放棄驗證。用 evaluate_script 取 cookie 後以 curl 呼叫。 |

## plan-security 專用

| # | AI 的內心獨白 | 為什麼不行 |
|---|-------------|-----------|
| S1 | 「這只是內部 API，不需要安全掃描」 | 內部 API 被 SSRF 攻擊時跟外部 API 一樣危險。而且「內部」定義會隨時間改變。 |
| S2 | 「這個 ${} 是用在 ORDER BY，不能用 #{}」 | 正確，但需要 allowlist 驗證。不是「不能用 #{}」就代表「可以用 ${}」，還有第三條路。 |
| S3 | 「專案已經有 ESAPI，安全應該 OK」 | ESAPI 存在不代表正確使用。最常見的問題是新程式碼忘記呼叫 ESAPI 方法。 |
| S4 | 「掃描結果太多 false positive，沒什麼用」 | Layer 1 是機械掃描，確實有 false positive。但 Layer 2 和 3 是上下文感知的，不能因為 Layer 1 有雜訊就跳過全部。 |
```

#### SKILL.md 引用方式

在每個 SKILL.md 的 `## 流程` 段落之前加入：

```markdown
## 紀律護欄

> 執行前閱讀 `references/anti-rationalizations.md` 的「通用」和「{skill} 專用」段落。
> 在任何步驟中感到「可以跳過」的衝動時，查表確認是否為已知偏離模式。
```

#### 影響範圍

| 動作 | 檔案 |
|------|------|
| 新增 | `references/anti-rationalizations.md` |
| 修改 | `skills/plan-build/SKILL.md` — 加入引用段落 |
| 修改 | `skills/plan-review/SKILL.md` — 加入引用段落 |
| 修改 | `skills/plan-verify/SKILL.md` — 加入引用段落 |
| 修改 | `skills/plan-security/SKILL.md` — 新 Skill 內建引用（Phase 2 才建立） |

---

### 1.2 退出驗證門檻

#### 概念

plan-build 完成後、回傳結果前（步驟 7 和步驟 8 之間），新增強制性的自動驗證門檻。門檻未通過不能標記完成。

#### 新增步驟：7.5 退出驗證

插入在現有步驟 7（更新 .spec/ 檔案）和步驟 8（回傳結果）之間。

```markdown
### 7.5 退出驗證（強制，不可跳過）

Leader 在回傳結果前，逐項檢查以下退出條件：

#### 自動驗證項目

| # | 檢查項目 | 驗證方式 | 失敗處理 |
|---|---------|---------|---------|
| E1 | 所有 Teammate 都已完成 | 確認每個 Teammate 回報了完成訊息 | 等待或重試未完成的 Teammate |
| E2 | files.md 已產出 | 檢查 .spec/{slug}/files.md 存在且非空 | 從 Teammate 產出中彙整產出 files.md |
| E3 | 產出檔案真的存在 | 讀取 files.md，用 ls 或 Read 確認每個檔案路徑存在 | 列出缺失檔案，要求使用者決定：重試 / 移除 |
| E4 | 無編譯錯誤（若可驗證） | 若專案有 build 指令（mvn compile / gradle build），執行一次 | 顯示錯誤訊息，標記 ⚠️ 但不阻擋 |
| E5 | API 契約一致性 | 比對 Controller 的 @RequestMapping 與 spec.md 的 API 端點 | 列出不一致項目，標記 ⚠️ |
| E6 | spec.md 驗收條件有對應程式碼 | 讀取 spec.md 的驗收條件 checkbox，grep 產出檔案確認有相關實作 | 列出無對應的驗收條件，標記 ⚠️ |

#### 驗證結果分級

- **🔴 BLOCK**（E1, E2, E3）：必須解決後才能標記完成
- **⚠️ WARN**（E4, E5, E6）：記錄到 log.md，不阻擋但提醒使用者

#### 驗證報告格式

寫入 `.spec/{slug}/log.md` 並在回傳結果中顯示：

```
退出驗證結果：
  ✅ E1 所有 Teammate 完成
  ✅ E2 files.md 已產出（12 個檔案）
  ✅ E3 所有檔案存在
  ⚠️  E4 編譯未驗證（專案無標準 build 指令）
  ✅ E5 API 契約一致（4/4 端點吻合）
  ⚠️  E6 驗收條件 #3「支援匯出 Excel」無對應程式碼

  結論：可繼續，但建議處理 E6 後再進 plan-verify
```
```

#### 影響範圍

| 動作 | 檔案 |
|------|------|
| 修改 | `skills/plan-build/SKILL.md` — 在步驟 7 和 8 之間插入步驟 7.5 |

---

## Phase 2：品質左移（P1）

### 2.1 三層邊界系統

#### 概念

每個 Skill 明確聲明三類動作邊界：ALWAYS（自動執行）、ASK FIRST（需確認）、NEVER（禁止）。集中管理在 `references/boundaries.md`，各 SKILL.md 引用對應段落。

#### references/boundaries.md 結構

```markdown
# 動作邊界參考

## plan-build

### 🟢 ALWAYS（自動執行，不詢問）
- 讀取 .spec/{slug}/ 下所有設計文件
- 載入技術棧定義和掃描規則
- 掃描現有程式碼範本
- 產出 files.md
- 執行退出驗證門檻
- 在 log.md 記錄執行結果

### 🟡 ASK FIRST（顯示計畫，等使用者確認）
- 啟動 Agent Teams（步驟 4 的確認提示）
- Teammate 失敗時的處理策略（重試 / 跳過 / 終止）
- API 契約不一致時的調整方向
- 退出驗證中 WARN 項目的處理

### 🔴 NEVER（禁止，即使使用者要求也應警告）
- Leader 自己寫應用程式碼
- 跳過 arch.md 不存在的 hard block
- 自動產出 arch.md 來繞過 hard block
- 修改其他任務（非當前 slug）的 .spec/ 文件
- 跳過退出驗證中的 BLOCK 項目

---

## plan-review

### 🟢 ALWAYS
- 從 files.md 或 git diff 收集審查範圍
- 讀取 .spec/ 設計文件作為審查基準
- 產出 review.md
- 執行交叉審查合併步驟

### 🟡 ASK FIRST
- 3 人完整審查（預設）vs --quick 單人審查
- 發現 🔴 嚴重問題後的處理策略

### 🔴 NEVER
- 跳過合併步驟
- 自動降級嚴重度（🔴 → 🟡）
- Reviewer 之間互相呼叫

---

## plan-verify

### 🟢 ALWAYS
- 連接 Chrome 前確認模式（MCP / Bash / api-only）
- 每條驗收條件都記錄結果（PASS / FAIL / SKIP / MANUAL）
- 收集截圖到 .spec/{slug}/screenshots/
- 產出 verify.md

### 🟡 ASK FIRST
- 第一次連接 Chrome（確認目標分頁）
- --manual 模式的每步驟確認
- FAIL 項目是否需要立即修正

### 🔴 NEVER
- 跳過 FAIL 項目不記錄
- 自動將 FAIL 標記為 SKIP
- 未驗證回應 body 就標記 PASS

---

## plan-security

### 🟢 ALWAYS
- 執行 Layer 1 靜態規則掃描
- 掃描 MyBatis ${} 使用
- 掃描硬編碼密碼/Token
- 檢查 Controller 參數驗證

### 🟡 ASK FIRST
- 發現 🔴 嚴重漏洞時是否立即修復
- 外部依賴 CVE 掃描結果（可能有 false positive）
- 需要新增安全 middleware 或 filter

### 🔴 NEVER
- 忽略 SQL Injection 發現（「只是內部 API」）
- 降級安全問題嚴重度
- 跳過 Layer 1 靜態掃描
```

#### SKILL.md 引用方式

在每個 SKILL.md 的 `## 紀律護欄` 段落（Phase 1 新增）中追加：

```markdown
## 紀律護欄

> **反合理化**：執行前閱讀 `references/anti-rationalizations.md` 的「通用」和「{skill} 專用」段落。
> **動作邊界**：遵循 `references/boundaries.md` 的「{skill}」段落。🟢 自動做、🟡 先問、🔴 絕不。
```

#### 影響範圍

| 動作 | 檔案 |
|------|------|
| 新增 | `references/boundaries.md` |
| 修改 | `skills/plan-build/SKILL.md` — 引用段落 |
| 修改 | `skills/plan-review/SKILL.md` — 引用段落 |
| 修改 | `skills/plan-verify/SKILL.md` — 引用段落 |
| 修改 | `skills/plan-security/SKILL.md` — 新 Skill 內建引用 |

---

### 2.2 plan-security Skill（安全左移）

#### 定位

```
修改前的安全覆蓋：
  plan-spec → plan-db → plan-arch → plan-build → plan-review(Reviewer3=安全+效能) → plan-verify
                                                        ↑ 太晚，且職責混合

修改後：
  plan-spec → plan-db → plan-arch → plan-build → plan-security → plan-review(Reviewer3=效能) → plan-verify
                                                      ↑ 專職安全，build 後立即掃描
```

#### SKILL.md 規格

```markdown
---
name: plan-security
description: 專職安全掃描 — 三層掃描架構（靜態規則/上下文感知/對抗性思維），涵蓋 OWASP Top 10、SQL Injection、XSS、權限控制、敏感資料。當使用者提到「plan-security」、「安全掃描」、「安全檢查」、「security」時觸發此 Skill。
---

# plan-security — 安全掃描（零 Notion 呼叫）

對 plan-build 產出的程式碼執行三層安全掃描，產出 `.spec/{slug}/security.md` 安全報告。

---

## 前置條件

> **前置檢查**：參照 bug-workflow plugin 的 `references/prerequisites.md` 檢查 CLAUDE.md 是否存在。

- 建議已執行 `/plan-build` 產生程式碼
- 若無 plan-build 產出，可對任何已有程式碼執行

---

## 紀律護欄

> **反合理化**：執行前閱讀 `references/anti-rationalizations.md` 的「通用」和「plan-security 專用」段落。
> **動作邊界**：遵循 `references/boundaries.md` 的「plan-security」段落。

---

## 使用方式

```
/plan-security                # 完整三層掃描
/plan-security --quick        # 只執行 Layer 1 靜態掃描（Subagent）
/plan-security --fix          # 掃描 + 自動修復 🔴 問題
```

---

## 流程

### 1. 定位活躍任務

與 `/plan` 相同邏輯：從 Git branch 或 `_index.md` 匹配活躍任務。

### 2. 收集掃描範圍

1. 若 `.spec/{slug}/files.md` 存在 → 從中取得新增/修改檔案清單
2. 否則，從 Git diff 取得
3. 若都沒有 → 提示使用者指定檔案

### 3. 讀取上下文

- `.spec/{slug}/spec.md` — API 設計、業務規則
- `.spec/{slug}/db.md` — 表結構、敏感欄位
- `.spec/{slug}/arch.md` — 分層架構
- 專案 CLAUDE.md — 安全框架（ESAPI? Spring Security? 自訂 Filter?）

### 4. 確認執行計畫

```
即將執行安全掃描：

📁 掃描範圍：N 個檔案
🔍 掃描層級：
  • Layer 1 — 靜態規則掃描（grep + pattern matching）
  • Layer 2 — 上下文感知掃描（AI + 設計文件比對）
  • Layer 3 — 對抗性思維（三角色攻擊模擬）

確認開始？[Y/n]
```

### 5. Layer 1：靜態規則掃描（自動，無需 AI 判斷）

用 grep / find 掃描已知的危險模式：

| 規則 ID | 掃描目標 | 指令 | 嚴重度 |
|---------|---------|------|--------|
| L1-SQL-1 | MyBatis ${} 使用 | `grep -rn '\\$\\{' --include='*.xml' --include='*.java'` | 🔴 |
| L1-SQL-2 | 字串拼接 SQL | `grep -rn 'sql.*+=\|"SELECT.*"+\|"INSERT.*"+\|"UPDATE.*"+\|"DELETE.*"+'  --include='*.java'` | 🔴 |
| L1-XSS-1 | JSP 未轉義輸出 | `grep -rn '<%=' --include='*.jsp'` 後過濾非 JSTL 使用 | 🟡 |
| L1-XSS-2 | innerHTML / v-html | `grep -rn 'innerHTML\|v-html' --include='*.jsp' --include='*.vue' --include='*.js'` | 🟡 |
| L1-SEC-1 | 硬編碼密碼 | `grep -rn 'password\s*=\s*"\|secret\s*=\s*"\|token\s*=\s*"' --include='*.java' --include='*.properties' --include='*.yml'` | 🔴 |
| L1-SEC-2 | 缺少參數驗證 | 掃描 Controller 方法，檢查 @RequestParam/@RequestBody 是否有 @Valid/@Validated | 🟡 |
| L1-SEC-3 | CORS 配置 | `grep -rn 'Access-Control-Allow-Origin\|@CrossOrigin\|CorsConfiguration' --include='*.java'` | 🟡 |

每條匹配結果需 AI 判斷是否為 false positive（如 ${} 在註解中、password 是欄位名不是值等）。

### 6. Layer 2：上下文感知掃描（AI 判斷，需讀設計文件）

使用 **Agent tool** 啟動 subagent（model: opus）：

```
你是安全工程師，負責上下文感知的安全掃描。

## 設計文件
{spec.md 的 API 設計和業務規則}
{db.md 的表結構和敏感欄位}
{arch.md 的分層架構}

## 專案安全框架
{CLAUDE.md 中的安全相關段落}

## 程式碼
{Layer 1 掃描過的檔案內容}

## 檢查清單

### 權限控制
- 每個 API endpoint 是否有對應的權限檢查？
- 是否有水平越權風險（A 用戶存取 B 用戶的資料）？
- 批量操作 API 是否有 Rate Limiting？

### 敏感資料
- db.md 中標記的敏感欄位在 API response 中是否遮罩？
- Log 輸出是否包含敏感資料（身分證、手機、信用卡）？
- 錯誤訊息是否洩漏內部實作細節？

### 輸入驗證
- 所有外部輸入（API 參數、查詢條件）是否有型別和範圍驗證？
- 檔案上傳是否有類型和大小限制？
- 分頁參數是否有上限（防止一次撈全表）？

### 框架正確使用
- 專案的安全框架（ESAPI/Spring Security/自訂 Filter）是否在新程式碼中正確使用？
- 新增的 Controller 是否被安全 Filter 覆蓋？
- Session 管理是否正確？

標記嚴重程度：🔴 安全漏洞 / 🟡 安全風險 / 🟢 良好
輸出使用繁體中文。
```

### 7. Layer 3：對抗性思維（AI 扮演攻擊者）

使用 **Agent tool** 啟動 subagent（model: opus）：

```
你是滲透測試工程師，對以下程式碼進行三角色對抗分析。

## 程式碼
{Layer 1 和 Layer 2 掃描的檔案}

## 三個角色

### 壞蛋（Scoundrel）
思考：「我怎麼濫用這個系統？」
- 設定能否關閉安全機制？
- 參數能否注入繞過驗證？
- 能否透過 API 順序漏洞執行未授權操作？
- 能否利用批量 API 進行列舉攻擊？

### 懶惰開發者（Lazy Developer）
思考：「預設行為安全嗎？」
- 預設值是否安全？零值/空值行為是否安全？
- 未初始化的狀態是否有害？
- 如果中途失敗，半完成的狀態是否安全？
- 新功能如果未設定某個 config，行為是什麼？

### 搞混開發者（Confused Developer）
思考：「如果用錯了會怎樣？」
- 參數能否交換而無型別錯誤？
- 安全檢查失敗是否被靜默忽略？
- 錯誤路徑是否洩漏資訊？
- 是否有 TOCTOU（Time-of-Check to Time-of-Use）問題？

每個發現標記嚴重程度：🔴 可利用 / 🟡 潛在風險 / 🟢 安全
輸出使用繁體中文。
```

### 8. 彙整安全報告

合併三層掃描結果，去重後寫入 `.spec/{slug}/security.md`：

```markdown
# 安全掃描報告

## 摘要

| 項目 | 值 |
|------|-----|
| 掃描日期 | {YYYY-MM-DD} |
| 掃描範圍 | {N} 個檔案 |
| 模式 | {完整 / quick / fix} |

## 統計

| 層級 | 🔴 漏洞 | 🟡 風險 | 🟢 良好 |
|------|---------|---------|---------|
| Layer 1 靜態掃描 | {N} | {N} | {N} |
| Layer 2 上下文感知 | {N} | {N} | {N} |
| Layer 3 對抗性思維 | {N} | {N} | {N} |
| **合計** | **{N}** | **{N}** | **{N}** |

## 🔴 安全漏洞

### [{序號}] {漏洞標題}
- **檔案**：{路徑}:{行號}
- **層級**：Layer {1/2/3}
- **規則**：{規則 ID，如 L1-SQL-1}
- **描述**：{問題描述}
- **影響**：{攻擊場景}
- **修復建議**：{具體修復方式，含程式碼範例}
{若 --fix 模式：- **已修復**：✅ / ❌}

## 🟡 安全風險
（同上格式）

## 🟢 安全良好實踐
（正面反饋）
```

### 9. --fix 模式

掃描完成後，對所有 🔴 漏洞嘗試自動修復：

| 漏洞類型 | 自動修復策略 |
|---------|------------|
| MyBatis ${} | 替換為 #{} + 若為 ORDER BY 則加 allowlist |
| 硬編碼密碼 | 移至 .properties + 加 @Value 注入 |
| 缺少參數驗證 | 加 @Valid + 建立對應 DTO validation |
| innerHTML | 替換為 textContent 或使用 DOMPurify |

修復後重新執行 Layer 1 確認問題消除。

### 10. 更新 .spec/

1. 更新 `README.md`：`status: 安全掃描`
2. 在 `log.md` 追加紀錄

### 11. 回傳結果

```
安全掃描完成！

📋 報告：.spec/{slug}/security.md
📊 統計：🔴 {N} 漏洞 / 🟡 {N} 風險 / 🟢 {N} 良好

{若有 🔴 漏洞}
⚠️  發現 {N} 個安全漏洞，強烈建議修復後再進 plan-review。
  • /plan-security --fix — 自動修復 🔴 問題

{若無 🔴 漏洞}
🎉 無嚴重安全漏洞！

後續可使用：
  • /plan-review  — Agent Teams 程式碼審查
  • /plan-verify  — 驗收驗證
  • /plan-close   — 結案並同步 Notion
```

---

## Gotchas

- **Layer 1 的 grep pattern 需要持續維護**：新的危險模式（如新版 framework 的 API 變化）需要手動加入。考慮未來在 references/ 維護一份 security-patterns.md 供擴充。
- **Layer 2 和 Layer 3 分開 subagent 避免角色混淆**：合併成一個 subagent 時，「安全工程師」和「滲透測試員」的視角會互相干擾。保持分離。
- **--fix 的自動修復有限**：只處理機械性可修復的問題。涉及架構調整的問題（如缺少權限框架）只能建議，不能自動修。
- **與 plan-review Reviewer 3 的分工**：plan-security 執行後，plan-review 的 Reviewer 3 **不再負責安全**，改為專職效能審查。需同步修改 plan-review 的 SKILL.md。
```

#### plan-review 的連動修改

Reviewer 3 從「安全性與效能」改為「效能審查」：

**原名稱**：Security & Performance Reviewer
**新名稱**：Performance Reviewer

**移除的職責**（移至 plan-security）：
- SQL Injection 掃描
- XSS 掃描
- 權限控制檢查
- 敏感資料洩漏
- CSRF 防護
- 三角色對抗性檢查

**保留的職責**：
- N+1 查詢偵測
- 缺少分頁
- 缺少索引
- 迴圈內 DB 呼叫
- 大量資料未串流
- 快取策略建議
- 連線池配置

**新增的職責**：
- 查詢執行計畫分析（若 DB MCP 可用）
- 效能指標預估（回應時間、吞吐量）

#### plugin.json 修改

新增 skill 路徑：

```json
{
  "skills": [
    "./skills/plan-setup",
    "./skills/plan-stack",
    "./skills/plan-start",
    "./skills/plan-explore",
    "./skills/plan-browse",
    "./skills/plan",
    "./skills/plan-spec",
    "./skills/plan-db",
    "./skills/plan-arch",
    "./skills/plan-build",
    "./skills/plan-security",
    "./skills/plan-verify",
    "./skills/plan-review",
    "./skills/plan-close",
    "./skills/plan-sync",
    "./skills/plan-status"
  ]
}
```

#### 影響範圍

| 動作 | 檔案 |
|------|------|
| 新增 | `skills/plan-security/SKILL.md` |
| 修改 | `skills/plan-review/SKILL.md` — Reviewer 3 改為 Performance Reviewer |
| 修改 | `.claude-plugin/plugin.json` — 新增 plan-security 路徑 |

---

### 2.3 plan-verify 改造（gstack browse 驅動）

#### 工具重新定位

```
修改前：
  plan-verify 用 chrome-devtools-mcp 或 cdp.mjs 做一切（QA + 除錯 + console）
  → 定位模糊，chrome-devtools 的強項（除錯）被浪費在 QA 上

修改後：
  plan-verify 用 gstack browse ($B) 做 QA 驗收
  → @e ref 交互、snapshot diff、health score、持久 session
  chrome-devtools-mcp 保留給除錯場景
  → console log 串流、network 攔截、performance trace、memory snapshot
```

#### 為什麼換 gstack browse

| 能力 | chrome-devtools-mcp | gstack browse ($B) | 勝者 |
|------|--------------------|--------------------|------|
| 元素定位 | CSS selector（需猜測） | @e ref（snapshot 自動編號） | gstack |
| 前後比對 | 無 | `snapshot -D`（unified diff） | gstack |
| 品質量化 | 無 | Health Score（0-100，8 維加權） | gstack |
| 指令速度 | ~500ms（MCP round trip） | ~100ms（compiled binary） | gstack |
| Session 持久 | 需每次連接 | Cookie/state 持久跨指令 | gstack |
| Console log | 即時串流 ✓ | `$B console --errors` | chrome-devtools |
| Network 攔截 | 完整 CDP 存取 ✓ | 無 | chrome-devtools |
| Performance trace | 完整 profiling ✓ | `$B perf`（基本） | chrome-devtools |
| Memory snapshot | heap snapshot ✓ | 無 | chrome-devtools |
| Lighthouse | 內建 ✓ | 無 | chrome-devtools |

**結論**：QA 驗收用 gstack，除錯/效能分析用 chrome-devtools。

#### 登入/認證策略

現有 plan-verify 的核心價值是「使用已登入的 Chrome session」。gstack 的對應方案：

| 場景 | gstack 解法 |
|------|-----------|
| 已登入的 Chrome | `$B connect` 連接使用者的 Chrome（headed CDP 模式） |
| Cookie 檔案 | `$B cookie-import cookies.json` |
| 需要手動登入 | `$B goto <login-url>` + `$B snapshot -i` + `$B fill @e3 "user"` + `$B click @e5` |
| SSO/VPN 內部系統 | 先 `$B connect` 到已登入的 Chrome，或用 `/setup-browser-cookies` 匯入 |
| 2FA/CAPTCHA | 提示使用者在 headed browser 中完成，然後繼續 |

CDP 模式偵測（gstack 自動判斷是否已連接真實 Chrome）：

```bash
$B status 2>/dev/null | grep -q "Mode: cdp" && echo "CDP_MODE=true" || echo "CDP_MODE=false"
```

若 CDP_MODE=true：跳過 cookie import（真實 Chrome 已有 cookie）。

#### plan-verify SKILL.md 重寫規格

##### 前置檢查（取代現有的 MCP/Bash 雙模式偵測）

```markdown
### 前置檢查

#### 1. gstack browse binary

```bash
B=""
_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
[ -n "$_ROOT" ] && [ -x "$_ROOT/.claude/skills/gstack/browse/dist/browse" ] && B="$_ROOT/.claude/skills/gstack/browse/dist/browse"
[ -z "$B" ] && B="$HOME/.claude/skills/gstack/browse/dist/browse"
if [ -x "$B" ]; then
  echo "BROWSE_READY: $B"
else
  echo "BROWSE_NEEDS_SETUP"
fi
```

- BROWSE_READY → 繼續
- BROWSE_NEEDS_SETUP → 提示安裝 gstack（`cd ~/.claude/skills/gstack && ./setup`）

#### 2. Chrome 連接狀態

```bash
$B status 2>/dev/null
```

偵測結果：
- `Mode: cdp` → 已連接真實 Chrome（有登入態），跳過認證步驟
- `Mode: headless` → 獨立 headless Chromium，可能需要認證
- 連接失敗 → 啟動新的 headless instance

#### 3. chrome-devtools-mcp（選配，用於除錯增強）

```bash
claude mcp list 2>/dev/null | grep -q "chrome-devtools" && echo "DEVTOOLS_AVAILABLE=true" || echo "DEVTOOLS_AVAILABLE=false"
```

若可用 → 在 console error 偵測和 network 分析時使用，作為 gstack 的補充。
```

##### 核心驗證流程（借鏡 gstack qa）

```markdown
### 5. 逐條驗證

#### 5.1 頁面探索（Orient）

```bash
$B goto <target-url>
$B snapshot -i -a
$B console --errors
```

AI 分析 snapshot 的 @e ref，識別可互動的元素。

#### 5.2 API 驗證

```bash
# 取得登入 cookie（CDP 模式下已有，headless 需取得）
$B cookie <domain>

# 呼叫 API
curl -s "<api-url>" -H "Cookie: <cookie>" | head -100
```

驗證清單：
- HTTP 狀態碼
- 回應 body 結構（不只看 200，要檢查內容）
- 資料筆數是否符合預期
- 欄位完整性（對照 spec.md 定義）
- 錯誤回應格式

#### 5.3 UI 驗證

```bash
# 步驟 1：操作前快照
$B snapshot -i

# 步驟 2：操作元素（用 @e ref，不用 CSS selector）
$B click @e5
$B fill @e3 "測試資料"
$B select @e7 "選項值"

# 步驟 3：操作後快照 + diff
$B snapshot -D

# 步驟 4：截圖存證
$B screenshot .spec/{slug}/screenshots/verify-{N}-{desc}.png

# 步驟 5：console error 檢查
$B console --errors
```

**snapshot -D 的關鍵作用**：顯示操作前後的 DOM 差異，格式如：

```
  @e1 [button] "送出"         → @e1 [button] "送出" [disabled]
- @e2 [div] "載入中..."
+ @e2 [div] "查詢完成，共 15 筆"
+ @e3 [table] 15 rows
```

AI 根據 diff 判斷操作是否成功，比純截圖分析更準確。

#### 5.4 表單驗證

```bash
$B forms                    # 列出頁面所有表單和欄位
$B fill @e3 "正常值"
$B click @e10               # 送出
$B snapshot -D              # 確認送出成功

# 邊界測試
$B goto <form-url>          # 重新載入
$B fill @e3 ""              # 空值
$B click @e10
$B snapshot -D              # 確認有驗證錯誤訊息

$B goto <form-url>
$B fill @e3 "<script>alert(1)</script>"  # XSS 測試
$B click @e10
$B snapshot -D              # 確認有轉義
```

#### 5.5 回應式檢查（若有前端）

```bash
$B responsive .spec/{slug}/screenshots/verify-{N}-responsive.png
# 產出 3 張截圖：desktop / tablet / mobile
```
```

##### Health Score（借鏡 gstack qa 的評分系統）

```markdown
### 6. 計算 Health Score

根據驗證結果計算品質分數，借用 gstack qa 的加權評分系統：

#### 評分維度

| 類別 | 權重 | 計算方式 |
|------|------|---------|
| API 正確性 | 25% | 每個 FAIL 的 API 驗收條件 -25（critical）或 -15（high） |
| UI 功能 | 20% | 每個 FAIL 的 UI 驗收條件 -25（critical）或 -15（high） |
| Console | 15% | 0 error = 100，1-3 = 70，4-10 = 40，10+ = 10 |
| 表單驗證 | 15% | 每個缺少驗證的表單欄位 -8 |
| 資料一致性 | 15% | API 回應與 UI 顯示不一致 -15 per 項 |
| 回應式 | 10% | 行動裝置嚴重破版 -25，輕微 -8 |

#### 分數等級

| 分數 | 等級 | 建議 |
|------|------|------|
| 90-100 | 優秀 | 可直接進 plan-close |
| 70-89 | 良好 | 建議處理 FAIL 項目 |
| 50-69 | 需改善 | 應修復後重新 verify |
| < 50 | 不通過 | 必須修復 |
```

##### Baseline / Regression 機制

```markdown
### 7. Baseline 管理

#### 首次驗證

寫入 `.spec/{slug}/baseline.json`：

```json
{
  "date": "2026-04-24",
  "healthScore": 85,
  "results": [
    { "id": 1, "condition": "可依日期範圍查詢", "status": "PASS" },
    { "id": 2, "condition": "支援匯出 Excel", "status": "FAIL", "reason": "按鈕不存在" }
  ],
  "categoryScores": {
    "api": 100,
    "ui": 75,
    "console": 85,
    "form": 90,
    "consistency": 80,
    "responsive": 90
  }
}
```

#### --recheck 模式

讀取 baseline.json，只重跑 FAIL 項目，合併結果：

```bash
# 自動比對
Health Score：75 → 92（+17）
修復項目：#2 支援匯出 Excel（FAIL → PASS）
新增問題：無
```
```

##### verify.md 報告格式（改版）

```markdown
### 8. 產出 verify.md（改版）

```markdown
# 驗證報告

## 摘要

| 項目 | 值 |
|------|-----|
| 驗證日期 | {YYYY-MM-DD} |
| 環境 | {URL} |
| 驗證工具 | gstack browse ($B){，chrome-devtools-mcp（console 增強）} |
| Chrome 模式 | {CDP（已登入）/ Headless} |
| Health Score | **{N}/100**（{等級}）|

## Health Score 細項

| 類別 | 分數 | 權重 | 加權 |
|------|------|------|------|
| API 正確性 | {N} | 25% | {N} |
| UI 功能 | {N} | 20% | {N} |
| Console | {N} | 15% | {N} |
| 表單驗證 | {N} | 15% | {N} |
| 資料一致性 | {N} | 15% | {N} |
| 回應式 | {N} | 10% | {N} |
| **合計** | | | **{N}** |

## 統計

| 狀態 | 數量 |
|------|------|
| ✅ PASS | {N} |
| ❌ FAIL | {N} |
| ⏭️ SKIP | {N} |
| 👤 MANUAL | {N} |

## 驗證結果

### [1] ✅ 可依日期範圍查詢
- **類型**：API
- **驗證**：`GET /api/xxx?startDate=2026-01-01&endDate=2026-03-16` → HTTP 200, 15 筆
- **snapshot diff**：
  ```
  + @e3 [table] 15 rows
  + @e4 [pagination] "1 / 2 頁"
  ```
- **截圖**：screenshots/verify-1-query-result.png

### [2] ❌ 支援匯出 Excel
- **類型**：UI
- **驗證**：`$B snapshot -i` → 搜尋「匯出」相關元素
- **snapshot**：頁面中無匯出按鈕（@e ref 清單中無 "export" / "匯出" 相關元素）
- **截圖**：screenshots/verify-2-export.png

{若有 regression baseline}
## Regression 比對

| 指標 | 上次 | 本次 | 差異 |
|------|------|------|------|
| Health Score | {N} | {N} | {+/-N} |
| PASS | {N} | {N} | {+/-N} |
| FAIL | {N} | {N} | {+/-N} |

### 修復的問題
- #2 支援匯出 Excel（FAIL → PASS）

### 新增的問題
- （無）

### 未解決的問題
- （無）
```
```

##### chrome-devtools-mcp 的輔助角色

```markdown
### chrome-devtools-mcp 在 plan-verify 中的使用

chrome-devtools-mcp 不再是主要工具，但在以下場景作為 gstack 的補充：

| 場景 | gstack 能力 | chrome-devtools 增強 |
|------|-----------|-------------------|
| Console error 偵測 | `$B console --errors`（基本） | `list_console_messages`（含 warning + info） |
| Network 請求分析 | 無 | `list_network_requests` + `get_network_request`（查看 request/response detail） |
| 非同步等待 | 無原生支援 | `wait_for`（等待特定文字出現） |
| Performance 效能 | `$B perf`（基本指標） | `performance_start_trace` + `performance_stop_trace`（完整 profiling） |

#### 使用條件

- `DEVTOOLS_AVAILABLE = true`（前置檢查中偵測）
- 使用者執行 `/plan-verify --deep`（深度模式）時啟用
- 或驗收條件明確涉及效能指標時自動啟用

#### --deep 模式

```
/plan-verify --deep    # 完整驗證 + chrome-devtools 增強
```

在標準 gstack 驗證完成後，額外執行：
1. 全頁面 console message 掃描（含 warning）
2. Network 請求分析（失敗的請求、慢請求 > 3s）
3. Performance trace（若有效能相關驗收條件）

結果追加到 verify.md 的獨立段落。
```

##### plan-verify 反合理化表（更新）

在 `references/anti-rationalizations.md` 的 plan-verify 段落更新：

```markdown
## plan-verify 專用

| # | AI 的內心獨白 | 為什麼不行 |
|---|-------------|-----------|
| V1 | 「API 回傳 200 就算 PASS」 | HTTP 200 只代表沒有伺服器錯誤。用 curl 檢查回應 body 的格式、筆數、欄位完整性。 |
| V2 | 「snapshot 太長了，我只看前幾行」 | 用 `$B snapshot -D` 看 diff 而不是全文。diff 會高亮變化，不需要掃描整個 snapshot。 |
| V3 | 「這條驗收條件需要登入，太複雜了，標 SKIP」 | 用 `$B connect` 連接已登入的 Chrome，或 `$B cookie-import` 匯入 cookie。gstack 支援 CDP 模式，不需要重新登入。 |
| V4 | 「gstack browse 沒裝，改用 curl 手動測就好」 | curl 只能測 API，無法測 UI 互動、表單驗證、回應式。plan-verify 的核心價值是端到端驗證。 |
| V5 | 「Health Score 太低但功能有跑起來，算 PASS 吧」 | Health Score 是客觀指標。低分代表使用者體驗有問題。記錄實際分數，讓使用者決定是否接受。 |
```

#### 影響範圍

| 動作 | 檔案 |
|------|------|
| 重寫 | `skills/plan-verify/SKILL.md` — 全面改為 gstack browse 驅動 |
| 新增 | `references/verify-gstack.md` — gstack browse 指令參考 |
| 刪除 | `references/verify-mcp.md` 和 `references/verify-bash.md`（Phase 3 原規劃取消，改為 verify-gstack.md） |
| 修改 | `references/anti-rationalizations.md` — 更新 plan-verify 段落 |

---

## Phase 3：智慧化與重構（P2）

### 3.1 脈絡工程策略

#### 概念

改善 plan-build 中 Leader 傳遞給 Teammate 的脈絡品質。從「全文塞入」改為「分層擷取、角色定制」。

#### references/build-context-layers.md

```markdown
# Delegate 脈絡分層策略

## Layer 0：共用核心脈絡（所有 Teammate 都收到）

Leader 從 CLAUDE.md 和技術棧定義中擷取，格式化為 5 行以內的摘要：

```
專案技術棧：{技術棧 ID}（{framework} + {orm} + {db}）
命名慣例：package prefix = {prefix}，欄位 = camelCase，表 = snake_case
scaffold：{scaffold 行為一句話}
禁止事項：{若有，如「禁止 Executors.newFixedThreadPool」}
Git branch：{branch}，任務：{name}
```

Token 預算：~200 tokens

## Layer 1：角色脈絡（按 Teammate 角色分配）

按 Teammate 角色，從 .spec/ 文件中擷取**該角色需要的段落**（不是全文）：

| Teammate | 從 spec.md 擷取 | 從 db.md 擷取 | 從 arch.md 擷取 |
|----------|----------------|---------------|----------------|
| 後端工程師 | 業務邏輯規則 | 全部表結構 | 類別清單 + 介面定義 |
| API 工程師 | API 端點設計 + 錯誤處理 | — | Controller 方法清單 |
| 前端工程師 | 畫面需求 + 操作流程 | — | — |
| 測試工程師 | 驗收條件 | 約束清單（NOT NULL、UNIQUE） | 介面定義 |
| DB 工程師 | — | 全文 | — |

Token 預算：~500-1000 tokens per teammate

## Layer 2：範本脈絡（Leader 預篩選後嵌入）

**不再只給路徑，Leader 要預篩選並嵌入關鍵片段。**

步驟：
1. 用 Glob 找到同層級的候選範本（如 3 個 Service 檔案）
2. 讀取每個候選，選出**最簡單、最標準的那個**
   - 排除：有特殊 annotation、非標準命名、過長、有大量 TODO
   - 優先：短小、清晰、典型
3. 擷取關鍵片段：
   - class 宣告（含 annotation）
   - 1 個代表性方法
   - import 區塊的前 5 行
4. 附帶學習重點指引

格式範例：

```
## 風格參考（已預篩選）

來源：src/main/java/com/xxx/service/impl/UserServiceImpl.java

```java
package com.xxx.service.impl;

import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Autowired;
// ...

@Service
public class UserServiceImpl implements UserService {
    @Autowired
    private UserMapper userMapper;

    @Override
    public ApiResult<UserDTO> findById(Long id) {
        User user = userMapper.selectByPrimaryKey(id);
        if (user == null) {
            return ApiResult.fail("使用者不存在");
        }
        return ApiResult.success(BeanUtils.toDTO(user));
    }
}
```

學習重點：
- Service 分 Interface + Impl
- 注入用 @Autowired field injection
- 回傳用 ApiResult<T> 包裝
- 錯誤用 ApiResult.fail()
- 轉換用 BeanUtils.toDTO()
```

Token 預算：~300-500 tokens per teammate

## Layer 3：交叉引用脈絡（跨角色需知道的約束）

Leader 從設計文件中提取跨角色約束，在**相關** Teammate 的 prompt 末尾附上：

| 約束來源 | 傳遞給 | 格式 |
|---------|--------|------|
| db.md NOT NULL 欄位 | 後端、API、前端 | 「以下欄位不可為 null：user_name, phone, created_at」 |
| db.md UNIQUE 約束 | API、後端 | 「以下欄位有唯一約束：email, id_number」 |
| spec.md API 必填參數 | 前端 | 「以下 API 參數為必填：startDate, endDate, userId」 |
| db.md 外鍵關聯 | 後端 | 「orders.user_id → users.id（CASCADE DELETE）」 |
| spec.md 分頁限制 | 後端、API | 「pageSize 上限 100，預設 20」 |

Token 預算：~100-200 tokens per teammate
```

#### plan-build 步驟 5 修改

現有步驟 5 標題「讀取專案上下文（給 Teammates 的共用上下文）」改為「準備分層脈絡」，內容替換為引用 `references/build-context-layers.md` 的四層策略。

#### 影響範圍

| 動作 | 檔案 |
|------|------|
| 新增 | `references/build-context-layers.md` |
| 修改 | `skills/plan-build/SKILL.md` — 步驟 5 重寫 + 步驟 6 的 prompt 模板調整 |

---

### 3.2 漸進式揭露重構

#### 概念

將 SKILL.md 中佔篇幅但只在特定步驟使用的內容抽到 references/，SKILL.md 只保留流程骨架，細節按需讀取。

#### 3.2.1 plan-build Prompt 模板抽離

**現狀**：步驟 6 的 Teammate prompt 模板佔 plan-build SKILL.md 約 180 行（50%）。

**改造**：抽到 `references/build-prompts.md`。

```markdown
# Teammate Prompt 模板

## Subagent 模式（僅後端）

```
你是後端程式碼產生器。
...（現有 Subagent prompt 全文）
```

## Agent Teams 模式

### 成員 0：DB 工程師（條件載入：DB_MCP_AVAILABLE = true）
...（現有 DB 工程師 prompt 全文）

### 成員 1：後端工程師
...（現有後端工程師 prompt 全文）

### 成員 2：API 工程師
...（現有 API 工程師 prompt 全文）

### 成員 3：前端工程師（條件載入：FRONTEND_REQUIRED = true）
...（現有前端工程師 prompt 全文）

### 成員 4：測試工程師
...（現有測試工程師 prompt 全文）

### 任務依賴關係
...（現有依賴關係描述）
```

plan-build SKILL.md 步驟 6 改為：

```markdown
### 6. 啟動 Agent Teams

讀取 `references/build-prompts.md` 取得 Teammate prompt 模板。

根據步驟 3 的團隊組成判斷，選擇對應的模板（Subagent / Agent Teams），
將步驟 5 準備的分層脈絡嵌入各 Teammate 的 prompt 中。

> 模板中的 `{placeholder}` 需替換為實際值。見 build-prompts.md 的變數說明。
```

#### 3.2.2 plan-verify 指令參考抽離

**現狀**：Phase 2 已將 plan-verify 改為 gstack browse 驅動，不再有 MCP/Bash 雙模式。

**改造**：gstack browse 的指令細節抽到 `references/verify-gstack.md`，SKILL.md 只保留流程骨架和判斷邏輯。

```markdown
# references/verify-gstack.md

## gstack browse 指令參考

### 導航
| 動作 | 指令 | 說明 |
|------|------|------|
| 前往頁面 | `$B goto <url>` | 載入頁面並等待 |
| 返回 | `$B back` | 瀏覽器上一頁 |
| 重新載入 | `$B reload` | 重新載入當前頁面 |
| 取得 URL | `$B url` | 取得當前頁面 URL |

### 探索
| 動作 | 指令 | 說明 |
|------|------|------|
| 快照 | `$B snapshot -i` | 互動式快照，元素帶 @e ref 編號 |
| 快照 diff | `$B snapshot -D` | 與上次快照的 unified diff |
| 截圖 | `$B screenshot <path>` | 存成 PNG |
| 回應式截圖 | `$B responsive <path>` | 3 張：desktop / tablet / mobile |
| 連結 | `$B links` | 列出頁面所有連結 |
| 表單 | `$B forms` | 列出頁面所有表單和欄位 |
| Console | `$B console --errors` | 取得 JS error |

### 互動
| 動作 | 指令 | 說明 |
|------|------|------|
| 點擊 | `$B click @eN` | 點擊第 N 個元素 |
| 填入 | `$B fill @eN "value"` | 填入文字 |
| 選擇 | `$B select @eN "option"` | 下拉選單選擇 |
| 按鍵 | `$B press Enter` | 鍵盤按鍵 |
| 捲動 | `$B scroll down` | 頁面捲動 |

### Session
| 動作 | 指令 | 說明 |
|------|------|------|
| 狀態 | `$B status` | 查看 browser 狀態（headless/cdp） |
| 連接 Chrome | `$B connect` | 連接使用者已開啟的 Chrome |
| Cookie | `$B cookie <domain>` | 取得指定 domain 的 cookie |
| Cookie 匯入 | `$B cookie-import <file>` | 匯入 cookie 檔案 |
```

#### 3.2.3 Token 載入對比

| Skill | 改造前（行數） | 改造後（行數） | 節省 |
|-------|-------------|-------------|------|
| plan-build | ~365 | ~200 | ~45% |
| plan-verify | ~438 | ~250（gstack 統一模式） | ~43% |
| plan-review | ~264 | ~240（微調）| ~9% |

新增 references 檔案不計入 SKILL.md，因為是按需載入，不佔初始脈絡。

#### 影響範圍

| 動作 | 檔案 |
|------|------|
| 新增 | `references/build-prompts.md` |
| 新增 | `references/verify-gstack.md`（取代原規劃的 verify-mcp.md + verify-bash.md） |
| 修改 | `skills/plan-build/SKILL.md` — 步驟 6 精簡為引用 |

---

### 3.3 智慧團隊組成

#### 概念

plan-build 的團隊組成不再只看 FRONTEND_REQUIRED 和 DB_MCP_AVAILABLE，還要根據任務類型（feature / adjustment / bugfix / refactor / performance）和變更範圍動態調整。

#### 3.3.1 擴充 spec.md 的「判斷」區塊

plan-spec 產出的 spec.md 末尾，原有的判斷區塊擴充為：

```markdown
## 判斷

### 任務屬性
- TASK_TYPE: feature / adjustment / bugfix / refactor / performance
- CHANGE_SCOPE: full / backend-only / frontend-only / api-only / db-only

### 技術需求
- FRONTEND_REQUIRED: true/false
- FRONTEND_TECH: JSP/Vue/React/無
- DB_REQUIRED: true/false
- DB_TABLES: [表清單]
- NEW_API: true/false
- EXISTING_API_CHANGE: true/false
```

新增欄位說明：

| 欄位 | 說明 | 取值 |
|------|------|------|
| TASK_TYPE | 任務類型 | feature（新功能）/ adjustment（功能調整）/ bugfix（修復）/ refactor（重構）/ performance（效能優化） |
| CHANGE_SCOPE | 變更範圍 | full（全棧）/ backend-only / frontend-only / api-only / db-only |
| NEW_API | 是否有新 API | true = 新增 endpoint，false = 只改既有 |
| EXISTING_API_CHANGE | 是否修改既有 API | true = 改參數/回應/邏輯，false = 不動 |

#### 3.3.2 references/team-composition.md

```markdown
# 團隊組成判斷規則

## 判斷流程

### Step 1：讀取判斷區塊

從 spec.md 的「判斷」區塊取得 TASK_TYPE 和 CHANGE_SCOPE。
若判斷區塊不存在或缺少新欄位 → 回退到 v4.9.0 的邏輯（只看 FRONTEND_REQUIRED × DB_MCP）。

### Step 2：按 TASK_TYPE 分流

#### feature（新功能）
走完整判斷流程（Step 3）。

#### adjustment（功能調整）
按 CHANGE_SCOPE 決定：

| CHANGE_SCOPE | 團隊配置 | 模式 |
|-------------|---------|------|
| backend-only | 後端工程師 | Subagent |
| frontend-only | 前端工程師 | Subagent |
| api-only | 後端 + API 工程師 | 2 人 Team 或 2 個 Subagent |
| db-only | DB 工程師（需 DB MCP）| Subagent |
| full | 走 Step 3 完整判斷 | Agent Teams |

#### bugfix（修復）
預設：後端工程師（Subagent）
例外：若 CHANGE_SCOPE = full → 走 Step 3

#### refactor（重構）
預設：後端工程師（Subagent）
例外：若跨多層級 → 後端 + 測試（2 人 Team）

#### performance（效能優化）
預設：
- 若 DB_MCP_AVAILABLE → DB 工程師 + 後端（2 人 Team）
- 若無 DB MCP → 後端工程師（Subagent）

### Step 3：完整判斷（feature 或 CHANGE_SCOPE = full）

沿用 v4.9.0 邏輯，增加 NEW_API 判斷：

| FRONTEND | DB_MCP | NEW_API | 團隊組成 |
|----------|--------|---------|---------|
| true | true | true | 5 人（DB + 後端 + API + 前端 + 測試）|
| true | true | false | 4 人（DB + 後端 + 前端 + 測試）|
| true | false | true | 4 人（後端 + API + 前端 + 測試）|
| true | false | false | 3 人（後端 + 前端 + 測試）|
| false | true | true | 4 人（DB + 後端 + API + 測試）|
| false | true | false | 3 人（DB + 後端 + 測試）|
| false | false | true | 3 人（後端 + API + 測試）|
| false | false | false | 後端 + 測試（2 人 Team 或 Subagent）|

### Step 4：確認計畫

顯示判斷依據，讓使用者確認或覆寫：

```
📊 Teammate 配置：後端工程師（Subagent 模式）

判斷依據：
  - TASK_TYPE = bugfix → 預設 Subagent
  - CHANGE_SCOPE = backend-only
  - FRONTEND_REQUIRED = false
  - NEW_API = false

需要調整嗎？（如需完整 Agent Teams，輸入配置）[Y/n]
```

## Bug-workflow 相容

bugfix 任務可能從 bug-workflow（/bug-start）進入，此時有 fix.md 而非 spec.md。

判斷區塊讀取優先順序：
1. `.spec/{slug}/spec.md` 的「判斷」區塊
2. `.spec/{slug}/fix.md` — 從修復方案推斷（TASK_TYPE 固定為 bugfix，CHANGE_SCOPE 從修復範圍推斷）
3. 都沒有 → 詢問使用者
```

#### 3.3.3 plan-spec prompt 修改

plan-spec 的 subagent prompt 需加入新欄位的產出指示：

```
在文件最後附加判斷區塊：
---
## 判斷

### 任務屬性
- TASK_TYPE: {根據需求分析判斷：feature/adjustment/bugfix/refactor/performance}
- CHANGE_SCOPE: {根據影響範圍判斷：full/backend-only/frontend-only/api-only/db-only}

### 技術需求
- FRONTEND_REQUIRED: true/false
- FRONTEND_TECH: JSP/Vue/React/無
- DB_REQUIRED: true/false
- DB_TABLES: [表清單]
- NEW_API: true/false
- EXISTING_API_CHANGE: true/false
```

#### 影響範圍

| 動作 | 檔案 |
|------|------|
| 新增 | `references/team-composition.md` |
| 修改 | `skills/plan-build/SKILL.md` — 步驟 3 改為引用 team-composition.md |
| 修改 | `skills/plan-spec/SKILL.md` — subagent prompt 擴充判斷區塊欄位 |

---

### 3.4 技術棧陷阱

#### 概念

在 `stacks/_builtin.md` 和自訂 `stacks/{id}.md` 中新增「技術棧陷阱」段落，記錄該技術棧下 Teammate 最容易犯的錯誤。

#### _builtin.md 結構擴充

在現有表格後，每個技術棧新增獨立的陷阱區塊：

```markdown
# 內建技術棧

| 技術棧 ID | 框架 | ORM | DB | scaffold 行為 |
|-----------|------|-----|-----|--------------|
（現有表格不變）

---

## spring-mvc-mybatis 陷阱

| 陷阱 | 正確做法 | 原因 |
|------|---------|------|
| Controller 用 @RestController | 用 @Controller + @ResponseBody（或每個方法標 @ResponseBody） | Spring MVC 4.x 部分版本的 @RestController 行為不一致 |
| JSP 用 <% scriptlet %> | 用 JSTL <c:out> + EL expression | 可維護性、XSS 防護（scriptlet 不經過轉義） |
| MyBatis XML 用 ${} 拼接查詢條件 | 用 #{} 參數綁定 | SQL Injection 風險。ORDER BY 場景用 allowlist 驗證後拼接 |
| Service 不分 Interface / Impl | 必須分 Interface + Impl | AOP 代理需要介面；且為專案慣例 |
| 用 @Autowired 在 constructor | 用 field injection（@Autowired 在欄位上） | 專案慣例，雖非 Spring 官方推薦但全專案一致 |
| XML Mapper 的 namespace 用短名 | 用完整 package path | tk.mybatis 的 Mapper 掃描依賴完整 namespace |

---

## spring-boot-mybatis 陷阱

| 陷阱 | 正確做法 | 原因 |
|------|---------|------|
| 直接用 @Select 寫複雜 SQL | 複雜 SQL 放 Mapper XML | @Select 難以維護多行 SQL、動態條件 |
| tk.mybatis 的 Example 過度使用 | 簡單查詢用 Example，複雜查詢寫 XML | Example 不支援 JOIN、子查詢 |
| application.yml 放敏感資訊 | 用 environment variable 或 Jasypt 加密 | 專案配置會進 Git |

---

## spring-boot-jpa 陷阱

| 陷阱 | 正確做法 | 原因 |
|------|---------|------|
| Entity 用 @Data | 用 @Getter @Setter（不含 equals/hashCode） | @Data 的 equals/hashCode 包含所有欄位，與 JPA lazy loading proxy 衝突 |
| Repository 方法名過長 | 超過 3 個條件用 @Query | findByStatusAndTypeAndCreatedAtBetweenAndUserIdOrderByCreatedAtDesc 不可讀 |
| 忘記 @Transactional | Service 的寫入方法必須標 @Transactional | JPA 預設不開 transaction，可能導致 lazy loading exception |
| FetchType.EAGER | 預設 FetchType.LAZY | EAGER 導致 N+1 查詢，所有關聯都被載入 |

---

## spring-boot-mybatis-plus 陷阱

| 陷阱 | 正確做法 | 原因 |
|------|---------|------|
| 用 BaseMapper 的 selectList(null) 撈全表 | 必須帶條件或分頁 | 全表掃描在資料量大時會 OOM |
| IService 的 saveOrUpdate 直接用 | 先確認 ID 策略（自增 / UUID / 雪花） | saveOrUpdate 依賴 ID 判斷新增或更新，ID 策略不對會導致每次都 INSERT |
| LambdaQueryWrapper 鏈式過長 | 超過 5 個條件考慮抽 helper method | 可讀性下降 |
```

#### 自訂 stacks/{id}.md 的範本更新

在 `references/config.template.md` 的自訂技術棧模板中新增：

```markdown
## ⚠️ 技術棧陷阱

| 陷阱 | 正確做法 | 原因 |
|------|---------|------|
| {陷阱 1} | {正確做法} | {原因} |
| {陷阱 2} | {正確做法} | {原因} |
```

#### plan-build 的整合

步驟 5（準備分層脈絡）的 Layer 0 從技術棧定義中擷取時，同時擷取「技術棧陷阱」表格，嵌入每個 Teammate 的 prompt 中：

```
## 技術棧陷阱（此技術棧常見錯誤，務必避免）
| 陷阱 | 正確做法 |
|------|---------|
（從 stacks/ 擷取的精簡版，只保留與該 Teammate 角色相關的條目）
```

不同 Teammate 收到不同的陷阱子集：
- 後端工程師：Service、Entity、Mapper 相關陷阱
- API 工程師：Controller、DTO 相關陷阱
- 前端工程師：JSP / Vue 相關陷阱
- 測試工程師：全部陷阱（測試需涵蓋這些邊界）

#### 影響範圍

| 動作 | 檔案 |
|------|------|
| 修改 | `references/config.template.md` — 自訂技術棧模板加入「技術棧陷阱」段落 |
| 說明 | stacks/_builtin.md 和 stacks/{id}.md 由使用者的 config 目錄管理，非 plugin 原始碼。此處定義格式規範，實際內容由 /plan-stack 或手動填寫。 |

> **注意**：stacks/ 目錄不在 plugin 原始碼中，而是在使用者的 `~/.claude-company/feature-workflow/stacks/` 下。plugin 只定義格式範本（config.template.md），實際內容在使用者環境。_builtin.md 的初始內容由 /plan-setup 產生。

---

## 完整影響檔案清單

### 新增檔案

| 檔案 | Phase | 說明 |
|------|-------|------|
| `references/anti-rationalizations.md` | Phase 1 | 反合理化表集中管理 |
| `references/boundaries.md` | Phase 2 | 三層邊界定義 |
| `skills/plan-security/SKILL.md` | Phase 2 | 安全掃描 Skill |
| `references/verify-gstack.md` | Phase 2 | gstack browse 指令參考 |
| `references/build-context-layers.md` | Phase 3 | 脈絡分層策略 |
| `references/build-prompts.md` | Phase 3 | Teammate prompt 模板 |
| `references/team-composition.md` | Phase 3 | 團隊組成判斷規則 |

### 修改檔案

| 檔案 | Phase | 修改內容 |
|------|-------|---------|
| `skills/plan-build/SKILL.md` | Phase 1-3 | 紀律護欄引用 + 步驟 7.5 退出驗證 + 步驟 3 引用 team-composition + 步驟 5 重寫脈絡策略 + 步驟 6 精簡為引用 build-prompts |
| `skills/plan-review/SKILL.md` | Phase 1-2 | 紀律護欄引用 + Reviewer 3 改為 Performance Reviewer |
| `skills/plan-verify/SKILL.md` | Phase 1-2 | 紀律護欄引用 + 全面改為 gstack browse 驅動 + Health Score + Baseline |
| `skills/plan-spec/SKILL.md` | Phase 3 | subagent prompt 擴充判斷區塊（TASK_TYPE、CHANGE_SCOPE、NEW_API、EXISTING_API_CHANGE） |
| `.claude-plugin/plugin.json` | Phase 2 | skills 陣列新增 plan-security |
| `references/config.template.md` | Phase 3 | 自訂技術棧模板加入「技術棧陷阱」段落 |

### 不修改（但有關聯）

| 檔案 | 說明 |
|------|------|
| `references/plan-common.md` | 不修改，但新 Skill（plan-security）會引用其共用邏輯 |
| `references/config-resolver.md` | 不修改，技術棧陷阱的載入遵循現有第 3 層邏輯 |
| `skills/plan-close/SKILL.md` | 不修改，但 security.md 會在 plan-close 時同步到 Notion |
| 使用者環境 `stacks/_builtin.md` | 非 plugin 原始碼，但格式需遵循新範本（含「技術棧陷阱」段落）|

---

## 驗收條件

### Phase 1（P0）

- [ ] `references/anti-rationalizations.md` 存在，含通用 + plan-build + plan-review + plan-verify 四個段落
- [ ] plan-build、plan-review、plan-verify 的 SKILL.md 都有「紀律護欄」引用段落
- [ ] plan-build SKILL.md 含步驟 7.5 退出驗證，有 6 項檢查（E1-E6）和 BLOCK/WARN 分級
- [ ] 執行 /plan-build 時，完成前會顯示退出驗證結果

### Phase 2（P1）

- [ ] `references/boundaries.md` 存在，含 plan-build、plan-review、plan-verify、plan-security 四個段落
- [ ] 各 SKILL.md 的「紀律護欄」段落含邊界引用
- [ ] `skills/plan-security/SKILL.md` 存在，含三層掃描架構（靜態/上下文/對抗）
- [ ] plan-security 在 plugin.json 的 skills 陣列中
- [ ] plan-review 的 Reviewer 3 改為 Performance Reviewer（移除安全職責）
- [ ] 反合理化表含 plan-security 專用段落
- [ ] plan-verify SKILL.md 改為 gstack browse ($B) 驅動
- [ ] plan-verify 前置檢查偵測 gstack browse binary 和 Chrome 連接狀態
- [ ] plan-verify 產出含 Health Score（0-100，6 維加權）
- [ ] plan-verify 支援 baseline.json 和 --recheck regression 比對
- [ ] plan-verify 的 snapshot diff（$B snapshot -D）取代純截圖分析
- [ ] plan-verify --deep 模式整合 chrome-devtools-mcp 做 console/network/performance 增強
- [ ] `references/verify-gstack.md` 存在，含 gstack browse 指令參考表
- [ ] 反合理化表的 plan-verify 段落更新（V4、V5 新增）

### Phase 3（P2）

- [ ] `references/build-context-layers.md` 存在，定義 Layer 0-3 策略
- [ ] `references/build-prompts.md` 存在，含所有 Teammate prompt 模板
- [ ] `references/team-composition.md` 存在，含按 TASK_TYPE 分流的判斷邏輯
- [ ] plan-build SKILL.md 行數 ≤ 220 行（精簡後）
- [ ] plan-verify SKILL.md 行數 ≤ 250 行（精簡後）
- [ ] plan-spec 的 subagent prompt 產出包含 TASK_TYPE、CHANGE_SCOPE、NEW_API、EXISTING_API_CHANGE
- [ ] `references/config.template.md` 的自訂技術棧模板含「技術棧陷阱」段落
- [ ] _builtin.md 的格式規範含四個內建技術棧的陷阱表格

---

## 判斷

### 任務屬性
- TASK_TYPE: feature
- CHANGE_SCOPE: full

### 技術需求
- FRONTEND_REQUIRED: false
- FRONTEND_TECH: 無
- DB_REQUIRED: false
- DB_TABLES: []
- NEW_API: false
- EXISTING_API_CHANGE: false
