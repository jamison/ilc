#!/usr/bin/env python3
"""
Route Index NDJSON Bundle Tool.

Phase 66C: Creates route_index bundles, writes to NDJSON, verifies each record.

Usage:
    python3 tools/make_route_index_bundle.py
"""

import os
import sys

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path

from cryptography.hazmat.primitives.asymmetric import ed25519

from ilc_core.star_map.route_index import (
    build_route_index_payload,
    build_route_index_cose_sign1,
    node_id_from_payload,
)
from ilc_core.protocol.ndjson_bundle import (
    make_bundle_header,
    make_bundle_record,
    write_bundle,
    iter_bundle,
)
from ilc_core.protocol.bundle_verify import verify_bundle_record


def main():
    """Generate route_index bundle, write, read, verify."""
    
    # Fixed key for reproducibility (same as make_ndjson_bundle.py)
    private_key_bytes = bytes.fromhex(
        "9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60"
    )
    private_key = ed25519.Ed25519PrivateKey.from_private_bytes(private_key_bytes)
    public_key = private_key.public_key()
    
    print("=== Phase 66C: Route Index NDJSON Bundle ===\n")
    
    # Create route_index payloads with realistic data
    payloads = [
        build_route_index_payload(
            routes=[
                {
                    "n": 2,
                    "head": 0,
                    "k": "HJa6H7nn6qk",
                    "targets": [
                        {"route": "shard-001", "w": 5},
                        {"route": "shard-002", "w": 3},
                    ],
                },
                {
                    "n": 2,
                    "head": 0,
                    "k": "sMfke74adZo",
                    "targets": [
                        {"route": "shard-001", "w": 2},
                    ],
                },
            ],
            ngram_orders=[2],
            heads=1,
            producer="phase-66c-demo",
            epoch="2026-W05",
        ),
        build_route_index_payload(
            routes=[
                {
                    "n": 2,
                    "head": 0,
                    "k": "dD6R9C-F-20",
                    "targets": [
                        {"route": "shard-003", "w": 10},
                    ],
                },
                {
                    "n": 3,
                    "head": 0,
                    "k": "abc123XYZ",
                    "targets": [
                        {"route": "shard-002", "w": 7},
                        {"route": "shard-003", "w": 4},
                    ],
                },
            ],
            ngram_orders=[2, 3],
            heads=1,
            producer="phase-66c-demo",
        ),
        build_route_index_payload(
            routes=[
                {
                    "n": 2,
                    "head": 0,
                    "k": "b5dh6DvrBoU",
                    "targets": [
                        {"route": "shard-001", "w": 1},
                    ],
                },
            ],
            ngram_orders=[2],
            heads=1,
            chunk_id=0,
            chunk_total=1,
        ),
    ]
    
    print(f"Creating {len(payloads)} route_index records...")
    
    # Create signed records
    records = []
    for i, payload in enumerate(payloads, 1):
        node_id = node_id_from_payload(payload)
        cose_bytes = build_route_index_cose_sign1(payload, private_key)
        record = make_bundle_record(seq=i, node_id=node_id, cose_bytes=cose_bytes)
        records.append(record)
        route_count = len(payload["routes"])
        print(f"  Record {i}: {node_id[:20]}... ({route_count} routes)")
    
    # Output path
    out_dir = Path("out/phase_66c_route_index_bundle")
    out_dir.mkdir(parents=True, exist_ok=True)
    bundle_path = out_dir / "bundle.ndjson"
    
    # Write bundle
    print(f"\nWriting bundle to: {bundle_path}")
    header = make_bundle_header(
        ilc_phase="66C",
        notes="Route index bundle from make_route_index_bundle.py",
    )
    
    with open(bundle_path, "w", encoding="utf-8") as f:
        result = write_bundle(f, header=header, records=records, include_footer=True)
    
    print(f"  Wrote {result['record_count']} records")
    print(f"  Footer digest: {result['sha256_b64u'][:20]}...")
    
    # Read and verify
    print("\nReading and verifying bundle...")
    verified_count = 0
    footer_info = None
    
    with open(bundle_path, "r", encoding="utf-8") as f:
        for event_type, obj in iter_bundle(f, validate_footer=True):
            if event_type == "header":
                print(f"  Header: bundle_id={obj['bundle_id'][:8]}...")
            elif event_type == "record":
                verified = verify_bundle_record(obj, public_key=public_key)
                verified_count += 1
                schema = verified["payload_obj"]["schema"]
                routes = len(verified["payload_obj"]["routes"])
                print(f"  Record {verified['seq']}: VERIFIED (schema={schema}, routes={routes})")
            elif event_type == "footer":
                footer_info = obj
    
    # Summary
    print("\n=== Summary ===")
    print(f"Records verified: {verified_count}")
    if footer_info:
        print(f"Footer record_count: {footer_info['record_count']}")
        print(f"Footer digest valid: YES")
    else:
        print("Footer: NOT PRESENT")
    
    print(f"\nBundle file: {bundle_path.absolute()}")
    print("Route index bundle complete!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
