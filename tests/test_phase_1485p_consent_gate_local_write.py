from types import SimpleNamespace

import pytest

from ilc_core.harness import local_immutable_store
from ilc_core.harness.co_attestation_receipt import (
    build_co_attestation_receipt,
    verify_co_attestation_receipt,
)
from ilc_core.harness.consent_gate import ConsentDecision, ConsentGate
from ilc_core.harness.local_immutable_store import (
    LOCAL_IMMUTABLE_STORE_NOT_PRODUCTION,
    LocalImmutableStore,
    StoreAtCapacity,
    build_local_ledger_entry,
)


def _artifact(artifact_sha256: str = "a" * 64) -> SimpleNamespace:
    return SimpleNamespace(sha256=artifact_sha256)


def _receipt(artifact_sha256: str = "a" * 64):
    return build_co_attestation_receipt(
        receipt_id="receipt-1",
        artifact_sha256=artifact_sha256,
        attestation_signatures=[
            {"agent_id": "agent-1", "signature": "sig-1"},
            {"agent_id": "agent-2", "signature": "sig-2"},
        ],
    )


def test_consent_gate_writes_local_entry_on_approve(tmp_path) -> None:
    store = LocalImmutableStore(tmp_path)
    gate = ConsentGate(
        [
            ConsentDecision(
                subject_id="agent-1",
                purpose="private_query_response_artifact",
                allowed=True,
                decision_id="consent-1",
            )
        ],
        store=store,
    )

    updated_receipt = gate.approve(
        _artifact(),
        subject_id="agent-1",
        purpose="private_query_response_artifact",
        committed_at_epoch=7,
        receipt=_receipt(),
    )

    assert updated_receipt is not None
    assert updated_receipt.local_ledger_entry_id is not None
    assert verify_co_attestation_receipt(updated_receipt) is True

    entry = store.read(updated_receipt.local_ledger_entry_id)
    assert entry.artifact_sha256 == "a" * 64
    assert entry.consent_gate_decision_id == "consent-1"
    assert entry.committed_at_epoch == 7


def test_consent_gate_reject_does_not_write(tmp_path) -> None:
    store = LocalImmutableStore(tmp_path)
    gate = ConsentGate(
        [
            ConsentDecision(
                subject_id="agent-1",
                purpose="private_query_response_artifact",
                allowed=False,
                decision_id="deny-1",
            )
        ],
        store=store,
    )
    receipt = _receipt()

    rejected_receipt = gate.reject(
        _artifact(),
        subject_id="agent-1",
        purpose="private_query_response_artifact",
        receipt=receipt,
    )

    assert rejected_receipt is receipt
    assert rejected_receipt.local_ledger_entry_id is None
    assert store.entry_count() == 0


def test_local_immutable_store_read_round_trips_entry(tmp_path) -> None:
    store = LocalImmutableStore(tmp_path)
    entry = build_local_ledger_entry(
        artifact_sha256="b" * 64,
        consent_gate_decision_id="consent-2",
        committed_at_epoch=3,
    )

    entry_id = store.write(entry)
    restored = store.read(entry_id)

    assert restored == entry
    assert restored.artifact_sha256 == "b" * 64


def test_local_immutable_store_enforces_max_entries(tmp_path) -> None:
    store = LocalImmutableStore(tmp_path, max_entries=2)
    store.write(
        build_local_ledger_entry(
            artifact_sha256="c" * 64,
            consent_gate_decision_id="consent-1",
            committed_at_epoch=1,
        )
    )
    store.write(
        build_local_ledger_entry(
            artifact_sha256="d" * 64,
            consent_gate_decision_id="consent-2",
            committed_at_epoch=2,
        )
    )

    with pytest.raises(StoreAtCapacity) as exc:
        store.write(
            build_local_ledger_entry(
                artifact_sha256="e" * 64,
                consent_gate_decision_id="consent-3",
                committed_at_epoch=3,
            )
        )

    assert str(exc.value) == "local_immutable_store_at_capacity"


def test_local_immutable_store_not_production_guard_is_visible() -> None:
    assert LOCAL_IMMUTABLE_STORE_NOT_PRODUCTION is True
    assert local_immutable_store.LOCAL_IMMUTABLE_STORE_NOT_PRODUCTION is True


def test_local_ledger_entry_rejects_float_epoch() -> None:
    entry = build_local_ledger_entry(
        artifact_sha256="f" * 64,
        consent_gate_decision_id="consent-4",
        committed_at_epoch=4,
    )

    assert isinstance(entry.committed_at_epoch, int)
    assert not isinstance(entry.committed_at_epoch, float)
    assert isinstance(entry.entry_id, str)
    assert isinstance(entry.artifact_sha256, str)

    with pytest.raises(ValueError) as exc:
        build_local_ledger_entry(
            artifact_sha256="f" * 64,
            consent_gate_decision_id="consent-4",
            committed_at_epoch=4.5,  # type: ignore[arg-type]
        )

    assert str(exc.value) == "local_ledger_entry_invalid_epoch"


def test_consent_gate_approve_without_store_preserves_existing_behavior() -> None:
    gate = ConsentGate(
        [
            ConsentDecision(
                subject_id="agent-1",
                purpose="private_query_response_artifact",
                allowed=True,
                decision_id="consent-1",
            )
        ]
    )
    receipt = _receipt()

    unchanged_receipt = gate.approve(
        _artifact(),
        subject_id="agent-1",
        purpose="private_query_response_artifact",
        receipt=receipt,
    )

    assert unchanged_receipt is receipt
    assert unchanged_receipt.local_ledger_entry_id is None
