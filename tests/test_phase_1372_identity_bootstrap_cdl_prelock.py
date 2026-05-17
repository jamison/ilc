from __future__ import annotations

from pathlib import Path

from tools.validate_phase_prompt import validate


ROOT = Path(__file__).resolve().parents[1]

PROMPT = (
    ROOT
    / "docs/antigravity_tasks/antigravity_prompt__phase_1372_g8_identity_bootstrap_cdl_prelock.md"
)
REGISTER = ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"
PRELOCK = ROOT / "docs/specs/ilc_cdl_090_prelock_spec_1372_v0.1.md"
OPENING = ROOT / "docs/specs/ilc_cdl_090_identity_bootstrap_opening_1371_v0.1.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"
FORWARD_PLAN = (
    ROOT / "docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.2.md"
)
WALKTHROUGH = ROOT / "docs/phases/phase_1372_identity_bootstrap_cdl_prelock_walkthrough.md"

REQUIRED_TOKENS = (
    "cdl_090_prelock_committed_phase_1372",
    "cdl_090_not_ratified_phase_1372",
    "cdl_090_scope_constants_locked_phase_1372",
)

LOCKED_CONSTANTS = (
    "secure_output_target_contract_v1",
    "identity_seed_non_rotating_agent_id_origin_v1",
    "recovery_rotation_receipt_chain_v1",
    "agent_mode_no_secret_stdout_output_contract_v1",
    "identity_bootstrap_attestation_envelope_v1",
    "identity_bootstrap_public_artifact_field_contract_v1",
    "identity_bootstrap_environment_class_v1",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_1372_prompt_remains_schema_valid() -> None:
    assert validate(PROMPT) == []


def test_prelock_spec_resolves_all_phase_1371_questions_and_records_non_ratification() -> None:
    prelock = read(PRELOCK)
    opening = read(OPENING)

    assert "CDL-090 remains open and not ratified" in prelock
    assert "No Phase 1371 question remains unresolved" in prelock
    for token in REQUIRED_TOKENS:
        assert token in prelock
    for constant in LOCKED_CONSTANTS:
        assert constant in prelock

    for question_id in ("Q1", "Q2", "Q3", "Q4", "Q5", "Q6"):
        assert f"| {question_id} " in opening
        assert f"| {question_id} " in prelock

    required_phrases = (
        "canonical JSON",
        "deterministic key ordering",
        "non-finite numeric rejection",
        "non-custodial",
        "private graph content",
        "no secret material",
        "production_public_candidate",
        "devnet_non_authoritative",
        "test_fixture_non_authoritative",
        "local_private_non_authoritative",
    )
    for phrase in required_phrases:
        assert phrase in prelock


def test_phase_1372_does_not_mutate_cdl_register_or_ratify_cdl_090() -> None:
    register = read(REGISTER)
    rows = [line for line in register.splitlines() if line.startswith("| CDL-090 |")]
    assert len(rows) == 1
    row = rows[0]

    assert "| open |" in row
    assert "prelock_status: deferred_to_phase_1372" in row
    assert "ratification_status: not_ratified_phase_1371" in row
    assert "cdl_090_prelock_committed_phase_1372" not in row
    assert "cdl_090_ratified_phase_1373" not in row
    assert not any(line.startswith("| CDL-088 |") for line in register.splitlines())


def test_phase_1372_support_docs_record_completion_and_next_phase() -> None:
    for path in (STATUS, PLANNING_INDEX, FORWARD_PLAN, WALKTHROUGH):
        text = read(path)
        for token in REQUIRED_TOKENS:
            assert token in text
        assert "Phase 1373" in text
        assert "CDL-090" in text

    walkthrough = read(WALKTHROUGH)
    assert "graph_delta=load_bearing_artifact_added" in walkthrough
    assert "No CDL register mutation" in walkthrough
    assert "No runtime mutation" in walkthrough

