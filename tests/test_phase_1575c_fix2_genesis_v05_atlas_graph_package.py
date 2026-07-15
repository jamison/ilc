from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from ilc_core.storage.genesis_atlas_candidate_lmdb_adapter import (
    GenesisAtlasCandidateStore,
)


ROOT = Path(__file__).resolve().parents[1]
LMDB_ROOT = ROOT / "out/genesis_base_graph_v0.4_unified.lmdb"
OUT_DIR = ROOT / "out/genesis_v05_atlas_graph_package_fix2"
PACKAGE = OUT_DIR / "genesis_v05_public_rc_atlas_graph_package.json"
MATERIALIZATION = OUT_DIR / "materialization_receipt.json"
SIGNING_REQUEST = OUT_DIR / "genesis_v05_public_rc_atlas_graph_package.signing_request.json"
SIGNATURE_PAYLOAD = OUT_DIR / "genesis_v05_public_rc_atlas_graph_package.signature_payload.bin"
SIGNATURE_HEX = OUT_DIR / "genesis_v05_public_rc_atlas_graph_package.signature.hex"
VERIFICATION = OUT_DIR / "genesis_v05_public_rc_atlas_graph_package.verification.json"
REGISTRATION_RECEIPT = OUT_DIR / "phase_file_registration_receipt.json"
REGISTRATION_REFRESH_RECEIPT = OUT_DIR / "phase_file_registration_refresh_receipt.json"
STATUS = ROOT / "docs/phases/STATUS.md"
FIX1_ENVELOPE = ROOT / "out/genesis_public_rc_signing_envelope_v0.5.json"
HUB_NODE = "artifact:genesis_source_tree_manifest_candidate_1545p_fix38"
DOMAIN = "ilc-genesis-v05-public-rc-atlas-graph-package"
PROJECTION_DIGEST = "65402e75945a86ccc14bd83610e5f721ea17ed14f6dd5e4d4547647a8853c900"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _canonical_bytes(payload: object) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _contains_float(value: object) -> bool:
    if isinstance(value, float):
        return True
    if isinstance(value, dict):
        return any(_contains_float(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_float(item) for item in value)
    return False


def _edge_source(edge: dict[str, Any]) -> str:
    return str(edge.get("source") or edge.get("src") or edge.get("source_candidate_id"))


def _edge_target(edge: dict[str, Any]) -> str:
    return str(edge.get("target") or edge.get("tgt") or edge.get("target_candidate_id"))


def test_fix38_hub_source_tree_member_edges_are_repaired() -> None:
    store = GenesisAtlasCandidateStore(LMDB_ROOT, allow_synthetic_edge_keys=True)
    try:
        bad_edges = [
            edge
            for edge in store.iter_edges()
            if edge.get("edge_type") == "SOURCE_TREE_MEMBER"
            and (_edge_source(edge) == HUB_NODE or _edge_target(edge) == HUB_NODE)
        ]
    finally:
        store.close()
    assert bad_edges == []


def test_package_exists_and_is_canonical_json_without_floats() -> None:
    package = _load(PACKAGE)
    assert PACKAGE.read_bytes() == _canonical_bytes(package) + b"\n"
    assert package["artifact_kind"] == "genesis_v05_public_rc_atlas_graph_package"
    assert package["artifact_version"] == "v0.5"
    assert _contains_float(package) is False


def test_package_projection_counts_and_privacy_boundary() -> None:
    package = _load(PACKAGE)
    assert package["node_count"] == 1035
    assert package["edge_count"] == 3841
    assert package["projection_summary"]["included_node_projection_counts"] == {
        "genesis_core_star_map": 428,
        "public_protocol_graph": 607,
    }
    assert package["privacy_boundary"]["excluded_private_material_included"] is False
    assert package["privacy_boundary"]["support_candidate_graph_included"] is False


def test_materialization_receipt_proves_lmdb_projection_digest() -> None:
    receipt = _load(MATERIALIZATION)
    assert receipt["verified_equal"] is True
    assert receipt["bad_fix38_source_tree_member_count_after"] == 0
    assert receipt["node_count"] == 1035
    assert receipt["edge_count"] == 3841
    assert (
        receipt["source_lmdb_projection_digest"]
        == receipt["materialized_graph_digest_from_package_rows"]
    )
    assert receipt["source_lmdb_projection_digest"] == PROJECTION_DIGEST
    assert receipt["package_file_sha256"] == hashlib.sha256(PACKAGE.read_bytes()).hexdigest()


def test_phase_file_registration_receipt_is_support_only_and_clean() -> None:
    receipt = _load(REGISTRATION_RECEIPT)
    assert receipt["status"] == "PASS"
    assert receipt["accepted_node_count"] == 33
    assert receipt["accepted_edge_count"] == 34
    assert receipt["rejected_edge_count"] == 0
    assert receipt["file_identity_update_count"] == 17
    assert all(receipt["post_invariants"].values())


def test_phase_file_registration_refresh_receipt_updates_content_identities() -> None:
    receipt = _load(REGISTRATION_REFRESH_RECEIPT)
    assert receipt["status"] == "PASS"
    assert receipt["accepted_node_count"] >= 0
    assert receipt["accepted_edge_count"] >= 0
    assert receipt["rejected_edge_count"] == 0
    assert receipt["file_identity_update_count"] >= 17
    assert all(receipt["post_invariants"].values())


def test_signature_payload_and_request_match_package_bytes() -> None:
    request = _load(SIGNING_REQUEST)
    assert request["domain_separator"] == DOMAIN
    assert request["package_path"] == "out/genesis_v05_atlas_graph_package_fix2/genesis_v05_public_rc_atlas_graph_package.json"
    assert request["signature_payload_path"] == "out/genesis_v05_atlas_graph_package_fix2/genesis_v05_public_rc_atlas_graph_package.signature_payload.bin"
    assert SIGNATURE_PAYLOAD.read_bytes() == DOMAIN.encode("utf-8") + PACKAGE.read_bytes()
    assert request["signature_payload_sha256"] == hashlib.sha256(
        SIGNATURE_PAYLOAD.read_bytes()
    ).hexdigest()


def test_prior_v05_envelope_is_not_graph_package() -> None:
    envelope = _load(FIX1_ENVELOPE)
    package = _load(PACKAGE)
    assert envelope["artifact_kind"] == "genesis_public_rc_signing_envelope"
    assert package["artifact_kind"] == "genesis_v05_public_rc_atlas_graph_package"
    assert envelope["artifact_kind"] != package["artifact_kind"]


def test_status_records_blocked_signature_boundary_not_success_tokens() -> None:
    status = STATUS.read_text(encoding="utf-8")
    assert "genesis_v05_public_rc_atlas_graph_package_materialized_phase_1575c_fix2" in status
    assert "genesis_v05_public_rc_atlas_graph_package_lmdb_replay_verified_phase_1575c_fix2" in status
    assert "genesis_v05_public_rc_atlas_graph_package_signature_payload_committed_phase_1575c_fix2" in status
    assert (
        "blocked_with_named_defect:genesis_v05_atlas_graph_package_operator_signature_not_provided_phase_1575c_fix2"
        in status
    )
    assert "genesis_v05_public_rc_atlas_graph_package_signed_phase_1575c_fix2" not in status
    assert (
        "genesis_v05_public_rc_atlas_graph_package_signature_verified_phase_1575c_fix2"
        not in status
    )


def test_signature_verification_record_if_signature_exists() -> None:
    if not SIGNATURE_HEX.exists():
        assert not VERIFICATION.exists()
        return
    verification = _load(VERIFICATION)
    assert verification["verification_result"] == "signature_verified"
