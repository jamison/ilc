"""
ILC Constitution Cluster A - Replay Proof Package Logic.
Phase 143.

Provides logic to build and verify canonical replay proof packages.
"""

import json
import hashlib
from typing import Any, Dict, List, Optional

from ilc_core.protocol.ilc_cluster_a_ingest import canonical_governance_record_digest
from ilc_core.protocol.ilc_cluster_a_acceptance_evidence import (
    validate_evidence_schema,
    canonical_evidence_contract_digest,
)
from ilc_core.protocol.ilc_cluster_a_replay_attestation import attest_cluster_a_replay

# --- Failure Tokens ---
E_SCHEMA_INVALID_PACKAGE = "schema_violation:invalid_replay_proof_package_shape"
E_MISSING_FIELD_PACKAGE = "schema_violation:missing_replay_proof_required_field"
E_HASH_MISMATCH_PACKAGE = "context_violation:replay_proof_package_hash_mismatch"
E_RECORD_HASH_MISMATCH = "context_violation:replay_proof_record_hash_mismatch"
E_CONTRACT_HASH_MISMATCH = "context_violation:replay_proof_evidence_contract_hash_mismatch"
E_ATTESTATION_FAILED = "context_violation:replay_proof_attestation_failed"

def _canonical_package_digest(package: Dict[str, Any]) -> str:
    """
    Compute canonical SHA-256 digest of the package.
    Excludes signature/hash fields if present? No, spec says:
    "Construct the package object with package_hash_sha256 set to empty string or excluded"
    Let's exclude it.
    """
    obj = {k: v for k, v in package.items() if k != "package_hash_sha256"}
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()

