from __future__ import annotations

import json
from decimal import Decimal, ROUND_DOWN
from pathlib import Path

import pytest

from ilc_core.ledger.cdl048_conversion_sweeper_runtime import (
    CDL048_ACTIVATED_PHASE_1388_TOKEN,
    CDL048_ACTIVATION_RUNTIME_VERSION,
    CDL048_CONVERSION_DEADLINE_ISSUANCE_EPOCHS,
    Cdl048ConversionSweeperRuntimeError,
    build_cdl048_dry_run_wire_quote,
    conversion_dry_run_wire_quote_payload,
    deadline_status,
    empty_conversion_sweeper_state,
    register_ecu_lot,
)
from tools.cdl048_production_conversion_rehearsal_1575r import (
    MAX_LOTS_PER_REHEARSAL,
    OUTPUT_TOKENS,
    REHEARSAL_RECEIPT_SCHEMA_VERSION,
    _register_lots,
    build_ecu_lot_records,
    build_rehearsal_evidence,
    file_sha256,
    run_rehearsal,
    stable_json,
    verify_rehearsal_evidence,
)


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/cdl048_production_conversion_rehearsal_1575r.py"
SWEEPER = ROOT / "ilc_core/ledger/cdl048_conversion_sweeper_runtime.py"
PROMPT = (
    ROOT
    / "docs/antigravity_tasks/antigravity_prompt__phase_1575r_g10_cdl048_production_conversion_rehearsal.md"
)
TEST_AGENT_ID = "a" * 96


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _test_lot(*, lot_id: str = "test_lot_001", amount_ecu: str = "2.000000000") -> dict:
    return {
        "agent_id": TEST_AGENT_ID,
        "amount_ecu": amount_ecu,
        "funding_provenance": ("phase1575r_fix1_test_provenance",),
        "issue_epoch": 0,
        "lot_id": lot_id,
        "origin": "phase1575r_fix1_test",
    }


def _quote_payload_for_lot(
    lot: dict,
    *,
    conversion_epoch: int,
    proposed_p_e: Decimal,
) -> dict:
    state = register_ecu_lot(
        empty_conversion_sweeper_state(),
        lot_id=lot["lot_id"],
        agent_id=lot["agent_id"],
        amount_ecu=lot["amount_ecu"],
        issue_epoch=lot["issue_epoch"],
        origin=lot["origin"],
        funding_provenance=tuple(lot["funding_provenance"]),
    )
    quote = build_cdl048_dry_run_wire_quote(
        state,
        lot_id=lot["lot_id"],
        agent_id=lot["agent_id"],
        conversion_epoch=conversion_epoch,
        settled_runtime_epoch=conversion_epoch,
        wallet_state_root=f"wallet_state_sha256:{'1' * 64}",
        settled_runtime_root=f"settled_runtime_sha256:{'2' * 64}",
        proposed_p_e=proposed_p_e,
        activation_requested=True,
    )
    return conversion_dry_run_wire_quote_payload(quote)


def test_realistic_ecu_lot_generator_produces_non_synthetic_ids() -> None:
    lots = build_ecu_lot_records()["lots"]

    assert lots
    for lot in lots:
        assert len(lot["agent_id"]) == 96
        assert not lot["agent_id"].startswith("soak_agent_")


def test_ecu_lots_are_decimal_only() -> None:
    dataset = build_ecu_lot_records()

    encoded = stable_json(dataset)
    assert "." in encoded
    for lot in dataset["lots"]:
        assert isinstance(lot["amount_ecu"], str)
        assert Decimal(lot["amount_ecu"]) > Decimal("0")


def test_activation_token_in_token_set() -> None:
    evidence = build_rehearsal_evidence()

    for quote in evidence["quote_payloads"]:
        assert CDL048_ACTIVATED_PHASE_1388_TOKEN in quote["tokens"]


def test_wire_quote_activation_token_live() -> None:
    evidence = build_rehearsal_evidence()

    assert evidence["activation_boundary"]["activation_token"] == CDL048_ACTIVATED_PHASE_1388_TOKEN
    assert evidence["activation_boundary"]["activation_token_live_in_this_private_rehearsal_caller"] is True
    assert all(
        quote["runtime_version"] == CDL048_ACTIVATION_RUNTIME_VERSION
        for quote in evidence["quote_payloads"]
    )


