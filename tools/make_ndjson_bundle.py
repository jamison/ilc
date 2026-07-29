#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""
NDJSON Bundle Demo Tool.

Phase 66C: Creates a demo bundle, writes it, reads it back, and verifies each record.

Usage:
    python3 tools/make_ndjson_bundle.py
"""

import os
import sys

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path

from cryptography.hazmat.primitives.asymmetric import ed25519

from ilc_core.encoding.dag_cbor import encode_dag_cbor
from ilc_core.encoding.cidv1 import node_id_from_obj
from ilc_core.crypto.cose_sign1 import cose_sign1_sign
from ilc_core.protocol.ndjson_bundle import (
    make_bundle_header,
    make_bundle_record,
    write_bundle,
    iter_bundle,
)
from ilc_core.protocol.bundle_verify import verify_bundle_record


def main():
    """Generate demo bundle, write, read, verify."""
    
    # Fixed key for reproducibility
    private_key_bytes = bytes.fromhex(
        "9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60"
    )
    private_key = ed25519.Ed25519PrivateKey.from_private_bytes(private_key_bytes)
    public_key = private_key.public_key()
    
    # Demo payloads
    payloads = [
        {"schema": "ilc.demo@v1", "message": "Hello from Phase 66C", "seq": 1},
        {"schema": "ilc.demo@v1", "message": "NDJSON bundle transport", "seq": 2},
        {"schema": "ilc.demo@v1", "message": "Streaming COSE artifacts", "seq": 3},
        {"schema": "ilc.demo@v1", "data": {"nested": True, "values": [1, 2, 3]}},
        {"schema": "ilc.demo@v1", "final": True, "count": 5},
    ]
    
    # Create signed records
    print("=== Phase 66C Demo: NDJSON Bundle ===\n")
    print(f"Creating {len(payloads)} signed records...")
    
    records = []
    for i, payload in enumerate(payloads, 1):
        payload_bytes = encode_dag_cbor(payload)
        node_id = node_id_from_obj(payload)
        cose_bytes = cose_sign1_sign(payload_bytes, private_key)
        record = make_bundle_record(seq=i, node_id=node_id, cose_bytes=cose_bytes)
        records.append(record)
        print(f"  Record {i}: {node_id[:20]}...")
    
    # Output path
    out_dir = Path("out/phase_66c_demo")
    out_dir.mkdir(parents=True, exist_ok=True)
    bundle_path = out_dir / "bundle.ndjson"
    
    # Write bundle
    print(f"\nWriting bundle to: {bundle_path}")
    header = make_bundle_header(
        ilc_phase="66C",
        notes="Demo bundle from make_ndjson_bundle.py",
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
                # Verify record
                verified = verify_bundle_record(obj, public_key=public_key)
                verified_count += 1
                print(f"  Record {verified['seq']}: VERIFIED (payload keys: {list(verified['payload_obj'].keys())})")
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
    print("Demo complete!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
