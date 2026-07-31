from __future__ import annotations

import hashlib
import json
import re
from decimal import Decimal
from pathlib import Path

from ilc_core.consensus.attribution_batch_bridge import (
    build_attribution_batch_from_claims,
)
from ilc_core.economics.backward_attribution_traversal import (
    BACKWARD_ATTRIBUTION_DECAY_ALPHA,
    BACKWARD_ATTRIBUTION_PER_NODE_CAP,
    BackwardAttributionTraversal,
)
from ilc_core.ledger.ecu_active_layer_runtime import EcuActiveLayerRuntime
from ilc_core.ledger.ecu_ilc_lifecycle_runtime import EcuIlcLifecycleRuntime
from ilc_core.protocol.public_wallet_runtime import PublicWalletRuntime
from ilc_core.storage.lmdb_public_runtime import LmdbWalletStore


ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "docs" / "phases" / "STATUS.md"
GAP_ECU_05_TESTS = ROOT / "tests" / "test_phase_1595i_rust_binding.py"
BALANCE_STORE = ROOT / "ilc_consensus" / "src" / "balance_store.rs"

AGENT_A = "a" * 96
AGENT_B = "b" * 96
AGENT_C = "c" * 96
AGENT_D = "d" * 96


def _node(agent_id: str, *, novelty: str = "1", status: str = "1") -> dict[str, object]:
    return {
        "artifact_type": "claim",
        "created_epoch": 0,
        "novelty_score": novelty,
        "recipient_agent_id": agent_id,
        "status_quality_weight": status,
    }


def _edge(source: str, target: str) -> dict[str, object]:
    return {
        "edge_confidence": "1",
        "edge_type": "PROVENANCE",
        "source_node_id": source,
        "target_node_id": target,
    }


def _claim_payload(*, agent_id: str = AGENT_B, amount: str = "7", epoch: int = 42) -> dict[str, object]:
    return {
        "claims": [
            {
                "agent_id": agent_id,
                "amount": amount,
                "claim_id": "claim-direct",
                "epoch": epoch,
            }
        ],
        "marker": "agent_loop_claims_ok",
    }


def _graph_context(
    *,
    nodes: dict[str, object] | None = None,
    edges: list[dict[str, object]] | None = None,
    event_id: str = "event-backward",
    event_budget_ecu: str = "100",
    event_epoch: int = 42,
    source_node_id: str = "node-b",
) -> dict[str, object]:
    return {
        "edges": edges or [_edge("node-b", "node-a")],
        "events": [
            {
                "event_budget_ecu": event_budget_ecu,
                "event_epoch": event_epoch,
                "event_id": event_id,
                "source_node_id": source_node_id,
            }
        ],
        "nodes": nodes or {"node-b": _node(AGENT_B), "node-a": _node(AGENT_A)},
    }


