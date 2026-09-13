from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from ilc_core.protocol.public_wallet_runtime import WALLET_CLAIMABILITY_STATE_DEFERRED
from ilc_core.epoch.pool_carry_forward_runtime import PERFORMER_CARRY_FORWARD_ACCOUNT_ID
from ilc_core.epoch.protocol_reserve_destination import PROTOCOL_RESERVE_ACCOUNT_ID
from ilc_core.server import create_app

DOC_PATH = Path("docs/specs/ilc_public_wallet_runtime_integration_653_v0.1.md")
TEST_PATH = Path("tests/test_phase_653_public_wallet_runtime_integration.py")
WALKTHROUGH_PATH = Path("docs/phases/phase_653_g8_public_wallet_runtime_integration_walkthrough.md")
STATUS_PATH = Path("docs/phases/STATUS.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
SERVER_PATH = Path("ilc_core/server.py")
RUNTIME_PATH = Path("ilc_core/protocol/public_wallet_runtime.py")
PHASE_653_SUBJECT_TOKENS = ("phase 653", "public wallet runtime integration")
PHASE_653_BACKFILL_SUBJECT_TOKENS = ("phase 653", "walkthrough", "backfill")
EXACT_REQUIRED_MAIN_PATHS = {
    str(DOC_PATH),
    str(SERVER_PATH),
    str(RUNTIME_PATH),
    str(TEST_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_HEADINGS = (
    "## 1. Runtime target and inherited wallet boundary",
    "## 2. Live wallet query operations",
    "## 3. Settled-root linkage and receipt-backed accounting visibility",
    "## 4. Failure-token and read-only enforcement discipline",
    "## 5. Explicit exclusions and preserved boundaries",
)
REQUIRED_TOKENS = (
    "public_wallet_runtime_653_live",
    "wallet_status_history_export_ledger_summary_live",
    "wallet_surface_read_only_and_accounting_only_in_runtime",
    "claimability_state_deferred_in_wallet_runtime",
    "wallet_history_and_export_bind_to_settled_runtime_root",
    "no_wallet_write_spend_transfer_withdrawal_in_653",
)
EXPECTED_ROUTE_PATHS = {
    "/v1/public/wallet/{agent_id}/status",
    "/v1/public/wallet/{agent_id}/history",
    "/v1/public/wallet/{agent_id}/export",
    "/v1/public/wallet/{agent_id}/ledger-summary",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _subject_matches(subject: str, tokens: tuple[str, ...]) -> bool:
    lowered = subject.lower()
    return all(token in lowered for token in tokens)


def _find_commit_ref(*, subject_tokens: tuple[str, ...]) -> str | None:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if _subject_matches(subject, subject_tokens):
            return commit_hash
    return None


def _resolve_commit_ref(*, subject_tokens: tuple[str, ...], expected_paths: set[str]) -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    matches: list[str] = []
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if _subject_matches(subject, subject_tokens):
            matches.append(commit_hash)
    for commit_ref in matches:
        if _changed_paths_for_commit(commit_ref) == expected_paths:
            return commit_ref
    raise AssertionError(f"commit_not_present_in_local_history:{subject_tokens}")


def _require_commit_or_skip(subject_tokens: tuple[str, ...]) -> None:
    if _find_commit_ref(subject_tokens=subject_tokens) is None:
        pytest.skip(f"commit_not_yet_present:{subject_tokens}")


def _seed_wallet_runtime(client: TestClient, *, agent_id: str = "a" * 96) -> dict[str, str]:
    state = client.app.state
    state.ecu_active_layer_runtime.set_accrued_ecu(agent_id, "8.5")
    state.public_lifecycle_runtime.commit_settled_epoch(
        agent_id=agent_id,
        epoch_id="epoch-001",
        reward_delta_ilc="3",
    )
    return {"agent_id": agent_id}


def test_runtime_doc_exists_and_contains_required_headings_and_tokens() -> None:
    text = _read(DOC_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text
    for token in REQUIRED_TOKENS:
        assert token in text


def test_wallet_operations_remain_available_as_local_runtime_only() -> None:
    app = create_app()
    with TestClient(app):
        assert app.state.public_wallet_runtime is not None
    server_text = _read(SERVER_PATH)
    for route_path in EXPECTED_ROUTE_PATHS:
        assert route_path not in server_text


def test_wallet_status_history_export_and_ledger_summary_are_read_only_and_accounting_only() -> None:
    with TestClient(create_app()) as client:
        seeded = _seed_wallet_runtime(client)
        agent_id = seeded["agent_id"]
        runtime = client.app.state.public_wallet_runtime
        status_payload = runtime.wallet_status(agent_id=agent_id)
        history_payload = runtime.wallet_history(agent_id=agent_id)
        export_payload = runtime.wallet_export(agent_id=agent_id)
        summary_payload = runtime.ledger_summary(agent_id=agent_id)

        assert status_payload["token"] == "wallet_status_found"
        assert history_payload["token"] == "wallet_history_found"
        assert export_payload["token"] == "wallet_export_found"
        assert summary_payload["token"] == "ledger_summary_found"

        status = status_payload["data"]
        history = history_payload["data"]
        export = export_payload["data"]
        summary = summary_payload["data"]

        assert status["balance_ilc"] == "3"
        assert status["ecu_accrual"] == "8.5"
        assert status["claimability_state"] == WALLET_CLAIMABILITY_STATE_DEFERRED
        assert history["record_count"] == 1
        assert history["records"][0]["epoch_id"] == "epoch-001"
        assert history["records"][0]["settled_amount_ilc"] == "3"
        assert export["settled_balance_ilc"] == "3"
        assert export["ecu_accrual"] == "8.5"
        assert summary["reward_total_ilc"] == "3"
        assert summary["epoch_record_count"] == 1


def test_history_and_export_are_bound_to_same_settled_runtime_root_and_receipt_linkage() -> None:
    with TestClient(create_app()) as client:
        agent_id = _seed_wallet_runtime(client)["agent_id"]
        runtime = client.app.state.public_wallet_runtime
        status = runtime.wallet_status(agent_id=agent_id)["data"]
        history = runtime.wallet_history(agent_id=agent_id)["data"]
        export = runtime.wallet_export(agent_id=agent_id)["data"]
        summary = runtime.ledger_summary(agent_id=agent_id)["data"]

        settled_root = status["settled_runtime_root_ref"]
        receipt_ref = status["latest_balance_receipt_ref"]

        assert settled_root.startswith("wallet_state_sha256:")
        assert receipt_ref.startswith("balance_receipt_sha256:")
        assert history["settled_runtime_root_ref"] == settled_root
        assert export["settled_runtime_root_ref"] == settled_root
        assert summary["settled_runtime_root_ref"] == settled_root
        assert history["latest_balance_receipt_ref"] == receipt_ref
        assert export["latest_balance_receipt_ref"] == receipt_ref
        assert summary["latest_balance_receipt_ref"] == receipt_ref


def test_settled_runtime_root_ref_changes_when_settled_state_changes() -> None:
    with TestClient(create_app()) as client:
        agent_id = _seed_wallet_runtime(client)["agent_id"]
        runtime = client.app.state.public_wallet_runtime
        first_status = runtime.wallet_status(agent_id=agent_id)["data"]
        first_ref = first_status["settled_runtime_root_ref"]

        client.app.state.public_lifecycle_runtime.commit_settled_epoch(
            agent_id=agent_id,
            epoch_id="epoch-002",
            reward_delta_ilc="2",
        )
        second_status = runtime.wallet_status(agent_id=agent_id)["data"]
        assert second_status["settled_runtime_root_ref"] != first_ref


def test_wallet_runtime_rejects_protocol_pool_and_reserve_accounts() -> None:
    with TestClient(create_app()) as client:
        runtime = client.app.state.public_wallet_runtime
        for account_id in (PERFORMER_CARRY_FORWARD_ACCOUNT_ID, PROTOCOL_RESERVE_ACCOUNT_ID):
            with pytest.raises(Exception) as exc_info:
                runtime.wallet_status(agent_id=account_id)
            assert getattr(exc_info.value, "token", None) == "wallet_protocol_account_not_user_wallet"


def test_wallet_runtime_reports_persisted_claimability_state() -> None:
    with TestClient(create_app()) as client:
        agent_id = _seed_wallet_runtime(client)["agent_id"]
        store = client.app.state.public_lifecycle_runtime.wallet_store
        row = store.get_wallet(agent_id)
        assert row is not None
        row["claimability_state"] = "proof_claimability_authorized"
        history = store.get_wallet_history(agent_id)
        assert history is not None
        store.put_wallet_and_history(agent_id, row, history)

        status = client.app.state.public_wallet_runtime.wallet_status(agent_id=agent_id)["data"]
        assert status["claimability_state"] == "proof_claimability_authorized"


def test_wallet_runtime_rejects_noncanonical_persisted_claimability_state() -> None:
    with TestClient(create_app()) as client:
        agent_id = _seed_wallet_runtime(client)["agent_id"]
        store = client.app.state.public_lifecycle_runtime.wallet_store
        row = store.get_wallet(agent_id)
        assert row is not None
        row["claimability_state"] = " deferred "
        history = store.get_wallet_history(agent_id)
        assert history is not None
        store.put_wallet_and_history(agent_id, row, history)

        with pytest.raises(Exception) as exc_info:
            client.app.state.public_wallet_runtime.wallet_status(agent_id=agent_id)
        assert getattr(exc_info.value, "token", None) == "lifecycle_claimability_state_invalid"


def test_ledger_summary_uses_one_lifecycle_snapshot_read(monkeypatch: pytest.MonkeyPatch) -> None:
    with TestClient(create_app()) as client:
        agent_id = _seed_wallet_runtime(client)["agent_id"]
        runtime = client.app.state.public_wallet_runtime
        lifecycle_runtime = client.app.state.public_lifecycle_runtime
        original = lifecycle_runtime.lifecycle_snapshot
        calls = 0

        def counting_lifecycle_snapshot(*, agent_id: str) -> dict:
            nonlocal calls
            calls += 1
            return original(agent_id=agent_id)

        monkeypatch.setattr(lifecycle_runtime, "lifecycle_snapshot", counting_lifecycle_snapshot)
        payload = runtime.ledger_summary(agent_id=agent_id)
        assert payload["token"] == "ledger_summary_found"
        assert calls == 1


def test_phase_1378_closes_public_wallet_http_routes_and_no_prohibited_operations_are_introduced() -> None:
    with TestClient(create_app()) as client:
        for route_path in EXPECTED_ROUTE_PATHS:
            concrete_path = route_path.replace("{agent_id}", "agent-alpha")
            assert client.get(concrete_path).status_code == 404
        assert client.post("/v1/public/wallet/agent-alpha/status", json={}).status_code == 404
    server_text = _read(SERVER_PATH)
    assert "/v1/public/wallet/{agent_id}/withdraw" not in server_text
    assert "/v1/public/wallet/{agent_id}/transfer" not in server_text
    assert "/v1/public/wallet/{agent_id}/spend" not in server_text
    assert "/v1/public/wallet/{agent_id}/mint" not in server_text


def test_phase_653_main_commit_touches_exactly_runtime_scope_paths() -> None:
    _require_commit_or_skip(PHASE_653_SUBJECT_TOKENS)
    commit_ref = _resolve_commit_ref(
        subject_tokens=PHASE_653_SUBJECT_TOKENS,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_653_main_commit_touches_no_adr_or_decision_log_paths() -> None:
    _require_commit_or_skip(PHASE_653_SUBJECT_TOKENS)
    commit_ref = _resolve_commit_ref(
        subject_tokens=PHASE_653_SUBJECT_TOKENS,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith("docs/adr/") for path in changed_paths)
    assert not any(path.startswith("docs/specs/ilc_cdl_") for path in changed_paths)
    assert not any(path.startswith("docs/specs/ilc_cdl-") for path in changed_paths)


def test_phase_653_backfill_commit_touches_exactly_walkthrough_and_status() -> None:
    _require_commit_or_skip(PHASE_653_BACKFILL_SUBJECT_TOKENS)
    commit_ref = _resolve_commit_ref(
        subject_tokens=PHASE_653_BACKFILL_SUBJECT_TOKENS,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS


def test_phase_653_backfill_commit_touches_no_runtime_or_constitutional_paths() -> None:
    _require_commit_or_skip(PHASE_653_BACKFILL_SUBJECT_TOKENS)
    commit_ref = _resolve_commit_ref(
        subject_tokens=PHASE_653_BACKFILL_SUBJECT_TOKENS,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith("ilc_core/") for path in changed_paths)
    assert not any(path.startswith("docs/adr/") for path in changed_paths)
