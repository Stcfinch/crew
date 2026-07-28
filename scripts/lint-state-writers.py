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

# --- 例外清單（重構過渡用）---------------------------------------------------
# ⚠️ 重構階段 5–7（改寫 SKILL.md）完成後須逐一移除，清空本清單為止。
#    本次 commit 只接線基礎設施，尚未改寫任何 SKILL.md，因此現有命中全數先豁免，
#    讓 CI 保持綠燈；每改寫完一個檔案就刪掉對應這一行，收緊防線。
# 格式：repo 相對路徑 → 待清理的原因摘要
# 維護提醒：檔案改寫完卻忘了刪除條目時，本 lint 會在結尾印「豁免已失效」提示
#          （不阻擋 CI），據此收斂清單。
EXEMPTIONS = {
    "plugins/bug-workflow/references/handoff-discipline.md": "handoff.md 字樣（階段 5–7 改寫）",
    "plugins/bug-workflow/skills/bug-close/SKILL.md": "handoff.md 字樣（階段 5–7 改寫）",
    "plugins/feature-workflow/references/handoff-discipline.md": "handoff.md 字樣（階段 5–7 改寫）",
    "plugins/feature-workflow/references/plan-common.md": "handoff.md／_index.md 字樣（階段 5–7 改寫）",
    "plugins/feature-workflow/skills/plan-arch/SKILL.md": "手寫 status:（階段 5–7 改寫）",
    "plugins/feature-workflow/skills/plan-build/SKILL.md": "手寫 status: 與 _index.md（階段 5–7 改寫）",
    "plugins/feature-workflow/skills/plan-close/SKILL.md": "手寫 status:、handoff.md、_index.md（階段 5–7 改寫）",
    "plugins/feature-workflow/skills/plan-db/SKILL.md": "手寫 status:（階段 5–7 改寫）",
    "plugins/feature-workflow/skills/plan-demo/SKILL.md": "手寫 status: 與 _index.md（階段 5–7 改寫）",
    "plugins/feature-workflow/skills/plan-deploy-confirm/SKILL.md": "手寫 status:（階段 5–7 改寫）",
    "plugins/feature-workflow/skills/plan-next/SKILL.md": "handoff.md／_index.md 字樣（階段 5–7 改寫）",
    "plugins/feature-workflow/skills/plan-review/SKILL.md": "手寫 status: 與 _index.md（階段 5–7 改寫）",
    "plugins/feature-workflow/skills/plan-security/SKILL.md": "手寫 status: 與 _index.md（階段 5–7 改寫）",
    "plugins/feature-workflow/skills/plan-spec/SKILL.md": "手寫 status:（階段 5–7 改寫）",
    "plugins/feature-workflow/skills/plan-start/SKILL.md": "手寫 status: 與 _index.md（階段 5–7 改寫）",
    "plugins/feature-workflow/skills/plan-status/SKILL.md": "_index.md 字樣（階段 5–7 改寫）",
    "plugins/feature-workflow/skills/plan-sync/SKILL.md": "手寫 status:（階段 5–7 改寫）",
    "plugins/feature-workflow/skills/plan-verify/SKILL.md": "手寫 status: 與 _index.md（階段 5–7 改寫）",
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
