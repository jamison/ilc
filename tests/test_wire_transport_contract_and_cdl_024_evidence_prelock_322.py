"""Contract tests for Phase 322 wire transport + CDL-024 evidence prelock artifact."""

from __future__ import annotations

from pathlib import Path
import subprocess

from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows


ARTIFACT_PATH = Path("docs/specs/ilc_wire_transport_contract_and_cdl_024_evidence_prelock_322_v0.1.md")
TEST_PATH = Path("tests/test_wire_transport_contract_and_cdl_024_evidence_prelock_322.py")
DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
PHASE_322_COMMIT_SUBJECT = "docs(g8): phase 322 wire transport contract and cdl-024 evidence prelock"


def _read() -> str:
    return ARTIFACT_PATH.read_text(encoding="utf-8")


def test_artifact_exists() -> None:
    assert ARTIFACT_PATH.exists()


def test_required_sections_present() -> None:
    text = _read()
    for heading in (
        "## 1. Purpose and scope",
        "## 2. CDL-024 state and option inventory",
        "## 3. Wire transport command/data contract baseline",
        "## 4. Dependency and transport-agnostic boundary lock",
        "## 5. Determinism and conformance validation rules",
        "## 6. Evidence prelock requirements for CDL-024",
        "## 7. Phase-323 runtime entry criteria lock",
        "## 8. Non-goals and canonical anchors",
    ):
        assert heading in text


def test_cdl_024_state_candidate_and_option_inventory_are_explicit() -> None:
    text = _read()
    row = parse_decision_register_rows(Path(DECISION_LOG_PATH).read_text(encoding="utf-8"))["CDL-024"]
    assert "CDL-024" in text
    # Phase-322 is a historical prelock artifact and must preserve pre-ratification state.
    assert "status: open" in text
    assert f"current_candidate: {row.get('current_candidate')}" in text
    for option_token in [token.strip() for token in row.get("options", "").split(",") if token.strip()]:
        assert option_token in text


def test_dependency_tokens_and_transport_agnostic_boundary_are_explicit() -> None:
    text = _read()
    for token in (
        "d2_schema_baseline_310.v0.1",
        "genesis_state_bundle_312.v0.1",
        "epoch_snapshot_runtime_314.v0.1",
        "transport-agnostic",
        "provider-neutral",
        "does not bind implementation to a single transport/provider",
    ):
        assert token in text


def test_runtime_deferral_and_phase_323_entry_criteria_are_explicit() -> None:
    text = _read()
    for token in (
        "Phase 323 may begin only when all of the following are true",
        "runtime scope is limited to wire transport implementation tranche",
        "no implicit ratification language",
        "does not implement runtime behavior in `ilc_core/`",
    ):
        assert token in text


def test_boundary_statements_are_explicit() -> None:
    text = _read()
    for token in (
        "no decision-log mutation in this phase",
        "no runtime changes under `ilc_core/` in this phase",
        "no CDL-024 ratification execution",
        "no CDL-021 rust/wasm runtime implementation",
    ):
        assert token in text


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_322_commit_ref() -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    matching_commits: list[str] = []
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if subject.strip() == PHASE_322_COMMIT_SUBJECT:
            matching_commits.append(commit_hash)
    for commit_ref in matching_commits:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if str(ARTIFACT_PATH) in changed_paths and str(TEST_PATH) in changed_paths:
            return commit_ref
    if matching_commits:
        raise AssertionError("phase_322_commit_subject_present_but_no_contract_artifact_commit")
    raise AssertionError("phase_322_commit_not_present_in_local_history")


def test_no_decision_log_mutation_in_phase_commit() -> None:
    commit_ref = _resolve_phase_322_commit_ref()
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    changed = {line.strip() for line in result.stdout.splitlines() if line.strip()}
    assert DECISION_LOG_PATH not in changed


def test_no_runtime_mutation_in_phase_commit() -> None:
    commit_ref = _resolve_phase_322_commit_ref()
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    changed = {line.strip() for line in result.stdout.splitlines() if line.strip()}
    forbidden = [path for path in changed if path.startswith("ilc_core/")]
    assert not forbidden, f"phase_322_runtime_mutations:{forbidden}"
