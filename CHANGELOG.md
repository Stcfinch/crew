# CREW Changelog

所有 CREW plugins（bug-workflow、feature-workflow）的變更紀錄。

格式：每個版本一個區塊，以 `## [plugin@version]` 開頭。
`/crew-upgrade` 會讀取此檔案，顯示上次更新以來的變更摘要。

---

## [bug-workflow@3.5.0] - 2026-04-25

### 新增
- **bug-investigate Skill** — 假說驅動的根因調查，五階段流程（證據收集 → 模式比對 → 假說驗證 → 根因確認 → 調查報告），含 3-Strike 升級規則、知識庫搜尋、本地學習搜尋
- **bug-fix Skill** — 修復紀律（鐵律：根因確認才能修）、修復建議、迴歸測試產出、gstack browse UI 驗證
- **Bug 模式表** — 7 種已知 bug 模式（NPE、SQL 異常、第三方 API、併發、設定、快取、前端 UI）
- **反合理化表** — 通用 3 條 + investigate 6 條 + fix 4 條 + close 3 條，防止 AI 偷工減料
- **三層邊界系統** — 每個 skill 的 ALWAYS / ASK FIRST / NEVER 行為定義
- **學習系統** — 跨 session 學習捕捉（JSONL 格式），bug-investigate 時自動搜尋歷史洞察

### 改善
- **bug-close** 新增退出驗證門檻（根因分析 + commit + 迴歸測試 + 驗證勾選）
- **bug-close** 新增學習捕捉步驟（自動判斷是否有可複用的洞察）
- **bug-start** 新增初始證據自動收集（最近 commit + 環境 + 知識庫 + 學習歷史）

## [feature-workflow@4.11.0] - 2026-04-25

### 新增
- **Word 驗收報告** — 驗證完成後可產出正式 Word 驗收報告（封面 + 簽核欄位 + 測試環境 + 驗收明細 + 待處理事項 + 附錄），使用 `/minimax-docx` 產出
- **人話操作敘述** — 驗證時同步記錄人話操作步驟（Playwright 操作 → 人話翻譯），寫入 verify.md 的 `<!-- human_steps -->` 註解
- **封面資訊快取** — `report-config.md` 跨專案快取承辦單位與製作人，首次詢問後自動存檔

### 改善
- **移除 PDF 報告選項** — 簡化為只產 Word（Y/n 詢問），需要 PDF 可從 Word 轉存
- **Playwright 改為預設驗證工具** — chrome-devtools 改為 `--deep` 模式除錯輔助
- **向下相容** — 舊版 verify.md 無 `human_steps` 時自動進入降級模式

## [feature-workflow@4.10.0] - 2026-04-25

### 新增
- **plan-security Skill** — 三層安全掃描（靜態規則 / 上下文感知 / 對抗性思維），含 OWASP Top 10、SQL Injection、XSS 掃描，支援 --quick 和 --fix 模式
- **反合理化表** — 通用 3 條 + plan-build 8 條 + plan-review 3 條 + plan-verify 5 條 + plan-security 4 條
- **三層邊界系統** — plan-build / plan-review / plan-verify / plan-security 的行為邊界定義
- **脈絡工程策略** — 四層脈絡分配（共用核心 / 角色定制 / 範本預篩選 / 交叉引用），改善 Agent Teams delegate 品質
- **智慧團隊組成** — 根據 TASK_TYPE（feature / adjustment / bugfix / refactor / performance）和 CHANGE_SCOPE 動態調整團隊規模
- **技術棧陷阱** — stacks/ 範本新增「陷阱」段落，記錄各技術棧常見錯誤

### 改善
- **plan-build** 新增退出驗證門檻（6 項檢查：Teammate 完成 + files.md + 檔案存在 + 編譯 + API 契約 + 驗收條件）
- **plan-build** 步驟重構，精簡 37%（prompt 模板和判斷邏輯抽到 references/）
- **plan-review** Reviewer 3 從「安全性與效能」拆分為純「效能審查」（安全移至 plan-security）
- **plan-spec** 判斷區塊擴充（新增 TASK_TYPE、CHANGE_SCOPE、NEW_API、EXISTING_API_CHANGE）
