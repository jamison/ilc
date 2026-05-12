from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

from ilc_core.ledger.cdl048_conversion_sweeper_runtime import (
    convert_ecu_lot,
    conversion_receipt_payload,
    empty_conversion_sweeper_state,
    register_ecu_lot,
)
from ilc_core.ledger.claimability_proof_binding_runtime import (
    build_claimability_proof_binding,
    claimability_proof_payload,
)
from ilc_core.sidecars.claimability_receipt_verifier import (
    ACCEPTED_LOCAL_ONLY_DECISION,
    REJECTED_DECISION,
    ClaimabilityReceiptVerifierError,
    build_claimability_verifier_presentation,
    canonical_decision_json,
    canonical_json,
    verify_claimability_receipt_presentation,
)


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "ilc_core/sidecars/claimability_receipt_verifier.py"
SPEC_PATH = (
    ROOT / "docs/specs/ilc_proof_binding_canonical_hash_negative_path_tests_1306_v0.1.md"
)
WALKTHROUGH_PATH = (
    ROOT
    / "docs/phases/phase_1306_proof_binding_canonical_hash_negative_path_tests_walkthrough.md"
)
STATUS_PATH = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX_PATH = ROOT / "docs/PLANNING_INDEX.md"
CAPSULE_PATH = ROOT / "docs/specs/ilc_antigravity_context_capsule_v5.53.md"
ROADMAP_PATH = ROOT / "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md"
PACKAGING_GATE_PATH = ROOT / "docs/architecture/ilc_public_rc_packaging_architecture_gate_v0.1.md"

REQUIRED_TOKENS = [
    "proof_binding_canonical_hash_negative_path_tests_phase_1306.v0.1",
    "forged_receipt_negative_paths_hardened_phase_1306",
    "canonical_json_exact_numeric_proof_safety_hardened_phase_1306",
    "replay_nullifier_duplicate_claim_policy_still_gated_phase_1306",
    "phase_1307_sidecar_registry_manifest_profile_hardening_next",
    "public_rc_remains_blocked_after_phase_1306",
]


def _valid_presentation() -> dict:
    agent_id = "agent:phase-1306-proof-negative-paths"
    epoch_id = "epoch-1306"
    wallet_state_root = f"wallet_state_sha256:{'a' * 64}"
    settled_runtime_root = f"settled_runtime_sha256:{'b' * 64}"
    history_digest = f"history_sha256:{'c' * 64}"

    state = register_ecu_lot(
        empty_conversion_sweeper_state(),
        lot_id="lot-phase-1306",
        agent_id=agent_id,
        amount_ecu="13",
        issue_epoch=10,
        origin="phase-1306-test-fixture",
        funding_provenance=("phase-1306-local-only",),
    )
    result = convert_ecu_lot(
        state,
        lot_id="lot-phase-1306",
        agent_id=agent_id,
        conversion_epoch=12,
        settled_runtime_epoch=12,
        wallet_state_root=wallet_state_root,
        settled_runtime_root=settled_runtime_root,
    )
    conversion_receipt = conversion_receipt_payload(result.receipt)
    latest_balance_receipt = {
        "balance_after_ilc": "13",
        "epoch_id": epoch_id,
        "reward_delta_ilc": "0",
        "settlement_status": "applied",
    }
    proof_binding = build_claimability_proof_binding(
        agent_id=agent_id,
        epoch_id=epoch_id,
        settled_runtime_root=settled_runtime_root,
        wallet_state_root=wallet_state_root,
        latest_balance_receipt=latest_balance_receipt,
        history_digest=history_digest,
        conversion_receipt=conversion_receipt,
    )
    return build_claimability_verifier_presentation(
        canonical_agent_identity=agent_id,
        epoch_id=epoch_id,
        settled_runtime_root=settled_runtime_root,
        wallet_state_root=wallet_state_root,
        latest_balance_receipt=latest_balance_receipt,
        history_digest=history_digest,
        claimability_proof=claimability_proof_payload(proof_binding),
        conversion_receipt=conversion_receipt,
    )


def _sha256_payload(payload: dict) -> str:
    rendered = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(rendered.encode("utf-8")).hexdigest()


def _assert_rejected(presentation: dict, expected_reason: str) -> None:
    decision = verify_claimability_receipt_presentation(presentation)

    assert decision["decision"] == REJECTED_DECISION
    assert decision["public_api_enabled"] is False
    assert decision["receipt_verifier_public_serving_enabled"] is False
    assert decision["public_claimability_activated"] is False
    assert decision["wallet_withdrawal_enabled"] is False
    assert decision["ecu_mint_authorized"] is False
    assert decision["ilc_settlement_authorized"] is False
    assert decision["rejection_reasons"] == [expected_reason]


