---
name: plan-security
description: 專職安全掃描 — 三層掃描架構（靜態規則/上下文感知/對抗性思維），涵蓋 OWASP Top 10、SQL Injection、XSS、權限控制、敏感資料。當使用者提到「plan-security」、「安全掃描」、「安全檢查」、「security」時觸發此 Skill。
---

# plan-security — 安全掃描（零 Notion 呼叫）

對 plan-build 產出的程式碼執行三層安全掃描，產出 `.spec/{slug}/security.md` 安全報告。

---

## 前置條件

> **前置檢查**：參照 `references/prerequisites.md` 檢查 CLAUDE.md 是否存在。

- 建議已執行 `/plan-build` 產生程式碼
- 若無 plan-build 產出，可對任何已有程式碼執行

---

## 紀律護欄

> **執行前必讀**：`references/discipline-preamble.md`（通用紀律 — 反合理化、動作邊界、鐵律）。
> 本 skill 專用條目：`anti-rationalizations.md` 「plan-security 專用」+ `boundaries.md` 「plan-security」段落。
> 在感到「可以跳過」「應該夠了」的衝動時，**停下查表**確認是否為已知偏離模式。

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

---

## 邊界情況

- **無程式碼可掃描**：提示先執行 `/plan-build` 或 commit 程式碼
- **Layer 1 結果全是 false positive**：仍需執行 Layer 2 和 Layer 3，不能因 Layer 1 雜訊而跳過
- **--quick 模式**：只執行 Layer 1 靜態掃描，適合快速檢查
- **--fix 修復失敗**：記錄失敗原因到 security.md，標記 ❌，不中斷流程
- **專案無安全框架**：Layer 2 的「框架正確使用」檢查項自動跳過，但在報告中標記 🟡 建議導入安全框架
