import json
from pathlib import Path

from ilc_core.protocol.ilc_cluster_a_acceptance_evidence import build_cluster_a_acceptance_evidence
from ilc_core.protocol.ilc_cluster_a_replay_proof_package import (
    build_cluster_a_replay_proof_package,
    _canonical_package_digest
)

FIXTURE_DIR = Path("tests/fixtures/cluster_a_replay_proof_v0_1")


def write_json(name, data):
    path = FIXTURE_DIR / name
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    path.write_text(payload + "\n", encoding="utf-8")
    print(f"Wrote {path} (canonical JSON)")

def main():
    # 1. Prepare Mock Inputs
    mock_record = {
        "gov_record_id": "rec-001-golden",
        "ver": "1.0",
        "op": "set_policy",
        "payload": {"foo": "bar"},
        "signatures": [{"sig": "dummy"}],  # Will be stripped in package
    }
    
    mock_apply_result = {
        "ok": True,
        "warnings": [],
        "errors": [],
        "data": {
            "policy_state_delta": {"foo": "bar_new"}
        }
    }
    
    mock_conformance_result = {
        "ok": True,
        "warnings": [],
        "errors": [],
        "constitution_checks": {
            "checks": [
                {"check_id": "CONST-001", "status": "pass"},
                {"check_id": "CONST-002", "status": "pass"}
            ]
        }
    }

    mock_context = {
        "timestamp": "2025-01-01T12:00:00.000000Z"
    }

    # 2. Build Valid Evidence
    evidence_valid = build_cluster_a_acceptance_evidence(
        governance_record=mock_record,
        apply_result=mock_apply_result,
        conformance_result=mock_conformance_result,
        runtime_context=mock_context
    )
    write_json("evidence_valid.json", evidence_valid)

    # 3. Build Valid Package
    package_valid = build_cluster_a_replay_proof_package(
        evidence=evidence_valid,
        governance_record=mock_record,
        apply_result=mock_apply_result,
        conformance_result=mock_conformance_result
    )
    write_json("package_valid.json", package_valid)

    # 4. Save Valid Contract
    contract_valid = package_valid["replay_contract"]
    write_json("contract_valid.json", contract_valid)

    # 5. Tampered Package: Hash Mismatch
    # Valid structure, but package_hash doesn't match content
    pkg_tampered_hash = package_valid.copy()
    pkg_tampered_hash["package_hash_sha256"] = "deadbeef" * 8
    write_json("package_tampered_hash.json", pkg_tampered_hash)

    # 6. Tampered Package: Record Hash Mismatch
    # We modify the record in the contract.
    # CRITICAL: We MUST update the package hash so that the outer check passes,
    # enabling the inner check (check_record_hash_match) to run and fail.
    pkg_tampered_record = json.loads(json.dumps(package_valid))
    pkg_tampered_record["replay_contract"]["governance_record"]["payload"]["foo"] = "tampered"
    # Recompute package hash
    pkg_tampered_record["package_hash_sha256"] = _canonical_package_digest(pkg_tampered_record)
    write_json("package_tampered_record_hash.json", pkg_tampered_record)

    # 7. Tampered Package: Evidence Contract Hash Mismatch
    # Modify evidence content.
    # CRITICAL: Update package hash.
    pkg_tampered_contract_digest = json.loads(json.dumps(package_valid))
    pkg_tampered_contract_digest["evidence"]["conformance_ok"] = False
    # Recompute package hash
    pkg_tampered_contract_digest["package_hash_sha256"] = _canonical_package_digest(pkg_tampered_contract_digest)
    write_json("package_tampered_contract_hash.json", pkg_tampered_contract_digest)

if __name__ == "__main__":
    main()
