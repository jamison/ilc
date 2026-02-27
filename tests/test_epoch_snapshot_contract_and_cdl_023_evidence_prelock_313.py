"""Contract tests for Phase 313 epoch snapshot + CDL-023 evidence prelock artifact."""

from __future__ import annotations

from pathlib import Path
import subprocess

from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows


ARTIFACT_PATH = Path("docs/specs/ilc_epoch_snapshot_contract_and_cdl_023_evidence_prelock_313_v0.1.md")
DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
PHASE_313_COMMIT_SUBJECT = "docs(g8): phase 313 epoch snapshot contract and cdl-023 evidence prelock"


def _read() -> str:
    return ARTIFACT_PATH.read_text(encoding="utf-8")


def test_artifact_exists() -> None:
    assert ARTIFACT_PATH.exists()


def test_required_sections_present() -> None:
    text = _read()
    for heading in (
        "## 1. Purpose and scope",
        "## 2. CDL-023 state and option inventory",
        "## 3. Epoch snapshot command/data contract baseline",
        "## 4. Dependency locks (`d2_schema_baseline_310.v0.1`, `genesis_state_bundle_312.v0.1`)",
        "## 5. Determinism and validation rules",
        "## 6. Evidence prelock requirements for CDL-023",
        "## 7. Phase-314 runtime entry criteria lock",
        "## 8. Non-goals and canonical anchors",
    ):
        assert heading in text


def test_cdl_023_state_candidate_and_option_inventory_are_explicit() -> None:
    text = _read()
    row = parse_decision_register_rows(Path(DECISION_LOG_PATH).read_text(encoding="utf-8"))["CDL-023"]
    assert "CDL-023" in text
    # Phase-313 is a historical prelock artifact and must preserve pre-ratification state.
    assert "status: open" in text
    assert f"current_candidate: {row.get('current_candidate')}" in text
    for option_token in [token.strip() for token in row.get("options", "").split(",") if token.strip()]:
        assert option_token in text


def test_dependency_tokens_are_explicit() -> None:
    text = _read()
    assert "d2_schema_baseline_310.v0.1" in text
    assert "genesis_state_bundle_312.v0.1" in text


def test_runtime_deferral_and_phase_314_entry_criteria_are_explicit() -> None:
    text = _read()
    for token in (
        "Phase 314 may begin only when all of the following are true",
        "runtime scope is limited to epoch snapshot implementation tranche",
        "no implicit ratification language",
        "does not implement runtime behavior in `ilc_core/`",
    ):
        assert token in text


def test_boundary_statements_are_explicit() -> None:
    text = _read()
    for token in (
        "no decision-log mutation in this phase",
        "no runtime changes under `ilc_core/` in this phase",
        "no CDL-023 ratification execution",
        "no CDL-024 wire transport implementation details",
    ):
        assert token in text


def _resolve_phase_313_commit_ref() -> str:
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
        if subject.strip() == PHASE_313_COMMIT_SUBJECT:
            return commit_hash
    raise AssertionError("phase_313_commit_not_present_in_local_history")


def test_no_decision_log_mutation_in_phase_commit() -> None:
    commit_ref = _resolve_phase_313_commit_ref()
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    changed = {line.strip() for line in result.stdout.splitlines() if line.strip()}
    assert DECISION_LOG_PATH not in changed


def test_no_runtime_mutation_in_phase_commit() -> None:
    commit_ref = _resolve_phase_313_commit_ref()
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    changed = {line.strip() for line in result.stdout.splitlines() if line.strip()}
    forbidden = [path for path in changed if path.startswith("ilc_core/")]
    assert not forbidden, f"phase_313_runtime_mutations:{forbidden}"
