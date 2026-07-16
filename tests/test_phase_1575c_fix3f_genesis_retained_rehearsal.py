from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from ilc_core.analysis.genesis_accrual_governor import (
    GENESIS_ACCRUAL_GOVERNOR_DECIMAL_MIGRATION_TOKEN,
)
from ilc_core.epoch.epoch_emission_production_path import (
    GENESIS_GOVERNOR_WIRING_TOKEN,
    PRODUCTION_EMISSION_NOT_ACTIVATED,
)
from ilc_core.epoch.genesis_settlement_destination import (
    CDL048_TREATMENT_APPLIED_TOKEN,
    GENESIS_5PCT_RETAINED_REHEARSAL_TOKEN,
    GENESIS_AGENT1_AGENT_ID,
    GENESIS_DESTINATION_BINDING_TOKEN,
    GENESIS_MINTING_AUTHORIZED,
    GENESIS_SETTLEMENT_WRITE_AUTHORIZED,
    GENESIS_WALLET_WRITE_AUTHORIZED,
    get_genesis_settlement_destination_record,
    verify_genesis_settlement_destination_record,
)
from tools.genesis_5pct_retained_rehearsal_fix3f import (
    _exact_genesis_share_ratio_string,
    _verify_fix3b_certificate_token,
    build_rehearsal_evidence,
)


def test_fix3f_rehearsal_token_pinned() -> None:
    assert GENESIS_5PCT_RETAINED_REHEARSAL_TOKEN == (
        "genesis_5pct_retained_rehearsal_1575c_fix3f.v0.1"
    )


def test_fix3f_all_fix3b_to_fix3e_tokens_importable() -> None:
    assert (
        "genesis_5pct_surface_reconciliation_certificate_1575c_fix3b.v0.1"
        in Path(
            "docs/specs/ilc_genesis_5pct_surface_reconciliation_certificate_1575c_fix3b_v0.1.md"
        ).read_text(encoding="utf-8")
    )
    assert GENESIS_ACCRUAL_GOVERNOR_DECIMAL_MIGRATION_TOKEN == (
        "genesis_accrual_governor_decimal_migration_1575c_fix3c.v0.1"
    )
    assert GENESIS_GOVERNOR_WIRING_TOKEN == (
        "genesis_governor_wired_into_production_path_1575c_fix3d.v0.1"
    )
    assert GENESIS_DESTINATION_BINDING_TOKEN == (
        "genesis_settlement_destination_bound_phase_1575c_fix3e.v0.1"
    )
    assert CDL048_TREATMENT_APPLIED_TOKEN == (
        "cdl_048_genesis_tranche_treatment_applied_phase_1575c_fix3e.v0.1"
    )


def test_fix3f_reads_fix3b_token_from_certificate_file() -> None:
    assert _verify_fix3b_certificate_token() == (
        "genesis_5pct_surface_reconciliation_certificate_1575c_fix3b.v0.1"
    )


def test_fix3f_rehearsal_script_exists() -> None:
    assert Path("tools/genesis_5pct_retained_rehearsal_fix3f.py").is_file()


def test_fix3f_all_guards_remain_false() -> None:
    assert PRODUCTION_EMISSION_NOT_ACTIVATED is True
    assert GENESIS_WALLET_WRITE_AUTHORIZED is False
    assert GENESIS_SETTLEMENT_WRITE_AUTHORIZED is False
    assert GENESIS_MINTING_AUTHORIZED is False


def test_fix3f_destination_binding_verified() -> None:
    record = get_genesis_settlement_destination_record()
    verify_genesis_settlement_destination_record(record)

    assert record["agent_id"] == GENESIS_AGENT1_AGENT_ID


def test_fix3f_rehearsal_builder_is_deterministic_for_settlement_roots() -> None:
    evidence = build_rehearsal_evidence(generated_at="2026-07-16T00:00:00+00:00")

    assert evidence["deterministic_verified"] is True
    assert evidence["auto_wipe"] is False
    assert evidence["settlement_root_hex"] == evidence["repeated_settlement_root_hex"]
    assert len(evidence["epochs"]) == 3
    for epoch in evidence["epochs"]:
        assert epoch["governor_cap_blocked"] is False
        assert epoch["cdl048_applies_fixed_tranche"] is True
        assert epoch["destination_agent_id"] == GENESIS_AGENT1_AGENT_ID


def test_fix3f_ratio_evidence_uses_exact_decimal_rehearsal_inputs() -> None:
    assert _exact_genesis_share_ratio_string(
        cumulative=Decimal("10000"),
        accrual=Decimal("500"),
    ) == "0.00001929012345679012345679012346"

    evidence = build_rehearsal_evidence(generated_at="2026-07-16T00:00:00+00:00")

    assert evidence["epochs"][1]["genesis_share_ratio"] == (
        "0.00001929012345679012345679012346"
    )
