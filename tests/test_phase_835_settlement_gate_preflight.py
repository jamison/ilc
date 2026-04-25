"""Phase 835 — settlement-path dry-run preflight tool tests.

Covers:
  - Version pin
  - None posture (default) passes for any config
  - Unknown settlement_path value rejected
  - MysticetiFastPath requires non-empty network_id
  - MysticetiFastPath requires estimated f >= 1 (N >= 4 peers)
  - MysticetiFastPath passes with valid network_id and enough peers
  - --config-dir glob collects *_config.json files
  - Smoke harness now emits smoke_settlement_gate_preflight_ok marker
  - Preflight tool is published with correct version token
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT = REPO_ROOT / "tools" / "settlement_gate_preflight.py"
SMOKE_HARNESS = REPO_ROOT / "tools" / "run_three_machine_smoke_phase_572.sh"
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "phase_572_three_machine_smoke"


def _run_preflight(*args: str) -> tuple[int, str]:
    """Run the preflight tool, return (exit_code, combined_output)."""
    result = subprocess.run(
        [sys.executable, str(PREFLIGHT)] + list(args),
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout + result.stderr


def _write_config(tmp_path: Path, name: str, data: dict) -> Path:
    p = tmp_path / f"{name}_config.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# Version and publication
# ---------------------------------------------------------------------------

def test_preflight_tool_exists() -> None:
    assert PREFLIGHT.exists()


def test_preflight_version_token_in_source() -> None:
    text = PREFLIGHT.read_text(encoding="utf-8")
    assert "settlement_gate_preflight_835_published" in text
    assert 'PREFLIGHT_VERSION = "settlement_gate_preflight_835.v0.1"' in text


def test_preflight_emits_version_on_run(tmp_path: Path) -> None:
    cfg = _write_config(tmp_path, "node", {"node_id": "n1"})
    code, out = _run_preflight("--config", str(cfg))
    assert "settlement_gate_preflight_version" in out
    assert "settlement_gate_preflight_835.v0.1" in out


# ---------------------------------------------------------------------------
# None posture (default — field absent)
# ---------------------------------------------------------------------------

def test_none_posture_passes_when_field_absent(tmp_path: Path) -> None:
    cfg = _write_config(tmp_path, "node", {"node_id": "n1"})
    code, out = _run_preflight("--config", str(cfg))
    assert code == 0
    assert "settlement_gate_preflight_none_posture_preserved" in out
    assert "settlement_gate_preflight_all_pass" in out


def test_none_posture_passes_when_field_is_none_string(tmp_path: Path) -> None:
    cfg = _write_config(tmp_path, "node", {"node_id": "n1", "settlement_path": "none"})
    code, out = _run_preflight("--config", str(cfg))
    assert code == 0
    assert "settlement_gate_preflight_none_posture_preserved" in out


def test_none_posture_passes_when_field_is_empty_string(tmp_path: Path) -> None:
    cfg = _write_config(tmp_path, "node", {"node_id": "n1", "settlement_path": ""})
    code, out = _run_preflight("--config", str(cfg))
    assert code == 0
    assert "settlement_gate_preflight_none_posture_preserved" in out


# ---------------------------------------------------------------------------
# Unknown value
# ---------------------------------------------------------------------------

def test_unknown_settlement_path_rejected(tmp_path: Path) -> None:
    cfg = _write_config(tmp_path, "node", {"node_id": "n1", "settlement_path": "legacy_path"})
    code, out = _run_preflight("--config", str(cfg))
    assert code == 1
    assert "settlement_gate_preflight_unknown_value" in out


# ---------------------------------------------------------------------------
# MysticetiFastPath — network_id guard
# ---------------------------------------------------------------------------

def test_mysticeti_requires_network_id(tmp_path: Path) -> None:
    cfg = _write_config(tmp_path, "node", {
        "node_id": "n1",
        "settlement_path": "mysticeti_fast_path",
        "peers": ["p1", "p2", "p3"],  # N=4 → f=1
    })
    code, out = _run_preflight("--config", str(cfg))
    assert code == 1
    assert "non-empty network_id" in out


def test_mysticeti_requires_non_empty_network_id(tmp_path: Path) -> None:
    cfg = _write_config(tmp_path, "node", {
        "node_id": "n1",
        "settlement_path": "mysticeti_fast_path",
        "network_id": "",
        "peers": ["p1", "p2", "p3"],
    })
    code, out = _run_preflight("--config", str(cfg))
    assert code == 1
    assert "non-empty network_id" in out


# ---------------------------------------------------------------------------
# MysticetiFastPath — f >= 1 guard
# ---------------------------------------------------------------------------

def test_mysticeti_fails_with_no_peers(tmp_path: Path) -> None:
    """N=1 (self only, no peers) → f=0 → rejected."""
    cfg = _write_config(tmp_path, "node", {
        "node_id": "n1",
        "settlement_path": "mysticeti_fast_path",
        "network_id": "testnet-1",
        "peers": [],
    })
    code, out = _run_preflight("--config", str(cfg))
    assert code == 1
    assert "sec_warn_settlement_gate_f_zero" in out
    assert "HIGH-002" in out


def test_mysticeti_fails_with_two_peers(tmp_path: Path) -> None:
    """N=3 (self + 2 peers) → f=0 → rejected."""
    cfg = _write_config(tmp_path, "node", {
        "node_id": "n1",
        "settlement_path": "mysticeti_fast_path",
        "network_id": "testnet-1",
        "peers": ["p1", "p2"],
    })
    code, out = _run_preflight("--config", str(cfg))
    assert code == 1
    assert "sec_warn_settlement_gate_f_zero" in out


def test_mysticeti_passes_with_three_peers(tmp_path: Path) -> None:
    """N=4 (self + 3 peers) → f=1 → accepted."""
    cfg = _write_config(tmp_path, "node", {
        "node_id": "n1",
        "settlement_path": "mysticeti_fast_path",
        "network_id": "testnet-1",
        "peers": ["p1", "p2", "p3"],
    })
    code, out = _run_preflight("--config", str(cfg))
    assert code == 0
    assert "settlement_gate_preflight_mysticeti_fast_path_ok" in out
    assert "Rollback: set settlement_path=none" in out


def test_mysticeti_passes_with_six_peers(tmp_path: Path) -> None:
    """N=7 → f=2 → accepted."""
    cfg = _write_config(tmp_path, "node", {
        "node_id": "n1",
        "settlement_path": "mysticeti_fast_path",
        "network_id": "testnet-2",
        "peers": [f"p{i}" for i in range(6)],
    })
    code, out = _run_preflight("--config", str(cfg))
    assert code == 0
    assert "settlement_gate_preflight_mysticeti_fast_path_ok" in out


# ---------------------------------------------------------------------------
# Multiple configs / --config-dir
# ---------------------------------------------------------------------------

def test_all_none_posture_configs_pass(tmp_path: Path) -> None:
    for i in range(3):
        _write_config(tmp_path, f"node{i+1}", {"node_id": f"n{i+1}"})
    code, out = _run_preflight("--config-dir", str(tmp_path))
    assert code == 0
    assert "3 passed, 0 failed" in out
    assert "settlement_gate_preflight_all_pass" in out


def test_one_failing_config_fails_suite(tmp_path: Path) -> None:
    _write_config(tmp_path, "node1", {"node_id": "n1"})                 # passes
    _write_config(tmp_path, "node2", {"node_id": "n2", "settlement_path": "bad"})  # fails
    code, out = _run_preflight("--config-dir", str(tmp_path))
    assert code == 1
    assert "1 passed, 1 failed" in out


def test_fixture_dir_passes_preflight() -> None:
    """The existing Phase 572 fixture dir (all none-posture configs) must pass."""
    if not FIXTURE_DIR.exists():
        pytest.skip("phase_572 fixture dir not present")
    code, out = _run_preflight("--config-dir", str(FIXTURE_DIR))
    assert code == 0
    assert "settlement_gate_preflight_all_pass" in out


def test_no_args_exits_nonzero() -> None:
    result = subprocess.run(
        [sys.executable, str(PREFLIGHT)],
        capture_output=True, text=True,
    )
    assert result.returncode != 0


# ---------------------------------------------------------------------------
# Smoke harness integration
# ---------------------------------------------------------------------------

def test_smoke_harness_contains_preflight_step() -> None:
    text = SMOKE_HARNESS.read_text(encoding="utf-8")
    assert "settlement_gate_preflight.py" in text
    assert "smoke_settlement_gate_preflight_ok" in text
    assert "smoke_settlement_gate_preflight_fail" in text


def test_smoke_harness_operator_guide_lists_preflight_marker() -> None:
    text = SMOKE_HARNESS.read_text(encoding="utf-8")
    # The operator-guide mode must list the new marker in its expected output
    assert "smoke_settlement_gate_preflight_ok" in text
