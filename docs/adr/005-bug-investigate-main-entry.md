# ADR-005：為何 bug-investigate 取代 bug-start 為主入口

- 日期：2026-05-15（bug-workflow@3.8.0）
- 狀態：已採用（推翻原本 bug-start 為主入口的設計）

## 背景

原始設計：使用者發現 Bug 後依序執行：

```
/bug-start <問題簡述>     建立 Notion 條目
/bug-investigate          假說驅動根因調查
/bug-fix                  修復
/bug-close                結案
```

問題：
1. `bug-start` 與 `bug-investigate` 必須連續使用，但分兩步無附加價值
2. 大多數使用者忘記 `bug-start`，直接執行 `bug-investigate` 結果找不到目標 Bug 條目
3. 新使用者面對「先 start 還是 investigate」感到困惑
4. 90% 的真實使用都是「發現 Bug → 立即想知道為什麼」，建立條目應該是副作用而非起點

## 決策

讓 `/bug-investigate` 成為主入口：

- 執行 `/bug-investigate` 時若無對應 Notion 條目，**自動建立**（內含原 bug-start 邏輯）
- `/bug-start` 降為**可選**的「只想先建條目」入口（少數場景：分配給他人調查）
- README 流程圖將 bug-start 改為虛線可選路徑

## 後果

**正面**：
- 使用者直觀：發現 Bug → `/bug-investigate` → 自動建立 + 開始調查
- 減少「找不到 Bug 條目」的常見錯誤
- 文件流程圖更清晰（主路徑 → investigate → fix → close）

**負面**：
- 對既有使用者是行為變更（雖然 bug-start 仍存在）
- `/bug-investigate` skill 邏輯變複雜（含 bug-start 的職責）

**中性**：
- bug-start 沒有移除，向下相容；只是不再是「主入口」

## 考慮過的替代方案

| 方案 | 為何沒選 |
|------|---------|
| 強制保留 bug-start 為主入口 | 90% 使用者體驗仍是「找不到條目」失敗 |
| 完全移除 bug-start | 少數「先建條目給他人」場景仍需要 |
| 改名為 `/bug` 統一入口 | 名稱衝突、現有使用者習慣已建立 |

## 相關

- bug-workflow@3.8.0 CHANGELOG「investigate 為主入口」
- bug-investigate SKILL.md 的「定位目標 Bug」流程含自動建條目邏輯
