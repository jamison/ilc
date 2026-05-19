from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from ilc_core.ledger.cdl048_conversion_sweeper_runtime import (
    CDL048_ACTIVATED_PHASE_1388_TOKEN,
    CDL048_ACTIVATION_RUNTIME_VERSION,
    CDL048_DRY_RUN_WIRE_RUNTIME_VERSION,
    CDL048_NOT_ACTIVATED_PHASE_1380_TOKEN,
    COUNSEL_CLEARANCE_PUBLIC_VERIFIER_API_PHASE_1388_TOKEN,
    FIRST_LIVE_VALUE_PATH_ACTIVATION_PHASE_1388_TOKEN,
    GATE_CLOSED_STATE_CONFIRMED_PHASE_1380_TOKEN,
    build_cdl048_dry_run_wire_quote,
    canonical_dry_run_wire_quote_json,
    conversion_dry_run_wire_quote_payload,
    conversion_sweeper_state_root,
    empty_conversion_sweeper_state,
    register_ecu_lot,
)


REPO = Path(__file__).resolve().parents[1]

PHASE_1387 = REPO / "docs/specs/ilc_pre_activation_hardening_gate_report_1387_rerun_v0.2.md"
PHASE_1387A_MATRIX = (
    REPO / "docs/specs/ilc_accepted_adr_cdl_public_rc_coverage_matrix_1387a_v0.1.md"
)
PHASE_1387A_FIREWALL = (
    REPO / "docs/specs/ilc_public_economics_admission_firewall_1387a_v0.1.md"
)
PHASE_1388A = REPO / "docs/specs/ilc_counsel_clearance_cdl_048_activation_1388a_v0.1.md"
PHASE_1388_SUCCESS = REPO / "docs/specs/ilc_counsel_clearance_1388_v0.1.md"
PHASE_1388_WALKTHROUGH = (
    REPO / "docs/phases/phase_1388_cdl_048_activation_counsel_clearance_walkthrough.md"
)
STATUS = REPO / "docs/phases/STATUS.md"
RUNTIME = REPO / "ilc_core/ledger/cdl048_conversion_sweeper_runtime.py"

SUCCESS_TOKENS = (
    CDL048_ACTIVATED_PHASE_1388_TOKEN,
    COUNSEL_CLEARANCE_PUBLIC_VERIFIER_API_PHASE_1388_TOKEN,
    FIRST_LIVE_VALUE_PATH_ACTIVATION_PHASE_1388_TOKEN,
)


def _sha_ref(prefix: str, char: str) -> str:
    return f"{prefix}:{char * 64}"


def _registered_state():
    return register_ecu_lot(
        empty_conversion_sweeper_state(),
        lot_id="lot:phase-1388-alpha",
        agent_id="agent:phase-1388-alpha",
        amount_ecu="10.5",
        issue_epoch=20,
        origin="phase-1388-activation-fixture",
        funding_provenance=("receipt:phase-1388-a", "receipt:phase-1388-b"),
    )


def _quote(*, activation_requested: bool):
    return build_cdl048_dry_run_wire_quote(
        _registered_state(),
        lot_id="lot:phase-1388-alpha",
        agent_id="agent:phase-1388-alpha",
        conversion_epoch=24,
        settled_runtime_epoch=24,
        wallet_state_root=_sha_ref("wallet_state_sha256", "a"),
        settled_runtime_root=_sha_ref("settled_runtime_sha256", "b"),
        proposed_p_e=Decimal("1.25"),
        activation_requested=activation_requested,
    )


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_1388_activation_quote_opens_value_path_but_not_public_claimability() -> None:
    quote = _quote(activation_requested=True)
    payload = conversion_dry_run_wire_quote_payload(quote)

    assert quote.runtime_version == CDL048_ACTIVATION_RUNTIME_VERSION
    assert quote.gate_closed is False
    assert quote.quote_only is False
    assert quote.conversion_activation_authorized is True
    assert quote.ledger_write_authorized is True
    assert quote.wallet_write_authorized is True
    assert quote.public_claimability_activated is False

    assert payload["gate_closed"] is False
    assert payload["quote_only"] is False
    assert payload["conversion_activation_authorized"] is True
    assert payload["ledger_write_authorized"] is True
    assert payload["wallet_write_authorized"] is True
    assert payload["public_claimability_activated"] is False

    for token in SUCCESS_TOKENS:
        assert token in quote.tokens
        assert token in payload["tokens"]
    assert CDL048_NOT_ACTIVATED_PHASE_1380_TOKEN not in quote.tokens
    assert GATE_CLOSED_STATE_CONFIRMED_PHASE_1380_TOKEN not in quote.tokens


