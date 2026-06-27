from __future__ import annotations

from decimal import Decimal

import pytest

from ilc_core.ledger.cdl048_conversion_sweeper_runtime import (
    CDL048_CONVERSION_DEADLINE_ISSUANCE_EPOCHS,
    Cdl048ConversionSweeperRuntimeError,
    build_cdl048_dry_run_wire_quote,
    empty_conversion_sweeper_state,
    register_ecu_lot,
)
from ilc_core.ledger.public_economics_admission_firewall import (
    PublicEconomicsAdmissionError,
    validate_public_economics_admission,
)
from tools.agent_loop_v1 import build_rehearsal_public_admission_source_node


def test_rehearsal_public_admission_source_node_satisfies_existing_firewall() -> None:
    source = build_rehearsal_public_admission_source_node(
        node_id="rehearsal:node:accepted-work-001",
        public_graph_root="block6_rehearsal_2026_06_27_v0_1",
        admitted_epoch=0,
        source_payload={
            "agent_id": "c43f69fcc4dfd021f5e468824c9560c03c45c601f8d004be4d244356ce6043849b9cf2af38bc51a40c1c4bc3e71b04d9",
            "amount_ecu": "1.25",
        },
    )

    normalized = validate_public_economics_admission(source, "public_ecu")

    assert normalized["visibility"] == "public"
    assert normalized["public_graph_admission_evidence"]["public_graph_root"] == (
        "block6_rehearsal_2026_06_27_v0_1"
    )


def test_rehearsal_public_admission_rejects_float_payloads() -> None:
    with pytest.raises(PublicEconomicsAdmissionError) as excinfo:
        build_rehearsal_public_admission_source_node(
            node_id="rehearsal:node:float-work",
            public_graph_root="block6_rehearsal_2026_06_27_v0_1",
            admitted_epoch=0,
            source_payload={"amount_ecu": 1.25},
        )

    assert excinfo.value.token == "public_economic_source_node_float_forbidden_phase_1387a"


def test_cdl048_lot_registration_rejects_float_and_accepts_exact_amounts() -> None:
    state = empty_conversion_sweeper_state()

    with pytest.raises(Cdl048ConversionSweeperRuntimeError):
        register_ecu_lot(
            state,
            lot_id="lot:float",
            agent_id="agent:float",
            amount_ecu=1.25,
            issue_epoch=0,
            origin="fix2b-smoke",
            funding_provenance=("claim:float",),
        )

    next_state = register_ecu_lot(
        state,
        lot_id="lot:exact",
        agent_id="agent:exact",
        amount_ecu="1.25",
        issue_epoch=0,
        origin="fix2b-smoke",
        funding_provenance=("claim:exact",),
    )

    assert next_state.lots[0].amount_ecu == Decimal("1.25")
    assert next_state.lots[0].deadline_epoch == CDL048_CONVERSION_DEADLINE_ISSUANCE_EPOCHS


def test_cdl048_dry_run_wire_quote_is_canonical_and_four_epoch_bound() -> None:
    state = register_ecu_lot(
        empty_conversion_sweeper_state(),
        lot_id="lot:quote",
        agent_id="agent:quote",
        amount_ecu="2.5",
        issue_epoch=0,
        origin="fix2b-smoke",
        funding_provenance=("claim:quote",),
    )

    quote = build_cdl048_dry_run_wire_quote(
        state,
        lot_id="lot:quote",
        agent_id="agent:quote",
        conversion_epoch=4,
        settled_runtime_epoch=4,
        wallet_state_root="wallet_state_sha256:" + "a" * 64,
        settled_runtime_root="settled_runtime_sha256:" + "b" * 64,
        proposed_p_e="1.0",
    )
    record = quote.to_canonical_record()

    assert record["deadline_epoch"] == 4
    assert record["amount_ecu_debit"] == "2.5"
    assert record["quote_only"] is True
    assert record["double_entry_conservation_proven"] is True
