from __future__ import annotations

import ast
from decimal import Decimal
from pathlib import Path

import ilc_core.analysis.governance_weight as governance_weight
import ilc_core.consensus.reputation as reputation
from ilc_core.protocol.governance_weighted_decision import (
    EMPTY_GOVERNANCE_PARTICIPANT_SET_REGRESSION_TOKEN,
    GOVERNANCE_WEIGHT_DECIMAL_REWRITE_CLOSED_TOKEN,
    NONFINITE_FLOAT_INF_NEGATIVE_INF_REGRESSION_TOKEN,
)


ROOT = Path(__file__).resolve().parents[1]
PROMPT = (
    ROOT
    / "docs/antigravity_tasks/antigravity_prompt__phase_1357_g8_reputation_py_h11_float_kill_decimal_rewrite.md"
)
GOVERNANCE_WEIGHT = ROOT / "ilc_core/analysis/governance_weight.py"
CONSENSUS_REPUTATION = ROOT / "ilc_core/consensus/reputation.py"
TEMPORAL_DECAY = ROOT / "ilc_core/reputation/temporal_decay_runtime.py"
ROUTING_REPUTATION = ROOT / "ilc_core/network/d2d/routing_reputation_runtime.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _ast_has_runtime_float_surface(path: Path) -> bool:
    tree = ast.parse(_read(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, float):
            return True
        if isinstance(node, ast.Name) and node.id == "float":
            return True
        if isinstance(node, ast.Attribute) and node.attr in {"exp", "log", "isfinite"}:
            if isinstance(node.value, ast.Name) and node.value.id == "math":
                return True
    return False


def test_phase_1357_tokens_are_committed() -> None:
    assert reputation.REPUTATION_RUNTIME_VERSION == "reputation_runtime_h11_float_kill_1357.v0.1"
    assert reputation.REPUTATION_RUNTIME_VERSION_TOKEN == "REPUTATION_RUNTIME_VERSION_token_phase_1357"
    assert reputation.REPUTATION_RUNTIME_H11_FLOAT_KILL_TOKEN == (
        "reputation_runtime_h11_float_kill_phase_1357.v0.1"
    )
    assert reputation.REPUTATION_NO_FLOAT_ARITHMETIC_TOKEN == (
        "reputation_no_float_arithmetic_phase_1357"
    )
    assert governance_weight.CDL_013_DEPENDENCY_TOKEN == "CDL_013_DEPENDENCY_token_phase_1357"
    assert governance_weight.GOVERNANCE_WEIGHT_NO_FLOAT_ARITHMETIC_TOKEN == (
        "governance_weight_no_float_arithmetic_phase_1357"
    )
    assert GOVERNANCE_WEIGHT_DECIMAL_REWRITE_CLOSED_TOKEN == (
        "governance_weight_vote_share_precision_gap_closed_phase_1357"
    )
    assert NONFINITE_FLOAT_INF_NEGATIVE_INF_REGRESSION_TOKEN == (
        "nonfinite_float_inf_negative_inf_regression_phase_1357"
    )
    assert EMPTY_GOVERNANCE_PARTICIPANT_SET_REGRESSION_TOKEN == (
        "empty_governance_participant_set_regression_phase_1357"
    )


def test_h11_in_scope_runtime_files_have_no_runtime_float_surface() -> None:
    for path in (GOVERNANCE_WEIGHT, CONSENSUS_REPUTATION, TEMPORAL_DECAY):
        assert not _ast_has_runtime_float_surface(path), path


def test_routing_reputation_is_explicitly_deferred_because_cdl_060_is_float_contract() -> None:
    text = _read(PROMPT)
    routing_text = _read(ROUTING_REPUTATION)
    assert "SERVE_CENTRALITY_DELTA" in routing_text
    assert "accumulate_centrality_delta" in routing_text
    assert "routing_reputation_decimal_rewrite_deferred_pending_cdl_060_decimal_pipeline_phase_1357" in text


def test_governance_weight_outputs_decimal_exact_three_agent_shares() -> None:
    outputs = governance_weight.compute_governance_weights(
        [
            {
                "agent_id": agent_id,
                "base_weight": Decimal("1"),
                "quality_score": Decimal("1"),
                "inactivity_epochs": 0,
                "is_genesis": False,
                "contribution_bonus": Decimal("0"),
            }
            for agent_id in ("a", "b", "c")
        ]
    )

    assert all(isinstance(row["governance_weight"], Decimal) for row in outputs)
    assert all(isinstance(row["vote_share"], Decimal) for row in outputs)
    assert sum((row["vote_share"] for row in outputs), Decimal("0")) == Decimal("1")


def test_reputation_atrophy_does_not_mutate_caller_state() -> None:
    agent_state = {
        "last_active_epoch": 0,
        "trust_vector": {"accuracy": Decimal("1"), "precision": Decimal("1")},
    }

    updated = reputation.apply_atrophy(agent_state, reputation.ATROPHY_HALF_LIFE_EPOCHS)

    assert updated is not agent_state
    assert updated["trust_vector"] is not agent_state["trust_vector"]
    assert agent_state["trust_vector"]["accuracy"] == Decimal("1")
    assert updated["trust_vector"]["accuracy"] == Decimal("0.500000000000")