def test_phase_1388_activation_quote_preserves_conservation_and_canonical_json() -> None:
    state = _registered_state()
    state_root = conversion_sweeper_state_root(state)
    quote = build_cdl048_dry_run_wire_quote(
        state,
        lot_id="lot:phase-1388-alpha",
        agent_id="agent:phase-1388-alpha",
        conversion_epoch=24,
        settled_runtime_epoch=24,
        wallet_state_root=_sha_ref("wallet_state_sha256", "a"),
        settled_runtime_root=_sha_ref("settled_runtime_sha256", "b"),
        proposed_p_e=Decimal("1.25"),
        activation_requested=True,
    )
    encoded = canonical_dry_run_wire_quote_json(quote)

    assert quote.debit_value_ilc == Decimal("13.125000000")
    assert quote.amount_ilc_credit == Decimal("13.125000000")
    assert quote.conservation_delta_ilc == Decimal("0")
    assert quote.double_entry_conservation_proven is True
    assert quote.sweeper_state_root_before == state_root
    assert quote.sweeper_state_root_after == state_root
    assert conversion_sweeper_state_root(state) == state_root
    assert encoded.startswith('{"agent_id":"agent:phase-1388-alpha",')
    assert canonical_dry_run_wire_quote_json(quote) == encoded
    assert '"public_claimability_activated":false' in encoded


def test_phase_1388_default_call_remains_phase_1380_gate_closed_dry_run() -> None:
    quote = _quote(activation_requested=False)

    assert quote.runtime_version == CDL048_DRY_RUN_WIRE_RUNTIME_VERSION
    assert quote.gate_closed is True
    assert quote.quote_only is True
    assert quote.conversion_activation_authorized is False
    assert quote.ledger_write_authorized is False
    assert quote.wallet_write_authorized is False
    assert quote.public_claimability_activated is False
    assert CDL048_NOT_ACTIVATED_PHASE_1380_TOKEN in quote.tokens
    assert CDL048_ACTIVATED_PHASE_1388_TOKEN not in quote.tokens


def test_phase_1388_prerequisite_records_are_present_and_passing() -> None:
    phase_1387 = _read(PHASE_1387)
    phase_1387a_matrix = _read(PHASE_1387A_MATRIX)
    phase_1387a_firewall = _read(PHASE_1387A_FIREWALL)
    phase_1388a = _read(PHASE_1388A)

    assert "pre_activation_hardening_gate_pass_phase_1387" in phase_1387
    assert "accepted_adr_cdl_runtime_coverage_matrix_phase_1387a" in phase_1387a_matrix
    assert "no_unrouted_accepted_cdl_adr_functionality_before_public_rc_phase_1387a" in phase_1387a_matrix
    assert "public_economics_requires_public_node_admission_verified_phase_1387a" in phase_1387a_firewall
    assert "private_visibility_excluded_from_public_economics_phase_1387a" in phase_1387a_firewall
    assert "counsel_clearance_cdl_048_activation_phase_1388a" in phase_1388a
    assert "self_counsel_decision_not_external_legal_opinion_phase_1388a" in phase_1388a


def test_phase_1388_success_record_walkthrough_and_status_tokens() -> None:
    combined = "\n".join(
        _read(path) for path in (PHASE_1388_SUCCESS, PHASE_1388_WALKTHROUGH, STATUS)
    )
    for token in SUCCESS_TOKENS:
        assert token in combined
    assert "Phase 1389 public claimability gate next" in combined


def test_phase_1388_runtime_source_records_activation_tokens_without_public_rc_result() -> None:
    text = _read(RUNTIME)
    for token in SUCCESS_TOKENS:
        assert token in text
    assert "result=public_claimability_activated" not in text