def test_rehearsal_receipt_keeps_mint_and_settlement_authorization_false() -> None:
    evidence = build_rehearsal_evidence()

    assert evidence["rehearsal_receipts"]
    for receipt in evidence["rehearsal_receipts"]:
        assert receipt["runtime_version"] == REHEARSAL_RECEIPT_SCHEMA_VERSION
        assert receipt["conversion_receipt_not_activated"] is True
        assert receipt["ecu_mint_authorized"] is False
        assert receipt["ilc_settlement_authorized"] is False


def test_double_entry_conservation() -> None:
    evidence = build_rehearsal_evidence()
    conservation = evidence["double_entry_conservation"]

    assert conservation["proven"] is True
    assert Decimal(conservation["total_debit_value_ilc"]) == Decimal(
        conservation["total_ilc_equivalent_out"]
    )
    assert Decimal(conservation["total_ecu_in"]) == Decimal(
        conservation["total_ilc_equivalent_out"]
    )
    assert Decimal(conservation["conservation_delta_ilc"]) == Decimal("0")


def test_wallet_withdrawal_remains_false() -> None:
    evidence = build_rehearsal_evidence()

    for receipt in evidence["rehearsal_receipts"]:
        assert receipt["wallet_withdrawal_enabled"] is False


def test_public_claimability_not_activated() -> None:
    evidence = build_rehearsal_evidence()

    for quote in evidence["quote_payloads"]:
        assert quote["public_claimability_activated"] is False
    for receipt in evidence["rehearsal_receipts"]:
        assert receipt["public_claimability_activated"] is False


def test_rehearsal_evidence_atomic_write() -> None:
    source = _read(TOOL)

    assert "tempfile.mkstemp" in source
    assert "os.replace" in source
    assert "os.fsync" in source


def test_evidence_sha256_matches_artifact(tmp_path: Path) -> None:
    result = run_rehearsal(tmp_path)
    evidence_path = Path(result["evidence_path"])
    sha_path = Path(result["evidence_sha256_path"])

    assert sha_path.read_text(encoding="utf-8").strip() == file_sha256(evidence_path)
    assert result["evidence_sha256"] == file_sha256(evidence_path)
    verify_rehearsal_evidence(json.loads(evidence_path.read_text(encoding="utf-8")))


def test_1575s_gate_evidence_is_present() -> None:
    evidence = build_rehearsal_evidence()
    gate = evidence["phase_1575s_gate_evidence"]

    assert gate["ready_for_1575s"] is True
    assert gate["candidate_set_non_empty"] is True
    assert gate["conversion_rate_readable"] is True
    assert gate["output_format_stable_canonical"] is True


def test_prompt_records_corrected_wire_quote_boundary() -> None:
    text = _read(PROMPT)

    assert "activated wire-quote path" in text
    assert "conversion_receipt_not_activated=True" in text
    assert "separate — Phase 1575s" in text


def test_sweeper_public_rc_exclude_retained() -> None:
    assert _read(SWEEPER).startswith(
        "# PUBLIC_RC_EXCLUDE: internal_phase_helper_not_public_rc_launch_surface"
    )


def test_output_tokens_use_non_activation_boundary_language() -> None:
    assert "cdl048_wire_quote_activation_rehearsed_phase_1575r" in OUTPUT_TOKENS
    assert "cdl048_conversion_receipt_activation_deferred_phase_1575r" in OUTPUT_TOKENS
    assert all("authorized_true" not in token for token in OUTPUT_TOKENS)


def test_deadline_epoch_conversion_succeeds() -> None:
    lot = _test_lot()
    deadline_epoch = lot["issue_epoch"] + CDL048_CONVERSION_DEADLINE_ISSUANCE_EPOCHS
    payload = _quote_payload_for_lot(
        lot,
        conversion_epoch=deadline_epoch,
        proposed_p_e=Decimal("1.00"),
    )
    state = _register_lots([lot])

    assert payload["conversion_epoch"] == deadline_epoch
    assert payload["deadline_epoch"] == deadline_epoch
    assert deadline_status(lot=state.lots[0], current_epoch=deadline_epoch)[
        "deadline_status"
    ] == "deadline_epoch"


