from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import lmdb
import pytest
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
)

from ilc_core.consensus.attribution_audit_lmdb import AttributionAuditLmdbStore
from tools.testbed import attribution_readback, ecu_transfer_submit, ilc_transfer_submit


SENDER = "a" * 96
RECIPIENT = "b" * 96
ANCHOR = "node:gap-harness-sidecar-06:anchor"


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


def test_public_rc_exclude_headers_and_no_taboo_imports() -> None:
    for path in [
        Path("tools/testbed/ilc_transfer_submit.py"),
        Path("tools/testbed/ecu_transfer_submit.py"),
        Path("tools/testbed/attribution_readback.py"),
    ]:
        text = path.read_text(encoding="utf-8")
        assert "PUBLIC_RC_EXCLUDE: phase_soak_tool" in text
        assert "subprocess" not in text
        assert "requests" not in text
        assert "urllib.request" not in text
        assert "socket" not in text


def test_ilc_transfer_dry_run_does_not_consume_nonce(tmp_path: Path) -> None:
    key_path = _write_key(tmp_path / "sender.pem")
    lmdb_path = tmp_path / "ilc.lmdb"
    result = ilc_transfer_submit.submit_ilc_transfer(
        lmdb_path=lmdb_path,
        sender_agent_id=SENDER,
        recipient_agent_id=RECIPIENT,
        amount_ilc=ilc_transfer_submit._parse_decimal("1.000000", "bad"),
        epoch=1,
        signing_key_path=key_path,
        dry_run=True,
        graph_context_anchor=ANCHOR,
    )
    assert result["mode"] == "dry_run"
    assert result["signature_verified"] is True
    env = lmdb.open(str(lmdb_path), max_dbs=16)
    try:
        store = ilc_transfer_submit.ActionNonceStore(env)
        assert store.peek_counter(SENDER) == 0
    finally:
        env.close()


def test_ilc_transfer_submit_records_double_entry(tmp_path: Path) -> None:
    key_path = _write_key(tmp_path / "sender.pem")
    result = ilc_transfer_submit.submit_ilc_transfer(
        lmdb_path=tmp_path / "ilc.lmdb",
        sender_agent_id=SENDER,
        recipient_agent_id=RECIPIENT,
        amount_ilc=ilc_transfer_submit._parse_decimal("1.250000", "bad"),
        epoch=2,
        signing_key_path=key_path,
        test_seed_balance_ilc=ilc_transfer_submit._parse_decimal("5.000000", "bad"),
        graph_context_anchor=ANCHOR,
    )
    assert result["mode"] == "submitted"
    assert result["sender_balance_after_ilc"] == "3.75"
    assert result["recipient_balance_after_ilc"] == "1.25"
    assert isinstance(result["record"], dict)
    assert len(result["record"]["transfer_id"]) == 64


def test_ilc_transfer_failed_submit_does_not_wedge_nonce_store(tmp_path: Path) -> None:
    key_path = _write_key(tmp_path / "sender.pem")
    lmdb_path = tmp_path / "ilc.lmdb"
    with pytest.raises(ilc_transfer_submit.InsufficientBalanceError):
        ilc_transfer_submit.submit_ilc_transfer(
            lmdb_path=lmdb_path,
            sender_agent_id=SENDER,
            recipient_agent_id=RECIPIENT,
            amount_ilc=ilc_transfer_submit._parse_decimal("1.000000", "bad"),
            epoch=2,
            signing_key_path=key_path,
        )
    result = ilc_transfer_submit.submit_ilc_transfer(
        lmdb_path=lmdb_path,
        sender_agent_id=SENDER,
        recipient_agent_id=RECIPIENT,
        amount_ilc=ilc_transfer_submit._parse_decimal("1.000000", "bad"),
        epoch=2,
        signing_key_path=key_path,
        test_seed_balance_ilc=ilc_transfer_submit._parse_decimal("2.000000", "bad"),
    )
    assert result["mode"] == "submitted"
    assert result["record"]["nonce"].endswith(":nonce:00000000000000000001")


def test_ilc_transfer_rejects_separate_nonce_store(tmp_path: Path) -> None:
    key_path = _write_key(tmp_path / "sender.pem")
    with pytest.raises(ValueError, match="nonce_store_must_share_lmdb_path"):
        ilc_transfer_submit.submit_ilc_transfer(
            lmdb_path=tmp_path / "ilc.lmdb",
            nonce_store_path=tmp_path / "nonce.lmdb",
            sender_agent_id=SENDER,
            recipient_agent_id=RECIPIENT,
            amount_ilc=ilc_transfer_submit._parse_decimal("1", "bad"),
            epoch=1,
            signing_key_path=key_path,
        )


