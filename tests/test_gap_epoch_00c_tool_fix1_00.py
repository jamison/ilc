from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.testbed.phase1591_fix6_public_epoch_roll import assert_consistent_initial_state
from tools.testbed.gap_epoch_00c_epoch_advance import (
    EXPECTED_AGENT_IDS,
    GENESIS_SHA256,
    VALIDATORS,
    build_checkpoint_argv,
    epoch_1_state_root,
    validate_testnet_client_bin,
    verify_quorum_keys,
)


ROOT = Path(__file__).resolve().parents[1]


def _epoch0_state(*, genesis_sha256: str = GENESIS_SHA256) -> dict[str, object]:
    return {
        "chain_complete": False,
        "epoch_chain": [],
        "genesis_sha256": genesis_sha256,
        "sentinel_consistent": True,
        "sentinel_current_epoch": 0,
        "verdict": "workload_d_replayability_fail_no_epochs_found",
    }


def test_epoch_zero_initial_state_accepted() -> None:
    assert (
        assert_consistent_initial_state([_epoch0_state() for _ in range(4)], allow_epoch_zero=True)
        == (0, "")
    )


def test_epoch_zero_initial_state_rejected_without_flag() -> None:
    with pytest.raises(ValueError, match="phase1591_fix6_public_initial_epoch_invalid"):
        assert_consistent_initial_state([_epoch0_state() for _ in range(4)])


def test_epoch_zero_mixed_genesis_sha256_rejected() -> None:
    states = [_epoch0_state() for _ in range(3)] + [_epoch0_state(genesis_sha256="b" * 64)]
    with pytest.raises(ValueError, match="phase1591_fix6_public_genesis_sha256_mismatch"):
        assert_consistent_initial_state(states, allow_epoch_zero=True)


def test_epoch_zero_non_empty_chain_rejected() -> None:
    state = _epoch0_state()
    state["epoch_chain"] = [{"epoch": 0, "state_root_hex": "01711220" + "a" * 64}]
    with pytest.raises(ValueError, match="phase1591_fix6_public_epoch0_chain_not_empty"):
        assert_consistent_initial_state([_epoch0_state(), _epoch0_state(), _epoch0_state(), state], allow_epoch_zero=True)


def test_epoch_zero_wrong_verdict_rejected() -> None:
    state = _epoch0_state()
    state["verdict"] = "workload_d_replayability_pass"
    with pytest.raises(ValueError, match="phase1591_fix6_public_epoch0_verdict_unexpected"):
        assert_consistent_initial_state([_epoch0_state(), _epoch0_state(), _epoch0_state(), state], allow_epoch_zero=True)


def test_epoch_1_state_root_deterministic() -> None:
    root_a = epoch_1_state_root()
    root_b = epoch_1_state_root()
    assert root_a == root_b
    assert len(root_a) == 72
    assert root_a.startswith("01711220")
    assert root_a.islower()


def test_key_dir_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="gap_epoch_00c_missing_quorum_key:validator_1"):
        verify_quorum_keys(tmp_path)


def test_expected_agent_id_constants_match_reprovision_receipt() -> None:
    receipt = json.loads(
        (ROOT / "out/gap_vps_validator_reprovision_00/reprovision_receipt.json").read_text(
            encoding="utf-8"
        )
    )
    actual = {
        int(slot["slot"].split("_", 1)[1]): slot["agent_id_new"]
        for slot in receipt["slots"]
    }
    assert actual == EXPECTED_AGENT_IDS


def test_testnet_client_bin_validation_rejects_non_absolute() -> None:
    with pytest.raises(ValueError, match="gap_epoch_00c_testnet_client_path_not_absolute"):
        validate_testnet_client_bin(Path("ilc_consensus/target/release/testnet_client"))


def test_existing_tool_soak_path_unaffected() -> None:
    root = "01711220" + "a" * 64
    states = [
        {
            "chain_complete": True,
            "epoch_chain": [{"epoch": 5, "state_root_hex": root}],
            "sentinel_consistent": True,
            "sentinel_current_epoch": 5,
            "verdict": "workload_d_replayability_pass",
        }
        for _ in range(4)
    ]
    assert assert_consistent_initial_state(states) == (5, root)


def test_build_checkpoint_argv_uses_absolute_tooling_and_current_key_dir(tmp_path: Path) -> None:
    client = tmp_path / "testnet_client"
    client.write_text("#!/bin/sh\n", encoding="utf-8")
    client.chmod(0o700)
    key_dir = tmp_path / "keys"
    key_dir.mkdir()
    cert_dir = tmp_path / "certs"
    cert_dir.mkdir()
    for slot in EXPECTED_AGENT_IDS:
        (key_dir / f"validator_{slot}_signing_key.hex").write_text("0" * 64, encoding="utf-8")
        for suffix in ("cert.pem", "key.pem", "cert.der"):
            (cert_dir / f"validator_{slot}_{suffix}").write_text("placeholder", encoding="utf-8")
    argv = build_checkpoint_argv(
        testnet_client_bin=client,
        key_dir=key_dir,
        cert_dir=cert_dir,
        endpoint=VALIDATORS[0],
        epoch=1,
        state_root=epoch_1_state_root(),
    )
    assert argv[0] == str(client)
    assert "--validator" in argv
    assert "164.90.201.11:7101" in argv
    quorum_keys = argv[argv.index("--quorum-keys") + 1]
    assert str(key_dir / "validator_1_signing_key.hex") in quorum_keys
    assert str(cert_dir / "validator_2_cert.pem") in argv
    assert str(cert_dir / "validator_1_cert.der") in argv
