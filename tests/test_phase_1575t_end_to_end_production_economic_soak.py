from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

import pytest

from ilc_core.epoch.genesis_settlement_destination import (
    GENESIS_AGENT1_AGENT_ID,
    GENESIS_WALLET_WRITE_AUTHORIZED,
)
from ilc_core.ledger.cdl048_conversion_sweeper_runtime import (
    CDL048_ACTIVATED_PHASE_1388_TOKEN,
)
from tools.phase1575t_e2e_production_soak import (
    MIN_EPOCH_COUNT,
    OUTPUT_TOKENS,
    PHASE,
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
    for epoch in evidence["epoch_records"]:
        for quote in epoch["cdl048_quote_payloads"]:
            assert CDL048_ACTIVATED_PHASE_1388_TOKEN in quote["tokens"]
            assert quote["conversion_activation_authorized"] is True
            assert quote["public_claimability_activated"] is False


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
    ilc = proof["ilc_equation"]
    assert (
        Decimal(ilc["total_ilc_credited_to_agents"])
        + Decimal(ilc["genesis_ilc_credit"])
        + Decimal(ilc["ilc_burned"])
        == Decimal(ilc["total_ilc_emitted"])
    )


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


def test_completion_certificate_no_wallet_writes_true(tmp_path: Path) -> None:
    cert = _certificate(_evidence(tmp_path))

    assert cert["no_wallet_writes"] is True
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
            "soak_completion_certificate": json.loads(Path(result["certificate_path"]).read_text(encoding="utf-8")),
        }
    )


def test_prompt_records_correct_e2e_envelope_scope() -> None:
    text = PROMPT.read_text(encoding="utf-8")

    assert "1575t_e2e_soak_root" in text
    assert "Do NOT claim `compute_settlement_root()` itself includes conversion" in text
    assert "PublicWalletRuntime(wallet_store=<wallet_store>, lifecycle_runtime=<lifecycle_runtime>).wallet_status" in text
