# SPDX-License-Identifier: AGPL-3.0-or-later
"""
ILC Constitution Cluster A - Core Runtime Ingest.
Phase 135.

Provides deterministic ingest, dispatch, assembly, and application logic 
for Cluster A artifacts (Wire, Receipt, Transcript, Governance Record).
"""

import json
import hashlib
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# Import Phase 134 validators
from ilc_core.protocol.ilc_wire_validate import validate_wire_event
from ilc_core.protocol.ilc_receipt_validate import validate_receipt_record
from ilc_core.protocol.ilc_transcript_validate import validate_transcript
from ilc_core.protocol.ilc_governance_record_validate import validate_governance_record
from ilc_core.exceptions import GovernanceIngestValidationError

logger = logging.getLogger(__name__)

# --- Helpers ---

ALLOWED_CODES = {
    "context_violation:missing_signature_verification_context",
    "context_violation:unknown_signing_key",
    "context_violation:unsupported_sig_alg",
    "value_violation:invalid_public_key_bytes",
    "value_violation:invalid_signature_hex",
    "value_violation:invalid_signature_length",
    "context_violation:signature_verification_failed",
    "context_violation:no_valid_signatures",
    "context_violation:duplicate_signature_key_id",
    "value_violation:invalid_min_valid_signatures",
    "context_violation:gov_record_id_record_digest_conflict",
    "context_violation:known_records_legacy_hash_mode",
    "context_violation:signature_verification_unavailable",
    "context_violation:gov_record_id_hash_conflict",
    "context_violation:invalid_state_transition",
    "context_violation:known_records_hash_mode_required",
    "schema_violation:invalid_type:policy_state.root",
    "schema_violation:invalid_type:policy_state.proposals",
    "schema_violation:invalid_type:policy_state.known_records",
    "schema_violation:invalid_type:policy_state.known_records_hash_mode",
    # Inherited from validators (we don't strictly enforce these in allowed codes set for runtime yet, 
    # but for this module's logic we should be strict)
}

KNOWN_RECORDS_HASH_MODE_PAYLOAD = "payload_hash_v0"
KNOWN_RECORDS_HASH_MODE_DIGEST = "record_digest_v1"

