from __future__ import annotations

import inspect
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from ilc_core.analysis.genesis_accrual_governor import (
    compute_taper_multiplier,
    evaluate_genesis_accrual_governor,
)
from ilc_core.consensus import engine as engine_module
from ilc_core.consensus.diversity_floor_runtime import compute_max_cluster_share
from ilc_core.consensus.engine import ConsensusEngine
from ilc_core.consensus.finality_evaluator import evaluate_epoch_finality_with_diversity
from ilc_core.epoch.epoch_emission_production_path import _canonical_governor_report
from ilc_core.exceptions import GenesisAccrualGovernorError
from ilc_core.graph import EpistemicGraph
from ilc_core.server import GOSSIP_SIGNATURE_VERIFICATION_NOT_WIRED_TOKEN, create_app
from ilc_core.types import Node


def _gossip_payload() -> dict[str, object]:
    node = Node(
        id="placeholder",
        type="claim",
        content="phase_1575h_fix1_unverified_gossip",
        agent_id="agent:phase1575h:fix1",
        signature="sig:not-a-verifiable-gossip-envelope",
    )
    node.id = node.compute_canonical_id()
    return node.model_dump(mode="json")


def test_phase_1575h_fix1_legacy_gossip_endpoint_rejects_unverified_signature() -> None:
    app = create_app()
    payload = _gossip_payload()

    with TestClient(app) as client:
        response = client.post("/gossip/receive", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid Gossip"
    assert payload["id"] not in app.state.graph.nodes
    assert GOSSIP_SIGNATURE_VERIFICATION_NOT_WIRED_TOKEN == (
        "gossip_signature_verification_not_wired_phase_1575h_fix1"
    )


def test_phase_1575h_fix1_governor_reports_decimal_ratios_and_rejects_float_ratio() -> None:
    report = evaluate_genesis_accrual_governor(
        {
            "genesis_cumulative_accrual": Decimal("648000"),
            "total_cumulative_issuance": Decimal("5000000"),
        }
    )

    assert report["genesis_share_ratio"] == Decimal("0.025000000000")
    assert isinstance(report["genesis_share_ratio"], Decimal)
    assert isinstance(report["taper_multiplier"], Decimal)

    with pytest.raises(GenesisAccrualGovernorError) as exc_info:
        compute_taper_multiplier(0.01)
    assert str(exc_info.value) == "genesis_accrual_governor_invalid_genesis_share_ratio"


def test_phase_1575h_fix1_canonical_governor_report_requires_decimal_values() -> None:
    canonical = _canonical_governor_report(
        {
            "genesis_share_ratio": Decimal("0.025000000000"),
            "taper_multiplier": Decimal("0.735000000000"),
            "cap_blocked": False,
        }
    )
    assert canonical == {
        "cap_blocked": False,
        "genesis_share_ratio": "0.025",
        "taper_multiplier": "0.735",
    }

    with pytest.raises(ValueError, match="governor_ratio_must_be_decimal"):
        _canonical_governor_report(
            {
                "genesis_share_ratio": 0.025,
                "taper_multiplier": Decimal("0.735000000000"),
                "cap_blocked": False,
            }
        )


def test_phase_1575h_fix1_consensus_engine_uses_decimal_exp_ln_not_math_float() -> None:
    source = inspect.getsource(engine_module)
    assert "math.pow" not in source
    assert "math.log" not in source

    engine = ConsensusEngine(EpistemicGraph())
    node = Node(
        id="node-phase-1575h-fix1",
        type="claim",
        content="decimal engine check",
        agent_id="agent:phase1575h:fix1",
        signature="sig",
        timestamp=datetime.now(timezone.utc) - timedelta(seconds=60),
        net_stake=Decimal("2"),
    )
    assert isinstance(engine.calculate_maintenance_tax(node), Decimal)
    assert isinstance(engine.calculate_refutation_bounty(node), Decimal)

    with pytest.raises(ValueError, match="float_token"):
        engine_module._engine_coerce_decimal(1.0, "float_token")


def test_phase_1575h_fix1_finality_diversity_outputs_decimal_share() -> None:
    share = compute_max_cluster_share(
        largest_cluster_slots=Decimal("3"),
        total_panel_slots=Decimal("8"),
    )
    assert share == Decimal("0.375000000000")

    result = evaluate_epoch_finality_with_diversity(
        [
            {
                "block_hash": "block-a",
                "epoch_index": 1,
                "validator_id": "validator-a",
                "vote_weight": Decimal("0.90"),
            },
            {
                "block_hash": "block-a",
                "epoch_index": 1,
                "validator_id": "validator-b",
                "vote_weight": Decimal("0.05"),
            },
            {
                "block_hash": "block-a",
                "epoch_index": 1,
                "validator_id": "validator-c",
                "vote_weight": Decimal("0.05"),
            },
        ],
        {"numerator": 2, "denominator": 3},
        {
            "validator-a": "cluster-1",
            "validator-b": "cluster-2",
            "validator-c": "cluster-3",
        },
        {"distinct_cluster_floor": 3, "max_cluster_share_ceiling": Decimal("0.50")},
    )

    assert result["finality_status"] == "insufficient_diversity"
    assert result["max_cluster_share"] == Decimal("0.900000000000")
