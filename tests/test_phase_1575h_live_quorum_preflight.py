from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from tools.phase_1575h_live_quorum_preflight import (
    atomic_write_json,
    bool_constant_from_file,
    build_evidence,
    quorum_threshold,
    status_token_checks,
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
