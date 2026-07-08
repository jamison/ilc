from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from ilc_core.ledger import conversion_candidate_runtime as runtime
from ilc_core.ledger.distributed_conversion_schema import (
    CDL057_WITNESS_ABSENT_TOKEN,
    GENESIS_TRANCHE_APPLIED_BY_AUTHORIZED_VALUE_PATH,
    GENESIS_TRANCHE_EXPLICITLY_DEFERRED,
    ConversionCandidate,
)


def _lot(
    lot_id: str,
    *,
    amount_ecu: object = Decimal("10.5"),
    issue_epoch: int = 6,
    deadline_epoch: int = 10,
    agent_id: str = "agent-1",
    is_genesis_tranche: bool = False,
) -> dict[str, object]:
    return {
        "agent_id": agent_id,
        "amount_ecu": amount_ecu,
        "deadline_epoch": deadline_epoch,
        "is_genesis_tranche": is_genesis_tranche,
        "issue_epoch": issue_epoch,
        "lot_id": lot_id,
    }


def _state(*lots: dict[str, object]) -> dict[str, object]:
    return {"lots": list(lots)}


def _generate(monkeypatch: pytest.MonkeyPatch, *lots: dict[str, object], current_epoch: int = 10):
    monkeypatch.setattr(runtime, "CONVERSION_CANDIDATE_RUNTIME_NOT_ACTIVATED", False)
    return runtime.generate_conversion_candidates(_state(*lots), current_epoch=current_epoch)


def test_guard_is_true_by_default() -> None:
    assert runtime.CONVERSION_CANDIDATE_RUNTIME_NOT_ACTIVATED is True


def test_cdl048_deadline_constant_is_public_profile_local() -> None:
    assert runtime.MANDATORY_CONVERSION_EPOCHS_CDL048 == 4
    source = Path(runtime.__file__).read_text(encoding="utf-8")
    assert "cdl048_conversion_sweeper_runtime" not in source


def test_generator_raises_when_guard_is_true() -> None:
    with pytest.raises(ValueError, match="conversion_candidate_runtime_not_activated"):
        runtime.generate_conversion_candidates(_state(_lot("lot-a")), current_epoch=10)


def test_generator_is_deterministic(monkeypatch: pytest.MonkeyPatch) -> None:
    lots = (_lot("lot-b"), _lot("lot-a", amount_ecu="2"))
    first = _generate(monkeypatch, *lots, current_epoch=10)
    second = _generate(monkeypatch, *lots, current_epoch=10)
    assert [candidate.to_canonical_record() for candidate in first] == [
        candidate.to_canonical_record() for candidate in second
    ]


def test_deadline_boundary_lot_is_included(monkeypatch: pytest.MonkeyPatch) -> None:
    candidates = _generate(monkeypatch, _lot("lot-boundary", deadline_epoch=10), current_epoch=10)
    assert [candidate.lot_id for candidate in candidates] == ["lot-boundary"]


def test_future_deadline_lot_is_not_included(monkeypatch: pytest.MonkeyPatch) -> None:
    candidates = _generate(monkeypatch, _lot("lot-future", deadline_epoch=11), current_epoch=10)
    assert candidates == []


def test_past_deadline_lot_is_included(monkeypatch: pytest.MonkeyPatch) -> None:
    candidates = _generate(
        monkeypatch,
        _lot("lot-past", issue_epoch=1, deadline_epoch=5),
        current_epoch=15,
    )
    assert [candidate.lot_id for candidate in candidates] == ["lot-past"]


def test_nan_amount_raises_non_finite(monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(ValueError, match="non_finite"):
        _generate(monkeypatch, _lot("lot-nan", amount_ecu=Decimal("NaN")))


def test_infinite_amount_raises_non_finite(monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(ValueError, match="non_finite"):
        _generate(monkeypatch, _lot("lot-infinity", amount_ecu=Decimal("Infinity")))


def test_float_amount_raises_exact_token(monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(ValueError, match="ecu_amount_must_be_decimal_not_float"):
        _generate(monkeypatch, _lot("lot-float", amount_ecu=3.14))


def test_genesis_tranche_lot_gets_authorized_value_path_treatment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    candidates = _generate(
        monkeypatch,
        _lot("lot-genesis", is_genesis_tranche=True),
    )
    assert candidates[0].genesis_tranche_treatment == (
        GENESIS_TRANCHE_APPLIED_BY_AUTHORIZED_VALUE_PATH
    )


def test_non_genesis_lot_gets_explicit_deferred_treatment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    candidates = _generate(monkeypatch, _lot("lot-normal"))
    assert candidates[0].genesis_tranche_treatment == GENESIS_TRANCHE_EXPLICITLY_DEFERRED


def test_candidates_use_cdl057_absent_token(monkeypatch: pytest.MonkeyPatch) -> None:
    candidates = _generate(monkeypatch, _lot("lot-a"), _lot("lot-b"))
    assert {candidate.cdl057_witness_ref for candidate in candidates} == {
        CDL057_WITNESS_ABSENT_TOKEN
    }


def test_candidates_use_phase_source(monkeypatch: pytest.MonkeyPatch) -> None:
    candidates = _generate(monkeypatch, _lot("lot-a"), _lot("lot-b"))
    assert {candidate.candidate_source for candidate in candidates} == {
        runtime.CONVERSION_CANDIDATE_SOURCE
    }


def test_detect_omission_returns_missing_candidates(monkeypatch: pytest.MonkeyPatch) -> None:
    expected = _generate(monkeypatch, _lot("lot-a"), _lot("lot-b"), _lot("lot-c"))
    checkpoint = [expected[0], expected[2]]
    missing = runtime.detect_omission(expected, checkpoint)
    assert [candidate.lot_id for candidate in missing] == ["lot-b"]


def test_detect_omission_returns_empty_when_checkpoint_complete(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expected = _generate(monkeypatch, _lot("lot-a"), _lot("lot-b"))
    assert runtime.detect_omission(expected, list(reversed(expected))) == []


def test_generator_output_is_sorted_by_lot_id(monkeypatch: pytest.MonkeyPatch) -> None:
    candidates = _generate(
        monkeypatch,
        _lot("lot-c"),
        _lot("lot-a"),
        _lot("lot-b"),
    )
    assert [candidate.lot_id for candidate in candidates] == ["lot-a", "lot-b", "lot-c"]


def test_conversion_candidate_schema_uses_amount_ecu_field(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    candidate = _generate(monkeypatch, _lot("lot-amount", amount_ecu="7.25"))[0]
    assert isinstance(candidate, ConversionCandidate)
    assert candidate.amount_ecu == Decimal("7.25")
    assert not hasattr(candidate, "ecu_amount")
