from __future__ import annotations

import subprocess
from pathlib import Path

from tools.validate_phase_prompt import validate


ROOT = Path(__file__).resolve().parents[1]

PROMPT = (
    ROOT
    / "docs/antigravity_tasks/antigravity_prompt__phase_1373_g8_identity_bootstrap_cdl_ratification.md"
)
REGISTER = ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"
PRELOCK = ROOT / "docs/specs/ilc_cdl_090_prelock_spec_1372_v0.1.md"
EVIDENCE = ROOT / "docs/specs/ilc_cdl_090_ratification_evidence_1373_v0.1.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"
FORWARD_PLAN = (
    ROOT / "docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.2.md"
)
WALKTHROUGH = ROOT / "docs/phases/phase_1373_identity_bootstrap_cdl_ratification_walkthrough.md"

PHASE_1371_OPENING_COMMIT = "580bf148"

REQUIRED_TOKENS = (
    "cdl_090_ratified_phase_1373",
    "cdl_090_identity_bootstrap_ratification_evidence_committed",
    "cdl_090_historical_hardening_phase_1371_ref_asserted",
)

LOCKED_CONSTANTS = (
    "agent_id_derivation_contract",
    "secure_output_target_contract_v1",
    "approved_production_secure_target_classes",
    "non_production_only_secure_target_classes",
    "no_stdout_secret_emission_rule",
    "private_graph_entropy_exclusion_rule",
    "non_custodial_default_rule",
    "identity_seed_non_rotating_agent_id_origin_v1",
    "recovery_rotation_receipt_chain_v1",
    "agent_mode_no_secret_stdout_output_contract_v1",
    "identity_bootstrap_attestation_envelope_v1",
    "identity_bootstrap_public_artifact_field_contract_v1",
    "identity_bootstrap_environment_class_v1",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def cdl_090_row(text: str) -> str:
    rows = [line for line in text.splitlines() if line.startswith("| CDL-090 |")]
    assert len(rows) == 1
    return rows[0]


def cdl_row(text: str, cdl_id: str) -> str:
    rows = [line for line in text.splitlines() if line.startswith(f"| {cdl_id} |")]
    assert len(rows) == 1
    return rows[0]


def historical_register_text() -> str:
    result = subprocess.run(
        [
            "git",
            "show",
            f"{PHASE_1371_OPENING_COMMIT}:docs/specs/ilc_constitutional_decision_log_v0.1.md",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
        timeout=10,
    )
    return result.stdout


def test_01_phase_1373_prompt_remains_schema_valid() -> None:
    assert validate(PROMPT) == []


def test_02_ratification_evidence_and_frontier_docs_record_required_tokens() -> None:
    texts = (
        read(EVIDENCE),
        read(WALKTHROUGH),
        read(STATUS),
        read(PLANNING_INDEX),
        read(FORWARD_PLAN),
    )

    for text in texts:
        for token in REQUIRED_TOKENS:
            assert token in text

    evidence = read(EVIDENCE)
    assert "ff841ad2" in evidence
    assert "GO Phase 1373" in evidence
    assert "ILC_CDL_MUTATION_PHASE=1373" in evidence
    assert "cdl_090_register_diff_disposition_phase_1373=cdl090_open_to_ratified" in evidence


def test_03_cdl_090_register_row_is_ratified_with_evidence_refs_and_blocks() -> None:
    register = read(REGISTER)
    row = cdl_090_row(register)

    assert "| ratified |" in row
    assert "| open |" not in row
    assert "prelock_phase: 1372" in row
    assert "prelock_token: cdl_090_prelock_committed_phase_1372" in row
    assert "scope_token: cdl_090_scope_constants_locked_phase_1372" in row
    assert "ratified_phase: 1373" in row
    assert "ratified_date: 2026-05-17" in row
    assert "ratification_token: cdl_090_ratified_phase_1373" in row
    assert (
        "evidence_document: "
        "docs/specs/ilc_cdl_090_ratification_evidence_1373_v0.1.md"
    ) in row
    assert "public_identity_activation_status: not_enabled" in row
    assert "identity_artifact_creation_status: not_authorized" in row
    assert "runtime_activation_status: not_authorized" in row
    assert "cdl_088_status: unopened_reserved_for_phase_1374" in row
    cdl_088 = cdl_row(register, "CDL-088")
    assert "| ratified |" in cdl_088
    assert "ratified_phase: 1376" in cdl_088


def test_04_scope_constants_from_prelock_are_ratified_in_evidence() -> None:
    prelock = read(PRELOCK)
    evidence = read(EVIDENCE)

    assert "## 5. Locked Scope Constants" in prelock
    assert "## 5. Ratified Scope Constants" in evidence
    for constant in LOCKED_CONSTANTS:
        assert constant in prelock
        assert constant in evidence

    for required_phrase in (
        "identity_bootstrap_attestation_v1",
        "ilc-identity-bootstrap-attestation-v1",
        "canonical JSON",
        "deterministic key ordering",
        "non-finite numeric rejection",
        "production_public_candidate",
        "devnet_non_authoritative",
        "test_fixture_non_authoritative",
        "local_private_non_authoritative",
    ):
        assert required_phrase in evidence


def test_05_non_goals_and_non_activation_are_explicit() -> None:
    evidence = read(EVIDENCE)
    walkthrough = read(WALKTHROUGH)
    status = read(STATUS)

    for text in (evidence, walkthrough, status):
        assert "does not authorize" in text or "did not authorize" in text
        assert "Identity artifact creation" in text or "identity artifact creation" in text
        assert "Runtime implementation" in text or "runtime implementation" in text
        assert "Public identity activation" in text or "public identity activation" in text
        assert "Public claimability" in text or "public claimability" in text
        assert "CDL-088" in text

    assert "No CDL-088 row was opened" in evidence
    assert "No runtime file changed" in walkthrough


def test_06_historical_phase_1371_register_row_was_open() -> None:
    historical = historical_register_text()
    row = cdl_090_row(historical)

    assert "| open |" in row
    assert "| ratified |" not in row
    assert "opening_token: cdl_090_identity_bootstrap_opened_phase_1371" in row
    assert "ratification_status: not_ratified_phase_1371" in row
    assert "cdl_090_ratified_phase_1373" not in row
    assert not any(line.startswith("| CDL-088 |") for line in historical.splitlines())


def test_07_current_register_row_is_ratified_without_stale_phase_1372_deferral() -> None:
    current = read(REGISTER)
    row = cdl_090_row(current)

    assert "| ratified |" in row
    assert "prelock_status: deferred_to_phase_1372" not in row
    assert "ratification_status: not_ratified_phase_1371" not in row
    assert "cdl_090_not_ratified_phase_1372" not in row
    assert "cdl_090_ratified_phase_1373" in row
    assert "docs/specs/ilc_cdl_090_ratification_evidence_1373_v0.1.md" in row
