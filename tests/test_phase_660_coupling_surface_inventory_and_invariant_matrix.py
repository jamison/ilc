from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest


MARKDOWN_PATH = Path("docs/specs/ilc_coupling_surface_inventory_and_invariant_matrix_660_v0.1.md")
JSON_PATH = Path("docs/specs/ilc_coupling_surface_inventory_and_invariant_matrix_660_v0.1.json")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
TEST_PATH = Path("tests/test_phase_660_coupling_surface_inventory_and_invariant_matrix.py")
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_660_g8_coupling_surface_inventory_and_invariant_matrix_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
PHASE_660_SUBJECT_TOKEN = "phase 660 coupling surface inventory and invariant matrix"
PHASE_660_BACKFILL_SUBJECT_TOKEN = "phase 660 walkthrough and status backfill"
EXACT_REQUIRED_MAIN_PATHS = {
    str(MARKDOWN_PATH),
    str(JSON_PATH),
    str(TEST_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_HEADINGS = (
    "## 1. Purpose and practical definitions",
    "## 2. Coupling surface inventory",
    "## 3. Invariant matrix",
    "## 4. Allowed downstream actions",
    "## 5. Forbidden backend actions",
    "## 6. Evidence basis and unresolved edges",
)
REQUIRED_TOKENS = (
    "coupling_surface_inventory_660_primary_artifact",
    "upstream_means_source_of_canonical_legitimacy_or_authority",
    "downstream_means_record_order_anchor_finalize_or_settle_only",
    "backend_may_not_author_protocol_legitimacy",
    "admission_namespace_quorum_settlement_reputation_surfaces_in_scope",
    "machine_legible_matrix_required_for_later_windows",
)
MINIMUM_SURFACES = {
    "public admission legitimacy",
    "canonical namespace / handle authority",
    "quorum / panel / evaluation authority",
    "public settlement legitimacy",
    "public reputation continuity",
    "public receipt lineage",
}
REQUIRED_ENTRY_KEYS = {
    "surface",
    "upstream_authority",
    "downstream_allowed_actions",
    "forbidden_backend_actions",
    "required_lineage_or_receipt_basis",
    "evidence_refs",
}


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


def test_markdown_inventory_exists_and_contains_all_required_headings() -> None:
    text = _read(MARKDOWN_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_markdown_inventory_contains_all_required_tokens() -> None:
    text = _read(MARKDOWN_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_json_matrix_exists_and_is_valid_canonical_json() -> None:
    text = _read(JSON_PATH)
    payload = json.loads(text)
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
    assert text.strip() == canonical
    assert payload["artifact"] == "ilc_coupling_surface_inventory_and_invariant_matrix_660_v0.1"
    assert payload["phase"] == 660
    assert payload["window"] == "659-664"


def test_json_matrix_contains_all_required_keys_for_every_surface_entry() -> None:
    payload = json.loads(_read(JSON_PATH))
    for entry in payload["entries"]:
        assert REQUIRED_ENTRY_KEYS.issubset(entry.keys())


def test_all_minimum_surfaces_are_present() -> None:
    payload = json.loads(_read(JSON_PATH))
    surfaces = {entry["surface"] for entry in payload["entries"]}
    assert MINIMUM_SURFACES.issubset(surfaces)


def test_allowed_downstream_actions_are_separated_from_forbidden_backend_actions() -> None:
    payload = json.loads(_read(JSON_PATH))
    for entry in payload["entries"]:
        assert entry["downstream_allowed_actions"]
        assert entry["forbidden_backend_actions"]
        assert set(entry["downstream_allowed_actions"]).isdisjoint(
            set(entry["forbidden_backend_actions"])
        )


def test_evidence_references_are_populated_for_each_surface() -> None:
    payload = json.loads(_read(JSON_PATH))
    for entry in payload["entries"]:
        assert entry["evidence_refs"]
        assert all(ref.startswith("docs/") for ref in entry["evidence_refs"])


def test_decision_log_and_ilc_core_remain_unchanged_for_main_commit() -> None:
    _require_commit_or_skip(PHASE_660_SUBJECT_TOKEN)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_660_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith("ilc_core/") for path in changed_paths)


def test_phase_660_main_and_backfill_commit_path_sets_obey_phase_scope() -> None:
    _require_commit_or_skip(PHASE_660_SUBJECT_TOKEN)
    main_commit_ref = _resolve_commit_ref(
        subject_token=PHASE_660_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    assert _changed_paths_for_commit(main_commit_ref) == EXACT_REQUIRED_MAIN_PATHS

    if _find_commit_ref(subject_token=PHASE_660_BACKFILL_SUBJECT_TOKEN) is None:
        pytest.skip(f"commit_not_yet_present:{PHASE_660_BACKFILL_SUBJECT_TOKEN}")
    backfill_commit_ref = _resolve_commit_ref(
        subject_token=PHASE_660_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    changed_paths = _changed_paths_for_commit(backfill_commit_ref)
    assert changed_paths == EXACT_REQUIRED_BACKFILL_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith("ilc_core/") for path in changed_paths)
