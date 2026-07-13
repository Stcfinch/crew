# 審查發現收尾對照報告（reconciliation）

> 對照對象：審查報告 181 條已驗證發現 vs. 四梯次修改後現況

> 基準 commit：`226d7f1`；已提交梯次 1-3（`318bbc9`/`d4528c3`/`36bcda1`）＋工作區未提交梯次 4（26 檔）

> 判定依據：現行檔案實測（grep/ls/read），非以 diff 為準


## 總表：維度 × 狀態

| 維度 | resolved | partial | unresolved | 小計 |
|---|---|---|---|---|
| reference | 44 | 1 | 27 | 72 |
| structure | 15 | 12 | 29 | 56 |
| token | 2 | 8 | 14 | 24 |
| trigger | 27 | 1 | 1 | 29 |
| **總計** | **88** | **22** | **71** | **181** |

## 總表：嚴重度 × 狀態

| 嚴重度 | resolved | partial | unresolved |
|---|---|---|---|
| 高 | 25 | 0 | 0 |
| 中 | 38 | 9 | 39 |
| 低 | 25 | 13 | 32 |

**關鍵結論：全部 25 條「高」嚴重度發現皆已 resolved。**未解決/部分集中在中·低嚴重度的結構一致性與 token 下放。

## 已解決的系統性修法（88 條 resolved 的依據）

- **觸發詞收斂（27/29 trigger 條）**：所有 skill description 改為「當使用者輸入 /xxx，或提到「具體片語」時觸發」，移除單字級觸發詞。
- **references 路徑（25 條 reference/路徑）**：統一改為「plugin 根目錄 `references/xxx.md`（相對 SKILL.md 為 `../../references/`）」明示寫法（未用 ${CLAUDE_PLUGIN_ROOT}，但已消除解析歧義）。
- **「何時不用」段落**：29 個 skill 全數新增。
- **boundaries.md / anti-rationalizations.md**：補齊 plan-demo/plan-deploy-confirm/plan-next/crew-init 等專用段落。
- **事實錯誤（高嚴重度）**：npm 套件改 @playwright/mcp、crew-upgrade/.claude 路徑加 fallback、plan-close gitignore 改 git add -f、部署狀態區塊/README status 回流鏈打通、plan-security grep 改 -F '${'、plan-verify 改 browser_* 工具名、移除死引用 /bug-search。
- **步驟編號**：bug-start(1-10)、plan-build(1-10)、plan-status/plan-sync 交叉引用改具名。

## unresolved 逐條清單（71 條）

