#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pickle
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable

DEFAULT_MANIFEST = Path("docs/tools/mempalace/ilc_mempalace_corpus_manifest_v0.1.json")
REPO_ROOT = Path(__file__).resolve().parents[2]
VALID_MODES = {"copy", "symlink"}
DEFAULT_TMPDIR = REPO_ROOT / "out" / "mempalace_tmp"
HASH_SIDECAR_NAME = ".ilc_content_hashes.json"
BM25_INDEX_NAME = ".ilc_bm25_index.pkl"
# Only read this many bytes per file when building BM25 tokens (large files
# would dominate memory; 200 KB is ample for scoring and snippet extraction).
BM25_READ_LIMIT = 200_000


# ---------------------------------------------------------------------------
# Content-hash sidecar helpers
# ---------------------------------------------------------------------------

def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_hash_sidecar(palace: Path) -> dict[str, str]:
    sidecar = palace / HASH_SIDECAR_NAME
    if sidecar.exists():
        try:
            return json.loads(sidecar.read_text(encoding="utf-8")).get("hashes", {})
        except Exception:
            return {}
    return {}


def _save_hash_sidecar(palace: Path, hashes: dict[str, str]) -> None:
    palace.mkdir(parents=True, exist_ok=True)
    sidecar = palace / HASH_SIDECAR_NAME
    sidecar.write_text(
        json.dumps({"version": "1", "hashes": hashes}, indent=2, sort_keys=True),
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# BM25 index helpers
# ---------------------------------------------------------------------------

def _tokenize(text: str) -> list[str]:
    # Preserve ILC-specific compound tokens: CDL-044, ADR-0029, v5.0, rc0_1
    return re.findall(r"[a-z0-9][a-z0-9\-_.]*", text.lower())


def _build_bm25_index(palace: Path, staged_root: Path, tiers: list[str]) -> None:
    try:
        from rank_bm25 import BM25Okapi  # type: ignore
    except ImportError:
        print(
            "rank_bm25 not installed — skipping BM25 index (add rank-bm25 to requirements)",
            file=sys.stderr,
        )
        return

    corpus_tokens: list[list[str]] = []
    corpus_meta: list[dict] = []

    for tier_name in tiers:
        tier_dir = staged_root / tier_name
        if not tier_dir.is_dir():
            continue
        for f in sorted(tier_dir.rglob("*")):
            if not f.is_file() or f.name == "mempalace.yaml":
                continue
            try:
                raw = f.read_bytes()[:BM25_READ_LIMIT]
                text = raw.decode("utf-8", errors="replace")
            except Exception:
                continue
            tokens = _tokenize(text)
            if not tokens:
                continue
            # source_file: path relative to tier_dir, matching ChromaDB source_file metadata
            try:
                source_file = str(f.relative_to(tier_dir))
            except ValueError:
                source_file = str(f)
            corpus_tokens.append(tokens)
            corpus_meta.append({
                "source_file": source_file,
                "wing": tier_name,
                "snippet": text[:400].strip(),
            })

    if not corpus_tokens:
        print("BM25: no documents found — index not written", file=sys.stderr)
        return

    bm25 = BM25Okapi(corpus_tokens)
    index_path = palace / BM25_INDEX_NAME
    palace.mkdir(parents=True, exist_ok=True)
    with index_path.open("wb") as fh:
        pickle.dump({"meta": corpus_meta, "bm25": bm25}, fh, protocol=4)

    print(
        f"BM25 index: {len(corpus_tokens)} documents → {index_path}",
        file=sys.stderr,
    )


# ---------------------------------------------------------------------------
# Manifest staging
# ---------------------------------------------------------------------------

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


def expand_dir_include(tier_name: str, entry: dict, repo_root: Path) -> list[tuple[str, bool]]:
    """Expand a {'dir': ..., 'glob': ...} manifest entry into (rel_path, optional) pairs."""
    dir_rel = entry.get("dir", "").rstrip("/")
    if not dir_rel:
        raise ValueError(f"invalid_manifest_include:{tier_name}:missing_dir")
    glob_pat = entry.get("glob", "**/*")
    optional = bool(entry.get("optional", False))
    dir_path = (repo_root / dir_rel).resolve()
    if not dir_path.is_dir():
        if optional:
            return []
        raise FileNotFoundError(f"missing_manifest_dir:{dir_rel}")
    return [
        (str(f.relative_to(repo_root)), optional)
        for f in sorted(dir_path.glob(glob_pat))
        if f.is_file()
    ]


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
    known_hashes: dict[str, str] | None = None,
) -> tuple[dict, dict[str, str]]:
    """Stage manifest files. Returns (summary, updated_hashes).

    When known_hashes is provided, files whose SHA-256 matches the stored hash
    are skipped (incremental mode). updated_hashes contains hashes for all
    files that were staged this run, merged with known_hashes.
    """
    if mode not in VALID_MODES:
        raise ValueError(f"invalid_mode:{mode}")
    selected = list(tiers) if tiers else list(manifest["tiers"].keys())
    summary: dict[str, dict] = {}
    new_hashes: dict[str, str] = dict(known_hashes or {})
    staged_root.mkdir(parents=True, exist_ok=True)

    for tier_name in selected:
        tier = manifest["tiers"][tier_name]
        if "include" not in tier:
            raise ValueError(f"tier_missing_include:{tier_name}")
        tier_dir = staged_root / tier_name
        tier_dir.mkdir(parents=True, exist_ok=True)
        write_tier_config(tier_dir, tier_name)
        staged_files: list[str] = []
        skipped_files: list[str] = []
        warnings: list[str] = []

        for entry in tier["include"]:
            if isinstance(entry, dict) and "dir" in entry:
                file_pairs = expand_dir_include(tier_name, entry, repo_root)
            else:
                rel, optional = normalize_include_entry(tier_name, entry)
                file_pairs = [(rel, optional)]

            for rel, optional in file_pairs:
                src = (repo_root / rel).resolve()
                if not src.exists():
                    if optional:
                        warnings.append(f"missing_optional_manifest_source:{rel}")
                        continue
                    raise FileNotFoundError(f"missing_manifest_source:{rel}")

                # Incremental skip: compare content hash
                if known_hashes is not None:
                    current_hash = _sha256_file(src)
                    if known_hashes.get(rel) == current_hash:
                        skipped_files.append(rel)
                        continue
                    new_hashes[rel] = current_hash
                else:
                    new_hashes[rel] = _sha256_file(src)

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
            "skipped_unchanged": len(skipped_files),
            "staged_files": staged_files,
            "warnings": warnings,
        }

    return summary, new_hashes


