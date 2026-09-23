from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal

import pytest

from ilc_core.epoch.ecu_accrual_evidence import (
    ECU_ACCRUAL_EVIDENCE_SCHEMA_VERSION,
    EcuAccrualEvidence,
    MAX_ECU_ACCRUAL_EVIDENCE_BYTES,
    build_ecu_accrual_evidence,
    is_replay_safe,
    read_ecu_accrual_evidence,
    write_ecu_accrual_evidence,
)
from ilc_core.epoch.epoch_distribution_writer import (
    EpochDistributionInput,
    compute_epoch_distribution,
)
from ilc_core.epoch.epoch_maturity_gate import (
    MIN_MONTHLY_ISSUANCE_VALIDATION_EPOCH_SPAN,
    MONTHLY_ISSUANCE_MATURITY_PROOF_REQUIRED_TOKEN,
    VALIDATION_EPOCH_TRANSITION_NOT_MONTHLY_MATURITY_TOKEN,
)
from ilc_core.epoch.monthly_close_orchestrator import (
    MAX_EPOCH_RECORD_AGG_SIG_BYTES,
    build_monthly_close_proof_from_epoch_record,
    build_settlement_input_from_ecu_accrual,
    verify_close_dry_run,
)
from ilc_core.ledger.ecu_active_layer_runtime import EcuActiveLayerRuntime


AGENT_A = "a" * 96
AGENT_B = "b" * 96
ROOT_HEX = "c" * 64


@dataclass(frozen=True)
class StubEpochRecord:
    epoch: int
    found: bool
    state_root: bytes
    spectral_hash: bytes = b"spectral"
    agg_sig: bytes = b"aggregate-signature"


def _epoch_record(*, state_root: bytes | None = None) -> StubEpochRecord:
    return StubEpochRecord(
        epoch=40320,
        found=True,
        state_root=state_root if state_root is not None else bytes.fromhex(ROOT_HEX),
    )


def _epoch_record_with(
    *,
    found: bool = True,
    state_root: bytes | None = None,
    agg_sig: bytes = b"aggregate-signature",
) -> StubEpochRecord:
    return StubEpochRecord(
        epoch=40320,
        found=found,
        state_root=state_root if state_root is not None else bytes.fromhex(ROOT_HEX),
        agg_sig=agg_sig,
    )


def _proof():
    return build_monthly_close_proof_from_epoch_record(
        _epoch_record(),
        matured_issuance_epoch=0,
        distribution_issuance_epoch=1,
        opening_validation_epoch=0,
        closing_validation_epoch=MIN_MONTHLY_ISSUANCE_VALIDATION_EPOCH_SPAN,
        evidence_ref="out/gap_monthly_close_orchestrator_00a/ecu_accrual_evidence_interval_0000.json",
    )


def _evidence() -> EcuAccrualEvidence:
    return EcuAccrualEvidence(
        issuance_interval_id=0,
        accrual_close_validation_epoch=MIN_MONTHLY_ISSUANCE_VALIDATION_EPOCH_SPAN,
        agent_ecu_weights={AGENT_A: "2", AGENT_B: "1"},
    )


def test_build_proof_from_epoch_record_success() -> None:
    proof = _proof()

    assert proof.matured_issuance_epoch == 0
    assert proof.distribution_issuance_epoch == 1
    assert proof.source_settlement_root_hex == ROOT_HEX
    assert proof.opening_validation_epoch == 0
    assert proof.closing_validation_epoch == MIN_MONTHLY_ISSUANCE_VALIDATION_EPOCH_SPAN
    assert proof.validator_quorum_certificate_ref.startswith("epoch_record_agg_sig_sha256:")


def test_build_proof_rejects_insufficient_validation_span() -> None:
    with pytest.raises(ValueError, match=VALIDATION_EPOCH_TRANSITION_NOT_MONTHLY_MATURITY_TOKEN):
        build_monthly_close_proof_from_epoch_record(
            _epoch_record(),
            matured_issuance_epoch=0,
            distribution_issuance_epoch=1,
            opening_validation_epoch=0,
            closing_validation_epoch=MIN_MONTHLY_ISSUANCE_VALIDATION_EPOCH_SPAN - 1,
            evidence_ref="out/gap_monthly_close_orchestrator_00a/too_early.json",
        )


