"""Phase 1561 guarded ECU live smoke evidence tests."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from ilc_core.epoch.epoch_emission_production_path import (
    PRODUCTION_EMISSION_NOT_ACTIVATED,
)


EVIDENCE_PATH = Path("out/ecu_live_smoke_1561.json")
EXPECTED_ROOT_SCHEMA = "epoch_emission_event_batch_root_1537p_fix1.v0.2"
EXPECTED_RUNTIME_VERSION = "epoch_emission_runtime_1345.v0.1"
EXPECTED_GUARD_TOKEN = "PRODUCTION_EMISSION_NOT_ACTIVATED"


def _read_evidence() -> dict[str, Any]:
    if not EVIDENCE_PATH.exists():
        raise AssertionError("Phase 1561 output is missing: out/ecu_live_smoke_1561.json")
    payload = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def _walk(value: Any) -> list[Any]:
    found = [value]
    if isinstance(value, dict):
        for key, item in value.items():
            found.extend(_walk(key))
            found.extend(_walk(item))
    elif isinstance(value, list):
        for item in value:
            found.extend(_walk(item))
    return found


def test_phase_1561_evidence_required_fields_and_constants() -> None:
    evidence = _read_evidence()
    required_fields = {
        "claim_id",
        "claiming_agent_id",
        "epoch",
        "ecu_credit_event_hash",
        "settlement_root_hash",
        "settlement_root_schema_version",
        "verifying_agent_id",
        "verification_result",
        "guard_token",
        "production_emission_activated",
        "epoch_emission_runtime_version",
        "production_emission_activation_token",
        "phase",
    }

    assert required_fields <= set(evidence)
    assert evidence["phase"] == "1561"
    assert evidence["epoch"] == 1
    assert evidence["production_emission_activated"] is False
    assert evidence["guard_token"] == EXPECTED_GUARD_TOKEN
    assert evidence["settlement_root_schema_version"] == EXPECTED_ROOT_SCHEMA
    assert evidence["epoch_emission_runtime_version"] == EXPECTED_RUNTIME_VERSION
    assert evidence["verification_result"] == "pass"


def test_phase_1561_agents_are_live_and_distinct() -> None:
    evidence = _read_evidence()

    assert isinstance(evidence["claiming_agent_id"], str)
    assert isinstance(evidence["verifying_agent_id"], str)
    assert evidence["claiming_agent_id"]
    assert evidence["verifying_agent_id"]
    assert evidence["claiming_agent_id"] != evidence["verifying_agent_id"]
    assert evidence["claiming_agent_label"] == "Validator-A1"
    assert evidence["verifying_agent_label"] == "Validator-B1"


def test_phase_1561_no_float_values_anywhere() -> None:
    evidence = _read_evidence()

    assert not any(isinstance(item, float) for item in _walk(evidence))


def test_phase_1561_guard_is_still_true_in_live_module() -> None:
    assert PRODUCTION_EMISSION_NOT_ACTIVATED is True


def test_phase_1561_claim_id_is_canonical_hash() -> None:
    evidence = _read_evidence()
    canonical = json.dumps(
        evidence["claim_inputs"],
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
        ensure_ascii=True,
    ).encode("utf-8")

    assert hashlib.sha256(canonical).hexdigest() == evidence["claim_id"]


def test_phase_1561_independent_root_verification_passed() -> None:
    evidence = _read_evidence()
    verification = evidence["independent_verification"]

    assert evidence["event_payload_batch_matches_settlement_root_payload"] is True
    assert verification["root_payload_hash_matches_settlement_root_hash"] is True
    assert verification["event_records_all_reference_settlement_root"] is True
    assert len(evidence["settlement_root_hash"]) == 64
    assert all(char in "0123456789abcdef" for char in evidence["settlement_root_hash"])
    assert len(evidence["ecu_credit_event_hash"]) == 64
    assert all(char in "0123456789abcdef" for char in evidence["ecu_credit_event_hash"])


def test_phase_1561_balance_report_command_confirmed() -> None:
    evidence = _read_evidence()
    check = evidence["balance_report_command_check"]

    assert evidence["conditional_token"] == "user_facing_balance_report_command_confirmed_phase_1561"
    assert check["accepted_as_user_facing_per_agent_report"] is True
    assert check["probe_status"] == "confirmed"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ilc_core.cli.main",
            "balance",
            "--agent-id",
            evidence["claiming_agent_id"],
            "--state-json",
            str(EVIDENCE_PATH),
        ],
        capture_output=True,
        check=False,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    data = payload["data"]
    assert data["agent_id"] == evidence["claiming_agent_id"]
    assert data["balance_ilc"] == "0"
    assert data["balance_status"] == "not_settled_no_ledger_write"
    assert data["pending_smoke_report"]["is_ledger_balance"] is False
    assert data["report_mode"] == "phase_1561_smoke_evidence"
