#!/usr/bin/env python3
"""Assemble GAP-PUBLIC-RC-NATIVE-STATUS-EVIDENCE-00a from durable Phase 1603 evidence."""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PHASE = "GAP-PUBLIC-RC-NATIVE-STATUS-EVIDENCE-00a"
SCHEMA_VERSION = "native_status_evidence_00a.v0.1"
OUTPUT_TOKEN = "native_status_evidence_assembled_GAP_PUBLIC_RC_NATIVE_STATUS_EVIDENCE_00a"
SOURCE_EVIDENCE_PATH = Path("out/phase_1603_public_user_smoke/evidence.json")
OUTPUT_PATH = Path("out/gap_public_rc_native_status_evidence_00a/native_status_evidence_00a.json")
EXPECTED_SOURCE_SHA256 = "aabfa87fb9ec96b8f2ac234b60e647aa8c30ebb305d2925f6dedb08c0efe7437"
STALE_RUST_BRIDGE_MARKER = "python_in_memory_ecu_python_rust_balance_bridge_missing_phase_1597"
EXPECTED_SOURCE_SCHEMA_VERSION = "phase_1603_public_user_smoke.v0.2"
EXPECTED_SOURCE_PHASE = "1603"
EXPECTED_GOSSIP_DELIVERY = "deferred \u2014 gossip peers not configured"
EXPECTED_PACKAGE_NAME = "ilc-core"
EXPECTED_PACKAGE_VERSION = "0.4.31"

ASSERTIONS_VERIFIED = [
    "agent_id_is_96_hex",
    "node_id_is_cid_v1",
    "graph_persistence_is_persisted",
    "balance_ecu_source_is_rust_committed_aggregate",
    "pending_attribution_quote_is_zero",
    "committed_ecu_balance_is_zero",
    "non_claim_committed_balance_visibility_present",
    "stale_rust_bridge_marker_absent",
]

NON_CLAIMS = [
    "no_native_network_ingress_claim",
    "no_signed_peer_response_claim",
    "no_live_validator_acceptance_claim",
    "gossip_delivery_deferred_is_expected_not_failure",
    "no_nonzero_ecu_claim",
    "no_monthly_close_claim",
    "no_ecu_minting",
    "no_ilc_minting",
    "no_settlement_claim",
    "committed_balance_visibility_not_monthly_close_eligibility",
]


class NativeStatusEvidence00aError(ValueError):
    """Named-token assembly failure."""


def _fail(token: str) -> None:
    raise NativeStatusEvidence00aError(token)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_source(path: Path = SOURCE_EVIDENCE_PATH) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, dict):
        _fail("source_evidence_result_not_pass_00a")
    return payload


