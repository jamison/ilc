from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from ilc_core.ledger.cdl048_conversion_sweeper_runtime import (
    CDL048_CONVERSION_DEADLINE_ISSUANCE_EPOCHS,
    CDL048_CONVERSION_SWEEPER_RUNTIME_VERSION,
    CONVERSION_SWEEPER_NO_PUBLIC_CLAIMABILITY_TOKEN,
    ECU_LOT_DEADLINE_ENFORCEMENT_TOKEN,
    WALLET_WITHDRAWAL_TRANSFER_SPEND_BLOCKED_TOKEN,
    Cdl048ConversionSweeperRuntimeError,
    ConversionSweeperState,
    canonical_json,
    canonical_receipt_json,
    conversion_receipt_payload,
    conversion_sweeper_state_root,
    convert_ecu_lot,
    deadline_status,
    empty_conversion_sweeper_state,
    export_conversion_sweeper_state,
    register_ecu_lot,
)


RUNTIME_PATH = Path("ilc_core/ledger/cdl048_conversion_sweeper_runtime.py")
SPEC_PATH = Path("docs/specs/ilc_cdl048_conversion_sweeper_runtime_skeleton_1274_v0.1.md")
WALKTHROUGH_PATH = Path("docs/phases/phase_1274_cdl048_conversion_sweeper_runtime_skeleton_walkthrough.md")
STATUS_PATH = Path("docs/phases/STATUS.md")
PLANNING_INDEX_PATH = Path("docs/PLANNING_INDEX.md")
ROADMAP_PATH = Path("docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md")
GUARDRAIL_PATH = Path("tools/check_sensitive_runtime_coding_taboos.py")
CDL_REGISTER_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
REQUIRED_TOKENS = (
    "cdl048_conversion_sweeper_runtime_skeleton_phase_1274.v0.1",
    "conversion_sweeper_no_public_claimability_activation_phase_1274",
    "ecu_lot_deadline_epoch_enforcement_recorded_phase_1274",
    "wallet_withdrawal_transfer_spend_still_blocked_phase_1274",
)


def _registered_state() -> ConversionSweeperState:
    return register_ecu_lot(
        empty_conversion_sweeper_state(),
        lot_id="lot:alpha",
        agent_id="agent:alpha",
        amount_ecu="0010.5000",
        issue_epoch=8,
        origin="epoch-attribution:alpha",
        funding_provenance=["receipt:001", "receipt:002"],
    )


def _error_token(exc_info: pytest.ExceptionInfo[BaseException]) -> str | None:
    return getattr(exc_info.value, "token", None)


def _sha_ref(prefix: str, char: str) -> str:
    return f"{prefix}:{char * 64}"


def test_required_tokens_and_initial_non_activation_export_are_present() -> None:
    assert CDL048_CONVERSION_SWEEPER_RUNTIME_VERSION == (
        "cdl048_conversion_sweeper_runtime_skeleton_phase_1274.v0.1"
    )
    state_export = export_conversion_sweeper_state(empty_conversion_sweeper_state())

    for token in (
        CONVERSION_SWEEPER_NO_PUBLIC_CLAIMABILITY_TOKEN,
        ECU_LOT_DEADLINE_ENFORCEMENT_TOKEN,
        WALLET_WITHDRAWAL_TRANSFER_SPEND_BLOCKED_TOKEN,
    ):
        assert token in state_export["tokens"]

    assert state_export["public_claimability_activated"] is False
    assert state_export["wallet_withdrawal_enabled"] is False
    assert state_export["wallet_transfer_enabled"] is False
    assert state_export["wallet_spend_enabled"] is False


def test_register_ecu_lot_records_deadline_and_exact_amount_without_float_state() -> None:
    state = _registered_state()
    lot = state.lots[0]

    assert CDL048_CONVERSION_DEADLINE_ISSUANCE_EPOCHS == 4
    assert lot.amount_ecu == Decimal("10.5000")
    assert lot.deadline_epoch == 12
    assert lot.conversion_status == "open"

    state_export = export_conversion_sweeper_state(state)
    assert state_export["lots"][0]["amount_ecu"] == "10.5"
    assert state_export["lots"][0]["issue_epoch"] == 8
    assert state_export["lots"][0]["deadline_epoch"] == 12
    assert state_export["lots"][0]["funding_provenance"] == ["receipt:001", "receipt:002"]


