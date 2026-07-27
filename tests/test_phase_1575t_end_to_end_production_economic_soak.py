from __future__ import annotations

import copy
import json
from decimal import Decimal
from pathlib import Path

import pytest

from ilc_core.epoch.genesis_settlement_destination import (
    GENESIS_AGENT1_AGENT_ID,
    GENESIS_WALLET_WRITE_AUTHORIZED,
)
from ilc_core.ledger.ecu_active_layer_runtime import EcuActiveLayerRuntime
from ilc_core.ledger.ecu_ilc_lifecycle_runtime import EcuIlcLifecycleRuntime, EcuIlcLifecycleRuntimeError
from ilc_core.ledger.cdl048_conversion_sweeper_runtime import (
    CDL048_ACTIVATED_PHASE_1388_TOKEN,
)
from ilc_core.storage.lmdb_public_runtime import LmdbWalletStore
import tools.phase1575t_e2e_production_soak as phase1575t
from tools.phase1575t_e2e_production_soak import (
    CONVERSION_DEADLINE_EPOCH_OFFSET,
    MAX_EPOCH_COUNT,
    MIN_EPOCH_COUNT,
    OUTPUT_TOKENS,
    PHASE,
    PROPOSED_P_E,
    SCHEMA_VERSION,
    build_e2e_production_soak_evidence,
    load_phase1560_agent_ids,
    run_e2e_production_soak,
    sha256_file,
    stable_json,
    stable_sha256,
    verify_soak_evidence,
)


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/phase1575t_e2e_production_soak.py"
PROMPT = (
    ROOT
    / "docs/antigravity_tasks/antigravity_prompt__phase_1575t_g10_end_to_end_production_economic_soak.md"
)


def _evidence(tmp_path: Path) -> dict:
    evidence = build_e2e_production_soak_evidence(output_root=tmp_path / "out")
    verify_soak_evidence(evidence)
    return evidence


def _certificate(evidence: dict) -> dict:
    return evidence["soak_completion_certificate"]


def _refresh_evidence_hashes(evidence: dict) -> None:
    certificate = evidence["soak_completion_certificate"]
    envelope = evidence["e2e_soak_envelope"]
    double_entry = evidence["double_entry_conservation"]
    certificate["gate_results"]["gate_5_double_entry_conservation"][
        "double_entry_conservation_sha256"
    ] = stable_sha256(double_entry)
    envelope["double_entry_conservation_sha256"] = stable_sha256(double_entry)
    certificate["e2e_soak_envelope_sha256"] = stable_sha256(envelope)
    body = dict(certificate)
    body.pop("certificate_payload_sha256", None)
    certificate["certificate_payload_sha256"] = stable_sha256(body)


def test_gate_1_non_synthetic_ecu_confirmed(tmp_path: Path) -> None:
    evidence = _evidence(tmp_path)
    cert = _certificate(evidence)

    assert cert["gate_results"]["gate_1_non_synthetic_ecu"]["pass"] is True
    assert Decimal(cert["gate_results"]["gate_1_non_synthetic_ecu"]["total_ecu_generated"]) > Decimal("0")
    for agent_id in load_phase1560_agent_ids():
        assert len(agent_id) == 96
        assert not agent_id.startswith("soak_agent_")


def test_gate_2_cdl048_live_conversion_confirmed(tmp_path: Path) -> None:
    evidence = _evidence(tmp_path)
    gate = _certificate(evidence)["gate_results"]["gate_2_cdl048_live_conversion"]

    assert gate["pass"] is True
    assert gate["activation_token"] == CDL048_ACTIVATED_PHASE_1388_TOKEN
    assert Decimal(gate["total_agent_ilc_credit"]) > Decimal("0")
    assert Decimal(gate["total_debit_value_ilc"]) == Decimal(gate["total_agent_ilc_credit"])
    for epoch in evidence["epoch_records"]:
        for quote in epoch["cdl048_quote_payloads"]:
            assert CDL048_ACTIVATED_PHASE_1388_TOKEN in quote["tokens"]
            assert quote["conversion_activation_authorized"] is True
            assert quote["public_claimability_activated"] is False
            assert Decimal(quote["effective_p_e"]) == PROPOSED_P_E


def test_gate_3_genesis_ilc_credit_confirmed(tmp_path: Path) -> None:
    evidence = _evidence(tmp_path)
    gate = _certificate(evidence)["gate_results"]["gate_3_genesis_ilc_credit"]

    assert gate["pass"] is True
    assert gate["wallet_status"]["data"]["agent_id"] == GENESIS_AGENT1_AGENT_ID
    assert gate["wallet_status"]["data"]["claimability_state"] == "deferred"
    assert Decimal(gate["genesis_ilc_credit"]) > Decimal("0")
    assert Decimal(gate["wallet_status"]["data"]["balance_ilc"]) == Decimal(gate["genesis_ilc_credit"])