def test_build_proof_rejects_epoch_zero_distribution() -> None:
    with pytest.raises(ValueError, match="monthly_maturity_proof_not_defined_for_epoch_zero"):
        build_monthly_close_proof_from_epoch_record(
            _epoch_record(),
            matured_issuance_epoch=0,
            distribution_issuance_epoch=0,
            opening_validation_epoch=0,
            closing_validation_epoch=MIN_MONTHLY_ISSUANCE_VALIDATION_EPOCH_SPAN,
            evidence_ref="out/gap_monthly_close_orchestrator_00a/epoch_zero.json",
        )


def test_build_proof_state_root_hex_encoding() -> None:
    proof = build_monthly_close_proof_from_epoch_record(
        _epoch_record(state_root=bytes.fromhex("aa" * 32)),
        matured_issuance_epoch=0,
        distribution_issuance_epoch=1,
        opening_validation_epoch=0,
        closing_validation_epoch=MIN_MONTHLY_ISSUANCE_VALIDATION_EPOCH_SPAN,
        evidence_ref="out/gap_monthly_close_orchestrator_00a/root_encoding.json",
    )

    assert proof.source_settlement_root_hex == "aa" * 32


def test_build_proof_rejects_missing_epoch_record() -> None:
    with pytest.raises(ValueError, match="epoch_record_not_found"):
        build_monthly_close_proof_from_epoch_record(
            _epoch_record_with(found=False),
            matured_issuance_epoch=0,
            distribution_issuance_epoch=1,
            opening_validation_epoch=0,
            closing_validation_epoch=MIN_MONTHLY_ISSUANCE_VALIDATION_EPOCH_SPAN,
            evidence_ref="out/gap_monthly_close_orchestrator_00a/not_found.json",
        )


def test_build_proof_rejects_oversized_aggregate_signature() -> None:
    with pytest.raises(ValueError, match="epoch_record_agg_sig_exceeds_max_bytes"):
        build_monthly_close_proof_from_epoch_record(
            _epoch_record_with(agg_sig=b"x" * (MAX_EPOCH_RECORD_AGG_SIG_BYTES + 1)),
            matured_issuance_epoch=0,
            distribution_issuance_epoch=1,
            opening_validation_epoch=0,
            closing_validation_epoch=MIN_MONTHLY_ISSUANCE_VALIDATION_EPOCH_SPAN,
            evidence_ref="out/gap_monthly_close_orchestrator_00a/oversized_sig.json",
        )


def test_ecu_accrual_evidence_build_roundtrip(tmp_path) -> None:
    runtime = EcuActiveLayerRuntime()
    runtime.set_accrued_ecu(AGENT_A, "2.5")
    runtime.set_accrued_ecu(AGENT_B, "0")
    evidence = build_ecu_accrual_evidence(
        runtime,
        issuance_interval_id=0,
        accrual_close_validation_epoch=MIN_MONTHLY_ISSUANCE_VALIDATION_EPOCH_SPAN,
        agent_ids=[AGENT_B, AGENT_A],
    )
    path = tmp_path / "ecu_accrual_evidence_interval_0000.json"

    write_ecu_accrual_evidence(evidence, path)
    loaded = read_ecu_accrual_evidence(path)

    assert loaded == evidence
    assert loaded.agent_ecu_weights == {AGENT_A: "2.5"}


def test_ecu_accrual_evidence_sha256_mismatch_rejected(tmp_path) -> None:
    path = tmp_path / "evidence.json"
    write_ecu_accrual_evidence(_evidence(), path)
    payload = json.loads(path.read_text())
    payload["agent_ecu_weights"][AGENT_A] = "99"
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")

    with pytest.raises(ValueError, match="ecu_accrual_evidence_sha256_mismatch"):
        read_ecu_accrual_evidence(path)


