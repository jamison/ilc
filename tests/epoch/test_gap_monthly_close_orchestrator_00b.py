# SPDX-License-Identifier: AGPL-3.0-only
"""Tests for GAP-MONTHLY-ISSUANCE-CLOSE-ORCHESTRATOR-00b."""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

from ilc_core.epoch.ecu_accrual_evidence import (
    EcuAccrualEvidence,
    write_ecu_accrual_evidence,
)
from ilc_core.epoch.epoch_maturity_gate import (
    MIN_MONTHLY_ISSUANCE_VALIDATION_EPOCH_SPAN,
    VALIDATION_EPOCH_TRANSITION_NOT_MONTHLY_MATURITY_TOKEN,
    MonthlyIssuanceMaturityProof,
    require_monthly_issuance_maturity_proof,
)
from ilc_core.epoch.monthly_close_orchestrator import (
    build_monthly_close_proof_from_epoch_record,
    build_settlement_input_from_ecu_accrual,
    verify_close_dry_run,
)


SCRIPT_PATH = Path("tools/monthly_close/run_monthly_close.py")
AGENT_ID = "a" * 96
STATE_ROOT = bytes.fromhex(
    "01711220bf4075c3892f014e14ac47e64c0e088e14d8867b19f47855c97521603c05d6b4"
)
SPECTRAL_HASH = b"s" * 32