def test_gate_4_e2e_evidence_envelope_complete(tmp_path: Path) -> None:
    evidence = _evidence(tmp_path)
    gate = _certificate(evidence)["gate_results"]["gate_4_e2e_evidence_envelope_complete"]
    envelope = evidence["e2e_soak_envelope"]

    assert gate["pass"] is True
    assert gate["e2e_soak_envelope_sha256"] == stable_sha256(envelope)
    assert envelope["cdl048_wire_quote_summary"]["quote_count"] > 0
    assert envelope["lifecycle_commit_receipts"]
    assert envelope["genesis_credit_summary"]["total_ilc"] != "0"


def test_gate_5_double_entry_conservation_proven(tmp_path: Path) -> None:
    evidence = _evidence(tmp_path)
    proof = evidence["double_entry_conservation"]

    assert _certificate(evidence)["gate_results"]["gate_5_double_entry_conservation"]["pass"] is True
    assert proof["proven"] is True
    ecu = proof["ecu_equation"]
    assert Decimal(ecu["total_ecu_converted"]) + Decimal(ecu["total_ecu_remaining"]) == Decimal(
        ecu["total_ecu_generated"]
    )
    cdl048 = proof["cdl048_value_equation"]
    assert (
        Decimal(cdl048["total_debit_value_ilc_from_quotes"])
        == Decimal(cdl048["total_ilc_credit_from_quotes"])
        == Decimal(cdl048["total_agent_ilc_wallet_readback"])
    )
    base = proof["base_emission_fee_equation"]
    assert Decimal(base["total_fee_input_ilc"]) == Decimal(base["total_fee_accounted_ilc"])


def test_no_synthetic_agent_ids_in_evidence(tmp_path: Path) -> None:
    encoded = stable_json(_evidence(tmp_path))

    assert "soak_agent_" not in encoded


def test_all_amounts_are_decimal_not_float(tmp_path: Path) -> None:
    encoded = stable_json(_evidence(tmp_path))

    assert "NaN" not in encoded
    assert "Infinity" not in encoded


def test_genesis_credit_per_epoch_equals_overhead_pool(tmp_path: Path) -> None:
    evidence = _evidence(tmp_path)
    expected = sum(
        (Decimal(record["genesis_overhead_pool_ilc"]) for record in evidence["epoch_records"]),
        Decimal("0"),
    )
    actual = Decimal(evidence["e2e_soak_envelope"]["genesis_credit_summary"]["total_ilc"])

    assert actual == expected


def test_ilc_balances_non_negative(tmp_path: Path) -> None:
    ledger = _evidence(tmp_path)["balance_ledger"]

    assert Decimal(ledger["genesis_balance"]["balance_ilc"]) >= Decimal("0")
    for row in ledger["agent_balances"]:
        assert Decimal(row["balance_ilc"]) >= Decimal("0")
        assert Decimal(row["balance_ecu_remaining"]) >= Decimal("0")


def test_settlement_root_deterministic_across_replays(tmp_path: Path) -> None:
    first = _evidence(tmp_path / "first")["soak_completion_certificate"]
    second = _evidence(tmp_path / "second")["soak_completion_certificate"]

    assert first["e2e_soak_envelope_sha256"] == second["e2e_soak_envelope_sha256"]
    assert first["base_emission_settlement_root_sha256"] == second["base_emission_settlement_root_sha256"]


def test_completion_certificate_no_ilc_conversion_false(tmp_path: Path) -> None:
    assert _certificate(_evidence(tmp_path))["no_ilc_conversion"] is False


def test_completion_certificate_no_wallet_provider_spend_transfer_withdrawal_writes_true(
    tmp_path: Path,
) -> None:
    cert = _certificate(_evidence(tmp_path))

    assert cert["no_wallet_provider_spend_transfer_withdrawal_writes"] is True
    assert cert["lifecycle_lmdb_settlement_writes_observed"] is True
    assert cert["genesis_wallet_write_authorized"] is False
    assert GENESIS_WALLET_WRITE_AUTHORIZED is False
    assert cert["non_claims"]["wallet_transfer_enabled"] is False


def test_evidence_atomic_writes(tmp_path: Path) -> None:
    source = TOOL.read_text(encoding="utf-8")
    result = run_e2e_production_soak(output_root=tmp_path / "out")

    assert "tempfile.mkstemp" in source
    assert "os.replace" in source
    assert "os.fsync" in source
    assert Path(result["certificate_path"]).is_file()
    assert result["certificate_sha256"] == sha256_file(Path(result["certificate_path"]))


