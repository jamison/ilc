from __future__ import annotations

import ast
import json
from decimal import Decimal
from pathlib import Path

import pytest

import ilc_core.protocol.governance_weighted_decision as runtime
from ilc_core.protocol import (
    CDL_013_GOVERNANCE_WEIGHT_LIVE_INTEGRATION_TOKEN,
    COMPUTE_GOVERNANCE_WEIGHTS_IN_CALL_PATH_TOKEN,
    GOVERNANCE_WEIGHT_OUTPUT_WIRED_DECISION_SURFACES_TOKEN,
    GOVERNANCE_WEIGHTED_DECISION_RUNTIME_VERSION,
    LEGACY_FLOAT_CONVERSION_GUARD_TOKEN,
    PRODUCTION_GOVERNANCE_DECISION_ACTIVATION_TOKEN,
    PRODUCTION_GOVERNANCE_DECISIONS_NOT_ACTIVATED_TOKEN,
    build_governance_weighted_decision_quote,
    require_production_governance_decision_activation,
)


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "ilc_core/protocol/governance_weighted_decision.py"
PROMPT = (
    ROOT
    / "docs/antigravity_tasks/antigravity_prompt__phase_1356_g8_cdl_013_governance_weight_live_integration.md"
)
WALKTHROUGH = (
    ROOT / "docs/phases/phase_1356_cdl_013_governance_weight_live_integration_walkthrough.md"
)
STATUS = ROOT / "docs/phases/STATUS.md"
INDEX = ROOT / "docs/PLANNING_INDEX.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _imports_module(path: Path, module_name: str) -> bool:
    tree = ast.parse(_read(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(alias.name == module_name for alias in node.names):
                return True
        if isinstance(node, ast.ImportFrom) and node.module == module_name:
            return True
    return False


def _governance_weight_inputs() -> list[dict[str, object]]:
    return [
        {
            "agent_id": "agent-a",
            "base_weight": 1,
            "quality_score": 1,
            "inactivity_epochs": 0,
            "is_genesis": False,
            "contribution_bonus": 0,
        },
        {
            "agent_id": "agent-b",
            "base_weight": 1,
            "quality_score": 1,
            "inactivity_epochs": 0,
            "is_genesis": False,
            "contribution_bonus": 0,
        },
    ]


def test_phase_1356_decision_quote_invokes_compute_governance_weights(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[dict[str, object]] = []

    def fake_compute_governance_weights(inputs: object, *, policy: object) -> list[dict[str, object]]:
        calls.append({"inputs": list(inputs), "policy": policy})  # type: ignore[arg-type]
        return [
            {"agent_id": "agent-a", "governance_weight": 0.75, "vote_share": 0.75},
            {"agent_id": "agent-b", "governance_weight": 0.25, "vote_share": 0.25},
        ]

    monkeypatch.setattr(
        runtime.governance_weight_module,
        "compute_governance_weights",
        fake_compute_governance_weights,
    )

    quote = build_governance_weighted_decision_quote(
        proposal_id="a" * 64,
        decision_epoch=1356,
        governance_weight_inputs=_governance_weight_inputs(),
        votes=[
            {"agent_id": "agent-a", "vote": "approve"},
            {"agent_id": "agent-b", "vote": "reject"},
        ],
    )

    assert calls
    assert quote.runtime_version == GOVERNANCE_WEIGHTED_DECISION_RUNTIME_VERSION
    assert quote.integration_token == CDL_013_GOVERNANCE_WEIGHT_LIVE_INTEGRATION_TOKEN
    assert quote.decision_surface_token == GOVERNANCE_WEIGHT_OUTPUT_WIRED_DECISION_SURFACES_TOKEN
    assert quote.compute_call_token == COMPUTE_GOVERNANCE_WEIGHTS_IN_CALL_PATH_TOKEN
    assert quote.legacy_float_conversion_guard_token == LEGACY_FLOAT_CONVERSION_GUARD_TOKEN
    assert quote.approval_governance_weight == Decimal("0.75")
    assert quote.rejection_governance_weight == Decimal("0.25")
    assert quote.approval_vote_share == Decimal("0.75")
    assert quote.rejection_vote_share == Decimal("0.25")
    assert quote.production_governance_decisions_activated is False
    assert quote.decision_token == PRODUCTION_GOVERNANCE_DECISIONS_NOT_ACTIVATED_TOKEN


def test_phase_1356_real_legacy_output_is_decimal_normalized_and_canonical() -> None:
    quote = build_governance_weighted_decision_quote(
        proposal_id="b" * 64,
        decision_epoch=1356,
        governance_weight_inputs=_governance_weight_inputs(),
        votes=[{"agent_id": "agent-a", "vote": "approve"}],
    )

    assert all(isinstance(item.governance_weight, Decimal) for item in quote.participants)
    assert all(isinstance(item.vote_share, Decimal) for item in quote.participants)
    assert quote.total_governance_weight == Decimal("2")
    assert quote.approval_vote_share == Decimal("0.5")
    assert quote.abstain_vote_share == Decimal("0.5")

    record = json.loads(quote.to_canonical_json())
    assert record["decision_token"] == PRODUCTION_GOVERNANCE_DECISIONS_NOT_ACTIVATED_TOKEN
    assert record["approval_vote_share"] == "0.5"
    assert record["participants"] == [
        {
            "agent_id": "agent-a",
            "governance_weight": "1",
            "vote": "approve",
            "vote_share": "0.5",
        },
        {
            "agent_id": "agent-b",
            "governance_weight": "1",
            "vote": "abstain",
            "vote_share": "0.5",
        },
    ]


def test_phase_1356_guards_reject_invalid_votes_unknown_agents_and_nonfinite_outputs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with pytest.raises(ValueError, match="governance_vote_choice_invalid_phase_1356"):
        build_governance_weighted_decision_quote(
            proposal_id="c" * 64,
            decision_epoch=1356,
            governance_weight_inputs=_governance_weight_inputs(),
            votes=[{"agent_id": "agent-a", "vote": "maybe"}],
        )

    with pytest.raises(ValueError, match="governance_vote_agent_not_in_weight_output_phase_1356"):
        build_governance_weighted_decision_quote(
            proposal_id="c" * 64,
            decision_epoch=1356,
            governance_weight_inputs=_governance_weight_inputs(),
            votes=[{"agent_id": "agent-c", "vote": "approve"}],
        )

    def fake_nonfinite_outputs(inputs: object, *, policy: object) -> list[dict[str, object]]:
        return [{"agent_id": "agent-a", "governance_weight": float("nan"), "vote_share": 1.0}]

    monkeypatch.setattr(
        runtime.governance_weight_module,
        "compute_governance_weights",
        fake_nonfinite_outputs,
    )
    with pytest.raises(ValueError, match="governance_weight_output_must_be_finite_phase_1356"):
        build_governance_weighted_decision_quote(
            proposal_id="c" * 64,
            decision_epoch=1356,
            governance_weight_inputs=_governance_weight_inputs(),
            votes=[{"agent_id": "agent-a", "vote": "approve"}],
        )


def test_phase_1356_production_activation_remains_unimplemented() -> None:
    with pytest.raises(ValueError, match=PRODUCTION_GOVERNANCE_DECISIONS_NOT_ACTIVATED_TOKEN):
        require_production_governance_decision_activation()
    with pytest.raises(
        ValueError,
        match="production_governance_decision_activation_not_implemented_phase_1356",
    ):
        require_production_governance_decision_activation(
            PRODUCTION_GOVERNANCE_DECISION_ACTIVATION_TOKEN
        )


def test_phase_1356_runtime_avoids_sensitive_runtime_taboos() -> None:
    assert not _imports_module(RUNTIME, "random")
    assert "assert " not in _read(RUNTIME)
    assert "sort_keys=True" in _read(RUNTIME)
    assert "allow_nan=False" in _read(RUNTIME)


def test_phase_1356_docs_record_tokens_and_stale_path_discovery() -> None:
    required = (
        "cdl_013_governance_weight_live_integration_phase_1356.v0.1",
        "governance_weight_output_wired_decision_surfaces_phase_1356",
        "compute_governance_weights_in_call_path_phase_1356",
        "production_governance_decisions_not_activated_phase_1356",
        "ilc_core/analysis/governance_weight.py",
        "ilc_core/reputation/governance_weight.py",
    )
    for path in (PROMPT, WALKTHROUGH, STATUS, INDEX):
        text = _read(path)
        for token in required[:4]:
            assert token in text
    assert required[4] in _read(WALKTHROUGH)
    assert required[5] in _read(WALKTHROUGH)
