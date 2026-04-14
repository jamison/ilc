from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest

from ilc_core.ledger.canon_bundle_key_registry_bundle import build_registry_bundle
from ilc_core.ledger.canon_bundle_key_registry_channel_signing import sign_channel_file
from ilc_core.ledger.canon_bundle_key_registry_promotion import promote_bundle
from ilc_core.ledger.canon_bundle_key_registry_sync import SyncContext, sync_channel_registry


FIX_DOC_PATH = Path("docs/specs/ilc_registry_channel_sync_reproducibility_fix_657_v0.1.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
TEST_PATH = Path("tests/test_phase_657_registry_channel_promotion_sync_reproducibility.py")
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_657_g8_registry_channel_promotion_sync_reproducibility_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
PHASE_657_SUBJECT_TOKEN = (
    "phase 657 registry channel promotion sync reproducibility"
)
PHASE_657_BACKFILL_SUBJECT_TOKEN = "phase 657 walkthrough and status backfill"
EXACT_REQUIRED_MAIN_PATHS = {
    str(FIX_DOC_PATH),
    str(TEST_PATH),
    "ilc_core/ledger/canon_bundle_key_registry_bundle.py",
    "ilc_core/ledger/canon_bundle_key_registry_channel.py",
    "ilc_core/ledger/canon_bundle_key_registry_channel_signing.py",
    "ilc_core/ledger/canon_bundle_key_registry_promotion.py",
    "ilc_core/ledger/canon_bundle_key_registry_sync.py",
    "tests/test_canon_bundle_key_registry_bundle.py",
    "tests/test_canon_bundle_key_registry_channel.py",
    "tests/test_canon_bundle_key_registry_channel_signing.py",
    "tests/test_canon_bundle_key_registry_promotion.py",
    "tests/test_canon_bundle_key_registry_sync.py",
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_HEADINGS = (
    "## 1. Remaining helper-level bug class",
    "## 2. Deterministic and explicit timestamp contracts",
    "## 3. Diagnostic metadata versus signed identity",
    "## 4. Verification compatibility and preserved boundaries",
)
REQUIRED_TOKENS = (
    "registry_channel_helper_reproducibility_fixed_in_657",
    "promotion_and_sync_timestamp_discipline_fixed_in_657",
    "diagnostic_metadata_separated_from_signed_identity_in_657",
    "filename_uniqueness_preserved_without_signed_state_pollution",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _find_commit_ref(*, subject_token: str) -> str | None:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if subject_token in subject.lower():
            return commit_hash
    return None


def _resolve_commit_ref(*, subject_token: str, expected_paths: set[str]) -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    matches: list[str] = []
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if subject_token not in subject.lower():
            continue
        matches.append(commit_hash)
    for commit_ref in matches:
        if _changed_paths_for_commit(commit_ref) == expected_paths:
            return commit_ref
    raise AssertionError(f"commit_not_present_in_local_history:{subject_token}")


def _require_commit_or_skip(subject_token: str) -> None:
    if _find_commit_ref(subject_token=subject_token) is None:
        pytest.skip(f"commit_not_yet_present:{subject_token}")


def _write_registry(tmp_path: Path) -> tuple[Path, bytes]:
    registry_path = tmp_path / "registry.json"
    registry_path.write_text(
        json.dumps(
            {
                "registry_version": "v0.1",
                "updated_at": "2026-04-14T10:00:00Z",
                "current_keys": ["a1b2c3d4e5f6a7b8"],
                "previous_keys": [],
                "deprecated_keys": [],
            }
        ),
        encoding="utf-8",
    )
    return registry_path, b"phase-657-registry-key"


def test_fix_doc_exists_contains_required_headings() -> None:
    text = _read(FIX_DOC_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_fix_doc_contains_required_tokens() -> None:
    text = _read(FIX_DOC_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_bundle_and_channel_helpers_are_reproducible_for_same_explicit_timestamp(
    tmp_path: Path,
) -> None:
    registry_path, key = _write_registry(tmp_path)
    out_dir = tmp_path / "bundles"
    explicit_timestamp = "2026-04-14T14:00:00Z"

    first = build_registry_bundle(registry_path, key, out_dir, created_at=explicit_timestamp)
    assert first["ok"] is True
    bundle_dir = Path(first["bundle_dir"])
    manifest_once = (bundle_dir / "registry_manifest.json").read_text(encoding="utf-8")
    sig_once = (bundle_dir / "canon_key_registry_v0.1.json.sig").read_text(encoding="utf-8")

    second = build_registry_bundle(
        registry_path,
        key,
        out_dir,
        force=True,
        created_at=explicit_timestamp,
    )
    assert second["ok"] is True
    manifest_twice = (bundle_dir / "registry_manifest.json").read_text(encoding="utf-8")
    sig_twice = (bundle_dir / "canon_key_registry_v0.1.json.sig").read_text(encoding="utf-8")

    assert manifest_once == manifest_twice
    assert sig_once == sig_twice

    channel_path = tmp_path / "channel.json"
    channel_path.write_text(
        json.dumps(
            {
                "channel_version": "v0.4",
                "updated_at": "2026-04-14T10:00:00Z",
                "published_at": "2026-04-14T10:00:00Z",
                "channel_seq": 1,
                "current_channel": "main",
                "channels": ["main"],
                "sources": {"main": [str(bundle_dir)]},
            }
        ),
        encoding="utf-8",
    )
    first_sig = sign_channel_file(channel_path, b"phase-657-channel-key", signed_at=explicit_timestamp)
    assert first_sig["ok"] is True
    sidecar_once = channel_path.with_suffix(".json.sig").read_text(encoding="utf-8")

    second_sig = sign_channel_file(channel_path, b"phase-657-channel-key", signed_at=explicit_timestamp)
    assert second_sig["ok"] is True
    sidecar_twice = channel_path.with_suffix(".json.sig").read_text(encoding="utf-8")

    assert sidecar_once == sidecar_twice


def test_promotion_and_sync_keep_bookkeeping_separate_from_signed_identity(
    tmp_path: Path,
) -> None:
    registry_path, key = _write_registry(tmp_path)
    src_dir = tmp_path / "src"
    build_result = build_registry_bundle(registry_path, key, src_dir, created_at="2026-04-14T10:15:00Z")
    assert build_result["ok"] is True
    bundle_dir = Path(build_result["bundle_dir"])

    channel_file = tmp_path / "channel.json"
    channel_data = {
        "channel_version": "v0.4",
        "updated_at": "2026-04-14T10:30:00Z",
        "published_at": "2026-04-14T10:30:00Z",
        "channel_seq": 1,
        "current_channel": "test",
        "channels": ["main", "test"],
        "channel_order": ["test", "main"],
        "sources": {"main": [str(bundle_dir)], "test": [str(bundle_dir)]},
    }
    channel_file.write_text(json.dumps(channel_data), encoding="utf-8")
    sign_channel_file(channel_file, b"phase-657-channel-key", signed_at="2026-04-14T10:30:00Z")

    dest_dir = tmp_path / "dest"
    promotion = promote_bundle(
        src_dir,
        dest_dir,
        channel_file,
        "test",
        "main",
        key,
        timestamp="2026-04-14T14:15:00Z",
    )
    assert promotion["ok"] is True
    assert promotion["last_promotion"]["timestamp"] == "2026-04-14T14:15:00Z"

    before_channel_hash = hashlib.sha256(channel_file.read_bytes()).hexdigest()
    sync_dest = tmp_path / "installed"
    sync_result = sync_channel_registry(
        SyncContext(
            channel_file=channel_file,
            key=key,
            dest_dir=sync_dest,
            channel="main",
            metadata_timestamp="2026-04-14T14:30:00Z",
        )
    )
    assert sync_result["ok"] is True
    assert sync_result["last_sync"]["timestamp"] == "2026-04-14T14:30:00Z"
    after_channel_hash = hashlib.sha256(channel_file.read_bytes()).hexdigest()
    assert before_channel_hash == after_channel_hash


def test_phase_657_main_commit_touches_expected_paths_only() -> None:
    _require_commit_or_skip(PHASE_657_SUBJECT_TOKEN)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_657_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith("docs/adr/") for path in changed_paths)


def test_phase_657_backfill_commit_touches_expected_paths_only() -> None:
    _require_commit_or_skip(PHASE_657_BACKFILL_SUBJECT_TOKEN)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_657_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_BACKFILL_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith("docs/adr/") for path in changed_paths)
    assert not any(path.startswith("ilc_core/") for path in changed_paths)
