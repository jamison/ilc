from __future__ import annotations

import json
from pathlib import Path

import pytest

from ilc_core.consensus import submit_ingress_endpoint_assertion as endpoint
from ilc_core.consensus.submit_ingress_endpoint_assertion import (
    PUBLIC_SUBMIT_INGRESS_ENDPOINT_ASSERTION_NODE_KIND,
    PUBLIC_SUBMIT_INGRESS_ENDPOINT_ASSERTION_SCHEMA_VERSION,
    PublicSubmitIngressEndpointAssertion,
    load_from_atlas,
    verify_endpoint_assertion_bls_signature,
)
from ilc_core.epistemic import truth_primitive_submission_runtime as truth_runtime
from ilc_core.epistemic.node_submission_runtime import EpistemicSubmissionError
from ilc_core.epoch.genesis_settlement_destination import (
    GENESIS_AGENT1_AGENT_ID,
    GENESIS_CAPSULE_SIGNING_PK_HEX,
    GENESIS_PUBLIC_SUBMIT_INGRESS_BLS_PK_HEX,
)
from ilc_core.identity.bls_backend import verify_endpoint_assertion_bytes
from ilc_core.storage.lmdb_public_runtime import LmdbGraphStore


NETWORK_ID = "ilc-public-rc-01-testnet-harness"
OUT_DIR = Path("out/gap_public_rc_native_submit_ingress_guard_clear_00")
ATLAS_PATH = OUT_DIR / "atlas.lmdb"
ASSERTION_PATH = OUT_DIR / "endpoint_assertion.json"
TRANSPORT_KEYPAIR_PATH = OUT_DIR / "transport_keypair.json"


def _valid_unsigned_submission() -> dict[str, object]:
    return {
        "v": 1,
        "primitive": "assert.truth",
        "agent_id": GENESIS_PUBLIC_SUBMIT_INGRESS_BLS_PK_HEX,
        "epoch": 0,
        "payload": {
            "content": {"claim": "guard-clear unsigned placeholder rejection"},
            "primitive_type": "observation",
            "epistemic_type": "objective",
            "parent_node_ids": [],
        },
        "sig": "UNSIGNED",
    }


def _assertion_record() -> dict[str, object]:
    return json.loads(ASSERTION_PATH.read_text(encoding="utf-8"))


def test_all_native_submit_ingress_guards_are_cleared() -> None:
    assert truth_runtime.NATIVE_SUBMISSION_SIG_VERIFICATION_NOT_ACTIVATED is False
    assert endpoint.PUBLIC_RC_NATIVE_SUBMIT_INGRESS_CDL_NOT_RATIFIED is False
    assert endpoint.PUBLIC_SUBMIT_INGRESS_ENDPOINT_ASSERTION_NOT_ACTIVATED is False


def test_unsigned_native_submit_is_rejected_after_guard_clear() -> None:
    with pytest.raises(EpistemicSubmissionError) as exc_info:
        truth_runtime.validate_truth_primitive_submission(_valid_unsigned_submission())

    assert exc_info.value.token == "native_submit_sig_unsigned_placeholder_rejected"


def test_endpoint_assertion_artifact_schema_and_key_binding() -> None:
    record = _assertion_record()
    assertion = PublicSubmitIngressEndpointAssertion.from_dict(record)

    assert assertion.node_kind == PUBLIC_SUBMIT_INGRESS_ENDPOINT_ASSERTION_NODE_KIND
    assert assertion.schema_version == PUBLIC_SUBMIT_INGRESS_ENDPOINT_ASSERTION_SCHEMA_VERSION
    assert assertion.network_id == NETWORK_ID
    assert assertion.serving_agent_id == GENESIS_AGENT1_AGENT_ID
    assert assertion.transport_public_key_hex == GENESIS_PUBLIC_SUBMIT_INGRESS_BLS_PK_HEX
    assert assertion.bls_public_key_hex == GENESIS_PUBLIC_SUBMIT_INGRESS_BLS_PK_HEX
    assert assertion.transport_public_key_hex == assertion.bls_public_key_hex
    assert assertion.transport_key_scope == "public_submit_ingress"
    assert assertion.valid_until_epoch == 0


def test_endpoint_assertion_artifact_bls_verifies() -> None:
    assertion = PublicSubmitIngressEndpointAssertion.from_dict(_assertion_record())

    assert (
        verify_endpoint_assertion_bls_signature(
            assertion,
            verifier=lambda payload, sig, pk, nid: verify_endpoint_assertion_bytes(
                pk,
                payload,
                sig,
                nid,
            ),
        )
        is True
    )


def test_endpoint_assertion_loads_from_phase_local_lmdb() -> None:
    store = LmdbGraphStore(ATLAS_PATH)
    try:
        loaded = load_from_atlas(
            store,
            serving_agent_id=GENESIS_AGENT1_AGENT_ID,
            network_id=NETWORK_ID,
        )
    finally:
        store.close()

    assert loaded.to_dict() == PublicSubmitIngressEndpointAssertion.from_dict(
        _assertion_record()
    ).to_dict()


def test_public_submit_ingress_key_is_distinct_from_reserved_keys() -> None:
    assert GENESIS_PUBLIC_SUBMIT_INGRESS_BLS_PK_HEX != GENESIS_AGENT1_AGENT_ID
    assert GENESIS_PUBLIC_SUBMIT_INGRESS_BLS_PK_HEX != GENESIS_CAPSULE_SIGNING_PK_HEX

    invite_payload = json.loads(
        Path(
            "docs/specs/ilc_genesis_invite_issuer_delegation_record_GAP_GENESIS_INVITE_ISSUER_00_v0.1.json"
        ).read_text(encoding="utf-8")
    )
    validator_payload = json.loads(
        Path("config/public_rc_validators/genesis.json").read_text(encoding="utf-8")
    )
    assert GENESIS_PUBLIC_SUBMIT_INGRESS_BLS_PK_HEX != invite_payload["invite_issuer_pk_hex"]
    assert all(
        GENESIS_PUBLIC_SUBMIT_INGRESS_BLS_PK_HEX != row["agent_id"]
        for row in validator_payload["validators"]
    )


def test_transport_keypair_artifact_contains_no_secret_material() -> None:
    payload = json.loads(TRANSPORT_KEYPAIR_PATH.read_text(encoding="utf-8"))

    assert payload["transport_public_key_hex"] == GENESIS_PUBLIC_SUBMIT_INGRESS_BLS_PK_HEX
    assert payload["secret_key_material_committed"] is False
    serialized = json.dumps(payload, sort_keys=True)
    assert "secret_key_hex" not in serialized
    assert "private_key" not in serialized
