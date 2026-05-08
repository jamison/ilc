from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Mapping, Optional, Sequence
import copy
import hashlib


ACTIVE = "active"
ROTATED = "rotated"
REVOKED = "revoked"
RECOVERED = "recovered"

REGISTER = "register"
ROTATE = "rotate"
REVOKE = "revoke"
RECOVER = "recover"

ALLOWED_STATES = {ACTIVE, ROTATED, REVOKED, RECOVERED}
ALLOWED_EVENTS = {REGISTER, ROTATE, REVOKE, RECOVER}
ALLOWED_TRANSITIONS = {
    (ACTIVE, ROTATED),
    (ACTIVE, REVOKED),
    (ROTATED, REVOKED),
    (REVOKED, RECOVERED),
    (RECOVERED, ROTATED),
    (RECOVERED, REVOKED),
}


@dataclass(frozen=True)
class LineageTransitionRecord:
    event_id: str
    event_name: str
    lineage_id: str
    subject_signer_id: str
    authorizer_signer_id: str
    reason_code: str
    event_ts: str
    prev_state: str
    next_state: str
    canonical_root_key: Optional[str] = None
    authority_recovery_key: Optional[str] = None
    replacement_signer_id: Optional[str] = None
    recovery_ticket_id: Optional[str] = None


@dataclass
class LineageEntry:
    lineage_id: str
    canonical_root_key: str
    authority_recovery_key: str
    operational_signer_key: str
    state: str


@dataclass(frozen=True)
class VerificationResult:
    accepted: bool
    reason: str


@dataclass(frozen=True)
class LineageRegistryCheckpoint:
    entries: Mapping[str, LineageEntry]
    transition_log: Sequence[LineageTransitionRecord]
    event_counter: int


