"""
ILC Constitution Cluster A - Core Runtime Ingest.
Phase 135.

Provides deterministic ingest, dispatch, assembly, and application logic 
for Cluster A artifacts (Wire, Receipt, Transcript, Governance Record).
"""

import json
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# Import Phase 134 validators
from ilc_core.protocol.ilc_wire_validate import validate_wire_event
from ilc_core.protocol.ilc_receipt_validate import validate_receipt_record
from ilc_core.protocol.ilc_transcript_validate import validate_transcript
from ilc_core.protocol.ilc_governance_record_validate import validate_governance_record

# --- Helpers ---

def _result(ok: bool, *, artifact_kind: Optional[str] = None, errors: List[str] = None, warnings: List[str] = None, version: Optional[str] = None, data: Any = None) -> Dict[str, Any]:
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
    }

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
    valid_records: List[Dict[str, Any]] = []
    
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

def apply_governance_record(record: Dict[str, Any], *, current_policy_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply a governance record to current policy state.
    Enforces validation and valid transitions.
    """
    errors: List[str] = []
    
    # 1. Validate Record
    val_res = validate_governance_record(record)
    if not val_res["ok"]:
        return _result(False, artifact_kind="governance_record", errors=val_res["errors"], warnings=val_res["warnings"])
        
    # 2. Check State Transition
    # Allowed: 
    #   (none/unknown) -> proposed (implicit initialization?)
    #   proposed -> finalized
    #   proposed -> rejected
    # Context: current_policy_state might track the proposal state?
    # Or does it valid transitions of the record's 'state' field itself?
    # The prompt says: "Enforce minimal deterministic state transitions... allowed: proposed->finalized".
    # This implies we are tracking the state OF THIS PROPOSAL ID in the policy history.
    
    proposal_id = record.get("proposal_id", "unknown")
    new_state = record.get("state", "unknown")
    
    # We need to know previous state of this proposal from current_policy_state?
    # Assuming current_policy_state has structure { "proposals": { proposal_id: state } } ??
    # Or implies checking consistency if we are updating an existing record?
    # The prompt example: "if (old_state, new_state) not in allowed..."
    
    # Let's assume current_policy_state tracks proposal states.
    proposals_map = current_policy_state.get("proposals", {})
    old_state = proposals_map.get(proposal_id, "proposed") # Default strictly? Or "new"?
    
    # Special case: If we haven't seen it, it's effectively "new/proposed". 
    # But if the record CLAIMS to be "finalized", and we haven't seen "proposed", is that allowed?
    # Usually you promote status.
    # Let's define:
    #   None -> proposed (New proposal) - wait, record HAS a state.
    #   So if record state is "proposed", allowed if old is None.
    #   If record state is "finalized", allowed if old is "proposed".
    
    # Wait, apply_governance_record is usually applying a CHANGE.
    # If the record is a "Proposal Record", it might be valid on its own.
    # Transition Logic:
    allowed_transitions = {
        (None, "proposed"),
        ("proposed", "finalized"),
        ("proposed", "rejected"),
        ("finalized", "finalized"), # Idempotent re-apply
        ("rejected", "rejected"),   # Idempotent re-apply
    }
    
    actual_prev = proposals_map.get(proposal_id) # None if missing
    
    if (actual_prev, new_state) not in allowed_transitions:
        return _result(False, artifact_kind="governance_record", errors=[f"context_violation:invalid_state_transition:{actual_prev}:{new_state}"])

    # 3. Check Hash Conflict (Idempotency Guard)
    # If we have seen this ID before, payload/hash must match.
    # prompt: "same gov_record_id + different payload hash must fail"
    known_records = current_policy_state.get("known_records", {}) # map id -> hash
    rec_id = record.get("gov_record_id")
    
    # Calculate hash of THIS record's payload
    current_payload_snapshot = _calc_policy_snapshot(record.get("payload", {}))
    current_hash = current_payload_snapshot["policy_hash"]
    
    if rec_id in known_records:
        known_hash = known_records[rec_id]
        if known_hash != current_hash:
             return _result(False, artifact_kind="governance_record", errors=["context_violation:gov_record_id_hash_conflict"])
             
    # 4. Success -> Bind Metadata
    return _result(
        True,
        artifact_kind="governance_record",
        data={
            "proposal_id": proposal_id,
            "new_state": new_state,
            "policy_snapshot": current_payload_snapshot
        }
    )
    
def infer_cluster_a_artifact_kind(obj: Dict[str, Any]) -> Optional[str]:
    """Public alias for _infer_kind."""
    return _infer_kind(obj)
