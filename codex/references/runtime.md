# Codex 執行契約

此版本將 CREW 的 Bug 與 Feature 工作流合併為一個 Codex plugin，保留上游狀態 schema。
使用者指示與 host 權限優先；skill 不自動授權 Git 發佈、Notion 寫入或 DB 操作。既有授權持續有效。

## 路徑與工具

從 SKILL.md 所在的 skill 目錄向上兩層可找到 plugin 根目錄；codex/scripts/ 與 codex/references/ 都在該根目錄內。
先解析為實際絕對路徑，不依賴安裝快取版號或任何平台專用環境變數。
下文 state 代表 scripts/crew-state.py，drift 代表 scripts/check-spec-drift.py。
用可用的 Python 3.10+ 執行，Git 用於分支及漂移檢查。無額外 Python 套件需求。
PowerShell 使用 & '<python.exe>' '<script.py>'；Bash 使用 python3 "<script.py>"。
每次傳明確 --project <root> 或 drift 的 --root <root>，不要假定目前目錄就是目標專案。

讀取有效範圍的 AGENTS.md。設定預設為 <project>/.crew/config.json；
不存在時本機模式仍能用。不要自動搬移舊環境設定或存取其他帳號。
Notion 整合只使用當前已連接且可呼叫的工具，依工具 schema 操作，不硬編碼工具名稱。
缺少 Notion 時先完成本機工作，將「尚未同步」清楚列出。
瀏覽器、文件與試算表功能依當前 host 提供的技能/工具使用。

## 工作狀態

.spec/<slug>/plan.md 是人讀文件；state.json 是唯一流程權威，透過 state CLI 寫入；deploy.sql 是唯一 SQL 來源。
task type=bug 把 spec 對應根因調查、build 對應修復，db/arch 初始 skipped；需要時可重新開啟。
phase 是當前/最後階段，不是完成證據；以 steps 和 results 判斷。

```text
crew-state.py init --slug login --type feature --project <root>
crew-state.py set --slug login --step spec --status done --project <root>
crew-state.py unit --slug login --skill plan-build --done 1 --total 3 --remaining auth-test --evidence tested-handler --project <root>
crew-state.py result --slug login --kind verify --status PASS --project <root>
crew-state.py set --slug login --step verify --status done --project <root>
crew-state.py validate --slug login --project <root>
crew-state.py next --slug login --project <root>
```

完整參數看各子命令 --help。工具回非零就處理失敗，不把打算做的事記成完成。
長任務每個單元完成即保存 unit，正常收尾用 unit --clear；不要手寫 state.json。
完成 result 不會自動標记 step 完成，兩者都需依證據更新。
程式修正後把 security/verify/review steps 改 pending、results 改 STALE，重跑受影響檢查。
修復或 skipped 需要真實理由；不能以 skipped 消除待處理失敗。

## Codex 整合差異

入口使用 $skill-name；不用平台專屬 slash parser 或動態 shell frontmatter。
無 SessionStart hook；需要任務摘要時明確執行 state session-brief --project <root>。
不安裝 agent 定義、不修改模型選擇。多代理只在使用者/專案已要求且 host 提供時運用。
工作流可以由單一 agent 完成，不以缺乏平行工具作為阻擋。安裝後以新任務載入技能。
