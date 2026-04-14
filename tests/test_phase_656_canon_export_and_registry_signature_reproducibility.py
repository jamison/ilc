from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from ilc_core.ledger.canon_bundle_key_registry import sign_registry_file
from ilc_core.ledger.canon_export_bundle_sign import sign_manifest


FIX_DOC_PATH = Path("docs/specs/ilc_signing_export_reproducibility_fix_656_v0.1.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
TEST_PATH = Path(
    "tests/test_phase_656_canon_export_and_registry_signature_reproducibility.py"
)
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_656_g8_canon_export_and_registry_signature_reproducibility_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
PHASE_656_SUBJECT_TOKEN = (
    "phase 656 canon export and registry signature reproducibility"
)
PHASE_656_BACKFILL_SUBJECT_TOKEN = "phase 656 walkthrough and status backfill"
EXACT_REQUIRED_MAIN_PATHS = {
    str(FIX_DOC_PATH),
    str(TEST_PATH),
    "ilc_core/ledger/canon_export_bundle_sign.py",
    "ilc_core/ledger/canon_bundle_key_registry.py",
    "tests/test_canon_export_bundle_sign.py",
    "tests/test_canon_bundle_key_registry_signing.py",
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_HEADINGS = (
    "## 1. Bug class and touched surfaces",
    "## 2. Manifest signing contract",
    "## 3. Registry signature sidecar contract",
    "## 4. Verification compatibility and preserved boundaries",
)
REQUIRED_TOKENS = (
    "canon_export_manifest_signing_reproducibility_fixed_in_656",
    "registry_signature_sidecar_reproducibility_fixed_in_656",
    "signed_metadata_timestamp_must_be_explicit_or_deterministic",
    "verification_compatibility_preserved_after_656",
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


def test_fix_doc_exists_contains_required_headings() -> None:
    text = _read(FIX_DOC_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_fix_doc_contains_required_tokens() -> None:
    text = _read(FIX_DOC_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_manifest_signing_same_explicit_timestamp_is_reproducible(
    tmp_path: Path,
) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    (bundle_dir / "manifest.json").write_text(
        json.dumps({"foo": "bar", "created_at": "2026-04-14T09:30:00Z"}),
        encoding="utf-8",
    )
    key = b"phase-656-manifest-key"
    signed_at = "2026-04-14T11:00:00Z"

    sign_manifest(bundle_dir, key, signed_at=signed_at)
    manifest_once = (bundle_dir / "manifest.json").read_text(encoding="utf-8")
    sig_once = (bundle_dir / "manifest.sig").read_bytes()

    sign_manifest(bundle_dir, key, overwrite=True, signed_at=signed_at)
    manifest_twice = (bundle_dir / "manifest.json").read_text(encoding="utf-8")
    sig_twice = (bundle_dir / "manifest.sig").read_bytes()

    assert manifest_once == manifest_twice
    assert sig_once == sig_twice


def test_registry_sidecar_generation_is_reproducible_for_same_timestamp(
    tmp_path: Path,
) -> None:
    registry_path = tmp_path / "registry.json"
    registry_path.write_text(
        json.dumps(
            {
                "registry_version": "v0.1",
                "updated_at": "2026-04-14T09:45:00Z",
                "current_keys": ["a1b2c3d4e5f6a7b8"],
                "previous_keys": [],
                "deprecated_keys": [],
            }
        ),
        encoding="utf-8",
    )
    key = b"phase-656-registry-key"
    signed_at = "2026-04-14T11:15:00Z"

    first = sign_registry_file(registry_path, key, signed_at=signed_at)
    assert first["ok"]
    sig_path = registry_path.with_suffix(".json.sig")
    sidecar_once = sig_path.read_text(encoding="utf-8")

    second = sign_registry_file(registry_path, key, signed_at=signed_at)
    assert second["ok"]
    sidecar_twice = sig_path.read_text(encoding="utf-8")

    assert sidecar_once == sidecar_twice


def test_phase_656_main_commit_touches_expected_paths_only() -> None:
    _require_commit_or_skip(PHASE_656_SUBJECT_TOKEN)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_656_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith("docs/adr/") for path in changed_paths)


def test_phase_656_backfill_commit_touches_expected_paths_only() -> None:
    _require_commit_or_skip(PHASE_656_BACKFILL_SUBJECT_TOKEN)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_656_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_BACKFILL_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith("docs/adr/") for path in changed_paths)
    assert not any(path.startswith("ilc_core/") for path in changed_paths)
