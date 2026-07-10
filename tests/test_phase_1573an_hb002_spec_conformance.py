from __future__ import annotations

import hashlib
from pathlib import Path

from ilc_core.bundle.layer0_protocol_bundle import generate_layer0_protocol_bundle
from ilc_core.genesis.serving_receipt import (
    MAX_SERVING_RESPONSE_BYTES,
    SERVING_REQUEST_PATH,
)


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs/specs/ilc_hb002_bootstrap_gossip_protocol_spec_1573an_v0.1.md"


def test_spec_exists_and_is_public_rc_excluded() -> None:
    text = SPEC.read_text(encoding="utf-8")
    assert "PUBLIC_RC_EXCLUDE: hb002_bootstrap_gossip_spec" in text
    assert "Not yet for public distribution" in text


def test_request_and_response_schema_versions_are_pinned() -> None:
    text = SPEC.read_text(encoding="utf-8")
    assert "hb002_bootstrap_request_v1" in text
    assert "hb002_bootstrap_response_v1" in text


def test_serving_receipt_path_and_response_cap_are_unchanged() -> None:
    assert SERVING_REQUEST_PATH == "/ilc/genesis/serve"
    assert MAX_SERVING_RESPONSE_BYTES == 1_048_576


def test_layer0_bundle_cidv1_is_deterministic_for_same_inputs() -> None:
    kwargs = {
        "bundle_id": "fixture-layer0",
        "version": "fixture.v1",
        "schemas": [
            {
                "schema_kind": "fixture",
                "schema_version": "fixture.v1",
                "type_name": "fixture.type",
            }
        ],
        "parameters": {"network": "fixture"},
    }
    first = generate_layer0_protocol_bundle(**kwargs)
    second = generate_layer0_protocol_bundle(**kwargs)
    assert first.cidv1 == second.cidv1
    assert first.dag_cbor == second.dag_cbor


def test_layer0_bundle_sha256_matches_dag_cbor() -> None:
    bundle = generate_layer0_protocol_bundle(
        bundle_id="fixture-layer0",
        version="fixture.v1",
        schemas=[
            {
                "schema_kind": "fixture",
                "schema_version": "fixture.v1",
                "type_name": "fixture.type",
            }
        ],
        parameters={"network": "fixture"},
    )
    assert hashlib.sha256(bundle.dag_cbor).hexdigest() == bundle.sha256


def test_spec_does_not_authorize_public_distribution() -> None:
    text = SPEC.read_text(encoding="utf-8")
    required_phrases = [
        "does not grant public distribution authority",
        "does not implement HB-002 full runtime",
        "public RC",
    ]
    for phrase in required_phrases:
        assert phrase in text

