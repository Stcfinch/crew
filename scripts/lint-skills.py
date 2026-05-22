#!/usr/bin/env python3
"""Lint 所有 SKILL.md 檔案。

檢查項目：
  1. frontmatter 必須有 name + description（缺則 fail）
  2. 行數 > 1200（fail，遠超公司規範 800 max）
  3. 行數 > 800（warn，建議拆分）

退出碼：
  0 = 無錯誤（可有警告）
  1 = 有錯誤
"""

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILL_GLOB = "plugins/*/skills/*/SKILL.md"
MAX_FAIL = 1200
MAX_WARN = 800


def parse_frontmatter(text: str) -> dict | None:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        return None
    fm = {}
    for line in m.group(1).split("\n"):
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    checked = 0

    for skill_md in sorted(REPO.glob(SKILL_GLOB)):
        rel = skill_md.relative_to(REPO)
        text = skill_md.read_text(encoding="utf-8")
        lines = text.count("\n") + 1
        checked += 1

        fm = parse_frontmatter(text)
        if fm is None:
            errors.append(f"{rel}: 缺少 frontmatter 區塊（---...---）")
        else:
            for key in ("name", "description"):
                if key not in fm or not fm[key]:
                    errors.append(f"{rel}: frontmatter 缺少必填欄位 `{key}`")

        if lines > MAX_FAIL:
            errors.append(
                f"{rel}: 行數 {lines} 超過上限 {MAX_FAIL}（請拆分）"
            )
        elif lines > MAX_WARN:
            warnings.append(
                f"{rel}: 行數 {lines} > {MAX_WARN}（建議拆分為 phases/*.md）"
            )

    for w in warnings:
        print(f"⚠️  {w}")
    for e in errors:
        print(f"❌ {e}")

    summary = f"\n檢查 {checked} 個 SKILL.md：{len(errors)} 錯誤 / {len(warnings)} 警告"
    print(summary)

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
