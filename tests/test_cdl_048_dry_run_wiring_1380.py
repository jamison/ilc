from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from ilc_core.ledger.cdl048_conversion_sweeper_runtime import (
    CDL048_ACTIVATED_PHASE_1388_TOKEN,
    CDL048_DRY_RUN_WIRE_RUNTIME_VERSION,
    CDL048_DRY_RUN_WIRING_TOKEN,
    CDL048_NOT_ACTIVATED_PHASE_1380_TOKEN,
    DOUBLE_ENTRY_CONSERVATION_PROVEN_WIRE_LEVEL_PHASE_1380_TOKEN,
    GATE_CLOSED_STATE_CONFIRMED_PHASE_1380_TOKEN,
    Cdl048ConversionSweeperRuntimeError,
    build_cdl048_dry_run_wire_quote,
    canonical_dry_run_wire_quote_json,
    conversion_dry_run_wire_quote_payload,
    conversion_sweeper_state_root,
    empty_conversion_sweeper_state,
    register_ecu_lot,
)


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "ilc_core/ledger/cdl048_conversion_sweeper_runtime.py"
PROMPT = (
    ROOT
    / "docs/antigravity_tasks/antigravity_prompt__phase_1380_g8_cdl_048_dry_run_wiring.md"
)
WALKTHROUGH = ROOT / "docs/phases/phase_1380_cdl_048_dry_run_wiring_walkthrough.md"
STATUS = ROOT / "docs/phases/STATUS.md"
INDEX = ROOT / "docs/PLANNING_INDEX.md"
FORWARD_PLAN = (
    ROOT / "docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.2.md"
)
GROUPING = ROOT / "docs/specs/ilc_window_1369_1390_candidate_phase_grouping_v0.1.md"
CDL_REGISTER = ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"

REQUIRED_TOKENS = (
    "cdl_048_dry_run_wiring_phase_1380",
    "cdl_048_not_activated_phase_1380",
    "gate_closed_state_confirmed_phase_1380",
    "double_entry_conservation_proven_wire_level_phase_1380",
)


def _sha_ref(prefix: str, char: str) -> str:
    return f"{prefix}:{char * 64}"


def _registered_state():
    return register_ecu_lot(
        empty_conversion_sweeper_state(),
        lot_id="lot:phase-1380-alpha",
        agent_id="agent:phase-1380-alpha",
        amount_ecu="10.5",
        issue_epoch=20,
        origin="phase-1380-dry-run-fixture",
        funding_provenance=("receipt:phase-1380-a", "receipt:phase-1380-b"),
    )


def _quote(**overrides):
    args = {
        "state": _registered_state(),
        "lot_id": "lot:phase-1380-alpha",
        "agent_id": "agent:phase-1380-alpha",
        "conversion_epoch": 24,
        "settled_runtime_epoch": 24,
        "wallet_state_root": _sha_ref("wallet_state_sha256", "a"),
        "settled_runtime_root": _sha_ref("settled_runtime_sha256", "b"),
        "proposed_p_e": "1.25",
    }
    args.update(overrides)
    return build_cdl048_dry_run_wire_quote(**args)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _error_token(exc_info: pytest.ExceptionInfo[BaseException]) -> str | None:
    return getattr(exc_info.value, "token", None)


def test_phase_1380_dry_run_quote_is_gate_closed_and_quote_only() -> None:
    quote = _quote()
    payload = conversion_dry_run_wire_quote_payload(quote)

    assert quote.runtime_version == CDL048_DRY_RUN_WIRE_RUNTIME_VERSION
    assert quote.gate_closed is True
    assert quote.quote_only is True
    assert quote.conversion_activation_authorized is False
    assert quote.ledger_write_authorized is False
    assert quote.wallet_write_authorized is False
    assert quote.public_claimability_activated is False
    assert payload["gate_closed"] is True
    assert payload["quote_only"] is True
    assert payload["conversion_activation_authorized"] is False
    assert payload["ledger_write_authorized"] is False
    assert payload["wallet_write_authorized"] is False
    assert payload["public_claimability_activated"] is False

    for token in REQUIRED_TOKENS:
        assert token in quote.tokens
        assert token in payload["tokens"]