def _expected_backward_root(entries: list[dict[str, object]]) -> str:
    sorted_entries = sorted(
        entries,
        key=lambda item: (
            item["event_id"],
            item["upstream_artifact_id"],
            item["recipient_agent_id"],
        ),
    )
    preimage = json.dumps(
        sorted_entries,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(preimage).hexdigest()


def _backward_credit_for(batch: dict[str, object], agent_id: str) -> dict[str, object]:
    entries = batch["backward_attribution_entries"]
    assert isinstance(entries, list)
    matches = [
        entry
        for entry in entries
        if isinstance(entry, dict) and entry["recipient_agent_id"] == agent_id
    ]
    assert len(matches) == 1
    return matches[0]


def _attribution_for(batch: dict[str, object], agent_id: str) -> dict[str, object]:
    attributions = batch["attributions"]
    assert isinstance(attributions, list)
    matches = [
        item
        for item in attributions
        if isinstance(item, dict) and item["agent_id_hex"] == agent_id
    ]
    assert len(matches) == 1
    return matches[0]


def test_simple_2hop_backward_attribution() -> None:
    traversal_result = BackwardAttributionTraversal(
        {"node-b": _node(AGENT_B), "node-a": _node(AGENT_A)},
        [_edge("node-b", "node-a")],
    ).traverse(
        "node-b",
        event_id="event-backward",
        event_budget_ecu="100",
        event_epoch=42,
        apply_antigaming_caps=True,
    )
    batch = build_attribution_batch_from_claims(
        _claim_payload(),
        backward_attribution_graph_context=_graph_context(),
    )

    credit = _backward_credit_for(batch, AGENT_A)
    final_credit_ecu = Decimal(str(credit["credit_amount"]))
    expected_age_weight = Decimal("0.25")
    expected_score = BACKWARD_ATTRIBUTION_DECAY_ALPHA * expected_age_weight

    assert final_credit_ecu == Decimal("0.5000")
    assert traversal_result.path_scores[0].age_weight == expected_age_weight
    assert traversal_result.path_scores[0].raw_path_score == expected_score
    assert re.fullmatch(r"[0-9a-f]{64}", str(batch["backward_attribution_batch_root"]))
    assert batch["backward_attribution_batch_root"] == _expected_backward_root(
        batch["backward_attribution_entries"]  # type: ignore[arg-type]
    )


def test_cycle_safe_traversal() -> None:
    nodes = {
        "node-a": _node(AGENT_A),
        "node-b": _node(AGENT_B),
        "node-c": _node(AGENT_C),
    }
    edges = [
        _edge("node-b", "node-a"),
        _edge("node-a", "node-c"),
        _edge("node-c", "node-b"),
    ]
    traversal = BackwardAttributionTraversal(nodes, edges)

    result = traversal.traverse(
        "node-b",
        event_id="event-cycle",
        event_budget_ecu="100",
        event_epoch=42,
        apply_antigaming_caps=True,
    )
    batch = build_attribution_batch_from_claims(
        _claim_payload(),
        backward_attribution_graph_context=_graph_context(
            nodes=nodes,
            edges=edges,
            event_id="event-cycle",
        ),
    )

    assert result.cycle_rejections == 1
    assert result.traversal_edge_count == 3
    assert re.fullmatch(r"[0-9a-f]{64}", str(batch["backward_attribution_batch_root"]))


def test_dominance_cap_in_soak() -> None:
    nodes = {
        "node-b": _node(AGENT_B),
        "node-a": _node(AGENT_A),
        "node-c": _node(AGENT_C),
    }
    edges = [
        _edge("node-b", "node-a"),
        _edge("node-b", "node-c"),
        _edge("node-c", "node-a"),
    ]

    result = BackwardAttributionTraversal(nodes, edges).traverse(
        "node-b",
        event_id="event-dominance",
        event_budget_ecu="100",
        event_epoch=42,
        apply_antigaming_caps=True,
    )
    node_a_credit = next(
        credit for credit in result.final_credits if credit.upstream_artifact_id == "node-a"
    )
    batch = build_attribution_batch_from_claims(
        _claim_payload(),
        backward_attribution_graph_context=_graph_context(
            nodes=nodes,
            edges=edges,
            event_id="event-dominance",
        ),
    )

    assert result.node_cap_amount_ecu == Decimal("10.0") * BACKWARD_ATTRIBUTION_PER_NODE_CAP
    assert node_a_credit.final_credit_ecu == result.node_cap_amount_ecu
    assert node_a_credit.node_cap_applied is True
    assert node_a_credit.clipped_residual_ecu > Decimal("0")
    assert _backward_credit_for(batch, AGENT_A)["node_cap_applied"] is True


def test_sybil_diversity_guard_gap_documented() -> None:
    traversal = BackwardAttributionTraversal(
        {"node-b": _node(AGENT_B), "node-a": _node(AGENT_A)},
        [_edge("node-b", "node-a")],
    )
    status_text = STATUS.read_text(encoding="utf-8")

    assert not hasattr(BackwardAttributionTraversal, "sybil_diversity_guard")
    assert not hasattr(traversal, "sybil_diversity_guard")
    assert "sybil_diversity_guard_cdl_gap" in status_text
    assert "no CDL-108 locked threshold" in status_text


def test_gap_ecu_05_rust_binding_tests_remain_present() -> None:
    test_source = GAP_ECU_05_TESTS.read_text(encoding="utf-8")
    balance_store_source = BALANCE_STORE.read_text(encoding="utf-8")

    for test_name in (
        "test_backward_attribution_root_present_when_credits_exist",
        "test_backward_attribution_root_deterministic",
        "test_rust_ingestion_accepts_batch_with_root",
        "test_rust_ingestion_accepts_batch_without_root",
        "test_rust_ingestion_rejects_malformed_backward_root",
    ):
        assert f"def {test_name}" in test_source
    assert "fn test_apply_attribution_stores_backward_attribution_batch_root" in balance_store_source
    assert "get_backward_attribution_batch_root" in balance_store_source


def test_bridge_output_shows_backward_attribution_credit(tmp_path: Path) -> None:
    batch = build_attribution_batch_from_claims(
        _claim_payload(agent_id=AGENT_B, amount="7"),
        backward_attribution_graph_context=_graph_context(event_id="event-bridge-output"),
    )

    credit = _backward_credit_for(batch, AGENT_A)
    final_credit_ecu = Decimal(str(credit["credit_amount"]))
    root = str(batch["backward_attribution_batch_root"])
    agent_a_before = "0"
    direct_b = _attribution_for(batch, AGENT_B)

    wallet_store = LmdbWalletStore(tmp_path / "wallet.lmdb")
    lifecycle_runtime = EcuIlcLifecycleRuntime(
        wallet_store=wallet_store,
        ecu_runtime=EcuActiveLayerRuntime(),
    )
    wallet_runtime = PublicWalletRuntime(
        wallet_store=wallet_store,
        lifecycle_runtime=lifecycle_runtime,
    )
    try:
        before = wallet_runtime.wallet_status(agent_id=AGENT_A)
        lifecycle_runtime.commit_settled_epoch(
            agent_id=AGENT_A,
            epoch_id="phase-1595j-event-bridge-output",
            reward_delta_ilc=str(final_credit_ecu),
        )
        after = wallet_runtime.wallet_status(agent_id=AGENT_A)
    finally:
        wallet_store.close()

    assert final_credit_ecu > Decimal("0")
    assert re.fullmatch(r"[0-9a-f]{64}", root)
    assert root == _expected_backward_root(
        batch["backward_attribution_entries"]  # type: ignore[arg-type]
    )
    assert direct_b["source_amount_ecu"] == "7"
    assert direct_b["amount_micro_ecu"] == 7_000_000
    assert before["data"]["balance_ilc"] == agent_a_before
    assert after["data"]["balance_ilc"] == str(final_credit_ecu)
