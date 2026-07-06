from __future__ import annotations

import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import pytest

from tools import agent_loop_v1
from tools.testbed import run_three_node_seven_agent_scenario as scenario_runner
from tools.testbed.rehearsal_economics import (
    RehearsalEconomicsError,
    build_rehearsal_economics_record,
    conversion_receipt_activation_defaults,
    settlement_root_inputs_hash,
    verify_rehearsal_economics_record,
    write_json,
)
from tests.test_agent_loop_v1_runtime import _cdl069_seed, _legacy_seed, _submission, _task


ROOT = Path(__file__).resolve().parents[1]


def _accepted_submissions() -> list[dict[str, object]]:
    return [
        _submission(1, _cdl069_seed("01"), "cluster-a"),
        _submission(2, _cdl069_seed("02"), "cluster-b"),
        _submission(3, _cdl069_seed("03"), "cluster-c"),
        _submission(4, _cdl069_seed("04"), "cluster-a"),
        _submission(5, _cdl069_seed("05"), "cluster-b"),
        _submission(6, _cdl069_seed("06"), "cluster-c"),
        _submission(7, _cdl069_seed("07"), "cluster-d", variant="divergent"),
    ]


def _panel_payload() -> dict[str, object]:
    submissions = _accepted_submissions()
    outsider = agent_loop_v1._build_outsider_submission(
        _task(),
        _legacy_seed("08"),
        "cluster-e",
        "ilc-node-6",
    )
    panel = agent_loop_v1.evaluate_panel(
        task=_task(),
        submissions=submissions,
        outsider_submission=outsider,
    )
    claims = agent_loop_v1.build_ecu_claim_batch(_task(), panel)
    return {
        "ecu_claim_batch": {key: value for key, value in claims.items() if key not in {"marker", "runtime_version"}},
        "panel_result": panel["panel_result"],
    }


def _record() -> dict[str, object]:
    panel_payload = _panel_payload()
    return build_rehearsal_economics_record(
        namespace_id="phase1568-fix2l-test",
        accepted_submissions=_accepted_submissions(),
        ecu_claims=panel_payload["ecu_claim_batch"]["claims"],
        rehearsal_epoch=574,
        cumulative_issued_before_epoch_ilc="0",
        total_epoch_fees_ilc="0",
    )


def test_record_uses_agent_loop_claims_and_verifies_settlement_root() -> None:
    record = _record()
    verification = verify_rehearsal_economics_record(record)

    assert record["marker"] == "phase_1568_fix2l_rehearsal_economics_record"
    assert record["accepted_submission_count"] == 7
    assert record["ecu_claims_total_ecu"] == "5.8173828125"
    assert record["cdl048_dry_run_quote_path_verified"] is True
    assert record["cdl048_per_agent_lot_coverage_verified"] is True
    assert record["cdl048_four_issuance_epoch_quote_coverage_verified"] is True
    assert record["allocation_quote_verified"] is True
    assert verification["settlement_root_verified"] is True
    assert verification["settlement_root_hex"] == record["settlement_root_hex"]
    assert verification["cdl048_per_agent_lot_coverage_verified"] is True


def test_cdl048_quote_and_conversion_receipt_boundaries_remain_no_write() -> None:
    record = _record()
    quote = record["cdl048_conversion_quote"]
    assert isinstance(quote, dict)

    assert record["activation_requested"] is False
    assert record["cdl048_wallet_write_authorized"] is False
    assert quote["conversion_activation_authorized"] is False
    assert quote["ledger_write_authorized"] is False
    assert quote["wallet_write_authorized"] is False
    assert quote["public_claimability_activated"] is False
    assert record["cdl048_per_agent_lot_coverage"]["wallet_write_authorized"] is False
    assert all(value is False for value in conversion_receipt_activation_defaults().values())


