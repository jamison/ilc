from __future__ import annotations

import subprocess
from pathlib import Path

from tools.validate_phase_prompt import validate


ROOT = Path(__file__).resolve().parents[1]

PROMPT = (
    ROOT
    / "docs/antigravity_tasks/antigravity_prompt__phase_1376_g8_cdl_088_ratification.md"
)
REGISTER = ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"
PRELOCK = ROOT / "docs/specs/ilc_cdl_088_prelock_spec_1375_v0.1.md"
EVIDENCE = ROOT / "docs/specs/ilc_cdl_088_ratification_evidence_1376_v0.1.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"
FORWARD_PLAN = (
    ROOT / "docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.2.md"
)
WALKTHROUGH = ROOT / "docs/phases/phase_1376_cdl_088_ratification_walkthrough.md"

PHASE_1374_OPENING_COMMIT = "43bcddc0"

REQUIRED_TOKENS = (
    "cdl_088_ratified_phase_1376",
    "cdl_088_public_claimability_ratification_evidence_committed",
    "cdl_088_historical_hardening_phase_1374_ref_asserted",
)

LOCKED_CONSTANTS = (
    "bounded_public_claimability_condition_v1",
    "public_claimability_proof_bundle_v1",
    "reciprocal_claim_identity_score_interlock_v1",
    "reciprocal_scoring_formula_deferred_v1",
    "ecu_escrow_admission_boundary_v1",
    "no_private_or_shadow_economics_claimability_v1",
    "public_verifier_api_minimum_preconditions_v1",
    "ratification_vs_activation_split_v1",
    "claim_endpoint_default_closed_v1",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def cdl_088_row(text: str) -> str:
    rows = [line for line in text.splitlines() if line.startswith("| CDL-088 |")]
    assert len(rows) == 1
    return rows[0]


def phase_1376_status_section() -> str:
    status = read(STATUS)
    start = status.index("## Phase 1376")
    next_start = status.find("\n## Phase ", start + len("## Phase 1376"))
    if next_start == -1:
        return status[start:]
    return status[start:next_start]


def historical_register_text() -> str:
    result = subprocess.run(
        [
            "git",
            "show",
            f"{PHASE_1374_OPENING_COMMIT}:docs/specs/ilc_constitutional_decision_log_v0.1.md",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
        timeout=10,
    )
    return result.stdout


def test_01_phase_1376_prompt_remains_schema_valid() -> None:
    assert validate(PROMPT) == []


def test_02_ratification_evidence_records_required_tokens_and_constants() -> None:
    evidence = read(EVIDENCE)
    prelock = read(PRELOCK)

    for token in REQUIRED_TOKENS:
        assert token in evidence

    assert "GO Phase 1376" in evidence
    assert "ILC_CDL_MUTATION_PHASE=1376" in evidence
    assert "3d8ce11e" in evidence
    assert "cdl_088_register_diff_disposition_phase_1376=cdl088_open_to_ratified" in evidence

    for constant in LOCKED_CONSTANTS:
        assert constant in prelock
        assert constant in evidence


def test_03_current_cdl_088_row_is_ratified_with_evidence_refs() -> None:
    row = cdl_088_row(read(REGISTER))

    assert "| ratified |" in row
    assert "| open |" not in row
    assert "prelock_phase: 1375" in row
    assert "prelock_token: cdl_088_prelock_committed_phase_1375" in row
    assert "scope_token: cdl_088_scope_constants_locked_phase_1375" in row
    assert "ratified_phase: 1376" in row
    assert "ratified_date: 2026-05-18" in row
    assert "ratification_token: cdl_088_ratified_phase_1376" in row
    assert (
        "evidence_document: "
        "docs/specs/ilc_cdl_088_ratification_evidence_1376_v0.1.md"
    ) in row


def test_04_cdl_088_ratification_preserves_no_activation_boundary() -> None:
    row = cdl_088_row(read(REGISTER))
    evidence = read(EVIDENCE)
    walkthrough = read(WALKTHROUGH)
    status_section = phase_1376_status_section()

    for text in (row, evidence, walkthrough, status_section):
        assert "public_claimability_activation_status: not_enabled" in text
        assert "claim_endpoint_status: not_enabled" in text
        assert "runtime_activation_status: not_authorized" in text

    assert "public_verifier_api_status: not_enabled" in row
    assert "phase_1389_gate_status: still_required" in row

    for forbidden_claim in (
        "result=public_claimability_activated",
        "claim_endpoint_active",
        "public_verifier_api_active",
    ):
        assert forbidden_claim not in evidence
        assert forbidden_claim not in walkthrough
        assert forbidden_claim not in status_section


def test_05_frontier_docs_record_phase_1376_and_downstream_dependencies() -> None:
    texts = (
        read(WALKTHROUGH),
        read(STATUS),
        read(PLANNING_INDEX),
        read(FORWARD_PLAN),
    )

    for text in texts:
        normalized = " ".join(text.split())
        for token in REQUIRED_TOKENS:
            assert token in text
        assert "Phase 1377" in text
        assert "Phase 1380 requires 1373+1376" in normalized
        assert "Phase 1389" in text


def test_06_historical_phase_1374_register_row_was_open() -> None:
    historical = historical_register_text()
    row = cdl_088_row(historical)

    assert "| open |" in row
    assert "| ratified |" not in row
    assert "opening_token: cdl_088_public_claimability_opened_phase_1374" in row
    assert "ratification_status: not_ratified_phase_1374" in row
    assert "cdl_088_ratified_phase_1376" not in row


def test_07_historical_row_lacks_ratification_token_current_row_has_it() -> None:
    historical_row = cdl_088_row(historical_register_text())
    current_row = cdl_088_row(read(REGISTER))

    assert "cdl_088_ratified_phase_1376" not in historical_row
    assert "docs/specs/ilc_cdl_088_ratification_evidence_1376_v0.1.md" not in historical_row
    assert "cdl_088_ratified_phase_1376" in current_row
    assert "docs/specs/ilc_cdl_088_ratification_evidence_1376_v0.1.md" in current_row
    assert "prelock_status: deferred_to_phase_1375" not in current_row
    assert "ratification_status: not_ratified_phase_1374" not in current_row