def test_post_deadline_conversion_raises() -> None:
    lot = _test_lot()
    post_deadline_epoch = (
        lot["issue_epoch"] + CDL048_CONVERSION_DEADLINE_ISSUANCE_EPOCHS + 1
    )

    with pytest.raises(Cdl048ConversionSweeperRuntimeError) as exc_info:
        _quote_payload_for_lot(
            lot,
            conversion_epoch=post_deadline_epoch,
            proposed_p_e=Decimal("1.00"),
        )

    assert exc_info.value.token == "cdl048_conversion_deadline_expired"


def test_duplicate_lot_id_raises() -> None:
    lot = _test_lot(lot_id="test_lot_dup_001")
    state = _register_lots([lot])

    with pytest.raises(Cdl048ConversionSweeperRuntimeError) as exc_info:
        register_ecu_lot(
            state,
            lot_id=lot["lot_id"],
            agent_id=lot["agent_id"],
            amount_ecu=lot["amount_ecu"],
            issue_epoch=lot["issue_epoch"],
            origin=lot["origin"],
            funding_provenance=tuple(lot["funding_provenance"]),
        )

    assert exc_info.value.token == "cdl048_lot_duplicate"


def test_rehearsal_evidence_is_deterministic() -> None:
    evidence_1 = build_rehearsal_evidence()
    evidence_2 = build_rehearsal_evidence()

    for key in (
        "quote_payloads",
        "rehearsal_receipts",
        "double_entry_conservation",
        "activation_boundary",
        "phase_1575s_gate_evidence",
    ):
        assert evidence_1[key] == evidence_2[key]
    assert stable_json(evidence_1) == stable_json(evidence_2)


def test_non_unit_price_produces_different_ilc_amount_and_conserves_value() -> None:
    evidence_floor = build_rehearsal_evidence(proposed_p_e=Decimal("0.75"))
    evidence_neutral = build_rehearsal_evidence(proposed_p_e=Decimal("1.00"))
    evidence_ceiling = build_rehearsal_evidence(proposed_p_e=Decimal("1.30"))

    for evidence in (evidence_floor, evidence_neutral, evidence_ceiling):
        conservation = evidence["double_entry_conservation"]
        assert conservation["proven"] is True
        assert Decimal(conservation["conservation_delta_ilc"]) == Decimal("0")
        assert Decimal(conservation["total_debit_value_ilc"]) == Decimal(
            conservation["total_ilc_equivalent_out"]
        )
        for quote in evidence["quote_payloads"]:
            amount_ecu = Decimal(quote["amount_ecu_debit"])
            amount_ilc = Decimal(quote["amount_ilc_credit"])
            effective_p_e = Decimal(quote["effective_p_e"])
            assert Decimal(quote["debit_value_ilc"]) == amount_ilc
            assert amount_ilc == (amount_ecu * effective_p_e).quantize(
                Decimal("0.000000001"),
                rounding=ROUND_DOWN,
            )

    floor_quote = evidence_floor["quote_payloads"][0]
    neutral_quote = evidence_neutral["quote_payloads"][0]
    ceiling_quote = evidence_ceiling["quote_payloads"][0]
    assert Decimal(floor_quote["amount_ilc_credit"]) < Decimal(
        floor_quote["amount_ecu_debit"]
    )
    assert Decimal(neutral_quote["amount_ilc_credit"]) == Decimal(
        neutral_quote["amount_ecu_debit"]
    )
    assert Decimal(ceiling_quote["amount_ilc_credit"]) > Decimal(
        ceiling_quote["amount_ecu_debit"]
    )


def test_oom_guard_rejects_oversized_lot_list() -> None:
    oversized_lots = [
        _test_lot(lot_id=f"test_lot_oom_{index:04d}")
        for index in range(MAX_LOTS_PER_REHEARSAL + 1)
    ]

    with pytest.raises(ValueError, match="cdl048_rehearsal_lot_count_exceeded"):
        _register_lots(oversized_lots)
