# ADR-004：為何兩 plugin 各自帶共用 reference（DRY 退讓給獨立性）

- 日期：2026-05-22（feature-workflow@4.18.0 + bug-workflow@3.9.0 同期）
- 狀態：已採用

## 背景

`prerequisites.md` / `db-templates.md` / `discipline-preamble.md` 三個 reference 檔案
原本只在 `bug-workflow` 內，`feature-workflow` 12 個 SKILL.md 跨 plugin 引用：

```
> **前置檢查**：參照 bug-workflow plugin 的 `references/prerequisites.md` ...
```

這違反 marketplace「plugin 可獨立安裝」的核心契約：
若使用者只裝 `feature-workflow`，引用會解析失敗。

候選方案：
- **A**：抽出第三個共用 plugin `crew-common`
- **B**：兩 plugin 各自帶一份 reference 副本，CI 防漂移
- **C**：保留現狀（接受跨 plugin 強耦合）

## 決策

採方案 **B**：兩 plugin 各自帶一份完整副本，靠 `scripts/check-shared-refs.py`
用 sha256 在 CI 防漂移。

理由：
1. 「可獨立安裝」是 marketplace 模型的核心契約，不能讓步
2. 方案 A 增加 marketplace 維運單元、使用者要多裝一個 plugin、安裝路徑變長
3. 重複的 reference（總共 ~600 行）變更頻率不高，同步成本可承受
4. CI lint 可低成本偵測漂移，把「人類記得同步」變為「機器強制」

## 後果

**正面**：
- 兩個 plugin 各自完整可獨立安裝
- 任何一份更新時 CI 立即偵測到不一致 → 強制使用者同改兩份
- 不增加 marketplace 維運單元

**負面**：
- 更新 reference 時要 cp 一次（CONTRIBUTING.md 寫明流程）
- 不嚴格的 DRY（同樣內容存兩處）

**中性**：
- 若未來有第三個 plugin 也需要共用，可重新評估方案 A

## 考慮過的替代方案

| 方案 | 為何沒選 |
|------|---------|
| A：crew-common 共用 plugin | marketplace 多單元、使用者要多裝、安裝路徑變長 |
| C：保留跨 plugin 引用 | 違反「plugin 可獨立安裝」核心契約 |
| Symlink | git 在 Windows 對 symlink 支援差、且 plugin 安裝時可能不展開 |

## 更新紀錄

### 2026-07-13（C9：單一權威來源 + 同步腳本）

本決策（雙份副本 + CI 防漂移）維持不變——「plugin 可獨立安裝」契約不動，
兩 plugin 仍各帶實體副本，發佈物不變。C9 只改善「負面」中「更新時要手動 cp 一次」：

- 確立 `plugins/bug-workflow/references/` 為共用檔的**單一權威來源**
  （`prerequisites.md`、`db-templates.md` 原生於 bug-workflow，且 bug-workflow 較基礎）；
  `feature-workflow` 那份一律視為同步產物。
- 新增 `scripts/sync-shared-refs.sh`：以 bug-workflow 為準單向同步，支援 `--check`；
  把手動 cp 升級為一鍵/可檢查機制。
- `check-shared-refs.py`（CI sha256 檢查）維持為最後防線，錯誤訊息改為指向同步腳本。
- 共用檔清單同步時（2026-07-13 稍後）由 3 個增為 4 個：`notion-backend.md`
  因 reconciliation #80（feature 側 prerequisites 指向卻缺檔）修復而納入，
  以 sync/CI 機制防兩份漂移。清單以 CONTRIBUTING.md 與兩 script 為準。

未採 symlink / crew-common / pre-commit hook 的理由同下方「考慮過的替代方案」
與本次評估（pre-commit hook 需額外安裝、`.git/hooks` 不隨 repo、改變 commit 行為）。

## 相關

- CONTRIBUTING.md「共用 reference 同步規則」
- `scripts/sync-shared-refs.sh`（C9 單一權威同步）
- `scripts/check-shared-refs.py`
- `.github/workflows/lint.yml` 的 `shared-refs-consistency` job
