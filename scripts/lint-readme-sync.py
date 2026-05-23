#!/usr/bin/env python3
"""Lint：每個 SKILL.md 的 name 必須出現在根 README + 自家 plugin README。

避免「新增 skill 卻忘了同步 README 指令表」的常見遺漏（CONTRIBUTING.md 警告過）。

匹配規則：找 `/{name}` token，後面不可緊接字母/數字/連字符
（避免 /plan 誤 match /plan-build、/plan 誤 match /plan-spec 等）。

退出碼：
  0 = 所有 skill 都在兩處 README 出現
  1 = 有缺漏
"""

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def get_skill_name(skill_md: Path) -> str | None:
    text = skill_md.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        return None
    for line in m.group(1).split("\n"):
        if line.startswith("name:"):
            return line.split(":", 1)[1].strip()
    return None


def has_token(readme: str, name: str) -> bool:
    """檢查 /name 是否在 readme 中出現（精確匹配，不誤 match 較長名稱）"""
    pattern = rf"/{re.escape(name)}(?![a-zA-Z0-9_-])"
    return bool(re.search(pattern, readme))


def main() -> int:
    root_readme_path = REPO / "README.md"
    if not root_readme_path.exists():
        print("❌ 根 README.md 不存在")
        return 1
    root_readme = root_readme_path.read_text(encoding="utf-8")

    errors: list[str] = []
    checked = 0

    for skill_md in sorted(REPO.glob("plugins/*/skills/*/SKILL.md")):
        name = get_skill_name(skill_md)
        if not name:
            continue
        checked += 1

        plugin_name = skill_md.parts[-4]
        plugin_readme_path = REPO / "plugins" / plugin_name / "README.md"
        if not plugin_readme_path.exists():
            errors.append(
                f"{plugin_name}/README.md 不存在（skill: {name}）"
            )
            continue
        plugin_readme = plugin_readme_path.read_text(encoding="utf-8")

        if not has_token(root_readme, name):
            errors.append(f"根 README.md 缺 `/{name}` (skill: {skill_md.relative_to(REPO)})")
        if not has_token(plugin_readme, name):
            errors.append(
                f"{plugin_name}/README.md 缺 `/{name}` (skill: {skill_md.relative_to(REPO)})"
            )

    for e in errors:
        print(f"❌ {e}")

    if errors:
        print(f"\n檢查 {checked} 個 skill，{len(errors)} 個 README 缺漏")
        return 1
    print(f"✅ 檢查 {checked} 個 skill，全部在根 README + 自家 plugin README 中出現")
    return 0


if __name__ == "__main__":
    sys.exit(main())
