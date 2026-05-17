from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Callable

import lmdb
import pytest

from ilc_core.analysis.governance_weight import compute_governance_weights
from ilc_core.economics.epoch_attribution_settle_runtime import (
    build_ejected_stake_treasury_distribution_quote,
    evaluate_ejected_stake_vote,
)
from ilc_core.epoch.allocation_distributor_runtime import build_allocation_distribution_quote
from ilc_core.epoch.ecu_price_clamp_runtime import build_ecu_price_clamp_quote
from ilc_core.epoch.fee_burn_split_runtime import build_fee_burn_split_quote
from ilc_core.epoch.treasury_governance_runtime import build_treasury_governance_quote
from ilc_core.epoch.validator_reward_pool_routing_runtime import (
    build_validator_reward_pool_routing_quote,
)
from ilc_core.exceptions import GovernanceWeightError
from ilc_core.genesis import (
    MAX_LIFETIME_INVOCATIONS,
    MAX_SUSPENSION_EPOCHS,
    GenesisInterventionRequest,
    read_genesis_intervention_counter,
    record_genesis_intervention_guardrail_invocation,
)
from ilc_core.storage.lmdb_graph_pruning_runtime import prune_lmdb_graph_tier_2_records


ROOT = Path(__file__).resolve().parents[1]

DEAD_BRANCH_RUNTIME_PATHS = (
    ROOT / "ilc_core/epoch/fee_burn_split_runtime.py",
    ROOT / "ilc_core/epoch/allocation_distributor_runtime.py",
    ROOT / "ilc_core/epoch/treasury_governance_runtime.py",
    ROOT / "ilc_core/epoch/ecu_price_clamp_runtime.py",
    ROOT / "ilc_core/epoch/validator_reward_pool_routing_runtime.py",
    ROOT / "ilc_core/economics/epoch_attribution_settle_runtime.py",
    ROOT / "ilc_core/epoch/epoch_emission_runtime.py",
    ROOT / "ilc_core/epoch/issuance_economics_integration_gate.py",
)


def _expect_invalid_amount_magnitude(call: Callable[[], object]) -> None:
    try:
        call()
    except InvalidOperation as exc:
        pytest.fail(f"raw Decimal InvalidOperation escaped: {exc}")
    except ValueError as exc:
        assert str(exc) == "invalid_amount_magnitude"
    else:
        pytest.fail("large finite Decimal was not rejected")


def test_phase_1369_fix1_large_finite_decimals_fail_before_quantize() -> None:
    huge = Decimal("1e19")

    cases: tuple[Callable[[], object], ...] = (
        lambda: build_fee_burn_split_quote(1, huge),
        lambda: build_allocation_distribution_quote(1, huge),
        lambda: build_treasury_governance_quote(1, huge, Decimal("0"), Decimal("0"), Decimal("0.91")),
        lambda: build_ecu_price_clamp_quote(1, huge),
        lambda: build_validator_reward_pool_routing_quote(
            1,
            huge,
            Decimal("0"),
            Decimal("0"),
            Decimal("0.91"),
        ),
        lambda: build_ejected_stake_treasury_distribution_quote(
            1,
            huge,
            {"agent-a": Decimal("1"), "agent-b": Decimal("1")},
            2,
            2,
        ),
        lambda: evaluate_ejected_stake_vote(huge, {"agent-a": Decimal("1")}, 1, 1),
    )

    for call in cases:
        _expect_invalid_amount_magnitude(call)


def test_phase_1369_fix1_governance_quality_score_is_unit_interval() -> None:
    with pytest.raises(GovernanceWeightError) as exc_info:
        compute_governance_weights(
            [
                {
                    "agent_id": "agent-a",
                    "base_weight": Decimal("1"),
                    "quality_score": Decimal("1.000000001"),
                    "inactivity_epochs": 0,
                    "is_genesis": False,
                    "contribution_bonus": Decimal("0"),
                }
            ]
        )

    assert str(exc_info.value) == "governance_weight_invalid_quality_score"


