# CREW Changelog

所有 CREW plugins（bug-workflow、feature-workflow）的變更紀錄。

格式：每個版本一個區塊，以 `## [plugin@version]` 開頭。
`/crew-upgrade` 會讀取此檔案，顯示上次更新以來的變更摘要。

---

## [feature-workflow@4.16.0] - 2026-05-15

### 新增
- **截圖穩定化策略** — 從 SmartRobotE2ETest 萃取的 6 步穩定化流程（ESC×2 + networkidle + retry），所有專案受益
- **元素定位 Fallback** — 6 級定位策略（記憶 → 穩定 selector → 產品知識 → i18n 翻譯 → CSS → URL 導航）
- **WARN 狀態** — verify.md 新增 ⚠️ WARN 狀態（介於 PASS 和 FAIL 之間，環境差異/selector 不穩定）
- **Excel 驗收報告** — `--excel` 選項，ExcelJS 獨立腳本產出 .xlsx（總表 + 步驟 Sheet + 嵌入截圖）
- **i18n 驗證指引** — 支援 zh-TW/zh-CN/en-US/ja-JP 四語系，產品模式用翻譯文字定位、通用模式用穩定 selector
- **產品知識庫** — 新增 `products/` 目錄，SmartRobot 知識庫含頁面導航地圖、Selector、i18n 對照、特殊操作 Recipe
- **驗證記憶系統** — 三層架構（產品級→專案級→任務級），自動記錄 + 結案升級，驗證越做越快
- **E2E Runner 模式** — `--e2e` 選項，匹配現有 E2E 測試直接跑（需 e2e_repo 設定）
- **測試骨架產出** — 驗證完成後可選產出 80% 完成度的 E2E 測試骨架
- **plan-common 第 4 層** — 產品知識庫偵測邏輯，projects/{id}.md 新增 product_id 選填欄位

## [bug-workflow@3.8.0] - 2026-05-15

### 新增
- **investigate 為主入口** — 流程從「start → investigate」改為「investigate（自動建立條目 + 調查）」，bug-start 降為可選的手動入口
- **釐清問題機制** — 調查完成後，若根因涉及商業邏輯疑問或環境差異，條件觸發 1-3 個釐清問題請使用者回答
- **動態建議指令** — 調查回傳結果根據根因確認狀態（已確認/需更多資訊/未確認）動態建議後續指令

### 改善
- **README 流程圖** — 以 bug-investigate 為主入口，bug-start 改為虛線可選路徑
- **根目錄 README** — 同步更新 Phase 2 摘要流程、詳細流程圖、指令表
- **feature-workflow 交叉引用** — plan SKILL.md 和 team-composition.md 的 bug 流程描述同步更新
- **marketplace.json 版本同步** — 修正 bug-workflow 和根目錄 marketplace.json 的落後版本號，補齊遺漏的 skills 清單

## [bug-workflow@3.7.0] - 2026-05-06

### 新增
- **自動關聯來源 Feature** — bug-start 建立 Bug 後，自動從同專案 Feature 中比對標題，設定「相關任務」self-relation（Step 6.7）
- **偵測來源 Feature Branch** — 從關聯 Feature 取得開發分支作為 Bug 修復分支，支援 Git-flow 規範（Step 6.8）
- **bug-fix 分支檢查** — 修復前檢查是否在正確分支，不一致時提示切換（Step 1.5）
- **bug-fix merge 引導** — 修復完成後提示 merge 回 DEV 分支
- **bug-close merge 引導** — 結案前偵測 feature branch，引導 `merge --no-ff` 回 DEV 分支（Step 1.5）
- **bug-setup self-relation** — 首次設定時自動建立「相關任務」self-relation 欄位

### 改善
- **config.template** 欄位對照新增「相關任務」Relation (self) 說明
- **db-templates** 第二輪 Relation 新增步驟 6（self-relation）+ 任務追蹤工具 Schema 說明

## [feature-workflow@4.15.0] - 2026-05-06

### 新增
- **plan-start Notion relation** — Bug 類型本地關聯 Feature 成功後，同步建立 Notion「相關任務」relation
- **plan-start 盲搜 fallback** — 本地 .spec/ 無匹配 Feature 時，走 Notion 層標題比對（同 bug-start Step 6.7）
- **plan-start Feature Branch 偵測** — 關聯 Feature 後偵測開發分支作為修復分支
- **dev_branch 設定** — projects/ frontmatter 新增 dev_branch 欄位，供 bug-close merge 引導使用