| # | skill | 維度/嚴重度 | issue（摘要） | 狀態原因 |
|---|---|---|---|---|
| 2 | bug-close | reference/中 | notion-search/notion-update-page 未用完整 Server:tool 名；環境有 noti | 其他——notion 工具仍用短名，未標完整 Server:tool 或 NOTION_BACKEND 映射 |
| 3 | bug-close | reference/中 | 學習寫入路徑硬編碼 ~/.claude-company/，但設定檔（14-16 行）支援 ~/.claude/ 個人環境 | 其他——學習寫入路徑仍硬編 ~/.claude-company/（219/248 行），未比照 dev_branch 加 ~/.claude/ 雙路徑 fallback |
| 5 | bug-close | token/中 | Step 1.5 Merge 引導約 50 行（53-104），且與 Gotchas（288-291）、邊界情況（304 | 低優先未排程——bug-close Merge 引導未下放 references/merge-guide.md（仍 inline） |
| 6 | bug-close | structure/低 | Gotchas 與邊界情況兩段內容重疊（283 vs 301 的 replace_content、290 vs 304  | 低優先未排程——bug-close Gotchas 與邊界情況 replace_content/merge 仍重疊 |
| 7 | bug-close | structure/低 | C3 檢查「grep test 目錄中含 Regression: {bug 相關關鍵字}」無具體指令，關鍵字定義模糊 | 低優先未排程——bug-close C3 檢查『grep Regression:{關鍵字}』仍無具體指令 |
| 12 | bug-fix | structure/中 | 編譯檢查只偵測 pom.xml/build.gradle（Java），非 Java 專案（Node/前端）無對應指令，流 | 其他——編譯檢查仍只偵測 pom.xml/build.gradle，非 Java 專案無 fallback |
| 13 | bug-fix | token/低 | Gotchas 段 3 條與正文重複（最小 diff 行130/263、update_content 行208/267、 | 低優先未排程——bug-fix Gotchas 最小 diff 等與正文仍重複 |
| 15 | bug-fix | token/低 | 範例硬寫具體專案分支名（MOM01P2401_DEV、feature/qa-log-user-id-statistics | 其他——bug-fix 仍硬寫具體分支名 MOM01P2401_DEV / feature/qa-log-user-id-statistics，未改佔位符 |
| 17 | bug-investigate | reference/中 | 要求用 rtk proxy 指令且稱「遵循 CLAUDE.md 規範」（:92-93、:398），但 rtk 不存在，全 | 其他——bug-investigate 仍要求 rtk proxy 並稱『遵循 CLAUDE.md 規範』，但本環境無 rtk |
| 20 | bug-investigate | reference/低 | 內文硬寫 notion-search/notion-fetch/notion-update-page（:63/70/12 | 其他——bug-investigate 內文用短名，開頭未註明依 NOTION_BACKEND 參照 notion-backend.md |
| 23 | bug-setup | structure/中 | 專案資料庫 Title 欄位在內文表寫「專案名稱」，db-templates.md:49 寫「Name」，兩處 sche | C9類（結構未排程）——bug-setup 內文 Title 欄仍寫『專案名稱』，與 db-templates『Name』及本檔 161 行『Name』矛盾 |
| 24 | bug-setup | token/中 | 步驟 2-3 的 15 列欄位表與 db-templates.md「A. 專案資料庫」Schema 重複，且已出現漂移（ | 低優先未排程——步驟 2-3 15 列欄位表與 db-templates.md 重複且漂移 |
| 27 | bug-start | token/中 | 6.7 自動關聯 Feature 與 6.8 偵測 Feature Branch 兩節共 130 行細節流程佔全檔 40 | 低優先未排程——bug-start 自動關聯/偵測分支兩節(~130行)未下放 references（已改名式交叉引用但未搬移） |
| 30 | bug-start | structure/低 | skill 接受位置引數（/bug-start <問題簡述> [環境] [優先順序]，見 L31、L77-80）但 fr | 低優先未排程——bug-start frontmatter 仍無 argument-hint |
| 33 | bug-update | reference/中 | examples/update-patterns.md（120 行）在 SKILL.md 乃至整個 plugin 零引用 | 低優先未排程——bug-update examples/update-patterns.md 仍存在且零引用 |
| 34 | bug-update | reference/中 | notion-search/notion-fetch/notion-update-page 共 8 處用短名（原報告誤計 | 其他——bug-update 仍用短名（8 處），headless 環境會失效 |
| 39 | crew-doctor | reference/中 | 宣稱 anti-rationalizations.md 與 boundaries.md 有「crew-doctor 專用 | 其他——crew-doctor SKILL 仍引用 anti-rationalizations/boundaries「crew-doctor 專用」段，但兩檔實際無此段（梯次2 補了多數 skill 段落卻漏 crew-doctor） |
| 41 | crew-doctor | structure/中 | 進階檢查前置條件自相矛盾：61 行寫「紅燈全綠時才跑」，95 行寫「僅當 #3 通過時」跑 | 結構未排程——crew-doctor 進階檢查前置：61 行『紅燈全綠才跑』vs 94 行『僅 #3 通過』仍矛盾 |
| 43 | crew-doctor | structure/低 | 「退出碼」段落定義 0/1/2，但 skill 無任何腳本，LLM 驅動流程沒有退出碼可回傳 | 低優先未排程——crew-doctor 「退出碼」段（line 142）仍在，LLM skill 無腳本無退出碼 |
| 46 | crew-init | reference/中 | 階段 2a 只檢查兩個階層式 config 路徑，漏掉 plan-setup 明列的舊單一檔格式（feature-wor | 結構未排程——crew-init 階段 2a 未偵測舊單一檔 config 格式（feature-workflow-config.md） |
| 47 | crew-init | structure/中 | 前置檢查表只列 3 項，內文卻寫「只跑必要 5 項」，且 crew-doctor 定義必要項為 8 項，三處數字互相矛盾 | 結構未排程——crew-init 前置表列 3 項但內文寫『必要 5 項』，仍不一致 |
| 55 | crew-upgrade | structure/中 | 步驟 2 目錄不存在時只 echo「嘗試 git fetch...」，實際未給任何 fetch 或替代指令，隨後仍對缺失 | 結構未排程——crew-upgrade 目錄不存在僅 echo『嘗試 git fetch』無實際指令，隨後仍 grep 死路徑 |
| 60 | plan-arch | structure/中 | 步驟 2 宣稱「prompt 指示如下」但僅給輸入/輸出來源；arch.md 規格只有 :37 一行括號列 4 元素，無 | 結構未排程——plan-arch 仍無 arch.md 章節契約與 subagent 自檢清單 |
| 63 | plan-browse | token/中 | 六個模式各附完整 ASCII 輸出範本，約 180 行佔全文六成，觸發即載入昂貴 | 低優先未排程——plan-browse 六模式 ASCII 範本未下放 references/examples.md（仍 295 行） |
| 64 | plan-browse | token/中 | 模式 1 要求讀取每個任務的 README 與所有設計文件才產總覽，任務多時 token 成本高 | 低優先未排程——plan-browse 模式 1 仍讀每任務全部文件，未優化為只讀 frontmatter |
| 65 | plan-browse | token/低 | box-drawing 框線混排全形中文，模型難精確對齊，重現成本高且易產出破版 | 低優先未排程——plan-browse 仍用 box-drawing 框線混排全形中文 |
| 66 | plan-browse | reference/低 | 文字說「在 .md 檔案中搜尋」但指令含 --include="*.sql"，敘述與指令不符 | 低優先未排程——plan-browse 指令含 --include=*.sql 但註解仍只寫『.md 檔案』 |
| 67 | plan-browse | reference/低 | 深度閱讀範本只列 README/spec/db/arch/log 五檔，遺漏其他 skill 實際產出的 verify. | 低優先未排程——plan-browse 深度閱讀範本仍漏 verify.md/review.md/deploy.sql |
| 68 | plan-browse | structure/低 | 銜接表寫 /plan-spec「會進入編輯迴圈」，但 plan-spec 內實名為「規格確認迴圈」（plan-spec/ | 低優先未排程——plan-browse 銜接表仍寫『編輯迴圈』，plan-spec 實名『規格確認迴圈』 |
| 75 | plan-build | token/低 | 7.3b 設定檔模式表（13 列）與 E7 deploy.sql 模板（行 257-279）為執行期細節，佔本體約 45 | 低優先未排程——plan-build 7.3b 設定檔表/E7 模板未下放 references |
| 76 | plan-build | structure/低 | 「回退到 v4.9.0 邏輯」為時效性版本指涉（plugin.json 現版 4.23.0），版本號會隨演進腐化 | 低優先未排程——plan-build 仍寫『回退到 v4.9.0 邏輯』時效性版本指涉 |
| 80 | plan-close | reference/中 | notion-fetch 等工具名僅對應 plugin 後端；prerequisites.md:106 指向的映射表 r | 其他——plan-close 經 prerequisites.md 指向 feature-workflow/references/notion-backend.md，該檔實測不存在（bug-workflow 有、feature-workflow 缺） |
| 83 | plan-close | structure/低 | 開頭宣稱「僅 3-5 次 Notion API 呼叫」，與行 279 Gotcha 承認實際可達 7 次自相矛盾 | 結構未排程——plan-close 第 8 行仍寫『僅 3-5 次』，與 279/304 行『實際可達 7 次』矛盾 |
| 86 | plan-db | structure/低 | opus subagent 為 fresh context，但 prompt 指示未要求傳入步驟 1 讀到的設計準則（r | 結構未排程——plan-db subagent prompt 未要求附上步驟1技術棧/DB規範，db.md 無段落契約 |
| 87 | plan-db | structure/低 | 「README.md」三處未寫全路徑，可能被解讀為專案根 README 而非 .spec/{slug}/README.m | 低優先未排程——plan-db README.md 三處未寫全路徑 .spec/{slug}/README.md |
| 88 | plan-db | reference/低 | 引用鏈兩層深：SKILL.md → plan-common.md → config-resolver.md，違反參考檔一 | 低優先未排程——plan-db 引用鏈兩層深（SKILL→plan-common→config-resolver）未攤平 |
| 90 | plan-demo | structure/中 | --keep 說明「預設清理會在 demo 結束時清除」與 §4「預設不自動清理」直接矛盾 | 結構未排程——plan-demo --keep 括號說明『預設清理會清除』與 §4『預設不自動清理』仍矛盾 |
| 91 | plan-demo | reference/中 | 宣稱 /plan-status 會標示 [DEMO] 並排末尾、分組顯示（L202 同），但 plan-status S | 其他——plan-demo 仍宣稱 /plan-status 會標 [DEMO] 並分組，但 plan-status SKILL 無任何 demo 邏輯（grep 0） |
| 93 | plan-demo | reference/中 | 引導指令 ls plugins/feature-workflow/skills/ 只在 marketplace repo | 結構未排程——plan-demo 引導仍用 ls plugins/feature-workflow/skills/（僅 marketplace repo 有效） |
| 95 | plan-demo | reference/低 | 引用 references/demo-spec-template.md 並自承「如未來新增該檔」，find 實測不存在， | 低優先未排程——plan-demo 仍寫『references/demo-spec-template.md（如未來新增）』前瞻死引用 |
| 100 | plan-deploy-confirm | reference/中 | Gotcha 建議「用 /plan-sync 重新同步補上區塊」，但 plan-sync 無建立「🚀 部署狀態」區塊的邏 | 其他——plan-deploy-confirm Gotcha 仍建議用 /plan-sync 補區塊，但 plan-sync 明文不建立該區塊（修法改由 plan-close，Gotcha 未同步） |
| 103 | plan-deploy-confirm | reference/低 | `notion-search` 未用完整 MCP Server:tool 名，環境同時有 notion-local（AP | 其他——plan-deploy-confirm notion-search 短名有歧義（兩套後端） |
| 112 | plan-next | reference/中 | 推薦重跑「/plan-start --resume」，但 plan-start SKILL.md 不支援 --resum | 其他——plan-next 仍推薦 /plan-start --resume，但 plan-start 不支援 --resume 旗標 |
| 115 | plan-next | structure/低 | skill 支援 <slug> 與 --all 引數，但 frontmatter 缺 argument-hint，使用者 | 低優先未排程——plan-next frontmatter 仍無 argument-hint |
| 116 | plan-review | structure/中 | 報告模板 Reviewer 欄枚舉為 {logic/quality/security}，與實際三軸（logic/qual | 結構未排程——plan-review 報告模板 Reviewer 仍列 {logic/quality/security}，應為 performance |
| 117 | plan-review | structure/中 | prod_branch 回退邏輯兩處不一致：行 57 直接嘗試 production→master→main，行 257 | 結構未排程——plan-review prod_branch 回退：55 行無 origin/HEAD、266 行有，仍不一致 |
| 119 | plan-review | structure/中 | 環境變數只寫「同 plan-build」未給變數名；行 264 說「顯示設定指引」但本文無指引，單獨觸發時不自足，且未提 | 結構未排程——plan-review 環境變數段只寫『同 plan-build』，未寫變數名與靜默失敗警告 |
| 121 | plan-review | token/低 | 66 行 Agent Team 派工 prompt 全文內嵌本文（行 91–157），佔本體約 1/4，觸發即載入 | 低優先未排程——plan-review 66 行派工 prompt 未下放 references/review-prompts.md |
| 125 | plan-security | reference/低 | Gotcha「需同步修改 plan-review 的 SKILL.md」已過時：實測 plan-review/SKILL | 低優先未排程——plan-security Gotcha 仍寫『需同步修改 plan-review SKILL.md』過時待辦句 |
| 129 | plan-setup | reference/中 | Agent 名稱寫 spec-analyst 等 4 個，實際檔案為 feature-spec-analyst.md 等 | 結構未排程——plan-setup Agent 名仍寫 spec-analyst 等（實檔 feature-*），且無安裝步驟 |
| 130 | plan-setup | reference/中 | 全篇 MCP 工具用短名（notion-fetch、notion-update-data-source），環境同時有 c | 其他——plan-setup 全篇短名（notion-fetch/notion-update-data-source） |
| 131 | plan-setup | token/中 | 3-4 段的工作區頁面更新步驟與 db-templates.md:203「更新步驟（plan-setup 追加功能設計庫 | 低優先未排程——plan-setup 3-4 段工作區更新步驟與 db-templates.md 重複未下放 |
| 133 | plan-setup | structure/低 | 「29 種工具，持續維護」為時效性宣稱，工具數會隨版本變動；且步驟 6 建立時未提本環境已裝 chrome-devtoo | 低優先未排程——plan-setup 仍寫『29 種工具，持續維護』時效性宣稱、缺 chrome-devtools 已裝跳過條件 |
| 136 | plan-spec | structure/中 | 範例檔「判斷」區塊缺 TASK_TYPE、CHANGE_SCOPE、NEW_API、EXISTING_API_CHANG | 結構未排程——plan-spec good-spec-output 範例判斷區塊仍缺 TASK_TYPE/CHANGE_SCOPE/NEW_API 欄位 |
| 138 | plan-spec | structure/低 | 前置條件標明僅適用 Feature，但未定義活躍任務為 bug 型時的行為；plan-start 支援 bug 型任務， | 低優先未排程——plan-spec 未補『活躍任務 type=bug 時導向 /bug-fix』 |
| 140 | plan-stack | structure/中 | ID 覆蓋規則三處自相矛盾：步驟 1（:37）可確認後覆蓋、步驟 3（:47）不可與內建重複、Gotcha（:108）說 | 結構未排程——plan-stack ID 覆蓋規則三處仍矛盾，且與 config-resolver『內建一律讀 _builtin』行為不符 |
| 142 | plan-stack | trigger/中 | description 宣稱通用技術棧設定，但內文以 Java 為前提（pom.xml/build.gradle:43、 | 其他——plan-stack description 仍稱通用，內文以 Java 為前提未標注 |
| 144 | plan-stack | reference/低 | 回傳結果硬寫 ~/.claude/feature-workflow/stacks/{id}.md，但 config-re | 低優先未排程——plan-stack 回傳仍硬寫 ~/.claude/feature-workflow/stacks/，未顯示實際解析路徑 |
| 146 | plan-start | reference/中 | Bug 模板僅寫「使用 bug-start 的標準模板」，無路徑；模板內嵌於另一 plugin 的 SKILL.md，G | 結構未排程——plan-start Bug 模板仍寫『用 bug-start 標準模板』無路徑，未抽共用 references |
| 149 | plan-start | structure/低 | frontmatter 未用 argument-hint，skill 明確接受 <任務簡述> [選項] 引數 | 低優先未排程——plan-start frontmatter 仍無 argument-hint |
| 154 | plan-status | structure/低 | cleanup 步驟 3「還原 .gitignore 中的 !.spec/{slug}/ 排除規則」語意含糊，實際是刪除 | 其他——plan-status cleanup 步驟仍寫『還原 !.spec/{slug}/ 排除規則』，且與 plan-close 改用 git add -f『不動 .gitignore』新做法不一致 |
| 158 | plan-sync | reference/低 | notion-fetch、notion-update-page 非完整 MCP 工具名，且環境有 claude.ai N | 其他——plan-sync notion-fetch/notion-update-page 短名未指明 server |
| 159 | plan-sync | token/低 | status→開發階段 對照表兩欄內容逐列完全相同，表格無資訊量 | 低優先未排程——plan-sync status→開發階段 對照表兩欄相同無資訊量 |
| 163 | plan-verify | structure/中 | 步驟 4 稱「MCP 的 --autoConnect 自動連本機 Chrome」，此為 chrome-devtools  | 結構未排程——plan-verify 225 行仍泛稱『MCP 的 --autoConnect』，該旗標僅 chrome-devtools 適用 |
| 164 | plan-verify | reference/中 | 「格式見 spec.md 的驗證記憶系統段落」為懸空引用；grep 全 plugin 僅 README.md 提及該詞 | 結構未排程——plan-verify 301 行仍懸空引用『spec.md 的驗證記憶系統段落』 |
| 165 | plan-verify | reference/中 | Bash 模式通篇使用 $CDP，但全 plugin grep 'CDP=' 無定義，照做必失敗 | 其他——plan-verify run-verification.md 仍用 $CDP（43/90/91 行）但全 plugin 無 CDP= 定義 |
| 167 | plan-verify | structure/中 | --from-e2e {dir} 只出現在用法清單，內文無任何執行步驟 | 結構未排程——plan-verify --from-e2e 仍只在用法清單、內文無執行步驟 |
| 171 | plan-verify | reference/低 | examples/verify-report-sample.md 未被 SKILL.md 或 phases 任何處引用（ | 低優先未排程——plan-verify examples/verify-report-sample.md 仍未被引用（原報告建議勿刪） |
| 172 | plan-verify | token/低 | 本體 563 行超過官方建議 500 行；Gotchas/邊界情況中約半數為 Word/Excel 報告細節 | 低優先未排程——plan-verify 本體仍 560 行(>500)，報告類 Gotchas 未下放 phases/ |
| 179 | project-add | token/中 | Git Flow 分支偵測約 70 行（指令、兩張信號表、邊界情況）全放內文，SKILL.md 已 482 行逼近 50 | 低優先未排程——project-add Git Flow 偵測(~70行)未下放 references（檔仍 483 行） |
| 181 | project-add | structure/低 | 步驟 9 結果範例只列舊格式 feature-workflow-config.md 路徑，與步驟 7／Gotchas「新 | 低優先未排程——project-add 步驟 9 結果範例仍列舊格式 feature-workflow-config.md 路徑 |

