# SPDX-License-Identifier: AGPL-3.0-only
"""
ILC Constitution Cluster A - Replay Proof Package Logic.
Phase 143.

Provides logic to build and verify canonical replay proof packages.
"""

import json
import hashlib
import logging
from typing import Dict, List, Optional, TypedDict, TypeAlias

from ilc_core.exceptions import ReplayProofPackageError
from ilc_core.protocol.ilc_cluster_a_ingest import canonical_governance_record_digest
from ilc_core.protocol.ilc_cluster_a_acceptance_evidence import (
    validate_evidence_schema,
    canonical_evidence_contract_digest,
)
from ilc_core.protocol.ilc_cluster_a_replay_attestation import attest_cluster_a_replay

logger = logging.getLogger(__name__)

# --- Failure Tokens ---
E_SCHEMA_INVALID_PACKAGE = "schema_violation:invalid_replay_proof_package_shape"
E_MISSING_FIELD_PACKAGE = "schema_violation:missing_replay_proof_required_field"
E_HASH_MISMATCH_PACKAGE = "context_violation:replay_proof_package_hash_mismatch"
E_RECORD_HASH_MISMATCH = "context_violation:replay_proof_record_hash_mismatch"
E_CONTRACT_HASH_MISMATCH = "context_violation:replay_proof_evidence_contract_hash_mismatch"
E_ATTESTATION_FAILED = "context_violation:replay_proof_attestation_failed"

ReplayObject: TypeAlias = Dict[str, object]
ReplayCheckMap: TypeAlias = Dict[str, object]
ReplayCheckList: TypeAlias = List[ReplayCheckMap]


class ReplayVerifyResult(TypedDict):
    ok: bool
    errors: List[str]
    warnings: List[str]
    checks: ReplayCheckList


def _canonical_package_digest(package: ReplayObject) -> str:
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
    evidence: ReplayObject,
    governance_record: ReplayObject,
    apply_result: ReplayObject,
    conformance_result: ReplayObject
) -> ReplayObject:
    """
    Build a deterministic replay proof package.
    """
    # 0. Validate Inputs exist/schema? We trust inputs here mostly but should ensure stability.
    if not isinstance(evidence, dict):
        raise ReplayProofPackageError("schema_violation:invalid_evidence_input")

    # 1. Compute Hashes
    record_hash = evidence.get("record_hash_sha256")
    if not record_hash:
        # Recompute? Or require it present?
        # Evidence schema requires it.
        raise ReplayProofPackageError("schema_violation:evidence_missing_record_hash_sha256")
    # Validate evidence roughly
    if validate_evidence_schema(evidence):
        raise ReplayProofPackageError("schema_violation:invalid_evidence_input")
        
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


def _failure_result(check_name: str, error_code: str) -> ReplayVerifyResult:
    return {
        "ok": False,
        "errors": [error_code],
        "warnings": [],
        "checks": [{"check": check_name, "status": "fail", "error_code": error_code}],
    }


def _add_check(
    checks: ReplayCheckList,
    errors: List[str],
    name: str,
    ok: bool,
    err: Optional[str] = None,
) -> None:
    checks.append({"check": name, "status": "pass" if ok else "fail", "error_code": err if not ok else None})
    if not ok and err:
        errors.append(err)


def _validate_package_shape(
    package: object,
) -> tuple[Optional[ReplayVerifyResult], Optional[ReplayObject], Optional[ReplayObject], Optional[ReplayObject]]:
    if not isinstance(package, dict):
        return _failure_result("check_package_root_type", E_SCHEMA_INVALID_PACKAGE), None, None, None

    typed_package: ReplayObject = package
    allowed_pkg_keys = {
        "package_version",
        "record_hash_sha256",
        "evidence_contract_hash_sha256",
        "package_hash_sha256",
        "evidence",
        "replay_contract",
    }
    if set(typed_package.keys()) - allowed_pkg_keys:
        return _failure_result("check_package_unknown_fields", E_SCHEMA_INVALID_PACKAGE), None, None, None

    if typed_package.get("package_version") != "v0.1":
        return _failure_result("check_package_version", E_SCHEMA_INVALID_PACKAGE), None, None, None

    required_pkg_keys = {
        "package_version",
        "record_hash_sha256",
        "evidence_contract_hash_sha256",
        "package_hash_sha256",
        "evidence",
        "replay_contract",
    }
    if any(field not in typed_package for field in required_pkg_keys):
        return _failure_result("check_package_schema_fields", E_MISSING_FIELD_PACKAGE), None, None, None

    replay_contract_obj = typed_package["replay_contract"]
    if not isinstance(replay_contract_obj, dict):
        return _failure_result("check_replay_contract_type", E_SCHEMA_INVALID_PACKAGE), None, None, None
    replay_contract: ReplayObject = replay_contract_obj

    allowed_contract_keys = {"governance_record", "apply_result", "conformance_result"}
    if set(replay_contract.keys()) - allowed_contract_keys:
        return _failure_result("check_replay_contract_unknown_fields", E_SCHEMA_INVALID_PACKAGE), None, None, None

    if any(field not in replay_contract for field in allowed_contract_keys):
        return _failure_result("check_replay_contract_fields", E_MISSING_FIELD_PACKAGE), None, None, None

    evidence_obj = typed_package["evidence"]
    if not isinstance(evidence_obj, dict):
        return _failure_result("check_evidence_type", E_SCHEMA_INVALID_PACKAGE), None, None, None
    evidence: ReplayObject = evidence_obj

    return None, typed_package, replay_contract, evidence


