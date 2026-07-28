# CREW（公司內部 Claude Code Plugins）

CREW 是公司內部的 Claude Code plugin 集合，整合 Notion 與 Claude Code，涵蓋 Bug 處理與功能開發的完整生命週期。本檔是團隊共用詞彙表（ubiquitous language），只定義 CREW 專屬概念，不含實作細節。

## Language

### 整體與 Plugin

**CREW**：
本 marketplace 兩個 plugin（bug-workflow 與 feature-workflow）的合稱，代表「一組分工協作、把任務從頭跑到尾的工作流」。
_Avoid_: 工具箱、外掛集、套件

**feature-workflow**：
負責功能開發全生命週期的 plugin，指令以 `plan-` 為前綴，是 CREW 的旗艦 plugin。
_Avoid_: feature plugin、開發外掛

**bug-workflow**：
負責 Bug 生命週期的 plugin，指令以 `bug-` 為前綴，並掛載 CREW 跨 plugin 的共用維運指令（`crew-*`、`project-add`）。
_Avoid_: bug plugin、除錯外掛

### 規劃與產物

**.spec/**：
放在專案本地的規劃目錄，一個任務一個子目錄，只放三個檔：`plan.md`、`state.json`、`deploy.sql`。
_Avoid_: spec 資料夾、規劃檔

**plan.md**：
一個任務**唯一**給人與 LLM 讀的文件，六個章節（目標與範圍／驗收條件／決策紀錄／已知取捨與風險／指路／檢查報告摘要）。只寫程式碼裡看不到的東西。
_Avoid_: 規格書、設計文件、spec（`spec.md` 已於 v5 廢除）

**code-truth**：
「程式碼才是唯一事實」的內容——欄位清單、方法簽章、類別清單、DDL、檔案清單。**禁止抄進 plan.md**，一律用錨點指過去。抄寫是 Token 昂貴與文件漂移的共同根因。
_Avoid_: 實作細節（範圍太模糊）

**錨點（anchor）**：
plan.md 指向程式碼的可機器驗證引用，正規形 `@code:<路徑>#<符號>` 與 `@sql:deploy.sql#<表名>`。行號 `(L88)` 寫在 token 外面，只給人看、不參與判定。
_Avoid_: 連結、引用、指標

**漂移（drift）**：
文件與程式碼不一致。v5 之後特指**錨點失效**（檔案改名、符號被刪、文件落後程式碼），由 `check-spec-drift.py` 偵測、`/plan-drift` 修復。
_Avoid_: 過時、不同步（語意太寬）

**硬關卡**：
`plan-close` 在 `git add -f` 與 Notion 同步**之前**的漂移檢查，是全流程唯一會擋下結案的檢查。FAIL 擋、WARN 逐筆明示放行。
_Avoid_: 檢查點、gate（中英混用）

**state.json**：
流程狀態的**唯一權威**，機器可讀，唯一寫者是 `crew-state.py`。結案後保留並入版控（不像已廢除的 `handoff.md` 結案即刪）。
_Avoid_: 狀態檔（易與設定檔混淆）、手寫 JSON

**展示層**：
指 Notion 在 CREW 中的角色——只是規劃結果的呈現與追蹤處，不是即時事實來源。plan-* 指令預設不呼叫 Notion，僅 start / close 批次同步。
_Avoid_: 資料來源、即時同步、主儲存

**deploy.sql**：
**唯一 SQL 事實來源**，由 `/plan` 的 db pass 產出、供 DBA 執行。任何 skill 都不得掃描文件的 SQL 區塊重新組裝。
_Avoid_: migration（遷移檔另有專門 skill，語意不同）、db.sql（v5 已廢除）

**Health Score**：
plan-verify 以 Playwright 逐條驗收後，對驗收條件達成度給出的量化分數。
_Avoid_: 通過率、驗收分數

### 執行模式

**三 pass**：
`/plan` 內含的 spec、db、arch 三個階段，各自往 `plan.md` 對應章節寫入。可 `/plan spec|db|arch` 單跑，但單跑不等於可以跳過確認。
_Avoid_: 三階段、三步驟（易與整體流程的階段混淆）

**append-only**：
`plan.md` 共享章節（決策紀錄／已知取捨與風險／指路／檢查報告摘要）的寫入紀律——只能用 Edit 對錨點註解插入新條目，**禁止整檔改寫或整段取代**。改變主意用 supersede（`D-7 取代 D-3`），不刪除舊條目。
_Avoid_: 追加、附加（會被誤解成可以順便改前面）

**Leader / Teammate（leader-delegate）**：
plan-build 與 plan-review 採用的 Agent Teams 分工——Leader 只協調、不寫 code；Teammate 各自承接單一角色脈絡（db / backend / api / frontend / test）。
_Avoid_: 主 agent／子 agent、master/worker

**退出驗證**：
plan-start、plan-build 等指令在收尾前強制檢查必填項是否齊全的關卡，用來防止半成品或虛報完成。
_Avoid_: 收尾檢查、self-check

**根因鐵律**：
bug-fix 的硬規則——未確認根因不得改碼。
_Avoid_: 先修再說、快速修復

### 專案分類

**簡單型專案 / 產品型專案**：
CREW 對承載專案的分類；產品型含 kernel/、Solr、Hazelcast 等額外基礎設施，規劃時需額外納入考量。
_Avoid_: 小專案／大專案
