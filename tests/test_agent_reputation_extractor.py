from __future__ import annotations

import inspect
from decimal import Decimal

import pytest

from ilc_core.consensus.reputation import REPUTATION_SCORE_QUANTUM
from ilc_core.economics import agent_reputation_extractor as extractor
from ilc_core.economics.agent_reputation_extractor import (
    DEPLOYMENT_EFFICIENCY_REQUIRES_CDL_107_TOKEN,
    PRODUCTION_REPUTATION_EXTRACTOR_NOT_ACTIVATED_TOKEN,
    AgentReputationRecord,
    canonical_agent_reputation_records_json,
    compute_agent_reputation_root,
    extract_agent_reputation_record,
    require_production_reputation_extractor_activation,
)


AGENT_A = "a" * 96
AGENT_B = "b" * 96


def _evidence(*, agent_id: str = AGENT_A, epoch: int = 10) -> dict[str, object]:
    return {
        "agent_id": agent_id,
        "epoch": epoch,
        "graph_snapshot_evidence": {
            "snapshot_id": "graph-snapshot-10",
            "node_count": 3,
            "edge_count": 2,
        },
        "lifecycle_evidence": {
            "last_active_epoch": 9,
            "trust_vector": {
                "accuracy": "0.80",
                "precision": "0.70",
                "potential": "0.20",
            },
        },
        "liveness_evidence": {
            "stake": "400",
            "consecutive_missed_epochs": 0,
            "equivocation_state": False,
        },
        "equivocation_evidence": {
            "equivocation_state": False,
            "evidence_count": 0,
        },
        "sybil_evidence": {
            "unresolved_sybil_risk": False,
            "advisory_cluster_risk": "0.10",
        },
        "attribution_evidence": {
            "backward_attribution_batch_root": "c" * 64,
            "credited_paths": 2,
        },
    }


def _record(**overrides: object) -> AgentReputationRecord:
    payload = _evidence()
    payload.update(overrides)
    return extract_agent_reputation_record(**payload)


def test_extract_single_agent_record_returns_valid_dataclass() -> None:
    record = _record()

    assert isinstance(record, AgentReputationRecord)
    assert record.agent_id == AGENT_A
    assert record.epoch == 10
    assert record.reputation_score == Decimal("0.847000000000")
    assert record.eligibility_flags == {
        "panel_eligible": True,
        "validator_tier_candidate": True,
        "validator_tier_official": False,
        "validator_tier_provisional": False,
    }
    assert record.to_canonical_record()["reputation_score"] == "0.847"


def test_reputation_score_is_decimal_quantized_to_quantum() -> None:
    record = _record(
        lifecycle_evidence={
            "last_active_epoch": 10,
            "trust_vector": {
                "accuracy": "0.3333333333333",
                "precision": "0.2222222222222",
                "potential": "0.1111111111111",
            },
        }
    )

    assert isinstance(record.reputation_score, Decimal)
    assert record.reputation_score == record.reputation_score.quantize(REPUTATION_SCORE_QUANTUM)


def test_non_finite_decimal_rejected_at_input_boundary() -> None:
    with pytest.raises(ValueError, match="invalid_amount_non_finite"):
        _record(
            lifecycle_evidence={
                "last_active_epoch": 10,
                "trust_vector": {
                    "accuracy": Decimal("NaN"),
                    "precision": "0.70",
                    "potential": "0.20",
                },
            }
        )


def test_float_input_rejected() -> None:
    with pytest.raises(ValueError, match="lifecycle_accuracy_must_be_unit_decimal"):
        _record(
            lifecycle_evidence={
                "last_active_epoch": 10,
                "trust_vector": {
                    "accuracy": 0.80,
                    "precision": "0.70",
                    "potential": "0.20",
                },
            }
        )


def test_compute_reputation_root_deterministic_across_ordering() -> None:
    first = _record(agent_id=AGENT_A)
    second = _record(agent_id=AGENT_B)

    assert compute_agent_reputation_root([first, second]) == compute_agent_reputation_root(
        [second, first]
    )