## partial 逐條清單（22 條）

| # | skill | 維度/嚴重度 | issue（摘要） | 狀態原因 |
|---|---|---|---|---|
| 18 | bug-investigate | structure/中 | ```markdown 範例區塊內再嵌 ``` 內層 fence，外層 fence 提前閉合，Markdown 結構壞損 | partial——bug-investigate 巢狀範例仍用三反引號外層，內層 fence 仍會提前閉合（內容已重構移至 references） |
| 37 | bug-update | token/低 | 「快捷用法彙整」與步驟 3「支援的輸入方式」範例重複：通報來源、初步判斷、log 檔案、stacktrace 四項兩處都 | partial（需人工確認）——bug-update 快捷用法與步驟 3 範例去重程度未逐項核對 |
| 49 | crew-init | structure/低 | --skip-bug/--skip-plan 宣告用途（已執行 setup）與各階段 1a/2a 自動偵測跳過功能重複； | partial（需人工確認）——crew-init --skip 與自動偵測/--resume 三路徑是否收斂未核對 |
| 50 | crew-init | token/低 | description 前半摘要執行流程（依序執行 /bug-setup → /plan-setup…），可能讓 age | partial——crew-init description 仍摘要執行流程（含跳過邏輯字樣） |
| 51 | crew-init | token/低 | 結尾摘要「可用指令」與「進階」兩區重複列出 /crew-doctor | partial（需人工確認）——crew-init 結尾 crew-doctor 是否仍重複列出未核對 |
| 57 | crew-upgrade | structure/低 | Gotcha 警告「版本比較是字串比較」，但內文從未定義任何比較邏輯（bash 或指示），agent 只能自行發明比較方 | partial——crew-upgrade Gotcha 已註明三段式版本，但步驟仍無明確比較指令（sort -V 等） |
| 72 | plan-build | token/中 | 步驟 8 兩個回傳模板（含測試/跳過測試）約 90% 重複，僅統計行與 test-engineer 行不同，浪費約 25 | partial（需人工確認）——plan-build 步驟8 兩回傳模板是否合併未核對 |
| 74 | plan-build | trigger/低 | description 摘要實作細節（E1~E7、DB_REQUIRED=insert-only、最多 5 人）而非觸發 | partial——plan-build description 已移除 E1~E7/5人，但仍留退出驗證/deploy.sql 實作細節 |
| 92 | plan-demo | structure/中 | 2c–2f（db/arch/files/verify 範本）僅一句話描述，L196 稱「prompt 內 inline」 | partial——plan-demo 2c-2f 已從一句話擴為 1-2 句描述，仍非完整範本 |
| 101 | plan-deploy-confirm | structure/中 | 前置條件要求設定檔含「任務追蹤工具」資料庫 ID，但未指引如何讀取（plan-sync/plan-close/plan- | partial——plan-deploy-confirm 前置條件已引 prerequisites，但未明指用 config-resolver 讀 DB ID |
| 106 | plan-explore | token/中 | 「不同進入情境的處理」四段完整範例對話近 100 行含大型 ASCII 圖，對執行幫助有限 | partial（需人工確認）——plan-explore 情境範例(~100行)是否下放未核對（觸發詞已修） |
| 107 | plan-explore | structure/低 | 範例含特定專案敘事內容（AQI、防汛水費、LineBC、Solr apilog），對通用 plugin 不具可移植性 | partial（需人工確認）——plan-explore 專案特定範例(AQI等)是否中性化未核對 |
| 108 | plan-explore | token/低 | 「視覺化」示範框圖純裝飾（用 ASCII 框畫「自由使用 ASCII 圖表」），大半無資訊量 | partial（需人工確認）——plan-explore 視覺化裝飾框圖是否精簡未核對 |
| 114 | plan-next | structure/低 | 決策表 first-match 順序：「files.md 但無 security.md」排在 verify.md=FAI | partial——plan-next 已補『verify FAIL+review PASS』邊界，但決策表 first-match 順序(security 缺檔先於 verify FAIL)未調整 |
| 126 | plan-security | structure/低 | L1-SEC-2 的「指令」欄放的是描述文字非可執行指令，與同表其他列（皆為 grep）不一致，agent 無法照表執行 | partial——plan-security L1-SEC-2 仍為描述性文字非 grep 指令，與同表其他列不一致 |
| 132 | plan-setup | token/低 | 情境 B 的建庫 7 步驟細節（Relation 補欄、is_inline、Views）與 db-templates.m | partial（需人工確認）——plan-setup 情境 B 建庫 7 步驟是否濃縮未核對 |
| 152 | plan-status | structure/中 | --cleanup 說「清除超過 N 天」但未定義 N 如何指定；第 5 節範例寫死 30 天 | partial——plan-status --cleanup 天數基準已於 Gotcha 說明，但用法列仍寫『N 天』未定義參數格式 |
| 166 | plan-verify | reference/中 | `npx --yes exceljs` 無法執行：exceljs 無 bin 欄位（npm view 實測為空），且 n | partial——plan-verify word-report.md 已加 npm_config_prefix 包裝，但仍用 npx --yes exceljs（exceljs 無 bin，能否執行需實測） |
| 175 | plan | structure/低 | 「回傳結果」模板無條件列出 db.md + db.sql，但 plan-db 僅在 DB_REQUIRED=true 時 | partial（需人工確認）——plan 流程已加 DB_REQUIRED 條件，但回傳模板(45行)是否仍無條件列 db.md/db.sql 未確認 |
| 177 | project-add | structure/中 | 宣告只檢查 prerequisites 第 2 項，跳過 §0.5 Notion 後端偵測，但本 skill 大量呼叫  | partial——project-add 前置已納入 §0.5 後端偵測，但第 16 行仍硬寫『claude plugin install notion』單一後端 |
| 178 | project-add | structure/中 | 情境 A 直接「跳到步驟 7」，但步驟 7 新格式檔必填 stack/prod_branch/uat_branch，未說 | partial（需人工確認）——project-add 情境 A 缺值設定檔問題是否修正未核對 |
| 180 | project-add | token/低 | 專案類型判斷表與 references/project-page-templates.md:9-22 重複，雙源易漂移（ | partial——project-add 類型判斷表已加 project-page-templates.md 引用，是否移除模版檔重複未核對 |
