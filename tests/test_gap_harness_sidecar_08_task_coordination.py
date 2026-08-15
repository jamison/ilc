# SPDX-License-Identifier: AGPL-3.0-only
"""Task coordination sidecar tests for GAP-HARNESS-SIDECAR-08."""

from __future__ import annotations

import ast
from decimal import Decimal
from pathlib import Path

import pytest

from ilc_core.sidecars.execution_receipt import SidecarExecutionReceiptStore
from ilc_core.sidecars.task_coordination import (
    ACCEPTANCES_DB_NAME,
    OFFERS_DB_NAME,
    RESULTS_DB_NAME,
    TASK_COORDINATION_TRANSFER_ENABLED,
    TaskCoordinationError,
    TaskCoordinationLmdbStore,
    TaskOffer,
)


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "ilc_core/sidecars/task_coordination.py"
AGENT_A = "a" * 96
AGENT_B = "b" * 96
AGENT_C = "c" * 96


def _offer(**overrides: object) -> TaskOffer:
    params = {
        "commissioning_agent_id": AGENT_A,
        "task_description": "Summarize the graph slice.",
        "result_criteria": "Result must cite the input node hash.",
        "expiry_epoch": 10,
    }
    params.update(overrides)
    return TaskOffer(**params)  # type: ignore[arg-type]


def test_task_offer_id_is_deterministic_and_round_trips() -> None:
    first = _offer()
    second = _offer()

    assert first.offer_id == second.offer_id
    assert TaskOffer.from_dict(first.to_dict()) == first
    assert first.with_status("accepted").offer_id == first.offer_id
    assert first.with_status("completed").offer_id == first.offer_id
    assert first.with_status("expired").offer_id == first.offer_id


def test_task_offer_rejects_invalid_agent_id_uppercase() -> None:
    with pytest.raises(TaskCoordinationError, match="task_agent_id_invalid"):
        _offer(commissioning_agent_id="A" * 96)


def test_task_offer_rejects_bool_epoch() -> None:
    with pytest.raises(TaskCoordinationError, match="task_expiry_epoch_invalid"):
        _offer(expiry_epoch=True)


def test_task_offer_rejects_non_finite_precommit_amount() -> None:
    with pytest.raises(ValueError, match="invalid_amount_non_finite"):
        _offer(pre_committed_ilc_amount=Decimal("NaN"))
    with pytest.raises(ValueError, match="invalid_amount_non_finite"):
        _offer(pre_committed_ilc_amount=Decimal("Infinity"))


def test_task_offer_rejects_non_positive_amount_and_excessive_text() -> None:
    with pytest.raises(TaskCoordinationError, match="invalid_amount_non_positive"):
        _offer(pre_committed_ilc_amount=Decimal("0"))
    with pytest.raises(TaskCoordinationError, match="task_description_invalid"):
        _offer(task_description="x" * 1001)
    with pytest.raises(TaskCoordinationError, match="task_result_criteria_invalid"):
        _offer(result_criteria="x" * 501)


def test_store_creates_offer_and_uses_required_lmdb_subdatabases(tmp_path: Path) -> None:
    store = TaskCoordinationLmdbStore(tmp_path / "tasks")
    offer = _offer()

    store.create_offer(offer)

    assert store.get_offer(offer.offer_id) == offer
    assert store.env.open_db(OFFERS_DB_NAME) is not None
    assert store.env.open_db(ACCEPTANCES_DB_NAME) is not None
    assert store.env.open_db(RESULTS_DB_NAME) is not None


def test_store_rejects_duplicate_offer(tmp_path: Path) -> None:
    store = TaskCoordinationLmdbStore(tmp_path / "tasks")
    offer = _offer()

    store.create_offer(offer)
    with pytest.raises(TaskCoordinationError, match="task_offer_duplicate"):
        store.create_offer(offer)


def test_accept_offer_records_acceptance_and_updates_status(tmp_path: Path) -> None:
    store = TaskCoordinationLmdbStore(tmp_path / "tasks")
    offer = _offer(caps_max_concurrent=2)
    store.create_offer(offer)

    store.accept_offer(offer.offer_id, AGENT_B, current_epoch=2)

    accepted = store.get_offer(offer.offer_id)
    assert accepted is not None
    assert accepted.offer_id == offer.offer_id
    assert accepted.status == "accepted"
    assert store.list_acceptances(offer.offer_id) == [
        {
            "accepted_epoch": 2,
            "accepting_agent_id": AGENT_B,
            "offer_id": offer.offer_id,
            "schema_version": "task_coordination_GAP_HARNESS_SIDECAR_08.v0.1",
        }
    ]


def test_accept_offer_rejects_expired_offer_using_protocol_epoch(tmp_path: Path) -> None:
    store = TaskCoordinationLmdbStore(tmp_path / "tasks")
    offer = _offer(expiry_epoch=4)
    store.create_offer(offer)

    with pytest.raises(TaskCoordinationError, match="task_offer_expired"):
        store.accept_offer(offer.offer_id, AGENT_B, current_epoch=4)

    expired = store.get_offer(offer.offer_id)
    assert expired is not None
    assert expired.offer_id == offer.offer_id
    assert expired.status == "expired"


def test_accept_offer_enforces_capacity_and_duplicate_acceptance(tmp_path: Path) -> None:
    store = TaskCoordinationLmdbStore(tmp_path / "tasks")
    offer = _offer(caps_max_concurrent=1)
    store.create_offer(offer)
    store.accept_offer(offer.offer_id, AGENT_B, current_epoch=2)

    with pytest.raises(TaskCoordinationError, match="task_offer_already_accepted_by_agent"):
        store.accept_offer(offer.offer_id, AGENT_B, current_epoch=3)
    with pytest.raises(TaskCoordinationError, match="task_offer_capacity_exceeded"):
        store.accept_offer(offer.offer_id, AGENT_C, current_epoch=3)