def build_cluster_a_replay_proof_package(
    *,
    evidence: Dict[str, Any],
    governance_record: Dict[str, Any],
    apply_result: Dict[str, Any],
    conformance_result: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Build a deterministic replay proof package.
    """
    # 0. Validate Inputs exist/schema? We trust inputs here mostly but should ensure stability.
    # Validate evidence roughly
    if validate_evidence_schema(evidence):
        raise ValueError("Invalid evidence provided to package builder")

    # 1. Compute Hashes
    record_hash = evidence.get("record_hash_sha256")
    if not record_hash:
        # Recompute? Or require it present?
        # Evidence schema requires it.
        raise ValueError("Evidence missing record_hash_sha256")
        
    contract_hash = canonical_evidence_contract_digest(evidence)
    
    # 2. Construct Package Stub
    # We minimize governance record (exclude signatures)
    min_record = {k: v for k, v in governance_record.items() if k != "signatures"}
    
    package = {
        "package_version": "v0.1",
        "record_hash_sha256": record_hash,
        "evidence_contract_hash_sha256": contract_hash,
        "evidence": evidence,
        "replay_contract": {
            "governance_record": min_record,
            "apply_result": apply_result,
            "conformance_result": conformance_result
        }
    }
    
    # 3. Compute Package Hash
    pkg_hash = _canonical_package_digest(package)
    package["package_hash_sha256"] = pkg_hash
    
    return package

def verify_cluster_a_replay_proof_package(package: Dict[str, Any]) -> Dict[str, Any]:
    """
    Verify a replay proof package.
    Returns result dict with ok/errors.
    Safe against malformed input.
    """
    errors: List[str] = []
    checks: List[Dict[str, Any]] = []
    
    def _add_check(name: str, ok: bool, err: Optional[str] = None):
        checks.append({"check": name, "status": "pass" if ok else "fail", "error_code": err})
        if not ok and err:
            errors.append(err)

    # 0. Fail-Safe Root Validation
    if not isinstance(package, dict):
        return {
            "ok": False,
            "errors": [E_SCHEMA_INVALID_PACKAGE],
            "warnings": [],
            "checks": [{"check": "check_package_root_type", "status": "fail", "error_code": E_SCHEMA_INVALID_PACKAGE}]
        }
        
    # 0.1 Check Version Strictness
    if package.get("package_version") != "v0.1":
        # New token for version mismatch? Or schema invalid?
        # Prompt suggested reusing tokens or defining explicitly.
        # Let's reuse schema invalid or specific if needed.
        # Let's use E_SCHEMA_INVALID_PACKAGE with a specific check context.
        return {
            "ok": False,
            "errors": [E_SCHEMA_INVALID_PACKAGE],
            "warnings": [],
            "checks": [{"check": "check_package_version", "status": "fail", "error_code": E_SCHEMA_INVALID_PACKAGE}]
        }

    # 1. Schema Validation (Required Fields)
    required = {
        "package_version", "record_hash_sha256", "evidence_contract_hash_sha256",
        "package_hash_sha256", "evidence", "replay_contract"
    }
    for f in required:
        if f not in package:
            # Fatal schema error
            return {
                "ok": False,
                "errors": [E_MISSING_FIELD_PACKAGE],
                "warnings": [],
                "checks": [{"check": "check_package_schema_fields", "status": "fail", "error_code": E_MISSING_FIELD_PACKAGE}]
            }
            
    # Check replay_contract fields
    replay_contract = package["replay_contract"]
    if not isinstance(replay_contract, dict):
        return {
            "ok": False, 
            "errors": [E_SCHEMA_INVALID_PACKAGE], 
            "warnings": [],
            "checks": [{"check": "check_replay_contract_type", "status": "fail", "error_code": E_SCHEMA_INVALID_PACKAGE}]
        }
        
    req_contract = {"governance_record", "apply_result", "conformance_result"}
    for f in req_contract:
        if f not in replay_contract:
             return {
                 "ok": False, 
                 "errors": [E_MISSING_FIELD_PACKAGE], 
                 "warnings": [],
                 "checks": [{"check": "check_replay_contract_fields", "status": "fail", "error_code": E_MISSING_FIELD_PACKAGE}]
             }

    # Check evidence structure (Light)
    evidence = package["evidence"]
    if not isinstance(evidence, dict):
         return {
            "ok": False, 
            "errors": [E_SCHEMA_INVALID_PACKAGE], 
            "warnings": [],
            "checks": [{"check": "check_evidence_type", "status": "fail", "error_code": E_SCHEMA_INVALID_PACKAGE}]
        }

    _add_check("check_package_schema_structure", True)

    try:
        # 2. Package Hash Verification
        claimed_pkg_hash = package["package_hash_sha256"]
        computed_pkg_hash = _canonical_package_digest(package)
        if claimed_pkg_hash != computed_pkg_hash:
            _add_check("check_package_hash_match", False, E_HASH_MISMATCH_PACKAGE)
            return {"ok": False, "errors": errors, "warnings": [], "checks": checks} # Fail fast on hash mismatch
        
        _add_check("check_package_hash_match", True)
        
        # 3. Evidence Contract Hash Verification
        claimed_contract_hash = package["evidence_contract_hash_sha256"]
        
        # Validate evidence strict schema before processing digest to prevent crashes?
        # attest_cluster_a_replay does validation too.
        # But canonical_evidence_contract_digest might fail if keys missing.
        # So we wrap in try/except or pre-validate.
        # Let's rely on try/except block around the whole logic as fail-safe.
        
        computed_contract_hash = canonical_evidence_contract_digest(evidence)
        
        if claimed_contract_hash != computed_contract_hash:
            _add_check("check_evidence_contract_hash_match", False, E_CONTRACT_HASH_MISMATCH)
        else:
            _add_check("check_evidence_contract_hash_match", True)
            
        # 4. Record Hash Verification
        # Recompute record hash from minimized record in contract
        gov_rec = replay_contract["governance_record"]
        if not isinstance(gov_rec, dict):
             # Should have been caught by schema check? No, we only checked keys exist.
             # Guard here.
             raise ValueError("governance_record must be dict")
             
        computed_rec_hash = canonical_governance_record_digest(gov_rec)
        claimed_rec_hash = package["record_hash_sha256"]
        
        if computed_rec_hash != claimed_rec_hash:
            _add_check("check_record_hash_match", False, E_RECORD_HASH_MISMATCH)
        else:
            _add_check("check_record_hash_match", True)
            
        # 5. Replay Attestation
        attest_res = attest_cluster_a_replay(
            evidence=evidence,
            governance_record=gov_rec,
            apply_result=replay_contract["apply_result"],
            conformance_result=replay_contract["conformance_result"]
        )
        
        if not attest_res["ok"]:
            # If attestation fails, we report generic failure + specific errors from attestation
            _add_check("check_replay_attest", False, E_ATTESTATION_FAILED)
            # Merge errors
            errors.extend(attest_res["errors"])
            # Merge checks
            for c in attest_res["checks"]:
                checks.append(c)
        else:
            _add_check("check_replay_attest", True)
            for c in attest_res["checks"]:
                checks.append(c)

    except Exception:
        # Catch-all for any digest/structural failure deep inside
        return {
            "ok": False,
            "errors": [E_SCHEMA_INVALID_PACKAGE],
            "warnings": [],
            "checks": checks + [{"check": "check_package_processing", "status": "fail", "error_code": E_SCHEMA_INVALID_PACKAGE}]
        }

    return {
        "ok": len(errors) == 0,
        "errors": sorted(list(set(errors))), # Dedupe just in case
        "warnings": [],
        "checks": checks
    }