def test_deadline_status_uses_issuance_epoch_math_only() -> None:
    lot = _registered_state().lots[0]

    assert deadline_status(lot=lot, current_epoch=11)["deadline_status"] == "open"
    at_deadline = deadline_status(lot=lot, current_epoch=12)
    assert at_deadline["deadline_status"] == "deadline_epoch"
    assert at_deadline["epochs_remaining"] == 0
    expired = deadline_status(lot=lot, current_epoch=13)
    assert expired["deadline_status"] == "expired"
    assert expired["token"] == ECU_LOT_DEADLINE_ENFORCEMENT_TOKEN


@pytest.mark.parametrize(
    ("amount", "token"),
    (
        (1.25, "cdl048_amount_float_forbidden"),
        ("NaN", "cdl048_amount_non_finite"),
        (Decimal("Infinity"), "cdl048_amount_non_finite"),
        ("-1", "cdl048_amount_must_be_positive"),
        ("0", "cdl048_amount_must_be_positive"),
    ),
)
def test_amount_boundary_rejects_float_non_finite_and_non_positive_values(
    amount: object,
    token: str,
) -> None:
    with pytest.raises(Cdl048ConversionSweeperRuntimeError) as exc_info:
        register_ecu_lot(
            empty_conversion_sweeper_state(),
            lot_id="lot:bad",
            agent_id="agent:alpha",
            amount_ecu=amount,
            issue_epoch=1,
            origin="origin",
            funding_provenance=["receipt:001"],
        )
    assert _error_token(exc_info) == token


def test_conversion_receipt_is_canonical_and_keeps_public_claimability_disabled() -> None:
    state = _registered_state()
    before_root = conversion_sweeper_state_root(state)
    result = convert_ecu_lot(
        state,
        lot_id="lot:alpha",
        agent_id="agent:alpha",
        conversion_epoch=12,
        settled_runtime_epoch=12,
        wallet_state_root=_sha_ref("wallet_state_sha256", "a"),
        settled_runtime_root=_sha_ref("settled_runtime_sha256", "b"),
    )
    payload = conversion_receipt_payload(result.receipt)

    assert payload["runtime_version"] == CDL048_CONVERSION_SWEEPER_RUNTIME_VERSION
    assert payload["amount_ecu"] == "10.5"
    assert payload["sweeper_state_root_before"] == before_root
    assert payload["public_claimability_activated"] is False
    assert payload["wallet_withdrawal_enabled"] is False
    assert payload["wallet_transfer_enabled"] is False
    assert payload["wallet_spend_enabled"] is False
    assert payload["ecu_mint_authorized"] is False
    assert payload["ilc_settlement_authorized"] is False
    assert payload["receipt_sha256"] == result.receipt.receipt_sha256
    assert result.sweeper_state_root_after != before_root
    assert result.state.lots[0].conversion_status == "converted_internal_skeleton"
    assert canonical_receipt_json(result.receipt) == canonical_json(payload)


def test_conversion_after_deadline_fails_closed() -> None:
    with pytest.raises(Cdl048ConversionSweeperRuntimeError) as exc_info:
        convert_ecu_lot(
            _registered_state(),
            lot_id="lot:alpha",
            agent_id="agent:alpha",
            conversion_epoch=13,
            settled_runtime_epoch=13,
            wallet_state_root=_sha_ref("wallet_state_sha256", "a"),
            settled_runtime_root=_sha_ref("settled_runtime_sha256", "b"),
        )
    assert _error_token(exc_info) == "cdl048_conversion_deadline_expired"


