#!/usr/bin/env python3
"""Install this checkout's Codex payload into the personal marketplace (stdlib only)."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

SOURCE = Path(__file__).resolve().parents[1]


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def install(home, update=False, enable=True, dry_run=False):
    home = home.expanduser().resolve()
    parent = home / "plugins"
    target = parent / "crew"
    market = home / ".agents" / "plugins" / "marketplace.json"
    if parent.resolve() != parent or target.resolve() != target:
        raise ValueError("Plugin parent/target must not be a symlink or junction")
    if not market.resolve().is_relative_to(home):
        raise ValueError("Marketplace must stay within the chosen home directory")
    if target == SOURCE or SOURCE.is_relative_to(target):
        raise ValueError("Install target would overlap the source checkout")
    manifest = read_json(SOURCE / ".codex-plugin" / "plugin.json")
    if manifest.get("name") != "crew" or manifest.get("skills") != "./skills/":
        raise ValueError("Unexpected CREW manifest")
    skills = list((SOURCE / "skills").glob("*/SKILL.md"))
    if len(skills) != 27:
        raise ValueError("Incomplete payload: expected 27 skills")
    for folder in (SOURCE / ".codex-plugin", SOURCE / "skills", SOURCE / "codex"):
        for item in folder.rglob("*"):
            if item.is_symlink() or not item.resolve().is_relative_to(folder.resolve()):
                raise ValueError(f"Payload must be self-contained: {item}")
    catalog = read_json(market) if market.exists() else {
        "name": "personal", "interface": {"displayName": "Personal"}, "plugins": []}
    if not isinstance(catalog, dict) or not re.fullmatch(r"[A-Za-z0-9_-]+", str(catalog.get("name", ""))):
        raise ValueError("Invalid personal marketplace name")
    entries = catalog.get("plugins")
    if not isinstance(entries, list) or any(not isinstance(e, dict) for e in entries):
        raise ValueError("Invalid marketplace plugins list")
    matches = [entry for entry in entries if entry.get("name") == "crew"]
    if len(matches) > 1:
        raise ValueError("Duplicate crew entries in marketplace")
    marker = target / ".crew-install.json"
    if target.exists() or matches:
        if not update:
            raise ValueError("CREW already exists; use --update after reviewing the source")
        if not marker.is_file() or read_json(marker).get("source") != str(SOURCE):
            raise ValueError("Existing crew was not installed from this checkout; refusing to overwrite")
        if not matches or matches[0].get("source") != {"source": "local", "path": "./plugins/crew"}:
            raise ValueError("Marketplace source does not match this local install")
    entry = {"name": "crew", "source": {"source": "local", "path": "./plugins/crew"},
             "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
             "category": "Productivity"}
    if not matches:
        entries.append(entry)
    # Existing entries and their policy/order are preserved on update.
    codex = shutil.which("codex")
    if enable and not codex:
        raise ValueError("codex CLI not on PATH; use --no-enable to stage only")
    selector = "crew@" + catalog["name"]
    print(f"Source: {SOURCE}\nPlugin: {target}\nMarketplace: {market}\nInstall: {selector}")
    if dry_run:
        return 0
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    manifest["version"] = manifest["version"].split("+", 1)[0] + "+codex." + stamp
    parent.mkdir(parents=True, exist_ok=True)
    backup = parent / ("crew.backup-" + stamp)
    with tempfile.TemporaryDirectory(prefix=".crew-stage-", dir=parent) as temporary:
        staging = Path(temporary) / "crew"
        for folder in (".codex-plugin", "skills", "codex"):
            shutil.copytree(SOURCE / folder, staging / folder,
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        write_json(staging / ".codex-plugin" / "plugin.json", manifest)
        write_json(staging / ".crew-install.json", {"source": str(SOURCE), "installed_at": stamp})
        market.parent.mkdir(parents=True, exist_ok=True)
        market_backup = market.with_name("marketplace.backup-" + stamp + ".json")
        if market.exists():
            shutil.copy2(market, market_backup)
        if target.exists():
            # Both absolute paths are verified under the intended plugins parent.
            if target.parent.resolve() != parent.resolve() or backup.parent.resolve() != parent.resolve():
                raise ValueError("Unsafe backup target")
            target.rename(backup)
        try:
            staging.rename(target)
            # Use a unique sibling temp file; never overwrite a preexisting temp link.
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=market.parent,
                                             prefix="marketplace-", suffix=".tmp", delete=False) as handle:
                json.dump(catalog, handle, ensure_ascii=False, indent=2)
                handle.write("\n")
                temp_market = Path(handle.name)
            os.replace(temp_market, market)
        except Exception:
            print(f"Install interrupted. Preserve {target}; previous plugin backup: {backup}", file=sys.stderr)
            raise
    if backup.exists():
        print(f"Previous plugin backup: {backup}")
    if enable:
        result = subprocess.run([codex, "plugin", "add", selector, "--json"])
        if result.returncode:
            print("Payload staged, but Codex activation failed. Check the error before retrying.", file=sys.stderr)
            return result.returncode
        print("Installed. Open a new Codex task to load CREW skills.")
    else:
        print("Staged only; Codex activation was not performed.")
    return 0


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", type=Path, default=Path.home(), help="Personal marketplace owner home")
    parser.add_argument("--update", action="store_true", help="Update this checkout's existing install with backup")
    parser.add_argument("--no-enable", action="store_true", help="Stage payload/catalog without invoking Codex")
    parser.add_argument("--dry-run", action="store_true", help="Validate and print paths without writing")
    args = parser.parse_args(argv)
    try:
        return install(args.home, args.update, not args.no_enable, args.dry_run)
    except (ValueError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
