from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from tools.phase_1575h_live_quorum_preflight import (
    PHASE1360_VALIDATORS,
    atomic_write_json,
    bool_constant_from_file,
    build_evidence,
    quorum_threshold,
    status_token_checks,
    udp_listener_probe,
    validator_endpoint_checks,
)


def test_quorum_threshold_matches_bft_formula() -> None:
    assert quorum_threshold(1) == 1
    assert quorum_threshold(2) == 1
    assert quorum_threshold(3) == 1
    assert quorum_threshold(4) == 3
    assert quorum_threshold(7) == 5
    assert quorum_threshold(10) == 7


def test_quorum_threshold_rejects_empty_validator_set() -> None:
    with pytest.raises(ValueError, match="validator_count_must_be_positive"):
        quorum_threshold(0)


def test_bool_constant_from_file_reads_literal_assignment(tmp_path: Path) -> None:
    p = tmp_path / "runtime.py"
    p.write_text(
        "OTHER = True\nPRODUCTION_EMISSION_NOT_ACTIVATED = False\n",
        encoding="utf-8",
    )
    assert bool_constant_from_file(p, "PRODUCTION_EMISSION_NOT_ACTIVATED") is False
    assert bool_constant_from_file(p, "OTHER") is True
    assert bool_constant_from_file(p, "MISSING") is None


def test_status_token_checks_detect_missing_tokens(tmp_path: Path) -> None:
    status_path = tmp_path / "docs/phases"
    status_path.mkdir(parents=True)
    (status_path / "STATUS.md").write_text("public_rc_live_phase_1575c\n", encoding="utf-8")

    result = status_token_checks(tmp_path)

    assert result["tokens"]["public_rc_live_phase_1575c"]["present"] is True
    assert result["passed"] is False


def test_atomic_write_json_uses_private_temp_file_mode(tmp_path: Path) -> None:
    out = tmp_path / "nested" / "evidence.json"
    atomic_write_json(out, {"b": 2, "a": 1})

    assert json.loads(out.read_text(encoding="utf-8")) == {"a": 1, "b": 2}
    assert oct(os.stat(out).st_mode & 0o777) == "0o600"
    assert out.read_text(encoding="utf-8").startswith('{"a":1,"b":2}')


def test_build_evidence_no_ssh_records_non_activation_boundary() -> None:
    evidence = build_evidence(Path.cwd(), include_ssh=False)

    assert evidence["phase"] == "1575h-readiness"
    assert evidence["activation_boundary"]["read_only_preflight"] is True
    assert evidence["activation_boundary"]["started_validator_processes"] is False
    assert evidence["activation_boundary"]["sent_epoch_checkpoint"] is False
    assert evidence["activation_boundary"]["executed_epoch_0_to_1_transition"] is False
    assert evidence["vps_check"]["skipped"] is True
    assert isinstance(evidence["ready_for_1575h"], bool)


def test_udp_listener_probe_uses_remote_ss_udp_local_address_column(monkeypatch: pytest.MonkeyPatch) -> None:
    commands: list[str] = []

    def fake_ssh_command(alias: str, command: str, *, timeout_seconds: int) -> dict[str, object]:
        commands.append(command)
        return {
            "argv": ["ssh", alias, command],
            "returncode": 0,
            "stdout": "UNCONN 0 0 100.112.32.42:50155 0.0.0.0:*",
            "stderr": "",
            "timed_out": False,
        }

    monkeypatch.setattr(
        "tools.phase_1575h_live_quorum_preflight.ssh_command",
        fake_ssh_command,
    )

    result = udp_listener_probe(PHASE1360_VALIDATORS[0])

    assert result["open"] is True
    assert result["transport"] == "udp"
    assert result["probe_method"] == "remote_ss_udp_listener"
    assert "$4 ~ /:50155$/" in commands[0]
    assert "$5 ~" not in commands[0]


def test_validator_endpoint_checks_counts_udp_quorum(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_ssh_command(alias: str, command: str, *, timeout_seconds: int) -> dict[str, object]:
        return {
            "argv": ["ssh", alias, command],
            "returncode": 0,
            "stdout": "UNCONN 0 0 100.112.32.42:50155 0.0.0.0:*",
            "stderr": "",
            "timed_out": False,
        }

    monkeypatch.setattr(
        "tools.phase_1575h_live_quorum_preflight.ssh_command",
        fake_ssh_command,
    )

    result = validator_endpoint_checks()

    assert result["open_quic_count"] == 4
    assert result["quorum_threshold"] == 3
    assert result["quorum_reachable"] is True
    assert all(record["quic"]["transport"] == "udp" for record in result["validators"])


def test_phase1575h_readiness_launcher_has_no_db_wipe_or_epoch_send() -> None:
    text = Path("tools/testbed/phase1575h_live_validator_quorum_readiness.sh").read_text(
        encoding="utf-8"
    )

    assert "rm -rf" not in text
    assert "send-epoch" not in text
    assert "epoch_checkpoint" not in text
    assert "mkdir -p '$db_path'" in text
    assert "validator_%s_1575h_readiness.pid" in text
    assert "start-clean --confirm-wipe" in text
    assert "phase1575h_start_clean_refused_without_confirm_wipe" in text
    assert "sha256sum" in text
    assert "db.tar.sha256" in text
    assert "db_moved" in text
