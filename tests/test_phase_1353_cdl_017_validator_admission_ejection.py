from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from ilc_core.identity.agent_id_runtime import derive_agent_id_v2
from ilc_core.validator import (
    ADMIT_VALIDATOR_PRODUCTION_IMPL_TOKEN,
    CDL_017_VALIDATOR_ADMISSION_EJECTION_RUNTIME_TOKEN,
    EJECT_VALIDATOR_PRODUCTION_IMPL_TOKEN,
    GENESIS_STAKE_AMOUNT,
    LIVENESS_MISS_THRESHOLD,
    LIVENESS_PENALTY_FRACTION,
    PRODUCTION_VALIDATOR_ADMISSION_NOT_ACTIVATED_TOKEN,
    SEC_004_TRANSFER_CERTIFICATE_EPOCH_BINDING_TOKEN,
    VALIDATOR_ADMISSION_EJECTION_RUNTIME_VERSION,
    VALIDATOR_SET_ROTATION_WIRED_FAST_PATH_TOKEN,
    admit_validator,
    eject_validator,
    require_production_validator_admission_activation,
)


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "ilc_core/validator/admission_ejection_runtime.py"
FAST_PATH = ROOT / "ilc_consensus/src/fast_path.rs"
PROMPT = (
    ROOT
    / "docs/antigravity_tasks/antigravity_prompt__phase_1353_g8_cdl_017_validator_admission_ejection_sec_004_wiring.md"
)
WALKTHROUGH = (
    ROOT
    / "docs/phases/phase_1353_cdl_017_validator_admission_ejection_sec_004_wiring_walkthrough.md"
)
STATUS = ROOT / "docs/phases/STATUS.md"
INDEX = ROOT / "docs/PLANNING_INDEX.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _agent_id(seed_byte: int = 7) -> str:
    return derive_agent_id_v2(bytes([seed_byte]) * 32)


def test_phase_1353_admit_validator_returns_default_off_rotation_decision() -> None:
    decision = admit_validator(
        current_epoch=10,
        active_from_epoch=11,
        current_validator_ids=[3, 1, 2],
        validator_id=4,
        agent_id=_agent_id(),
        stake_ecu=Decimal("400"),
    )

    assert decision.runtime_version == VALIDATOR_ADMISSION_EJECTION_RUNTIME_VERSION
    assert decision.admission_token == ADMIT_VALIDATOR_PRODUCTION_IMPL_TOKEN
    assert decision.decision_token == PRODUCTION_VALIDATOR_ADMISSION_NOT_ACTIVATED_TOKEN
    assert decision.sec_004_epoch_binding_token == SEC_004_TRANSFER_CERTIFICATE_EPOCH_BINDING_TOKEN
    assert decision.rotation_token == VALIDATOR_SET_ROTATION_WIRED_FAST_PATH_TOKEN
    assert decision.current_validator_ids == (1, 2, 3)
    assert decision.next_validator_ids == (1, 2, 3, 4)
    assert decision.production_validator_admission_activated is False
    assert decision.stake_ecu == GENESIS_STAKE_AMOUNT
    assert decision.to_canonical_record()["stake_ecu"] == "400"


def test_phase_1353_admit_rejects_float_non_finite_and_low_stake() -> None:
    common = {
        "current_epoch": 10,
        "active_from_epoch": 11,
        "current_validator_ids": [1, 2, 3],
        "validator_id": 4,
        "agent_id": _agent_id(),
    }

    with pytest.raises(ValueError, match="validator_stake_ecu_must_be_exact_decimal"):
        admit_validator(**common, stake_ecu=400.0)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="validator_stake_ecu_must_be_exact_decimal"):
        admit_validator(**common, stake_ecu="NaN")
    with pytest.raises(ValueError, match="validator_participation_stake_below_minimum_phase_1353"):
        admit_validator(**common, stake_ecu=Decimal("399.999999"))


def test_phase_1353_re_admission_boundary_uses_cdl_058_cooldowns() -> None:
    common = {
        "current_epoch": 20,
        "active_from_epoch": 21,
        "current_validator_ids": [1, 2, 3],
        "validator_id": 4,
        "agent_id": _agent_id(8),
        "stake_ecu": Decimal("400"),
        "prior_exit_reason": "equivocation",
    }

    with pytest.raises(ValueError, match="validator_re_admission_cooldown_active_phase_1353"):
        admit_validator(**common, epochs_since_exit=11)

    decision = admit_validator(**common, epochs_since_exit=12)
    assert decision.re_admission_cooldown_remaining == 0
    assert decision.next_validator_ids == (1, 2, 3, 4)


