# CREW for Codex

Codex 版將上游 27 個工作流入口整合成一個 `crew` plugin。
本機工作流只需要 Python 3.10+；分支與文件漂移檢查另需 Git。
原本的 `plugins/bug-workflow` 和 `plugins/feature-workflow` 持續保留。

## 安裝

在有 Codex CLI 的環境執行：

```powershell
git clone --branch codex-plugin https://github.com/Stcfinch/crew.git
cd crew
python scripts/install-codex.py
```

macOS/Linux 的 Python 指令可改用 `python3`；Windows 也可使用 `py -3` 或 Python 的絕對路徑。

安裝程式會：
- 只複製 `.codex-plugin/`、`skills/`、`codex/` 到 `~/plugins/crew/`。
- 在預設 `~/.agents/plugins/marketplace.json` 加入 crew，保留其他 entries 與顯示名稱。
- 執行 `codex plugin add crew@<personal marketplace 名稱>`。
- 安裝來源不包含 Git 歷史、上游 hooks、Claude 設定或任何帳號憑證。

可先用 `--dry-run` 預覽；`--no-enable` 只建立檔案，未啟用。
已安裝更新需 `--update`，會保存舊套件/marketplace 備份並刷新版本快取識別。
不同來源的既有同名套件會拒絕覆蓋。這是個人 marketplace，無需執行 marketplace add。

安裝完成後**開啟新的 Codex 任務**：

```text
$crew-init
$plan-demo
$plan-start 新增登入失敗次數限制
$plan
$plan-build
$plan-verify
$plan-review
$plan-close
```

Bug 流程：

```text
$bug-investigate 登入後偶爾被登出
$bug-fix
$plan-verify
$plan-review
$bug-close
```

目前 task 未結案時可用 `$plan-next <slug>` 查看下一步。
以上是 Codex 輸入框中的 skill 語法，不是 PowerShell 指令。

## 行為差異與相容範圍

| 原本的行為 | Codex 版 |
|---|---|
| 兩個 Claude plugins | 一個 crew plugin、27 個原生 Codex skills |
| Claude 指令、模型名稱、Team API | 使用目前 Codex 工具，繼承使用者模型；可單代理完成 |
| 全域雙設定目錄 | 每個專案共用 `.crew/config.json`，預設 local |
| 所有流程依賴 Notion 設定 | 本機模式先工作；Notion 需另外連接可用工具 |
| 自動 SessionStart hook | 明確呼叫 `$plan-status` 或 `$plan-next` |
| Unix fcntl 鎖 | Windows msvcrt / Unix fcntl，保留原子寫入 |
| 特定 CDP/E2E、Word 品牌模板 | 使用 host 可用瀏覽器、文件、試算表技能或既有專案 runner |

這是 Codex 原生移植，**不承諾原平台的所有附加整合一對一相容**：
上游四個專家 agent、特定 Word 三種品牌样式、Chrome CDP 腳本與自動 hooks 不會安裝。
Word/Excel/E2E 入口保留，但產出依實際可用的技能/runner；缺少時會明確報告。
Notion 不隨套件自動授權；需要提供連線與 workspace/schema 映射才能讀寫。
舊版語意文件不自動改寫，見 [移轉流程](../codex/references/legacy.md)。

## 檔案與續接

```text
<project>/
  .crew/config.json          # local / notion；不存 token
  .crew/project.md           # 可選專案識別與建置摘要
  .crew/stack.md             # 可選技術棧規則
  .crew/notion.md            # 可選實際 schema 與欄位映射
  .spec/<slug>/
    plan.md                 # 六章節的人讀文件
    state.json              # scripts/crew-state.py 單一寫者
    deploy.sql              # 有 SQL 需求時才建立
    deployment.md           # 有部署回報時記錄環境/Step 證據
    .cache/                 # 可選驗證報告與待同步摘要
```

設定沒有預設伺服器或外部 endpoint。詳見 [執行契約](../codex/references/runtime.md)、
[Notion 整合](../codex/references/notion.md)、[結案檢查](../codex/references/closure.md)。
建議在目標專案忽略 `.crew/`、`.spec/` 的個人/暫存資料；安裝程式不修改專案 gitignore。
既有 schema_version=1 狀態可沿用；Bug 的 spec/build 對應調查/修復。
程式變更後重設舊驗證為 STALE，結案檢查會拒絕未完成、失效或 FAIL 結果。