def test_stale_or_missing_roots_fail_closed() -> None:
    with pytest.raises(Cdl048ConversionSweeperRuntimeError) as stale_exc:
        convert_ecu_lot(
            _registered_state(),
            lot_id="lot:alpha",
            agent_id="agent:alpha",
            conversion_epoch=12,
            settled_runtime_epoch=11,
            wallet_state_root=_sha_ref("wallet_state_sha256", "a"),
            settled_runtime_root=_sha_ref("settled_runtime_sha256", "b"),
        )
    assert _error_token(stale_exc) == "cdl048_settled_runtime_root_stale"

    with pytest.raises(Cdl048ConversionSweeperRuntimeError) as root_exc:
        convert_ecu_lot(
            _registered_state(),
            lot_id="lot:alpha",
            agent_id="agent:alpha",
            conversion_epoch=12,
            settled_runtime_epoch=12,
            wallet_state_root="",
            settled_runtime_root=_sha_ref("settled_runtime_sha256", "b"),
        )
    assert _error_token(root_exc) == "cdl048_wallet_state_root_required"

    with pytest.raises(Cdl048ConversionSweeperRuntimeError) as malformed_root:
        convert_ecu_lot(
            _registered_state(),
            lot_id="lot:alpha",
            agent_id="agent:alpha",
            conversion_epoch=12,
            settled_runtime_epoch=12,
            wallet_state_root="wallet_state_sha256:alpha",
            settled_runtime_root=_sha_ref("settled_runtime_sha256", "b"),
        )
    assert _error_token(malformed_root) == "cdl048_wallet_state_root_required"


def test_duplicate_lot_agent_mismatch_double_conversion_and_replay_fail_closed() -> None:
    state = _registered_state()
    with pytest.raises(Cdl048ConversionSweeperRuntimeError) as duplicate_lot:
        register_ecu_lot(
            state,
            lot_id="lot:alpha",
            agent_id="agent:alpha",
            amount_ecu="1",
            issue_epoch=9,
            origin="origin",
            funding_provenance=["receipt:003"],
        )
    assert _error_token(duplicate_lot) == "cdl048_lot_duplicate"

    with pytest.raises(Cdl048ConversionSweeperRuntimeError) as mismatch:
        convert_ecu_lot(
            state,
            lot_id="lot:alpha",
            agent_id="agent:other",
            conversion_epoch=12,
            settled_runtime_epoch=12,
            wallet_state_root=_sha_ref("wallet_state_sha256", "a"),
            settled_runtime_root=_sha_ref("settled_runtime_sha256", "b"),
        )
    assert _error_token(mismatch) == "cdl048_conversion_agent_mismatch"

    converted = convert_ecu_lot(
        state,
        lot_id="lot:alpha",
        agent_id="agent:alpha",
        conversion_epoch=12,
        settled_runtime_epoch=12,
        wallet_state_root=_sha_ref("wallet_state_sha256", "a"),
        settled_runtime_root=_sha_ref("settled_runtime_sha256", "b"),
    )
    with pytest.raises(Cdl048ConversionSweeperRuntimeError) as double_conversion:
        convert_ecu_lot(
            converted.state,
            lot_id="lot:alpha",
            agent_id="agent:alpha",
            conversion_epoch=12,
            settled_runtime_epoch=12,
            wallet_state_root=_sha_ref("wallet_state_sha256", "a"),
            settled_runtime_root=_sha_ref("settled_runtime_sha256", "b"),
        )
    assert _error_token(double_conversion) == "cdl048_conversion_duplicate_lot"

    replay_seed = ConversionSweeperState(
        lots=state.lots,
        conversion_keys=frozenset({converted.receipt.conversion_key_sha256}),
    )
    with pytest.raises(Cdl048ConversionSweeperRuntimeError) as replay:
        convert_ecu_lot(
            replay_seed,
            lot_id="lot:alpha",
            agent_id="agent:alpha",
            conversion_epoch=12,
            settled_runtime_epoch=12,
            wallet_state_root=_sha_ref("wallet_state_sha256", "a"),
            settled_runtime_root=_sha_ref("settled_runtime_sha256", "b"),
        )
    assert _error_token(replay) == "cdl048_conversion_replay_detected"