def test_ecu_transfer_submit_validates_local_rust_payload() -> None:
    result = ecu_transfer_submit.submit_ecu_transfer(
        sender_agent_id=SENDER,
        recipient_agent_id=RECIPIENT,
        amount_ecu=ecu_transfer_submit._parse_decimal("0.500000", "bad"),
        transfer_class=ecu_transfer_submit.parse_transfer_class("peer_reward"),
        graph_context_anchor=ANCHOR,
        express_consent=None,
        nonce="nonce-001",
        created_epoch=3,
    )
    assert result["mode"] == "payload_validated"
    assert result["bridge_payload"]["amount_micro_ecu"] == 500000
    assert result["rust_payload"]["transfer_class"] == "Contribution"
    assert str(result["transfer_reference"]).startswith("local-ecu-transfer:")


def test_ecu_transfer_rejects_unsupported_staking_adjustment() -> None:
    with pytest.raises(ValueError, match="unsupported_ecu_transfer_class"):
        ecu_transfer_submit.parse_transfer_class("staking_adjustment")


def test_attribution_readback_reads_lmdb_credit_entries(tmp_path: Path) -> None:
    store = AttributionAuditLmdbStore(tmp_path / "attr.lmdb")
    try:
        store.write_epoch_events(
            7,
            [
                {
                    "credit_amount": "0.25",
                    "event_id": "event-1",
                    "recipient_agent_id": RECIPIENT,
                }
            ],
        )
    finally:
        store.env.close()
    result = attribution_readback.read_attribution_events(
        epoch=7,
        lmdb_path=tmp_path / "attr.lmdb",
        fallback_dir=None,
        require_credit_entries=True,
    )
    assert result["source"] == "lmdb"
    assert result["has_credit_entries"] is True
    assert result["credit_entry_count"] == 1


def test_attribution_readback_fallback_handles_zero_events(tmp_path: Path) -> None:
    fallback = tmp_path / "events"
    fallback.mkdir()
    result = attribution_readback.read_attribution_events(
        epoch=9,
        lmdb_path=tmp_path / "missing.lmdb",
        fallback_dir=fallback,
        require_credit_entries=False,
    )
    assert result["source"] == "fallback_dir"
    assert result["event_count"] == 0
    assert result["has_credit_entries"] is False


def test_cli_help_works_for_all_three_tools() -> None:
    for path in [
        "tools/testbed/ilc_transfer_submit.py",
        "tools/testbed/ecu_transfer_submit.py",
        "tools/testbed/attribution_readback.py",
    ]:
        completed = subprocess.run(
            [sys.executable, path, "--help"],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        assert completed.returncode == 0
        assert "usage:" in completed.stdout


def test_transfer_tools_expose_genesis_certificate_wiring() -> None:
    ilc_source = Path("tools/testbed/ilc_transfer_submit.py").read_text(encoding="utf-8")
    ecu_source = Path("tools/testbed/ecu_transfer_submit.py").read_text(encoding="utf-8")

    assert "--genesis-value-certificate-path" in ilc_source
    assert "load_and_verify_certificate(genesis_value_certificate_path)" in ilc_source
    assert "ILCTransferLedger(env, genesis_value_certificate=genesis_value_certificate)" in ilc_source
    assert "--genesis-value-certificate-path" in ecu_source
    assert "--genesis-epoch-spent-micro-ecu" in ecu_source
    assert '"genesis_value_certificate": genesis_value_certificate' in ecu_source


def test_ecu_cli_outputs_json(tmp_path: Path) -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "tools/testbed/ecu_transfer_submit.py",
            "--sender-agent-id",
            SENDER,
            "--recipient-agent-id",
            RECIPIENT,
            "--amount-ecu",
            "0.500000",
            "--transfer-class",
            "peer_reward",
            "--graph-context-anchor",
            ANCHOR,
            "--nonce",
            "nonce-002",
            "--epoch",
            "4",
        ],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert completed.returncode == 0
    payload = json.loads(completed.stdout)
    assert payload["ok"] is True
    assert payload["rust_payload"]["amount_micro_ecu"] == 500000
