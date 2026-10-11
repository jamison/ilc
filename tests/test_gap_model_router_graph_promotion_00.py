from __future__ import annotations

import json
from argparse import Namespace
from decimal import Decimal
from pathlib import Path

import pytest

from ilc_core.encoding.cidv1 import parse_nodeid_strict
from ilc_model_router import cli as model_router_cli
from ilc_model_router.receipt_schema import RouterReceiptError
from ilc_model_router.receipt_store import (
    list_router_receipts,
    lookup_by_token,
    open_router_receipt_env,
    update_receipt_consent_status,
)
from ilc_model_router.werner_model_router_bridge import compute_werner_model_router_context


AGENT_ID = "c" * 96


def _route_args(
    tmp_path: Path,
    *,
    no_promote: bool = False,
    graph_store_path: Path | None = None,
) -> Namespace:
    return Namespace(
        agent_id=AGENT_ID,
        capability_class="inference",
        dry_run=True,
        epoch=0,
        graph_store_path=str(graph_store_path or tmp_path / "truth_graph.lmdb"),
        message='{"role":"user","content":"ping"}',
        model_id="claude-haiku-4-5",
        model_router_command="route",
        no_promote=no_promote,
        provider="anthropic",
        store_path=str(tmp_path / "router_receipts.lmdb"),
        timeout=30.0,
    )


def _promote_args(tmp_path: Path, receipt_token: str) -> Namespace:
    return Namespace(
        graph_store_path=str(tmp_path / "truth_graph.lmdb"),
        model_router_command="promote-receipt",
        out_dir=str(tmp_path / "promotions"),
        receipt_token=receipt_token,
        store_path=str(tmp_path / "router_receipts.lmdb"),
    )


def _set_consent_args(state: str) -> Namespace:
    return Namespace(model_router_command="set-consent", state=state)


