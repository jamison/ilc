from __future__ import annotations

from pathlib import Path

from tools.validate_phase_prompt import validate


ROOT = Path(__file__).resolve().parents[1]

PROMPT = (
    ROOT / "docs/antigravity_tasks/antigravity_prompt__phase_1375_g8_cdl_088_prelock.md"
)
REGISTER = ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"
PRELOCK = ROOT / "docs/specs/ilc_cdl_088_prelock_spec_1375_v0.1.md"
OPENING = ROOT / "docs/specs/ilc_cdl_088_public_claimability_opening_1374_v0.1.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"
FORWARD_PLAN = (
    ROOT / "docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.2.md"
)
WALKTHROUGH = ROOT / "docs/phases/phase_1375_cdl_088_prelock_walkthrough.md"

REQUIRED_TOKENS = (
    "cdl_088_prelock_committed_phase_1375",
    "cdl_088_not_ratified_phase_1375",
    "cdl_088_scope_constants_locked_phase_1375",
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


def cdl_row(text: str, cdl_id: str) -> str:
    rows = [line for line in text.splitlines() if line.startswith(f"| {cdl_id} |")]
    assert len(rows) == 1
    return rows[0]


def test_phase_1375_prompt_remains_schema_valid() -> None:
    assert validate(PROMPT) == []


def test_prelock_spec_resolves_phase_1374_questions_and_records_tokens() -> None:
    prelock = read(PRELOCK)
    opening = read(OPENING)

    assert "CDL-088 remains open and not ratified" in prelock
    assert "No Phase 1374 question remains unresolved" in prelock
    assert "phase_1376_cdl_088_ratification_next" in prelock

    for token in REQUIRED_TOKENS:
        assert token in prelock
    for constant in LOCKED_CONSTANTS:
        assert constant in prelock

    for question in (
        "Is reciprocal scoring in CDL-088 scope?",
        "Is ECU-escrow admission in CDL-088 scope?",
        "What exactly constitutes bounded public claimability?",
        "What proof bundle must exist before a public claim endpoint can activate?",
        "Does CDL-088 impose a condition-bounded window",
        "Which items are CDL-088 ratification requirements versus Phase 1389",
    ):
        assert question in opening
        assert question in prelock


def test_prelock_locks_conservative_claimability_scope() -> None:
    prelock = read(PRELOCK)

    required_phrases = (
        "condition-bounded",
        "epoch-scoped",
        "Replay/nullifier",
        "settled runtime root",
        "wallet-state root",
        "canonical agent identity",
        "public-only economics admission",
        "The Phase 1222 reciprocal scoring formula remains a non-selected research candidate",
        "ECU escrow is not a universal prerequisite",
        "Phase 1375 creates no HTTP route",
    )
    for phrase in required_phrases:
        assert phrase in prelock

    forbidden_phrases = (
        "public_claimability_activation_status: enabled",
        "claim_endpoint_status: enabled",
        "runtime_activation_status: authorized",
        "result=public_claimability_activated",
    )
    for phrase in forbidden_phrases:
        assert phrase not in prelock


def test_phase_1375_does_not_mutate_cdl_register_or_ratify_cdl_088() -> None:
    register = read(REGISTER)
    row = cdl_row(register, "CDL-088")

    assert "| open |" in row
    assert "| ratified |" not in row
    assert "prelock_status: deferred_to_phase_1375" in row
    assert "ratification_status: not_ratified_phase_1374" in row
    assert "public_claimability_activation_status: not_enabled" in row
    assert "claim_endpoint_status: not_enabled" in row
    assert "runtime_activation_status: not_authorized" in row
    assert "cdl_088_prelock_committed_phase_1375" not in row
    assert "cdl_088_ratified_phase_1376" not in row


def test_phase_1375_frontier_docs_record_completion_and_next_phase() -> None:
    for path in (STATUS, PLANNING_INDEX, FORWARD_PLAN, WALKTHROUGH):
        text = read(path)
        for token in REQUIRED_TOKENS:
            assert token in text
        assert "Phase 1376" in text
        assert "CDL-088" in text

    walkthrough = read(WALKTHROUGH)
    assert "graph_delta=load_bearing_artifact_added" in walkthrough
    assert "No CDL register mutation" in walkthrough
    assert "No runtime mutation" in walkthrough
