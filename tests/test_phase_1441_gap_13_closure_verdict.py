from __future__ import annotations

from pathlib import Path

from ilc_core.distribution.package_profiles import (
    GAP_13_CLOSED_TOKEN,
    GAP_13_CLOSURE_VERDICT_PASS_TOKEN,
)
from ilc_core.sidecars.claimability_receipt_verifier import (
    CLAIMABILITY_VERIFIER_LOCAL_ONLY_TOKEN,
    PUBLIC_CLAIMABILITY_ACTIVATION_NOT_AUTHORIZED_TOKEN,
    RECEIPT_VERIFIER_PUBLIC_SERVING_NOT_ENABLED_TOKEN,
    claimability_receipt_verifier_manifest,
    claimability_receipt_verifier_tokens,
)


ROOT = Path(__file__).resolve().parents[1]
SEQUENCE_LOCK = ROOT / "docs/specs/ilc_phase_1429_1458_sequence_lock_v0.1.md"

EVIDENCE_PATHS = (
    ROOT / "ilc_core/sidecars/cdl088_claimability_activation.py",
    ROOT / "ilc_core/sidecars/public_verifier_api_activation.py",
    ROOT / "ilc_core/sidecars/claimability_receipt_verifier.py",
    ROOT / "ilc_core/epoch/allocation_distributor_runtime.py",
    ROOT / "ilc_core/epoch/ecu_price_clamp_runtime.py",
    ROOT / "ilc_core/protocol/event_log_retention.py",
    ROOT / "tests/test_phase_1440_claimability_integration_tests.py",
    ROOT / "docs/phases/phase_1438_cdl088_public_claimability_activation_walkthrough.md",
    ROOT / "docs/phases/phase_1439_public_verifier_api_activation_walkthrough.md",
    ROOT / "docs/phases/phase_1440_claimability_integration_tests_security_review_walkthrough.md",
    ROOT / "docs/phases/STATUS.md",
)

REQUIRED_UPSTREAM_TOKENS = (
    "public_claimability_activated_phase_1438",
    "public_verifier_api_activated_phase_1439",
    "claimability_integration_tests_phase_1440",
    "security_review_gate_passed_phase_1440",
    "finding_1_rounding_residual_cap_blocked_resolved_phase_1440",
    "finding_3_price_clamp_width_derived_resolved_phase_1440",
    "finding_11_nullifier_expire_stale_public_path_resolved_phase_1440",
    "finding_13_negative_int_constraint_documented_resolved_phase_1440",
    "finding_14_event_log_retention_provenance_guard_resolved_phase_1440",
    "cdl_088_is_public_claimability_api_authority_phase_1389a",
)


def _corpus(paths: tuple[Path, ...] = EVIDENCE_PATHS) -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in paths)


def test_phase_1441_required_gap_13_input_tokens_are_present() -> None:
    corpus = _corpus()

    for token in REQUIRED_UPSTREAM_TOKENS:
        assert token in corpus, token


def test_phase_1441_closure_constants_are_exact() -> None:
    assert GAP_13_CLOSED_TOKEN == "gap_13_closed_phase_1441"
    assert GAP_13_CLOSURE_VERDICT_PASS_TOKEN == "gap_13_closure_verdict_pass_phase_1441"


def test_phase_1441_pre_activation_blockers_cleared_without_value_activation() -> None:
    tokens = claimability_receipt_verifier_tokens()
    manifest = claimability_receipt_verifier_manifest()

    assert PUBLIC_CLAIMABILITY_ACTIVATION_NOT_AUTHORIZED_TOKEN not in tokens
    assert CLAIMABILITY_VERIFIER_LOCAL_ONLY_TOKEN not in tokens
    assert RECEIPT_VERIFIER_PUBLIC_SERVING_NOT_ENABLED_TOKEN not in tokens
    assert manifest["public_claimability_activated"] is True
    assert manifest["public_api_enabled"] is True
    assert manifest["receipt_verifier_public_serving_enabled"] is True
    assert manifest["ecu_mint_authorized"] is False
    assert manifest["ilc_settlement_authorized"] is False
    assert manifest["wallet_ops_authorized"] is False


def test_phase_1441_sequence_lock_records_gap_13_pass_verdict() -> None:
    sequence_lock = SEQUENCE_LOCK.read_text(encoding="utf-8")

    assert "Phase 1441 Completion Addendum" in sequence_lock
    assert GAP_13_CLOSED_TOKEN in sequence_lock
    assert GAP_13_CLOSURE_VERDICT_PASS_TOKEN in sequence_lock
    for token in REQUIRED_UPSTREAM_TOKENS:
        assert token in sequence_lock, token
    for non_activation in (
        "ecu_mint_authorized=false",
        "ilc_settlement_authorized=false",
        "wallet_ops_authorized=false",
        "public_rc_activated=false",
        "epoch_transition_triggered=false",
    ):
        assert non_activation in sequence_lock