def test_conversion_key_binds_epoch_agent_lot_wallet_root_transition_and_settled_root() -> None:
    first = convert_ecu_lot(
        _registered_state(),
        lot_id="lot:alpha",
        agent_id="agent:alpha",
        conversion_epoch=12,
        settled_runtime_epoch=12,
        wallet_state_root=_sha_ref("wallet_state_sha256", "a"),
        settled_runtime_root=_sha_ref("settled_runtime_sha256", "b"),
    )
    different_wallet_root = convert_ecu_lot(
        _registered_state(),
        lot_id="lot:alpha",
        agent_id="agent:alpha",
        conversion_epoch=12,
        settled_runtime_epoch=12,
        wallet_state_root=_sha_ref("wallet_state_sha256", "c"),
        settled_runtime_root=_sha_ref("settled_runtime_sha256", "b"),
    )
    different_settled_root = convert_ecu_lot(
        _registered_state(),
        lot_id="lot:alpha",
        agent_id="agent:alpha",
        conversion_epoch=12,
        settled_runtime_epoch=12,
        wallet_state_root=_sha_ref("wallet_state_sha256", "a"),
        settled_runtime_root=_sha_ref("settled_runtime_sha256", "d"),
    )

    keys = {
        first.receipt.conversion_key_sha256,
        different_wallet_root.receipt.conversion_key_sha256,
        different_settled_root.receipt.conversion_key_sha256,
    }
    assert len(keys) == 3


def test_canonical_json_is_sorted_and_rejects_nan() -> None:
    assert canonical_json({"b": 1, "a": 2}) == '{"a":2,"b":1}'
    with pytest.raises(ValueError):
        canonical_json({"value": float("nan")})


def test_runtime_source_does_not_add_public_wallet_or_wall_clock_surfaces() -> None:
    source = RUNTIME_PATH.read_text(encoding="utf-8")
    header = "\n".join(source.splitlines()[:6])
    assert "PUBLIC_RC_EXCLUDE: internal_phase_helper_not_public_rc_launch_surface" in header
    assert "PUBLIC_RC_EXCLUDE_REASON: Phase 1274 CDL-048 conversion-sweeper skeleton" in header
    for forbidden in (
        "def withdraw",
        "def transfer",
        "def spend",
        "def sign",
        "mint_ecu(",
        "settle_ilc(",
        "datetime.now",
        "time.time",
        "import random",
        "assert ",
    ):
        assert forbidden not in source


def test_phase_docs_status_planning_and_roadmap_record_tokens_and_non_claims() -> None:
    for path in (SPEC_PATH, WALKTHROUGH_PATH, STATUS_PATH, PLANNING_INDEX_PATH, ROADMAP_PATH):
        text = path.read_text(encoding="utf-8")
        for token in REQUIRED_TOKENS:
            assert token in text
        assert "public claimability" in text
        assert "wallet withdrawal" in text
        assert "wallet transfer" in text
    assert "wallet spend" in text

    planning = PLANNING_INDEX_PATH.read_text(encoding="utf-8")
    assert "Window 1281-1288 is OPEN through Phase 1282 Fix1" in planning
    assert "Phase 1274 CDL-048 conversion-sweeper runtime skeleton" in planning
    assert "Phase 1283 is sensitive" in planning
    assert "phase_1275_claimability_proof_binding_runtime_requires_explicit_go" in STATUS_PATH.read_text(
        encoding="utf-8"
    )
    assert "public_rc_remains_blocked_after_phase_1274" in ROADMAP_PATH.read_text(encoding="utf-8")


def test_guardrail_scans_the_new_machine_json_runtime_surface() -> None:
    guardrail = GUARDRAIL_PATH.read_text(encoding="utf-8")
    assert "ilc_core/ledger/cdl048_conversion_sweeper_runtime.py" in guardrail
    runtime = RUNTIME_PATH.read_text(encoding="utf-8")
    assert "sort_keys=True" in runtime
    assert "allow_nan=False" in runtime


def test_cdl048_register_row_remains_ratified_without_phase_1274_mutation_claim() -> None:
    register = CDL_REGISTER_PATH.read_text(encoding="utf-8")
    cdl048_rows = [line for line in register.splitlines() if line.startswith("| CDL-048 |")]
    assert len(cdl048_rows) == 1
    assert "| ratified |" in cdl048_rows[0]
    assert "ratified_phase: 419" in cdl048_rows[0]
