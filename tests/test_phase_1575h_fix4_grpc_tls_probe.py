from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from tools.testbed import phase1575h_testbed_grpc_tls_probe as probe


def _ca_cert(tmp_path: Path) -> Path:
    path = tmp_path / "ca.cert.pem"
    path.write_bytes(b"-----BEGIN CERTIFICATE-----\nphase1575h\n-----END CERTIFICATE-----\n")
    return path


def test_probe_records_all_validator_epochs(
    monkeypatch,
    tmp_path: Path,
) -> None:
    configs: list[object] = []

    class StubAdapter:
        def __init__(self, config: object) -> None:
            configs.append(config)

        def get_epoch(self) -> int:
            return 1

    monkeypatch.setattr(probe, "ILCConsensusGrpcReadAdapter", StubAdapter)
    args = probe.parse_args(
        [
            "--ca-cert",
            str(_ca_cert(tmp_path)),
            "--validators",
            "127.0.0.1:50161",
            "127.0.0.1:50162",
            "--expect-epoch",
            "1",
        ]
    )

    evidence = probe.build_evidence(args)

    assert evidence["probe_passed"] is True
    assert [record["status"] for record in evidence["validators"]] == ["ok", "ok"]
    assert configs[0].tls_root_certificates == args.ca_cert.read_bytes()
    assert evidence["activation_boundary"]["read_only_probe"] is True
    assert evidence["activation_boundary"]["sent_epoch_checkpoint"] is False


def test_probe_fails_on_epoch_mismatch(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        probe,
        "ILCConsensusGrpcReadAdapter",
        lambda _config: SimpleNamespace(get_epoch=lambda: 2),
    )
    args = probe.parse_args(
        [
            "--ca-cert",
            str(_ca_cert(tmp_path)),
            "--validators",
            "127.0.0.1:50161",
            "--expect-epoch",
            "0",
        ]
    )

    evidence = probe.build_evidence(args)

    assert evidence["probe_passed"] is False
    assert evidence["validators"][0]["status"] == "epoch_mismatch"
