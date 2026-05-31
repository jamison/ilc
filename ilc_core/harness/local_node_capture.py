"""PUBLIC_RC_EXCLUDE: private_local_node_capture
PUBLIC_RC_EXCLUDE_REASON: Private local node capture helper. Does not write production graph state.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Mapping

from ilc_core.harness.consent_gate import ConsentGate
from ilc_core.private_json_guardrails import canonical_json as _canonical_json, reject_float

MAX_CAPTURE_FIELDS = 64


@dataclass(frozen=True)
class LocalNodeSnapshot:
    capture_id: str
    node_id: str
    subject_id: str
    purpose: str
    canonical_json: str
    sha256: str
    public_rc_exclude: bool = True
    production_graph_write: bool = False


class LocalNodeCapture:
    """Build deterministic local snapshots for private graph-shaped artifacts."""

    def __init__(self, *, purpose: str, consent_gate: ConsentGate) -> None:
        if purpose == "":
            raise ValueError("local_node_capture_missing_purpose")
        self._purpose = purpose
        self._consent_gate = consent_gate

    def capture(
        self,
        *,
        capture_id: str,
        node_id: str,
        subject_id: str,
        payload: Mapping[str, object],
    ) -> LocalNodeSnapshot:
        if capture_id == "" or node_id == "" or subject_id == "":
            raise ValueError("local_node_capture_missing_identifier")
        if len(payload) > MAX_CAPTURE_FIELDS:
            raise ValueError("local_node_capture_field_cap_exceeded")
        reject_float(payload, "local_node_capture_float_not_allowed")

        self._consent_gate.require_allowed(subject_id, self._purpose)
        envelope = {
            "capture_id": capture_id,
            "node_id": node_id,
            "payload": dict(payload),
            "production_graph_write": False,
            "public_rc_exclude": True,
            "purpose": self._purpose,
            "subject_id": subject_id,
        }
        canonical_json = _canonical_json(envelope, float_token="local_node_capture_float_not_allowed")
        digest = hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()
        return LocalNodeSnapshot(
            capture_id=capture_id,
            node_id=node_id,
            subject_id=subject_id,
            purpose=self._purpose,
            canonical_json=canonical_json,
            sha256=digest,
        )