## 27 個入口

| Skill | 用途 |
|---|---|
| `$crew-init` | 初始化 CREW for Codex 專案；建立本機設定、檢查環境，或接續未完成設定。 |
| `$crew-doctor` | 檢查 CREW 的 Python、Git、設定與任務狀態；用於環境健診或工作流故障排查。 |
| `$crew-upgrade` | 更新已安裝的 CREW Codex plugin；適用使用者明確要求升級 CREW。 |
| `$bug-setup` | 設定 CREW Bug 工作流的本機環境或 Notion 任務庫、Bug 知識庫。 |
| `$plan-setup` | 設定 CREW 功能開發工作流與選用 Notion 功能設計庫。 |
| `$project-add` | 偵測專案技術棧、建置方式與 Git remote，選用註冊至 Notion 專案庫。 |
| `$plan-stack` | 偵測與記錄 CREW 專案的程式分層、命名和建置測試慣例。 |
| `$plan-start` | 建立 CREW 功能任務、plan.md、流程狀態與工作分支。 |
| `$bug-start` | 建立 CREW Bug 任務與重現紀錄；尚不調查或修復程式碼。 |
| `$bug-investigate` | 調查 CREW Bug 的重現條件與根因，以假說和證據定位問題。 |
| `$bug-update` | 更新 CREW Bug 調查證據，或重新開啟已結案 Bug。 |
| `$bug-fix` | 依 CREW 已確認根因實作 Bug 修復，執行重現與迴歸驗證。 |
| `$plan-explore` | 以 CREW 探索功能構想、調查問題或比較設計方案，尚不啟動實作。 |
| `$plan-browse` | 閱讀、搜尋或比較既有 CREW .spec 規劃與工作流狀態。 |
| `$plan` | 執行 CREW 功能規劃的 spec、db、arch 三階段，產出單一 plan.md 與必要 deploy.sql。 |
| `$plan-build` | 依 CREW plan.md 實作功能並維護可續接的工作單元；支援 dry-run 與 resume。 |
| `$plan-security` | 針對 CREW 任務變更執行安全審查，記錄具體可驗證的發現。 |
| `$plan-verify` | 驗證 CREW 任務的驗收條件，支援瀏覽器、E2E 與選用 Word/Excel 報告。 |
| `$plan-review` | 審查 CREW 任務的程式邏輯、品質與效能；支援 quick 範圍審查。 |
| `$plan-close` | 在驗收、審查和漂移檢查完成後結束 CREW 功能任務，按授權提交或同步。 |
| `$bug-close` | 確認 Bug 修復與迴歸驗證後結案，選用同步 Notion Bug 知識庫。 |
| `$plan-sync` | 將 CREW 任務進度與規劃摘要同步至已設定的 Notion。 |
| `$plan-status` | 列出 CREW 任務與狀態，恢復中斷工作或檢查舊版任務。 |
| `$plan-next` | 根據 CREW state.json 推薦下一步或續接中斷工作。 |
| `$plan-drift` | 檢查與修正 CREW plan.md 中失效的程式碼/SQL 錨點與過時決策。 |
| `$plan-demo` | 建立不依賴 Notion 的 CREW 功能規劃示範，便於評估套件。 |
| `$plan-deploy-confirm` | 記錄使用者或 DBA 回報的 CREW SQL 部署進度，支援 env、list 與 all-done。 |

## 開發與驗證

```text
python scripts/validate-codex.py
python -m unittest discover -s tests -v
```

測試使用暫存專案，不連接 Notion，也不啟用真實 Codex 設定。
涵蓋本機建立、重複任務保護、Bug 路由/續接、Windows 檔案鎖競爭、
路徑限制、損壞狀態診斷、結案/漂移與隔離安裝及更新備份。
CI matrix 為 Windows/Linux、Python 3.10/3.12；實際執行結果以 Actions 為準。

`codex/scripts/crew-state.py` 和 `check-spec-drift.py` 由上游
`2d8acc5bc826ef22f9fd3d2abe01e515bb7f8801` 移植，保留 MIT 授權於
[codex/LICENSE](../codex/LICENSE)。不要直接同步覆蓋 Codex 的平台適配修改。

套件格式參照 [OpenAI Build plugins](https://learn.chatgpt.com/docs/build-plugins)
與 [Build skills](https://learn.chatgpt.com/docs/build-skills)。