def test_ecu_accrual_evidence_atomic_write(tmp_path) -> None:
    path = tmp_path / "evidence.json"

    write_ecu_accrual_evidence(_evidence(), path)

    assert path.exists()
    assert read_ecu_accrual_evidence(path) == _evidence()
    assert list(tmp_path.glob("*.tmp")) == []
    assert list(tmp_path.glob(".evidence.json.*.tmp")) == []


def test_is_replay_safe_match() -> None:
    assert is_replay_safe(
        _evidence(),
        issuance_interval_id=0,
        accrual_close_validation_epoch=MIN_MONTHLY_ISSUANCE_VALIDATION_EPOCH_SPAN,
    )


def test_is_replay_safe_mismatch() -> None:
    assert not is_replay_safe(
        _evidence(),
        issuance_interval_id=1,
        accrual_close_validation_epoch=MIN_MONTHLY_ISSUANCE_VALIDATION_EPOCH_SPAN,
    )


def test_build_settlement_input_from_ecu_accrual() -> None:
    proof = _proof()
    distribution_input = build_settlement_input_from_ecu_accrual(
        _evidence(),
        distribution_issuance_epoch=1,
        proof=proof,
        total_epoch_fees_ilc="0",
        genesis_cumulative_accrual_ilc="0",
        prior_carry_forward_records=(),
        cumulative_issued_before_epoch_ilc="0",
    )

    assert distribution_input.issuance_epoch == 1
    assert distribution_input.eligible_agents == {AGENT_A: "2", AGENT_B: "1"}
    assert distribution_input.total_epoch_fees_ilc == "0"
    assert distribution_input.genesis_cumulative_accrual_ilc == "0"
    assert distribution_input.prior_carry_forward_records == ()
    assert distribution_input.monthly_maturity_proof == proof
    assert distribution_input.source_settlement_root_hex == proof.source_settlement_root_hex
    assert distribution_input.allow_default_source_settlement_root is False


def test_verify_close_dry_run_conserves_ilc() -> None:
    distribution_input = build_settlement_input_from_ecu_accrual(
        _evidence(),
        distribution_issuance_epoch=1,
        proof=_proof(),
        total_epoch_fees_ilc="0",
        genesis_cumulative_accrual_ilc="0",
    )

    output = verify_close_dry_run(distribution_input)

    assert output.conservation_verified is True
    assert output.conservation_record.to_canonical_record()["difference_ilc"] == "0"
    assert output.agent_settled_balance_deltas[AGENT_A] > Decimal("0")


def test_verify_close_dry_run_rejects_missing_proof() -> None:
    with pytest.raises(ValueError, match=MONTHLY_ISSUANCE_MATURITY_PROOF_REQUIRED_TOKEN):
        compute_epoch_distribution(
            EpochDistributionInput(
                issuance_epoch=1,
                total_epoch_fees_ilc="0",
                genesis_cumulative_accrual_ilc="0",
                eligible_agents={AGENT_A: "1"},
                prior_carry_forward_records=[],
                source_settlement_root_hex=ROOT_HEX,
                allow_default_source_settlement_root=False,
                monthly_maturity_proof=None,
            )
        )


def test_evidence_ref_max_bytes_rejected() -> None:
    with pytest.raises(ValueError, match="monthly_maturity_proof_evidence_ref_required_exceeds"):
        build_monthly_close_proof_from_epoch_record(
            _epoch_record(),
            matured_issuance_epoch=0,
            distribution_issuance_epoch=1,
            opening_validation_epoch=0,
            closing_validation_epoch=MIN_MONTHLY_ISSUANCE_VALIDATION_EPOCH_SPAN,
            evidence_ref="x" * 513,
        )


