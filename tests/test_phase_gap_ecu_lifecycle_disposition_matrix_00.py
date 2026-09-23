from __future__ import annotations

import pytest

from ilc_core.ledger.ecu_lifecycle_state import (
    CLAIM_BEARING_STATES,
    CONTRIBUTION_TRANSFER_NOT_CLAIM_BEARING_TOKEN,
    ECU_LIFECYCLE_DISPOSITION_MATRIX_PARTITION_TOKEN,
    ECU_LIFECYCLE_DISPOSITION_MATRIX_VERSION,
    EcuLifecycleState,
    NON_CLAIM_BEARING_STATES,
    PAYMENT_TRANSFER_NOT_CLAIM_BEARING_TOKEN,
    is_claim_bearing,
)


def test_all_states_have_disposition() -> None:
    assert CLAIM_BEARING_STATES | NON_CLAIM_BEARING_STATES == frozenset(EcuLifecycleState)


def test_no_state_in_both_sets() -> None:
    assert CLAIM_BEARING_STATES & NON_CLAIM_BEARING_STATES == frozenset()


def test_attribution_evented_is_claim_bearing() -> None:
    assert is_claim_bearing(EcuLifecycleState.ATTRIBUTION_EVENTED) is True


@pytest.mark.parametrize(
    "state",
    [
        EcuLifecycleState.TRANSFERRED,
        EcuLifecycleState.EARMARKED,
        EcuLifecycleState.CONVERTED,
        EcuLifecycleState.EXPIRED,
        EcuLifecycleState.PROVISIONAL,
        EcuLifecycleState.QUOTED,
        EcuLifecycleState.COMMITTED,
        EcuLifecycleState.LOTIZED,
        EcuLifecycleState.CONVERSION_CANDIDATE,
    ],
)
def test_non_claim_bearing_states(state: EcuLifecycleState) -> None:
    assert is_claim_bearing(state) is False


def test_transferred_is_not_claim_bearing() -> None:
    assert is_claim_bearing(EcuLifecycleState.TRANSFERRED) is False


def test_earmarked_is_not_claim_bearing() -> None:
    assert is_claim_bearing(EcuLifecycleState.EARMARKED) is False


def test_converted_is_not_claim_bearing() -> None:
    assert is_claim_bearing(EcuLifecycleState.CONVERTED) is False


def test_expired_is_not_claim_bearing() -> None:
    assert is_claim_bearing(EcuLifecycleState.EXPIRED) is False


def test_provisional_is_not_claim_bearing() -> None:
    assert is_claim_bearing(EcuLifecycleState.PROVISIONAL) is False


def test_quoted_is_not_claim_bearing() -> None:
    assert is_claim_bearing(EcuLifecycleState.QUOTED) is False


def test_committed_is_not_claim_bearing() -> None:
    assert is_claim_bearing(EcuLifecycleState.COMMITTED) is False


def test_lotized_is_not_claim_bearing() -> None:
    assert is_claim_bearing(EcuLifecycleState.LOTIZED) is False


def test_conversion_candidate_is_not_claim_bearing() -> None:
    assert is_claim_bearing(EcuLifecycleState.CONVERSION_CANDIDATE) is False


def test_contribution_transfer_token_present() -> None:
    assert isinstance(CONTRIBUTION_TRANSFER_NOT_CLAIM_BEARING_TOKEN, str)
    assert CONTRIBUTION_TRANSFER_NOT_CLAIM_BEARING_TOKEN
    assert "GAP_ECU_LIFECYCLE_DISPOSITION_MATRIX_00" in (
        CONTRIBUTION_TRANSFER_NOT_CLAIM_BEARING_TOKEN
    )


def test_payment_transfer_token_present() -> None:
    assert isinstance(PAYMENT_TRANSFER_NOT_CLAIM_BEARING_TOKEN, str)
    assert PAYMENT_TRANSFER_NOT_CLAIM_BEARING_TOKEN


def test_version_token_present() -> None:
    assert isinstance(ECU_LIFECYCLE_DISPOSITION_MATRIX_VERSION, str)
    assert "ecu_lifecycle_disposition_matrix_GAP_ECU_LIFECYCLE_DISPOSITION_MATRIX_00" in (
        ECU_LIFECYCLE_DISPOSITION_MATRIX_VERSION
    )


def test_state_enum_string_values_are_canonical_tokens() -> None:
    for state in EcuLifecycleState:
        assert state.value.startswith("ecu_state_")
        assert not any(char.isspace() for char in state.value)


def test_is_claim_bearing_rejects_non_state() -> None:
    with pytest.raises(TypeError, match="ecu_lifecycle_state_required"):
        is_claim_bearing("attribution_evented")  # type: ignore[arg-type]


def test_partition_token_present() -> None:
    assert isinstance(ECU_LIFECYCLE_DISPOSITION_MATRIX_PARTITION_TOKEN, str)
    assert ECU_LIFECYCLE_DISPOSITION_MATRIX_PARTITION_TOKEN


def test_claim_bearing_states_exactly_attribution_evented() -> None:
    assert CLAIM_BEARING_STATES == frozenset({EcuLifecycleState.ATTRIBUTION_EVENTED})
