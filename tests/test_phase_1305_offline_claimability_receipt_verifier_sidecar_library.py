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
    CLAIMABILITY_VERIFIER_LOCAL_ONLY_TOKEN,
    OFFLINE_CLAIMABILITY_RECEIPT_VERIFIER_VERSION,
    PHASE_1306_NEXT_TOKEN,
    PUBLIC_CLAIMABILITY_ACTIVATED_PHASE_1438_TOKEN,
    PUBLIC_CLAIMABILITY_ACTIVATION_NOT_AUTHORIZED_TOKEN,
    PUBLIC_RC_REMAINS_BLOCKED_TOKEN,
    RECEIPT_VERIFIER_PUBLIC_SERVING_NOT_ENABLED_TOKEN,
    REJECTED_DECISION,
    ClaimabilityReceiptVerifierError,
    build_claimability_verifier_presentation,
    canonical_decision_json,
    claimability_receipt_verifier_manifest,
    verify_claimability_receipt_presentation,
)


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "ilc_core/sidecars/claimability_receipt_verifier.py"
SPEC_PATH = (
    ROOT / "docs/specs/ilc_offline_claimability_receipt_verifier_sidecar_1305_v0.1.md"
)
WALKTHROUGH_PATH = (
    ROOT
    / "docs/phases/phase_1305_offline_claimability_receipt_verifier_sidecar_library_walkthrough.md"
)
STATUS_PATH = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX_PATH = ROOT / "docs/PLANNING_INDEX.md"
CAPSULE_PATH = ROOT / "docs/specs/ilc_antigravity_context_capsule_v5.53.md"

REQUIRED_TOKENS = [
    OFFLINE_CLAIMABILITY_RECEIPT_VERIFIER_VERSION,
    CLAIMABILITY_VERIFIER_LOCAL_ONLY_TOKEN,
    RECEIPT_VERIFIER_PUBLIC_SERVING_NOT_ENABLED_TOKEN,
    PUBLIC_CLAIMABILITY_ACTIVATED_PHASE_1438_TOKEN,
    PHASE_1306_NEXT_TOKEN,
    PUBLIC_RC_REMAINS_BLOCKED_TOKEN,
]


