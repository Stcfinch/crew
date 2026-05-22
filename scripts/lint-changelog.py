#!/usr/bin/env python3
"""Lint CHANGELOG.md 版本順序。

規則：
  1. 日期單調遞減（新版在上，舊版在下）
  2. 同一 plugin 內版本號單調遞減（不可 3.5.1 在 3.5.0 之前）
  3. 同日不同 plugin：feature-workflow 應在 bug-workflow 之前（沿用慣例）

退出碼：
  0 = 順序正確
  1 = 順序違規
"""

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CHANGELOG = REPO / "CHANGELOG.md"
PLUGIN_ORDER = {"feature-workflow": 0, "bug-workflow": 1}


def parse_entries(text: str) -> list[dict]:
    pattern = re.compile(
        r"^## \[([\w-]+)@(\d+)\.(\d+)\.(\d+)\] - (\d{4}-\d{2}-\d{2})",
        re.MULTILINE,
    )
    entries = []
    for m in pattern.finditer(text):
        plugin, major, minor, patch, date = m.groups()
        entries.append({
            "plugin": plugin,
            "version": (int(major), int(minor), int(patch)),
            "date": date,
            "line": text[:m.start()].count("\n") + 1,
        })
    return entries


def main() -> int:
    text = CHANGELOG.read_text(encoding="utf-8")
    entries = parse_entries(text)

    if not entries:
        print("❌ 找不到任何版本區塊（## [plugin@x.y.z] - YYYY-MM-DD）")
        return 1

    errors: list[str] = []

    # 1+3. 整體順序：日期倒序 → 同日 plugin order → 版本倒序
    for i in range(len(entries) - 1):
        cur, nxt = entries[i], entries[i + 1]
        # 日期：cur 必須 >= nxt
        if cur["date"] < nxt["date"]:
            errors.append(
                f"L{nxt['line']}: 日期回升 — {cur['plugin']}@{'.'.join(map(str, cur['version']))} "
                f"({cur['date']}) → {nxt['plugin']}@{'.'.join(map(str, nxt['version']))} ({nxt['date']})"
            )
            continue
        if cur["date"] == nxt["date"]:
            # 同日：先 plugin 順序，再版本倒序
            cp = PLUGIN_ORDER.get(cur["plugin"], 99)
            np = PLUGIN_ORDER.get(nxt["plugin"], 99)
            if cp > np:
                errors.append(
                    f"L{nxt['line']}: 同日 plugin 順序錯誤 — "
                    f"{cur['plugin']} 應在 {nxt['plugin']} 之後"
                )

    # 2. 同 plugin 版本單調遞減
    by_plugin: dict[str, list[dict]] = {}
    for e in entries:
        by_plugin.setdefault(e["plugin"], []).append(e)
    for plugin, lst in by_plugin.items():
        for i in range(len(lst) - 1):
            cur, nxt = lst[i], lst[i + 1]
            if cur["version"] <= nxt["version"]:
                errors.append(
                    f"L{nxt['line']}: {plugin} 版本未遞減 — "
                    f"{'.'.join(map(str, cur['version']))} → {'.'.join(map(str, nxt['version']))}"
                )

    for e in errors:
        print(f"❌ {e}")

    if errors:
        print(f"\nCHANGELOG.md 有 {len(errors)} 個順序違規")
        return 1

    print(f"✅ CHANGELOG.md 順序正確（{len(entries)} 個版本區塊）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