def test_store_level_agent_concurrent_cap_is_defaulted_and_enforced(tmp_path: Path) -> None:
    store = TaskCoordinationLmdbStore(tmp_path / "tasks", max_concurrent_acceptances_per_agent=1)
    first = _offer(task_description="task one", caps_max_concurrent=2)
    second = _offer(task_description="task two", caps_max_concurrent=2)
    store.create_offer(first)
    store.create_offer(second)
    store.accept_offer(first.offer_id, AGENT_B, current_epoch=1)

    with pytest.raises(TaskCoordinationError, match="task_agent_concurrent_cap_exceeded"):
        store.accept_offer(second.offer_id, AGENT_B, current_epoch=1)


def test_precommitted_transfer_path_is_default_off(tmp_path: Path) -> None:
    assert TASK_COORDINATION_TRANSFER_ENABLED is False
    store = TaskCoordinationLmdbStore(tmp_path / "tasks")
    offer = _offer(pre_committed_ilc_amount=Decimal("1.25"))
    store.create_offer(offer)

    with pytest.raises(ValueError, match="task_coordination_transfer_not_activated"):
        store.accept_offer(offer.offer_id, AGENT_B, current_epoch=1)

    assert store.list_acceptances(offer.offer_id) == []


def test_submit_result_requires_acceptance_and_records_result(tmp_path: Path) -> None:
    store = TaskCoordinationLmdbStore(tmp_path / "tasks")
    offer = _offer(caps_max_concurrent=1)
    store.create_offer(offer)

    with pytest.raises(TaskCoordinationError, match="task_offer_not_accepted_by_agent"):
        store.submit_result(offer.offer_id, AGENT_B, "abc123", "summary", current_epoch=2)

    store.accept_offer(offer.offer_id, AGENT_B, current_epoch=1)
    store.submit_result(offer.offer_id, AGENT_B, "abc123", "summary", current_epoch=2)

    completed = store.get_offer(offer.offer_id)
    assert completed is not None
    assert completed.offer_id == offer.offer_id
    assert completed.status == "completed"
    assert store.list_results(offer.offer_id)[0]["ordinal"] == 0


def test_expire_stale_offers_marks_only_open_or_accepted_offers(tmp_path: Path) -> None:
    store = TaskCoordinationLmdbStore(tmp_path / "tasks")
    stale = _offer(task_description="stale", expiry_epoch=2)
    fresh = _offer(task_description="fresh", expiry_epoch=5)
    store.create_offer(stale)
    store.create_offer(fresh)

    assert store.expire_stale_offers(current_epoch=3) == [stale.offer_id]
    assert store.get_offer(stale.offer_id).status == "expired"  # type: ignore[union-attr]
    assert store.get_offer(fresh.offer_id).status == "open"  # type: ignore[union-attr]


def test_lifecycle_events_are_recorded_as_sidecar_receipts(tmp_path: Path) -> None:
    receipt_store = SidecarExecutionReceiptStore(tmp_path / "receipts")
    store = TaskCoordinationLmdbStore(tmp_path / "tasks", receipt_store=receipt_store)
    offer = _offer(caps_max_concurrent=1)

    store.create_offer(offer)
    store.accept_offer(offer.offer_id, AGENT_B, current_epoch=1)
    store.submit_result(offer.offer_id, AGENT_B, "abc123", "summary", current_epoch=2)

    create_receipts = receipt_store.read_receipts_for_epoch(offer.expiry_epoch)
    action_receipts = receipt_store.read_receipts_for_epoch(1) + receipt_store.read_receipts_for_epoch(2)
    assert create_receipts[0].tool_id == "task_coordination:create_offer"
    assert [receipt.tool_id for receipt in action_receipts] == [
        "task_coordination:accept_offer",
        "task_coordination:submit_result",
    ]


def test_corrupted_stored_amount_raises_stable_error_token() -> None:
    payload = _offer(pre_committed_ilc_amount=Decimal("1")).to_dict()
    payload["pre_committed_ilc_amount"] = "not-a-decimal"

    with pytest.raises(TaskCoordinationError, match="invalid_amount_type"):
        TaskOffer.from_dict(payload)


def test_module_has_no_wall_clock_network_public_serving_or_cdl_mutation_surface() -> None:
    source = MODULE.read_text(encoding="utf-8")
    tree = ast.parse(source)

    assert "datetime.now" not in source
    assert "time.time()" not in source
    assert "constitutional_decision_log" not in source
    assert "cdl_register" not in source
    forbidden_import_roots = {"aiohttp", "fastapi", "httpx", "requests", "socket", "urllib"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] not in forbidden_import_roots
        if isinstance(node, ast.ImportFrom):
            assert (node.module or "").split(".")[0] not in forbidden_import_roots


def test_json_dumps_calls_lock_sort_keys_and_allow_nan_false() -> None:
    source = MODULE.read_text(encoding="utf-8")
    tree = ast.parse(source)
    dumps_calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "dumps"
    ]

    assert dumps_calls
    for call in dumps_calls:
        kwargs = {keyword.arg: keyword.value for keyword in call.keywords}
        assert isinstance(kwargs["sort_keys"], ast.Constant)
        assert kwargs["sort_keys"].value is True
        assert isinstance(kwargs["allow_nan"], ast.Constant)
        assert kwargs["allow_nan"].value is False