@pytest.fixture(autouse=True)
def _isolated_consent(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    path = tmp_path / "consent.json"
    monkeypatch.setenv("ILC_MODEL_ROUTER_CONSENT_PATH", str(path))
    return path


def _lookup(tmp_path: Path, receipt_token: str):
    env = open_router_receipt_env(tmp_path / "router_receipts.lmdb")
    try:
        return lookup_by_token(env, receipt_token)
    finally:
        env.close()


def test_route_no_promote_flag_creates_local_only(tmp_path: Path) -> None:
    graph_store = tmp_path / "truth_graph.lmdb"

    result = model_router_cli.run_model_router_command(
        _route_args(tmp_path, no_promote=True, graph_store_path=graph_store)
    )

    receipt = _lookup(tmp_path, result["receipt_token"])
    assert result["promotion_status"] == "suppressed_no_promote"
    assert receipt is not None
    assert receipt.companion.consent_status == "local_only"
    assert not graph_store.exists()


def test_route_consent_disabled_creates_local_only(tmp_path: Path) -> None:
    graph_store = tmp_path / "truth_graph.lmdb"
    model_router_cli.run_model_router_command(_set_consent_args("disabled"))

    result = model_router_cli.run_model_router_command(
        _route_args(tmp_path, graph_store_path=graph_store)
    )

    receipt = _lookup(tmp_path, result["receipt_token"])
    assert result["promotion_status"] == "local_only"
    assert receipt is not None
    assert receipt.companion.consent_status == "local_only"
    assert not graph_store.exists()


def test_route_first_run_notice_emitted_and_acknowledged(tmp_path: Path) -> None:
    result = model_router_cli.run_model_router_command(_route_args(tmp_path))
    consent = json.loads((tmp_path / "consent.json").read_text(encoding="utf-8"))

    assert "first_run_notice" in result
    assert "eligible receipt metadata" in result["first_run_notice"]
    assert consent["first_run_notice_acknowledged"] is True
    assert consent["promotion_enabled"] is True


def test_route_consent_enabled_creates_promoted_receipt(tmp_path: Path) -> None:
    model_router_cli.run_model_router_command(_set_consent_args("enabled"))

    result = model_router_cli.run_model_router_command(_route_args(tmp_path))

    receipt = _lookup(tmp_path, result["receipt_token"])
    assert result["promotion_status"] == "promoted"
    assert result["node_id"].startswith("b")
    assert receipt is not None
    assert receipt.companion.consent_status == "promoted"


def test_route_graph_store_unavailable_leaves_promotion_pending(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    model_router_cli.run_model_router_command(_set_consent_args("enabled"))

    def _boom(*_args, **_kwargs):
        raise OSError("store unavailable")

    monkeypatch.setattr(model_router_cli, "_write_promotion_node", _boom)
    result = model_router_cli.run_model_router_command(_route_args(tmp_path))

    receipt = _lookup(tmp_path, result["receipt_token"])
    assert result["promotion_status"] == "pending_catch_up"
    assert result["catch_up_token"] == result["receipt_token"]
    assert receipt is not None
    assert receipt.companion.consent_status == "promotion_pending"
    context = compute_werner_model_router_context(AGENT_ID, 0, [receipt])
    assert context.flow_budget == Decimal("0E-12")


def test_route_graph_promotion_guard_fails_before_pending_status(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    model_router_cli.run_model_router_command(_set_consent_args("enabled"))
    monkeypatch.setattr(model_router_cli, "GRAPH_PROMOTION_NOT_ACTIVATED", True)

    with pytest.raises(ValueError, match="model_router_graph_promotion_guard_active"):
        model_router_cli.run_model_router_command(_route_args(tmp_path))

    env = open_router_receipt_env(tmp_path / "router_receipts.lmdb")
    try:
        receipts = list(list_router_receipts(env, limit=10))
    finally:
        env.close()
    assert len(receipts) == 1
    assert receipts[0].companion.consent_status == "local_only"


def test_route_corrupt_consent_file_fails_closed_local_only(tmp_path: Path) -> None:
    (tmp_path / "consent.json").write_text("{not-json", encoding="utf-8")

    result = model_router_cli.run_model_router_command(_route_args(tmp_path))

    receipt = _lookup(tmp_path, result["receipt_token"])
    assert result["promotion_status"] == "local_only"
    assert result["consent_status"] == "local_only"
    assert result["consent_error_token"] == "model_router_consent_file_invalid"
    assert receipt is not None
    assert receipt.companion.consent_status == "local_only"


def test_route_programming_error_does_not_become_pending(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    model_router_cli.run_model_router_command(_set_consent_args("enabled"))

    def _boom(_receipt):
        raise ValueError("programming_bug")

    monkeypatch.setattr(model_router_cli, "_promotion_node_payload", _boom)
    with pytest.raises(ValueError, match="programming_bug"):
        model_router_cli.run_model_router_command(_route_args(tmp_path))

    env = open_router_receipt_env(tmp_path / "router_receipts.lmdb")
    try:
        receipts = list(list_router_receipts(env, limit=10))
    finally:
        env.close()
    assert len(receipts) == 1
    assert receipts[0].companion.consent_status == "local_only"


def test_promote_receipt_catch_up_from_promotion_pending(tmp_path: Path) -> None:
    result = model_router_cli.run_model_router_command(_route_args(tmp_path, no_promote=True))
    env = open_router_receipt_env(tmp_path / "router_receipts.lmdb")
    try:
        update_receipt_consent_status(env, result["receipt_token"], "promotion_pending")
    finally:
        env.close()

    promoted = model_router_cli.run_model_router_command(
        _promote_args(tmp_path, result["receipt_token"])
    )

    receipt = _lookup(tmp_path, result["receipt_token"])
    assert promoted["promotion_status"] == "promoted"
    assert receipt is not None
    assert receipt.companion.consent_status == "promoted"


def test_promote_receipt_catch_up_from_local_only(tmp_path: Path) -> None:
    result = model_router_cli.run_model_router_command(_route_args(tmp_path, no_promote=True))

    promoted = model_router_cli.run_model_router_command(
        _promote_args(tmp_path, result["receipt_token"])
    )

    receipt = _lookup(tmp_path, result["receipt_token"])
    assert promoted["promotion_status"] == "promoted"
    assert receipt is not None
    assert receipt.companion.consent_status == "promoted"


def test_promote_receipt_is_idempotent_after_status_update(tmp_path: Path) -> None:
    result = model_router_cli.run_model_router_command(_route_args(tmp_path, no_promote=True))

    first = model_router_cli.run_model_router_command(_promote_args(tmp_path, result["receipt_token"]))
    second = model_router_cli.run_model_router_command(_promote_args(tmp_path, result["receipt_token"]))

    assert first["node_id"] == second["node_id"]
    assert first["node_written"] is True
    assert second["node_written"] is False


def test_promote_receipt_export_payload_field_order(tmp_path: Path) -> None:
    result = model_router_cli.run_model_router_command(_route_args(tmp_path, no_promote=True))

    promoted = model_router_cli.run_model_router_command(_promote_args(tmp_path, result["receipt_token"]))

    assert tuple(promoted) == model_router_cli._PROMOTION_RECEIPT_EXPORT_FIELD_ORDER
    exported = json.loads(
        (tmp_path / "promotions" / f"{result['receipt_token']}.json").read_text(encoding="utf-8")
    )
    assert exported == promoted


def test_update_receipt_consent_status_updates_companion(tmp_path: Path) -> None:
    result = model_router_cli.run_model_router_command(_route_args(tmp_path, no_promote=True))
    env = open_router_receipt_env(tmp_path / "router_receipts.lmdb")
    try:
        update_receipt_consent_status(env, result["receipt_token"], "promoted")
        receipt = lookup_by_token(env, result["receipt_token"])
    finally:
        env.close()

    assert receipt is not None
    assert receipt.companion.consent_status == "promoted"


def test_update_receipt_consent_status_raises_on_missing(tmp_path: Path) -> None:
    env = open_router_receipt_env(tmp_path / "router_receipts.lmdb")
    try:
        with pytest.raises(RouterReceiptError, match="model_router_receipt_not_found"):
            update_receipt_consent_status(env, "f" * 64, "promoted")
    finally:
        env.close()


def test_promoted_node_contains_only_allowlisted_fields(tmp_path: Path) -> None:
    result = model_router_cli.run_model_router_command(_route_args(tmp_path, no_promote=True))
    receipt = _lookup(tmp_path, result["receipt_token"])
    assert receipt is not None

    node_record = model_router_cli._promoted_node_record(receipt)

    assert frozenset(node_record) == model_router_cli._PROMOTED_FIELDS_ALLOWLIST
    assert tuple(node_record) == model_router_cli._PROMOTED_FIELD_ORDER


def test_promoted_node_excludes_private_fields(tmp_path: Path) -> None:
    result = model_router_cli.run_model_router_command(_route_args(tmp_path, no_promote=True))
    receipt = _lookup(tmp_path, result["receipt_token"])
    assert receipt is not None
    node_record = model_router_cli._promoted_node_record(receipt)

    forbidden = {
        "raw_prompt",
        "raw_completion",
        "prompt_text",
        "completion_text",
        "api_key",
        "provider_secret",
        "inputs_hash",
        "outputs_hash",
        "provider_id",
    }
    assert forbidden.isdisjoint(node_record)


def test_promoted_node_consent_status_is_always_promoted(tmp_path: Path) -> None:
    result = model_router_cli.run_model_router_command(_route_args(tmp_path, no_promote=True))
    receipt = _lookup(tmp_path, result["receipt_token"])
    assert receipt is not None

    assert model_router_cli._promoted_node_record(receipt)["consent_status"] == "promoted"


def test_promoted_node_has_valid_cidv1(tmp_path: Path) -> None:
    result = model_router_cli.run_model_router_command(_route_args(tmp_path, no_promote=True))
    receipt = _lookup(tmp_path, result["receipt_token"])
    assert receipt is not None

    node_id = model_router_cli._write_promotion_node(
        receipt,
        graph_store_path=tmp_path / "truth_graph.lmdb",
    )["node_id"]

    assert node_id.startswith("b")
    parse_nodeid_strict(node_id)


def test_local_only_receipt_produces_zero_werner_signal(tmp_path: Path) -> None:
    result = model_router_cli.run_model_router_command(_route_args(tmp_path, no_promote=True))
    receipt = _lookup(tmp_path, result["receipt_token"])
    assert receipt is not None

    context = compute_werner_model_router_context(AGENT_ID, 0, [receipt])

    assert context.flow_budget == Decimal("0E-12")


def test_promoted_receipt_produces_positive_werner_signal(tmp_path: Path) -> None:
    result = model_router_cli.run_model_router_command(_route_args(tmp_path, no_promote=True))
    model_router_cli.run_model_router_command(_promote_args(tmp_path, result["receipt_token"]))
    receipt = _lookup(tmp_path, result["receipt_token"])
    assert receipt is not None

    context = compute_werner_model_router_context(AGENT_ID, 0, [receipt])

    assert context.flow_budget > Decimal("0")


def test_no_genesis_atlas_lmdb_writer_imported() -> None:
    source = Path(model_router_cli.__file__).read_text(encoding="utf-8")

    assert "genesis_atlas_lmdb_writer" not in source


def test_graph_store_path_env_var_overrides_default(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    graph_path = tmp_path / "custom_truth_graph.lmdb"
    monkeypatch.setenv("ILC_MODEL_ROUTER_GRAPH_STORE_PATH", str(graph_path))

    assert model_router_cli._graph_store_path("") == graph_path


def test_set_consent_disabled_writes_consent_file(tmp_path: Path) -> None:
    result = model_router_cli.run_model_router_command(_set_consent_args("disabled"))
    consent = json.loads((tmp_path / "consent.json").read_text(encoding="utf-8"))

    assert result["promotion_enabled"] is False
    assert consent["promotion_enabled"] is False


def test_set_consent_enabled_writes_consent_file(tmp_path: Path) -> None:
    result = model_router_cli.run_model_router_command(_set_consent_args("enabled"))
    consent = json.loads((tmp_path / "consent.json").read_text(encoding="utf-8"))

    assert result["promotion_enabled"] is True
    assert consent["promotion_enabled"] is True
    assert consent["first_run_notice_acknowledged"] is True


def test_consent_disable_enable_round_trip_controls_route(tmp_path: Path) -> None:
    graph_store = tmp_path / "truth_graph.lmdb"

    disabled = model_router_cli.run_model_router_command(_set_consent_args("disabled"))
    local = model_router_cli.run_model_router_command(
        _route_args(tmp_path, graph_store_path=graph_store)
    )
    local_receipt = _lookup(tmp_path, local["receipt_token"])

    enabled = model_router_cli.run_model_router_command(_set_consent_args("enabled"))
    promoted = model_router_cli.run_model_router_command(
        _route_args(tmp_path, graph_store_path=graph_store)
    )
    promoted_receipt = _lookup(tmp_path, promoted["receipt_token"])

    assert disabled["promotion_enabled"] is False
    assert enabled["promotion_enabled"] is True
    assert local["promotion_status"] == "local_only"
    assert local_receipt is not None
    assert local_receipt.companion.consent_status == "local_only"
    assert promoted["promotion_status"] == "promoted"
    assert promoted_receipt is not None
    assert promoted_receipt.companion.consent_status == "promoted"
