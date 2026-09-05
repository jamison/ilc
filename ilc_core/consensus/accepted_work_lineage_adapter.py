# SPDX-License-Identifier: AGPL-3.0-only
"""Accepted-work lineage receipt for Phase 1568-Fix2t.

This adapter binds existing artifacts across the current private Soft-RC read
path. It does not define a new attribution schema and it does not authorize
wallet, treasury, minting, settlement, or public-RC effects.
"""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal
from typing import Any

from ilc_core.consensus.attribution_batch_bridge import (
    ATTRIBUTION_BATCH_BRIDGE_VERSION,
    build_attribution_batch_from_claims,
)
from ilc_core.ledger.distributed_conversion_schema import verify_conversion_resolution
from ilc_core.ledger.exact_numeric import decimal_to_canonical_string


ACCEPTED_WORK_LINEAGE_VERSION = "accepted_work_lineage_adapter_1568_fix2t.v0.1"
LINEAGE_ROOT_PREFIX = "accepted_work_lineage_sha256:"

FIX2T_RECEIPT_TOKEN = "phase_1568_fix2t_accepted_work_lineage_adapter_committed"
FIX2T_CLAIMS_BATCH_TOKEN = (
    "phase_1568_fix2t_agent_loop_claims_bound_to_attribution_batch"
)
FIX2T_CONVERSION_REF_TOKEN = "phase_1568_fix2t_conversion_resolution_ref_bound"
FIX2T_REPLAY_REF_TOKEN = "phase_1568_fix2t_ilc_read_model_replay_ref_recorded"
FIX2T_NO_NEW_SCHEMA_TOKEN = "phase_1568_fix2t_no_new_attribution_schema"
FIX2T_NO_FRACTION_TOKEN = "phase_1568_fix2t_no_attribution_fraction"
FIX2T_NO_WRITE_TOKEN = "phase_1568_fix2t_no_value_write_authorized"
FIX2T_PUBLIC_BLOCKED_TOKEN = "public_path_remains_blocked_phase_1568_fix2t"

WRITE_AUTHORIZATION_FIELDS = frozenset(
    {
        "conversion_activation_authorized",
        "ledger_write_authorized",
        "wallet_write_authorized",
        "treasury_write_authorized",
        "production_minting_authorized",
        "ecu_mint_authorized",
        "ilc_settlement_authorized",
        "public_claimability_activated",
        "wallet_withdrawal_enabled",
        "wallet_transfer_enabled",
        "wallet_spend_enabled",
    }
)


class AcceptedWorkLineageError(ValueError):
    def __init__(self, token: str, message: str) -> None:
        super().__init__(message)
        self.token = token