def test_evidence_sha256_excludes_self_reference() -> None:
    evidence = _evidence()
    payload = evidence.to_canonical_record()
    hash_payload = dict(payload)
    hash_payload.pop("evidence_sha256")
    expected = hashlib.sha256(
        json.dumps(hash_payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode(
            "utf-8"
        )
    ).hexdigest()

    assert evidence.evidence_sha256 == expected
    assert evidence.evidence_sha256 not in json.dumps(hash_payload, sort_keys=True)


def test_ecu_accrual_evidence_rejects_reserved_protocol_account_id() -> None:
    with pytest.raises(ValueError, match="ecu_accrual_evidence_agent_id_reserved_protocol_account"):
        EcuAccrualEvidence(
            issuance_interval_id=0,
            accrual_close_validation_epoch=MIN_MONTHLY_ISSUANCE_VALIDATION_EPOCH_SPAN,
            agent_ecu_weights={"pool:cdl029:performer": "1"},
        )


def test_ecu_accrual_evidence_rejects_oversized_file_before_json_parse(tmp_path) -> None:
    path = tmp_path / "oversized.json"
    path.write_bytes(b"{" + (b" " * MAX_ECU_ACCRUAL_EVIDENCE_BYTES) + b"}")

    with pytest.raises(ValueError, match="ecu_accrual_evidence_exceeds_max_bytes"):
        read_ecu_accrual_evidence(path)


def test_ecu_accrual_evidence_rejects_duplicate_json_keys(tmp_path) -> None:
    path = tmp_path / "duplicate.json"
    path.write_text(
        (
            '{"issuance_interval_id":0,'
            '"issuance_interval_id":1,'
            '"agent_ecu_weights":{},'
            '"accrual_close_validation_epoch":40320,'
            f'"schema_version":"{ECU_ACCRUAL_EVIDENCE_SCHEMA_VERSION}",'
            '"evidence_sha256":"0"}'
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="ecu_accrual_evidence_duplicate_json_key"):
        read_ecu_accrual_evidence(path)


def test_ecu_accrual_evidence_rejects_duplicate_agent_ids() -> None:
    runtime = EcuActiveLayerRuntime()

    with pytest.raises(ValueError, match="ecu_accrual_agent_id_duplicate"):
        build_ecu_accrual_evidence(
            runtime,
            issuance_interval_id=0,
            accrual_close_validation_epoch=MIN_MONTHLY_ISSUANCE_VALIDATION_EPOCH_SPAN,
            agent_ids=[AGENT_A, AGENT_A],
        )


def test_ecu_accrual_evidence_rejects_noncanonical_decimal_string() -> None:
    with pytest.raises(ValueError, match="ecu_accrual_weight_must_be_canonical_decimal_string"):
        EcuAccrualEvidence(
            issuance_interval_id=0,
            accrual_close_validation_epoch=MIN_MONTHLY_ISSUANCE_VALIDATION_EPOCH_SPAN,
            agent_ecu_weights={AGENT_A: "1.0"},
        )


def test_ecu_accrual_evidence_rejects_float_weight() -> None:
    with pytest.raises(ValueError, match="ecu_accrual_weight_must_be_canonical_decimal_string"):
        EcuAccrualEvidence(
            issuance_interval_id=0,
            accrual_close_validation_epoch=MIN_MONTHLY_ISSUANCE_VALIDATION_EPOCH_SPAN,
            agent_ecu_weights={AGENT_A: 1.0},  # type: ignore[dict-item]
        )


def test_zero_accrual_agents_are_filtered_from_evidence() -> None:
    runtime = EcuActiveLayerRuntime()
    evidence = build_ecu_accrual_evidence(
        runtime,
        issuance_interval_id=0,
        accrual_close_validation_epoch=MIN_MONTHLY_ISSUANCE_VALIDATION_EPOCH_SPAN,
        agent_ids=[AGENT_A],
    )

    assert evidence.agent_ecu_weights == {}
    distribution_input = build_settlement_input_from_ecu_accrual(
        evidence,
        distribution_issuance_epoch=1,
        proof=_proof(),
        total_epoch_fees_ilc="0",
        genesis_cumulative_accrual_ilc="0",
    )
    output = verify_close_dry_run(distribution_input)
    assert output.conservation_verified is True
