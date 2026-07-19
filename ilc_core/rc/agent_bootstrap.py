# SPDX-License-Identifier: AGPL-3.0-only
"""Local agent-bootstrap plan from staged public-agent census intake.

The plan is a readiness receipt only. It verifies local intake and signed
release artifacts, then emits candidate bootstrap rows without assigning roles
or writing graph/economic state.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from ilc_core.private_json_guardrails import canonical_json, reject_float
from ilc_core.rc.bootstrap_census_intake import (
    BOOTSTRAP_CENSUS_CLASSIFICATION_TOKEN,
    BOOTSTRAP_CENSUS_DEDUP_TOKEN,
    BOOTSTRAP_CENSUS_INTAKE_PHASE,
    BOOTSTRAP_CENSUS_INTAKE_SCHEMA_VERSION,
    BOOTSTRAP_CENSUS_INTAKE_TOKEN,
    BOOTSTRAP_CENSUS_NO_GRAPH_WRITE_TOKEN,
)


AGENT_BOOTSTRAP_SCHEMA_VERSION = "agent_bootstrap_plan_1576.v0.1"
AGENT_BOOTSTRAP_PHASE = "1576-agent-bootstrap"
AGENT_BOOTSTRAP_PLAN_TOKEN = "agent_bootstrap_plan_committed_phase_1576"
AGENT_BOOTSTRAP_CENSUS_DEPENDENCY_TOKEN = (
    "agent_bootstrap_census_intake_dependency_verified_phase_1576"
)
AGENT_BOOTSTRAP_BASELINE_MANIFEST_TOKEN = (
    "agent_bootstrap_signed_baseline_manifest_verified_phase_1576"
)
AGENT_BOOTSTRAP_NO_VERIFIER_EPOCH_TOKEN = (
    "agent_bootstrap_no_verifier_no_epoch_transition_phase_1576"
)

_FLOAT_TOKEN = "agent_bootstrap_float_not_allowed"
_INTAKE_PREFIX = "bootstrap_census_intake:"
_PLAN_PREFIX = "agent_bootstrap_plan:"
_CANDIDATE_PREFIX = "agent_bootstrap_candidate:"
_HEX_64 = frozenset("0123456789abcdef")
_MAX_ARTIFACT_BYTES = 25 * 1024 * 1024
_MAX_TOTAL_ARTIFACT_BYTES = 128 * 1024 * 1024
_MAX_CANDIDATES = 10_000
_REQUIRED_INTAKE_TOKENS = frozenset(
    {
        BOOTSTRAP_CENSUS_INTAKE_TOKEN,
        BOOTSTRAP_CENSUS_DEDUP_TOKEN,
        BOOTSTRAP_CENSUS_CLASSIFICATION_TOKEN,
        BOOTSTRAP_CENSUS_NO_GRAPH_WRITE_TOKEN,
    }
)
_REQUIRED_INTAKE_NON_CLAIMS = frozenset(
    {
        "no_ecu_credit",
        "no_epoch_transition",
        "no_lmdb_write",
        "no_live_settlement",
        "no_production_minting",
        "no_public_graph_write",
        "no_verifier_role_claim",
        "no_wallet_write",
    }
)
_REQUIRED_RELEASE_FILES = {
    "core_package": (
        "release_artifacts/genesis_v05/core_slice_0/"
        "genesis_core_slice_0_authority_package.json"
    ),
    "core_signature_payload": (
        "release_artifacts/genesis_v05/core_slice_0/"
        "genesis_core_slice_0_authority_package.signature_payload.bin"
    ),
    "core_signature": (
        "release_artifacts/genesis_v05/core_slice_0/"
        "genesis_core_slice_0_authority_package.signature.hex"
    ),
    "core_verification": (
        "release_artifacts/genesis_v05/core_slice_0/"
        "genesis_core_slice_0_authority_package.verification.json"
    ),
    "slice1_package": (
        "release_artifacts/genesis_v05/public_rc_baseline_slice_1/"
        "genesis_v05_public_rc_baseline_slice_1.json"
    ),
    "slice1_signature_payload": (
        "release_artifacts/genesis_v05/public_rc_baseline_slice_1/"
        "genesis_v05_public_rc_baseline_slice_1.signature_payload.bin"
    ),
    "slice1_signature": (
        "release_artifacts/genesis_v05/public_rc_baseline_slice_1/"
        "genesis_v05_public_rc_baseline_slice_1.signature.hex"
    ),
    "slice1_verification": (
        "release_artifacts/genesis_v05/public_rc_baseline_slice_1/"
        "genesis_v05_public_rc_baseline_slice_1.verification.json"
    ),
}
_DOWNSTREAM_DEPENDENCIES = (
    "1576-slice-schema",
    "1576-slice-verifier",
    "1576-slice-materializer",
    "1576-sidecar-profile",
    "1576-private-slice",
)


class AgentBootstrapError(ValueError):
    """Stable local agent-bootstrap error."""


def build_agent_bootstrap_plan(
    *,
    census_intake_path: str | Path,
    release_manifest_path: str | Path = "release_artifacts/genesis_v05/manifest.json",
    repo_root: str | Path = ".",
    generated_at_utc: str | None = None,
    source_label: str = "local",
    require_accepted_receipts: bool = True,
) -> dict[str, Any]:
    """Build a deterministic local agent-bootstrap readiness plan."""

    root = Path(repo_root).resolve()
    if not root.is_dir():
        raise AgentBootstrapError("repo_root_not_directory")
    if generated_at_utc is None:
        generated_at_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    _validate_timestamp(generated_at_utc)
    if not isinstance(source_label, str) or not source_label:
        raise AgentBootstrapError("source_label_invalid")

    intake_path = _resolve_file_under_root(root, census_intake_path)
    manifest_path = _resolve_file_under_root(root, release_manifest_path)
    intake = _load_json_object(intake_path)
    intake_summary = _verify_census_intake(intake, require_accepted=require_accepted_receipts)
    release_summary = _verify_release_manifest(root, manifest_path)
    candidates = _candidate_rows(intake)

    body: dict[str, Any] = {
        "candidate_agent_count": len(candidates),
        "candidate_agents": candidates,
        "census_intake": {
            **intake_summary,
            "path": _relative_to_root(root, intake_path),
        },
        "generated_at_utc": generated_at_utc,
        "materialization_dependency_status": {
            "atlas_slice_manifest_materialization": (
                "pending_1576_slice_schema_verifier_materializer"
            ),
            "downstream_required_phases": list(_DOWNSTREAM_DEPENDENCIES),
            "full_distributed_bootstrap_rehearsal": "not_claimed_this_phase",
            "signed_release_artifacts_available": True,
        },
        "non_claims": _non_claims(),
        "phase": AGENT_BOOTSTRAP_PHASE,
        "release_artifacts": {
            **release_summary,
            "manifest_path": _relative_to_root(root, manifest_path),
        },
        "schema_version": AGENT_BOOTSTRAP_SCHEMA_VERSION,
        "source_label": source_label,
        "tokens": [
            AGENT_BOOTSTRAP_PLAN_TOKEN,
            AGENT_BOOTSTRAP_CENSUS_DEPENDENCY_TOKEN,
            AGENT_BOOTSTRAP_BASELINE_MANIFEST_TOKEN,
            AGENT_BOOTSTRAP_NO_VERIFIER_EPOCH_TOKEN,
        ],
    }
    body_sha256 = _sha256_canonical(body)
    plan = {
        **body,
        "plan_body_sha256": body_sha256,
        "plan_id": f"{_PLAN_PREFIX}{body_sha256}",
    }
    reject_float(plan, _FLOAT_TOKEN)
    return plan


def write_agent_bootstrap_plan(path: str | Path, plan: dict[str, Any]) -> Path:
    """Atomically write the local agent-bootstrap plan."""

    reject_float(plan, _FLOAT_TOKEN)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_name(f".{target.name}.tmp.{os.getpid()}")
    payload = json.dumps(plan, sort_keys=True, indent=2, allow_nan=False) + "\n"
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


def _verify_census_intake(
    intake: Mapping[str, Any],
    *,
    require_accepted: bool,
) -> dict[str, Any]:
    reject_float(intake, _FLOAT_TOKEN)
    if intake.get("schema_version") != BOOTSTRAP_CENSUS_INTAKE_SCHEMA_VERSION:
        raise AgentBootstrapError("agent_bootstrap_intake_schema_version_invalid")
    if intake.get("phase") != BOOTSTRAP_CENSUS_INTAKE_PHASE:
        raise AgentBootstrapError("agent_bootstrap_intake_phase_invalid")
    intake_hash = intake.get("intake_body_sha256")
    if not _is_sha256(str(intake_hash)):
        raise AgentBootstrapError("agent_bootstrap_intake_body_sha256_invalid")
    if intake.get("intake_id") != f"{_INTAKE_PREFIX}{intake_hash}":
        raise AgentBootstrapError("agent_bootstrap_intake_id_hash_mismatch")
    body = {
        key: value
        for key, value in intake.items()
        if key not in {"intake_body_sha256", "intake_id"}
    }
    if _sha256_canonical(body) != intake_hash:
        raise AgentBootstrapError("agent_bootstrap_intake_body_hash_mismatch")
    tokens = intake.get("tokens")
    if not isinstance(tokens, list) or not _REQUIRED_INTAKE_TOKENS.issubset(set(tokens)):
        raise AgentBootstrapError("agent_bootstrap_intake_required_tokens_missing")
    non_claims = intake.get("non_claims")
    if not isinstance(non_claims, dict):
        raise AgentBootstrapError("agent_bootstrap_intake_non_claims_invalid")
    for key in sorted(_REQUIRED_INTAKE_NON_CLAIMS):
        if non_claims.get(key) is not True:
            raise AgentBootstrapError(f"agent_bootstrap_intake_non_claim_missing:{key}")
    entries = intake.get("entries")
    if not isinstance(entries, list):
        raise AgentBootstrapError("agent_bootstrap_intake_entries_invalid")
    if len(entries) > _MAX_CANDIDATES:
        raise AgentBootstrapError("agent_bootstrap_candidate_count_exceeds_bound")
    if require_accepted and not entries:
        raise AgentBootstrapError("agent_bootstrap_no_accepted_receipts")
    if int(intake.get("accepted_count", -1)) != len(entries):
        raise AgentBootstrapError("agent_bootstrap_intake_accepted_count_mismatch")
    return {
        "accepted_count": len(entries),
        "duplicate_count": _required_non_negative_int(intake, "duplicate_count"),
        "intake_body_sha256": str(intake_hash),
        "intake_id": str(intake["intake_id"]),
        "invalid_count": _required_non_negative_int(intake, "invalid_count"),
        "verified": True,
    }


def _verify_release_manifest(root: Path, manifest_path: Path) -> dict[str, Any]:
    manifest = _load_json_object(manifest_path)
    reject_float(manifest, _FLOAT_TOKEN)
    if manifest.get("schema_version") != "ilc_release_artifact_manifest.v0.1":
        raise AgentBootstrapError("agent_bootstrap_release_manifest_schema_invalid")
    if manifest.get("phase") != "1575c-Fix3":
        raise AgentBootstrapError("agent_bootstrap_release_manifest_phase_invalid")
    files = manifest.get("files")
    if not isinstance(files, list):
        raise AgentBootstrapError("agent_bootstrap_release_manifest_files_invalid")
    by_path: dict[str, Mapping[str, Any]] = {}
    total_bytes = 0
    for raw in files:
        if not isinstance(raw, dict):
            raise AgentBootstrapError("agent_bootstrap_release_manifest_file_not_object")
        relpath = _required_str(raw, "path")
        if relpath in by_path:
            raise AgentBootstrapError(f"agent_bootstrap_release_manifest_duplicate_path:{relpath}")
        byte_size = _required_non_negative_int(raw, "byte_size")
        total_bytes += byte_size
        if byte_size > _MAX_ARTIFACT_BYTES:
            raise AgentBootstrapError(f"agent_bootstrap_release_artifact_too_large:{relpath}")
        if total_bytes > _MAX_TOTAL_ARTIFACT_BYTES:
            raise AgentBootstrapError("agent_bootstrap_release_artifact_total_too_large")
        path = _resolve_file_under_root(root, relpath)
        if path.stat().st_size != byte_size:
            raise AgentBootstrapError(f"agent_bootstrap_release_artifact_size_mismatch:{relpath}")
        if _sha256_file(path) != _required_sha256(raw, "sha256"):
            raise AgentBootstrapError(f"agent_bootstrap_release_artifact_hash_mismatch:{relpath}")
        by_path[relpath] = raw

    missing = sorted(path for path in _REQUIRED_RELEASE_FILES.values() if path not in by_path)
    if missing:
        raise AgentBootstrapError("agent_bootstrap_release_required_files_missing:" + ",".join(missing))

    core_summary = _verify_signed_package(
        root,
        package_relpath=_REQUIRED_RELEASE_FILES["core_package"],
        payload_relpath=_REQUIRED_RELEASE_FILES["core_signature_payload"],
        signature_relpath=_REQUIRED_RELEASE_FILES["core_signature"],
        verification_relpath=_REQUIRED_RELEASE_FILES["core_verification"],
        expected_artifact_kind="genesis_core_slice_0_authority_package",
    )
    slice1_summary = _verify_signed_package(
        root,
        package_relpath=_REQUIRED_RELEASE_FILES["slice1_package"],
        payload_relpath=_REQUIRED_RELEASE_FILES["slice1_signature_payload"],
        signature_relpath=_REQUIRED_RELEASE_FILES["slice1_signature"],
        verification_relpath=_REQUIRED_RELEASE_FILES["slice1_verification"],
        expected_artifact_kind="genesis_public_rc_baseline_slice_1",
    )
    return {
        "all_file_hashes_verified": True,
        "artifact_set": _required_str(manifest, "artifact_set"),
        "artifact_source_private_commit": _required_str(
            manifest,
            "artifact_source_private_commit",
        ),
        "core_slice_0": core_summary,
        "file_count": len(files),
        "public_rc_baseline_slice_1": slice1_summary,
        "signature_sidecars_verified": True,
        "verified": True,
    }


def _verify_signed_package(
    root: Path,
    *,
    package_relpath: str,
    payload_relpath: str,
    signature_relpath: str,
    verification_relpath: str,
    expected_artifact_kind: str,
) -> dict[str, Any]:
    package = _load_json_object(_resolve_file_under_root(root, package_relpath))
    verification = _load_json_object(_resolve_file_under_root(root, verification_relpath))
    if package.get("artifact_kind") != expected_artifact_kind:
        raise AgentBootstrapError("agent_bootstrap_package_artifact_kind_invalid")
    if verification.get("verification_result") != "signature_verified":
        raise AgentBootstrapError("agent_bootstrap_signature_sidecar_not_verified")
    if verification.get("stdout") != "signature_verified":
        raise AgentBootstrapError("agent_bootstrap_signature_sidecar_stdout_invalid")
    if _sha256_file(_resolve_file_under_root(root, payload_relpath)) != _required_sha256(
        verification,
        "signature_payload_sha256",
    ):
        raise AgentBootstrapError("agent_bootstrap_signature_payload_hash_mismatch")
    if _sha256_signature_hex_text(
        _resolve_file_under_root(root, signature_relpath)
    ) != _required_sha256(verification, "signature_sha256"):
        raise AgentBootstrapError("agent_bootstrap_signature_hash_mismatch")
    return {
        "artifact_kind": expected_artifact_kind,
        "detached_signature_sidecar_verified": True,
        "edge_count": _required_non_negative_int(package, "edge_count"),
        "node_count": _required_non_negative_int(package, "node_count"),
        "package_file_sha256": _sha256_file(_resolve_file_under_root(root, package_relpath)),
        "package_sha256": _required_sha256(package, "package_sha256"),
        "signature_status_field": str(package.get("signature_status", "")),
    }


def _candidate_rows(intake: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for entry in intake["entries"]:
        if not isinstance(entry, dict):
            raise AgentBootstrapError("agent_bootstrap_intake_entry_not_object")
        base = {
            "agent_identity_configured": bool(entry.get("agent_identity_configured")),
            "baseline_all_signatures_verified": bool(
                entry.get("baseline_all_signatures_verified")
            ),
            "bootstrap_classification": _required_str(entry, "classification"),
            "ccss_agent_id": str(entry.get("ccss_agent_id", "")),
            "d2e_lineage_id": str(entry.get("d2e_lineage_id", "")),
            "graph_write_status": "not_written",
            "install_surface": _required_str(entry, "install_surface"),
            "receipt_id": _required_str(entry, "receipt_id"),
            "verifier_status": "not_granted",
        }
        rows.append(
            {
                **base,
                "bootstrap_candidate_id": _CANDIDATE_PREFIX + _sha256_canonical(base),
            }
        )
    return sorted(rows, key=lambda row: str(row["bootstrap_candidate_id"]))


def _non_claims() -> dict[str, bool]:
    return {
        "no_ccss_delivery_activation": True,
        "no_ecu_credit": True,
        "no_epoch_transition": True,
        "no_full_distributed_bootstrap_rehearsal": True,
        "no_lmdb_write": True,
        "no_live_settlement": True,
        "no_production_minting": True,
        "no_public_graph_write": True,
        "no_public_p2p_activation": True,
        "no_verifier_role_grant": True,
        "no_wallet_write": True,
    }


def _load_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise AgentBootstrapError(f"agent_bootstrap_json_invalid:{path}") from exc
    if not isinstance(payload, dict):
        raise AgentBootstrapError(f"agent_bootstrap_json_not_object:{path}")
    return payload


def _resolve_file_under_root(root: Path, path: str | Path) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = root / candidate
    resolved = candidate.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise AgentBootstrapError(f"agent_bootstrap_path_outside_repo:{path}") from exc
    if not resolved.is_file():
        raise AgentBootstrapError(f"agent_bootstrap_file_not_found:{path}")
    return resolved


def _relative_to_root(root: Path, path: Path) -> str:
    return path.resolve().relative_to(root).as_posix()


def _required_str(payload: Mapping[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise AgentBootstrapError(f"agent_bootstrap_required_string_invalid:{key}")
    return value


def _required_non_negative_int(payload: Mapping[str, Any], key: str) -> int:
    value = payload.get(key)
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise AgentBootstrapError(f"agent_bootstrap_required_int_invalid:{key}")
    return value


def _required_sha256(payload: Mapping[str, Any], key: str) -> str:
    value = _required_str(payload, key)
    if not _is_sha256(value):
        raise AgentBootstrapError(f"agent_bootstrap_required_sha256_invalid:{key}")
    return value


def _sha256_file(path: Path, *, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sha256_signature_hex_text(path: Path) -> str:
    return hashlib.sha256(path.read_text(encoding="utf-8").strip().encode("utf-8")).hexdigest()


def _sha256_canonical(payload: Mapping[str, Any]) -> str:
    body = canonical_json(payload, float_token=_FLOAT_TOKEN)
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def _is_sha256(value: str) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(c in _HEX_64 for c in value)


def _validate_timestamp(value: str) -> None:
    if not isinstance(value, str) or not value:
        raise AgentBootstrapError("generated_at_utc_invalid")
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise AgentBootstrapError("generated_at_utc_invalid") from exc
    if parsed.tzinfo is None:
        raise AgentBootstrapError("generated_at_utc_must_include_timezone")
