# Git Flow 分支偵測

自動推測正式環境（PROD）和測試環境（UAT）分支。以 **commit 活動模式**為主要依據，分支名稱為輔助信號。

## 資料收集

```bash
# 預設分支（最強 PROD 信號）
git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's|refs/remotes/origin/||'

# 所有遠端分支 + 最後 commit 時間 + commit 數（近 6 個月）
git for-each-ref --sort=-committerdate \
  --format='%(refname:short) %(committerdate:iso) %(committerdate:relative)' \
  refs/remotes/origin/

# 各分支近 6 個月的 commit 頻率
git rev-list --count --since="6 months ago" origin/{branch}

# 檢查是否有 release tag 指向特定分支
git tag -l 'v*' --sort=-creatordate | head -5
git branch -a --contains {latest-tag}
```

## 推測邏輯

**Step 1 — PROD 分支推測**（依信號強度排序）：

| 優先順序 | 信號 | 說明 |
|---------|------|------|
| 1 | `origin/HEAD` 指向的分支 | 遠端預設分支，最強信號 |
| 2 | 最新 release tag 所在的分支 | 有版本標籤的分支通常是正式環境 |
| 3 | commit 頻率**最低**的長期分支 | PROD 通常只接收 merge，commit 頻率低於 UAT |
| 4 | 名稱匹配 | `production` / `master` / `main` / `release` / `prod` |

> 「長期分支」= 最後 commit 在 30 天內且存在超過 3 個月的分支，排除 `feature/*`、`hotfix/*`、`bugfix/*` 等短期分支。

**Step 2 — UAT 分支推測**（排除已選為 PROD 的分支後）：

| 優先順序 | 信號 | 說明 |
|---------|------|------|
| 1 | commit 頻率**最高**的長期分支 | UAT/staging 通常是最頻繁接收 merge 的分支 |
| 2 | 名稱匹配 | `uat` / `staging` / `develop` / `dev` / `test` / `sit` |
| 3 | 無符合 | 可能專案無 UAT 分支（如直接從 feature merge 到 PROD） |

## 展示偵測結果

```
Git Flow 分支偵測：

  分支列表（依最後 commit 時間排序）：
    1. production    — 2 天前（近 6 個月 23 次 commit）← 推測 PROD
    2. uat           — 1 天前（近 6 個月 87 次 commit）← 推測 UAT
    3. develop       — 5 天前（近 6 個月 102 次 commit）
    4. feature/xxx   — 3 小時前（短期分支，已排除）

  正式環境（PROD）分支：production ⭐ 預設分支 + 低頻 commit
  測試環境（UAT）分支：uat ⭐ 高頻 commit

確認？[Y/n]
  輸入分支名稱可直接覆蓋，輸入「無」跳過 UAT
```

## 邊界情況

- **只有一個長期分支**（如 `main`）→ 設為 PROD，UAT 留空
- **所有分支 commit 頻率相近** → 以 `origin/HEAD` 為 PROD，詢問使用者指定 UAT
- **無遠端分支**（剛 init 的 repo）→ 直接詢問使用者手動輸入
- **偵測結果明顯不合理**（如 `feature/xxx` 被選為 PROD）→ 不應發生（已排除短期分支），但仍需使用者確認

> 此資訊會影響 `/plan-start`（從 PROD 分支建立 feature branch）、`/plan-close` 和 `/plan-review`（用 PROD 分支做 merge-base 計算 diff）。
