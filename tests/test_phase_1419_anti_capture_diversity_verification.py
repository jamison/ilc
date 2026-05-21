"""Phase 1419 anti-capture diversity verification pass tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from ilc_core.epistemic import jury_assignment_runtime as jury_runtime
from ilc_core.epistemic.jury_activation_gate import (
    GateConditionStatus,
    evaluate_jury_activation_gate,
)
from ilc_core.epistemic.jury_assignment_runtime import (
    EligibleAgent,
    JuryAssignmentError,
    quote_jury_assignment,
)

REPO = Path(__file__).resolve().parents[1]
JURY_PATH = REPO / "ilc_core/epistemic/jury_assignment_runtime.py"

RFC_B4_VECTORS = (
    {
        "public_key": bytes.fromhex(
            "d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a"
        ),
        "alpha": b"",
        "pi": bytes.fromhex(
            "7d9c633ffeee27349264cf5c667579fc583b4bda63ab71d001f89c10003ab"
            "46f14adf9a3cd8b8412d9038531e865c341cafa73589b023d14311c331a9ad15ff"
            "2fb37831e00f0acaa6d73bc9997b06501"
        ),
    },
    {
        "public_key": bytes.fromhex(
            "3d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f12af4660c"
        ),
        "alpha": bytes.fromhex("72"),
        "pi": bytes.fromhex(
            "47b327393ff2dd81336f8a2ef10339112401253b3c714eeda879f12c50907"
            "2ef055b48372bb82efbdce8e10c8cb9a2f9d60e93908f93df1623ad78a86a028d6"
            "bc064dbfc75a6a57379ef855dc6733801"
        ),
    },
    {
        "public_key": bytes.fromhex(
            "fc51cd8e6218a1a38da47ed00230f0580816ed13ba3303ac5deb911548908025"
        ),
        "alpha": bytes.fromhex("af82"),
        "pi": bytes.fromhex(
            "926e895d308f5e328e7aa159c06eddbe56d06846abf5d98c2512235eaa57f"
            "dce35b46edfc655bc828d44ad09d1150f31374e7ef73027e14760d42e77341fe05"
            "467bb286cc2c9d7fde29120a0b2320d04"
        ),
    },
)


def _make_agent(
    agent_id: str,
    *,
    cluster_id: str,
    operator_domain: str,
    outsider: bool = False,
) -> EligibleAgent:
    return EligibleAgent(
        agent_id=agent_id,
        cluster_id=cluster_id,
        operator_domain=operator_domain,
        identity_lineage_ref=f"lineage-{agent_id}",
        outsider_candidate_flag=outsider,
        capability_tier_or_lane_score="tier1",
    )


def _passing_pool() -> list[EligibleAgent]:
    return [
        _make_agent("r1", cluster_id="c1", operator_domain="op-a"),
        _make_agent("r2", cluster_id="c1", operator_domain="op-b"),
        _make_agent("r3", cluster_id="c1", operator_domain="op-c"),
        _make_agent("r4", cluster_id="c2", operator_domain="op-d"),
        _make_agent("r5", cluster_id="c2", operator_domain="op-e"),
        _make_agent("r6", cluster_id="c3", operator_domain="op-f"),
        _make_agent("r7", cluster_id="c3", operator_domain="op-g"),
        _make_agent("o1", cluster_id="c4", operator_domain="op-out", outsider=True),
    ]


def _quote_kwargs(agents: list[EligibleAgent]) -> dict[str, object]:
    return {
        "review_epoch": 1,
        "review_lane": "objective",
        "claim_or_task_id": "cid-phase-1419",
        "author_agent_id": "author",
        "author_operator_domain": "author-domain",
        "eligible_agents": agents,
    }


def _proofs_for(agents: list[EligibleAgent]) -> dict[str, dict[str, bytes]]:
    proofs: dict[str, dict[str, bytes]] = {}
    for index, agent in enumerate(agents):
        vector = RFC_B4_VECTORS[index % len(RFC_B4_VECTORS)]
        proofs[agent.agent_id] = {
            "public_key": vector["public_key"],
            "pi": vector["pi"],
        }
    return proofs


def _patch_alpha_to_rfc_vectors(monkeypatch: pytest.MonkeyPatch, agents: list[EligibleAgent]) -> None:
    alpha_by_agent = {
        agent.agent_id: RFC_B4_VECTORS[index % len(RFC_B4_VECTORS)]["alpha"]
        for index, agent in enumerate(agents)
    }

    def fixture_alpha(*, agent: EligibleAgent, **_kwargs: object) -> bytes:
        return alpha_by_agent[agent.agent_id]

    monkeypatch.setattr(jury_runtime, "_canonical_vrf_alpha", fixture_alpha)


def test_phase_1419_tokens_are_present_in_runtime_source() -> None:
    source = JURY_PATH.read_text(encoding="utf-8")

    for token in (
        "anti_capture_diversity_verified_phase_1419",
        "cdl_v3_cluster_diversity_wired_jury_assignment_phase_1419",
        "vrf_outsider_selection_verified_phase_1419",
        "same_operator_domain_independence_verified_phase_1419",
        "anti_capture_production_not_activated_phase_1419",
    ):
        assert token in source


def test_cluster_diversity_evidence_passes_for_selected_panel() -> None:
    quote = quote_jury_assignment(**_quote_kwargs(_passing_pool()))

    assert quote.cluster_diversity_verified is True
    assert quote.cluster_diversity_distinct_clusters == 4
    assert quote.cluster_diversity_largest_cluster_slots == 3
    assert quote.cluster_diversity_total_panel_slots == 8
    assert quote.cluster_diversity_max_cluster_share == 0.375
    assert quote.cluster_diversity_floor == jury_runtime.JURY_CLUSTER_DIVERSITY_FLOOR
    assert (
        quote.cluster_diversity_max_cluster_share_ceiling
        == jury_runtime.JURY_MAX_CLUSTER_SHARE_CEILING
    )
    assert jury_runtime._TOKEN_CDL_V3_CLUSTER_WIRED in quote.phase_tokens


def test_compute_max_cluster_share_is_called_for_cluster_evidence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[float, float]] = []
    real_fn = jury_runtime.compute_max_cluster_share

    def tracking_compute_max_cluster_share(
        *,
        largest_cluster_slots: float,
        total_panel_slots: float,
    ) -> float:
        calls.append((largest_cluster_slots, total_panel_slots))
        return real_fn(
            largest_cluster_slots=largest_cluster_slots,
            total_panel_slots=total_panel_slots,
        )

    monkeypatch.setattr(jury_runtime, "compute_max_cluster_share", tracking_compute_max_cluster_share)

    quote = quote_jury_assignment(**_quote_kwargs(_passing_pool()))

    assert quote.cluster_diversity_verified is True
    assert calls == [(3, 8)]


def test_distinct_cluster_floor_failure_fails_closed() -> None:
    pool = [
        _make_agent("r1", cluster_id="c1", operator_domain="op-a"),
        _make_agent("r2", cluster_id="c1", operator_domain="op-b"),
        _make_agent("r3", cluster_id="c1", operator_domain="op-c"),
        _make_agent("r4", cluster_id="c2", operator_domain="op-d"),
        _make_agent("r5", cluster_id="c2", operator_domain="op-e"),
        _make_agent("r6", cluster_id="c3", operator_domain="op-f"),
        _make_agent("r7", cluster_id="c3", operator_domain="op-g"),
        _make_agent("o1", cluster_id="c3", operator_domain="op-out", outsider=True),
    ]

    with pytest.raises(JuryAssignmentError, match="jury_cluster_diversity_floor_not_met"):
        quote_jury_assignment(**_quote_kwargs(pool))


def test_two_cluster_pool_fails_closed() -> None:
    pool = [
        _make_agent("r1", cluster_id="c1", operator_domain="op-a"),
        _make_agent("r2", cluster_id="c1", operator_domain="op-b"),
        _make_agent("r3", cluster_id="c1", operator_domain="op-c"),
        _make_agent("r4", cluster_id="c1", operator_domain="op-d"),
        _make_agent("r5", cluster_id="c2", operator_domain="op-e"),
        _make_agent("r6", cluster_id="c2", operator_domain="op-f"),
        _make_agent("r7", cluster_id="c2", operator_domain="op-g"),
        _make_agent("o1", cluster_id="c2", operator_domain="op-out", outsider=True),
    ]

    with pytest.raises(JuryAssignmentError, match="jury_cluster_diversity_floor_not_met"):
        quote_jury_assignment(**_quote_kwargs(pool))


def test_max_cluster_share_ceiling_failure_fails_closed() -> None:
    pool = [
        _make_agent("r1", cluster_id="c1", operator_domain="op-a"),
        _make_agent("r2", cluster_id="c1", operator_domain="op-b"),
        _make_agent("r3", cluster_id="c1", operator_domain="op-c"),
        _make_agent("r4", cluster_id="c1", operator_domain="op-d"),
        _make_agent("r5", cluster_id="c2", operator_domain="op-e"),
        _make_agent("r6", cluster_id="c3", operator_domain="op-f"),
        _make_agent("r7", cluster_id="c4", operator_domain="op-g"),
        _make_agent("o1", cluster_id="c5", operator_domain="op-out", outsider=True),
    ]

    with pytest.raises(JuryAssignmentError, match="jury_max_cluster_share_ceiling_exceeded"):
        quote_jury_assignment(**_quote_kwargs(pool))


def test_operator_domain_independence_remains_enforced() -> None:
    pool = [
        _make_agent(f"r{index}", cluster_id=f"c{index}", operator_domain="op-mono")
        for index in range(1, 8)
    ]
    pool.append(_make_agent("o1", cluster_id="c8", operator_domain="op-out", outsider=True))

    with pytest.raises(JuryAssignmentError, match="insufficient_regular_candidates"):
        quote_jury_assignment(**_quote_kwargs(pool))


def test_vrf_outsider_selection_and_cluster_evidence_verified(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    agents = _passing_pool()
    _patch_alpha_to_rfc_vectors(monkeypatch, agents)

    quote = quote_jury_assignment(
        **_quote_kwargs(agents),
        is_high_value_slot=True,
        assignment_nonce="phase-1419-audit-nonce",
        vrf_proofs=_proofs_for(agents),
        _audit_only=True,
    )

    assert quote.assignment_mode == "vrf_verified"
    assert len(quote.outsider_panel) == 1
    assert quote.cluster_diversity_verified is True
    assert jury_runtime._TOKEN_VRF_OUTSIDER_VERIFIED in quote.phase_tokens
    assert jury_runtime._TOKEN_ANTI_CAPTURE_VERIFIED in quote.phase_tokens


def test_production_assignment_guard_stays_default_off(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    agents = _passing_pool()
    _patch_alpha_to_rfc_vectors(monkeypatch, agents)

    assert jury_runtime.PRODUCTION_ASSIGNMENT_NOT_ACTIVATED is True
    with pytest.raises(JuryAssignmentError, match="production_assignment_not_activated"):
        quote_jury_assignment(
            **_quote_kwargs(agents),
            is_high_value_slot=True,
            assignment_nonce="phase-1419-audit-nonce",
            vrf_proofs=_proofs_for(agents),
        )


def test_j008_gate_source_not_patched_by_phase_1419() -> None:
    report = evaluate_jury_activation_gate()
    condition_by_id = {condition.condition_id: condition for condition in report.conditions}

    condition = condition_by_id["ANTI_CAPTURE_DIVERSITY_VERIFIED"]
    assert condition.status is GateConditionStatus.NOT_MET
    assert "ANTI_CAPTURE_DIVERSITY_VERIFIED" in report.blocking_not_met
    assert report.verdict == "INCOMPLETE"
