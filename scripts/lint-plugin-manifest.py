#!/usr/bin/env python3
"""Lint plugin.json / marketplace.json 的宣告是否與實際檔案相符。

存在的理由：
  其餘 lint 腳本（lint-skills.py、lint-readme-sync.py、lint-skill-contract.py）
  一律以「掃 plugins/*/skills/*/ 實際目錄」為基準，沒有任何一支比對
  plugin.json 的 skills 陣列，因此「陣列與目錄不一致」是 CI 的檢查盲區。
  feature-workflow@5.0.0 刪掉 plan-spec / plan-db / plan-arch 三個目錄卻沒同步
  陣列，導致 Claude Code 載入時報 `skills path not found`，該問題存活 37 天
  （2026-07-28 → 2026-09-03）都沒被 CI 攔下。本腳本補上這個維度。

檢查項目（全部 fail，無警告級）：
  1. skills 陣列宣告的路徑，實際目錄不存在
  2. skills/ 下實際存在的目錄，未被 skills 陣列宣告
  3. skills 陣列有重複宣告
  4. 宣告的 skill 目錄缺少 SKILL.md 或其內容為空
  5. hooks 欄位指向的檔案不存在
  6. marketplace.json 的 source 目錄不存在，或與 plugins/ 下實際 plugin 未一一對應

退出碼：
  0 = 無錯誤
  1 = 有錯誤
"""

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PLUGINS_DIR = REPO / "plugins"
MARKETPLACE_JSON = REPO / ".claude-plugin" / "marketplace.json"


def lint_plugin(plugin_dir: Path, errors: list[str]) -> int:
    """檢查單一 plugin 的 manifest，回傳檢查過的 skill 宣告數。"""
    manifest = plugin_dir / ".claude-plugin" / "plugin.json"
    rel = manifest.relative_to(REPO)

    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{rel}: JSON 解析失敗 —— {exc}")
        return 0

    declared = data.get("skills", [])
    if not isinstance(declared, list):
        errors.append(f"{rel}: skills 欄位必須是陣列")
        return 0

    # 1 + 4：宣告的路徑要存在，且要有非空 SKILL.md
    for entry in declared:
        target = plugin_dir / entry
        if not target.is_dir():
            errors.append(
                f"{rel}: skills 宣告 `{entry}` 但目錄不存在"
                f"（Claude Code 載入時會報 skills path not found）"
            )
            continue
        skill_md = target / "SKILL.md"
        if not skill_md.is_file():
            errors.append(f"{rel}: `{entry}` 缺少 SKILL.md")
        elif not skill_md.read_text(encoding="utf-8").strip():
            errors.append(f"{rel}: `{entry}/SKILL.md` 內容為空")

    declared_names = [entry.rstrip("/").split("/")[-1] for entry in declared]

    # 2：實際存在但未宣告
    skills_dir = plugin_dir / "skills"
    if skills_dir.is_dir():
        for child in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
            if child.name not in declared_names:
                errors.append(
                    f"{rel}: `skills/{child.name}/` 實際存在但 skills 陣列未宣告"
                )

    # 3：重複宣告
    for name in sorted(set(declared_names)):
        count = declared_names.count(name)
        if count > 1:
            errors.append(f"{rel}: skills 陣列重複宣告 `{name}` {count} 次")

    # 5：hooks 路徑
    hooks = data.get("hooks")
    if isinstance(hooks, str) and not (plugin_dir / hooks).is_file():
        errors.append(f"{rel}: hooks 宣告 `{hooks}` 但檔案不存在")

    return len(declared)


def lint_marketplace(plugin_dirs: list[Path], errors: list[str]) -> None:
    """檢查 marketplace.json 的 source 與 plugins/ 一一對應。"""
    rel = MARKETPLACE_JSON.relative_to(REPO)
    try:
        data = json.loads(MARKETPLACE_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{rel}: JSON 解析失敗 —— {exc}")
        return

    listed: set[str] = set()
    for entry in data.get("plugins", []):
        source = entry.get("source", "")
        target = (REPO / source).resolve() if source else None
        if target is None or not target.is_dir():
            errors.append(
                f"{rel}: plugin `{entry.get('name')}` 的 source `{source}` 目錄不存在"
            )
            continue
        listed.add(target.name)

    actual = {d.name for d in plugin_dirs}
    for name in sorted(actual - listed):
        errors.append(f"{rel}: `plugins/{name}/` 存在但 marketplace.json 未列出")
    for name in sorted(listed - actual):
        errors.append(f"{rel}: marketplace.json 列出 `{name}` 但 plugins/ 下無此目錄")


def main() -> int:
    errors: list[str] = []
    plugin_dirs = sorted(
        d for d in PLUGINS_DIR.iterdir()
        if d.is_dir() and (d / ".claude-plugin" / "plugin.json").is_file()
    )

    total_skills = 0
    for plugin_dir in plugin_dirs:
        total_skills += lint_plugin(plugin_dir, errors)

    lint_marketplace(plugin_dirs, errors)

    for e in errors:
        print(f"❌ {e}")

    if errors:
        print(f"\n檢查 {len(plugin_dirs)} 個 plugin manifest：{len(errors)} 錯誤")
        return 1

    print(
        f"✅ 檢查 {len(plugin_dirs)} 個 plugin manifest、"
        f"{total_skills} 個 skill 宣告，與實際檔案完全相符"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
