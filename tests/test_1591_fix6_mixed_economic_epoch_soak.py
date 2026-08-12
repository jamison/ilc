from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
)

from tools.testbed.mixed_economic_epoch_soak import (
    _parse_decimal,
    run_mixed_epoch_soak,
)


SENDER = "c" * 96
RECIPIENT = "d" * 96


def _write_key(path: Path) -> Path:
    key = ed25519.Ed25519PrivateKey.generate()
    path.write_bytes(
        key.private_bytes(
            Encoding.PEM,
            PrivateFormat.PKCS8,
            NoEncryption(),
        )
    )
    path.chmod(0o600)
    return path


def _claims(path: Path) -> Path:
    path.write_text(json.dumps({"events": []}, sort_keys=True), encoding="utf-8")
    return path


def test_local_stub_runs_three_epoch_mixed_soak(tmp_path: Path) -> None:
    report = run_mixed_epoch_soak(
        epochs=3,
        lmdb_path=tmp_path / "runtime",
        signing_key_path=_write_key(tmp_path / "sender.pem"),
        sender_agent_id=SENDER,
        recipient_agent_id=RECIPIENT,
        transfer_amount_ilc=_parse_decimal("1.000000", "bad"),
        ecu_amount=_parse_decimal("0.500000", "bad"),
        attribution_claims_path=_claims(tmp_path / "claims.json"),
        validator_endpoints=[],
        dry_run=False,
    )
    assert report["verdict"] == "pass"
    assert report["epochs_completed"] == 3
    assert report["final_epoch_counter"] == 3
    assert all(item["roll"]["mode"] == "local_stub_counter" for item in report["per_epoch"])
    assert all(
        item["attribution_readback"]["has_credit_entries"] is True
        for item in report["per_epoch"]
    )


def test_dry_run_skips_epoch_roll(tmp_path: Path) -> None:
    report = run_mixed_epoch_soak(
        epochs=2,
        lmdb_path=tmp_path / "runtime",
        signing_key_path=_write_key(tmp_path / "sender.pem"),
        sender_agent_id=SENDER,
        recipient_agent_id=RECIPIENT,
        transfer_amount_ilc=_parse_decimal("1.000000", "bad"),
        ecu_amount=_parse_decimal("0.500000", "bad"),
        attribution_claims_path=_claims(tmp_path / "claims.json"),
        validator_endpoints=[],
        dry_run=True,
    )
    assert report["epochs_completed"] == 2
    assert report["final_epoch_counter"] == 0
    assert all(item["roll"]["rolled"] is False for item in report["per_epoch"])


def test_testnet_min_epoch_requires_validator_endpoints(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="testnet_min_epoch_ms_requires_validator_endpoints"):
        run_mixed_epoch_soak(
            epochs=1,
            lmdb_path=tmp_path / "runtime",
            signing_key_path=_write_key(tmp_path / "sender.pem"),
            sender_agent_id=SENDER,
            recipient_agent_id=RECIPIENT,
            transfer_amount_ilc=_parse_decimal("1.000000", "bad"),
            ecu_amount=_parse_decimal("0.500000", "bad"),
            attribution_claims_path=_claims(tmp_path / "claims.json"),
            validator_endpoints=[],
            testnet_min_epoch_ms=1000,
        )


def test_live_endpoints_do_not_silently_fallback_to_stub(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="live_epoch_roll_requires_explicit_phase1575h_runner"):
        run_mixed_epoch_soak(
            epochs=1,
            lmdb_path=tmp_path / "runtime",
            signing_key_path=_write_key(tmp_path / "sender.pem"),
            sender_agent_id=SENDER,
            recipient_agent_id=RECIPIENT,
            transfer_amount_ilc=_parse_decimal("1.000000", "bad"),
            ecu_amount=_parse_decimal("0.500000", "bad"),
            attribution_claims_path=_claims(tmp_path / "claims.json"),
            validator_endpoints=["127.0.0.1:50165"],
            dry_run=False,
        )


def test_cli_help_works() -> None:
    completed = subprocess.run(
        [sys.executable, "tools/testbed/mixed_economic_epoch_soak.py", "--help"],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert completed.returncode == 0
    assert "usage:" in completed.stdout


def test_cli_writes_output_path(tmp_path: Path) -> None:
    output = tmp_path / "report.json"
    completed = subprocess.run(
        [
            sys.executable,
            "tools/testbed/mixed_economic_epoch_soak.py",
            "--epochs",
            "1",
            "--lmdb-path",
            str(tmp_path / "runtime"),
            "--signing-key-path",
            str(_write_key(tmp_path / "sender.pem")),
            "--sender-agent-id",
            SENDER,
            "--recipient-agent-id",
            RECIPIENT,
            "--transfer-amount-ilc",
            "1.000000",
            "--ecu-amount",
            "0.500000",
            "--attribution-claims-path",
            str(_claims(tmp_path / "claims.json")),
            "--output-path",
            str(output),
        ],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert completed.returncode == 0
    assert output.exists()
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["verdict"] == "pass"
