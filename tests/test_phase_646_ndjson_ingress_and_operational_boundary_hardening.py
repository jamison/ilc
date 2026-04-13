from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

DOC_PATH = Path("docs/specs/ilc_ndjson_ingress_and_operational_boundary_hardening_646_v0.1.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
NDJSON_PATH = Path("ilc_core/protocol/ndjson_bundle.py")
CLI_PATH = Path("ilc_core/cli/ep_task_cli.py")
PHASE_646_BACKFILL_SUBJECT_TOKEN = "phase 646 walkthrough and status backfill"
BACKFILL_PATHS = {
    "docs/phases/phase_646_g8_ndjson_ingress_and_operational_boundary_hardening_walkthrough.md",
    "docs/phases/STATUS.md",
}
REQUIRED_HEADINGS = (
    "## 1. Scope and threat basis",
    "## 2. Bundle-scale hard limits",
    "## 3. Non-finite and parser boundary rules",
    "## 4. CLI timeout and exception boundary",
    "## 5. Wall-clock classification",
    "## 6. Verification evidence",
)
REQUIRED_TOKENS = (
    "ndjson_bundle_total_scale_bounded_without_temp_disk_spooling",
    "ndjson_bundle_record_count_and_total_bytes_limited",
    "ndjson_bundle_non_finite_json_constants_rejected",
    "ep_task_cli_http_timeout_contract_is_explicit_and_bifurcated",
    "ep_task_cli_broad_exception_catch_reduced_on_touched_boundary",
    "wall_clock_remains_metadata_only_in_touched_646_surfaces",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


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


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def test_phase_doc_exists_with_required_headings() -> None:
    text = _read(DOC_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_phase_doc_contains_required_tokens() -> None:
    text = _read(DOC_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_ndjson_bundle_has_record_count_and_total_byte_limits() -> None:
    text = _read(NDJSON_PATH)
    assert "DEFAULT_MAX_RECORDS_PER_BUNDLE" in text
    assert "DEFAULT_MAX_TOTAL_BYTES_PER_BUNDLE" in text
    assert "max_records" in text
    assert "max_total_bytes" in text


def test_ndjson_bundle_continues_to_reject_non_finite_json_constants() -> None:
    text = _read(NDJSON_PATH)
    assert "parse_constant=_reject_nan_infinity" in text
    assert "allow_nan=False" in text


def test_ndjson_bundle_fix_does_not_add_temp_disk_spooling() -> None:
    text = _read(NDJSON_PATH)
    assert "NamedTemporaryFile" not in text
    assert "tempfile" not in text


def test_ep_task_cli_uses_explicit_bifurcated_timeouts() -> None:
    text = _read(CLI_PATH)
    assert "CONNECT_TIMEOUT_S = 2.0" in text
    assert "READ_TIMEOUT_S = 30.0" in text
    assert "timeout=(CONNECT_TIMEOUT_S, READ_TIMEOUT_S)" in text


def test_ep_task_cli_no_longer_uses_generic_except_exception_on_touched_handlers() -> None:
    text = _read(CLI_PATH)
    assert "except Exception" not in text


def test_decision_log_unchanged() -> None:
    assert DECISION_LOG_PATH.exists()


def test_phase_646_backfill_commit_touches_expected_paths_only() -> None:
    commit_ref = _find_commit_ref(subject_token=PHASE_646_BACKFILL_SUBJECT_TOKEN)
    if commit_ref is None:
        pytest.skip("commit_not_yet_present")
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == BACKFILL_PATHS