def test_phase_1306_rejects_forged_receipt_and_proof_binding_mutations() -> None:
    cases: list[tuple[str, dict, str]] = []

    forged_receipt_amount = _valid_presentation()
    forged_receipt_amount["conversion_receipt"]["amount_ecu"] = "14"
    cases.append(
        (
            "forged conversion receipt amount",
            forged_receipt_amount,
            "claimability_conversion_receipt_hash_mismatch_phase_1305",
        )
    )

    forged_receipt_ref = _valid_presentation()
    forged_receipt_ref["conversion_receipt_sha256"] = "0" * 64
    cases.append(
        (
            "forged conversion receipt ref",
            forged_receipt_ref,
            "claimability_conversion_receipt_hash_mismatch_phase_1305",
        )
    )

    forged_conversion_key = _valid_presentation()
    forged_conversion_key["conversion_key_sha256"] = "0" * 64
    cases.append(
        (
            "forged conversion key",
            forged_conversion_key,
            "claimability_conversion_key_mismatch_phase_1305",
        )
    )

    forged_proof_hash = _valid_presentation()
    forged_proof_hash["claimability_proof"]["proof_binding_sha256"] = "0" * 64
    cases.append(
        (
            "forged proof binding hash",
            forged_proof_hash,
            "claimability_proof_hash_mismatch_phase_1305",
        )
    )

    forged_proof_ref = _valid_presentation()
    forged_proof_ref["claimability_proof_ref"] = f"claimability_proof_sha256:{'0' * 64}"
    cases.append(
        (
            "forged proof ref",
            forged_proof_ref,
            "claimability_proof_ref_mismatch_phase_1305",
        )
    )

    nested_balance_mismatch = _valid_presentation()
    nested_balance_mismatch["claimability_proof"]["latest_balance_receipt"] = dict(
        nested_balance_mismatch["claimability_proof"]["latest_balance_receipt"]
    )
    nested_balance_mismatch["claimability_proof"]["latest_balance_receipt"][
        "balance_after_ilc"
    ] = "12"
    cases.append(
        (
            "nested proof balance receipt mismatch",
            nested_balance_mismatch,
            "claimability_proof_balance_receipt_mismatch_phase_1305",
        )
    )

    for _label, presentation, expected_reason in cases:
        _assert_rejected(presentation, expected_reason)


def test_phase_1306_rejects_root_namespace_drift_and_receipt_ref_drift() -> None:
    wrong_wallet_namespace = _valid_presentation()
    wrong_wallet_namespace["wallet_state_root"] = f"settled_runtime_sha256:{'d' * 64}"
    _assert_rejected(
        wrong_wallet_namespace,
        "claimability_wallet_state_root_invalid_phase_1305",
    )

    wrong_settled_namespace = _valid_presentation()
    wrong_settled_namespace["settled_runtime_root"] = f"wallet_state_sha256:{'e' * 64}"
    _assert_rejected(
        wrong_settled_namespace,
        "claimability_settled_runtime_root_invalid_phase_1305",
    )

    latest_balance_ref_drift = _valid_presentation()
    latest_balance_ref_drift["latest_balance_receipt_ref"] = f"balance_receipt_sha256:{'f' * 64}"
    _assert_rejected(
        latest_balance_ref_drift,
        "claimability_latest_balance_receipt_ref_mismatch_phase_1305",
    )


def test_phase_1306_rejects_noncanonical_exact_numeric_inputs() -> None:
    decimal_scale_drift = _valid_presentation()
    decimal_scale_drift["latest_balance_receipt"]["balance_after_ilc"] = "13.0"
    _assert_rejected(
        decimal_scale_drift,
        "claimability_latest_balance_receipt_invalid_phase_1305",
    )

    decimal_exponent_drift = _valid_presentation()
    decimal_exponent_drift["conversion_receipt"]["amount_ecu"] = "1.3E+1"
    _assert_rejected(
        decimal_exponent_drift,
        "claimability_conversion_receipt_invalid_phase_1305",
    )

    non_finite_decimal = _valid_presentation()
    non_finite_decimal["latest_balance_receipt"]["reward_delta_ilc"] = "Infinity"
    _assert_rejected(
        non_finite_decimal,
        "claimability_latest_balance_receipt_invalid_phase_1305",
    )

    float_payload = _valid_presentation()
    float_payload["latest_balance_receipt"]["balance_after_ilc"] = 13.0
    _assert_rejected(
        float_payload,
        "claimability_payload_float_forbidden_phase_1305",
    )


