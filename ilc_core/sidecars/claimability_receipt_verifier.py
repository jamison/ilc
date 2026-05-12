"""Phase 1305 local-only claimability receipt verifier sidecar substrate.

The verifier is intentionally an in-process/library boundary. It provides no
HTTP route, socket listener, bind helper, peer discovery, wallet action, ECU
mint, or ILC settlement authority.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from decimal import Decimal, InvalidOperation
from typing import Any


OFFLINE_CLAIMABILITY_RECEIPT_VERIFIER_VERSION = (
    "offline_claimability_receipt_verifier_sidecar_phase_1305.v0.1"
)
PHASE_1291_CONTRACT_VERSION = "public_claimability_verifier_contract_preflight_phase_1291.v0.1"
CLAIMABILITY_VERIFIER_LOCAL_ONLY_TOKEN = "claimability_verifier_local_only_no_api_phase_1305"
RECEIPT_VERIFIER_PUBLIC_SERVING_NOT_ENABLED_TOKEN = (
    "receipt_verifier_public_serving_not_enabled_phase_1305"
)
PUBLIC_CLAIMABILITY_ACTIVATION_NOT_AUTHORIZED_TOKEN = (
    "public_claimability_activation_not_authorized_phase_1305"
)
PHASE_1306_NEXT_TOKEN = "phase_1306_proof_binding_canonical_hash_negative_path_tests_next"
PUBLIC_RC_REMAINS_BLOCKED_TOKEN = "public_rc_remains_blocked_after_phase_1305"

ACCEPTED_LOCAL_ONLY_DECISION = "accepted_local_only_no_public_serving_phase_1305"
REJECTED_DECISION = "rejected_fail_closed_phase_1305"

CLAIMABILITY_PROOF_BINDING_RUNTIME_VERSION = (
    "claimability_proof_binding_runtime_boundary_phase_1275.v0.1"
)
CDL048_CONVERSION_SWEEPER_RUNTIME_VERSION = (
    "cdl048_conversion_sweeper_runtime_skeleton_phase_1274.v0.1"
)
CDL048_CONVERSION_DEADLINE_ISSUANCE_EPOCHS = 4
CONVERSION_TRANSITION = "cdl048_ecu_lot_internal_conversion_skeleton"

SETTLED_ROOT_WALLET_ROOT_RECEIPT_BINDING_TOKEN = (
    "settled_root_wallet_root_receipt_binding_recorded_phase_1275"
)
NON_LOOPBACK_CLAIMABILITY_API_BLOCKED_TOKEN = (
    "non_loopback_claimability_api_still_blocked_phase_1275"
)
PUBLIC_CLAIMABILITY_NOT_ACTIVATED_TOKEN = "public_claimability_not_activated_phase_1275"
CONVERSION_SWEEPER_NO_PUBLIC_CLAIMABILITY_TOKEN = (
    "conversion_sweeper_no_public_claimability_activation_phase_1274"
)
ECU_LOT_DEADLINE_ENFORCEMENT_TOKEN = (
    "ecu_lot_deadline_epoch_enforcement_recorded_phase_1274"
)
WALLET_WITHDRAWAL_TRANSFER_SPEND_BLOCKED_TOKEN = (
    "wallet_withdrawal_transfer_spend_still_blocked_phase_1274"
)

CLAIMABILITY_STATE = "proof_bound_local_only"
PRESENTATION_ID_PREFIX = "claimability_presentation_sha256"
CLAIMABILITY_PROOF_REF_PREFIX = "claimability_proof_sha256"
LATEST_BALANCE_RECEIPT_REF_PREFIX = "balance_receipt_sha256"
WALLET_STATE_ROOT_PREFIX = "wallet_state_sha256"
SETTLED_RUNTIME_ROOT_PREFIX = "settled_runtime_sha256"
HISTORY_DIGEST_PREFIX = "history_sha256"
CONVERSION_SWEEPER_STATE_ROOT_PREFIX = "cdl048_conversion_sweeper_state_sha256"

_HEX = frozenset("0123456789abcdef")
_MAX_CANONICAL_PAYLOAD_DEPTH = 32
_MAX_CANONICAL_PAYLOAD_NODES = 100_000
_MAX_TEXT_LENGTH = 4096
_MAX_CANONICAL_PAYLOAD_TEXT_BYTES = 1_000_000
_MAX_PROTOCOL_INT = 1_000_000_000_000
_MAX_DECIMAL_DIGITS = 128
_MAX_DECIMAL_SCALE = 128
_MAX_DECIMAL_ADJUSTED_EXPONENT = 128
_MAX_TOKEN_COUNT = 64
_MAX_REASON_COUNT = 64

_ACTIVATION_FIELDS = (
    "public_claimability_activated",
    "non_loopback_claimability_api_enabled",
    "wallet_withdrawal_enabled",
    "wallet_transfer_enabled",
    "wallet_spend_enabled",
    "ecu_mint_authorized",
    "ilc_settlement_authorized",
)

_CONVERSION_ACTIVATION_FIELDS = (
    "public_claimability_activated",
    "wallet_withdrawal_enabled",
    "wallet_transfer_enabled",
    "wallet_spend_enabled",
    "ecu_mint_authorized",
    "ilc_settlement_authorized",
)

_EXPECTED_PRESENTATION_KEYS = frozenset(
    {
        "canonical_agent_identity",
        "claimability_proof",
        "claimability_proof_ref",
        "contract_version",
        "conversion_deadline_epoch",
        "conversion_issuance_epoch",
        "conversion_key_sha256",
        "conversion_lot_id",
        "conversion_receipt",
        "conversion_receipt_sha256",
        "ecu_mint_authorized",
        "epoch_id",
        "history_digest",
        "ilc_settlement_authorized",
        "latest_balance_receipt",
        "latest_balance_receipt_ref",
        "non_loopback_claimability_api_enabled",
        "presentation_id",
        "public_claimability_activated",
        "settled_runtime_root",
        "tokens",
        "transport_principal_ref",
        "wallet_spend_enabled",
        "wallet_state_root",
        "wallet_transfer_enabled",
        "wallet_withdrawal_enabled",
    }
)

_EXPECTED_BALANCE_RECEIPT_KEYS = frozenset(
    {"balance_after_ilc", "epoch_id", "reward_delta_ilc", "settlement_status"}
)

_EXPECTED_CONVERSION_RECEIPT_KEYS = frozenset(
    {
        "agent_id",
        "amount_ecu",
        "conversion_epoch",
        "conversion_key_sha256",
        "conversion_state_transition",
        "deadline_epoch",
        "ecu_mint_authorized",
        "ilc_settlement_authorized",
        "issue_epoch",
        "lot_id",
        "public_claimability_activated",
        "receipt_sha256",
        "runtime_version",
        "settled_runtime_epoch",
        "settled_runtime_root",
        "sweeper_state_root_before",
        "tokens",
        "wallet_spend_enabled",
        "wallet_state_root",
        "wallet_transfer_enabled",
        "wallet_withdrawal_enabled",
    }
)

_EXPECTED_PROOF_KEYS = frozenset(
    {
        "agent_id",
        "canonical_agent_identity",
        "claimability_state",
        "conversion_deadline_epoch",
        "conversion_epoch",
        "conversion_key_sha256",
        "conversion_lot_id",
        "conversion_receipt",
        "conversion_receipt_sha256",
        "conversion_sweeper_state_root_before",
        "ecu_mint_authorized",
        "epoch_id",
        "history_digest",
        "ilc_settlement_authorized",
        "latest_balance_receipt",
        "latest_balance_receipt_ref",
        "non_loopback_claimability_api_enabled",
        "proof_binding_sha256",
        "public_claimability_activated",
        "runtime_version",
        "settled_runtime_root",
        "tokens",
        "transport_principal_required_before_non_loopback",
        "wallet_spend_enabled",
        "wallet_state_root",
        "wallet_transfer_enabled",
        "wallet_withdrawal_enabled",
    }
)

_EXPECTED_DECISION_KEYS = frozenset(
    {
        "canonical_decision_sha256",
        "claimability_proof_ref",
        "contract_version",
        "conversion_receipt_sha256",
        "decision",
        "ecu_mint_authorized",
        "ilc_settlement_authorized",
        "latest_balance_receipt_ref",
        "non_loopback_claimability_api_enabled",
        "presentation_id",
        "public_api_enabled",
        "public_claimability_activated",
        "public_mode_blockers",
        "receipt_verifier_public_serving_enabled",
        "rejection_reasons",
        "tokens",
        "verifier_version",
        "wallet_spend_enabled",
        "wallet_transfer_enabled",
        "wallet_withdrawal_enabled",
    }
)

_DECISION_FALSE_FIELDS = (
    "ecu_mint_authorized",
    "ilc_settlement_authorized",
    "non_loopback_claimability_api_enabled",
    "public_api_enabled",
    "public_claimability_activated",
    "receipt_verifier_public_serving_enabled",
    "wallet_spend_enabled",
    "wallet_transfer_enabled",
    "wallet_withdrawal_enabled",
)

_PUBLIC_MODE_BLOCKERS = (
    "public_claimability_api_authority_missing_phase_1305",
    "replay_nullifier_policy_not_activated_phase_1305",
    "duplicate_claim_registry_not_activated_phase_1305",
    "public_safe_disclosure_schema_not_final_phase_1305",
    "transport_principal_public_path_not_activated_phase_1305",
)


class ClaimabilityReceiptVerifierError(ValueError):
    """Fail-closed local verifier error with a stable token."""

    def __init__(self, token: str, message: str) -> None:
        super().__init__(message)
        self.token = token


def claimability_receipt_verifier_tokens() -> list[str]:
    return [
        OFFLINE_CLAIMABILITY_RECEIPT_VERIFIER_VERSION,
        CLAIMABILITY_VERIFIER_LOCAL_ONLY_TOKEN,
        RECEIPT_VERIFIER_PUBLIC_SERVING_NOT_ENABLED_TOKEN,
        PUBLIC_CLAIMABILITY_ACTIVATION_NOT_AUTHORIZED_TOKEN,
        PHASE_1306_NEXT_TOKEN,
        PUBLIC_RC_REMAINS_BLOCKED_TOKEN,
    ]


def claimability_receipt_verifier_manifest() -> dict[str, Any]:
    """Return deterministic local-only sidecar metadata."""

    payload = {
        "allowed_binding_modes": [
            "in_process_import",
            "local_cli_subprocess",
            "private_loopback_or_private_overlay_when_authorized_by_harness",
        ],
        "contract_version": OFFLINE_CLAIMABILITY_RECEIPT_VERIFIER_VERSION,
        "local_only": True,
        "non_loopback_claimability_api_enabled": False,
        "public_api_enabled": False,
        "public_claimability_activated": False,
        "receipt_verifier_public_serving_enabled": False,
        "source_contract_version": PHASE_1291_CONTRACT_VERSION,
        "tokens": claimability_receipt_verifier_tokens(),
    }
    _reject_unsafe_json_tree(payload)
    return payload


def build_claimability_verifier_presentation(
    *,
    canonical_agent_identity: str,
    epoch_id: str,
    settled_runtime_root: str,
    wallet_state_root: str,
    latest_balance_receipt: Mapping[str, Any],
    history_digest: str,
    claimability_proof: Mapping[str, Any],
    conversion_receipt: Mapping[str, Any],
    transport_principal_ref: str = "transport_principal_ref:local_only_not_activated_phase_1305",
) -> dict[str, Any]:
    """Build a canonical local verifier presentation with a content id."""

    agent = _require_text(
        canonical_agent_identity,
        token="claimability_presentation_agent_invalid_phase_1305",
    )
    epoch = _require_text(epoch_id, token="claimability_presentation_epoch_invalid_phase_1305")
    settled_root = _require_prefixed_sha256(
        settled_runtime_root,
        prefix=SETTLED_RUNTIME_ROOT_PREFIX,
        token="claimability_settled_runtime_root_invalid_phase_1305",
    )
    wallet_root = _require_prefixed_sha256(
        wallet_state_root,
        prefix=WALLET_STATE_ROOT_PREFIX,
        token="claimability_wallet_state_root_invalid_phase_1305",
    )
    history = _require_sha256_or_prefixed_sha256(
        history_digest,
        prefix=HISTORY_DIGEST_PREFIX,
        token="claimability_history_digest_invalid_phase_1305",
    )
    balance_receipt = _normalize_latest_balance_receipt(latest_balance_receipt, epoch_id=epoch)
    receipt = _normalize_conversion_receipt(
        conversion_receipt,
        canonical_agent_identity=agent,
        settled_runtime_root=settled_root,
        wallet_state_root=wallet_root,
    )
    proof = _normalize_claimability_proof(
        claimability_proof,
        canonical_agent_identity=agent,
        epoch_id=epoch,
        settled_runtime_root=settled_root,
        wallet_state_root=wallet_root,
        latest_balance_receipt=balance_receipt,
        history_digest=history,
        conversion_receipt=receipt,
    )
    body = {
        "canonical_agent_identity": agent,
        "claimability_proof": proof,
        "claimability_proof_ref": _claimability_proof_ref(proof),
        "contract_version": OFFLINE_CLAIMABILITY_RECEIPT_VERIFIER_VERSION,
        "conversion_deadline_epoch": receipt["deadline_epoch"],
        "conversion_issuance_epoch": receipt["issue_epoch"],
        "conversion_key_sha256": receipt["conversion_key_sha256"],
        "conversion_lot_id": receipt["lot_id"],
        "conversion_receipt": receipt,
        "conversion_receipt_sha256": receipt["receipt_sha256"],
        "ecu_mint_authorized": False,
        "epoch_id": epoch,
        "history_digest": history,
        "ilc_settlement_authorized": False,
        "latest_balance_receipt": balance_receipt,
        "latest_balance_receipt_ref": _latest_balance_receipt_ref(balance_receipt),
        "non_loopback_claimability_api_enabled": False,
        "public_claimability_activated": False,
        "settled_runtime_root": settled_root,
        "tokens": claimability_receipt_verifier_tokens(),
        "transport_principal_ref": _require_text(
            transport_principal_ref,
            token="claimability_transport_principal_ref_invalid_phase_1305",
        ),
        "wallet_spend_enabled": False,
        "wallet_state_root": wallet_root,
        "wallet_transfer_enabled": False,
        "wallet_withdrawal_enabled": False,
    }
    presentation = {"presentation_id": _presentation_id_for_body(body), **body}
    return _normalize_presentation(presentation)


def verify_claimability_receipt_presentation(presentation: Mapping[str, Any]) -> dict[str, Any]:
    """Verify a claimability presentation locally and return a canonical decision."""

    try:
        normalized = _normalize_presentation(presentation)
    except ClaimabilityReceiptVerifierError as exc:
        return _build_decision(
            decision=REJECTED_DECISION,
            presentation_id=_safe_presentation_id(presentation),
            claimability_proof_ref=None,
            latest_balance_receipt_ref=None,
            conversion_receipt_sha256=None,
            rejection_reasons=[exc.token],
        )

    return _build_decision(
        decision=ACCEPTED_LOCAL_ONLY_DECISION,
        presentation_id=normalized["presentation_id"],
        claimability_proof_ref=normalized["claimability_proof_ref"],
        latest_balance_receipt_ref=normalized["latest_balance_receipt_ref"],
        conversion_receipt_sha256=normalized["conversion_receipt_sha256"],
        rejection_reasons=[],
    )


def canonical_decision_json(decision: Mapping[str, Any]) -> str:
    payload = _normalize_decision(decision)
    return canonical_json(payload)


def canonical_json(payload: Any) -> str:
    _reject_unsafe_json_tree(payload)
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _normalize_presentation(presentation: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(presentation, Mapping):
        raise ClaimabilityReceiptVerifierError(
            "claimability_presentation_not_object_phase_1305",
            "presentation must be an object",
        )
    _reject_unsafe_json_tree(presentation)
    payload = dict(presentation)
    if frozenset(payload) != _EXPECTED_PRESENTATION_KEYS:
        raise ClaimabilityReceiptVerifierError(
            "claimability_presentation_fields_invalid_phase_1305",
            "presentation fields do not match the Phase 1305 local verifier contract",
        )
    if payload["contract_version"] != OFFLINE_CLAIMABILITY_RECEIPT_VERIFIER_VERSION:
        raise ClaimabilityReceiptVerifierError(
            "claimability_contract_version_invalid_phase_1305",
            "presentation contract_version is not the Phase 1305 local verifier contract",
        )
    tokens = _normalize_token_list(
        payload["tokens"],
        required=claimability_receipt_verifier_tokens(),
        token="claimability_presentation_tokens_invalid_phase_1305",
    )
    for field in _ACTIVATION_FIELDS:
        _require_false(
            payload[field],
            token="claimability_activation_flag_forbidden_phase_1305",
        )
    agent = _require_text(
        payload["canonical_agent_identity"],
        token="claimability_presentation_agent_invalid_phase_1305",
    )
    epoch = _require_text(payload["epoch_id"], token="claimability_presentation_epoch_invalid_phase_1305")
    settled_root = _require_prefixed_sha256(
        payload["settled_runtime_root"],
        prefix=SETTLED_RUNTIME_ROOT_PREFIX,
        token="claimability_settled_runtime_root_invalid_phase_1305",
    )
    wallet_root = _require_prefixed_sha256(
        payload["wallet_state_root"],
        prefix=WALLET_STATE_ROOT_PREFIX,
        token="claimability_wallet_state_root_invalid_phase_1305",
    )
    history = _require_sha256_or_prefixed_sha256(
        payload["history_digest"],
        prefix=HISTORY_DIGEST_PREFIX,
        token="claimability_history_digest_invalid_phase_1305",
    )
    balance_receipt = _normalize_latest_balance_receipt(
        payload["latest_balance_receipt"],
        epoch_id=epoch,
    )
    expected_balance_ref = _latest_balance_receipt_ref(balance_receipt)
    if payload["latest_balance_receipt_ref"] != expected_balance_ref:
        raise ClaimabilityReceiptVerifierError(
            "claimability_latest_balance_receipt_ref_mismatch_phase_1305",
            "latest_balance_receipt_ref does not match canonical balance receipt",
        )
    receipt = _normalize_conversion_receipt(
        payload["conversion_receipt"],
        canonical_agent_identity=agent,
        settled_runtime_root=settled_root,
        wallet_state_root=wallet_root,
    )
    if payload["conversion_receipt_sha256"] != receipt["receipt_sha256"]:
        raise ClaimabilityReceiptVerifierError(
            "claimability_conversion_receipt_hash_mismatch_phase_1305",
            "conversion_receipt_sha256 does not match conversion receipt",
        )
    if payload["conversion_key_sha256"] != receipt["conversion_key_sha256"]:
        raise ClaimabilityReceiptVerifierError(
            "claimability_conversion_key_mismatch_phase_1305",
            "conversion_key_sha256 does not match conversion receipt",
        )
    if payload["conversion_lot_id"] != receipt["lot_id"]:
        raise ClaimabilityReceiptVerifierError(
            "claimability_conversion_lot_mismatch_phase_1305",
            "conversion_lot_id does not match conversion receipt",
        )
    if payload["conversion_issuance_epoch"] != receipt["issue_epoch"]:
        raise ClaimabilityReceiptVerifierError(
            "claimability_conversion_issuance_epoch_mismatch_phase_1305",
            "conversion_issuance_epoch does not match conversion receipt",
        )
    if payload["conversion_deadline_epoch"] != receipt["deadline_epoch"]:
        raise ClaimabilityReceiptVerifierError(
            "claimability_conversion_deadline_epoch_mismatch_phase_1305",
            "conversion_deadline_epoch does not match conversion receipt",
        )
    proof = _normalize_claimability_proof(
        payload["claimability_proof"],
        canonical_agent_identity=agent,
        epoch_id=epoch,
        settled_runtime_root=settled_root,
        wallet_state_root=wallet_root,
        latest_balance_receipt=balance_receipt,
        history_digest=history,
        conversion_receipt=receipt,
    )
    expected_proof_ref = _claimability_proof_ref(proof)
    if payload["claimability_proof_ref"] != expected_proof_ref:
        raise ClaimabilityReceiptVerifierError(
            "claimability_proof_ref_mismatch_phase_1305",
            "claimability_proof_ref does not match canonical proof",
        )
    body = {
        "canonical_agent_identity": agent,
        "claimability_proof": proof,
        "claimability_proof_ref": expected_proof_ref,
        "contract_version": OFFLINE_CLAIMABILITY_RECEIPT_VERIFIER_VERSION,
        "conversion_deadline_epoch": receipt["deadline_epoch"],
        "conversion_issuance_epoch": receipt["issue_epoch"],
        "conversion_key_sha256": receipt["conversion_key_sha256"],
        "conversion_lot_id": receipt["lot_id"],
        "conversion_receipt": receipt,
        "conversion_receipt_sha256": receipt["receipt_sha256"],
        "ecu_mint_authorized": False,
        "epoch_id": epoch,
        "history_digest": history,
        "ilc_settlement_authorized": False,
        "latest_balance_receipt": balance_receipt,
        "latest_balance_receipt_ref": expected_balance_ref,
        "non_loopback_claimability_api_enabled": False,
        "public_claimability_activated": False,
        "settled_runtime_root": settled_root,
        "tokens": tokens,
        "transport_principal_ref": _require_text(
            payload["transport_principal_ref"],
            token="claimability_transport_principal_ref_invalid_phase_1305",
        ),
        "wallet_spend_enabled": False,
        "wallet_state_root": wallet_root,
        "wallet_transfer_enabled": False,
        "wallet_withdrawal_enabled": False,
    }
    presentation_id = _require_text(
        payload["presentation_id"],
        token="claimability_presentation_id_invalid_phase_1305",
    )
    if presentation_id != _presentation_id_for_body(body):
        raise ClaimabilityReceiptVerifierError(
            "claimability_presentation_id_mismatch_phase_1305",
            "presentation_id does not match canonical presentation body",
        )
    return {"presentation_id": presentation_id, **body}


def _normalize_latest_balance_receipt(
    receipt: Mapping[str, Any],
    *,
    epoch_id: str,
) -> dict[str, Any]:
    if not isinstance(receipt, Mapping):
        raise ClaimabilityReceiptVerifierError(
            "claimability_latest_balance_receipt_invalid_phase_1305",
            "latest_balance_receipt must be an object",
        )
    payload = dict(receipt)
    if frozenset(payload) != _EXPECTED_BALANCE_RECEIPT_KEYS:
        raise ClaimabilityReceiptVerifierError(
            "claimability_latest_balance_receipt_invalid_phase_1305",
            "latest_balance_receipt fields do not match the local verifier contract",
        )
    if _require_text(payload["epoch_id"], token="claimability_latest_balance_receipt_invalid_phase_1305") != epoch_id:
        raise ClaimabilityReceiptVerifierError(
            "claimability_latest_balance_receipt_epoch_mismatch_phase_1305",
            "latest_balance_receipt epoch_id does not match presentation epoch_id",
        )
    normalized = {
        "balance_after_ilc": _require_decimal_string(
            payload["balance_after_ilc"],
            token="claimability_latest_balance_receipt_invalid_phase_1305",
            non_negative=True,
        ),
        "epoch_id": epoch_id,
        "reward_delta_ilc": _require_decimal_string(
            payload["reward_delta_ilc"],
            token="claimability_latest_balance_receipt_invalid_phase_1305",
            non_negative=False,
        ),
        "settlement_status": _require_text(
            payload["settlement_status"],
            token="claimability_latest_balance_receipt_invalid_phase_1305",
        ),
    }
    if normalized["settlement_status"] != "applied":
        raise ClaimabilityReceiptVerifierError(
            "claimability_latest_balance_receipt_invalid_phase_1305",
            "latest_balance_receipt settlement_status must be applied",
        )
    return normalized


def _normalize_conversion_receipt(
    receipt: Mapping[str, Any],
    *,
    canonical_agent_identity: str,
    settled_runtime_root: str,
    wallet_state_root: str,
) -> dict[str, Any]:
    if not isinstance(receipt, Mapping):
        raise ClaimabilityReceiptVerifierError(
            "claimability_conversion_receipt_invalid_phase_1305",
            "conversion_receipt must be an object",
        )
    payload = dict(receipt)
    if frozenset(payload) != _EXPECTED_CONVERSION_RECEIPT_KEYS:
        raise ClaimabilityReceiptVerifierError(
            "claimability_conversion_receipt_invalid_phase_1305",
            "conversion_receipt fields do not match the Phase 1274 receipt shape",
        )
    if payload["runtime_version"] != CDL048_CONVERSION_SWEEPER_RUNTIME_VERSION:
        raise ClaimabilityReceiptVerifierError(
            "claimability_conversion_receipt_invalid_phase_1305",
            "conversion_receipt runtime_version is not the expected Phase 1274 runtime",
        )
    agent_id = _require_text(
        payload["agent_id"],
        token="claimability_conversion_receipt_invalid_phase_1305",
    )
    if agent_id != canonical_agent_identity:
        raise ClaimabilityReceiptVerifierError(
            "claimability_conversion_receipt_agent_mismatch_phase_1305",
            "conversion_receipt agent_id does not match presentation agent",
        )
    lot_id = _require_text(
        payload["lot_id"],
        token="claimability_conversion_receipt_invalid_phase_1305",
    )
    amount_ecu = _require_decimal_string(
        payload["amount_ecu"],
        token="claimability_conversion_receipt_invalid_phase_1305",
        positive=True,
    )
    issue_epoch = _require_non_negative_int(
        payload["issue_epoch"],
        token="claimability_conversion_receipt_invalid_phase_1305",
    )
    deadline_epoch = _require_non_negative_int(
        payload["deadline_epoch"],
        token="claimability_conversion_receipt_invalid_phase_1305",
    )
    conversion_epoch = _require_non_negative_int(
        payload["conversion_epoch"],
        token="claimability_conversion_receipt_invalid_phase_1305",
    )
    settled_epoch = _require_non_negative_int(
        payload["settled_runtime_epoch"],
        token="claimability_conversion_receipt_invalid_phase_1305",
    )
    if deadline_epoch != issue_epoch + CDL048_CONVERSION_DEADLINE_ISSUANCE_EPOCHS:
        raise ClaimabilityReceiptVerifierError(
            "claimability_conversion_receipt_invalid_phase_1305",
            "conversion_receipt deadline_epoch does not match CDL-048 issuance window",
        )
    if conversion_epoch < issue_epoch or conversion_epoch > deadline_epoch:
        raise ClaimabilityReceiptVerifierError(
            "claimability_conversion_receipt_invalid_phase_1305",
            "conversion_receipt conversion_epoch is outside the allowed window",
        )
    if settled_epoch != conversion_epoch:
        raise ClaimabilityReceiptVerifierError(
            "claimability_conversion_receipt_invalid_phase_1305",
            "conversion_receipt settled_runtime_epoch must match conversion_epoch",
        )
    if payload["conversion_state_transition"] != CONVERSION_TRANSITION:
        raise ClaimabilityReceiptVerifierError(
            "claimability_conversion_receipt_invalid_phase_1305",
            "conversion_receipt transition is invalid",
        )
    if _require_prefixed_sha256(
        payload["wallet_state_root"],
        prefix=WALLET_STATE_ROOT_PREFIX,
        token="claimability_conversion_wallet_root_invalid_phase_1305",
    ) != wallet_state_root:
        raise ClaimabilityReceiptVerifierError(
            "claimability_conversion_receipt_wallet_root_mismatch_phase_1305",
            "conversion_receipt wallet_state_root does not match presentation",
        )
    if _require_prefixed_sha256(
        payload["settled_runtime_root"],
        prefix=SETTLED_RUNTIME_ROOT_PREFIX,
        token="claimability_conversion_settled_root_invalid_phase_1305",
    ) != settled_runtime_root:
        raise ClaimabilityReceiptVerifierError(
            "claimability_conversion_receipt_settled_root_mismatch_phase_1305",
            "conversion_receipt settled_runtime_root does not match presentation",
        )
    _require_prefixed_sha256(
        payload["sweeper_state_root_before"],
        prefix=CONVERSION_SWEEPER_STATE_ROOT_PREFIX,
        token="claimability_conversion_sweeper_state_root_invalid_phase_1305",
    )
    conversion_key_sha256 = _require_bare_sha256(
        payload["conversion_key_sha256"],
        token="claimability_conversion_key_invalid_phase_1305",
    )
    receipt_sha256 = _require_bare_sha256(
        payload["receipt_sha256"],
        token="claimability_conversion_receipt_sha256_invalid_phase_1305",
    )
    expected_key = _sha256_payload(
        {
            "agent_id": agent_id,
            "conversion_epoch": conversion_epoch,
            "conversion_state_transition": CONVERSION_TRANSITION,
            "lot_id": lot_id,
            "settled_runtime_root": settled_runtime_root,
            "wallet_state_root": wallet_state_root,
        }
    )
    if conversion_key_sha256 != expected_key:
        raise ClaimabilityReceiptVerifierError(
            "claimability_conversion_key_mismatch_phase_1305",
            "conversion_key_sha256 does not match binding material",
        )
    for field in _CONVERSION_ACTIVATION_FIELDS:
        _require_false(
            payload[field],
            token="claimability_conversion_receipt_activation_forbidden_phase_1305",
        )
    tokens = _normalize_token_list(
        payload["tokens"],
        required=[
            CONVERSION_SWEEPER_NO_PUBLIC_CLAIMABILITY_TOKEN,
            ECU_LOT_DEADLINE_ENFORCEMENT_TOKEN,
            WALLET_WITHDRAWAL_TRANSFER_SPEND_BLOCKED_TOKEN,
        ],
        token="claimability_conversion_receipt_tokens_invalid_phase_1305",
    )
    normalized = {
        "agent_id": agent_id,
        "amount_ecu": amount_ecu,
        "conversion_epoch": conversion_epoch,
        "conversion_key_sha256": conversion_key_sha256,
        "conversion_state_transition": CONVERSION_TRANSITION,
        "deadline_epoch": deadline_epoch,
        "ecu_mint_authorized": False,
        "ilc_settlement_authorized": False,
        "issue_epoch": issue_epoch,
        "lot_id": lot_id,
        "public_claimability_activated": False,
        "receipt_sha256": receipt_sha256,
        "runtime_version": CDL048_CONVERSION_SWEEPER_RUNTIME_VERSION,
        "settled_runtime_epoch": settled_epoch,
        "settled_runtime_root": settled_runtime_root,
        "sweeper_state_root_before": payload["sweeper_state_root_before"],
        "tokens": tokens,
        "wallet_spend_enabled": False,
        "wallet_state_root": wallet_state_root,
        "wallet_transfer_enabled": False,
        "wallet_withdrawal_enabled": False,
    }
    expected_hash_body = dict(normalized)
    actual_hash = expected_hash_body.pop("receipt_sha256")
    if actual_hash != _sha256_payload(expected_hash_body):
        raise ClaimabilityReceiptVerifierError(
            "claimability_conversion_receipt_hash_mismatch_phase_1305",
            "conversion_receipt receipt_sha256 does not match canonical receipt body",
        )
    return normalized


def _normalize_claimability_proof(
    proof: Mapping[str, Any],
    *,
    canonical_agent_identity: str,
    epoch_id: str,
    settled_runtime_root: str,
    wallet_state_root: str,
    latest_balance_receipt: dict[str, Any],
    history_digest: str,
    conversion_receipt: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(proof, Mapping):
        raise ClaimabilityReceiptVerifierError(
            "claimability_proof_invalid_phase_1305",
            "claimability_proof must be an object",
        )
    payload = dict(proof)
    if frozenset(payload) != _EXPECTED_PROOF_KEYS:
        raise ClaimabilityReceiptVerifierError(
            "claimability_proof_fields_invalid_phase_1305",
            "claimability_proof fields do not match the Phase 1275 proof shape",
        )
    if payload["runtime_version"] != CLAIMABILITY_PROOF_BINDING_RUNTIME_VERSION:
        raise ClaimabilityReceiptVerifierError(
            "claimability_proof_runtime_version_invalid_phase_1305",
            "claimability_proof runtime_version is invalid",
        )
    if payload["claimability_state"] != CLAIMABILITY_STATE:
        raise ClaimabilityReceiptVerifierError(
            "claimability_proof_state_invalid_phase_1305",
            "claimability_proof state is invalid",
        )
    for field in _ACTIVATION_FIELDS:
        _require_false(
            payload[field],
            token="claimability_proof_activation_forbidden_phase_1305",
        )
    if payload["transport_principal_required_before_non_loopback"] is not True:
        raise ClaimabilityReceiptVerifierError(
            "claimability_proof_transport_principal_gate_invalid_phase_1305",
            "claimability_proof must require TransportPrincipal before non-loopback use",
        )
    if payload["agent_id"] != canonical_agent_identity:
        raise ClaimabilityReceiptVerifierError(
            "claimability_proof_agent_mismatch_phase_1305",
            "claimability_proof agent_id does not match presentation agent",
        )
    if payload["canonical_agent_identity"] != canonical_agent_identity:
        raise ClaimabilityReceiptVerifierError(
            "claimability_proof_agent_mismatch_phase_1305",
            "claimability_proof canonical_agent_identity does not match presentation agent",
        )
    if payload["epoch_id"] != epoch_id:
        raise ClaimabilityReceiptVerifierError(
            "claimability_proof_epoch_mismatch_phase_1305",
            "claimability_proof epoch_id does not match presentation epoch",
        )
    if payload["settled_runtime_root"] != settled_runtime_root:
        raise ClaimabilityReceiptVerifierError(
            "claimability_proof_settled_root_mismatch_phase_1305",
            "claimability_proof settled_runtime_root does not match presentation",
        )
    if payload["wallet_state_root"] != wallet_state_root:
        raise ClaimabilityReceiptVerifierError(
            "claimability_proof_wallet_root_mismatch_phase_1305",
            "claimability_proof wallet_state_root does not match presentation",
        )
    if payload["history_digest"] != history_digest:
        raise ClaimabilityReceiptVerifierError(
            "claimability_proof_history_digest_mismatch_phase_1305",
            "claimability_proof history_digest does not match presentation",
        )
    nested_balance = _normalize_latest_balance_receipt(
        payload["latest_balance_receipt"],
        epoch_id=epoch_id,
    )
    if nested_balance != latest_balance_receipt:
        raise ClaimabilityReceiptVerifierError(
            "claimability_proof_balance_receipt_mismatch_phase_1305",
            "claimability_proof latest_balance_receipt does not match presentation",
        )
    if payload["latest_balance_receipt_ref"] != _latest_balance_receipt_ref(latest_balance_receipt):
        raise ClaimabilityReceiptVerifierError(
            "claimability_proof_balance_receipt_ref_mismatch_phase_1305",
            "claimability_proof latest_balance_receipt_ref does not match presentation",
        )
    nested_receipt = _normalize_conversion_receipt(
        payload["conversion_receipt"],
        canonical_agent_identity=canonical_agent_identity,
        settled_runtime_root=settled_runtime_root,
        wallet_state_root=wallet_state_root,
    )
    if nested_receipt != conversion_receipt:
        raise ClaimabilityReceiptVerifierError(
            "claimability_proof_conversion_receipt_mismatch_phase_1305",
            "claimability_proof conversion_receipt does not match presentation",
        )
    if payload["conversion_receipt_sha256"] != conversion_receipt["receipt_sha256"]:
        raise ClaimabilityReceiptVerifierError(
            "claimability_proof_conversion_receipt_hash_mismatch_phase_1305",
            "claimability_proof conversion_receipt_sha256 does not match presentation",
        )
    if payload["conversion_key_sha256"] != conversion_receipt["conversion_key_sha256"]:
        raise ClaimabilityReceiptVerifierError(
            "claimability_proof_conversion_key_mismatch_phase_1305",
            "claimability_proof conversion_key_sha256 does not match presentation",
        )
    if payload["conversion_lot_id"] != conversion_receipt["lot_id"]:
        raise ClaimabilityReceiptVerifierError(
            "claimability_proof_conversion_lot_mismatch_phase_1305",
            "claimability_proof conversion_lot_id does not match presentation",
        )
    if payload["conversion_epoch"] != conversion_receipt["conversion_epoch"]:
        raise ClaimabilityReceiptVerifierError(
            "claimability_proof_conversion_epoch_mismatch_phase_1305",
            "claimability_proof conversion_epoch does not match presentation",
        )
    if payload["conversion_deadline_epoch"] != conversion_receipt["deadline_epoch"]:
        raise ClaimabilityReceiptVerifierError(
            "claimability_proof_conversion_deadline_mismatch_phase_1305",
            "claimability_proof conversion_deadline_epoch does not match presentation",
        )
    if (
        payload["conversion_sweeper_state_root_before"]
        != conversion_receipt["sweeper_state_root_before"]
    ):
        raise ClaimabilityReceiptVerifierError(
            "claimability_proof_conversion_sweeper_root_mismatch_phase_1305",
            "claimability_proof conversion sweeper root does not match presentation",
        )
    proof_hash = _require_bare_sha256(
        payload["proof_binding_sha256"],
        token="claimability_proof_sha256_invalid_phase_1305",
    )
    tokens = _normalize_token_list(
        payload["tokens"],
        required=[
            CLAIMABILITY_PROOF_BINDING_RUNTIME_VERSION,
            SETTLED_ROOT_WALLET_ROOT_RECEIPT_BINDING_TOKEN,
            NON_LOOPBACK_CLAIMABILITY_API_BLOCKED_TOKEN,
            PUBLIC_CLAIMABILITY_NOT_ACTIVATED_TOKEN,
        ],
        token="claimability_proof_tokens_invalid_phase_1305",
    )
    normalized = {
        "agent_id": canonical_agent_identity,
        "canonical_agent_identity": canonical_agent_identity,
        "claimability_state": CLAIMABILITY_STATE,
        "conversion_deadline_epoch": conversion_receipt["deadline_epoch"],
        "conversion_epoch": conversion_receipt["conversion_epoch"],
        "conversion_key_sha256": conversion_receipt["conversion_key_sha256"],
        "conversion_lot_id": conversion_receipt["lot_id"],
        "conversion_receipt": conversion_receipt,
        "conversion_receipt_sha256": conversion_receipt["receipt_sha256"],
        "conversion_sweeper_state_root_before": conversion_receipt[
            "sweeper_state_root_before"
        ],
        "ecu_mint_authorized": False,
        "epoch_id": epoch_id,
        "history_digest": history_digest,
        "ilc_settlement_authorized": False,
        "latest_balance_receipt": latest_balance_receipt,
        "latest_balance_receipt_ref": _latest_balance_receipt_ref(latest_balance_receipt),
        "non_loopback_claimability_api_enabled": False,
        "proof_binding_sha256": proof_hash,
        "public_claimability_activated": False,
        "runtime_version": CLAIMABILITY_PROOF_BINDING_RUNTIME_VERSION,
        "settled_runtime_root": settled_runtime_root,
        "tokens": tokens,
        "transport_principal_required_before_non_loopback": True,
        "wallet_spend_enabled": False,
        "wallet_state_root": wallet_state_root,
        "wallet_transfer_enabled": False,
        "wallet_withdrawal_enabled": False,
    }
    expected_hash_body = dict(normalized)
    actual_hash = expected_hash_body.pop("proof_binding_sha256")
    if actual_hash != _sha256_payload(expected_hash_body):
        raise ClaimabilityReceiptVerifierError(
            "claimability_proof_hash_mismatch_phase_1305",
            "proof_binding_sha256 does not match canonical proof body",
        )
    return normalized


def _build_decision(
    *,
    decision: str,
    presentation_id: str | None,
    claimability_proof_ref: str | None,
    latest_balance_receipt_ref: str | None,
    conversion_receipt_sha256: str | None,
    rejection_reasons: list[str],
) -> dict[str, Any]:
    body = {
        "claimability_proof_ref": claimability_proof_ref,
        "contract_version": OFFLINE_CLAIMABILITY_RECEIPT_VERIFIER_VERSION,
        "conversion_receipt_sha256": conversion_receipt_sha256,
        "decision": decision,
        "ecu_mint_authorized": False,
        "ilc_settlement_authorized": False,
        "latest_balance_receipt_ref": latest_balance_receipt_ref,
        "non_loopback_claimability_api_enabled": False,
        "presentation_id": presentation_id,
        "public_api_enabled": False,
        "public_claimability_activated": False,
        "public_mode_blockers": list(_PUBLIC_MODE_BLOCKERS),
        "receipt_verifier_public_serving_enabled": False,
        "rejection_reasons": list(rejection_reasons),
        "tokens": claimability_receipt_verifier_tokens(),
        "verifier_version": OFFLINE_CLAIMABILITY_RECEIPT_VERIFIER_VERSION,
        "wallet_spend_enabled": False,
        "wallet_transfer_enabled": False,
        "wallet_withdrawal_enabled": False,
    }
    return {"canonical_decision_sha256": _sha256_payload(body), **body}


def _normalize_decision(decision: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(decision, Mapping):
        raise ClaimabilityReceiptVerifierError(
            "claimability_decision_not_object_phase_1305",
            "decision must be an object",
        )
    _reject_unsafe_json_tree(decision)
    payload = dict(decision)
    if frozenset(payload) != _EXPECTED_DECISION_KEYS:
        raise ClaimabilityReceiptVerifierError(
            "claimability_decision_fields_invalid_phase_1305",
            "decision fields do not match the Phase 1305 decision contract",
        )
    if payload["contract_version"] != OFFLINE_CLAIMABILITY_RECEIPT_VERIFIER_VERSION:
        raise ClaimabilityReceiptVerifierError(
            "claimability_decision_contract_version_invalid_phase_1305",
            "decision contract_version is invalid",
        )
    if payload["verifier_version"] != OFFLINE_CLAIMABILITY_RECEIPT_VERIFIER_VERSION:
        raise ClaimabilityReceiptVerifierError(
            "claimability_decision_verifier_version_invalid_phase_1305",
            "decision verifier_version is invalid",
        )
    decision_token = _require_text(
        payload["decision"],
        token="claimability_decision_token_invalid_phase_1305",
    )
    if decision_token not in {ACCEPTED_LOCAL_ONLY_DECISION, REJECTED_DECISION}:
        raise ClaimabilityReceiptVerifierError(
            "claimability_decision_token_invalid_phase_1305",
            "decision token is invalid",
        )
    for field in _DECISION_FALSE_FIELDS:
        _require_false(
            payload[field],
            token="claimability_decision_activation_flag_forbidden_phase_1305",
        )
    _normalize_token_list(
        payload["tokens"],
        required=claimability_receipt_verifier_tokens(),
        token="claimability_decision_tokens_invalid_phase_1305",
    )
    public_mode_blockers = _normalize_string_list(
        payload["public_mode_blockers"],
        token="claimability_decision_public_mode_blockers_invalid_phase_1305",
        max_count=_MAX_REASON_COUNT,
    )
    if public_mode_blockers != list(_PUBLIC_MODE_BLOCKERS):
        raise ClaimabilityReceiptVerifierError(
            "claimability_decision_public_mode_blockers_invalid_phase_1305",
            "decision public_mode_blockers are not canonical",
        )
    rejection_reasons = _normalize_string_list(
        payload["rejection_reasons"],
        token="claimability_decision_rejection_reasons_invalid_phase_1305",
        max_count=_MAX_REASON_COUNT,
    )
    if decision_token == ACCEPTED_LOCAL_ONLY_DECISION:
        if rejection_reasons:
            raise ClaimabilityReceiptVerifierError(
                "claimability_decision_rejection_reasons_invalid_phase_1305",
                "accepted decision must not carry rejection reasons",
            )
        _require_prefixed_sha256(
            payload["presentation_id"],
            prefix=PRESENTATION_ID_PREFIX,
            token="claimability_decision_presentation_id_invalid_phase_1305",
        )
        _require_prefixed_sha256(
            payload["claimability_proof_ref"],
            prefix=CLAIMABILITY_PROOF_REF_PREFIX,
            token="claimability_decision_claimability_proof_ref_invalid_phase_1305",
        )
        _require_prefixed_sha256(
            payload["latest_balance_receipt_ref"],
            prefix=LATEST_BALANCE_RECEIPT_REF_PREFIX,
            token="claimability_decision_balance_receipt_ref_invalid_phase_1305",
        )
        _require_bare_sha256(
            payload["conversion_receipt_sha256"],
            token="claimability_decision_conversion_receipt_hash_invalid_phase_1305",
        )
    else:
        if not rejection_reasons:
            raise ClaimabilityReceiptVerifierError(
                "claimability_decision_rejection_reasons_invalid_phase_1305",
                "rejected decision must carry a rejection reason",
            )
        for field in (
            "claimability_proof_ref",
            "latest_balance_receipt_ref",
            "conversion_receipt_sha256",
        ):
            if payload[field] is not None:
                raise ClaimabilityReceiptVerifierError(
                    "claimability_decision_rejected_refs_invalid_phase_1305",
                    "rejected decision must not carry accepted proof refs",
                )
        if payload["presentation_id"] is not None:
            _require_prefixed_sha256(
                payload["presentation_id"],
                prefix=PRESENTATION_ID_PREFIX,
                token="claimability_decision_presentation_id_invalid_phase_1305",
            )
    expected = dict(payload)
    actual_hash = expected.pop("canonical_decision_sha256")
    if actual_hash != _sha256_payload(expected):
        raise ClaimabilityReceiptVerifierError(
            "claimability_decision_hash_mismatch_phase_1305",
            "canonical_decision_sha256 does not match decision body",
        )
    return payload


def _presentation_id_for_body(body: Mapping[str, Any]) -> str:
    return f"{PRESENTATION_ID_PREFIX}:{_sha256_payload(dict(body))}"


def _claimability_proof_ref(proof: Mapping[str, Any]) -> str:
    return f"{CLAIMABILITY_PROOF_REF_PREFIX}:{proof['proof_binding_sha256']}"


def _latest_balance_receipt_ref(receipt: Mapping[str, Any]) -> str:
    return f"{LATEST_BALANCE_RECEIPT_REF_PREFIX}:{_sha256_payload(dict(receipt))}"


def _safe_presentation_id(presentation: object) -> str | None:
    if isinstance(presentation, Mapping):
        value = presentation.get("presentation_id")
        if isinstance(value, str):
            try:
                return _require_prefixed_sha256(
                    value,
                    prefix=PRESENTATION_ID_PREFIX,
                    token="claimability_presentation_id_invalid_phase_1305",
                )
            except ClaimabilityReceiptVerifierError:
                return None
    return None


def _normalize_token_list(value: Any, *, required: list[str], token: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ClaimabilityReceiptVerifierError(token, "tokens must be a list of strings")
    if len(value) > _MAX_TOKEN_COUNT:
        raise ClaimabilityReceiptVerifierError(token, "token list exceeds maximum size")
    for item in value:
        _require_text(item, token=token)
    if len(set(value)) != len(value):
        raise ClaimabilityReceiptVerifierError(token, "tokens must be unique")
    if not set(required).issubset(set(value)):
        raise ClaimabilityReceiptVerifierError(token, "tokens missing required entries")
    extras = sorted(item for item in value if item not in required)
    normalized = [*required, *extras]
    if value != normalized:
        raise ClaimabilityReceiptVerifierError(token, "tokens are not in canonical order")
    return normalized


def _normalize_string_list(value: Any, *, token: str, max_count: int) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ClaimabilityReceiptVerifierError(token, "required list of strings")
    if len(value) > max_count:
        raise ClaimabilityReceiptVerifierError(token, "string list exceeds maximum size")
    return [_require_text(item, token=token) for item in value]


def _require_false(value: object, *, token: str) -> None:
    if value is not False:
        raise ClaimabilityReceiptVerifierError(token, "activation field must be false")


def _require_text(value: object, *, token: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ClaimabilityReceiptVerifierError(token, "required non-empty string")
    if len(value) > _MAX_TEXT_LENGTH:
        raise ClaimabilityReceiptVerifierError(token, "string exceeds maximum length")
    if value != value.strip():
        raise ClaimabilityReceiptVerifierError(token, "string must be canonical without padding")
    return value


def _require_non_negative_int(value: object, *, token: str) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value < 0
        or value > _MAX_PROTOCOL_INT
    ):
        raise ClaimabilityReceiptVerifierError(token, "required non-negative integer")
    return value


def _require_decimal_string(
    value: object,
    *,
    token: str,
    non_negative: bool = False,
    positive: bool = False,
) -> str:
    if isinstance(value, bool) or isinstance(value, float) or not isinstance(value, str):
        raise ClaimabilityReceiptVerifierError(token, "required finite Decimal string")
    text = _require_text(value, token=token)
    try:
        number = Decimal(text)
    except InvalidOperation as exc:
        raise ClaimabilityReceiptVerifierError(token, "required finite Decimal string") from exc
    if not number.is_finite():
        raise ClaimabilityReceiptVerifierError(token, "required finite Decimal string")
    _require_decimal_bounds(number, token=token)
    if positive and number <= Decimal("0"):
        raise ClaimabilityReceiptVerifierError(token, "required positive Decimal string")
    if non_negative and number < Decimal("0"):
        raise ClaimabilityReceiptVerifierError(token, "required non-negative Decimal string")
    canonical = _decimal_to_canonical_string(number)
    if canonical != text:
        raise ClaimabilityReceiptVerifierError(token, "required canonical Decimal string")
    return canonical


def _require_prefixed_sha256(value: object, *, prefix: str, token: str) -> str:
    text = _require_text(value, token=token)
    expected_prefix = f"{prefix}:"
    if not text.startswith(expected_prefix):
        raise ClaimabilityReceiptVerifierError(token, "required prefixed SHA-256 digest")
    _require_bare_sha256(text[len(expected_prefix) :], token=token)
    return text


def _require_sha256_or_prefixed_sha256(value: object, *, prefix: str, token: str) -> str:
    text = _require_text(value, token=token)
    if ":" not in text:
        _require_bare_sha256(text, token=token)
        return text
    expected_prefix = f"{prefix}:"
    if not text.startswith(expected_prefix):
        raise ClaimabilityReceiptVerifierError(token, "required expected-prefixed SHA-256 digest")
    _require_bare_sha256(text[len(expected_prefix) :], token=token)
    return text


def _require_bare_sha256(value: object, *, token: str) -> str:
    text = _require_text(value, token=token)
    if len(text) != 64 or any(char not in _HEX for char in text):
        raise ClaimabilityReceiptVerifierError(token, "required lowercase full SHA-256 digest")
    return text


def _reject_unsafe_json_tree(
    value: Any,
    *,
    _depth: int = 0,
    _seen: set[int] | None = None,
    _counter: list[int] | None = None,
    _text_counter: list[int] | None = None,
) -> None:
    if _depth > _MAX_CANONICAL_PAYLOAD_DEPTH:
        raise ClaimabilityReceiptVerifierError(
            "claimability_payload_too_deep_phase_1305",
            "canonical payload exceeds maximum traversal depth",
        )
    if _seen is None:
        _seen = set()
    if _counter is None:
        _counter = [0]
    if _text_counter is None:
        _text_counter = [0]
    _counter[0] += 1
    if _counter[0] > _MAX_CANONICAL_PAYLOAD_NODES:
        raise ClaimabilityReceiptVerifierError(
            "claimability_payload_too_large_phase_1305",
            "canonical payload exceeds maximum traversal size",
        )
    if isinstance(value, float):
        raise ClaimabilityReceiptVerifierError(
            "claimability_payload_float_forbidden_phase_1305",
            "float is forbidden in local claimability verifier payloads",
        )
    if isinstance(value, bool):
        return
    if isinstance(value, int):
        if value < 0 or value > _MAX_PROTOCOL_INT:
            raise ClaimabilityReceiptVerifierError(
                "claimability_payload_int_invalid_phase_1305",
                "canonical payload integer exceeds the local verifier bound",
            )
        return
    if isinstance(value, str):
        if len(value) > _MAX_TEXT_LENGTH:
            raise ClaimabilityReceiptVerifierError(
                "claimability_payload_text_too_large_phase_1305",
                "canonical payload string exceeds maximum length",
            )
        _text_counter[0] += len(value)
        if _text_counter[0] > _MAX_CANONICAL_PAYLOAD_TEXT_BYTES:
            raise ClaimabilityReceiptVerifierError(
                "claimability_payload_text_too_large_phase_1305",
                "canonical payload text exceeds maximum aggregate size",
            )
        return
    if isinstance(value, Mapping):
        object_id = id(value)
        if object_id in _seen:
            raise ClaimabilityReceiptVerifierError(
                "claimability_payload_cycle_forbidden_phase_1305",
                "canonical payload must not contain cycles",
            )
        _seen.add(object_id)
        try:
            for key, item in value.items():
                if not isinstance(key, str):
                    raise ClaimabilityReceiptVerifierError(
                        "claimability_payload_key_invalid_phase_1305",
                        "canonical payload keys must be strings",
                    )
                _reject_unsafe_json_tree(
                    key,
                    _depth=_depth + 1,
                    _seen=_seen,
                    _counter=_counter,
                    _text_counter=_text_counter,
                )
                _reject_unsafe_json_tree(
                    item,
                    _depth=_depth + 1,
                    _seen=_seen,
                    _counter=_counter,
                    _text_counter=_text_counter,
                )
        finally:
            _seen.remove(object_id)
        return
    if isinstance(value, list):
        object_id = id(value)
        if object_id in _seen:
            raise ClaimabilityReceiptVerifierError(
                "claimability_payload_cycle_forbidden_phase_1305",
                "canonical payload must not contain cycles",
            )
        _seen.add(object_id)
        try:
            for item in value:
                _reject_unsafe_json_tree(
                    item,
                    _depth=_depth + 1,
                    _seen=_seen,
                    _counter=_counter,
                    _text_counter=_text_counter,
                )
        finally:
            _seen.remove(object_id)
        return
    if value is None or isinstance(value, str):
        return
    raise ClaimabilityReceiptVerifierError(
        "claimability_payload_type_invalid_phase_1305",
        "canonical payload contains a non-JSON type",
    )


def _sha256_payload(payload: Any) -> str:
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def _decimal_to_canonical_string(value: Decimal) -> str:
    if value == Decimal("0"):
        return "0"
    rendered = format(value, "f")
    if "." in rendered:
        rendered = rendered.rstrip("0").rstrip(".")
    return rendered


def _require_decimal_bounds(value: Decimal, *, token: str) -> None:
    """Reject values that would allocate huge fixed-point strings."""

    decimal_tuple = value.as_tuple()
    if len(decimal_tuple.digits) > _MAX_DECIMAL_DIGITS:
        raise ClaimabilityReceiptVerifierError(token, "Decimal has too many digits")
    if abs(decimal_tuple.exponent) > _MAX_DECIMAL_SCALE:
        raise ClaimabilityReceiptVerifierError(token, "Decimal scale exceeds local verifier bound")
    adjusted = value.adjusted()
    if (
        adjusted < -_MAX_DECIMAL_SCALE
        or adjusted > _MAX_DECIMAL_ADJUSTED_EXPONENT
    ):
        raise ClaimabilityReceiptVerifierError(token, "Decimal exponent exceeds local verifier bound")


__all__ = [
    "ACCEPTED_LOCAL_ONLY_DECISION",
    "CLAIMABILITY_VERIFIER_LOCAL_ONLY_TOKEN",
    "OFFLINE_CLAIMABILITY_RECEIPT_VERIFIER_VERSION",
    "PHASE_1306_NEXT_TOKEN",
    "PUBLIC_CLAIMABILITY_ACTIVATION_NOT_AUTHORIZED_TOKEN",
    "PUBLIC_RC_REMAINS_BLOCKED_TOKEN",
    "RECEIPT_VERIFIER_PUBLIC_SERVING_NOT_ENABLED_TOKEN",
    "REJECTED_DECISION",
    "ClaimabilityReceiptVerifierError",
    "build_claimability_verifier_presentation",
    "canonical_decision_json",
    "canonical_json",
    "claimability_receipt_verifier_manifest",
    "claimability_receipt_verifier_tokens",
    "verify_claimability_receipt_presentation",
]
