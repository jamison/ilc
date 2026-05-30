"""PUBLIC_RC_EXCLUDE: private_co_attestation_receipt
PUBLIC_RC_EXCLUDE_REASON: Private local co-attestation fixture. Not a public consensus or settlement proof.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Mapping

MAX_ATTESTATIONS = 16


def _canonical_json(payload: Mapping[str, object]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)


@dataclass(frozen=True)
class CoAttestationReceipt:
    receipt_id: str
    artifact_sha256: str
    attestation_signatures: list[dict[str, str]]
    canonical_json: str
    receipt_sha256: str
    public_rc_exclude: bool = True


def build_co_attestation_receipt(
    *,
    receipt_id: str,
    artifact_sha256: str,
    attestation_signatures: list[Mapping[str, str]],
) -> CoAttestationReceipt:
    if receipt_id == "" or artifact_sha256 == "":
        raise ValueError("co_attestation_missing_identifier")
    if len(attestation_signatures) == 0 or len(attestation_signatures) > MAX_ATTESTATIONS:
        raise ValueError("co_attestation_invalid_signature_count")

    normalized: list[dict[str, str]] = []
    seen_agents: set[str] = set()
    for row in attestation_signatures:
        agent_id = str(row.get("agent_id", ""))
        signature = str(row.get("signature", ""))
        if agent_id == "" or signature == "":
            raise ValueError("co_attestation_invalid_signature")
        if agent_id in seen_agents:
            raise ValueError("co_attestation_duplicate_agent")
        seen_agents.add(agent_id)
        normalized.append({"agent_id": agent_id, "signature": signature})

    normalized.sort(key=lambda row: row["agent_id"])
    envelope = {
        "artifact_sha256": artifact_sha256,
        "attestation_signatures": normalized,
        "public_rc_exclude": True,
        "receipt_id": receipt_id,
    }
    canonical_json = _canonical_json(envelope)
    return CoAttestationReceipt(
        receipt_id=receipt_id,
        artifact_sha256=artifact_sha256,
        attestation_signatures=normalized,
        canonical_json=canonical_json,
        receipt_sha256=hashlib.sha256(canonical_json.encode("utf-8")).hexdigest(),
    )


def verify_co_attestation_receipt(receipt: CoAttestationReceipt) -> bool:
    rebuilt = build_co_attestation_receipt(
        receipt_id=receipt.receipt_id,
        artifact_sha256=receipt.artifact_sha256,
        attestation_signatures=receipt.attestation_signatures,
    )
    return (
        rebuilt.canonical_json == receipt.canonical_json
        and rebuilt.receipt_sha256 == receipt.receipt_sha256
        and receipt.public_rc_exclude is True
    )
