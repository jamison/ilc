from decimal import Decimal

import pytest

from ilc_core.capproof.capability_vector import CapabilityVector
from ilc_core.epoch import capproof_epoch_init_wiring as wiring

_AGENT_ID = "a" * 96


def _cv(
    *,
    det_pass: bool = True,
    epoch: int = 7,
    gemm: str = "100000",
    infer: str = "10000",
    bw: str = "1000",
    graph: str = "10000",
) -> CapabilityVector:
    return CapabilityVector(
        gemm_gops=Decimal(gemm),
        infer_tps=Decimal(infer),
        bw_gbps=Decimal(bw),
        graph_mteps=Decimal(graph),
        det_pass=det_pass,
        epoch=epoch,
        agent_id=_AGENT_ID,
    )


def _assert_token(excinfo: pytest.ExceptionInfo[BaseException], token: str) -> None:
    assert getattr(excinfo.value, "token", None) == token
    assert token in str(excinfo.value)


def test_default_guard_bypasses_application_path_with_neutral_result() -> None:
    result = wiring.process_capproof_epoch_init(_cv(), 7, Decimal("100"))

    assert result.protocol_executed is False
    assert result.potential_updated == Decimal("0")
    assert result.band_multiplier == Decimal("1.00")
    assert result.base_ecu_amount == Decimal("100")
    assert result.cap_adjusted_base_ecu_amount == Decimal("100")
    assert result.conservation_check_passed is True
    assert result.runtime_version == wiring.CAPPROOF_EPOCH_INIT_RUNTIME_VERSION
    assert result.activation_guard == "capproof_epoch_wiring_not_activated_phase_1607"
    assert result.epoch_seal_token == "capproof_epoch_wiring_bypassed_7"


