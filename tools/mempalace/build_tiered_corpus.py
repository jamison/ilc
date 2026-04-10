#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable

DEFAULT_MANIFEST = Path("docs/tools/mempalace/ilc_mempalace_corpus_manifest_v0.1.json")
REPO_ROOT = Path(__file__).resolve().parents[2]
VALID_MODES = {"copy", "symlink"}


def load_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _safe_remove(path: Path) -> None:
    if path.exists() or path.is_symlink():
        if path.is_dir() and not path.is_symlink():
            shutil.rmtree(path)
        else:
            path.unlink()


def write_tier_config(tier_dir: Path, tier_name: str) -> None:
    config = (
        f"wing: {tier_name}\n"
        "rooms:\n"
        "  - name: general\n"
        f"    description: staged {tier_name} corpus\n"
    )
    (tier_dir / "mempalace.yaml").write_text(config, encoding="utf-8")


def stage_manifest(
    manifest: dict,
    *,
    repo_root: Path,
    staged_root: Path,
    mode: str,
    tiers: Iterable[str] | None = None,
) -> dict:
    if mode not in VALID_MODES:
        raise ValueError(f"invalid_mode:{mode}")
    selected = list(tiers) if tiers else list(manifest["tiers"].keys())
    summary: dict[str, dict] = {}
    staged_root.mkdir(parents=True, exist_ok=True)

    for tier_name in selected:
        tier = manifest["tiers"][tier_name]
        tier_dir = staged_root / tier_name
        tier_dir.mkdir(parents=True, exist_ok=True)
        write_tier_config(tier_dir, tier_name)
        staged_files: list[str] = []
        for rel in tier.get("include", []):
            src = (repo_root / rel).resolve()
            if not src.exists():
                raise FileNotFoundError(f"missing_manifest_source:{rel}")
            dst = tier_dir / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            _safe_remove(dst)
            if mode == "copy":
                shutil.copy2(src, dst)
            else:
                os.symlink(src, dst)
            staged_files.append(str(dst.relative_to(staged_root)))
        summary[tier_name] = {
            "tier_dir": str(tier_dir),
            "file_count": len(staged_files),
            "staged_files": staged_files,
        }
    return summary


def build_mine_commands(mempalace_bin: str, palace_path: Path, staged_root: Path, tiers: Iterable[str]) -> list[list[str]]:
    commands: list[list[str]] = []
    for tier_name in tiers:
        tier_dir = staged_root / tier_name
        commands.append(
            [
                mempalace_bin,
                "--palace",
                str(palace_path),
                "mine",
                str(tier_dir),
                "--wing",
                tier_name,
                "--no-gitignore",
            ]
        )
    return commands


def run_mine_commands(commands: list[list[str]]) -> None:
    for cmd in commands:
        subprocess.run(cmd, check=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build and mine a staged tiered MemPalace corpus.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--staged-root", type=Path, required=True)
    parser.add_argument("--palace", type=Path, required=True)
    parser.add_argument("--mode", choices=sorted(VALID_MODES), default="copy")
    parser.add_argument("--mempalace", default="mempalace")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--tier", action="append", dest="tiers")
    parser.add_argument("--clean", action="store_true")
    parser.add_argument("--no-mine", action="store_true")
    args = parser.parse_args(argv)

    manifest = load_manifest(args.manifest)
    tiers = args.tiers or list(manifest["tiers"].keys())
    for tier_name in tiers:
        if tier_name not in manifest["tiers"]:
            raise SystemExit(f"unknown_tier:{tier_name}")

    if args.clean:
        _safe_remove(args.staged_root)
        _safe_remove(args.palace)

    summary = stage_manifest(
        manifest,
        repo_root=args.repo_root,
        staged_root=args.staged_root,
        mode=args.mode,
        tiers=tiers,
    )
    commands = build_mine_commands(args.mempalace, args.palace, args.staged_root, tiers)
    if not args.no_mine:
        run_mine_commands(commands)

    payload = {
        "manifest": str(args.manifest),
        "staged_root": str(args.staged_root),
        "palace": str(args.palace),
        "mode": args.mode,
        "tiers": tiers,
        "summary": summary,
        "commands": commands,
        "mined": not args.no_mine,
    }
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