## [feature-workflow@4.14.0] - 2026-05-04

### 新增
- **DB_REQUIRED=insert-only 支援** — plan-build 退出驗證（E7）自動從設計文件擷取 SQL，產出 deploy.sql（含執行順序、驗證 SQL、回滾 SQL）
- **deploy.sql 標準格式** — Step 註解、驗證 SQL、回滾 SQL 三段式結構，上線時不會遺漏
- **deploy.sql Notion 同步** — plan-sync / plan-close 自動將 deploy.sql 寫入「🗄️ 資料庫設計 → 部署 SQL」子區塊

### 改善
- **team-composition.md** 新增 Step 3.5 DB_REQUIRED 三值判斷（true / insert-only / false）
- **E7 分級** — DB_REQUIRED=true 時為 BLOCK，insert-only 時為 WARN

## [feature-workflow@4.13.0] - 2026-05-04

### 新增
- **plan-start 退出驗證（S1~S7）** — 建立 Notion 條目後，強制用 notion-fetch 讀回頁面驗證 7 項必填欄位（專案資料庫、修復分支、開發階段等），防止 auto mode 下遺漏欄位

### 改善
- **S1 條件式降級** — Notion API 不可用時 S1 降為 WARN，不阻擋 offline-first 流程
- **S3 刻意 friction** — 修復分支未建立時，即使 auto mode 也強制二次確認
- **驗證失敗自動修復** — Agent 自行補呼叫 notion-update-page，不要求使用者手動操作
- **步驟 6 重構為兩步法** — 頁面建立拆分為 Step A（properties）+ Step B（body），配合退出驗證降級邏輯

## [bug-workflow@3.5.1] - 2026-04-25

### 修正
- **crew-upgrade Skill 未被安裝** — plugin.json 在 3.5.0 版本的 cache 中缺少 crew-upgrade 條目，升版觸發重新安裝

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

## [bug-workflow@3.6.0] - 2026-04-25

### 新增
- **notion-local 後端支援** — 新增 `references/notion-backend.md` 工具映射表，CREW 自動偵測 Notion Plugin 或 notion-local 並選擇對應工具，既有使用者不受影響
- **Notion 後端偵測邏輯** — `prerequisites.md` 新增第 0.5 項，所有需要 Notion 的 Skill 首次呼叫時自動偵測可用後端（優先 Notion Plugin）

### 改善
- **適用範圍表格重構** — 改為矩陣式，清楚標示每個 Skill 需要哪些前置檢查項目

## [feature-workflow@4.12.0] - 2026-04-25

### 新增
- **notion-local 後端支援** — 共享 bug-workflow 的 Notion 後端偵測與映射機制，所有 Notion 操作自動適配

## [bug-workflow@3.5.2] - 2026-04-25

### 改善
- **Node.js / Git 前置檢查** — setup 時自動偵測 Node.js 和 Git，未安裝時依作業系統顯示對應安裝指令（macOS / Windows / Linux）
- **Windows 完整支援** — prerequisites.md 新增 OS 偵測邏輯，所有安裝引導提供 Windows 對應指令
- **README 新增 Node.js 前置條件** — 明確標示 Node.js ≥ 18 為必要依賴，附各平台安裝方式

## [feature-workflow@4.11.2] - 2026-04-25

### 改善
- **README 新增前置條件段落** — 明確列出 Node.js、Notion Plugin、Agent Teams 三項必要依賴
- **Windows 完整支援** — README 加入 Windows 使用者引導連結

## [feature-workflow@4.11.1] - 2026-04-25

### 改善
- **API 測試紀錄（Evidence）** — Word 驗收報告新增「測試紀錄」段落，包含完整 API 請求指令與回應內容，證明測試確實執行
- **回應截斷顯示** — 回應超過 20 行時，報告顯示前 10 行 + 後 10 行 + 省略提示，完整回應另存 `evidence/` 目錄
- **後台頁面截圖** — 驗證計畫新增「截圖」欄，API 有對應後台頁面時自動截圖存證（AI 從 arch.md 推斷，使用者可覆寫）
- **敏感資訊遮蔽** — Word 報告中的 Cookie / Token 自動遮蔽（前 4 + **** + 後 4），evidence 原始檔保留完整值

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
