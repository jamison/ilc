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
DEFAULT_TMPDIR = REPO_ROOT / "out" / "mempalace_tmp"


def load_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def ensure_tmpdir() -> Path:
    tmpdir = Path(os.environ.get("ILC_MEMPALACE_TMPDIR", os.environ.get("TMPDIR", str(DEFAULT_TMPDIR))))
    tmpdir.mkdir(parents=True, exist_ok=True)
    os.environ["TMPDIR"] = str(tmpdir)
    return tmpdir


def normalize_include_entry(tier_name: str, entry: str | dict) -> tuple[str, bool]:
    if isinstance(entry, str):
        return entry, False
    if isinstance(entry, dict):
        if "path" not in entry:
            raise ValueError(f"invalid_manifest_include:{tier_name}:missing_path")
        path = entry["path"]
        optional = bool(entry.get("optional", False))
        if not isinstance(path, str) or not path.strip():
            raise ValueError(f"invalid_manifest_include:{tier_name}:bad_path")
        return path, optional
    raise ValueError(f"invalid_manifest_include:{tier_name}:unsupported_entry_type")


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
        if "include" not in tier:
            raise ValueError(f"tier_missing_include:{tier_name}")
        tier_dir = staged_root / tier_name
        tier_dir.mkdir(parents=True, exist_ok=True)
        write_tier_config(tier_dir, tier_name)
        staged_files: list[str] = []
        warnings: list[str] = []
        for entry in tier["include"]:
            rel, optional = normalize_include_entry(tier_name, entry)
            src = (repo_root / rel).resolve()
            if not src.exists():
                if optional:
                    warnings.append(f"missing_optional_manifest_source:{rel}")
                    continue
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
            "warnings": warnings,
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


def run_mine_commands(commands: list[list[str]], env: dict[str, str]) -> None:
    for cmd in commands:
        subprocess.run(cmd, check=True, env=env)


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
    tmpdir = ensure_tmpdir()
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
        run_mine_commands(commands, os.environ.copy())

    payload = {
        "manifest": str(args.manifest),
        "staged_root": str(args.staged_root),
        "palace": str(args.palace),
        "tmpdir": str(tmpdir),
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
