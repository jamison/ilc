from __future__ import annotations

from pathlib import Path

from ilc_core.epoch.genesis_settlement_destination import (
    GENESIS_AGENT1_AGENT_ID,
    GENESIS_MINTING_AUTHORIZED,
    GENESIS_SETTLEMENT_WRITE_AUTHORIZED,
    GENESIS_WALLET_WRITE_AUTHORIZED,
)
from ilc_core.ledger.cdl048_conversion_sweeper_runtime import (
    CDL048_CONVERSION_DEADLINE_ISSUANCE_EPOCHS,
    CDL048_ACTIVATED_PHASE_1388_TOKEN,
    ConversionReceipt,
)


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs/specs/ilc_cdl048_production_conversion_and_genesis_minting_spec_1575q_v0.1.md"
PROMPT = ROOT / "docs/antigravity_tasks/antigravity_prompt__phase_1575q_g10_cdl048_production_conversion_spec.md"
FORWARD_PLAN = ROOT / "docs/specs/ilc_comprehensive_forward_plan_post_1575c_v0.1.md"
SWEEPER = ROOT / "ilc_core/ledger/cdl048_conversion_sweeper_runtime.py"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_1575q_spec_exists_and_records_required_tokens() -> None:
    text = _text(SPEC)

    assert "cdl048_production_conversion_spec_committed_phase_1575q" in text
    assert "genesis_ilc_wallet_gap_formally_recorded_phase_1575q" in text
    assert "cdl048_guard_clearance_criteria_table_committed_phase_1575q" in text
    assert "cdl048_production_path_integration_spec_committed_phase_1575q" in text
    assert "genesis_ilc_wallet_option_c_decided_phase_1575q" in text


def test_phase_1575q_spec_matches_live_conversion_receipt_guard_defaults() -> None:
    fields = ConversionReceipt.__dataclass_fields__
    guard_fields = (
        "public_claimability_activated",
        "wallet_withdrawal_enabled",
        "wallet_transfer_enabled",
        "wallet_spend_enabled",
        "ecu_mint_authorized",
        "ilc_settlement_authorized",
    )
    text = _text(SPEC)

    for field in guard_fields:
        assert fields[field].default is False
        assert f"| `{field}` | `False` |" in text


def test_phase_1575q_spec_records_historical_genesis_guard_defaults_and_live_1575s_state() -> None:
    text = _text(SPEC)

    assert GENESIS_WALLET_WRITE_AUTHORIZED is False
    assert GENESIS_SETTLEMENT_WRITE_AUTHORIZED is True
    assert GENESIS_MINTING_AUTHORIZED is True
    assert GENESIS_AGENT1_AGENT_ID in _text(ROOT / "ilc_core/epoch/genesis_settlement_destination.py")
    assert "| `GENESIS_WALLET_WRITE_AUTHORIZED` | `False` |" in text
    assert "| `GENESIS_SETTLEMENT_WRITE_AUTHORIZED` | `False` |" in text
    assert "| `GENESIS_MINTING_AUTHORIZED` | `False` |" in text
    assert "These fields are cleared by Phase 1575s" in text


def test_phase_1575q_spec_selects_option_c_without_wallet_claims() -> None:
    text = _text(SPEC)

    assert "**Option C**" in text
    assert "settlement-root/off-chain accounting" in text
    assert "No Genesis private key, mnemonic, wallet address, or withdrawal credential" in text
    assert "GENESIS_WALLET_WRITE_AUTHORIZED` stays `False" in text
    assert "genesis_ilc_wallet_option_c_decided_phase_1575q" in text


def test_phase_1575q_spec_preserves_cdl029_cdl048_boundary() -> None:
    text = _text(SPEC)

    assert "CDL-048 is the ECU mandatory conversion deadline" in text
    assert "distinct from the CDL-029 Genesis overhead allocation" in text
    assert "CDL-029 path accrues Genesis ILC" in text
    assert "CDL-048 path converts eligible ECU lots to ILC" in text


def test_phase_1575q_spec_records_live_deadline_and_activation_boundary() -> None:
    text = _text(SPEC)

    assert CDL048_CONVERSION_DEADLINE_ISSUANCE_EPOCHS == 4
    assert "four-issuance-epoch deadline" in text
    assert CDL048_ACTIVATED_PHASE_1388_TOKEN in text
    assert "Phase 1575q does not pass it to any runtime" in text


def test_phase_1575q_prompt_is_hardened_and_mirror_safe() -> None:
    text = _text(PROMPT)

    assert text.startswith("<!-- PUBLIC_RC_EXCLUDE: antigravity_phase_prompt -->")
    assert "# Phase 1575q-G10:" in text
    for heading in (
        "## Mission",
        "### §0a — Known-token audit",
        "### §0b — Concept-discovery search",
        "### §0c — Contradiction and non-claim search",
        "### §0d — Source expansion and newly discovered tokens",
        "## LMDB Node Registration",
        "## Public Mirror Maintenance",
    ):
        assert heading in text
    assert "No ellipses in walkthrough" in text
    assert "STATUS.md" in text


def test_phase_1575q_sweeper_remains_public_rc_excluded() -> None:
    text = _text(SWEEPER)

    assert text.startswith("# PUBLIC_RC_EXCLUDE: internal_phase_helper_not_public_rc_launch_surface")


def test_phase_1575q_forward_plan_uses_option_c_accounting_language() -> None:
    text = _text(FORWARD_PLAN)

    assert "Phase 1575q" in text
    assert "Option C" in text
    assert "settlement-root/off-chain accounting" in text
    assert "1575q COMPLETE" in text