def test_epoch_count_minimum_three(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="phase1575t_epoch_count_minimum_three"):
        build_e2e_production_soak_evidence(output_root=tmp_path / "out", epoch_count=2)

    assert _certificate(_evidence(tmp_path))["epoch_count"] == MIN_EPOCH_COUNT


def test_epoch_count_maximum_bound(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="phase1575t_epoch_count_exceeded"):
        build_e2e_production_soak_evidence(
            output_root=tmp_path / "out",
            epoch_count=MAX_EPOCH_COUNT + 1,
        )


def test_genesis_minting_guard_false_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(phase1575t, "GENESIS_MINTING_AUTHORIZED", False)

    with pytest.raises(ValueError, match="phase1575t_genesis_minting_not_authorized"):
        build_e2e_production_soak_evidence(output_root=tmp_path / "out")


def test_deadline_epoch_offset_is_exercised(tmp_path: Path) -> None:
    evidence = build_e2e_production_soak_evidence(
        output_root=tmp_path / "out",
        conversion_epoch_offset=CONVERSION_DEADLINE_EPOCH_OFFSET,
    )

    for epoch in evidence["epoch_records"]:
        for quote in epoch["cdl048_quote_payloads"]:
            assert quote["conversion_epoch"] == quote["deadline_epoch"]


def test_post_deadline_epoch_offset_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="phase1575t_conversion_epoch_offset_exceeds_deadline"):
        build_e2e_production_soak_evidence(
            output_root=tmp_path / "out",
            conversion_epoch_offset=CONVERSION_DEADLINE_EPOCH_OFFSET + 1,
        )


def test_non_unit_price_changes_ilc_quantity_and_conserves_value(tmp_path: Path) -> None:
    floor = build_e2e_production_soak_evidence(output_root=tmp_path / "floor", proposed_p_e=Decimal("0.75"))
    neutral = build_e2e_production_soak_evidence(output_root=tmp_path / "neutral", proposed_p_e=Decimal("1.00"))
    ceiling = build_e2e_production_soak_evidence(output_root=tmp_path / "ceiling", proposed_p_e=Decimal("1.30"))

    for evidence in (floor, neutral, ceiling):
        proof = evidence["double_entry_conservation"]
        assert proof["proven"] is True
        equation = proof["cdl048_value_equation"]
        assert Decimal(equation["total_debit_value_ilc_from_quotes"]) == Decimal(
            equation["total_ilc_credit_from_quotes"]
        )

    floor_quote = floor["epoch_records"][0]["cdl048_quote_payloads"][0]
    neutral_quote = neutral["epoch_records"][0]["cdl048_quote_payloads"][0]
    ceiling_quote = ceiling["epoch_records"][0]["cdl048_quote_payloads"][0]
    assert Decimal(floor_quote["amount_ilc_credit"]) < Decimal(floor_quote["amount_ecu_debit"])
    assert Decimal(neutral_quote["amount_ilc_credit"]) == Decimal(neutral_quote["amount_ecu_debit"])
    assert Decimal(ceiling_quote["amount_ilc_credit"]) > Decimal(ceiling_quote["amount_ecu_debit"])


def test_default_price_is_non_unit_canary(tmp_path: Path) -> None:
    evidence = _evidence(tmp_path)
    ecu = Decimal(evidence["double_entry_conservation"]["ecu_equation"]["total_ecu_converted"])
    ilc = Decimal(
        evidence["double_entry_conservation"]["cdl048_value_equation"]["total_ilc_credit_from_quotes"]
    )

    assert PROPOSED_P_E != Decimal("1.00")
    assert ilc != ecu


def test_lifecycle_rejects_non_finite_reward_delta(tmp_path: Path) -> None:
    store = LmdbWalletStore(tmp_path / "wallet_lmdb")
    runtime = EcuIlcLifecycleRuntime(wallet_store=store, ecu_runtime=EcuActiveLayerRuntime())
    try:
        with pytest.raises(EcuIlcLifecycleRuntimeError) as exc_info:
            runtime.commit_settled_epoch(
                agent_id="a" * 96,
                epoch_id="phase1575t:test:nonfinite",
                reward_delta_ilc=Decimal("NaN"),
            )
    finally:
        store.close()

    assert exc_info.value.token == "lifecycle_reward_delta_invalid"


def test_verify_rejects_tampered_balance_ledger(tmp_path: Path) -> None:
    evidence = _evidence(tmp_path)
    tampered = copy.deepcopy(evidence)
    tampered["balance_ledger"]["agent_balances"][0]["balance_ilc"] = "0"

    with pytest.raises(ValueError, match="phase1575t_balance_ledger_sha256_mismatch"):
        verify_soak_evidence(tampered)


