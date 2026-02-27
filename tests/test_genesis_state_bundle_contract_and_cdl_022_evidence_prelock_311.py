"""Contract tests for Phase 311 genesis bundle + CDL-022 evidence prelock artifact."""

from __future__ import annotations

from pathlib import Path
import subprocess

from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows


ARTIFACT_PATH = Path("docs/specs/ilc_genesis_state_bundle_contract_and_cdl_022_evidence_prelock_311_v0.1.md")
DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
PHASE_311_COMMIT_SUBJECT = "docs(g8): phase 311 genesis state bundle contract and cdl-022 evidence prelock"


def _read() -> str:
    return ARTIFACT_PATH.read_text(encoding="utf-8")


def test_artifact_exists() -> None:
    assert ARTIFACT_PATH.exists()


def test_required_sections_present() -> None:
    text = _read()
    for heading in (
        "## 1. Purpose and scope",
        "## 2. CDL-022 state and option inventory",
        "## 3. Genesis state bundle command/data contract baseline",
        "## 4. D2 schema dependency lock (`d2_schema_baseline_310.v0.1`)",
        "## 5. Determinism and validation rules",
        "## 6. Evidence prelock requirements for CDL-022",
        "## 7. Phase-312 runtime entry criteria lock",
        "## 8. Non-goals and canonical anchors",
    ):
        assert heading in text


def test_cdl_022_state_candidate_and_option_inventory_are_explicit() -> None:
    text = _read()
    row = parse_decision_register_rows(Path(DECISION_LOG_PATH).read_text(encoding="utf-8"))["CDL-022"]
    assert "CDL-022" in text
    # Phase-311 is a historical prelock artifact and must preserve pre-ratification state.
    assert "status: open" in text
    assert f"current_candidate: {row.get('current_candidate')}" in text
    for option_token in [token.strip() for token in row.get("options", "").split(",") if token.strip()]:
        assert option_token in text


def test_dependency_token_and_verifier_regression_tokens_are_explicit() -> None:
    text = _read()
    for token in (
        "d2_schema_baseline_310.v0.1",
        "d2_schema_catalog_not_object",
        "d2_schema_invalid_catalog_version",
        "d2_schema_catalog_digest_missing",
        "d2_schema_catalog_digest_mismatch",
        "d2_schema_catalog_not_canonical",
    ):
        assert token in text


def test_runtime_deferral_and_phase_312_entry_criteria_are_explicit() -> None:
    text = _read()
    for token in (
        "Phase 312 may begin only when all of the following are true",
        "runtime scope is limited to genesis state bundle implementation tranche",
        "no implicit ratification language",
        "does not implement runtime behavior in `ilc_core/`",
    ):
        assert token in text


def test_boundary_statements_are_explicit() -> None:
    text = _read()
    for token in (
        "no decision-log mutation in this phase",
        "no runtime changes under `ilc_core/` in this phase",
        "no CDL-022 ratification execution",
        "no CDL-024 wire transport implementation details",
    ):
        assert token in text


def _resolve_phase_311_commit_ref() -> str:
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
        if subject.strip() == PHASE_311_COMMIT_SUBJECT:
            return commit_hash
    raise AssertionError("phase_311_commit_not_present_in_local_history")


def test_no_decision_log_mutation_in_phase_commit() -> None:
    commit_ref = _resolve_phase_311_commit_ref()
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    changed = {line.strip() for line in result.stdout.splitlines() if line.strip()}
    assert DECISION_LOG_PATH not in changed


def test_no_runtime_mutation_in_phase_commit() -> None:
    commit_ref = _resolve_phase_311_commit_ref()
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    changed = {line.strip() for line in result.stdout.splitlines() if line.strip()}
    forbidden = [path for path in changed if path.startswith("ilc_core/")]
    assert not forbidden, f"phase_311_runtime_mutations:{forbidden}"
