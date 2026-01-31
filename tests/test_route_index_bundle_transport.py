"""
Integration tests for Route Index NDJSON bundle transport.

Tests that route_index payloads can be:
1. COSE-signed
2. Bundled as NDJSON records
3. Verified by verify_bundle_record
"""

import sys
from pathlib import Path
from datetime import datetime, timezone

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cryptography.hazmat.primitives.asymmetric import ed25519

from ilc_core.star_map.route_index import (
    build_route_index_payload,
    build_route_index_cose_sign1,
    node_id_from_payload,
    SCHEMA_URI,
)
from ilc_core.protocol.ndjson_bundle import make_bundle_record
from ilc_core.protocol.bundle_verify import verify_bundle_record


# Fixed test key (deterministic)
TEST_PRIVATE_KEY_HEX = "9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60"


@pytest.fixture
def ed25519_keypair():
    """Provide fixed Ed25519 keypair for reproducibility."""
    private_key_bytes = bytes.fromhex(TEST_PRIVATE_KEY_HEX)
    private_key = ed25519.Ed25519PrivateKey.from_private_bytes(private_key_bytes)
    public_key = private_key.public_key()
    return private_key, public_key


class TestRouteIndexBundleTransport:
    """Test route_index payloads through NDJSON bundle transport."""

    def test_route_index_roundtrip_verification(self, ed25519_keypair) -> None:
        """Route index can be signed, bundled, and verified."""
        private_key, public_key = ed25519_keypair
        
        # Build payload
        payload = build_route_index_payload(
            routes=[
                {
                    "n": 2,
                    "head": 0,
                    "k": "testkey123",
                    "targets": [{"route": "shard-001", "w": 5}],
                }
            ],
            ngram_orders=[2],
            heads=1,
            created_at=datetime(2026, 1, 30, tzinfo=timezone.utc),
        )
        
        # Sign
        node_id = node_id_from_payload(payload)
        cose_bytes = build_route_index_cose_sign1(payload, private_key)
        
        # Bundle
        record = make_bundle_record(seq=1, node_id=node_id, cose_bytes=cose_bytes)
        
        # Verify
        verified = verify_bundle_record(record, public_key=public_key)
        
        assert verified["seq"] == 1
        assert verified["node_id"] == node_id
        assert verified["payload_obj"]["schema"] == SCHEMA_URI

    def test_verified_payload_matches_original(self, ed25519_keypair) -> None:
        """Decoded payload matches original payload dict."""
        private_key, public_key = ed25519_keypair
        
        routes = [
            {
                "n": 2,
                "head": 0,
                "k": "HJa6H7nn6qk",
                "targets": [
                    {"route": "shard-002", "w": 3},
                    {"route": "shard-001", "w": 5},
                ],
            }
        ]
        
        payload = build_route_index_payload(
            routes=routes,
            ngram_orders=[2],
            heads=1,
            created_at=datetime(2026, 1, 30, tzinfo=timezone.utc),
            producer="test-producer",
        )
        
        node_id = node_id_from_payload(payload)
        cose_bytes = build_route_index_cose_sign1(payload, private_key)
        record = make_bundle_record(seq=1, node_id=node_id, cose_bytes=cose_bytes)
        
        verified = verify_bundle_record(record, public_key=public_key)
        decoded = verified["payload_obj"]
        
        # Schema and key fields match
        assert decoded["schema"] == SCHEMA_URI
        assert decoded["canonicalizer"] == "ilc.text.canon@v1"
        assert decoded["bucket_key_len"] == 8
        assert decoded["heads"] == 1
        assert decoded["ngram_orders"] == [2]
        assert decoded["producer"] == "test-producer"
        
        # Routes match (targets sorted by route key)
        assert len(decoded["routes"]) == 1
        assert decoded["routes"][0]["k"] == "HJa6H7nn6qk"
        # Targets should be sorted by route
        target_routes = [t["route"] for t in decoded["routes"][0]["targets"]]
        assert target_routes == ["shard-001", "shard-002"]

    def test_node_id_recomputation_matches(self, ed25519_keypair) -> None:
        """NodeID from verified payload matches original computation."""
        private_key, public_key = ed25519_keypair
        
        payload = build_route_index_payload(
            routes=[
                {"n": 2, "head": 0, "k": "abc", "targets": []},
            ],
            ngram_orders=[2],
            heads=1,
            created_at=datetime(2026, 1, 30, tzinfo=timezone.utc),
        )
        
        original_node_id = node_id_from_payload(payload)
        cose_bytes = build_route_index_cose_sign1(payload, private_key)
        record = make_bundle_record(seq=1, node_id=original_node_id, cose_bytes=cose_bytes)
        
        verified = verify_bundle_record(record, public_key=public_key)
        
        # The verified node_id should match what we computed
        assert verified["node_id"] == original_node_id
        
        # Recomputing from the decoded payload should also match
        from ilc_core.encoding.cidv1 import node_id_from_obj
        recomputed = node_id_from_obj(verified["payload_obj"])
        assert recomputed == original_node_id

    def test_multiple_records_verification(self, ed25519_keypair) -> None:
        """Multiple route_index records all verify correctly."""
        private_key, public_key = ed25519_keypair
        
        payloads = [
            build_route_index_payload(
                routes=[{"n": 2, "head": 0, "k": "k1", "targets": []}],
                ngram_orders=[2],
                heads=1,
                created_at=datetime(2026, 1, 30, tzinfo=timezone.utc),
            ),
            build_route_index_payload(
                routes=[{"n": 3, "head": 0, "k": "k2", "targets": []}],
                ngram_orders=[3],
                heads=1,
                created_at=datetime(2026, 1, 30, 0, 0, 1, tzinfo=timezone.utc),
            ),
            build_route_index_payload(
                routes=[{"n": 2, "head": 1, "k": "k3", "targets": []}],
                ngram_orders=[2],
                heads=2,
                created_at=datetime(2026, 1, 30, 0, 0, 2, tzinfo=timezone.utc),
            ),
        ]
        
        for i, payload in enumerate(payloads, 1):
            node_id = node_id_from_payload(payload)
            cose_bytes = build_route_index_cose_sign1(payload, private_key)
            record = make_bundle_record(seq=i, node_id=node_id, cose_bytes=cose_bytes)
            
            verified = verify_bundle_record(record, public_key=public_key)
            assert verified["seq"] == i
            assert verified["payload_obj"]["schema"] == SCHEMA_URI