def test_phase_1306_canonical_json_rejects_non_json_types_and_memory_edges() -> None:
    with pytest.raises(ClaimabilityReceiptVerifierError) as tuple_exc:
        canonical_json({"tuple_is_not_json": ("value",)})
    assert tuple_exc.value.token == "claimability_payload_type_invalid_phase_1305"

    with pytest.raises(ClaimabilityReceiptVerifierError) as key_exc:
        canonical_json({1: "non-string key"})
    assert key_exc.value.token == "claimability_payload_key_invalid_phase_1305"

    with pytest.raises(ClaimabilityReceiptVerifierError) as key_size_exc:
        canonical_json({"k" * 4097: "oversized key"})
    assert key_size_exc.value.token == "claimability_payload_text_too_large_phase_1305"

    cyclic: list[object] = []
    cyclic.append(cyclic)
    with pytest.raises(ClaimabilityReceiptVerifierError) as cycle_exc:
        canonical_json({"cycle": cyclic})
    assert cycle_exc.value.token == "claimability_payload_cycle_forbidden_phase_1305"


def test_phase_1306_canonical_decision_rejects_hash_and_semantic_drift() -> None:
    decision = verify_claimability_receipt_presentation(_valid_presentation())
    assert decision["decision"] == ACCEPTED_LOCAL_ONLY_DECISION

    hash_forgery = dict(decision)
    hash_forgery["latest_balance_receipt_ref"] = f"balance_receipt_sha256:{'0' * 64}"
    with pytest.raises(ClaimabilityReceiptVerifierError) as hash_exc:
        canonical_decision_json(hash_forgery)
    assert hash_exc.value.token == "claimability_decision_hash_mismatch_phase_1305"

    semantic_forgery = dict(decision)
    semantic_forgery["public_claimability_activated"] = True
    body = dict(semantic_forgery)
    body.pop("canonical_decision_sha256")
    semantic_forgery["canonical_decision_sha256"] = _sha256_payload(body)
    with pytest.raises(ClaimabilityReceiptVerifierError) as semantic_exc:
        canonical_decision_json(semantic_forgery)
    assert (
        semantic_exc.value.token
        == "claimability_decision_activation_flag_forbidden_phase_1305"
    )


def test_phase_1306_replay_nullifier_and_duplicate_claim_policy_remain_gated() -> None:
    decision = verify_claimability_receipt_presentation(_valid_presentation())

    assert decision["decision"] == ACCEPTED_LOCAL_ONLY_DECISION
    assert "replay_nullifier_policy_not_activated_phase_1305" in decision[
        "public_mode_blockers"
    ]
    assert "duplicate_claim_registry_not_activated_phase_1305" in decision[
        "public_mode_blockers"
    ]
    assert decision["public_claimability_activated"] is False
    assert decision["receipt_verifier_public_serving_enabled"] is False


def test_phase_1306_docs_and_source_record_tokens_nonclaims_and_no_public_surface() -> None:
    corpus = "\n".join(
        path.read_text()
        for path in (
            MODULE_PATH,
            SPEC_PATH,
            WALKTHROUGH_PATH,
            STATUS_PATH,
            PLANNING_INDEX_PATH,
            CAPSULE_PATH,
            ROADMAP_PATH,
            PACKAGING_GATE_PATH,
        )
    )

    for token in REQUIRED_TOKENS:
        assert token in corpus
    for non_claim in (
        "no public verifier service",
        "no public claimability activation",
        "no wallet withdrawal",
        "no ECU minting",
        "no ILC settlement",
        "Phase 1307 is sensitive and requires explicit `GO Phase 1307`",
        "deterministic scaffold compilation",
        "compile_into_contract",
        "strip_from_export",
    ):
        assert non_claim in corpus

    source = MODULE_PATH.read_text()
    for forbidden in (
        "from fastapi",
        "FastAPI(",
        "import socket",
        "requests.",
        "aiohttp",
        "uvicorn",
        ".bind(",
        ".listen(",
    ):
        assert forbidden not in source


def test_phase_1306_fixture_builder_remains_stable_under_copy_mutations() -> None:
    original = _valid_presentation()
    mutated = copy.deepcopy(original)
    mutated["transport_principal_ref"] = "transport_principal_ref:mutated"

    assert original["transport_principal_ref"] != mutated["transport_principal_ref"]
    _assert_rejected(
        mutated,
        "claimability_presentation_id_mismatch_phase_1305",
    )