def _load_script_module():
    spec = importlib.util.spec_from_file_location("gap_run_monthly_close", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _epoch_record(**overrides):
    values = {
        "found": True,
        "epoch": 1,
        "state_root": STATE_ROOT,
        "spectral_hash": SPECTRAL_HASH,
        "agg_sig": b"aggregate-signature",
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def _evidence() -> EcuAccrualEvidence:
    return EcuAccrualEvidence(
        issuance_interval_id=0,
        agent_ecu_weights={AGENT_ID: "1"},
        accrual_close_validation_epoch=MIN_MONTHLY_ISSUANCE_VALIDATION_EPOCH_SPAN,
    )


def test_organic_path_dry_run_synthetic_maturity():
    assert "synthetic" in test_organic_path_dry_run_synthetic_maturity.__name__
    proof = build_monthly_close_proof_from_epoch_record(
        _epoch_record(),
        matured_issuance_epoch=0,
        distribution_issuance_epoch=1,
        opening_validation_epoch=0,
        closing_validation_epoch=MIN_MONTHLY_ISSUANCE_VALIDATION_EPOCH_SPAN,
        evidence_ref="synthetic:test",
    )
    distribution_input = build_settlement_input_from_ecu_accrual(
        _evidence(),
        distribution_issuance_epoch=1,
        proof=proof,
        total_epoch_fees_ilc="0",
        genesis_cumulative_accrual_ilc="0",
    )

    output = verify_close_dry_run(distribution_input)

    assert output.conservation_verified is True


def test_organic_path_fails_maturity_gate_insufficient_span():
    with pytest.raises(ValueError, match=VALIDATION_EPOCH_TRANSITION_NOT_MONTHLY_MATURITY_TOKEN):
        build_monthly_close_proof_from_epoch_record(
            _epoch_record(),
            matured_issuance_epoch=0,
            distribution_issuance_epoch=1,
            opening_validation_epoch=0,
            closing_validation_epoch=MIN_MONTHLY_ISSUANCE_VALIDATION_EPOCH_SPAN - 1,
            evidence_ref="synthetic:test",
        )


def test_distribution_issuance_epoch_zero_rejected():
    proof = MonthlyIssuanceMaturityProof(
        matured_issuance_epoch=0,
        distribution_issuance_epoch=1,
        source_settlement_root_hex=STATE_ROOT.hex(),
        opening_validation_epoch=0,
        closing_validation_epoch=MIN_MONTHLY_ISSUANCE_VALIDATION_EPOCH_SPAN,
        validator_quorum_certificate_ref="synthetic:quorum",
        evidence_ref="synthetic:test",
    )

    with pytest.raises(ValueError, match="monthly_maturity_proof_not_defined_for_epoch_zero"):
        require_monthly_issuance_maturity_proof(
            proof,
            distribution_issuance_epoch=0,
            source_settlement_root_hex=STATE_ROOT.hex(),
        )


def test_epoch_record_not_found_raises():
    with pytest.raises(ValueError, match="epoch_record_not_found"):
        build_monthly_close_proof_from_epoch_record(
            _epoch_record(found=False),
            matured_issuance_epoch=0,
            distribution_issuance_epoch=1,
            opening_validation_epoch=0,
            closing_validation_epoch=MIN_MONTHLY_ISSUANCE_VALIDATION_EPOCH_SPAN,
            evidence_ref="synthetic:test",
        )


def test_epoch_record_state_root_length_invalid_raises():
    with pytest.raises(ValueError, match="epoch_record_state_root_length_invalid"):
        build_monthly_close_proof_from_epoch_record(
            _epoch_record(state_root=b"too-short"),
            matured_issuance_epoch=0,
            distribution_issuance_epoch=1,
            opening_validation_epoch=0,
            closing_validation_epoch=MIN_MONTHLY_ISSUANCE_VALIDATION_EPOCH_SPAN,
            evidence_ref="synthetic:test",
        )


def test_agg_sig_empty_raises():
    with pytest.raises(ValueError, match="epoch_record_agg_sig_bytes_required"):
        build_monthly_close_proof_from_epoch_record(
            _epoch_record(agg_sig=b""),
            matured_issuance_epoch=0,
            distribution_issuance_epoch=1,
            opening_validation_epoch=0,
            closing_validation_epoch=MIN_MONTHLY_ISSUANCE_VALIDATION_EPOCH_SPAN,
            evidence_ref="synthetic:test",
        )


def test_script_dry_run_has_no_commit_path():
    source = SCRIPT_PATH.read_text(encoding="utf-8")

    assert "commit_epoch_distribution" not in source
    assert "--commit" not in source


def test_script_arg_validation_rejects_nonfinite_timeout():
    module = _load_script_module()

    with pytest.raises(Exception, match="grpc_timeout_invalid"):
        module._require_positive_finite_timeout(float("nan"))


def test_script_arg_validation_rejects_nonfinite_synthetic_money():
    module = _load_script_module()

    with pytest.raises(Exception, match="non_negative_decimal"):
        module._parse_canonical_non_negative_decimal_string("NaN")


def test_validator_tls_context_keeps_certificate_verification(tmp_path, monkeypatch):
    module = _load_script_module()
    ca_path = tmp_path / "ca.pem"
    ca_path.write_text("", encoding="utf-8")

    class FakeContext:
        verify_flags = 0xFFFF
        verify_mode = object()
        check_hostname = True

    fake_context = FakeContext()
    monkeypatch_create_default_context = lambda **_: fake_context
    monkeypatch.setattr(module.ssl, "create_default_context", monkeypatch_create_default_context)

    context = module._create_validator_tls_context(ca_path)

    assert context is fake_context
    assert context.check_hostname is True
    assert context.verify_mode is not module.ssl.CERT_NONE


def test_live_report_path_does_not_construct_live_maturity_proof(tmp_path, monkeypatch):
    module = _load_script_module()
    evidence_path = tmp_path / "evidence.json"
    write_ecu_accrual_evidence(_evidence(), evidence_path)
    atlas_path = tmp_path / "atlas.json"
    atlas_path.write_text(
        json.dumps(
            {
                "assertions": [
                    {
                        "validator_agent_id": AGENT_ID,
                        "node_kind": "validator_grpc_endpoint_assertion",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    class FakeAdapter:
        def __init__(self, config, **kwargs):
            self.config = config
            self.kwargs = kwargs

        def get_epoch(self):
            return 1

        def get_epoch_record(self, epoch):
            assert epoch == 1
            return _epoch_record()

    monkeypatch.setattr(module, "ILCConsensusGrpcReadAdapter", FakeAdapter)
    monkeypatch.setattr(module, "_build_remote_server_cert_der_provider", lambda **_: lambda: b"der")
    monkeypatch.setattr(module, "_build_bls_verifier", lambda: (lambda *_: True))

    report = module.run(
        [
            "--validator-endpoint",
            "127.0.0.1:50151",
            "--tls-root-ca",
            __file__,
            "--client-cert",
            __file__,
            "--client-key",
            __file__,
            "--evidence-path",
            str(evidence_path),
            "--issuance-interval-id",
            "0",
            "--opening-validation-epoch",
            "0",
            "--distribution-issuance-epoch",
            "1",
            "--graph-binding-validator-agent-id",
            AGENT_ID,
            "--graph-binding-bls-key-hex",
            AGENT_ID,
            "--graph-binding-network-id",
            "public-rc",
            "--graph-binding-atlas-path",
            str(atlas_path),
            "--synthetic-total-epoch-fees-ilc",
            "0",
            "--synthetic-genesis-cumulative-accrual-ilc",
            "0",
            "--out",
            str(tmp_path / "out"),
        ]
    )

    assert report["live_current_epoch_seq"] == 1
    assert report["maturity_metadata_available"] is False
    assert report["live_maturity_proof_not_constructed_reason"] == (
        "closing_validation_epoch_not_available_from_get_epoch"
    )
    assert report["synthetic_conservation_verified"] is True
    assert "live_closing_validation_epoch" not in report


def test_graph_binding_args_required_when_guard_active(tmp_path):
    module = _load_script_module()
    evidence_path = tmp_path / "evidence.json"
    write_ecu_accrual_evidence(_evidence(), evidence_path)

    with pytest.raises(SystemExit, match="VALIDATOR_CERT_GRAPH_BINDING_NOT_ACTIVATED=False"):
        module.run(
            [
                "--validator-endpoint",
                "127.0.0.1:50151",
                "--tls-root-ca",
                __file__,
                "--client-cert",
                __file__,
                "--client-key",
                __file__,
                "--evidence-path",
                str(evidence_path),
                "--issuance-interval-id",
                "0",
                "--opening-validation-epoch",
                "0",
                "--distribution-issuance-epoch",
                "1",
                "--synthetic-total-epoch-fees-ilc",
                "0",
                "--synthetic-genesis-cumulative-accrual-ilc",
                "0",
            ]
        )