def test_guard_cleared_runs_full_six_step_flow(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(wiring, "CAPPROOF_EPOCH_WIRING_NOT_ACTIVATED", False)
    monkeypatch.setattr(
        wiring.probe_runner,
        "CAPPROOF_DETERMINISM_PROBE_PRODUCTION_ACTIVATED",
        True,
    )

    result = wiring.process_capproof_epoch_init(_cv(), 7, Decimal("100"))

    assert result.protocol_executed is True
    assert Decimal("0") <= result.potential_updated <= Decimal("1")
    assert Decimal("0.85") <= result.band_multiplier <= Decimal("1.15")
    assert result.cap_adjusted_base_ecu_amount == wiring._multiply_decimal(
        Decimal("100"),
        result.band_multiplier,
    )
    assert result.epoch_seal_token.startswith("capproof_epoch_seal_7_")


def test_epoch_mismatch_rejected_before_guard_bypass() -> None:
    with pytest.raises(wiring.CapProofEpochWiringError) as excinfo:
        wiring.process_capproof_epoch_init(_cv(epoch=6), 7, Decimal("100"))

    _assert_token(excinfo, "capproof_cv_epoch_mismatch")


def test_step3_sets_zero_potential_when_determinism_fails() -> None:
    assert wiring.step3_update_potential(_cv(det_pass=False)) == Decimal("0")


def test_step4_uses_floor_when_determinism_fails() -> None:
    assert wiring.step4_compute_band_multiplier(_cv(det_pass=False)) == Decimal("0.85")


def test_step4_high_metrics_remain_bounded_by_ceil() -> None:
    band = wiring.step4_compute_band_multiplier(
        _cv(gemm="999999999", infer="999999999", bw="999999999", graph="999999999")
    )

    assert band <= Decimal("1.15")


def test_conservation_rejects_band_below_floor() -> None:
    with pytest.raises(wiring.CapProofEpochWiringError) as excinfo:
        wiring.step5_conservation_check(Decimal("100"), Decimal("84"), Decimal("0.84"))

    _assert_token(excinfo, "capproof_conservation_check_failed_band_out_of_range")


def test_conservation_rejects_amount_mismatch() -> None:
    with pytest.raises(wiring.CapProofEpochWiringError) as excinfo:
        wiring.step5_conservation_check(Decimal("100"), Decimal("100"), Decimal("1.01"))

    _assert_token(excinfo, "capproof_conservation_check_failed_amount_mismatch")


def test_result_constructor_enforces_conservation_when_flag_is_true() -> None:
    with pytest.raises(wiring.CapProofEpochWiringError) as excinfo:
        wiring.CapProofEpochInitResult(
            agent_id=_AGENT_ID,
            epoch=7,
            protocol_executed=True,
            potential_updated=Decimal("0.5"),
            band_multiplier=Decimal("1.15"),
            base_ecu_amount=Decimal("100"),
            cap_adjusted_base_ecu_amount=Decimal("100"),
            conservation_check_passed=True,
            epoch_seal_token="seal",
            det_pass=True,
        )

    _assert_token(excinfo, "capproof_conservation_check_failed_amount_mismatch")


def test_executed_result_cannot_claim_failed_conservation() -> None:
    with pytest.raises(wiring.CapProofEpochWiringError) as excinfo:
        wiring.CapProofEpochInitResult(
            agent_id=_AGENT_ID,
            epoch=7,
            protocol_executed=True,
            potential_updated=Decimal("0.5"),
            band_multiplier=Decimal("1.00"),
            base_ecu_amount=Decimal("100"),
            cap_adjusted_base_ecu_amount=Decimal("100"),
            conservation_check_passed=False,
            epoch_seal_token="seal",
            det_pass=True,
        )

    _assert_token(excinfo, "capproof_wiring_executed_result_requires_conservation_pass")


def test_result_rejects_potential_outside_unit_interval() -> None:
    with pytest.raises(wiring.CapProofEpochWiringError) as excinfo:
        wiring.CapProofEpochInitResult(
            agent_id=_AGENT_ID,
            epoch=7,
            protocol_executed=False,
            potential_updated=Decimal("1.01"),
            band_multiplier=Decimal("1.00"),
            base_ecu_amount=Decimal("100"),
            cap_adjusted_base_ecu_amount=Decimal("100"),
            conservation_check_passed=True,
            epoch_seal_token="seal",
            det_pass=True,
        )

    _assert_token(excinfo, "capproof_wiring_potential_out_of_unit_interval")


def test_result_rejects_runtime_version_mismatch() -> None:
    with pytest.raises(wiring.CapProofEpochWiringError) as excinfo:
        wiring.CapProofEpochInitResult(
            agent_id=_AGENT_ID,
            epoch=7,
            protocol_executed=False,
            potential_updated=Decimal("0"),
            band_multiplier=Decimal("1.00"),
            base_ecu_amount=Decimal("100"),
            cap_adjusted_base_ecu_amount=Decimal("100"),
            conservation_check_passed=True,
            epoch_seal_token="seal",
            det_pass=True,
            runtime_version="old-version",
        )

    _assert_token(excinfo, "capproof_wiring_runtime_version_mismatch")


def test_activation_guard_token_present_in_executed_result(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(wiring, "CAPPROOF_EPOCH_WIRING_NOT_ACTIVATED", False)
    monkeypatch.setattr(
        wiring.probe_runner,
        "CAPPROOF_DETERMINISM_PROBE_PRODUCTION_ACTIVATED",
        True,
    )

    result = wiring.process_capproof_epoch_init(_cv(), 7, Decimal("100"))

    assert result.activation_guard == "capproof_epoch_wiring_not_activated_phase_1607"


def test_guard_clear_fails_closed_until_determinism_probe_is_production_ready(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(wiring, "CAPPROOF_EPOCH_WIRING_NOT_ACTIVATED", False)
    monkeypatch.setattr(
        wiring.probe_runner,
        "CAPPROOF_DETERMINISM_PROBE_PRODUCTION_ACTIVATED",
        False,
    )

    with pytest.raises(wiring.CapProofEpochWiringError) as excinfo:
        wiring.process_capproof_epoch_init(_cv(), 7, Decimal("100"))

    _assert_token(excinfo, "capproof_determinism_probe_not_production_ready")


def test_step3_and_step4_are_inverse_inside_band() -> None:
    cv = _cv()
    potential = wiring.step3_update_potential(cv)
    band = wiring.step4_compute_band_multiplier(cv)

    assert potential == (band - wiring.CAPPROOF_BAND_FLOOR) / (
        wiring.CAPPROOF_BAND_CEIL - wiring.CAPPROOF_BAND_FLOOR
    )


def test_epoch_seal_is_deterministic() -> None:
    first = wiring.step6_seal_epoch(_AGENT_ID, 7, Decimal("1.00"), Decimal("100"))
    second = wiring.step6_seal_epoch(_AGENT_ID, 7, Decimal("1.00"), Decimal("100"))

    assert first == second
    assert first.startswith("capproof_epoch_seal_7_")


def test_no_ilc_mint_invariant_is_reasserted(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(wiring, "CAPPROOF_V1_NO_ILC_MINT", False)

    with pytest.raises(wiring.CapProofEpochWiringError) as excinfo:
        wiring.step4_compute_band_multiplier(_cv())

    _assert_token(excinfo, "capproof_no_ilc_mint_invariant_violated")


def test_step2_does_not_reject_false_determinism() -> None:
    assert wiring.step2_verify_probe(_cv(det_pass=False)) is True


def test_non_decimal_base_amount_rejected() -> None:
    with pytest.raises(wiring.CapProofEpochWiringError) as excinfo:
        wiring.process_capproof_epoch_init(_cv(), 7, 100)  # type: ignore[arg-type]

    _assert_token(excinfo, "capproof_wiring_base_ecu_amount_must_be_decimal")


def test_non_finite_internal_decimal_rejected_by_boundary() -> None:
    with pytest.raises(wiring.CapProofEpochWiringError) as excinfo:
        wiring._clamp_unit(Decimal("NaN"))

    _assert_token(excinfo, "capproof_wiring_unit_value_must_be_finite")
