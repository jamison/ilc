import json

import pytest

from ilc_core.network.d2d.cdl087_serving_peer_evidence import (
    BOOTSTRAP_SNAPSHOT_EVIDENCE_TOKEN,
    CDL087_SERVING_PEER_EVIDENCE_VERSION,
    NO_PUBLIC_FETCH_SERVING_TOKEN,
    PRODUCTION_CANDIDATE_TIER_CLASSIFICATION_TOKEN,
    TIER_A,
    TIER_B,
    TIER_C,
    build_bootstrap_snapshot,
    build_tier_classification_evidence,
    classify_artifact,
    compute_artifact_hash,
    export_bootstrap_snapshot_json,
    verify_bootstrap_snapshot,
    verify_bootstrap_snapshot_json,
)

GENESIS_HASH = "a" * 64
AUTHORITY_REF = "b" * 64
LINEAGE_REF = "c" * 64


def _artifact(
    artifact_id: str,
    artifact_type: str,
    payload: dict[str, object],
    *,
    lineage: list[str] | None = None,
) -> dict[str, object]:
    return {
        "artifact_id": artifact_id,
        "artifact_payload": payload,
        "artifact_type": artifact_type,
        "lineage_proof_chain": lineage or [GENESIS_HASH, LINEAGE_REF],
    }


def _snapshot() -> dict[str, object]:
    return build_bootstrap_snapshot(
        [
            _artifact(
                "genesis-root",
                "genesis_root",
                {"root": GENESIS_HASH, "kind": "genesis_root"},
            ),
            _artifact(
                "recent-route-index",
                "route_index",
                {"epoch": 9, "kind": "route_index"},
            ),
        ],
        authority_refs=[AUTHORITY_REF],
        epoch_checkpoint_range={"start_epoch": 8, "end_epoch": 10},
        genesis_domain_hash=GENESIS_HASH,
        snapshot_epoch=9,
    )


def test_tier_classifier_records_required_cdl087_classes() -> None:
    assert classify_artifact({"artifact_type": "genesis_root"}) == TIER_A
    assert classify_artifact({"artifact_type": "accepted_cdl"}) == TIER_A
    assert classify_artifact({"artifact_type": "signed_manifest"}) == TIER_A
    assert classify_artifact({"artifact_type": "route_index"}) == TIER_B
    assert classify_artifact({"artifact_type": "research_note"}) == TIER_C


def test_build_tier_classification_evidence_is_local_and_non_public() -> None:
    evidence = build_tier_classification_evidence(
        [
            {"artifact_id": "adr-0004", "artifact_type": "adr_0004_truth_primitive"},
            {"artifact_id": "epoch-delta", "artifact_type": "epoch_delta"},
            {"artifact_id": "paper", "artifact_type": "research_note"},
        ],
        serving_peer_id="local-production-candidate-peer",
    )

    assert evidence["version"] == CDL087_SERVING_PEER_EVIDENCE_VERSION
    assert evidence["tokens"]["classification"] == PRODUCTION_CANDIDATE_TIER_CLASSIFICATION_TOKEN
    assert evidence["non_public_boundary"]["token"] == NO_PUBLIC_FETCH_SERVING_TOKEN
    assert evidence["non_public_boundary"]["network_endpoint_enabled"] is False
    assert evidence["non_public_boundary"]["public_fetch_serving_enabled"] is False
    assert evidence["counts_by_tier"] == {TIER_A: 1, TIER_B: 1, TIER_C: 1}


def test_bootstrap_snapshot_builder_exports_canonical_json() -> None:
    snapshot = _snapshot()
    payload = export_bootstrap_snapshot_json(snapshot)

    assert snapshot["snapshot_manifest"]["token"] == BOOTSTRAP_SNAPSHOT_EVIDENCE_TOKEN
    assert snapshot["snapshot_manifest"]["public_fetch_serving_enabled"] is False
    assert snapshot["snapshot_manifest"]["network_endpoint_enabled"] is False
    assert payload == json.dumps(snapshot, allow_nan=False, separators=(",", ":"), sort_keys=True)
    assert verify_bootstrap_snapshot_json(payload, expected_genesis_domain_hash=GENESIS_HASH)


