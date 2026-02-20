from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Mapping, Sequence

from .signer_lineage_runtime import SignerLineageRegistry


FINALIZATION_STATE_ROLLED_BACK = "rolled_back"
CLAWBACK_REQUIRED = "clawback_required"
CLAWBACK_NOT_REQUIRED = "clawback_not_required"

ALLOWED_CLAWBACK_POLICIES = {CLAWBACK_REQUIRED, CLAWBACK_NOT_REQUIRED}


@dataclass(frozen=True)
class RollbackSupersessionEvent:
    supersession_id: str
    target_window_id: str
    finalization_state: str
    clawback_policy: str
    canonical_root_key: str
    authorizing_lineage_id: str
    authorizing_signer_id: str
    reason_code: str
    event_ts: str


class RollbackResistanceRuntime:
    """CDL-007 rollback resistance runtime surface."""

    def __init__(self, registry: SignerLineageRegistry) -> None:
        self._registry = registry
        self._events_by_id: Dict[str, RollbackSupersessionEvent] = {}
        self._window_to_supersession_id: Dict[str, str] = {}

    @property
    def events(self) -> Sequence[RollbackSupersessionEvent]:
        return tuple(self._events_by_id.values())

    @staticmethod
    def build_event_from_mapping(payload: Mapping[str, object]) -> RollbackSupersessionEvent:
        required = [
            "supersession_id",
            "target_window_id",
            "finalization_state",
            "clawback_policy",
            "canonical_root_key",
            "authorizing_lineage_id",
            "authorizing_signer_id",
            "reason_code",
            "event_ts",
        ]
        missing = [key for key in required if key not in payload]
        if missing:
            raise ValueError(f"missing_supersession_tokens:{','.join(missing)}")

        for key in required:
            if not isinstance(payload[key], str) or not payload[key]:
                raise ValueError(f"invalid_supersession_token:{key}")

        return RollbackSupersessionEvent(
            supersession_id=str(payload["supersession_id"]),
            target_window_id=str(payload["target_window_id"]),
            finalization_state=str(payload["finalization_state"]),
            clawback_policy=str(payload["clawback_policy"]),
            canonical_root_key=str(payload["canonical_root_key"]),
            authorizing_lineage_id=str(payload["authorizing_lineage_id"]),
            authorizing_signer_id=str(payload["authorizing_signer_id"]),
            reason_code=str(payload["reason_code"]),
            event_ts=str(payload["event_ts"]),
        )

    def validate_supersession_event(self, event: RollbackSupersessionEvent) -> None:
        if event.finalization_state != FINALIZATION_STATE_ROLLED_BACK:
            raise ValueError("invalid_finalization_state")

        if event.clawback_policy not in ALLOWED_CLAWBACK_POLICIES:
            raise ValueError("invalid_clawback_policy")

        authority = self._registry.verify_canonical_authority(
            canonical_root_key=event.canonical_root_key,
            lineage_id=event.authorizing_lineage_id,
            signer_id=event.authorizing_signer_id,
        )
        if not authority.accepted:
            raise ValueError(f"unauthorized_supersession_signer:{authority.reason}")

    def apply_supersession_event(self, event: RollbackSupersessionEvent) -> None:
        self.validate_supersession_event(event)

        if event.supersession_id in self._events_by_id:
            raise ValueError("replayed_supersession_identifier")

        existing = self._window_to_supersession_id.get(event.target_window_id)
        if existing is not None and existing != event.supersession_id:
            raise ValueError("conflicting_supersession_chain")

        self._events_by_id[event.supersession_id] = event
        self._window_to_supersession_id[event.target_window_id] = event.supersession_id
