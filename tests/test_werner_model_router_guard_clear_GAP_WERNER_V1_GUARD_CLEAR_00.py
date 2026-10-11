from __future__ import annotations

from argparse import Namespace
from decimal import Decimal

import pytest

from ilc_model_router import cli as model_router_cli
from ilc_model_router.receipt_schema import RouterCompanionRecord
from ilc_model_router.werner_model_router_bridge import (
    NON_CLAIMS,
    WERNER_CONTEXT_ABSENT_TOKEN,
    WERNER_GUARD_ACTIVE_ABSENT_TOKEN,
    WERNER_MODEL_ROUTER_NOT_ACTIVATED,
    compute_werner_model_router_context,
)


AGENT_ID = "a" * 96


def _receipt(
    *,
    token: str = "1" * 64,
    consent: str = "promoted",
    in_tokens: int = 10_000,
    out_tokens: int = 10_000,
) -> RouterCompanionRecord:
    return RouterCompanionRecord(
        receipt_token=token,
        model_id="model-x",
        provider="provider-x",
        token_counts_input=in_tokens,
        token_counts_output=out_tokens,
        capability_class="inference",
        consent_status=consent,
    )


def _route_args(store_path: str) -> Namespace:
    return Namespace(
        agent_id="c" * 96,
        capability_class="inference",
        dry_run=True,
        epoch=0,
        message='{"role":"user","content":"ping"}',
        model_id="claude-haiku-4-5",
        model_router_command="route",
        graph_store_path="",
        no_promote=True,
        provider="anthropic",
        store_path=store_path,
        timeout=30.0,
    )


def test_guard_is_false_after_clearance() -> None:
    assert WERNER_MODEL_ROUTER_NOT_ACTIVATED is False


def test_guard_true_branch_returns_absent_context(monkeypatch: pytest.MonkeyPatch) -> None:
    import ilc_model_router.werner_model_router_bridge as bridge

    monkeypatch.setattr(bridge, "WERNER_MODEL_ROUTER_NOT_ACTIVATED", True)

    context = bridge.compute_werner_model_router_context(AGENT_ID, 0, [_receipt()])

    assert context.werner_context_present is False
    assert context.flow_budget == bridge.ZERO
    assert context.receipt_count == 0
    assert context.absent_token == WERNER_GUARD_ACTIVE_ABSENT_TOKEN


def test_guard_true_branch_returns_context_not_exception(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import ilc_model_router.werner_model_router_bridge as bridge

    monkeypatch.setattr(bridge, "WERNER_MODEL_ROUTER_NOT_ACTIVATED", True)

    context = bridge.compute_werner_model_router_context(AGENT_ID, 0, [_receipt()])

    assert context.werner_context_present is False


def test_guard_false_with_valid_receipt_produces_positive_budget() -> None:
    context = compute_werner_model_router_context(AGENT_ID, 0, [_receipt()])

    assert context.werner_context_present is True
    assert context.flow_budget > Decimal("0")


def test_stale_guard_not_cleared_non_claim_removed() -> None:
    assert "guard_not_cleared_WERNER_MODEL_ROUTER_NOT_ACTIVATED" not in NON_CLAIMS


def test_expected_non_claims_remain_after_guard_clearance() -> None:
    for claim in (
        "no_ecu_mint",
        "no_ilc_settlement",
        "no_genesis_atlas_lmdb_write",
        "no_signed_AtlasSliceManifest_mutation",
        "no_capproof_stacking",
        "no_passive_ecu_quality_factor_stacking",
    ):
        assert claim in NON_CLAIMS


def test_normal_absent_path_uses_generic_absent_token() -> None:
    context = compute_werner_model_router_context(AGENT_ID, 0, [])

    assert context.werner_context_present is False
    assert context.absent_token == WERNER_CONTEXT_ABSENT_TOKEN


def test_guarded_path_uses_guard_active_absent_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import ilc_model_router.werner_model_router_bridge as bridge

    monkeypatch.setattr(bridge, "WERNER_MODEL_ROUTER_NOT_ACTIVATED", True)

    context = bridge.compute_werner_model_router_context(AGENT_ID, 0, [_receipt()])

    assert context.absent_token == WERNER_GUARD_ACTIVE_ABSENT_TOKEN


def test_werner_context_cli_subcommand_exists() -> None:
    parser = model_router_cli._build_parser()

    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(
            [
                "werner-context",
                "--agent-id",
                "a" * 96,
                "--epoch",
                "0",
                "--help",
            ]
        )

    assert exc_info.value.code == 0


def test_werner_context_cli_returns_required_keys(tmp_path) -> None:
    store_path = str(tmp_path / "router_receipts.lmdb")
    model_router_cli.run_model_router_command(_route_args(store_path))

    result = model_router_cli.run_model_router_command(
        Namespace(
            agent_id="c" * 96,
            epoch=0,
            limit=100,
            model_router_command="werner-context",
            store_path=store_path,
        )
    )

    for key in (
        "flow_budget",
        "receipt_count",
        "werner_context_present",
        "non_claims",
    ):
        assert key in result
    assert result["receipt_count"] == 1


def test_werner_context_cli_flow_budget_is_string(tmp_path) -> None:
    store_path = str(tmp_path / "router_receipts.lmdb")
    model_router_cli.run_model_router_command(_route_args(store_path))

    result = model_router_cli.run_model_router_command(
        Namespace(
            agent_id="c" * 96,
            epoch=0,
            limit=100,
            model_router_command="werner-context",
            store_path=store_path,
        )
    )

    assert isinstance(result["flow_budget"], str)


def test_promote_receipt_writes_graph_node_after_promotion_activation(tmp_path) -> None:
    store_path = str(tmp_path / "router_receipts.lmdb")
    graph_store_path = str(tmp_path / "truth_graph.lmdb")
    promotion_dir = str(tmp_path / "promotions")
    route = model_router_cli.run_model_router_command(_route_args(store_path))

    promoted = model_router_cli.run_model_router_command(
        Namespace(
            graph_store_path=graph_store_path,
            model_router_command="promote-receipt",
            out_dir=promotion_dir,
            receipt_token=route["receipt_token"],
            store_path=store_path,
        )
    )

    assert promoted["promotion_status"] == "promoted"
    assert promoted["node_id"].startswith("b")