def _request(proposal_id: str, *, epoch: int = 12) -> GenesisInterventionRequest:
    return GenesisInterventionRequest(
        proposal_id=proposal_id,
        proposal_content_hash=f"sha256:{proposal_id}",
        trigger_type="canonical_genesis_lineage_severance",
        invocation_epoch=epoch,
        expected_sunset_epoch=epoch + MAX_SUSPENSION_EPOCHS,
        ratified_artifact_or_lineage_boundary="phase_1369_fix1_test_boundary",
        cdl_v4_review_pointer="phase_1369_fix1_test_review",
        requested_by="phase_1369_fix1_test_operator",
        justification="test guardrail audit record only",
        signed_audit_record_ref="signed-audit-record-ref:phase-1369-fix1-test-only",
    )


def test_phase_1369_fix1_genesis_guardrail_counter_is_serialized_for_threads(
    tmp_path: Path,
) -> None:
    counter_path = tmp_path / "counter.json"
    audit_log_path = tmp_path / "audit.ndjson"

    def invoke(index: int) -> tuple[str, int | str]:
        try:
            audit = record_genesis_intervention_guardrail_invocation(
                request=_request(f"proposal-{index}"),
                counter_path=counter_path,
                audit_log_path=audit_log_path,
                diagnostic_timestamp=f"2026-05-17T00:00:{index:02d}+00:00",
            )
            return ("accepted", audit.counter_after)
        except ValueError as exc:
            return ("rejected", str(exc))

    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(invoke, range(8)))

    accepted = [value for status, value in results if status == "accepted"]
    rejected = [value for status, value in results if status == "rejected"]
    records = [
        json.loads(line)
        for line in audit_log_path.read_text(encoding="utf-8").splitlines()
    ]

    assert sorted(accepted) == list(range(1, MAX_LIFETIME_INVOCATIONS + 1))
    assert len(rejected) == 8 - MAX_LIFETIME_INVOCATIONS
    assert set(rejected) == {"genesis_intervention_max_invocations_exceeded"}
    assert read_genesis_intervention_counter(counter_path).lifetime_invocations == 3
    assert len(records) == 8
    assert sum(1 for record in records if record["accepted"] is True) == 3


def _put_json(env: lmdb.Environment, db: lmdb._Database, key: str, payload: dict[str, object]) -> None:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    with env.begin(write=True, db=db) as txn:
        txn.put(key.encode("utf-8"), encoded)


def test_phase_1369_fix1_lmdb_batch_cap_counts_prunable_records(tmp_path: Path) -> None:
    env = lmdb.open(str(tmp_path), max_dbs=1, map_size=1024 * 1024)
    db = env.open_db(b"nodes")
    try:
        for index in range(2):
            _put_json(
                env,
                db,
                f"a-non-tier-{index}",
                {
                    "id": f"a-non-tier-{index}",
                    "temporal_tier": "tier_3",
                    "epoch_scope": "permanent",
                    "issuance_epoch": 1,
                    "ecu_score": "0.0",
                },
            )
        _put_json(
            env,
            db,
            "z-old-low",
            {
                "id": "z-old-low",
                "temporal_tier": "tier_2",
                "epoch_scope": "issuance_epoch",
                "issuance_epoch": 1,
                "ecu_score": "0.1",
            },
        )

        result = prune_lmdb_graph_tier_2_records(
            env,
            db,
            current_issuance_epoch=5,
            minting_confirmed=True,
            dry_run=True,
            max_records_per_batch=1,
        )

        assert result["scanned"] == 3
        assert result["skipped_not_tier_2"] == 2
        assert result["planned_prune"] == 1
        assert result["deleted"] == 0
    finally:
        env.close()


def test_phase_1369_fix1_lmdb_dry_run_uses_read_transaction() -> None:
    source = (ROOT / "ilc_core/storage/lmdb_graph_pruning_runtime.py").read_text(
        encoding="utf-8"
    )

    assert "env.begin(write=not dry_run, db=db)" in source
    assert "env.begin(write=True, db=db)" not in source


def test_phase_1369_fix1_decimal_to_string_dead_branch_removed() -> None:
    for path in DEAD_BRANCH_RUNTIME_PATHS:
        source = path.read_text(encoding="utf-8")
        assert "normalized == normalized.to_integral()" not in source
        assert 'return format(value.normalize(), "f")' in source
