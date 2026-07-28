#!/usr/bin/env python3
"""Lint「叫 LLM 直接手寫狀態欄位」的殘留指示（.spec/ 瘦身重構的防回歸檢查）。

背景：CREW major 重構把 `.spec/{slug}/` 瘦身為 plan.md + state.json + deploy.sql。
狀態改由單一寫者 `scripts/crew-state.py` 負責，SKILL.md 不得再指示 LLM 手寫
`status:` 到 plan.md／README.md 的 frontmatter；`handoff.md`、`_index.md`
兩個檔名已廢除。本 lint 防止改寫完成後又被寫回來（防回歸）。

兩條規則：
  1. STATUS_WRITE    — 指示把 `status:` 寫進 plan.md／README.md：
                       同一行提及 README／plan.md，或該行本身就是 frontmatter 式
                       `status: 值`（範本區塊）
  2. DEPRECATED_FILE — 出現已廢除的 `handoff.md`／`_index.md` 字樣

掃描範圍：plugins/*/skills/**/SKILL.md 與 plugins/*/references/*.md

用法：
  python3 scripts/lint-state-writers.py            # advisory：列出違規與待清理清單，return 0
  python3 scripts/lint-state-writers.py --strict   # CI 用：非豁免檔有違規 return 1

退出碼：
  0 = 通過，或 advisory 模式
  1 = --strict 模式下有非豁免違規
"""

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

SKILL_GLOB = "plugins/*/skills/**/SKILL.md"
REFERENCE_GLOB = "plugins/*/references/*.md"

# --- 規則 1：status: 寫入 plan.md／README.md ---------------------------------
# 同一行提及 README／plan.md → 明確的「更新某檔的 status」指示
STATUS_WITH_TARGET_RE = re.compile(
    r"status\s*[:：].*?(README|plan\.md)|(README|plan\.md).*?status\s*[:：]",
    re.IGNORECASE,
)
# 行首（可含清單符號 / 引號）就是 frontmatter 式 `status: 值` → 範本區塊裡的欄位
STATUS_FRONTMATTER_RE = re.compile(r"^\s*[-*>]?\s*[\"'`]?status\s*[:：]\s*\S", re.IGNORECASE)

# --- 規則 2：已廢除的檔名 ----------------------------------------------------
DEPRECATED_FILES = ("handoff.md", "_index.md")
DEPRECATED_RE = re.compile(r"(handoff\.md|_index\.md)")

FIX_HINT = {
    "STATUS_WRITE": "改為呼叫單一寫者：`python3 scripts/crew-state.py set status=<值>`，不要叫 LLM 手寫欄位",
    "DEPRECATED_FILE": "已廢除的檔名；狀態一律讀寫 state.json（透過 crew-state.py），文件內容併入 plan.md",
}

# --- 例外清單 ----------------------------------------------------------------
# 過渡期已結束：重構階段 5–7 的 18 個暫時豁免已全部清掉，以下是**永久**豁免。
#
# 唯一合法的豁免理由是「刻意的新舊對照說明」—— 這些句子把 handoff.md 明確標示為
# 舊版做法，用來教「結案不刪除」這個容易搞錯的語意變更。拿掉反而讓人沿用舊習慣踩坑。
#
# 🔴 新增條目前先自問：這是「在教新舊差異」，還是「還沒改完」？
#    後者不得進本清單 —— 那會讓防線永久破洞。理由欄禁止寫「暫時」「之後再處理」。
# 格式：repo 相對路徑 → 為什麼這個檔案提到廢除檔名是正確的
# 維護提醒：檔案改寫後條目失效時，本 lint 會在結尾印「豁免已失效」提示（不阻擋 CI）。
EXEMPTIONS = {
    "plugins/bug-workflow/references/state-discipline.md":
        "新舊對照：說明 handoff.md 結案即刪、state.json 結案保留（語意變更需明講）",
    "plugins/feature-workflow/references/state-discipline.md":
        "同上（bug-workflow 的同步副本）",
    "plugins/bug-workflow/skills/bug-close/SKILL.md":
        "新舊對照：警告不要沿用舊習慣刪掉 state.json",
}


def rel(path: Path) -> str:
    return str(path.relative_to(REPO))


def scan(path: Path) -> list[tuple[int, str, str]]:
    """回傳 [(行號, 規則代號, 訊息)]。"""
    findings = []
    text = path.read_text(encoding="utf-8")
    for i, line in enumerate(text.split("\n"), start=1):
        if STATUS_WITH_TARGET_RE.search(line) or STATUS_FRONTMATTER_RE.match(line):
            findings.append(
                (i, "STATUS_WRITE", f"指示手寫狀態欄位：{line.strip()[:70]}")
            )
        m = DEPRECATED_RE.search(line)
        if m:
            findings.append(
                (i, "DEPRECATED_FILE", f"已廢除的檔名 `{m.group(1)}`：{line.strip()[:70]}")
            )
    return findings


def targets() -> list[Path]:
    seen = {}
    for pattern in (SKILL_GLOB, REFERENCE_GLOB):
        for p in REPO.glob(pattern):
            seen[rel(p)] = p
    return [seen[k] for k in sorted(seen)]


def main() -> int:
    strict = "--strict" in sys.argv

    violations: list[tuple[str, str]] = []   # 非豁免 → 阻擋，(訊息, 規則代號)
    pending: list[str] = []                  # 豁免中 → 待清理
    hit_files: set[str] = set()
    checked = 0

    for path in targets():
        checked += 1
        r = rel(path)
        for line_no, rule, msg in scan(path):
            hit_files.add(r)
            entry = f"{r}:{line_no} [{rule}] {msg}"
            if r in EXEMPTIONS:
                pending.append(entry)
            else:
                violations.append((entry, rule))

    marker = "❌" if strict else "⚠️ "
    for entry, rule in violations:
        print(f"{marker} {entry}")
        print(f"   修法：{FIX_HINT[rule]}")

    # 豁免已失效（檔案已改乾淨但條目還留著）→ 提示收斂清單，不阻擋
    stale = sorted(set(EXEMPTIONS) - hit_files)

    if not strict:
        if pending:
            print(f"\n📋 待清理清單（EXEMPTIONS 豁免中，共 {len(pending)} 處）：")
            for p in pending:
                print(f"   · {p}")
        for s in stale:
            print(f"\n💡 豁免已失效，可從 EXEMPTIONS 移除：{s}")

    scope = f"{checked} 個檔案（SKILL.md + references）"

    if violations:
        print(f"\n檢查 {scope}，{len(violations)} 個{'違規' if strict else '建議檢查項'}"
              f"，另有 {len(pending)} 處在 EXEMPTIONS 豁免中")
        if strict:
            print("狀態一律經 scripts/crew-state.py 單一寫者讀寫；過渡期可暫列 EXEMPTIONS")
            return 1
        print("（advisory 模式：不阻擋；CI 以 --strict 執行）")
        return 0

    print(f"✅ 檢查 {scope}，無非豁免的手寫狀態指示"
          f"（EXEMPTIONS 豁免 {len(EXEMPTIONS)} 個檔案／{len(pending)} 處待清理）")
    if strict and stale:
        print(f"💡 {len(stale)} 個豁免已失效，可從 EXEMPTIONS 移除："
              f"{'、'.join(stale)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