def _verify_package_hash(
    package: ReplayObject,
    errors: List[str],
    checks: ReplayCheckList,
) -> bool:
    claimed_pkg_hash = package["package_hash_sha256"]
    computed_pkg_hash = _canonical_package_digest(package)
    is_match = claimed_pkg_hash == computed_pkg_hash
    _add_check(checks, errors, "check_package_hash_match", is_match, E_HASH_MISMATCH_PACKAGE)
    return is_match


def _verify_contract_hash(
    package: ReplayObject,
    evidence: ReplayObject,
    errors: List[str],
    checks: ReplayCheckList,
) -> None:
    claimed_contract_hash = package["evidence_contract_hash_sha256"]
    computed_contract_hash = canonical_evidence_contract_digest(evidence)
    _add_check(
        checks,
        errors,
        "check_evidence_contract_hash_match",
        claimed_contract_hash == computed_contract_hash,
        E_CONTRACT_HASH_MISMATCH,
    )


def _verify_record_hash(
    package: ReplayObject,
    replay_contract: ReplayObject,
    errors: List[str],
    checks: ReplayCheckList,
) -> None:
    gov_rec_obj = replay_contract["governance_record"]
    if not isinstance(gov_rec_obj, dict):
        raise ReplayProofPackageError("schema_violation:governance_record_not_object")

    computed_rec_hash = canonical_governance_record_digest(gov_rec_obj)
    claimed_rec_hash = package["record_hash_sha256"]
    _add_check(
        checks,
        errors,
        "check_record_hash_match",
        computed_rec_hash == claimed_rec_hash,
        E_RECORD_HASH_MISMATCH,
    )


def _verify_replay_attestation(
    evidence: ReplayObject,
    replay_contract: ReplayObject,
    errors: List[str],
    checks: ReplayCheckList,
) -> None:
    gov_rec_obj = replay_contract["governance_record"]
    if not isinstance(gov_rec_obj, dict):
        raise ReplayProofPackageError("schema_violation:governance_record_not_object")

    attest_res = attest_cluster_a_replay(
        evidence=evidence,
        governance_record=gov_rec_obj,
        apply_result=replay_contract["apply_result"],
        conformance_result=replay_contract["conformance_result"],
    )
    if not attest_res["ok"]:
        _add_check(checks, errors, "check_replay_attest", False, E_ATTESTATION_FAILED)
        errors.extend(attest_res["errors"])
    else:
        _add_check(checks, errors, "check_replay_attest", True)
    checks.extend(attest_res["checks"])


def verify_cluster_a_replay_proof_package(package: object) -> ReplayVerifyResult:
    """
    Verify a replay proof package.
    Returns result dict with ok/errors.
    Safe against malformed input.
    """
    errors: List[str] = []
    checks: ReplayCheckList = []

    schema_failure, typed_package, replay_contract, evidence = _validate_package_shape(package)
    if schema_failure is not None:
        return schema_failure
    if typed_package is None or replay_contract is None or evidence is None:
        return _failure_result("check_package_processing", E_SCHEMA_INVALID_PACKAGE)

    _add_check(checks, errors, "check_package_schema_structure", True)

    try:
        if not _verify_package_hash(typed_package, errors, checks):
            return {"ok": False, "errors": errors, "warnings": [], "checks": checks}

        _verify_contract_hash(typed_package, evidence, errors, checks)
        _verify_record_hash(typed_package, replay_contract, errors, checks)
        _verify_replay_attestation(evidence, replay_contract, errors, checks)
    except Exception as exc:
        logger.debug("package_verify_processing_exception: %s", exc, exc_info=True)
        return {
            "ok": False,
            "errors": [E_SCHEMA_INVALID_PACKAGE],
            "warnings": [],
            "checks": checks + [{"check": "check_package_processing", "status": "fail", "error_code": E_SCHEMA_INVALID_PACKAGE}],
        }

    return {
        "ok": len(errors) == 0,
        "errors": sorted(list(set(errors))),
        "warnings": [],
        "checks": checks,
    }
