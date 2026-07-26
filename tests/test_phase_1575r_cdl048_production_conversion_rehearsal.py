from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

from ilc_core.ledger.cdl048_conversion_sweeper_runtime import (
    CDL048_ACTIVATED_PHASE_1388_TOKEN,
    CDL048_ACTIVATION_RUNTIME_VERSION,
)
from tools.cdl048_production_conversion_rehearsal_1575r import (
    OUTPUT_TOKENS,
    REHEARSAL_RECEIPT_SCHEMA_VERSION,
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


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


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
