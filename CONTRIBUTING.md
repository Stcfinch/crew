# 開發與發版指南

## 版本升級 Checklist

升版時**必須完成以下所有步驟**，缺一不可：

### 1. 修改版號

- `plugins/{plugin}/README.md` 第一行的 `` `vX.Y.Z` `` 標記

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
├── CHANGELOG.md          # 所有 Plugin 的變更紀錄（/crew-upgrade 讀取）
├── CONTRIBUTING.md       # 本文件
├── README.md             # 根目錄總覽（安裝、流程、指令表）
└── plugins/
    ├── bug-workflow/
    │   ├── README.md     # Bug Workflow 詳細文件
    │   └── skills/       # 各 Skill 的 SKILL.md
    └── feature-workflow/
        ├── README.md     # Feature Workflow 詳細文件
        └── skills/       # 各 Skill 的 SKILL.md
```