def _normalize_json(value: Any) -> Any:
    if isinstance(value, Decimal):
        return decimal_to_canonical_string(value)
    if isinstance(value, dict):
        return {str(key): _normalize_json(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_normalize_json(item) for item in value]
    return value


def _reject_float_tree(value: Any, *, path: str = "$") -> None:
    if isinstance(value, float):
        raise AcceptedWorkLineageError(
            "accepted_work_lineage_float_rejected",
            f"float value is not allowed at {path}",
        )
    if isinstance(value, dict):
        for key, item in value.items():
            _reject_float_tree(key, path=f"{path}.{key!r}<key>")
            _reject_float_tree(item, path=f"{path}.{key}")
        return
    if isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _reject_float_tree(item, path=f"{path}[{index}]")


def _stable_json_bytes(payload: Any) -> bytes:
    normalized = _normalize_json(payload)
    _reject_float_tree(normalized)
    return json.dumps(
        normalized,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
        ensure_ascii=True,
    ).encode("utf-8")


def stable_sha256_hex(payload: Any) -> str:
    return hashlib.sha256(_stable_json_bytes(payload)).hexdigest()


def _require_dict(name: str, value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise AcceptedWorkLineageError(f"{name}_must_be_object", f"{name} must be an object")
    return value


def _require_text(name: str, value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AcceptedWorkLineageError(f"{name}_required", f"{name} must be a non-empty string")
    return value.strip()


def _require_epoch(name: str, value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise AcceptedWorkLineageError(
            f"{name}_must_be_non_negative_int",
            f"{name} must be a non-negative integer",
        )
    return value


def _assert_no_true_write_flags(value: Any, *, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key in WRITE_AUTHORIZATION_FIELDS and item is True:
                raise AcceptedWorkLineageError(
                    "accepted_work_lineage_write_authorization_forbidden",
                    f"{key} must not be true at {path}.{key}",
                )
            _assert_no_true_write_flags(item, path=f"{path}.{key}")
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _assert_no_true_write_flags(item, path=f"{path}[{index}]")


def _assert_no_attribution_fraction_field(value: Any, *, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key == "attribution_fraction":
                raise AcceptedWorkLineageError(
                    "attribution_fraction_field_forbidden_phase_1568_fix2t",
                    f"attribution_fraction field is forbidden at {path}.{key}",
                )
            _assert_no_attribution_fraction_field(item, path=f"{path}.{key}")
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _assert_no_attribution_fraction_field(item, path=f"{path}[{index}]")


def _claim_ids(claim_payload: dict[str, Any]) -> list[str]:
    claims = claim_payload.get("claims")
    if not isinstance(claims, list) or not claims:
        raise AcceptedWorkLineageError(
            "accepted_work_lineage_claims_required",
            "accepted claim payload must contain claims",
        )
    ids: list[str] = []
    for claim in claims:
        item = _require_dict("claim", claim)
        ids.append(_require_text("claim_id", item.get("claim_id")))
    return sorted(ids)


def _claim_binding_rows(claims: Any) -> list[dict[str, Any]]:
    if not isinstance(claims, list) or not claims:
        raise AcceptedWorkLineageError(
            "accepted_work_lineage_claims_required",
            "claim list must contain claims",
        )
    rows: list[dict[str, Any]] = []
    for claim in claims:
        item = _require_dict("claim", claim)
        rows.append(
            {
                "agent_id": _require_text("claim_agent_id", item.get("agent_id")),
                "amount": _require_text("claim_amount", item.get("amount")),
                "claim_id": _require_text("claim_id", item.get("claim_id")),
                "claim_kind": _require_text("claim_kind", item.get("claim_kind")),
                "epoch": _require_epoch("claim_epoch", item.get("epoch")),
                "task_id": _require_text("claim_task_id", item.get("task_id")),
            }
        )
    return sorted(rows, key=lambda row: row["claim_id"])


def _direct_author_claim_present(
    *,
    claim_payload: dict[str, Any],
    direct_author_agent_id: str,
) -> bool:
    for claim in claim_payload.get("claims", []):
        if not isinstance(claim, dict):
            continue
        if (
            claim.get("claim_kind") == "direct"
            and claim.get("agent_id") == direct_author_agent_id
        ):
            return True
    return False


def _batch_claim_ids(attribution_batch: dict[str, Any]) -> list[str]:
    attributions = attribution_batch.get("attributions")
    if not isinstance(attributions, list) or not attributions:
        raise AcceptedWorkLineageError(
            "accepted_work_lineage_attributions_required",
            "attribution batch must contain attributions",
        )
    ids: list[str] = []
    for attribution in attributions:
        item = _require_dict("attribution", attribution)
        source_claim_ids = item.get("source_claim_ids")
        if not isinstance(source_claim_ids, list) or not source_claim_ids:
            raise AcceptedWorkLineageError(
                "accepted_work_lineage_source_claim_ids_required",
                "each attribution must contain source_claim_ids",
            )
        for claim_id in source_claim_ids:
            ids.append(_require_text("source_claim_id", claim_id))
    return sorted(ids)


def _validate_panel_and_claims(
    *,
    panel_payload: dict[str, Any],
    claim_payload: dict[str, Any],
) -> dict[str, Any]:
    if panel_payload.get("marker") != "agent_loop_panel_ok":
        raise AcceptedWorkLineageError(
            "agent_loop_panel_ok_required_phase_1568_fix2t",
            "panel payload must be agent_loop_panel_ok",
        )
    if claim_payload.get("marker") != "agent_loop_claims_ok":
        raise AcceptedWorkLineageError(
            "agent_loop_claims_ok_required_phase_1568_fix2t",
            "claim payload must be agent_loop_claims_ok",
        )
    panel_result = _require_dict("panel_result", panel_payload.get("panel_result"))
    if panel_result.get("passed") is not True:
        raise AcceptedWorkLineageError(
            "accepted_panel_required_phase_1568_fix2t",
            "panel result must be accepted before lineage binding",
        )
    verdict_token = _require_text("verdict_token", panel_result.get("verdict_token"))
    direct_author_agent_id = _require_text(
        "direct_author_agent_id",
        panel_result.get("direct_author_agent_id"),
    )
    if not _direct_author_claim_present(
        claim_payload=claim_payload,
        direct_author_agent_id=direct_author_agent_id,
    ):
        raise AcceptedWorkLineageError(
            "direct_author_claim_missing_phase_1568_fix2t",
            "accepted claims must include the panel direct author claim",
        )
    return {
        "direct_author_agent_id": direct_author_agent_id,
        "panel_payload_sha256": stable_sha256_hex(panel_payload),
        "panel_result_sha256": stable_sha256_hex(panel_result),
        "verdict_token": verdict_token,
    }


def _validate_attribution_batch(
    *,
    claim_payload: dict[str, Any],
    attribution_batch: dict[str, Any],
) -> dict[str, Any]:
    if attribution_batch.get("marker") != "attribution_batch_bridge_ok":
        raise AcceptedWorkLineageError(
            "attribution_batch_bridge_ok_required_phase_1568_fix2t",
            "attribution batch must come from attribution_batch_bridge.py",
        )
    expected = build_attribution_batch_from_claims(
        claim_payload,
        epoch=attribution_batch.get("epoch"),
    )
    if _normalize_json(attribution_batch) != _normalize_json(expected):
        raise AcceptedWorkLineageError(
            "attribution_batch_mismatch_phase_1568_fix2t",
            "attribution batch does not match accepted claims",
        )
    if _claim_ids(claim_payload) != _batch_claim_ids(attribution_batch):
        raise AcceptedWorkLineageError(
            "claim_ids_not_bound_to_attribution_batch_phase_1568_fix2t",
            "accepted claim IDs do not match attribution source claim IDs",
        )
    return {
        "attribution_batch_bridge_version": ATTRIBUTION_BATCH_BRIDGE_VERSION,
        "attribution_batch_sha256": stable_sha256_hex(attribution_batch),
        "attribution_count": attribution_batch["attribution_count"],
        "claim_payload_sha256": stable_sha256_hex(claim_payload),
        "claim_ids_sha256": stable_sha256_hex(_claim_ids(claim_payload)),
        "rounding": attribution_batch["rounding"],
        "source_claim_count": attribution_batch["source_claim_count"],
        "total_micro_ecu": attribution_batch["total_micro_ecu"],
        "total_source_ecu": attribution_batch["total_source_ecu"],
    }


def _validate_conversion_resolution(conversion_resolution: dict[str, Any]) -> dict[str, Any]:
    verification = verify_conversion_resolution(conversion_resolution)
    if verification.get("ok") is not True:
        raise AcceptedWorkLineageError(
            "conversion_resolution_invalid_phase_1568_fix2t",
            str(verification.get("reason", "unknown")),
        )
    if conversion_resolution.get("quote_read_model_only") is not True:
        raise AcceptedWorkLineageError(
            "conversion_resolution_read_model_only_required_phase_1568_fix2t",
            "conversion resolution must remain read-model only",
        )
    return {
        "cdl057_witness_ref": conversion_resolution["cdl057_witness_ref"],
        "conversion_resolution_sha256": stable_sha256_hex(conversion_resolution),
        "genesis_tranche_treatment": conversion_resolution["genesis_tranche_treatment"],
        "resolution_status": conversion_resolution["resolution_status"],
        "verifier_root": conversion_resolution["verifier_root"],
    }


def _read_model_replay_ref_from_record(
    *,
    claim_payload: dict[str, Any],
    conversion_resolution: dict[str, Any],
    ilc_read_model_replay_record: dict[str, Any],
) -> dict[str, Any]:
    record = ilc_read_model_replay_record
    if record.get("marker") != "phase_1568_fix2l_rehearsal_economics_record":
        raise AcceptedWorkLineageError(
            "ilc_read_model_replay_record_required_phase_1568_fix2t",
            "ILC read-model replay record must be a rehearsal economics record",
        )
    if record.get("cdl048_conversion_resolution_verified") is not True:
        raise AcceptedWorkLineageError(
            "conversion_resolution_verification_required_phase_1568_fix2t",
            "rehearsal economics record must verify the conversion resolution",
        )
    if _normalize_json(record.get("cdl048_conversion_resolution")) != _normalize_json(
        conversion_resolution
    ):
        raise AcceptedWorkLineageError(
            "conversion_resolution_ref_mismatch_phase_1568_fix2t",
            "rehearsal economics conversion resolution does not match lineage input",
        )
    if _claim_binding_rows(record.get("ecu_claims")) != _claim_binding_rows(
        claim_payload.get("claims")
    ):
        raise AcceptedWorkLineageError(
            "ilc_read_model_claims_mismatch_phase_1568_fix2t",
            "rehearsal economics claims do not match accepted claim payload",
        )
    if record.get("ecu_claims_sha256") != stable_sha256_hex(record["ecu_claims"]):
        raise AcceptedWorkLineageError(
            "ilc_read_model_claims_hash_mismatch_phase_1568_fix2t",
            "rehearsal economics claims hash does not match claims",
        )
    if record.get("cdl048_wallet_write_authorized") is not False:
        raise AcceptedWorkLineageError(
            "ilc_read_model_wallet_write_forbidden_phase_1568_fix2t",
            "rehearsal economics record must not authorize wallet writes",
        )
    if record.get("no_treasury_write_activated") is not True:
        raise AcceptedWorkLineageError(
            "ilc_read_model_treasury_boundary_required_phase_1568_fix2t",
            "rehearsal economics record must assert no treasury write activation",
        )
    return {
        "ecu_claims_sha256": record["ecu_claims_sha256"],
        "ecu_claims_total_ecu": record["ecu_claims_total_ecu"],
        "ilc_read_model_replay_record_sha256": stable_sha256_hex(record),
        "marker": record["marker"],
        "settlement_root_hex": record["settlement_root_hex"],
        "settlement_root_inputs_sha256": record["settlement_root_inputs_sha256"],
    }


def _validate_attribution_apply_receipt(
    *,
    attribution_apply_receipt: dict[str, Any] | None,
    attribution_batch: dict[str, Any],
) -> dict[str, Any]:
    if attribution_apply_receipt is None:
        return {
            "attribution_apply_receipt_supplied": False,
            "consensus_checkpoint_mode": "not_supplied_read_model_lineage_only",
        }
    if attribution_apply_receipt.get("marker") != "attribution_batch_ingest_ok":
        raise AcceptedWorkLineageError(
            "attribution_apply_receipt_invalid_phase_1568_fix2t",
            "attribution apply receipt must be attribution_batch_ingest_ok",
        )
    if attribution_apply_receipt.get("total_micro_ecu") != attribution_batch.get("total_micro_ecu"):
        raise AcceptedWorkLineageError(
            "attribution_apply_total_mismatch_phase_1568_fix2t",
            "attribution apply receipt total does not match attribution batch",
        )
    if attribution_apply_receipt.get("attribution_count") != attribution_batch.get("attribution_count"):
        raise AcceptedWorkLineageError(
            "attribution_apply_count_mismatch_phase_1568_fix2t",
            "attribution apply receipt count does not match attribution batch",
        )
    return {
        "attribution_apply_receipt_sha256": stable_sha256_hex(attribution_apply_receipt),
        "attribution_apply_receipt_supplied": True,
        "consensus_checkpoint_mode": "attribution_batch_ingest_receipt_bound",
        "dry_run": attribution_apply_receipt.get("dry_run"),
    }


def build_accepted_work_lineage_receipt(
    *,
    panel_payload: dict[str, Any],
    claim_payload: dict[str, Any],
    attribution_batch: dict[str, Any],
    conversion_resolution: dict[str, Any],
    ilc_read_model_replay_record: dict[str, Any],
    attribution_apply_receipt: dict[str, Any] | None = None,
) -> dict[str, Any]:
    inputs = (
        panel_payload,
        claim_payload,
        attribution_batch,
        conversion_resolution,
        ilc_read_model_replay_record,
    )
    for item in inputs:
        _reject_float_tree(item)
        _assert_no_true_write_flags(item)
        _assert_no_attribution_fraction_field(item)
    if attribution_apply_receipt is not None:
        _reject_float_tree(attribution_apply_receipt)
        _assert_no_true_write_flags(attribution_apply_receipt)
        _assert_no_attribution_fraction_field(attribution_apply_receipt)

    normalized_panel = _require_dict("panel_payload", panel_payload)
    normalized_claims = _require_dict("claim_payload", claim_payload)
    normalized_batch = _require_dict("attribution_batch", attribution_batch)
    normalized_resolution = _require_dict("conversion_resolution", conversion_resolution)
    normalized_replay_record = _require_dict(
        "ilc_read_model_replay_record",
        ilc_read_model_replay_record,
    )

    accepted_work_ref = _validate_panel_and_claims(
        panel_payload=normalized_panel,
        claim_payload=normalized_claims,
    )
    attribution_ref = _validate_attribution_batch(
        claim_payload=normalized_claims,
        attribution_batch=normalized_batch,
    )
    conversion_ref = _validate_conversion_resolution(normalized_resolution)
    replay_ref = _read_model_replay_ref_from_record(
        claim_payload=normalized_claims,
        conversion_resolution=normalized_resolution,
        ilc_read_model_replay_record=normalized_replay_record,
    )
    apply_ref = _validate_attribution_apply_receipt(
        attribution_apply_receipt=attribution_apply_receipt,
        attribution_batch=normalized_batch,
    )

    record_without_root = {
        "accepted_work_ref": accepted_work_ref,
        "attribution_batch_ref": attribution_ref,
        "consensus_checkpoint_ref": apply_ref,
        "conversion_resolution_ref": conversion_ref,
        "ilc_read_model_replay_ref": replay_ref,
        "marker": "phase_1568_fix2t_accepted_work_lineage_receipt",
        "new_attribution_schema_defined": False,
        "runtime_version": ACCEPTED_WORK_LINEAGE_VERSION,
        "tokens": [
            FIX2T_RECEIPT_TOKEN,
            FIX2T_CLAIMS_BATCH_TOKEN,
            FIX2T_CONVERSION_REF_TOKEN,
            FIX2T_REPLAY_REF_TOKEN,
            FIX2T_NO_NEW_SCHEMA_TOKEN,
            FIX2T_NO_FRACTION_TOKEN,
            FIX2T_NO_WRITE_TOKEN,
            FIX2T_PUBLIC_BLOCKED_TOKEN,
        ],
        "value_write_authorized": False,
        "wallet_write_authorized": False,
        "treasury_write_authorized": False,
        "production_minting_authorized": False,
        "ilc_settlement_authorized": False,
        "public_claimability_activated": False,
    }
    lineage_root = f"{LINEAGE_ROOT_PREFIX}{stable_sha256_hex(record_without_root)}"
    record = {**record_without_root, "lineage_root": lineage_root}
    _assert_no_attribution_fraction_field(record)
    _assert_no_true_write_flags(record)
    return _normalize_json(record)


def verify_accepted_work_lineage_receipt(
    receipt: dict[str, Any],
    *,
    panel_payload: dict[str, Any],
    claim_payload: dict[str, Any],
    attribution_batch: dict[str, Any],
    conversion_resolution: dict[str, Any],
    ilc_read_model_replay_record: dict[str, Any],
    attribution_apply_receipt: dict[str, Any] | None = None,
) -> dict[str, Any]:
    try:
        expected = build_accepted_work_lineage_receipt(
            panel_payload=panel_payload,
            claim_payload=claim_payload,
            attribution_batch=attribution_batch,
            conversion_resolution=conversion_resolution,
            ilc_read_model_replay_record=ilc_read_model_replay_record,
            attribution_apply_receipt=attribution_apply_receipt,
        )
        _reject_float_tree(receipt)
        _assert_no_true_write_flags(receipt)
        _assert_no_attribution_fraction_field(receipt)
    except AcceptedWorkLineageError as exc:
        return {"ok": False, "reason": exc.token}
    if _normalize_json(receipt) != expected:
        return {
            "ok": False,
            "reason": "accepted_work_lineage_receipt_mismatch",
        }
    return {
        "lineage_root": expected["lineage_root"],
        "ok": True,
        "tokens": expected["tokens"],
        "value_write_authorized": False,
    }


__all__ = [
    "ACCEPTED_WORK_LINEAGE_VERSION",
    "AcceptedWorkLineageError",
    "LINEAGE_ROOT_PREFIX",
    "build_accepted_work_lineage_receipt",
    "stable_sha256_hex",
    "verify_accepted_work_lineage_receipt",
]
