"""PUBLIC_RC_EXCLUDE: private_consent_gate
PUBLIC_RC_EXCLUDE_REASON: Private local capture consent gate. Does not authorize production graph writes.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Mapping

from ilc_core.harness.co_attestation_receipt import CoAttestationReceipt
from ilc_core.harness.local_immutable_store import LocalImmutableStore, build_local_ledger_entry
from ilc_core.private_json_guardrails import require_sha256_hex

MAX_DECISIONS = 4096


@dataclass(frozen=True)
class ConsentDecision:
    subject_id: str
    purpose: str
    allowed: bool
    decision_id: str


class ConsentGate:
    """Deterministic local gate for private capture-to-artifact transitions."""

    def __init__(
        self,
        decisions: list[ConsentDecision] | None = None,
        *,
        max_decisions: int = MAX_DECISIONS,
        store: LocalImmutableStore | None = None,
    ) -> None:
        if max_decisions < 1 or max_decisions > MAX_DECISIONS:
            raise ValueError("consent_gate_invalid_max_decisions")
        self._max_decisions = max_decisions
        self._store = store
        self._decisions: dict[tuple[str, str], ConsentDecision] = {}
        for decision in decisions or []:
            self.record(decision)

    @staticmethod
    def from_fixture(
        rows: list[Mapping[str, object]],
        *,
        max_decisions: int = MAX_DECISIONS,
    ) -> "ConsentGate":
        decisions: list[ConsentDecision] = []
        for row in rows:
            allowed = row.get("allowed", False)
            if not isinstance(allowed, bool):
                raise ValueError("consent_gate_fixture_allowed_must_be_bool")
            decisions.append(
                ConsentDecision(
                    subject_id=str(row.get("subject_id", "")),
                    purpose=str(row.get("purpose", "")),
                    allowed=allowed,
                    decision_id=str(row.get("decision_id", "")),
                )
            )
        return ConsentGate(decisions, max_decisions=max_decisions)

    def record(self, decision: ConsentDecision) -> None:
        if decision.subject_id == "" or decision.purpose == "" or decision.decision_id == "":
            raise ValueError("consent_gate_invalid_decision")
        key = (decision.subject_id, decision.purpose)
        existing = self._decisions.get(key)
        if existing is not None:
            if existing != decision:
                raise ValueError("consent_gate_duplicate_decision")
            return
        if len(self._decisions) >= self._max_decisions:
            raise ValueError("consent_gate_max_decisions_exceeded")
        self._decisions[key] = decision

    def decision_for(self, subject_id: str, purpose: str) -> ConsentDecision | None:
        return self._decisions.get((subject_id, purpose))

    def is_allowed(self, subject_id: str, purpose: str) -> bool:
        decision = self.decision_for(subject_id, purpose)
        return bool(decision and decision.allowed)

    def require_allowed(self, subject_id: str, purpose: str) -> ConsentDecision:
        decision = self.decision_for(subject_id, purpose)
        if decision is None or not decision.allowed:
            raise ValueError("consent_gate_denied")
        return decision

    def approve(
        self,
        artifact: object,
        *,
        subject_id: str,
        purpose: str,
        committed_at_epoch: int = 0,
        receipt: CoAttestationReceipt | None = None,
        store: LocalImmutableStore | None = None,
    ) -> CoAttestationReceipt | None:
        decision = self.require_allowed(subject_id, purpose)
        artifact_sha256 = _extract_artifact_sha256(artifact)
        if receipt is not None and receipt.artifact_sha256 != artifact_sha256:
            raise ValueError("consent_gate_receipt_artifact_mismatch")

        active_store = store if store is not None else self._store
        if active_store is None:
            return receipt

        entry = build_local_ledger_entry(
            artifact_sha256=artifact_sha256,
            consent_gate_decision_id=decision.decision_id,
            committed_at_epoch=committed_at_epoch,
        )
        entry_id = active_store.write(entry)
        if receipt is None:
            return None
        return replace(receipt, local_ledger_entry_id=entry_id)

    def reject(
        self,
        artifact: object | None = None,
        *,
        subject_id: str,
        purpose: str,
        receipt: CoAttestationReceipt | None = None,
    ) -> CoAttestationReceipt | None:
        decision = self.decision_for(subject_id, purpose)
        if decision is None or decision.allowed:
            raise ValueError("consent_gate_denied")
        return receipt


def _extract_artifact_sha256(artifact: object) -> str:
    if isinstance(artifact, Mapping):
        candidate = artifact.get("sha256", artifact.get("artifact_sha256"))
    else:
        candidate = getattr(artifact, "sha256", None)
        if candidate is None:
            candidate = getattr(artifact, "artifact_sha256", None)
    if not isinstance(candidate, str):
        raise ValueError("consent_gate_artifact_sha256_missing")
    require_sha256_hex(candidate, "consent_gate_artifact_sha256_invalid")
    return candidate
