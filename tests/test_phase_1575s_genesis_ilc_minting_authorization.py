from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from ilc_core.epoch.allocation_distributor_runtime import (
    GENESIS_OVERHEAD_ALLOCATION_FRACTION,
)
from ilc_core.epoch.epoch_emission_production_path import (
    GENESIS_FIXED_TRANCHE_FRACTION,
    GENESIS_FIXED_TRANCHE_ILC,
    compute_epoch_emission_production_path,
    compute_settlement_root,
)
from ilc_core.epoch.epoch_emission_runtime import C_MAX_ILC
from ilc_core.epoch.genesis_settlement_destination import (
    GENESIS_MINTING_AUTHORIZED,
    GENESIS_SETTLEMENT_WRITE_AUTHORIZED,
    GENESIS_WALLET_WRITE_AUTHORIZED,
    get_genesis_settlement_destination_record,
    verify_genesis_settlement_destination_record,
)
from tools.phase_1575s_genesis_ilc_minting_authorization import (
    CANONICAL_SOAK_EPOCH,
    CANONICAL_SOAK_EVIDENCE_PATH,
    CANONICAL_TOTAL_EPOCH_FEES_ILC,
    OUTPUT_TOKENS,
    PHASE,
    SCHEMA_VERSION,
    build_genesis_ilc_minting_authorization_evidence,
    run_genesis_ilc_minting_authorization,
    stable_json,
    verify_genesis_ilc_minting_authorization_evidence,
)


def test_phase_1575s_guard_semantics_are_option_c2() -> None:
    assert GENESIS_WALLET_WRITE_AUTHORIZED is False
    assert GENESIS_SETTLEMENT_WRITE_AUTHORIZED is True
    assert GENESIS_MINTING_AUTHORIZED is True


def test_phase_1575s_destination_verifier_accepts_current_record() -> None:
    verify_genesis_settlement_destination_record(
        get_genesis_settlement_destination_record()
    )


@pytest.mark.parametrize(
    ("field", "value", "token"),
    (
        (
            "genesis_wallet_write_authorized",
            True,
            "genesis_wallet_write_authorized_must_be_false",
        ),
        (
            "genesis_settlement_write_authorized",
            False,
            "genesis_settlement_write_authorized_must_be_true_phase_1575s",
        ),
        (
            "genesis_minting_authorized",
            False,
            "genesis_minting_authorized_must_be_true_phase_1575s",
        ),
    ),
)
def test_phase_1575s_destination_verifier_rejects_wrong_guard_state(
    field: str,
    value: bool,
    token: str,
) -> None:
    record = get_genesis_settlement_destination_record()
    record[field] = value

    with pytest.raises(ValueError, match=token):
        verify_genesis_settlement_destination_record(record)


def test_phase_1575s_canonical_epoch_one_root_matches_soak() -> None:
    result = compute_epoch_emission_production_path(
        CANONICAL_SOAK_EPOCH,
        "0",
        CANONICAL_TOTAL_EPOCH_FEES_ILC,
        genesis_cumulative_accrual_ilc="0",
    )
    root = compute_settlement_root(result)
    evidence_text = CANONICAL_SOAK_EVIDENCE_PATH.read_text(encoding="utf-8")

    assert CANONICAL_SOAK_EPOCH == 1
    assert root.root_hex in evidence_text
    assert result.fee_burn_quote.to_canonical_record()["remaining_fee_pool_ilc"] == "900"
    assert result.allocation_quote.to_canonical_record()["genesis_overhead_pool_ilc"] == "45"
    assert Decimal("900") * GENESIS_OVERHEAD_ALLOCATION_FRACTION == Decimal("45")


def test_phase_1575s_fixed_tranche_reference_remains_canonical() -> None:
    assert GENESIS_FIXED_TRANCHE_FRACTION == Decimal("0.05")
    assert GENESIS_FIXED_TRANCHE_ILC == C_MAX_ILC * Decimal("0.05")


