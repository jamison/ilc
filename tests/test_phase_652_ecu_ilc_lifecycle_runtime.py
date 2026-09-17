from __future__ import annotations

import subprocess
from decimal import Decimal
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from ilc_core.epoch.epoch_emission_runtime import C_MAX_ILC
from ilc_core.ledger.ecu_ilc_lifecycle_runtime import (
    LIFECYCLE_C_MAX_ILC,
    LIFECYCLE_MAX_AGENT_ID_BYTES,
    LIFECYCLE_MAX_EPOCH_ID_BYTES,
    EcuIlcLifecycleRuntimeError,
    _epoch_history_sort_key,
    _stable_digest,
)
from ilc_core.server import create_app

DOC_PATH = Path("docs/specs/ilc_ecu_ilc_lifecycle_runtime_652_v0.1.md")
TEST_PATH = Path("tests/test_phase_652_ecu_ilc_lifecycle_runtime.py")
WALKTHROUGH_PATH = Path("docs/phases/phase_652_g8_ecu_ilc_lifecycle_runtime_walkthrough.md")
STATUS_PATH = Path("docs/phases/STATUS.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_652_SUBJECT_TOKEN = "phase 652 ecu/ilc lifecycle runtime"
PHASE_652_BACKFILL_SUBJECT_TOKEN = "phase 652 walkthrough and status backfill"
AGENT_ID = "a" * 96
ALLOWED_MAIN_PREFIXES = {
    str(DOC_PATH),
    str(TEST_PATH),
    "ilc_core/server.py",
    "ilc_core/ledger/ecu_ilc_lifecycle_runtime.py",
}
REQUIRED_HEADINGS = (
    "## 1. Runtime target and inherited lifecycle law",
    "## 2. Visible ECU runtime surface",
    "## 3. Delayed visible ILC settlement runtime surface",
    "## 4. Coupling-invariants diagnostic surface",
    "## 5. Exact-numeric, non-finite, and fail-closed discipline",
    "## 6. Explicit exclusions and preserved boundaries",
)
REQUIRED_TOKENS = (
    "ecu_ilc_lifecycle_runtime_652_live",
    "ecu_visibility_read_only_runtime_live",
    "delayed_ilc_visibility_post_epoch_commit_runtime_live",
    "coupling_invariants_diagnostic_surface_present_in_652",
    "coupling_diagnostic_is_read_only_and_not_governance_lock_claim",
    "claimability_state_remains_deferred_in_652",
    "no_spend_transfer_withdrawal_or_wallet_write_in_652",
    "exact_numeric_and_non_finite_rules_apply_to_lifecycle_runtime",
)


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


def _find_commit_ref(*, subject_token: str) -> str | None:
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
        if subject_token in subject.lower():
            return commit_hash
    return None


def _require_commit_or_skip(subject_token: str) -> None:
    if _find_commit_ref(subject_token=subject_token) is None:
        pytest.skip(f"commit_not_yet_present:{subject_token}")


def test_runtime_doc_exists_and_contains_required_headings() -> None:
    text = _read(DOC_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_runtime_doc_contains_required_tokens() -> None:
    text = _read(DOC_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_visible_ecu_surface_is_read_only() -> None:
    app = create_app()
    with TestClient(app):
        app.state.ecu_active_layer_runtime.set_accrued_ecu(AGENT_ID, "10.5")
        payload = app.state.public_lifecycle_runtime.lifecycle_status(agent_id=AGENT_ID)["data"]
        assert payload["balance_ecu"] == "10.5"
        assert payload["balance_ilc"] == "0"
        for forbidden_field in (
            "spend_authority",
            "transfer_authority",
            "withdrawal_authority",
            "wallet_write_authority",
        ):
            assert forbidden_field not in payload


def test_delayed_visible_ilc_appears_only_after_epoch_commit() -> None:
    app = create_app()
    with TestClient(app):
        app.state.ecu_active_layer_runtime.set_accrued_ecu(AGENT_ID, "4")
        before_payload = app.state.public_lifecycle_runtime.lifecycle_status(agent_id=AGENT_ID)["data"]
        assert before_payload["balance_ilc"] == "0"
        assert before_payload["last_settled_epoch_id"] is None
        assert before_payload["latest_balance_receipt"] is None

        commit_result = app.state.public_lifecycle_runtime.commit_settled_epoch(
            agent_id=AGENT_ID,
            epoch_id="epoch-001",
            reward_delta_ilc="3.25",
        )
        assert commit_result["token"] == "lifecycle_epoch_commit_applied"

        after_payload = app.state.public_lifecycle_runtime.lifecycle_status(agent_id=AGENT_ID)["data"]
        assert after_payload["balance_ilc"] == "3.25"
        assert after_payload["last_settled_epoch_id"] == "epoch-001"
        assert after_payload["latest_balance_receipt"]["settlement_status"] == "applied"


def test_same_epoch_same_delta_is_idempotent_and_conflicting_replay_fails_closed() -> None:
    app = create_app()
    with TestClient(app):
        first = app.state.public_lifecycle_runtime.commit_settled_epoch(
            agent_id=AGENT_ID,
            epoch_id="epoch-001",
            reward_delta_ilc="3.25",
        )
        assert first["token"] == "lifecycle_epoch_commit_applied"

        replay = app.state.public_lifecycle_runtime.commit_settled_epoch(
            agent_id=AGENT_ID,
            epoch_id="epoch-001",
            reward_delta_ilc="3.25",
        )
        assert replay["token"] == "lifecycle_epoch_commit_idempotent_replay"
        assert replay["data"]["balance_ilc"] == "3.25"

        with pytest.raises(Exception) as exc_info:
            app.state.public_lifecycle_runtime.commit_settled_epoch(
                agent_id=AGENT_ID,
                epoch_id="epoch-001",
                reward_delta_ilc="4.00",
            )
        assert getattr(exc_info.value, "token", None) == "lifecycle_epoch_replay_conflict"

        status = app.state.public_lifecycle_runtime.lifecycle_status(agent_id=AGENT_ID)
        assert status["data"]["balance_ilc"] == "3.25"


def test_numeric_epoch_history_sorts_numerically_not_lexicographically() -> None:
    app = create_app()
    with TestClient(app):
        runtime = app.state.public_lifecycle_runtime
        runtime.commit_settled_epoch(agent_id=AGENT_ID, epoch_id="10", reward_delta_ilc="1")
        runtime.commit_settled_epoch(agent_id=AGENT_ID, epoch_id="2", reward_delta_ilc="1")
        runtime.commit_settled_epoch(agent_id=AGENT_ID, epoch_id="1", reward_delta_ilc="1")

        history = runtime.lifecycle_snapshot(agent_id=AGENT_ID)["wallet_history"]["balance_history"]
        assert [entry["epoch_id"] for entry in history] == ["1", "2", "10"]


def test_lifecycle_rejects_balance_above_cmax() -> None:
    app = create_app()
    with TestClient(app):
        with pytest.raises(Exception) as exc_info:
            app.state.public_lifecycle_runtime.commit_settled_epoch(
                agent_id=AGENT_ID,
                epoch_id="epoch-001",
                reward_delta_ilc="25920000.000000001",
            )
        assert getattr(exc_info.value, "token", None) == "lifecycle_balance_exceeds_c_max"


def test_lifecycle_rejects_subquantum_reward_delta() -> None:
    app = create_app()
    with TestClient(app):
        with pytest.raises(Exception) as exc_info:
            app.state.public_lifecycle_runtime.commit_settled_epoch(
                agent_id=AGENT_ID,
                epoch_id="epoch-001",
                reward_delta_ilc="0.0000000001",
            )
        assert getattr(exc_info.value, "token", None) == "lifecycle_reward_delta_invalid"


def test_lifecycle_rejects_oversized_agent_and_epoch_ids() -> None:
    app = create_app()
    with TestClient(app):
        with pytest.raises(Exception) as agent_exc:
            app.state.public_lifecycle_runtime.commit_settled_epoch(
                agent_id="a" * (LIFECYCLE_MAX_AGENT_ID_BYTES + 1),
                epoch_id="epoch-001",
                reward_delta_ilc="1",
            )
        assert getattr(agent_exc.value, "token", None) == "agent_id_required"

        with pytest.raises(Exception) as epoch_exc:
            app.state.public_lifecycle_runtime.commit_settled_epoch(
                agent_id=AGENT_ID,
                epoch_id="e" * (LIFECYCLE_MAX_EPOCH_ID_BYTES + 1),
                reward_delta_ilc="1",
            )
        assert getattr(epoch_exc.value, "token", None) == "epoch_id_required"


def test_lifecycle_rejects_whitespace_padded_ids() -> None:
    app = create_app()
    with TestClient(app):
        with pytest.raises(Exception) as agent_exc:
            app.state.public_lifecycle_runtime.commit_settled_epoch(
                agent_id=f" {AGENT_ID} ",
                epoch_id="epoch-001",
                reward_delta_ilc="1",
            )
        assert getattr(agent_exc.value, "token", None) == "agent_id_required"

        with pytest.raises(Exception) as epoch_exc:
            app.state.public_lifecycle_runtime.commit_settled_epoch(
                agent_id=AGENT_ID,
                epoch_id=" epoch-001 ",
                reward_delta_ilc="1",
            )
        assert getattr(epoch_exc.value, "token", None) == "epoch_id_required"


def test_lifecycle_rejects_non_canonical_agent_id_format() -> None:
    app = create_app()
    with TestClient(app):
        with pytest.raises(Exception) as exc_info:
            app.state.public_lifecycle_runtime.commit_settled_epoch(
                agent_id="agent-a",
                epoch_id="epoch-001",
                reward_delta_ilc="1",
            )
        assert getattr(exc_info.value, "token", None) == "agent_id_required"


def test_lifecycle_cmax_imports_epoch_emission_cmax() -> None:
    assert LIFECYCLE_C_MAX_ILC == C_MAX_ILC


def test_lifecycle_stable_digest_rejects_decimal_inside_tuple() -> None:
    with pytest.raises(EcuIlcLifecycleRuntimeError) as exc_info:
        _stable_digest({"tuple_payload": ("encoded", Decimal("1"))})
    assert exc_info.value.token == "lifecycle_stable_digest_decimal_unencoded"


@pytest.mark.parametrize("bad_float", [0.25, float("nan"), float("inf")])
def test_lifecycle_stable_digest_rejects_float_scalars(bad_float: float) -> None:
    with pytest.raises(EcuIlcLifecycleRuntimeError) as exc_info:
        _stable_digest({"float_payload": bad_float})
    assert exc_info.value.token == "lifecycle_stable_digest_float_unencoded"


def test_epoch_history_sort_key_places_non_decimal_epoch_ids_after_numeric_ids() -> None:
    items = [
        {"epoch_id": "epoch-2"},
        {"epoch_id": "10"},
        {"epoch_id": "2"},
    ]

    assert [item["epoch_id"] for item in sorted(items, key=_epoch_history_sort_key)] == [
        "2",
        "10",
        "epoch-2",
    ]


def test_coupling_invariants_diagnostic_surface_is_present_and_read_only() -> None:
    app = create_app()
    with TestClient(app):
        payload = app.state.public_lifecycle_runtime.coupling_invariants_diagnostic(
            graph_node_count=len(app.state.graph.nodes),
        )["data"]
        assert payload["graph_truth_upstream"] is True
        assert payload["delayed_ilc_requires_epoch_commit"] is True
        assert payload["diagnostic_only"] is True
        assert payload["governance_lock_closed"] is False


def test_phase_1378_closes_public_lifecycle_http_routes() -> None:
    app = create_app()
    with TestClient(app) as client:
        assert client.get("/v1/public/lifecycle/agent-a").status_code == 404
        assert client.get("/v1/public/lifecycle/coupling-invariants").status_code == 404


def test_claimability_remains_deferred_and_non_finite_inputs_fail_closed() -> None:
    app = create_app()
    with TestClient(app):
        status = app.state.public_lifecycle_runtime.lifecycle_status(agent_id=AGENT_ID)
        assert status["data"]["claimability_state"] == "deferred"
        with pytest.raises(Exception) as exc_info:
            app.state.public_lifecycle_runtime.commit_settled_epoch(
                agent_id=AGENT_ID,
                epoch_id="epoch-001",
                reward_delta_ilc="Infinity",
            )
        assert getattr(exc_info.value, "token", None) == "lifecycle_reward_delta_invalid"


def test_no_wallet_widening_or_governance_lock_claim_is_made() -> None:
    text = _read(DOC_PATH)
    assert "It is not a claim that the" in text
    assert "coupling-invariants governance lock is already closed." in text
    assert "no wallet write authority" in text
    assert "no spend authority" in text
    assert "no transfer authority" in text
    assert "no withdrawal authority" in text


def test_main_commit_touches_expected_runtime_scope_without_decision_log_mutation() -> None:
    _require_commit_or_skip(PHASE_652_SUBJECT_TOKEN)
    commit_ref = _find_commit_ref(subject_token=PHASE_652_SUBJECT_TOKEN)
    assert commit_ref is not None
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DOC_PATH) in changed_paths
    assert str(TEST_PATH) in changed_paths
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith("docs/adr/") for path in changed_paths)
    unexpected = {path for path in changed_paths if path not in ALLOWED_MAIN_PREFIXES}
    assert not unexpected


def test_backfill_commit_touches_walkthrough_and_status_only() -> None:
    _require_commit_or_skip(PHASE_652_BACKFILL_SUBJECT_TOKEN)
    commit_ref = _find_commit_ref(subject_token=PHASE_652_BACKFILL_SUBJECT_TOKEN)
    assert commit_ref is not None
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == {str(WALKTHROUGH_PATH), str(STATUS_PATH)}


def test_phase_652_phase_test_passes_post_commit() -> None:
    _require_commit_or_skip(PHASE_652_SUBJECT_TOKEN)
    result = subprocess.run(
        [
            "bash",
            "-lc",
            "PATH=.venv/bin:$PATH .venv/bin/pytest "
            "tests/test_phase_652_ecu_ilc_lifecycle_runtime.py "
            "-q -k 'not test_phase_652_phase_test_passes_post_commit'",
        ],
        capture_output=True,
        check=True,
        text=True,
    )
    assert "passed" in result.stdout