def test_compute_reputation_root_changes_with_different_records() -> None:
    first = _record(agent_id=AGENT_A)
    changed = _record(
        agent_id=AGENT_A,
        lifecycle_evidence={
            "last_active_epoch": 10,
            "trust_vector": {
                "accuracy": "0.81",
                "precision": "0.70",
                "potential": "0.20",
            },
        },
    )

    assert compute_agent_reputation_root([first]) != compute_agent_reputation_root([changed])


def test_canonical_record_uses_sort_keys_and_compact_separators() -> None:
    source = inspect.getsource(extractor)
    assert "sort_keys=True" in source
    assert 'separators=(",", ":")' in source
    rendered = canonical_agent_reputation_records_json([_record()])
    assert " " not in rendered
    assert '"agent_id":"' in rendered


def test_production_guard_raises() -> None:
    with pytest.raises(ValueError, match=PRODUCTION_REPUTATION_EXTRACTOR_NOT_ACTIVATED_TOKEN):
        require_production_reputation_extractor_activation()


def test_equivocation_zeroes_advisory_eligibility_flags() -> None:
    record = _record(
        liveness_evidence={
            "stake": "400",
            "consecutive_missed_epochs": 0,
            "equivocation_state": True,
        },
        equivocation_evidence={
            "equivocation_state": True,
            "evidence_count": 1,
        },
    )

    assert record.eligibility_flags == {
        "panel_eligible": False,
        "validator_tier_candidate": False,
        "validator_tier_official": False,
        "validator_tier_provisional": False,
    }


def test_unresolved_sybil_risk_zeroes_advisory_eligibility_flags() -> None:
    record = _record(
        sybil_evidence={
            "unresolved_sybil_risk": True,
            "advisory_cluster_risk": "0.90",
        }
    )

    assert record.eligibility_flags["panel_eligible"] is False
    assert record.eligibility_flags["validator_tier_candidate"] is False


def test_duplicate_agent_ids_rejected_for_epoch_root() -> None:
    with pytest.raises(ValueError, match="duplicate_agent_id"):
        compute_agent_reputation_root([_record(), _record()])


def test_empty_agent_reputation_root_rejected() -> None:
    with pytest.raises(ValueError, match="agent_reputation_root_requires_records"):
        compute_agent_reputation_root([])


def test_deployment_efficiency_is_cdl_107_gated() -> None:
    with pytest.raises(ValueError, match=DEPLOYMENT_EFFICIENCY_REQUIRES_CDL_107_TOKEN):
        _record(deployment_efficiency="0.50")


def test_equivocation_detected_alias_branch_is_supported() -> None:
    record = _record(
        liveness_evidence={
            "stake": "400",
            "consecutive_missed_epochs": 0,
            "equivocation_state": True,
        },
        equivocation_evidence={
            "equivocation_detected": True,
            "evidence_count": 1,
        },
    )

    assert record.eligibility_flags["panel_eligible"] is False


def test_liveness_stake_passed_downstream_as_parsed_decimal(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: dict[str, object] = {}

    def fake_validate(stake: object, missed_epochs: int, equivocation_state: bool) -> dict[str, object]:
        seen["stake"] = stake
        seen["missed_epochs"] = missed_epochs
        seen["equivocation_state"] = equivocation_state
        return {"status": "active"}

    monkeypatch.setattr(extractor, "validate_staking_and_liveness_state", fake_validate)

    _record()

    assert seen == {
        "stake": Decimal("400"),
        "missed_epochs": 0,
        "equivocation_state": False,
    }


def test_reputation_atrophy_grace_boundary_is_stable() -> None:
    grace_record = _record(
        epoch=1450,
        lifecycle_evidence={
            "last_active_epoch": 10,
            "trust_vector": {
                "accuracy": "0.80",
                "precision": "0.70",
                "potential": "0.20",
            },
        },
    )
    decayed_record = _record(
        epoch=1451,
        lifecycle_evidence={
            "last_active_epoch": 10,
            "trust_vector": {
                "accuracy": "0.80",
                "precision": "0.70",
                "potential": "0.20",
            },
        },
    )

    assert grace_record.reputation_score == Decimal("0.847000000000")
    assert decayed_record.reputation_score < grace_record.reputation_score


def test_analysis_grade_node_value_kernel_not_imported() -> None:
    source = inspect.getsource(extractor)
    assert "node_value_kernel" not in source
