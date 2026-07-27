#!/usr/bin/env python3
"""檢查兩個 plugin 的共用 reference 檔案沒有漂移。

bug-workflow 與 feature-workflow 各自帶一份 prerequisites.md / db-templates.md
（為了 plugin 可獨立安裝），用 sha256 強制兩份完全一致，否則 CI fail。

當其中一份要更新時，正確做法是同時改兩份；本檢查防止漏改。

退出碼：
  0 = 所有共用 reference 在兩 plugin 中內容一致
  1 = 任一份漂移或缺失
"""

import hashlib
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

SHARED_REFS = [
    "references/prerequisites.md",
    "references/db-templates.md",
    "references/discipline-preamble.md",
    "references/notion-backend.md",
    "references/handoff-discipline.md",
    "references/model-policy.md",
]

PLUGIN_A = "bug-workflow"
PLUGIN_B = "feature-workflow"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    rc = 0
    for ref in SHARED_REFS:
        a = REPO / "plugins" / PLUGIN_A / ref
        b = REPO / "plugins" / PLUGIN_B / ref

        if not a.exists():
            print(f"❌ 缺失：{a.relative_to(REPO)}")
            rc = 1
            continue
        if not b.exists():
            print(f"❌ 缺失：{b.relative_to(REPO)}")
            rc = 1
            continue

        ha = sha256(a)
        hb = sha256(b)

        if ha == hb:
            print(f"✅ {ref} 兩 plugin 內容一致")
        else:
            print(f"❌ {ref} 兩 plugin 內容不同：")
            print(f"   {PLUGIN_A:>20}: {ha[:12]}...")
            print(f"   {PLUGIN_B:>20}: {hb[:12]}...")
            print(f"   修法：只改 bug-workflow 那份（權威），再跑 ./scripts/sync-shared-refs.sh 同步")
            rc = 1

    return rc


if __name__ == "__main__":
    sys.exit(main())
