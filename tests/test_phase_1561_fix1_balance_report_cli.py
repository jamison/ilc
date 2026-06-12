"""Phase 1561-Fix1 per-agent balance/report CLI tests."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


CLI = [sys.executable, "-m", "ilc_core.cli.main"]


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [*CLI, *args],
        capture_output=True,
        check=False,
        text=True,
        timeout=10,
    )


def test_bare_balance_preserves_compat_without_float_or_acct_prototype() -> None:
    result = _run_cli("balance")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["command"] == "balance"
    assert payload["data"]["report_mode"] == "prototype_compat"
    assert payload["data"]["account_id"] == "prototype_compat"
    assert payload["data"]["balance_ilc"] == "0"
    assert payload["data"]["pending_balance_ilc"] == "0"
    assert "acct-prototype" not in result.stdout
    assert ".0" not in json.dumps(payload["data"], sort_keys=True)


def test_agent_balance_reports_phase_1561_smoke_evidence(tmp_path: Path) -> None:
    state_path = tmp_path / "ecu_live_smoke_1561.json"
    state_path.write_text(
        json.dumps(
            {
                "amounts": {"scheduled_emission_pool_ilc": "12.5"},
                "claim_id": "claim-1",
                "claiming_agent_id": "agent-a",
                "ecu_credit_event_hash": "event-hash",
                "phase": "1561",
                "production_emission_activated": False,
                "settlement_root_hash": "root-hash",
                "verifying_agent_id": "agent-b",
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    result = _run_cli(
        "balance",
        "--agent-id",
        "agent-a",
        "--state-json",
        str(state_path),
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    data = payload["data"]
    assert data["agent_id"] == "agent-a"
    assert data["balance_ilc"] == "0"
    assert data["balance_status"] == "not_settled_no_ledger_write"
    assert data["pending_smoke_report"]["amount_ilc"] == "12.5"
    assert data["pending_smoke_report"]["is_ledger_balance"] is False
    assert data["pending_smoke_report"]["role"] == "claiming_agent"
    assert data["report_mode"] == "phase_1561_smoke_evidence"


def test_agent_balance_rejects_float_state_amount(tmp_path: Path) -> None:
    state_path = tmp_path / "bad.json"
    state_path.write_text(
        json.dumps(
            {
                "amounts": {"scheduled_emission_pool_ilc": 12.5},
                "claiming_agent_id": "agent-a",
                "phase": "1561",
                "verifying_agent_id": "agent-b",
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    result = _run_cli(
        "balance",
        "--agent-id",
        "agent-a",
        "--state-json",
        str(state_path),
    )

    assert result.returncode == 1
    payload = json.loads(result.stderr)
    assert payload["ok"] is False
    assert "scheduled_emission_pool_ilc_must_be_exact_decimal_string" in payload["message"]