def _valid_presentation() -> dict:
    agent_id = "agent:phase-1305-local-verifier"
    epoch_id = "epoch-1305"
    wallet_state_root = f"wallet_state_sha256:{'a' * 64}"
    settled_runtime_root = f"settled_runtime_sha256:{'b' * 64}"
    history_digest = f"history_sha256:{'c' * 64}"

    state = register_ecu_lot(
        empty_conversion_sweeper_state(),
        lot_id="lot-phase-1305",
        agent_id=agent_id,
        amount_ecu="13",
        issue_epoch=10,
        origin="phase-1305-test-fixture",
        funding_provenance=("phase-1305-local-only",),
    )
    result = convert_ecu_lot(
        state,
        lot_id="lot-phase-1305",
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


def test_local_verifier_accepts_canonical_presentation_without_public_serving() -> None:
    presentation = _valid_presentation()

    decision = verify_claimability_receipt_presentation(presentation)

    assert decision["decision"] == ACCEPTED_LOCAL_ONLY_DECISION
    assert decision["rejection_reasons"] == []
    assert decision["public_api_enabled"] is False
    assert decision["receipt_verifier_public_serving_enabled"] is False
    assert decision["public_claimability_activated"] is False
    assert decision["non_loopback_claimability_api_enabled"] is False
    assert decision["wallet_withdrawal_enabled"] is False
    assert decision["wallet_transfer_enabled"] is False
    assert decision["wallet_spend_enabled"] is False
    assert decision["ecu_mint_authorized"] is False
    assert decision["ilc_settlement_authorized"] is False
    assert decision["public_mode_blockers"] == []
    assert canonical_decision_json(decision).startswith('{"canonical_decision_sha256"')


def test_local_verifier_rejects_public_activation_flags() -> None:
    presentation = _valid_presentation()
    presentation["public_claimability_activated"] = True

    decision = verify_claimability_receipt_presentation(presentation)

    assert decision["decision"] == REJECTED_DECISION
    assert decision["public_api_enabled"] is False
    assert decision["public_claimability_activated"] is False
    assert decision["rejection_reasons"] == [
        "claimability_activation_flag_forbidden_phase_1305"
    ]


def test_local_verifier_rejects_forged_conversion_receipts() -> None:
    presentation = _valid_presentation()
    presentation["conversion_receipt"]["amount_ecu"] = "14"

    decision = verify_claimability_receipt_presentation(presentation)

    assert decision["decision"] == REJECTED_DECISION
    assert decision["rejection_reasons"] == [
        "claimability_conversion_receipt_hash_mismatch_phase_1305"
    ]


def test_local_verifier_rejects_float_or_non_finite_numeric_inputs() -> None:
    float_presentation = _valid_presentation()
    float_presentation["latest_balance_receipt"]["balance_after_ilc"] = 13.0

    float_decision = verify_claimability_receipt_presentation(float_presentation)

    assert float_decision["decision"] == REJECTED_DECISION
    assert float_decision["rejection_reasons"] == [
        "claimability_payload_float_forbidden_phase_1305"
    ]

    nan_presentation = _valid_presentation()
    nan_presentation["latest_balance_receipt"]["balance_after_ilc"] = "NaN"

    nan_decision = verify_claimability_receipt_presentation(nan_presentation)

    assert nan_decision["decision"] == REJECTED_DECISION
    assert nan_decision["rejection_reasons"] == [
        "claimability_latest_balance_receipt_invalid_phase_1305"
    ]


def test_local_verifier_manifest_and_source_have_no_public_serving_surface() -> None:
    manifest = claimability_receipt_verifier_manifest()
    source = MODULE_PATH.read_text()

    assert manifest["local_only"] is True
    assert manifest["public_api_enabled"] is False
    assert manifest["receipt_verifier_public_serving_enabled"] is False
    assert manifest["non_loopback_claimability_api_enabled"] is False
    assert manifest["public_claimability_activated"] is True
    assert manifest["tokens"][: len(REQUIRED_TOKENS)] == REQUIRED_TOKENS
    assert PUBLIC_CLAIMABILITY_ACTIVATION_NOT_AUTHORIZED_TOKEN not in manifest["tokens"]
    assert "claimability_verifier_public_mode_ready_phase_1389b" in manifest["tokens"]
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


def test_phase_1305_tokens_and_non_claims_are_recorded() -> None:
    corpus = "\n".join(
        path.read_text()
        for path in (
            MODULE_PATH,
            SPEC_PATH,
            WALKTHROUGH_PATH,
            STATUS_PATH,
            PLANNING_INDEX_PATH,
            CAPSULE_PATH,
        )
    )

    for token in REQUIRED_TOKENS:
        assert token in corpus
    for non_claim in (
        "no public API",
        "no public verifier service",
        "no public claimability activation",
        "no wallet withdrawal",
        "no ECU minting",
        "no ILC settlement",
        "Phase 1306 is sensitive and requires explicit `GO Phase 1306`",
    ):
        assert non_claim in corpus


def test_presentation_id_detects_canonical_body_mutation() -> None:
    presentation = _valid_presentation()
    mutated = copy.deepcopy(presentation)
    mutated["transport_principal_ref"] = "transport_principal_ref:mutated"

    decision = verify_claimability_receipt_presentation(mutated)

    assert decision["decision"] == REJECTED_DECISION
    assert decision["rejection_reasons"] == [
        "claimability_presentation_id_mismatch_phase_1305"
    ]


def test_audit_rejects_noncanonical_trimmed_fields_and_duplicate_tokens() -> None:
    padded = _valid_presentation()
    padded["canonical_agent_identity"] = f"{padded['canonical_agent_identity']} "

    padded_decision = verify_claimability_receipt_presentation(padded)

    assert padded_decision["decision"] == REJECTED_DECISION
    assert padded_decision["rejection_reasons"] == [
        "claimability_presentation_agent_invalid_phase_1305"
    ]

    duplicate_token = _valid_presentation()
    duplicate_token["tokens"] = [*duplicate_token["tokens"], duplicate_token["tokens"][0]]

    duplicate_decision = verify_claimability_receipt_presentation(duplicate_token)

    assert duplicate_decision["decision"] == REJECTED_DECISION
    assert duplicate_decision["rejection_reasons"] == [
        "claimability_presentation_tokens_invalid_phase_1305"
    ]


def test_audit_canonical_decision_json_rejects_semantic_flag_forgery() -> None:
    decision = verify_claimability_receipt_presentation(_valid_presentation())
    forged = dict(decision)
    forged["public_api_enabled"] = True
    body = dict(forged)
    body.pop("canonical_decision_sha256")
    forged["canonical_decision_sha256"] = _sha256_payload(body)

    with pytest.raises(ClaimabilityReceiptVerifierError) as exc_info:
        canonical_decision_json(forged)

    assert exc_info.value.token == "claimability_decision_activation_flag_forbidden_phase_1305"
