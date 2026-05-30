"""PUBLIC_RC_EXCLUDE: private_consent_gate
PUBLIC_RC_EXCLUDE_REASON: Private local capture consent gate. Does not authorize production graph writes.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class ConsentDecision:
    subject_id: str
    purpose: str
    allowed: bool
    decision_id: str


class ConsentGate:
    """Deterministic local gate for private capture-to-artifact transitions."""

    def __init__(self, decisions: list[ConsentDecision] | None = None) -> None:
        self._decisions: dict[tuple[str, str], ConsentDecision] = {}
        for decision in decisions or []:
            self.record(decision)

    @staticmethod
    def from_fixture(rows: list[Mapping[str, object]]) -> "ConsentGate":
        decisions: list[ConsentDecision] = []
        for row in rows:
            decisions.append(
                ConsentDecision(
                    subject_id=str(row.get("subject_id", "")),
                    purpose=str(row.get("purpose", "")),
                    allowed=bool(row.get("allowed", False)),
                    decision_id=str(row.get("decision_id", "")),
                )
            )
        return ConsentGate(decisions)

    def record(self, decision: ConsentDecision) -> None:
        if decision.subject_id == "" or decision.purpose == "" or decision.decision_id == "":
            raise ValueError("consent_gate_invalid_decision")
        self._decisions[(decision.subject_id, decision.purpose)] = decision

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