def test_phase_1353_eject_validator_returns_default_off_rotation_decision() -> None:
    decision = eject_validator(
        current_epoch=22,
        active_from_epoch=23,
        current_validator_ids=[4, 1, 3, 2],
        validator_id=3,
        exit_reason="liveness_miss",
        consecutive_missed_epochs=LIVENESS_MISS_THRESHOLD,
        equivocation_state=False,
    )

    assert decision.ejection_token == EJECT_VALIDATOR_PRODUCTION_IMPL_TOKEN
    assert decision.decision_token == PRODUCTION_VALIDATOR_ADMISSION_NOT_ACTIVATED_TOKEN
    assert decision.sec_004_epoch_binding_token == SEC_004_TRANSFER_CERTIFICATE_EPOCH_BINDING_TOKEN
    assert decision.rotation_token == VALIDATOR_SET_ROTATION_WIRED_FAST_PATH_TOKEN
    assert decision.current_validator_ids == (1, 2, 3, 4)
    assert decision.next_validator_ids == (1, 2, 4)
    assert decision.penalty_fraction == LIVENESS_PENALTY_FRACTION
    assert decision.re_admission_cooldown_epochs == 2
    assert decision.re_admission_not_before_epoch == 25
    assert decision.production_validator_admission_activated is False


def test_phase_1353_eject_validator_rejects_invalid_reasons_and_thresholds() -> None:
    common = {
        "current_epoch": 22,
        "active_from_epoch": 23,
        "current_validator_ids": [1, 2, 3, 4],
        "validator_id": 3,
    }

    with pytest.raises(ValueError, match="liveness_ejection_requires_threshold_phase_1353"):
        eject_validator(
            **common,
            exit_reason="liveness_miss",
            consecutive_missed_epochs=LIVENESS_MISS_THRESHOLD - 1,
        )
    with pytest.raises(ValueError, match="equivocation_exit_requires_equivocation_state_phase_1353"):
        eject_validator(**common, exit_reason="equivocation", equivocation_state=False)
    with pytest.raises(ValueError, match="validator_activation_epoch_must_be_future_phase_1353"):
        eject_validator(
            current_epoch=22,
            active_from_epoch=22,
            current_validator_ids=[1, 2, 3],
            validator_id=3,
            exit_reason="voluntary_exit",
        )


def test_phase_1353_production_activation_remains_unimplemented() -> None:
    with pytest.raises(ValueError, match=PRODUCTION_VALIDATOR_ADMISSION_NOT_ACTIVATED_TOKEN):
        require_production_validator_admission_activation()
    with pytest.raises(
        ValueError,
        match="production_validator_admission_activation_not_implemented_phase_1353",
    ):
        require_production_validator_admission_activation(
            "first_non_genesis_validator_deployment_requires_later_human_gate"
        )


def test_phase_1353_fast_path_records_sec_004_and_rotation_tokens() -> None:
    fast_path = _read(FAST_PATH)
    assert "pub const SEC_004_TRANSFER_CERTIFICATE_EPOCH_BINDING_PHASE_1353" in fast_path
    assert SEC_004_TRANSFER_CERTIFICATE_EPOCH_BINDING_TOKEN in fast_path
    assert "pub const VALIDATOR_SET_ROTATION_WIRED_FAST_PATH_PHASE_1353" in fast_path
    assert VALIDATOR_SET_ROTATION_WIRED_FAST_PATH_TOKEN in fast_path
    assert "cert: TransferCertificate" in fast_path
    assert ".range(..=cert.epoch)" in fast_path
    assert "pub fn rotate_validator_set(&self, active_from_epoch: EpochSeq" in fast_path


def test_phase_1353_docs_record_tokens_and_non_authorization() -> None:
    for path in (RUNTIME, PROMPT, WALKTHROUGH, STATUS, INDEX):
        text = _read(path)
        assert CDL_017_VALIDATOR_ADMISSION_EJECTION_RUNTIME_TOKEN in text
        assert ADMIT_VALIDATOR_PRODUCTION_IMPL_TOKEN in text
        assert EJECT_VALIDATOR_PRODUCTION_IMPL_TOKEN in text
        assert SEC_004_TRANSFER_CERTIFICATE_EPOCH_BINDING_TOKEN in text
        assert VALIDATOR_SET_ROTATION_WIRED_FAST_PATH_TOKEN in text
        assert PRODUCTION_VALIDATOR_ADMISSION_NOT_ACTIVATED_TOKEN in text

    runtime = _read(RUNTIME)
    assert "float" in runtime
    assert "Decimal" in runtime
    assert "production_validator_admission_activated=False" in runtime