def test_phase_1380_wire_quote_proves_double_entry_conservation_without_state_mutation() -> None:
    state = _registered_state()
    state_root = conversion_sweeper_state_root(state)
    quote = _quote(state=state)
    payload = conversion_dry_run_wire_quote_payload(quote)

    assert quote.amount_ecu_debit == Decimal("10.5")
    assert quote.effective_p_e == Decimal("1.250000000")
    assert quote.debit_value_ilc == Decimal("13.125000000")
    assert quote.amount_ilc_credit == Decimal("13.125000000")
    assert quote.conservation_delta_ilc == Decimal("0")
    assert quote.double_entry_conservation_proven is True
    assert quote.sweeper_state_root_before == state_root
    assert quote.sweeper_state_root_after == state_root
    assert conversion_sweeper_state_root(state) == state_root
    assert state.lots[0].conversion_status == "open"
    assert payload["amount_ecu_debit"] == "10.5"
    assert payload["amount_ilc_credit"] == "13.125"
    assert payload["conservation_delta_ilc"] == "0"


def test_phase_1380_uses_cdl_030_p_e_clamp_and_preserves_price_gate_closed() -> None:
    floor_quote = _quote(proposed_p_e="0.50")
    ceiling_quote = _quote(proposed_p_e="1.50")

    assert floor_quote.effective_p_e == Decimal("0.75")
    assert floor_quote.p_e_clamp_applied is True
    assert floor_quote.p_e_clamp_direction == "floor"
    assert floor_quote.amount_ilc_credit == Decimal("7.875000000")
    assert floor_quote.p_e_decision_token == "live_price_adjustment_not_activated_phase_1351"

    assert ceiling_quote.effective_p_e == Decimal("1.30")
    assert ceiling_quote.p_e_clamp_applied is True
    assert ceiling_quote.p_e_clamp_direction == "ceiling"
    assert ceiling_quote.amount_ilc_credit == Decimal("13.650000000")
    assert ceiling_quote.p_e_decision_token == "live_price_adjustment_not_activated_phase_1351"


def test_phase_1380_rejects_invalid_activation_flag_and_invalid_p_e_inputs() -> None:
    with pytest.raises(Cdl048ConversionSweeperRuntimeError) as flag_exc:
        _quote(activation_requested="yes")
    assert _error_token(flag_exc) == "cdl048_activation_request_flag_invalid"

    with pytest.raises(Cdl048ConversionSweeperRuntimeError) as price_exc:
        _quote(proposed_p_e=1.25)
    assert _error_token(price_exc) == "cdl048_p_e_quote_invalid"
    assert "proposed_price_must_be_exact_decimal" in str(price_exc.value)


def test_phase_1380_canonical_quote_json_is_stable_and_sorted() -> None:
    quote = _quote()
    payload = conversion_dry_run_wire_quote_payload(quote)
    encoded = canonical_dry_run_wire_quote_json(quote)

    assert encoded.startswith(
        '{"agent_id":"agent:phase-1380-alpha",'
        '"amount_ecu_debit":"10.5",'
    )
    assert canonical_dry_run_wire_quote_json(quote) == encoded
    assert '"gate_closed":true' in encoded
    assert '"ledger_write_authorized":false' in encoded
    assert '"tokens":[' in encoded
    assert payload == quote.to_canonical_record()


def test_phase_1380_frontier_docs_record_non_activation_and_prerequisites() -> None:
    for path in (PROMPT, WALKTHROUGH, STATUS, INDEX, FORWARD_PLAN, GROUPING):
        text = _read(path)
        for token in REQUIRED_TOKENS:
            assert token in text

    runtime = _read(RUNTIME)
    assert CDL048_DRY_RUN_WIRING_TOKEN in runtime
    assert GATE_CLOSED_STATE_CONFIRMED_PHASE_1380_TOKEN in runtime
    assert DOUBLE_ENTRY_CONSERVATION_PROVEN_WIRE_LEVEL_PHASE_1380_TOKEN in runtime
    assert CDL048_ACTIVATED_PHASE_1388_TOKEN in runtime

    register = _read(CDL_REGISTER)
    cdl048_row = next(line for line in register.splitlines() if line.startswith("| CDL-048 |"))
    assert "| ratified |" in cdl048_row
    assert "ratified_phase: 419" in cdl048_row
