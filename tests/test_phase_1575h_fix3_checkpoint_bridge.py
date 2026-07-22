from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from tools.testbed import phase1575h_economic_checkpoint_send as checkpoint_send
from tools.testbed import phase1575h_economic_soak_setup as soak_setup

VALID_ROOT = "01711220" + "01" * 32


class _StubAdapter:
    def __init__(self, current_epoch: int = 0, *, found: bool = True) -> None:
        self.current_epoch = current_epoch
        self.found = found

    def get_epoch(self) -> int:
        return self.current_epoch

    def get_epoch_record(self, epoch: int) -> SimpleNamespace:
        return SimpleNamespace(
            agg_sig=b"x" * 96,
            epoch=epoch,
            found=self.found,
            state_root=bytes.fromhex(VALID_ROOT),
        )


def _checkpoint_args(**overrides: object) -> argparse.Namespace:
    values: dict[str, object] = {
        "ca_cert": None,
        "cert": Path("cert.pem"),
        "client_binary": Path("testnet_client"),
        "execute": False,
        "grpc_target": "127.0.0.1:50165",
        "grpc_timeout_seconds": 5,
        "key": Path("key.pem"),
        "output": Path("out.json"),
        "peer_cert": Path("peer.der"),
        "peer_id": 5,
        "quorum_keys": Path("keys.csv"),
        "state_root_cidv1_hex": VALID_ROOT,
        "timeout_seconds": 10,
        "validator": "127.0.0.1:50155",
        "validators": "1@127.0.0.1:50155",
        "epoch": 1,
    }
    values.update(overrides)
    return argparse.Namespace(**values)


def test_checkpoint_command_includes_state_root() -> None:
    command = checkpoint_send.build_testnet_client_command(_checkpoint_args())

    assert "--state-root" in command
    assert command[command.index("--state-root") + 1] == VALID_ROOT
    assert "--msg" in command
    assert command[command.index("--msg") + 1] == "epoch_checkpoint"


def test_checkpoint_send_aborts_non_monotonic_epoch(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        checkpoint_send,
        "ILCConsensusGrpcReadAdapter",
        lambda _config: _StubAdapter(current_epoch=1),
    )

    with pytest.raises(ValueError, match="epoch_not_monotonic"):
        checkpoint_send.build_evidence(_checkpoint_args(epoch=1))


def test_checkpoint_send_dry_run_does_not_execute(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        checkpoint_send,
        "ILCConsensusGrpcReadAdapter",
        lambda _config: _StubAdapter(current_epoch=0),
    )

    evidence = checkpoint_send.build_evidence(_checkpoint_args())

    assert evidence["activation_boundary"]["sent_epoch_checkpoint"] is False
    assert evidence["grpc_tls"]["ca_cert_supplied"] is False
    assert evidence["send_result"] is None
    assert evidence["record_check"] is None


def test_checkpoint_send_wires_ca_cert_into_bridge_config(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    ca_cert = tmp_path / "ca.cert.pem"
    ca_cert.write_bytes(b"-----BEGIN CERTIFICATE-----\nphase1575h\n-----END CERTIFICATE-----\n")
    configs: list[object] = []

    def fake_adapter(config: object) -> _StubAdapter:
        configs.append(config)
        return _StubAdapter(current_epoch=0)

    monkeypatch.setattr(checkpoint_send, "ILCConsensusGrpcReadAdapter", fake_adapter)

    evidence = checkpoint_send.build_evidence(_checkpoint_args(ca_cert=ca_cert))

    assert evidence["grpc_tls"]["ca_cert_supplied"] is True
    assert evidence["grpc_tls"]["ca_cert_path"] == str(ca_cert)
    assert configs[0].tls_root_certificates == ca_cert.read_bytes()


def test_checkpoint_send_rejects_missing_ca_cert() -> None:
    with pytest.raises(FileNotFoundError, match="testbed_ca_cert_not_found"):
        checkpoint_send.load_testbed_ca_cert(Path("does-not-exist.cert.pem"))


def test_checkpoint_send_execute_verifies_committed_record(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        checkpoint_send,
        "ILCConsensusGrpcReadAdapter",
        lambda _config: _StubAdapter(current_epoch=0),
    )
    monkeypatch.setattr(
        checkpoint_send,
        "run_command",
        lambda _command, *, timeout_seconds: {"returncode": 0, "stdout": "", "stderr": ""},
    )

    evidence = checkpoint_send.build_evidence(_checkpoint_args(execute=True))

    assert evidence["activation_boundary"]["sent_epoch_checkpoint"] is True
    assert evidence["record_check"]["passed"] is True


def test_checkpoint_send_command_output_is_bounded() -> None:
    result = checkpoint_send.run_command(
        [
            sys.executable,
            "-c",
            "import sys; sys.stdout.write('x' * 70000); sys.stderr.write('y' * 70000)",
        ],
        timeout_seconds=5,
    )

    assert result["returncode"] == 0
    assert len(result["stdout"]) == checkpoint_send.MAX_COMMAND_OUTPUT_BYTES
    assert len(result["stderr"]) == checkpoint_send.MAX_COMMAND_OUTPUT_BYTES
    assert result["stdout_truncated"] is True
    assert result["stderr_truncated"] is True


def test_soak_setup_records_are_deterministic_across_two_runs() -> None:
    args = soak_setup.parse_args(["--epoch-count", "2"])
    first = soak_setup.build_evidence(args)
    second = soak_setup.build_evidence(args)

    assert [record["state_root_cidv1_hex"] for record in first["records"]] == [
        record["state_root_cidv1_hex"] for record in second["records"]
    ]
    assert [record["economic_settlement_root_sha256"] for record in first["records"]] == [
        record["economic_settlement_root_sha256"] for record in second["records"]
    ]
    assert first["activation_boundary"]["sent_epoch_checkpoint"] is False


def test_soak_setup_atomic_write(tmp_path: Path) -> None:
    output = tmp_path / "evidence.json"
    soak_setup.atomic_write_json(output, {"b": 2, "a": 1})

    assert json.loads(output.read_text(encoding="utf-8")) == {"a": 1, "b": 2}
    assert oct(output.stat().st_mode & 0o777) == "0o600"


def test_rust_testnet_client_requires_state_root_and_rejects_zero_source_contract() -> None:
    text = Path("ilc_consensus/src/testnet_client_main.rs").read_text(encoding="utf-8")

    assert "--state-root is required for --msg epoch_checkpoint" in text
    assert "--state-root is required for --msg epoch_settlement" in text
    assert "--count must be 1 for --msg epoch_checkpoint with --state-root" in text
    assert "--count must be 1 for --msg epoch_settlement with --state-root" in text
    assert "--state-root must not be all zeros" in text
    assert "--state-root must be CIDv1 dag-cbor sha2-256 bytes" in text
    assert "CIDv1Root::new([0u8; 36])" not in text


def test_legacy_phase1360_requires_explicit_non_synthetic_state_root() -> None:
    text = Path("tools/testbed/phase1360_multiop_control.sh").read_text(encoding="utf-8")

    assert 'PHASE1360_TESTNET_STATE_ROOT_CIDV1_HEX:-' in text
    assert "phase1360_state_root_required" in text
    assert "phase1360_legacy_synthetic_state_root_rejected" in text
    assert "^01711220[0-9a-f]{64}$" in text
    assert "--state-root \"$testnet_state_root_cidv1_hex\"" in text