class SignerLineageRegistry:
    """Runtime signer-lineage trust-root registry with append-only transition log."""

    def __init__(self) -> None:
        self._entries: Dict[str, LineageEntry] = {}
        self._transition_log: List[LineageTransitionRecord] = []
        self._event_counter: int = 0

    @property
    def entries(self) -> Mapping[str, LineageEntry]:
        return self._entries

    @property
    def transition_log(self) -> Sequence[LineageTransitionRecord]:
        return tuple(self._transition_log)

    def register(
        self,
        *,
        lineage_id: str,
        canonical_root_key: str,
        authority_recovery_key: str,
        operational_signer_key: str,
        authorizer_signer_id: str,
        reason_code: str,
        event_ts: str,
    ) -> LineageTransitionRecord:
        if lineage_id in self._entries:
            raise ValueError(f"lineage already registered: {lineage_id}")

        entry = LineageEntry(
            lineage_id=lineage_id,
            canonical_root_key=canonical_root_key,
            authority_recovery_key=authority_recovery_key,
            operational_signer_key=operational_signer_key,
            state=ACTIVE,
        )
        self._entries[lineage_id] = entry

        record = self._make_record(
            event_name=REGISTER,
            lineage_id=lineage_id,
            reason_code=reason_code,
            event_ts=event_ts,
            transition=("none", ACTIVE),
            signers=(operational_signer_key, authorizer_signer_id),
            root_keys=(canonical_root_key, authority_recovery_key),
        )
        self._append_record(record)
        return record

    def rotate(
        self,
        *,
        lineage_id: str,
        replacement_signer_id: str,
        authorizer_signer_id: str,
        reason_code: str,
        event_ts: str,
    ) -> LineageTransitionRecord:
        entry = self._require_entry(lineage_id)
        self._require_transition_allowed(entry.state, ROTATED)

        prev_state = entry.state
        entry.operational_signer_key = replacement_signer_id
        entry.state = ROTATED

        record = self._make_record(
            event_name=ROTATE,
            lineage_id=lineage_id,
            reason_code=reason_code,
            event_ts=event_ts,
            transition=(prev_state, ROTATED),
            signers=(replacement_signer_id, authorizer_signer_id),
            replacement_signer_id=replacement_signer_id,
        )
        self._append_record(record)
        return record

    def revoke(
        self,
        *,
        lineage_id: str,
        authorizer_signer_id: str,
        reason_code: str,
        event_ts: str,
    ) -> LineageTransitionRecord:
        entry = self._require_entry(lineage_id)
        self._require_transition_allowed(entry.state, REVOKED)

        prev_state = entry.state
        entry.state = REVOKED

        record = self._make_record(
            event_name=REVOKE,
            lineage_id=lineage_id,
            reason_code=reason_code,
            event_ts=event_ts,
            transition=(prev_state, REVOKED),
            signers=(entry.operational_signer_key, authorizer_signer_id),
        )
        self._append_record(record)
        return record

    def recover(
        self,
        *,
        lineage_id: str,
        replacement_signer_id: str,
        recovery_ticket_id: str,
        authorizer_signer_id: str,
        reason_code: str,
        event_ts: str,
    ) -> LineageTransitionRecord:
        entry = self._require_entry(lineage_id)
        self._require_transition_allowed(entry.state, RECOVERED)

        prev_state = entry.state
        entry.operational_signer_key = replacement_signer_id
        entry.state = RECOVERED

        record = self._make_record(
            event_name=RECOVER,
            lineage_id=lineage_id,
            reason_code=reason_code,
            event_ts=event_ts,
            transition=(prev_state, RECOVERED),
            signers=(replacement_signer_id, authorizer_signer_id),
            replacement_signer_id=replacement_signer_id,
            recovery_ticket_id=recovery_ticket_id,
        )
        self._append_record(record)
        return record

    def validate_lineage_chain(
        self,
        *,
        canonical_root_key: str,
        lineage_id: str,
        operational_signer_key: str,
    ) -> VerificationResult:
        entry = self._entries.get(lineage_id)
        if entry is None:
            return VerificationResult(False, "unknown_lineage")
        if entry.canonical_root_key != canonical_root_key:
            return VerificationResult(False, "non_anchored_lineage")
        if entry.operational_signer_key != operational_signer_key:
            return VerificationResult(False, "operational_signer_mismatch")
        return VerificationResult(True, "lineage_chain_valid")

    def verify_canonical_authority(
        self,
        *,
        canonical_root_key: str,
        lineage_id: str,
        signer_id: str,
    ) -> VerificationResult:
        """Check whether signer_id holds canonical signing authority for lineage_id.

        Authority-eligible states: ``active`` and ``recovered`` only.
        ``rotated`` is non-authoritative — replacement authority is established only
        after the full ``revoke`` → ``recover`` cycle completes (``recovered`` state).
        ``revoked`` is never authoritative.
        """
        entry = self._entries.get(lineage_id)
        if entry is None:
            return VerificationResult(False, "unknown_lineage")
        if entry.canonical_root_key != canonical_root_key:
            return VerificationResult(False, "non_anchored_lineage")
        if entry.state == REVOKED:
            return VerificationResult(False, "revoked_lineage")
        if entry.state not in {ACTIVE, RECOVERED}:
            return VerificationResult(False, "lineage_not_canonical_authority_state")
        if signer_id not in {
            entry.canonical_root_key,
            entry.authority_recovery_key,
            entry.operational_signer_key,
        }:
            return VerificationResult(False, "signer_not_in_lineage")
        return VerificationResult(True, "accepted")

    def create_checkpoint(self) -> LineageRegistryCheckpoint:
        return LineageRegistryCheckpoint(
            entries=copy.deepcopy(self._entries),
            transition_log=tuple(self._transition_log),
            event_counter=self._event_counter,
        )

    def restore_checkpoint(self, checkpoint: LineageRegistryCheckpoint) -> None:
        self._entries = copy.deepcopy(dict(checkpoint.entries))
        self._transition_log = list(checkpoint.transition_log)
        self._event_counter = checkpoint.event_counter

    @classmethod
    def replay_from_log(cls, transition_log: Sequence[LineageTransitionRecord]) -> "SignerLineageRegistry":
        registry = cls()
        for record in transition_log:
            registry._apply_record(record)
        return registry

    def _apply_record(self, record: LineageTransitionRecord) -> None:
        if record.event_name not in ALLOWED_EVENTS:
            raise ValueError(f"unsupported event: {record.event_name}")

        if record.event_name == REGISTER:
            if record.lineage_id in self._entries:
                raise ValueError(f"duplicate register event for lineage: {record.lineage_id}")
            self._entries[record.lineage_id] = LineageEntry(
                lineage_id=record.lineage_id,
                canonical_root_key=record.canonical_root_key or record.authorizer_signer_id,
                authority_recovery_key=record.authority_recovery_key or record.authorizer_signer_id,
                operational_signer_key=record.subject_signer_id,
                state=record.next_state,
            )
        else:
            entry = self._require_entry(record.lineage_id)
            self._require_transition_allowed(entry.state, record.next_state)
            entry.state = record.next_state
            if record.replacement_signer_id:
                entry.operational_signer_key = record.replacement_signer_id

        self._transition_log.append(record)

    def _append_record(self, record: LineageTransitionRecord) -> None:
        if record.next_state != ACTIVE and record.next_state not in ALLOWED_STATES:
            raise ValueError(f"invalid next_state: {record.next_state}")
        self._transition_log.append(record)

    def _require_entry(self, lineage_id: str) -> LineageEntry:
        entry = self._entries.get(lineage_id)
        if entry is None:
            raise ValueError(f"unknown lineage: {lineage_id}")
        return entry

    def _require_transition_allowed(self, from_state: str, to_state: str) -> None:
        if (from_state, to_state) not in ALLOWED_TRANSITIONS:
            raise ValueError(f"disallowed transition: {from_state} -> {to_state}")

    def _make_record(
        self,
        *,
        event_name: str,
        lineage_id: str,
        reason_code: str,
        event_ts: str,
        transition: tuple[str, str],
        signers: tuple[str, str],
        root_keys: tuple[Optional[str], Optional[str]] = (None, None),
        replacement_signer_id: Optional[str] = None,
        recovery_ticket_id: Optional[str] = None,
    ) -> LineageTransitionRecord:
        prev_state, next_state = transition
        subject_signer_id, authorizer_signer_id = signers
        canonical_root_key, authority_recovery_key = root_keys
        self._event_counter += 1
        event_id = self._derive_event_id(
            event_name=event_name,
            lineage_id=lineage_id,
            event_counter=self._event_counter,
            event_ts=event_ts,
        )
        return LineageTransitionRecord(
            event_id=event_id,
            event_name=event_name,
            lineage_id=lineage_id,
            subject_signer_id=subject_signer_id,
            authorizer_signer_id=authorizer_signer_id,
            reason_code=reason_code,
            event_ts=event_ts,
            prev_state=prev_state,
            next_state=next_state,
            canonical_root_key=canonical_root_key,
            authority_recovery_key=authority_recovery_key,
            replacement_signer_id=replacement_signer_id,
            recovery_ticket_id=recovery_ticket_id,
        )

    @staticmethod
    def _derive_event_id(*, event_name: str, lineage_id: str, event_counter: int, event_ts: str) -> str:
        payload = f"{event_name}|{lineage_id}|{event_counter}|{event_ts}".encode("utf-8")
        return hashlib.sha256(payload).hexdigest()