def test_verify_rejects_tampered_double_entry_value(tmp_path: Path) -> None:
    evidence = _evidence(tmp_path)
    tampered = copy.deepcopy(evidence)
    tampered["double_entry_conservation"]["ecu_equation"]["total_ecu_generated"] = "999"

    with pytest.raises(ValueError, match="phase1575t_double_entry_sha256_mismatch"):
        verify_soak_evidence(tampered)


def test_verify_rejects_tampered_quote_payload(tmp_path: Path) -> None:
    evidence = _evidence(tmp_path)
    tampered = copy.deepcopy(evidence)
    tampered["epoch_records"][0]["cdl048_quote_payloads"][0]["amount_ilc_credit"] = "0"

    with pytest.raises(ValueError, match="phase1575t_quote_payloads_sha256_mismatch"):
        verify_soak_evidence(tampered)


def test_verify_rejects_non_finite_double_entry_even_when_hashes_match(tmp_path: Path) -> None:
    evidence = _evidence(tmp_path)
    tampered = copy.deepcopy(evidence)
    ecu = tampered["double_entry_conservation"]["ecu_equation"]
    ecu["total_ecu_converted"] = "Infinity"
    ecu["total_ecu_generated"] = "Infinity"
    ecu["total_ecu_remaining"] = "0"
    ecu["holds"] = True
    _refresh_evidence_hashes(tampered)

    with pytest.raises(ValueError, match="phase1575t_ecu_equation_non_finite"):
        verify_soak_evidence(tampered)


def test_verify_rejects_envelope_epoch_count_mismatch_when_hashes_match(tmp_path: Path) -> None:
    evidence = _evidence(tmp_path)
    tampered = copy.deepcopy(evidence)
    tampered["e2e_soak_envelope"]["epoch_count"] = tampered["soak_completion_certificate"]["epoch_count"] + 1
    _refresh_evidence_hashes(tampered)

    with pytest.raises(ValueError, match="phase1575t_envelope_epoch_count_mismatch"):
        verify_soak_evidence(tampered)


def test_verify_rejects_envelope_summary_mismatch_when_hashes_match(tmp_path: Path) -> None:
    evidence = _evidence(tmp_path)
    tampered = copy.deepcopy(evidence)
    tampered["e2e_soak_envelope"]["cdl048_wire_quote_summary"]["total_agent_ilc_credit"] = "0"
    _refresh_evidence_hashes(tampered)

    with pytest.raises(ValueError, match="phase1575t_summary_ilc_credit_mismatch"):
        verify_soak_evidence(tampered)


def test_all_five_gates_pass_in_certificate(tmp_path: Path) -> None:
    cert = _certificate(_evidence(tmp_path))

    assert cert["schema_version"] == SCHEMA_VERSION
    assert cert["phase"] == PHASE
    assert set(cert["output_tokens"]) == set(OUTPUT_TOKENS)
    assert len(cert["gate_results"]) == 5
    assert all(gate["pass"] is True for gate in cert["gate_results"].values())


def test_run_writes_all_required_artifacts(tmp_path: Path) -> None:
    result = run_e2e_production_soak(output_root=tmp_path / "out")

    for key in (
        "certificate_path",
        "double_entry_conservation_path",
        "e2e_soak_envelope_path",
        "final_balance_ledger_path",
    ):
        assert Path(result[key]).is_file()
    assert len(result["epoch_evidence_paths"]) == MIN_EPOCH_COUNT
    for path in result["epoch_evidence_paths"]:
        assert Path(path).is_file()
    verify_soak_evidence(
        {
            "balance_ledger": json.loads(Path(result["final_balance_ledger_path"]).read_text(encoding="utf-8")),
            "double_entry_conservation": json.loads(
                Path(result["double_entry_conservation_path"]).read_text(encoding="utf-8")
            ),
            "e2e_soak_envelope": json.loads(Path(result["e2e_soak_envelope_path"]).read_text(encoding="utf-8")),
            "epoch_records": [
                json.loads(Path(path).read_text(encoding="utf-8"))
                for path in result["epoch_evidence_paths"]
            ],
            "soak_completion_certificate": json.loads(Path(result["certificate_path"]).read_text(encoding="utf-8")),
        }
    )


def test_prompt_records_correct_e2e_envelope_scope() -> None:
    text = PROMPT.read_text(encoding="utf-8")

    assert "1575t_e2e_soak_root" in text
    assert "Do NOT claim `compute_settlement_root()` itself includes conversion" in text
    assert "PublicWalletRuntime(wallet_store=<wallet_store>, lifecycle_runtime=<lifecycle_runtime>).wallet_status" in text
