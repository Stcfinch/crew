# 開發與發版指南

## 版本升級 Checklist

升版時**必須完成以下所有步驟**，缺一不可：

### 1. 修改版號（兩個地方）

- `plugins/{plugin}/.claude-plugin/plugin.json` 的 `"version"` 欄位 — **這是 `claude plugin update` 判斷是否有新版的依據**
- `plugins/{plugin}/README.md` 第一行的 `` `vX.Y.Z` `` 標記

> **易錯點**：只改 README 不改 plugin.json，會導致 update 認為「已是最新」不會重新安裝。

### 2. 更新 CHANGELOG.md

在根目錄 `CHANGELOG.md` 新增版本區塊，格式：

```markdown
## [{plugin}@{version}] - {YYYY-MM-DD}

### 新增
- **功能名稱** — 一句話說明

### 改善
- **改善項目** — 一句話說明
```

- `/crew-upgrade` 讀取此檔案顯示更新摘要，**沒寫就等於沒更新**
- 條目從 git diff 和 commit message 提取，確保完整

### 3. 同步 README

需同步更新的 README 共三份：

| 檔案 | 需更新的內容 |
|------|-------------|
| `plugins/{plugin}/README.md` | 版號、功能說明、指令表、前置條件 |
| `README.md`（根目錄） | 指令表、流程圖、前置條件 |

**常見遺漏**：根目錄 README 的指令說明欄（如 plan-verify 的功能描述）未同步。

### 4. Commit

```bash
# 功能 commit（先提交）
git commit -m "feat({scope}): {功能說明}"

# 升版 commit（最後提交）
git commit -m "chore({plugin}): 升版至 v{X.Y.Z}"
```

升版 commit 應包含：版號修改 + CHANGELOG 更新 + README 同步。

---

## 版號規則

- **Major（X）**：破壞性變更（設定格式不相容、Skill 行為大改）
- **Minor（Y）**：新功能、新 Skill
- **Patch（Z）**：Bug 修復、文案修正、小改善

兩個 Plugin 版號獨立遞增：
- `bug-workflow` 目前 v3.x
- `feature-workflow` 目前 v4.x

---

## 檔案結構

```
company-marketplace/
├── .github/workflows/    # CI lint（版本一致性、SKILL.md 格式、共用 ref 漂移）
├── .gitignore
├── CHANGELOG.md          # 所有 Plugin 的變更紀錄（/crew-upgrade 讀取）
├── CONTRIBUTING.md       # 本文件
├── README.md             # 根目錄總覽（安裝、流程、指令表）
├── scripts/              # 版本同步、lint
└── plugins/
    ├── bug-workflow/
    │   ├── README.md     # Bug Workflow 詳細文件
    │   ├── references/   # 共用 reference（與 feature-workflow 同步，CI 防漂移）
    │   └── skills/       # 各 Skill 的 SKILL.md
    └── feature-workflow/
        ├── README.md     # Feature Workflow 詳細文件
        ├── references/   # 共用 reference + 專屬 reference
        └── skills/       # 各 Skill 的 SKILL.md
```

---

## `.spec/` 目錄規範

`.spec/{slug}/` 是 `/plan-start` 建立的本地任務目錄，**預設不入版控**
（已寫入 `.gitignore` 的 `.spec/*/`）。

### 何時應該 commit `.spec/`？

只有「對外設計文件」性質的內容才入版控：

- ✅ 套件本身的改進計畫（如 `.spec/crew-improvement/`）
- ✅ 重大架構決策的設計文件（之後可能改為 `docs/adr/`）
- ❌ 個人 dogfood 的暫存 spec
- ❌ 在客戶專案內 `/plan-start` 產生的工作目錄

### 如何 commit「對外設計」目錄

由於 `.gitignore` 預設排除 `.spec/*/`，需強制加入：

```bash
git add -f .spec/{slug}/
```

並建議在 `.gitignore` 的「白名單」段落明示意圖：

```gitignore
!.spec/{slug}/
```

---

## 共用 reference 同步規則

`plugins/bug-workflow/references/` 與 `plugins/feature-workflow/references/`
各自帶以下檔案的副本（為了 plugin 可獨立安裝）：

- `prerequisites.md`
- `db-templates.md`
- `discipline-preamble.md`
- `notion-backend.md`

**單一權威來源（C9）**：`plugins/bug-workflow/references/` 那份是唯一權威，
**只改這份**；`feature-workflow` 那份一律視為同步產物，不要直接編輯。

改完共用 reference 後，跑一次同步腳本把權威份同步到 feature-workflow：

```bash
./scripts/sync-shared-refs.sh          # 以 bug-workflow 為準同步到 feature-workflow
./scripts/sync-shared-refs.sh --check  # push 前檢查是否一致（CI 同款檢查，不修改）
```

CI 的 `shared-refs-consistency` job（`scripts/check-shared-refs.py`）仍用 sha256
強制兩份一致，是最後防線：忘了跑同步腳本、或誤改了 feature-workflow 那份，都會被 CI block。