def test_phase_1575s_evidence_builds_and_verifies(tmp_path: Path) -> None:
    evidence = build_genesis_ilc_minting_authorization_evidence(
        wallet_root=tmp_path / "wallet_lmdb",
    )

    verify_genesis_ilc_minting_authorization_evidence(evidence)
    assert evidence["schema_version"] == SCHEMA_VERSION
    assert evidence["phase"] == PHASE
    assert evidence["settled_balance_proof"]["genesis_ilc_credit_ilc"] == "45"
    assert evidence["settled_balance_proof"]["genesis_overhead_pool_ilc"] == "45"
    assert evidence["canonical_soak"]["epoch"] == 1
    assert evidence["wallet_evidence"]["wallet_status"]["data"]["balance_ilc"] == "45"
    assert evidence["wallet_evidence"]["wallet_status"]["data"]["claimability_state"] == "deferred"


def test_phase_1575s_non_claims_all_false(tmp_path: Path) -> None:
    evidence = build_genesis_ilc_minting_authorization_evidence(
        wallet_root=tmp_path / "wallet_lmdb",
    )

    assert evidence["non_claims"]
    assert all(value is False for value in evidence["non_claims"].values())
    assert evidence["non_claims"]["wallet_transfer_enabled"] is False
    assert evidence["non_claims"]["wallet_spend_enabled"] is False
    assert evidence["non_claims"]["wallet_withdrawal_enabled"] is False


def test_phase_1575s_output_tokens_present(tmp_path: Path) -> None:
    evidence = build_genesis_ilc_minting_authorization_evidence(
        wallet_root=tmp_path / "wallet_lmdb",
    )

    assert tuple(evidence["output_tokens"]) == OUTPUT_TOKENS
    assert "genesis_ilc_balance_proof_committed_phase_1575s" in evidence["output_tokens"]


def test_phase_1575s_rejects_tampered_balance(tmp_path: Path) -> None:
    evidence = build_genesis_ilc_minting_authorization_evidence(
        wallet_root=tmp_path / "wallet_lmdb",
    )
    evidence["wallet_evidence"]["wallet_status"]["data"]["balance_ilc"] = "44"

    with pytest.raises(ValueError, match="phase_1575s_wallet_balance_mismatch"):
        verify_genesis_ilc_minting_authorization_evidence(evidence)


def test_phase_1575s_rejects_tampered_payload_hash(tmp_path: Path) -> None:
    evidence = build_genesis_ilc_minting_authorization_evidence(
        wallet_root=tmp_path / "wallet_lmdb",
    )
    evidence["phase_disposition"] = "tampered"

    with pytest.raises(ValueError, match="phase_1575s_evidence_payload_sha256_mismatch"):
        verify_genesis_ilc_minting_authorization_evidence(evidence)


def test_phase_1575s_stable_json_rejects_float_and_decimal() -> None:
    with pytest.raises(ValueError, match="float_in_phase_1575s_evidence_rejected"):
        stable_json({"amount": 1.0})

    with pytest.raises(ValueError, match="decimal_must_be_encoded"):
        stable_json({"amount": Decimal("1")})


def test_phase_1575s_atomic_writer_is_hardened() -> None:
    source = Path("tools/phase_1575s_genesis_ilc_minting_authorization.py").read_text(
        encoding="utf-8"
    )

    assert "tempfile.mkstemp" in source
    assert "os.chmod" in source
    assert "os.fsync" in source
    assert "os.replace" in source


def test_phase_1575s_run_writes_private_evidence(tmp_path: Path) -> None:
    result = run_genesis_ilc_minting_authorization(output_root=tmp_path / "phase1575s")
    evidence_path = Path(result["evidence_path"])

    assert evidence_path.is_file()
    assert result["genesis_ilc_credit_ilc"] == "45"
    assert len(result["evidence_payload_sha256"]) == 64
    assert len(result["evidence_file_sha256"]) == 64