def test_settlement_root_verifier_cli_recomputes_record(tmp_path: Path) -> None:
    record_path = tmp_path / "rehearsal_economics_record.json"
    write_json(record_path, _record())

    result = subprocess.run(
        [
            sys.executable,
            "tools/testbed/verify_settlement_root.py",
            "--record-path",
            str(record_path),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["marker"] == "phase_1568_fix2l_settlement_root_verified"
    assert payload["settlement_root_verified"] is True


def test_settlement_root_verifier_cli_fails_on_tampered_record(tmp_path: Path) -> None:
    record = _record()
    record["settlement_root_hex"] = "0" * 64
    record_path = tmp_path / "tampered.json"
    write_json(record_path, record)

    result = subprocess.run(
        [
            sys.executable,
            "tools/testbed/verify_settlement_root.py",
            "--record-path",
            str(record_path),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["settlement_root_verified"] is False
    assert payload["token"] == "settlement_root_hex_mismatch"


def test_verifier_rejects_current_record_missing_required_subrecords_by_default() -> None:
    record = _record()
    for key in (
        "cdl048_per_agent_lot_coverage",
        "cdl048_per_agent_lot_coverage_verified",
        "cdl048_four_issuance_epoch_quote_coverage_verified",
        "cdl048_conversion_coverage_mode",
    ):
        record.pop(key)
    record["settlement_root_inputs_sha256"] = settlement_root_inputs_hash(record)

    with pytest.raises(RehearsalEconomicsError) as excinfo:
        verify_rehearsal_economics_record(record)

    assert excinfo.value.token == "cdl048_per_agent_lot_coverage_required"


def test_verifier_rejects_accepted_submission_hash_mismatch() -> None:
    record = deepcopy(_record())
    record["accepted_submissions"][0]["output_hash"] = "tampered-output"

    with pytest.raises(RehearsalEconomicsError) as excinfo:
        verify_rehearsal_economics_record(record)

    assert excinfo.value.token in {
        "accepted_submissions_projection_mismatch",
        "accepted_submissions_hash_mismatch",
    }


def test_record_rejects_float_shaped_economic_claim_amount() -> None:
    panel_payload = _panel_payload()
    claims = list(panel_payload["ecu_claim_batch"]["claims"])
    claims[0] = dict(claims[0])
    claims[0]["amount"] = 1.0

    with pytest.raises(RehearsalEconomicsError) as excinfo:
        build_rehearsal_economics_record(
            namespace_id="phase1568-fix2l-test",
            accepted_submissions=_accepted_submissions(),
            ecu_claims=claims,
            rehearsal_epoch=574,
        )

    assert excinfo.value.token == "rehearsal_economics_float_rejected"


def test_scenario_runner_writes_rehearsal_economics_record(tmp_path: Path) -> None:
    panel_payload = _panel_payload()
    scenario = {"namespace_id": "phase1568-fix2l-test"}

    record = scenario_runner._emit_rehearsal_economics_record(
        scenario=scenario,
        task_payload=_task(),
        output_root=tmp_path,
        submissions=_accepted_submissions(),
        panel_payload=panel_payload,
    )

    record_path = tmp_path / "rehearsal_economics_record.json"
    assert record_path.exists()
    assert json.loads(record_path.read_text(encoding="utf-8"))["settlement_root_hex"] == record["settlement_root_hex"]


def test_scenario_manifest_includes_rehearsal_economics_references(tmp_path: Path) -> None:
    panel_payload = _panel_payload()
    record = _record()
    manifest = scenario_runner._scenario_manifest(
        scenario_path=ROOT / "testbed/scenarios/block6_seven_agent_v1.json",
        hosts_path=ROOT / "testbed/hosts.json",
        output_root=tmp_path,
        start_output="home_node_already_running",
        submissions=_accepted_submissions(),
        panel_payload=panel_payload,
        panel_broadcast={"send_statuses": []},
        claims_broadcast={"send_statuses": []},
        benchmark_metrics={},
        rehearsal_economics_record=record,
    )

    assert manifest["rehearsal_economics_record_file"] == "rehearsal_economics_record.json"
    assert manifest["rehearsal_settlement_root_hex"] == record["settlement_root_hex"]
    assert manifest["rehearsal_cdl048_wallet_write_authorized"] is False
    assert manifest["rehearsal_cdl048_per_agent_lot_count"] == 6
    assert manifest["rehearsal_cdl048_positive_claim_count"] == 6
    assert manifest["rehearsal_cdl048_four_epoch_quote_coverage_verified"] is True


def test_fix2l_does_not_clear_production_emission_guard() -> None:
    source = (ROOT / "ilc_core/epoch/epoch_emission_production_path.py").read_text(encoding="utf-8")
    assert "PRODUCTION_EMISSION_NOT_ACTIVATED = True" in source
    assert "PRODUCTION_EMISSION_NOT_ACTIVATED = False" not in source


def test_rehearsal_economics_module_does_not_use_simple_epoch_ledger() -> None:
    source = (ROOT / "tools/testbed/rehearsal_economics.py").read_text(encoding="utf-8")
    assert "SimpleEpochLedger" not in source
    assert "activation_requested=True," not in source
    assert "activation_requested=True)" not in source