# ---------------------------------------------------------------------------
# Mining
# ---------------------------------------------------------------------------

def build_mine_commands(
    mempalace_bin: str, palace_path: Path, staged_root: Path, tiers: Iterable[str]
) -> list[list[str]]:
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


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build and mine a staged tiered MemPalace corpus.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--staged-root", type=Path, required=True)
    parser.add_argument("--palace", type=Path, required=True)
    parser.add_argument("--mode", choices=sorted(VALID_MODES), default="copy")
    parser.add_argument("--mempalace", default="mempalace")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--tier", action="append", dest="tiers")
    parser.add_argument("--clean", action="store_true",
                        help="Wipe staged root and palace before building.")
    parser.add_argument("--incremental", action="store_true",
                        help="Skip files whose SHA-256 matches the stored hash sidecar. "
                             "Ignored when --clean is also passed.")
    parser.add_argument("--no-mine", action="store_true")
    parser.add_argument("--no-bm25", action="store_true",
                        help="Skip BM25 index build.")
    args = parser.parse_args(argv)

    manifest = load_manifest(args.manifest)
    tmpdir = ensure_tmpdir()
    tiers = args.tiers or list(manifest["tiers"].keys())
    for tier_name in tiers:
        if tier_name not in manifest["tiers"]:
            raise SystemExit(f"unknown_tier:{tier_name}")

    # --clean wipes everything; --incremental is then moot
    incremental = args.incremental and not args.clean
    if args.clean:
        _safe_remove(args.staged_root)
        _safe_remove(args.palace)

    known_hashes: dict[str, str] | None = None
    if incremental:
        known_hashes = _load_hash_sidecar(args.palace)
        loaded = len(known_hashes)
        print(f"Incremental mode: {loaded} known hashes loaded from sidecar", file=sys.stderr)

    summary, new_hashes = stage_manifest(
        manifest,
        repo_root=args.repo_root,
        staged_root=args.staged_root,
        mode=args.mode,
        tiers=tiers,
        known_hashes=known_hashes,
    )

    # In incremental mode, only run mine on tiers that actually staged new files
    mine_tiers = tiers
    if incremental:
        mine_tiers = [t for t in tiers if summary[t]["file_count"] > 0]
        skipped_total = sum(summary[t]["skipped_unchanged"] for t in tiers)
        staged_total = sum(summary[t]["file_count"] for t in tiers)
        print(
            f"Incremental: {staged_total} changed/new, {skipped_total} unchanged (skipped)",
            file=sys.stderr,
        )

    commands = build_mine_commands(args.mempalace, args.palace, args.staged_root, mine_tiers)
    if not args.no_mine:
        if commands:
            run_mine_commands(commands, os.environ.copy())
        else:
            print("No changed files — nothing to mine.", file=sys.stderr)

    # Persist hash sidecar so future incremental runs can diff
    _save_hash_sidecar(args.palace, new_hashes)

    # Build BM25 index over the full staged corpus (not just the delta)
    if not args.no_mine and not args.no_bm25:
        _build_bm25_index(args.palace, args.staged_root, tiers)

    payload = {
        "manifest": str(args.manifest),
        "staged_root": str(args.staged_root),
        "palace": str(args.palace),
        "tmpdir": str(tmpdir),
        "mode": args.mode,
        "incremental": incremental,
        "tiers": tiers,
        "summary": summary,
        "commands": commands,
        "mined": not args.no_mine,
        "bm25_built": not args.no_mine and not args.no_bm25,
    }
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
