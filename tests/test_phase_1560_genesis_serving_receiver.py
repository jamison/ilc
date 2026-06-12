"""Phase 1560 receiver-remediation tests.

PUBLIC_RC_EXCLUDE: phase_1560_private_receiver_selftest
PUBLIC_RC_EXCLUDE_REASON: Private pre-RC receiver helper tests. No live Tailscale call or Agent INIT ceremony.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ilc_core.bundle.layer0_protocol_bundle import generate_layer0_protocol_bundle
from ilc_core.bundle.layer1_genesis_bundle import generate_layer1_genesis_bundle
from ilc_core.genesis.serving_receipt import (
    SERVING_RECEIPT_SCHEMA_VERSION,
    build_serving_receipt,
)
from tools.genesis_serving_receiver import (
    GenesisReceiverError,
    status_payload,
    validate_serve_payload,
    validate_verify_payload,
)


def _layer0_fixture():
    return generate_layer0_protocol_bundle(
        bundle_id="phase1560-receiver-layer0",
        version="v0.1-private",
        schemas=[{"type_name": "Node", "required": ["node_id"]}],
        parameters={"truth_primitives": 7},
        include_truth_primitive_schemas=True,
    )


def _layer1_fixture(layer0):
    return generate_layer1_genesis_bundle(
        bundle_id="phase1560-receiver-layer1",
        layer0_sha256=layer0.sha256,
        layer0_cidv1=layer0.cidv1,
        seed_claims=[{"claim_id": "seed-001", "truth_primitive": "assert.truth"}],
        initial_agent_roster=[{"agent_id": "agent-a"}],
        initial_shard_topology={"shards": [], "version": "v0.1-private"},
        genesis_signing_key_refs=[{"key_ref": "key-a"}],
    )


def _serve_payload():
    layer0 = _layer0_fixture()
    layer1 = _layer1_fixture(layer0)
    receipt = build_serving_receipt(
        "genesis_agent:01",
        "layer0+layer1",
        layer0_protocol_bundle_sha256=layer0.sha256,
        layer1_genesis_bundle_sha256=layer1.sha256,
        layer0_protocol_bundle_cidv1=layer0.cidv1,
        serving_epoch=0,
        served_peer_url="https://100.64.0.10:8443",
    )
    return {
        "layer0": {
            "canonical_json": layer0.canonical_json,
            "cidv1": layer0.cidv1,
            "sha256": layer0.sha256,
        },
        "layer1": {
            "canonical_json": layer1.canonical_json,
            "cidv1": layer1.cidv1,
            "sha256": layer1.sha256,
        },
        "receipt": receipt.to_dict(),
        "schema_version": SERVING_RECEIPT_SCHEMA_VERSION,
    }


def test_validate_serve_payload_persists_expected_state_shape() -> None:
    response = validate_serve_payload(_serve_payload())

    assert response["accepted"] is True
    assert response["schema_version"] == SERVING_RECEIPT_SCHEMA_VERSION
    assert isinstance(response["layer0_cidv1"], str)
    assert isinstance(response["layer0_sha256"], str)
    assert isinstance(response["receipt_id"], str)


def test_validate_serve_payload_rejects_receipt_layer0_mismatch() -> None:
    payload = _serve_payload()
    receipt = dict(payload["receipt"])  # type: ignore[arg-type]
    receipt["layer0_protocol_bundle_sha256"] = "0" * 64
    payload["receipt"] = receipt

    with pytest.raises(GenesisReceiverError, match="genesis_receiver_receipt_layer0_sha_mismatch"):
        validate_serve_payload(payload)


def test_validate_serve_payload_rejects_float() -> None:
    payload = _serve_payload()
    payload["float"] = 1.25

    with pytest.raises(GenesisReceiverError, match="genesis_receiver_float_not_allowed"):
        validate_serve_payload(payload)


def test_verify_payload_uses_atomic_state(tmp_path: Path) -> None:
    response = validate_serve_payload(_serve_payload())
    state_path = tmp_path / "state.json"
    state_path.write_text(json.dumps(response, sort_keys=True), encoding="utf-8")

    verified = validate_verify_payload(
        {
            "expected_layer0_cidv1": response["layer0_cidv1"],
            "schema_version": SERVING_RECEIPT_SCHEMA_VERSION,
        },
        state_path=state_path,
    )
    assert verified["verified"] is True
    assert verified["layer0_cidv1"] == response["layer0_cidv1"]


def test_status_payload_does_not_claim_public_activation(tmp_path: Path) -> None:
    status = status_payload(state_path=tmp_path / "missing.json")

    assert status["receiver_ready"] is True
    assert status["state_present"] is False
    assert status["public_p2p_activated"] is False