def _result(
    ok: bool, 
    *, 
    artifact_kind: Optional[str] = None, 
    errors: List[str] = None, 
    warnings: List[str] = None, 
    version: Optional[str] = None, 
    data: Any = None,
    error_details: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Construct a deterministic result envelope.
    """
    return {
        "ok": ok,
        "artifact_kind": artifact_kind,
        "errors": sorted(errors or []),
        "warnings": sorted(warnings or []),
        "version": version,
        "data": data,
        "error_details": error_details, # Optional field, None if empty/missing can be omitted by serializer if desired, here just consistent
    }

def _emit(errors: List[str], details: List[Dict[str, Any]], code: str, **ctx) -> None:
    """
    Emit a runtime error with strict token enforcement.
    """
    if code not in ALLOWED_CODES:
        # Fail fast in tests, or could log warning in prod. 
        # For this phase, we treat adherence as mandatory.
        raise GovernanceIngestValidationError(f"unapproved_error_code:{code}")
        
    errors.append(code)
    if ctx:
        details.append({"code": code, **ctx})

def _infer_kind(obj: Dict[str, Any]) -> Optional[str]:
    """
    Infer artifact kind from discriminator fields.
    Deterministic checks in order: Governance -> Transcript -> Receipt -> Wire.
    """
    # Governance Record: "gov_record_id" + "signatures"
    if "gov_record_id" in obj and "signatures" in obj:
        return "governance_record"
    
    # Transcript: "transcript_id" + "records"
    if "transcript_id" in obj and "records" in obj:
        return "transcript"
    
    # Receipt: "receipt_id" + "outcome"
    if "receipt_id" in obj and "outcome" in obj:
        return "receipt"
    
    # Wire Event: "event_id" + "event_kind"
    if "event_id" in obj and "event_kind" in obj:
        return "wire"
        
    return None

def _get_sort_key(record: Dict[str, Any]) -> Tuple[str, str, str]:
    """
    Get deterministic sort key for a transcript record.
    Key: (timestamp, normalized_kind, normalized_id)
    """
    timestamp = record.get("timestamp", "")
    
    # Normalize kind
    # If wire, use event_kind. If receipt, use "receipt".
    if "receipt_id" in record:
         kind = "receipt"
    else:
         kind = record.get("event_kind", "")
         
    # Normalize ID
    # Use event_id or receipt_id
    rec_id = record.get("event_id") or record.get("receipt_id") or ""
    
    return (timestamp, kind, rec_id)

def _calc_policy_snapshot(policy_payload: Dict[str, Any]) -> Dict[str, str]:
    """
    Calculate deterministic policy snapshot (hash).
    """
    # Deterministic JSON serialization
    policy_blob = json.dumps(policy_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    policy_hash = hashlib.sha256(policy_blob).hexdigest()
    
    return {
        "policy_hash": policy_hash,
        # In a real system, might also include policy_version/id if present in payload
    }

# --- Core Functions ---

def ingest_cluster_a_artifact(path_or_obj: Union[str, Path, Dict[str, Any]], artifact_kind: Optional[str] = None) -> Dict[str, Any]:
    """
    Ingest and validate a Cluster A artifact.
    
    Args:
        path_or_obj: File path (str/Path) or Dict object.
        artifact_kind: Optional expected kind. If None, inferred.
        
    Returns:
        Deterministic envelope Dict found in _result.
    """
    errors: List[str] = []
    warnings: List[str] = []
    obj: Dict[str, Any] = {}
    
    # 1. Load Object
    if isinstance(path_or_obj, (str, Path)):
        try:
            p = Path(path_or_obj)
            if not p.exists():
                return _result(False, errors=["file_not_found"])
            obj = json.loads(p.read_text(encoding="utf-8"))
        except OSError:
            return _result(False, errors=["file_read_error"])
        except json.JSONDecodeError:
            return _result(False, errors=["invalid_json"])
    elif isinstance(path_or_obj, dict):
        obj = path_or_obj
    else:
        return _result(False, errors=["schema_violation:invalid_type:root"])

    # 2. Infer Kind
    inferred_kind = _infer_kind(obj)
    
    # 3. Check Context Violations
    if inferred_kind is None:
        return _result(False, errors=["context_violation:unknown_artifact_kind"])
        
    if artifact_kind is not None and artifact_kind != inferred_kind:
        # Check explicit mismatch
        return _result(False, artifact_kind=inferred_kind, errors=["context_violation:artifact_kind_mismatch"])
    
    target_kind = inferred_kind
    
    # 4. Dispatch Validation
    res: Dict[str, Any] = {"ok": False}
    
    if target_kind == "wire":
        res = validate_wire_event(obj)
    elif target_kind == "receipt":
        res = validate_receipt_record(obj)
    elif target_kind == "transcript":
        res = validate_transcript(obj)
    elif target_kind == "governance_record":
        res = validate_governance_record(obj)
    
    # 5. Return Envelope
    return _result(
        res["ok"],
        artifact_kind=target_kind,
        errors=res.get("errors", []),
        warnings=res.get("warnings", []),
        version=res.get("version"),
        data=obj if res["ok"] else None
    )

def assemble_canonical_transcript(records: List[Dict[str, Any]], *, transcript_meta: Dict[str, Any]) -> Dict[str, Any]:
    """
    Assemble a canonical transcript from raw records.
    Sorts and validates.
    """
    errors: List[str] = []
    valid_records: List[str] = []
    
    # 1. Validate Items
    for idx, rec in enumerate(records):
        wire_res = validate_wire_event(rec)
        receipt_res = validate_receipt_record(rec)
        
        if not wire_res["ok"] and not receipt_res["ok"]:
           errors.append(f"context_violation:record_not_wire_or_receipt:{idx}")
           # Stop processing on first context violation? Or collect all?
           # Prompt says: "Transcript assembly rejects any non-wire/non-receipt record."
           # We'll collect errors.
           continue
        
        valid_records.append(rec)
        
    if errors:
        return _result(False, artifact_kind="transcript", errors=errors)

    # 2. Sort Deterministically
    sorted_records = sorted(valid_records, key=_get_sort_key)
    
    # 3. Construct Transcript
    transcript_obj = transcript_meta.copy()
    transcript_obj["records"] = sorted_records
    
    if "protocol_version" not in transcript_obj:
        transcript_obj["protocol_version"] = "v0.1" # Default or required?
        
    # 4. Validate Resulting Transcript
    # This also checks schema fields like transcript_id etc.
    res = validate_transcript(transcript_obj)
    
    # Add metadata
    data = transcript_obj if res["ok"] else None
    if data:
         # Inject meta if not present (but transcript schema is strict...)
         # Actually assemble returns the transcript object usually.
         pass

    return _result(
        res["ok"],
        artifact_kind="transcript",
        errors=res.get("errors", []) + errors,
        warnings=res.get("warnings", []),
        version=res.get("version"),
        data=data
    )

# --- Phase 138: Signature Verification Helpers ---

try:
    from cryptography.hazmat.primitives.asymmetric import ed25519
    _HAS_CRYPTO = True
except ImportError:
    _HAS_CRYPTO = False

def canonical_governance_payload_bytes(record: Dict[str, Any]) -> bytes:
    """
    Compute canonical bytes for signing from a governance record.
    Removes 'signatures' field, sorts keys, uses compact separators.
    """
    payload = {k: v for k, v in record.items() if k != "signatures"}
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")

def verify_ed25519_signature(public_key_bytes: bytes, message: bytes, signature_hex: str) -> bool:
    """
    Verify Ed25519 signature.
    Raises GovernanceIngestValidationError on invalid input format.
    """
    if not _HAS_CRYPTO:
        raise RuntimeError("cryptography library missing")

    if len(public_key_bytes) != 32:
        raise GovernanceIngestValidationError("invalid_public_key_bytes")
    
    try:
        sig = bytes.fromhex(signature_hex)
    except ValueError:
        raise GovernanceIngestValidationError("invalid_signature_hex")

    if len(sig) != 64:
        raise GovernanceIngestValidationError("invalid_signature_length")
        
    pk = ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)
    try:
        pk.verify(sig, message)
        return True
    except Exception as exc:
        logger.debug("ingest_verify_signature_failure: %s", exc, exc_info=True)
        return False


def canonical_governance_record_digest(record: Dict[str, Any]) -> str:
    """
    Compute canonical digest of the entire record (excluding signatures).
    Used for identity binding in known_records.
    """
    # Exclude signatures, they are malleable witnessing data
    obj = {k: v for k, v in record.items() if k != "signatures"}
    # Deterministic JSON serialization
    blob = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()

def _resolve_known_records_hash_mode(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Resolve known-record identity mode with fail-closed behavior.

    Rules:
    - Explicit `payload_hash_v0` or `record_digest_v1` are accepted.
    - If mode is missing/unknown and `known_records` is non-empty, fail closed.
    - If mode is missing/unknown and `known_records` is empty, default to `record_digest_v1`.
    """
    known_records = state.get("known_records", {})
    if not isinstance(known_records, dict):
        known_records = {}

    mode = state.get("known_records_hash_mode")
    if mode == KNOWN_RECORDS_HASH_MODE_PAYLOAD:
        return {
            "ok": True,
            "mode": KNOWN_RECORDS_HASH_MODE_PAYLOAD,
            "warnings": [],
            "telemetry": {},
        }
    if mode == KNOWN_RECORDS_HASH_MODE_DIGEST:
        return {
            "ok": True,
            "mode": KNOWN_RECORDS_HASH_MODE_DIGEST,
            "warnings": [],
            "telemetry": {},
        }

    if known_records:
        return {
            "ok": False,
            "errors": ["context_violation:known_records_hash_mode_required"],
            "error_details": [{
                "code": "context_violation:known_records_hash_mode_required",
                "known_records_hash_mode": mode,
                "known_records_count": len(known_records),
                "telemetry_counter": "known_records_hash_mode_required_rejects",
            }],
        }

    return {
        "ok": True,
        "mode": KNOWN_RECORDS_HASH_MODE_DIGEST,
        "warnings": ["known_records_hash_mode_defaulted_to_record_digest_v1"],
        "telemetry": {
            "known_records_hash_mode_defaulted_to_record_digest_v1": 1,
        },
    }

def _verify_governance_signatures(
    record: Dict[str, Any],
    governance_keyring: Dict[str, bytes],
    min_valid_signatures: int
) -> Tuple[List[str], List[str], List[Dict[str, Any]]]:
    """
    Verify signatures on a governance record.
    Returns (valid_key_ids, errors, error_details).
    """
    errors: List[str] = []
    error_details: List[Dict[str, Any]] = []
    
    def _add(code: str, **ctx):
        _emit(errors, error_details, code, **ctx)

    if not _HAS_CRYPTO:
         _add("context_violation:signature_verification_unavailable")
         return [], errors, error_details

    if not isinstance(min_valid_signatures, int) or min_valid_signatures < 1:
        _add("value_violation:invalid_min_valid_signatures", min_valid_signatures=min_valid_signatures)
        return [], errors, error_details

    canonical_payload = canonical_governance_payload_bytes(record)
    valid_key_ids = set()
    seen_key_ids = set()
    
    for sig_block in record.get("signatures", []):
        key_id = sig_block.get("key_id")
        sig_alg = sig_block.get("sig_alg")
        sig_hex = sig_block.get("signature")
        
        # M1: Duplicate check (Option A: Hard Fail)
        if key_id in seen_key_ids:
            _add("context_violation:duplicate_signature_key_id", key_id=key_id)
            continue
        seen_key_ids.add(key_id)
        
        # Check algorithm
        if sig_alg != "ed25519":
            _add("context_violation:unsupported_sig_alg", alg=sig_alg)
            continue
            
        # Check key known
        if key_id not in governance_keyring:
            _add("context_violation:unknown_signing_key", key_id=key_id)
            continue
            
        pub_key = governance_keyring[key_id]
        
        # Verify
        try:
            if verify_ed25519_signature(pub_key, canonical_payload, sig_hex):
                valid_key_ids.add(key_id)
            else:
                _add("context_violation:signature_verification_failed", key_id=key_id)
        except GovernanceIngestValidationError as e:
            _add(f"value_violation:{str(e)}", key_id=key_id)
        except Exception as exc:
            logger.debug("ingest_signature_verification_guard: %s", exc, exc_info=True)
            _add("context_violation:signature_verification_failed", key_id=key_id)

    # Check Threshold
    if len(valid_key_ids) < min_valid_signatures:
        if not errors: # If no specific verification errors but threshold failed
             _add("context_violation:no_valid_signatures", required=min_valid_signatures, found=len(valid_key_ids))
             
    return sorted(list(valid_key_ids)), errors, error_details

def apply_governance_record(
    record: Dict[str, Any], 
    *, 
    current_policy_state: Dict[str, Any],
    governance_keyring: Optional[Dict[str, bytes]] = None,
    min_valid_signatures: int = 1
) -> Dict[str, Any]:
    """
    Apply a governance record to current policy state.
    Enforces validation, signature verification, and valid transitions.
    """
    # 0. Validate Policy State Shape (Hardening)
    if not isinstance(current_policy_state, dict):
         return _result(False, artifact_kind="governance_record", errors=["schema_violation:invalid_type:policy_state.root"])
    
    proposals_map = current_policy_state.get("proposals", {})
    if not isinstance(proposals_map, dict):
         return _result(False, artifact_kind="governance_record", errors=["schema_violation:invalid_type:policy_state.proposals"])

    known_records_raw = current_policy_state.get("known_records", {})
    if not isinstance(known_records_raw, dict):
         return _result(False, artifact_kind="governance_record", errors=["schema_violation:invalid_type:policy_state.known_records"])
    
    mode_raw = current_policy_state.get("known_records_hash_mode")
    if mode_raw is not None and not isinstance(mode_raw, str):
         return _result(False, artifact_kind="governance_record", errors=["schema_violation:invalid_type:policy_state.known_records_hash_mode"])

    # 1. Validate Record Schema
    val_res = validate_governance_record(record)
    if not val_res["ok"]:
        return _result(False, artifact_kind="governance_record", errors=val_res["errors"], warnings=val_res["warnings"])

    # 2. Verify Signatures (Phase 138)
    if governance_keyring is None:
        return _result(False, artifact_kind="governance_record", errors=["context_violation:missing_signature_verification_context"])

    valid_key_ids, sig_errors, sig_details = _verify_governance_signatures(
        record, governance_keyring, min_valid_signatures
    )
    
    if sig_errors:
        return _result(False, artifact_kind="governance_record", errors=sig_errors, error_details=sig_details or None)
        
    # 3. Check State Transition
    proposal_id = record.get("proposal_id", "unknown")
    new_state = record.get("state", "unknown")
    proposals_map = current_policy_state.get("proposals", {})
    actual_prev = proposals_map.get(proposal_id) # None if missing
    
    allowed_transitions = {
        (None, "proposed"),
        ("proposed", "finalized"),
        ("proposed", "rejected"),
        ("finalized", "finalized"), # Idempotent re-apply
        ("rejected", "rejected"),   # Idempotent re-apply
    }
    
    if (actual_prev, new_state) not in allowed_transitions:
        return _result(
            False, 
            artifact_kind="governance_record", 
            errors=["context_violation:invalid_state_transition"], 
            error_details=[{"code": "context_violation:invalid_state_transition", "prev": str(actual_prev), "current": str(new_state)}]
        )

    # 4. Resolve identity mode and check hash conflict (Identity Guard H1)
    mode_resolution = _resolve_known_records_hash_mode(current_policy_state)
    if not mode_resolution["ok"]:
        return _result(
            False,
            artifact_kind="governance_record",
            errors=mode_resolution["errors"],
            error_details=mode_resolution.get("error_details"),
        )

    known_records_mode = mode_resolution["mode"]
    mode_warnings = mode_resolution.get("warnings", [])
    mode_telemetry = mode_resolution.get("telemetry", {})

    known_records_raw = current_policy_state.get("known_records", {}) # map id -> hash
    known_records = known_records_raw if isinstance(known_records_raw, dict) else {}
    rec_id = record.get("gov_record_id")
    current_digest = canonical_governance_record_digest(record)
    current_payload_snapshot = _calc_policy_snapshot(record.get("payload", {}))
    current_payload_hash = current_payload_snapshot["policy_hash"]
    
    if rec_id in known_records:
        known_hash = known_records[rec_id]
        if known_records_mode == KNOWN_RECORDS_HASH_MODE_PAYLOAD:
            if known_hash != current_payload_hash:
                return _result(False, artifact_kind="governance_record", errors=["context_violation:gov_record_id_hash_conflict"])
        else:
            if known_hash != current_digest:
                return _result(False, artifact_kind="governance_record", errors=["context_violation:gov_record_id_record_digest_conflict"])

    known_record_value = (
        current_payload_hash
        if known_records_mode == KNOWN_RECORDS_HASH_MODE_PAYLOAD
        else current_digest
    )

    # 5. Success -> Bind metadata and return deterministic state delta (pure function)
    return _result(
        True,
        artifact_kind="governance_record",
        warnings=mode_warnings,
        data={
            "proposal_id": proposal_id,
            "new_state": new_state,
            "policy_snapshot": current_payload_snapshot,
            "verified_signers": valid_key_ids,
            "record_digest": current_digest,
            "record_digest_mode": KNOWN_RECORDS_HASH_MODE_DIGEST,
            "known_records_hash_mode_effective": known_records_mode,
            "telemetry": mode_telemetry,
            "policy_state_delta": {
                "proposals": {proposal_id: new_state},
                "known_records": {rec_id: known_record_value},
                "known_records_hash_mode": known_records_mode,
            },
        }
    )
    
def infer_cluster_a_artifact_kind(obj: Dict[str, Any]) -> Optional[str]:
    """Public alias for _infer_kind."""
    return _infer_kind(obj)
