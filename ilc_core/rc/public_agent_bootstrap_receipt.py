# SPDX-License-Identifier: AGPL-3.0-only
"""Local public-agent bootstrap receipt runtime.

The receipt is intentionally local and read-only. It records install proof,
sanitized identity status, signed baseline artifact status, and explicit
non-claims without writing LMDB, wallets, settlement state, or public graph
state.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ilc_core.private_json_guardrails import canonical_json, reject_float
from ilc_core.sidecars.public_path_activation import public_path_activation_manifest


PUBLIC_AGENT_BOOTSTRAP_RECEIPT_SCHEMA_VERSION = "public_agent_bootstrap_receipt_1576.v0.1"
PUBLIC_AGENT_BOOTSTRAP_RECEIPT_PHASE = "1576-public-agent-bootstrap-receipts"
PUBLIC_AGENT_BOOTSTRAP_RECEIPT_TOKEN = (
    "public_agent_bootstrap_receipts_local_receipt_committed_phase_1576"
)
PUBLIC_AGENT_BOOTSTRAP_BASELINE_TOKEN = (
    "install_proof_agent_identity_status_baseline_verification_receipt_phase_1576"
)
PUBLIC_AGENT_BOOTSTRAP_NON_CLAIMS_TOKEN = (
    "bootstrap_receipt_no_mint_no_settlement_non_claims_phase_1576"
)
PUBLIC_AGENT_BOOTSTRAP_GRAPH_BRIDGE_TOKEN = (
    "bootstrap_receipt_graph_evidence_bridge_ready_phase_1576"
)
DISTRIBUTION_TELEMETRY_BOUNDARY_TOKEN = (
    "distribution_telemetry_not_graph_evidence_boundary_recorded_phase_1576"
)

_HEX_40 = frozenset("0123456789abcdef")
_RECEIPT_FLOAT_TOKEN = "public_agent_bootstrap_receipt_float_not_allowed"
_DEFAULT_BASELINE_ARTIFACTS: tuple[dict[str, str], ...] = (
    {
        "artifact_id": "genesis_core_slice_0_authority_package",
        "slice_id": "genesis_core_slice_0",
        "payload_relpath": (
            "out/genesis_v05_core_slice_0_1575c_fix3/"
            "genesis_core_slice_0_authority_package.signature_payload.bin"
        ),
        "signature_relpath": (
            "out/genesis_v05_core_slice_0_1575c_fix3/"
            "genesis_core_slice_0_authority_package.signature.hex"
        ),
    },
    {
        "artifact_id": "genesis_v05_public_rc_baseline_slice_1",
        "slice_id": "public_rc_baseline_slice_1",
        "payload_relpath": (
            "out/genesis_v05_atlas_graph_package_fix3/"
            "genesis_v05_public_rc_baseline_slice_1.signature_payload.bin"
        ),
        "signature_relpath": (
            "out/genesis_v05_atlas_graph_package_fix3/"
            "genesis_v05_public_rc_baseline_slice_1.signature.hex"
        ),
    },
)


class PublicAgentBootstrapReceiptError(ValueError):
    """Stable local receipt error."""


def build_public_agent_bootstrap_receipt(
    *,
    repo_root: str | Path = ".",
    install_surface: str = "local",
    generated_at_utc: str | None = None,
    graph_state_path: str | Path = ".ilc_d2e03_graph.json",
    identity_state_path: str | Path | None = None,
    ccss_home: str | Path | None = None,
    verifier_path: str | Path = "ilc_consensus/target/debug/pq_sign",
    skip_signature_verify: bool = False,
    require_baseline_artifacts: bool = False,
) -> dict[str, Any]:
    """Build a side-effect-free bootstrap receipt payload."""

    root = Path(repo_root).resolve()
    if not root.is_dir():
        raise PublicAgentBootstrapReceiptError("repo_root_not_directory")
    if install_surface not in {"github", "clawhub", "openclaw", "private-dev-main", "local"}:
        raise PublicAgentBootstrapReceiptError("install_surface_invalid")

    if generated_at_utc is None:
        generated_at_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    _validate_timestamp(generated_at_utc)

    graph_state = Path(graph_state_path)
    identity_path = (
        Path(identity_state_path)
        if identity_state_path is not None
        else graph_state.with_name(".ilc_d2e04_identity_state.json")
    )

    source_commit = _current_git_commit(root)
    body: dict[str, Any] = {
        "activation_state": _activation_state_snapshot(),
        "agent_identity_status": _agent_identity_status(identity_path, ccss_home),
        "baseline_slice_verification": _baseline_slice_verification(
            root=root,
            verifier_path=Path(verifier_path),
            skip_signature_verify=skip_signature_verify,
            require_baseline_artifacts=require_baseline_artifacts,
        ),
        "distribution_telemetry_boundary": {
            "github_visits_are_graph_evidence": False,
            "github_clones_are_graph_evidence": False,
            "clawhub_installs_are_graph_evidence": False,
            "token": DISTRIBUTION_TELEMETRY_BOUNDARY_TOKEN,
        },
        "generated_at_utc": generated_at_utc,
        "install_proof": {
            "install_surface": install_surface,
            "repo_root_git_head": source_commit,
            "repo_root_git_head_valid_40_hex": _is_git_sha(source_commit),
            "working_tree_required_clean": False,
        },
        "non_claims": _non_claims(),
        "phase": PUBLIC_AGENT_BOOTSTRAP_RECEIPT_PHASE,
        "receipt_kind": "public_agent_bootstrap_receipt",
        "schema_version": PUBLIC_AGENT_BOOTSTRAP_RECEIPT_SCHEMA_VERSION,
        "tokens": [
            PUBLIC_AGENT_BOOTSTRAP_RECEIPT_TOKEN,
            PUBLIC_AGENT_BOOTSTRAP_BASELINE_TOKEN,
            PUBLIC_AGENT_BOOTSTRAP_NON_CLAIMS_TOKEN,
            PUBLIC_AGENT_BOOTSTRAP_GRAPH_BRIDGE_TOKEN,
            DISTRIBUTION_TELEMETRY_BOUNDARY_TOKEN,
        ],
    }
    body_sha256 = _sha256_canonical(body)
    receipt = {
        **body,
        "receipt_body_sha256": body_sha256,
        "receipt_id": f"public_agent_bootstrap_receipt:{body_sha256}",
    }
    reject_float(receipt, _RECEIPT_FLOAT_TOKEN)
    return receipt


def write_public_agent_bootstrap_receipt(
    path: str | Path,
    receipt: dict[str, Any],
) -> Path:
    """Atomically write a receipt JSON file and return its path."""

    reject_float(receipt, _RECEIPT_FLOAT_TOKEN)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_name(f".{target.name}.tmp.{os.getpid()}")
    payload = json.dumps(receipt, sort_keys=True, indent=2, allow_nan=False) + "\n"
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


def _activation_state_snapshot() -> dict[str, Any]:
    manifest = public_path_activation_manifest()
    return {
        "ecu_distribution_activated": bool(manifest["ecu_distribution_activated"]),
        "epoch_transition_triggered": bool(manifest["epoch_transition_triggered"]),
        "non_loopback_sidecar_projection_activated": bool(
            manifest["non_loopback_sidecar_projection_activated"]
        ),
        "openclaw_p2p_activated": bool(manifest["openclaw_p2p_activated"]),
        "public_confidential_coordination_activated": bool(
            manifest["public_confidential_coordination_activated"]
        ),
        "public_fetch_serving_activated": bool(manifest["public_fetch_serving_activated"]),
        "public_p2p_activated": bool(manifest["public_p2p_activated"]),
        "transport_principal_cdl_ratified": bool(manifest["transport_principal_cdl_ratified"]),
        "version": str(manifest["version"]),
    }


def _agent_identity_status(
    identity_state_path: Path,
    ccss_home: str | Path | None,
) -> dict[str, Any]:
    d2e_state = _read_json_object(identity_state_path)
    ccss_state = _read_json_object(_ccss_identity_path(ccss_home))

    d2e = {
        "configured": isinstance(d2e_state, dict),
        "lineage_id": str(d2e_state.get("lineage_id", "")) if isinstance(d2e_state, dict) else "",
        "rotation_count": str(d2e_state.get("rotation_count", "")) if isinstance(d2e_state, dict) else "",
        "status": str(d2e_state.get("status", "")) if isinstance(d2e_state, dict) else "",
    }
    ccss = {
        "agent_id": str(ccss_state.get("agent_id", "")) if isinstance(ccss_state, dict) else "",
        "configured": isinstance(ccss_state, dict),
        "public_key_sha256": _public_key_sha256(ccss_state) if isinstance(ccss_state, dict) else "",
        "reply_endpoint_configured": _reply_endpoint_configured(ccss_state)
        if isinstance(ccss_state, dict)
        else False,
        "schema": str(ccss_state.get("schema", "")) if isinstance(ccss_state, dict) else "",
    }
    return {
        "configured": bool(d2e["configured"] or ccss["configured"]),
        "ccss_identity": ccss,
        "d2e_identity": d2e,
        "private_key_material_included": False,
    }


def _baseline_slice_verification(
    *,
    root: Path,
    verifier_path: Path,
    skip_signature_verify: bool,
    require_baseline_artifacts: bool,
) -> dict[str, Any]:
    artifacts = [
        _verify_artifact(
            root=root,
            verifier_path=verifier_path,
            skip_signature_verify=skip_signature_verify,
            require_baseline_artifacts=require_baseline_artifacts,
            **artifact,
        )
        for artifact in _DEFAULT_BASELINE_ARTIFACTS
    ]
    all_verified = all(artifact["signature_verified"] is True for artifact in artifacts)
    all_present = all(
        artifact["payload_present"] is True and artifact["signature_present"] is True
        for artifact in artifacts
    )
    return {
        "all_artifacts_present": all_present,
        "all_signatures_verified": all_verified,
        "artifacts": artifacts,
        "verification_policy": (
            "required" if require_baseline_artifacts else "best_effort_local"
        ),
    }


def _verify_artifact(
    *,
    root: Path,
    artifact_id: str,
    slice_id: str,
    payload_relpath: str,
    signature_relpath: str,
    verifier_path: Path,
    skip_signature_verify: bool,
    require_baseline_artifacts: bool,
) -> dict[str, Any]:
    payload_path = root / payload_relpath
    signature_path = root / signature_relpath
    payload_present = payload_path.is_file()
    signature_present = signature_path.is_file()
    record: dict[str, Any] = {
        "artifact_id": artifact_id,
        "payload_present": payload_present,
        "payload_relpath": payload_relpath,
        "signature_present": signature_present,
        "signature_relpath": signature_relpath,
        "slice_id": slice_id,
    }
    if payload_present:
        record["payload_sha256"] = _sha256_file(payload_path)
    if signature_present:
        signature_hex = "".join(signature_path.read_text(encoding="utf-8").split())
        record["signature_hex_length"] = len(signature_hex)
        record["signature_sha256"] = hashlib.sha256(signature_hex.encode("utf-8")).hexdigest()

    if not payload_present or not signature_present:
        if require_baseline_artifacts:
            raise PublicAgentBootstrapReceiptError(f"baseline_artifact_missing:{artifact_id}")
        record["signature_verified"] = "not_checked_artifact_missing"
        return record
    if skip_signature_verify:
        record["signature_verified"] = "not_checked_skipped_by_caller"
        return record

    resolved_verifier = verifier_path if verifier_path.is_absolute() else root / verifier_path
    if not resolved_verifier.is_file():
        if require_baseline_artifacts:
            raise PublicAgentBootstrapReceiptError("pq_sign_verifier_missing")
        record["signature_verified"] = "not_checked_verifier_missing"
        return record

    result = subprocess.run(
        [
            str(resolved_verifier),
            "verify",
            "--input-file",
            str(payload_path),
            "--signature-hex",
            "".join(signature_path.read_text(encoding="utf-8").split()),
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    record["verification_stdout"] = result.stdout.strip()
    record["signature_verified"] = (
        result.returncode == 0 and result.stdout.strip() == "signature_verified"
    )
    if require_baseline_artifacts and record["signature_verified"] is not True:
        raise PublicAgentBootstrapReceiptError(f"baseline_signature_not_verified:{artifact_id}")
    return record


def _non_claims() -> dict[str, bool]:
    return {
        "no_ecu_distribution_activation": True,
        "no_economic_guard_clearance": True,
        "no_epoch_transition": True,
        "no_live_settlement": True,
        "no_mainnet_activation": True,
        "no_production_minting": True,
        "no_public_graph_write": True,
        "no_public_p2p_activation": True,
        "no_treasury_write": True,
        "no_wallet_write": True,
    }


def _current_git_commit(root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return "unknown"
    value = result.stdout.strip()
    return value if result.returncode == 0 and _is_git_sha(value) else "unknown"


def _is_git_sha(value: str) -> bool:
    return isinstance(value, str) and len(value) == 40 and all(c in _HEX_40 for c in value)


def _ccss_identity_path(ccss_home: str | Path | None) -> Path:
    if ccss_home is None or str(ccss_home) == "":
        return Path.home() / ".ilc" / "ccss" / "identity.json"
    return Path(ccss_home) / "identity.json"


def _read_json_object(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _public_key_sha256(state: dict[str, Any]) -> str:
    value = str(state.get("ccss_recipient_pubkey", ""))
    try:
        return hashlib.sha256(bytes.fromhex(value)).hexdigest() if value else ""
    except ValueError:
        return ""


def _reply_endpoint_configured(state: dict[str, Any]) -> bool:
    endpoint = str(state.get("ccss_peer_endpoint", ""))
    onion = str(state.get("ccss_contact_onion", ""))
    return bool(endpoint or onion)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sha256_canonical(payload: dict[str, Any]) -> str:
    body = canonical_json(payload, float_token=_RECEIPT_FLOAT_TOKEN)
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def _validate_timestamp(value: str) -> None:
    if not isinstance(value, str) or not value:
        raise PublicAgentBootstrapReceiptError("generated_at_utc_invalid")
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise PublicAgentBootstrapReceiptError("generated_at_utc_invalid") from exc
    if parsed.tzinfo is None:
        raise PublicAgentBootstrapReceiptError("generated_at_utc_must_include_timezone")
