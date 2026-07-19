# SPDX-License-Identifier: AGPL-3.0-only
"""Local bootstrap census intake for public-agent receipts.

This runtime validates locally generated bootstrap receipts and writes a
deduplicated intake bundle. It is intentionally not an LMDB writer; a later
graph-ingest phase can consume the bundle after privacy and authority review.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ilc_core.private_json_guardrails import canonical_json, reject_float
from ilc_core.rc.public_agent_bootstrap_receipt import (
    DISTRIBUTION_TELEMETRY_BOUNDARY_TOKEN,
    PUBLIC_AGENT_BOOTSTRAP_BASELINE_TOKEN,
    PUBLIC_AGENT_BOOTSTRAP_GRAPH_BRIDGE_TOKEN,
    PUBLIC_AGENT_BOOTSTRAP_NON_CLAIMS_TOKEN,
    PUBLIC_AGENT_BOOTSTRAP_RECEIPT_PHASE,
    PUBLIC_AGENT_BOOTSTRAP_RECEIPT_SCHEMA_VERSION,
    PUBLIC_AGENT_BOOTSTRAP_RECEIPT_TOKEN,
)


BOOTSTRAP_CENSUS_INTAKE_SCHEMA_VERSION = "bootstrap_census_intake_1576.v0.1"
BOOTSTRAP_CENSUS_INTAKE_PHASE = "1576-bootstrap-census-intake"
BOOTSTRAP_CENSUS_INTAKE_TOKEN = "bootstrap_census_intake_local_queue_committed_phase_1576"
BOOTSTRAP_CENSUS_DEDUP_TOKEN = "bootstrap_census_receipt_dedup_validation_committed_phase_1576"
BOOTSTRAP_CENSUS_CLASSIFICATION_TOKEN = (
    "bootstrap_census_identity_status_only_classification_committed_phase_1576"
)
BOOTSTRAP_CENSUS_NO_GRAPH_WRITE_TOKEN = (
    "bootstrap_census_no_lmdb_no_public_graph_write_phase_1576"
)

_INTAKE_FLOAT_TOKEN = "bootstrap_census_intake_float_not_allowed"
_MAX_RECEIPTS = 10_000
_MAX_RECEIPT_BYTES = 2_000_000
_RECEIPT_PREFIX = "public_agent_bootstrap_receipt:"
_HEX_64 = frozenset("0123456789abcdef")
_RECEIPT_REQUIRED_TOKENS = frozenset(
    {
        PUBLIC_AGENT_BOOTSTRAP_RECEIPT_TOKEN,
        PUBLIC_AGENT_BOOTSTRAP_BASELINE_TOKEN,
        PUBLIC_AGENT_BOOTSTRAP_NON_CLAIMS_TOKEN,
        PUBLIC_AGENT_BOOTSTRAP_GRAPH_BRIDGE_TOKEN,
        DISTRIBUTION_TELEMETRY_BOUNDARY_TOKEN,
    }
)
_REQUIRED_NON_CLAIMS = frozenset(
    {
        "no_ecu_distribution_activation",
        "no_economic_guard_clearance",
        "no_epoch_transition",
        "no_live_settlement",
        "no_mainnet_activation",
        "no_production_minting",
        "no_public_graph_write",
        "no_public_p2p_activation",
        "no_treasury_write",
        "no_wallet_write",
    }
)
_RECEIPT_BODY_FIELDS = frozenset(
    {
        "activation_state",
        "agent_identity_status",
        "baseline_slice_verification",
        "distribution_telemetry_boundary",
        "generated_at_utc",
        "install_proof",
        "non_claims",
        "phase",
        "receipt_kind",
        "schema_version",
        "tokens",
    }
)


class BootstrapCensusIntakeError(ValueError):
    """Stable local census-intake error."""


def build_bootstrap_census_intake(
    *,
    receipt_paths: list[str | Path] | None = None,
    receipt_dirs: list[str | Path] | None = None,
    generated_at_utc: str | None = None,
    source_label: str = "local",
    fail_on_invalid: bool = True,
) -> dict[str, Any]:
    """Validate, deduplicate, and classify local bootstrap receipt files."""

    if generated_at_utc is None:
        generated_at_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    _validate_timestamp(generated_at_utc)
    if not isinstance(source_label, str) or not source_label:
        raise BootstrapCensusIntakeError("source_label_invalid")

    paths = _collect_receipt_paths(receipt_paths or [], receipt_dirs or [])
    accepted: dict[str, dict[str, Any]] = {}
    invalid: list[dict[str, str]] = []
    duplicates: list[dict[str, str]] = []

    for path in paths:
        try:
            receipt = _read_receipt(path)
            summary = validate_bootstrap_receipt(receipt)
        except (BootstrapCensusIntakeError, OSError, json.JSONDecodeError) as exc:
            invalid.append(
                {
                    "path": path.as_posix(),
                    "reason": str(exc),
                    "status": "invalid",
                }
            )
            continue
        receipt_id = str(summary["receipt_id"])
        if receipt_id in accepted:
            duplicates.append(
                {
                    "duplicate_of_path": str(accepted[receipt_id]["source_path"]),
                    "path": path.as_posix(),
                    "receipt_id": receipt_id,
                    "status": "duplicate",
                }
            )
            continue
        accepted[receipt_id] = {**summary, "source_path": path.as_posix()}

    if invalid and fail_on_invalid:
        raise BootstrapCensusIntakeError("bootstrap_census_invalid_receipts_present")

    entries = [accepted[key] for key in sorted(accepted)]
    body: dict[str, Any] = {
        "accepted_count": len(entries),
        "duplicate_count": len(duplicates),
        "duplicates": duplicates,
        "entries": entries,
        "generated_at_utc": generated_at_utc,
        "graph_intake_status": "staged_local_json_only",
        "invalid_count": len(invalid),
        "invalid_receipts": invalid,
        "non_claims": _intake_non_claims(),
        "phase": BOOTSTRAP_CENSUS_INTAKE_PHASE,
        "receipt_count_seen": len(paths),
        "schema_version": BOOTSTRAP_CENSUS_INTAKE_SCHEMA_VERSION,
        "source_label": source_label,
        "tokens": [
            BOOTSTRAP_CENSUS_INTAKE_TOKEN,
            BOOTSTRAP_CENSUS_DEDUP_TOKEN,
            BOOTSTRAP_CENSUS_CLASSIFICATION_TOKEN,
            BOOTSTRAP_CENSUS_NO_GRAPH_WRITE_TOKEN,
            DISTRIBUTION_TELEMETRY_BOUNDARY_TOKEN,
        ],
    }
    body_sha256 = _sha256_canonical(body)
    intake = {
        **body,
        "intake_body_sha256": body_sha256,
        "intake_id": f"bootstrap_census_intake:{body_sha256}",
    }
    reject_float(intake, _INTAKE_FLOAT_TOKEN)
    return intake


def validate_bootstrap_receipt(receipt: dict[str, Any]) -> dict[str, Any]:
    """Validate one bootstrap receipt and return a graph-intake summary."""

    reject_float(receipt, _INTAKE_FLOAT_TOKEN)
    _require_receipt_shape(receipt)
    _require_receipt_hash(receipt)
    _require_receipt_non_claims(receipt)
    _require_distribution_boundary(receipt)

    identity = receipt["agent_identity_status"]
    baseline = receipt["baseline_slice_verification"]
    install = receipt["install_proof"]
    entry = {
        "agent_identity_configured": bool(identity["configured"]),
        "baseline_all_artifacts_present": bool(baseline["all_artifacts_present"]),
        "baseline_all_signatures_verified": bool(baseline["all_signatures_verified"]),
        "ccss_agent_id": str(identity["ccss_identity"].get("agent_id", "")),
        "classification": _classification(receipt),
        "d2e_lineage_id": str(identity["d2e_identity"].get("lineage_id", "")),
        "generated_at_utc": str(receipt["generated_at_utc"]),
        "graph_evidence_status": "candidate_status_only",
        "install_surface": str(install["install_surface"]),
        "receipt_body_sha256": str(receipt["receipt_body_sha256"]),
        "receipt_id": str(receipt["receipt_id"]),
        "repo_root_git_head": str(install["repo_root_git_head"]),
    }
    reject_float(entry, _INTAKE_FLOAT_TOKEN)
    return entry


def write_bootstrap_census_intake(path: str | Path, intake: dict[str, Any]) -> Path:
    """Atomically write the local census intake bundle."""

    reject_float(intake, _INTAKE_FLOAT_TOKEN)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_name(f".{target.name}.tmp.{os.getpid()}")
    payload = json.dumps(intake, sort_keys=True, indent=2, allow_nan=False) + "\n"
    try:
        with tmp.open("w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, target)
    finally:
        if tmp.exists():
            tmp.unlink()
    return target


def _collect_receipt_paths(
    receipt_paths: list[str | Path],
    receipt_dirs: list[str | Path],
) -> list[Path]:
    paths: list[Path] = []
    for value in receipt_paths:
        path = Path(value)
        if not path.is_file():
            raise BootstrapCensusIntakeError(f"receipt_file_not_found:{path}")
        paths.append(path)
    for value in receipt_dirs:
        directory = Path(value)
        if not directory.is_dir():
            raise BootstrapCensusIntakeError(f"receipt_dir_not_found:{directory}")
        paths.extend(sorted(path for path in directory.glob("*.json") if path.is_file()))
    deduped = sorted(dict.fromkeys(path.resolve() for path in paths))
    if not deduped:
        raise BootstrapCensusIntakeError("bootstrap_census_no_receipts")
    if len(deduped) > _MAX_RECEIPTS:
        raise BootstrapCensusIntakeError("bootstrap_census_receipt_count_exceeds_bound")
    return deduped


def _read_receipt(path: Path) -> dict[str, Any]:
    if path.stat().st_size > _MAX_RECEIPT_BYTES:
        raise BootstrapCensusIntakeError("bootstrap_census_receipt_file_too_large")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise BootstrapCensusIntakeError("bootstrap_census_receipt_not_object")
    return data


def _require_receipt_shape(receipt: dict[str, Any]) -> None:
    if receipt.get("schema_version") != PUBLIC_AGENT_BOOTSTRAP_RECEIPT_SCHEMA_VERSION:
        raise BootstrapCensusIntakeError("bootstrap_receipt_schema_version_invalid")
    if receipt.get("receipt_kind") != "public_agent_bootstrap_receipt":
        raise BootstrapCensusIntakeError("bootstrap_receipt_kind_invalid")
    if receipt.get("phase") != PUBLIC_AGENT_BOOTSTRAP_RECEIPT_PHASE:
        raise BootstrapCensusIntakeError("bootstrap_receipt_phase_invalid")
    receipt_id = receipt.get("receipt_id")
    if not isinstance(receipt_id, str) or not receipt_id.startswith(_RECEIPT_PREFIX):
        raise BootstrapCensusIntakeError("bootstrap_receipt_id_invalid")
    body_sha = receipt.get("receipt_body_sha256")
    if not _is_sha256(str(body_sha)):
        raise BootstrapCensusIntakeError("bootstrap_receipt_body_sha256_invalid")
    if receipt_id != _RECEIPT_PREFIX + str(body_sha):
        raise BootstrapCensusIntakeError("bootstrap_receipt_id_hash_mismatch")
    tokens = receipt.get("tokens")
    if not isinstance(tokens, list) or not _RECEIPT_REQUIRED_TOKENS.issubset(set(tokens)):
        raise BootstrapCensusIntakeError("bootstrap_receipt_required_tokens_missing")
    for key in (
        "agent_identity_status",
        "baseline_slice_verification",
        "distribution_telemetry_boundary",
        "generated_at_utc",
        "install_proof",
        "non_claims",
    ):
        if key not in receipt:
            raise BootstrapCensusIntakeError(f"bootstrap_receipt_field_missing:{key}")


def _require_receipt_hash(receipt: dict[str, Any]) -> None:
    missing = sorted(key for key in _RECEIPT_BODY_FIELDS if key not in receipt)
    if missing:
        raise BootstrapCensusIntakeError(
            "bootstrap_receipt_body_fields_missing:" + ",".join(missing)
        )
    body = {key: receipt[key] for key in sorted(_RECEIPT_BODY_FIELDS)}
    if set(body) != _RECEIPT_BODY_FIELDS:
        raise BootstrapCensusIntakeError("bootstrap_receipt_body_fields_invalid")
    expected = _sha256_canonical(body)
    if expected != receipt["receipt_body_sha256"]:
        raise BootstrapCensusIntakeError("bootstrap_receipt_body_hash_mismatch")


def _require_receipt_non_claims(receipt: dict[str, Any]) -> None:
    non_claims = receipt.get("non_claims")
    if not isinstance(non_claims, dict):
        raise BootstrapCensusIntakeError("bootstrap_receipt_non_claims_invalid")
    for key in sorted(_REQUIRED_NON_CLAIMS):
        if non_claims.get(key) is not True:
            raise BootstrapCensusIntakeError(f"bootstrap_receipt_non_claim_missing:{key}")


def _require_distribution_boundary(receipt: dict[str, Any]) -> None:
    boundary = receipt.get("distribution_telemetry_boundary")
    if not isinstance(boundary, dict):
        raise BootstrapCensusIntakeError("bootstrap_receipt_distribution_boundary_invalid")
    if boundary.get("token") != DISTRIBUTION_TELEMETRY_BOUNDARY_TOKEN:
        raise BootstrapCensusIntakeError("bootstrap_receipt_distribution_boundary_token_missing")
    for key in (
        "github_visits_are_graph_evidence",
        "github_clones_are_graph_evidence",
        "clawhub_installs_are_graph_evidence",
    ):
        if boundary.get(key) is not False:
            raise BootstrapCensusIntakeError(f"bootstrap_receipt_telemetry_boundary_invalid:{key}")


def _classification(receipt: dict[str, Any]) -> str:
    identity = receipt["agent_identity_status"]
    baseline = receipt["baseline_slice_verification"]
    if bool(identity["configured"]) and bool(baseline["all_signatures_verified"]):
        return "identity_status_and_baseline_verified"
    if bool(identity["configured"]):
        return "identity_status_only"
    if bool(baseline["all_signatures_verified"]):
        return "install_baseline_verified_no_identity"
    return "install_status_only"


def _intake_non_claims() -> dict[str, bool]:
    return {
        "no_ecu_credit": True,
        "no_epoch_transition": True,
        "no_lmdb_write": True,
        "no_live_settlement": True,
        "no_production_minting": True,
        "no_public_graph_write": True,
        "no_verifier_role_claim": True,
        "no_wallet_write": True,
    }


def _sha256_canonical(payload: dict[str, Any]) -> str:
    body = canonical_json(payload, float_token=_INTAKE_FLOAT_TOKEN)
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def _is_sha256(value: str) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(c in _HEX_64 for c in value)


def _validate_timestamp(value: str) -> None:
    if not isinstance(value, str) or not value:
        raise BootstrapCensusIntakeError("generated_at_utc_invalid")
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise BootstrapCensusIntakeError("generated_at_utc_invalid") from exc
    if parsed.tzinfo is None:
        raise BootstrapCensusIntakeError("generated_at_utc_must_include_timezone")