def test_bootstrap_snapshot_verifier_recomputes_artifact_hashes() -> None:
    snapshot = _snapshot()
    first_artifact = snapshot["artifact_list"][0]
    assert first_artifact["artifact_hash"] == compute_artifact_hash(first_artifact["artifact_payload"])

    tampered = json.loads(export_bootstrap_snapshot_json(snapshot))
    tampered["artifact_list"][0]["artifact_payload"]["root"] = "d" * 64

    with pytest.raises(ValueError, match="artifact_hash_mismatch"):
        verify_bootstrap_snapshot(tampered, expected_genesis_domain_hash=GENESIS_HASH)


def test_bootstrap_snapshot_rejects_malformed_hashes() -> None:
    with pytest.raises(ValueError, match="genesis_domain_hash_invalid"):
        build_bootstrap_snapshot(
            [_artifact("bad", "genesis_root", {"kind": "bad"})],
            authority_refs=[AUTHORITY_REF],
            epoch_checkpoint_range={"start_epoch": 1, "end_epoch": 1},
            genesis_domain_hash="ABC",
            snapshot_epoch=1,
        )


def test_bootstrap_snapshot_rejects_wrong_genesis_hash() -> None:
    with pytest.raises(ValueError, match="bootstrap_snapshot_genesis_hash_mismatch"):
        verify_bootstrap_snapshot(_snapshot(), expected_genesis_domain_hash="d" * 64)


def test_bootstrap_snapshot_requires_authority_refs() -> None:
    with pytest.raises(ValueError, match="authority_refs_required"):
        build_bootstrap_snapshot(
            [_artifact("no-authority", "genesis_root", {"kind": "genesis"})],
            authority_refs=[],
            epoch_checkpoint_range={"start_epoch": 1, "end_epoch": 1},
            genesis_domain_hash=GENESIS_HASH,
            snapshot_epoch=1,
        )


def test_bootstrap_snapshot_rejects_stale_epoch_range() -> None:
    with pytest.raises(ValueError, match="bootstrap_snapshot_epoch_range_stale"):
        build_bootstrap_snapshot(
            [_artifact("stale", "genesis_root", {"kind": "genesis"})],
            authority_refs=[AUTHORITY_REF],
            epoch_checkpoint_range={"start_epoch": 1, "end_epoch": 4},
            genesis_domain_hash=GENESIS_HASH,
            snapshot_epoch=5,
        )


def test_bootstrap_snapshot_rejects_non_canonical_json() -> None:
    snapshot = _snapshot()
    non_canonical = json.dumps(snapshot, indent=2, sort_keys=True)

    with pytest.raises(ValueError, match="bootstrap_snapshot_json_not_canonical"):
        verify_bootstrap_snapshot_json(
            non_canonical,
            expected_genesis_domain_hash=GENESIS_HASH,
        )


def test_bootstrap_snapshot_rejects_float_payload_values() -> None:
    with pytest.raises(ValueError, match="float_values_forbidden"):
        build_bootstrap_snapshot(
            [
                _artifact(
                    "float",
                    "genesis_root",
                    {"bad_float": 1.25},
                )
            ],
            authority_refs=[AUTHORITY_REF],
            epoch_checkpoint_range={"start_epoch": 1, "end_epoch": 1},
            genesis_domain_hash=GENESIS_HASH,
            snapshot_epoch=1,
        )


def test_module_does_not_define_public_server_or_socket_surface() -> None:
    import ilc_core.network.d2d.cdl087_serving_peer_evidence as module

    source = module.__dict__
    assert "ThreadingHTTPServer" not in source
    assert "HTTPServer" not in source
    assert "socket" not in source