def assert_source_sha(
    path: Path = SOURCE_EVIDENCE_PATH,
    expected_sha256: str = EXPECTED_SOURCE_SHA256,
) -> str:
    actual_sha256 = sha256_file(path)
    if actual_sha256 != expected_sha256:
        _fail("source_evidence_sha256_mismatch_00a")
    return actual_sha256


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def assemble_evidence(
    source: dict[str, Any],
    *,
    source_sha256: str = EXPECTED_SOURCE_SHA256,
    produced_at_utc: str | None = None,
) -> dict[str, Any]:
    if source_sha256 != EXPECTED_SOURCE_SHA256:
        _fail("source_evidence_sha256_mismatch_00a")

    if source.get("result") != "pass":
        _fail("source_evidence_result_not_pass_00a")
    if (
        source.get("schema_version") != EXPECTED_SOURCE_SCHEMA_VERSION
        or source.get("phase") != EXPECTED_SOURCE_PHASE
    ):
        _fail("source_evidence_schema_mismatch_00a")

    if STALE_RUST_BRIDGE_MARKER in json.dumps(source, sort_keys=True):
        _fail("stale_rust_bridge_marker_present_00a")

    agent_id = source.get("agent_id")
    if not isinstance(agent_id, str) or not re.fullmatch(r"[0-9a-f]{96}", agent_id):
        _fail("agent_id_invalid_in_source_evidence_00a")

    submit = source.get("submit")
    if not isinstance(submit, dict):
        _fail("node_id_not_cid_v1_00a")

    node_id = submit.get("node_id")
    if not isinstance(node_id, str) or not node_id.startswith("bafy"):
        _fail("node_id_not_cid_v1_00a")

    node_parse = submit.get("node_id_parse")
    node_id_cid_version = node_parse.get("version") if isinstance(node_parse, dict) else None
    if node_id_cid_version != 1:
        _fail("node_id_not_cid_v1_00a")

    graph_persistence = submit.get("graph_persistence")
    if graph_persistence != "persisted":
        _fail("graph_persistence_not_persisted_00a")

    primitive_type = submit.get("node_primitive_type")
    if primitive_type != "observation":
        _fail("node_primitive_type_invalid_00a")

    source_refs = submit.get("source_refs")
    source_refs_count = len(source_refs) if isinstance(source_refs, list) else 0
    if source_refs_count != 1:
        _fail("source_refs_count_invalid_00a")

    gossip_delivery = submit.get("gossip_delivery")
    if gossip_delivery != EXPECTED_GOSSIP_DELIVERY:
        _fail("gossip_delivery_unexpected_00a")

    ecu_status = source.get("ecu_status")
    if not isinstance(ecu_status, dict):
        _fail("balance_ecu_source_invalid_00a")

    if ecu_status.get("balance_ecu_source") != "rust_balance_store_committed_aggregate":
        _fail("balance_ecu_source_invalid_00a")
    if ecu_status.get("pending_attribution_quote") != "0":
        _fail("pending_attribution_quote_nonzero_00a")
    if ecu_status.get("committed_ecu_balance") != "0":
        _fail("committed_ecu_balance_nonzero_00a")
    if ecu_status.get("non_claim") != "committed_balance_visibility_not_monthly_close_eligibility":
        _fail("non_claim_missing_from_source_evidence_00a")

    package = source.get("package")
    if not isinstance(package, dict):
        _fail("package_identity_invalid_00a")
    if package.get("name") != EXPECTED_PACKAGE_NAME or package.get("version") != EXPECTED_PACKAGE_VERSION:
        _fail("package_identity_invalid_00a")

    clean_venv = bool(package.get("clean_venv"))
    repo_import_leak_checked = package.get("repo_import_leak_checked") is True
    if not clean_venv or not repo_import_leak_checked:
        _fail("clean_venv_or_repo_import_leak_check_invalid_00a")

    return {
        "schema_version": SCHEMA_VERSION,
        "produced_by": PHASE,
        "produced_at_utc": produced_at_utc or _utc_now(),
        "source_evidence": {
            "path": SOURCE_EVIDENCE_PATH.as_posix(),
            "sha256": source_sha256,
            "schema_version": EXPECTED_SOURCE_SCHEMA_VERSION,
            "phase": EXPECTED_SOURCE_PHASE,
        },
        "agent_id": agent_id,
        "agent_id_valid": True,
        "graph_node": {
            "node_id": node_id,
            "node_id_cid_version": node_id_cid_version,
            "graph_persistence": graph_persistence,
            "primitive_type": primitive_type,
            "source_refs_count": source_refs_count,
        },
        "gossip": {
            "delivery": gossip_delivery,
            "non_claim": "gossip_delivery_deferred_is_expected_not_failure",
        },
        "ecu_status": {
            "ok": ecu_status.get("ok") is True,
            "balance_ecu_source": ecu_status.get("balance_ecu_source"),
            "pending_attribution_quote": ecu_status.get("pending_attribution_quote"),
            "committed_ecu_balance": ecu_status.get("committed_ecu_balance"),
            "non_claim": ecu_status.get("non_claim"),
        },
        "package": {
            "name": package.get("name"),
            "version": package.get("version"),
            "clean_venv": clean_venv,
            "repo_import_leak_checked": repo_import_leak_checked,
        },
        "assertions_verified": list(ASSERTIONS_VERIFIED),
        "non_claims": list(NON_CLAIMS),
        "output_token": OUTPUT_TOKEN,
        "result": "pass",
    }


def write_evidence(evidence: dict[str, Any], output_path: Path = OUTPUT_PATH) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        dir=output_path.parent,
        prefix=f".{output_path.name}.",
        suffix=".tmp",
        text=True,
    )
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(evidence, f, sort_keys=True, indent=2)
            f.write("\n")
        os.replace(tmp_path, output_path)
    except Exception:
        try:
            tmp_path.unlink()
        except FileNotFoundError:
            pass
        raise


def main() -> int:
    source_sha256 = assert_source_sha()
    source = load_source()
    evidence = assemble_evidence(source, source_sha256=source_sha256)
    write_evidence(evidence)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
