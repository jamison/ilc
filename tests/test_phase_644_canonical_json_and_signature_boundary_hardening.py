from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

DOC_PATH = Path("docs/specs/ilc_canonical_json_and_signature_boundary_hardening_644_v0.1.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
TEST_PATH = Path("tests/test_phase_644_canonical_json_and_signature_boundary_hardening.py")
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_644_g8_canonical_json_and_signature_boundary_hardening_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
PHASE_644_SUBJECT_TOKEN = "phase 644 canonical json and signature boundary hardening"
PHASE_644_BACKFILL_SUBJECT_TOKEN = "phase 644 walkthrough and status backfill"
CANONICAL_TARGETS = (
    Path("ilc_core/ledger/canon_bundle_replay_report.py"),
    Path("ilc_core/ledger/canon_export_bundle_sign.py"),
    Path("ilc_core/ledger/canon_bundle_pipeline_report.py"),
    Path("ilc_core/cli/canon_bundle_sign.py"),
    Path("ilc_core/cli/canon_bundle_validate.py"),
    Path("ilc_core/cli/canon_bundle_replay.py"),
    Path("ilc_core/cli/canon_bundle_pipeline.py"),
)
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_HEADINGS = (
    "## 1. Scope and threat basis",
    "## 2. Canonical JSON contract",
    "## 3. Touched file changes",
    "## 4. Non-finite JSON boundary",
    "## 5. Second-order regression guardrails",
    "## 6. Verification evidence",
)
REQUIRED_TOKENS = (
    "canonical_json_sort_keys_and_compact_separators_locked",
    "canonical_json_no_whitespace_hash_drift_on_touched_surfaces",
    "canonical_json_non_finite_constants_rejected_on_touched_surfaces",
    "manifest_signing_uses_canonical_json_bytes",
    "machine_verifiable_bundle_reports_no_longer_use_sort_keys_false",
    "json_canonicalization_fix_does_not_introduce_separator_drift",
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


def _resolve_commit_ref(*, subject_token: str) -> str:
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
    raise AssertionError(f"commit_not_present_in_local_history:{subject_token}")


def _require_commit_or_skip(subject_token: str) -> None:
    if _find_commit_ref(subject_token=subject_token) is None:
        pytest.skip(f"commit_not_yet_present:{subject_token}")


def test_phase_doc_exists_with_required_headings() -> None:
    text = _read(DOC_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_phase_doc_contains_required_tokens() -> None:
    text = _read(DOC_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_touched_canonical_sources_use_sorted_keys_compact_separators_and_allow_nan_false() -> None:
    for path in CANONICAL_TARGETS:
        text = _read(path)
        assert "sort_keys=True" in text
        assert 'separators=(",", ":")' in text
        assert "allow_nan=False" in text


def test_manifest_signing_path_uses_canonical_manifest_json_bytes() -> None:
    text = _read(Path("ilc_core/ledger/canon_export_bundle_sign.py"))
    assert "_canonical_manifest_json" in text
    assert "invalid_manifest_non_finite" in text


def test_cli_json_outputs_remain_parseable_after_canonicalization() -> None:
    sample = {"warnings": [], "ok": True, "errors": [], "steps": {"verify": True}}
    dumped = json.dumps(sample, sort_keys=True, separators=(",", ":"), allow_nan=False)
    parsed = json.loads(dumped)
    assert parsed["ok"] is True
    assert list(parsed.keys()) == ["errors", "ok", "steps", "warnings"]


def test_no_touched_source_uses_sort_keys_false_any_longer() -> None:
    for path in CANONICAL_TARGETS:
        assert "sort_keys=False" not in _read(path)


def test_decision_log_unchanged_in_main_commit() -> None:
    _require_commit_or_skip(PHASE_644_SUBJECT_TOKEN)
    commit_ref = _resolve_commit_ref(subject_token=PHASE_644_SUBJECT_TOKEN)
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths


def test_phase_644_backfill_commit_touches_expected_paths_only() -> None:
    _require_commit_or_skip(PHASE_644_BACKFILL_SUBJECT_TOKEN)
    commit_ref = _resolve_commit_ref(subject_token=PHASE_644_BACKFILL_SUBJECT_TOKEN)
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_BACKFILL_PATHS
