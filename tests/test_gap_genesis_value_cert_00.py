# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import json
from pathlib import Path

from ilc_core.epoch.genesis_settlement_destination import (
    GENESIS_WALLET_WRITE_AUTHORIZED,
    get_genesis_settlement_destination_record,
    verify_genesis_settlement_destination_record,
)
from ilc_core.genesis import load_and_verify_certificate
from ilc_core.genesis.genesis_value_action_guard import (
    GENESIS_VALUE_NETWORK_ID,
    GenesisValueGuardError,
)


CERT_PATH = Path("out/gap_genesis_value_cert_00/genesis_value_action_policy_certificate.json")
PUBKEYS_PATH = Path("out/gap_genesis_value_cert_00/guardian_pubkeys.json")
RECEIPT_PATH = Path("out/gap_genesis_value_cert_00/cert_issue_receipt.json")


def test_gap_genesis_value_cert_artifact_loads_and_verifies() -> None:
    cert = load_and_verify_certificate(CERT_PATH)

    assert cert.network_id == GENESIS_VALUE_NETWORK_ID
    assert cert.effective_epoch_start == 1
    assert cert.effective_epoch_end == 4
    assert cert.guardian_threshold == 2
    assert cert.guardian_key_count == 3


def test_gap_genesis_value_cert_sig_bundle_has_required_three_keys() -> None:
    raw = json.loads(CERT_PATH.read_text(encoding="utf-8"))

    assert sorted(raw["certificate_sig"]) == [
        "guardian_public_keys",
        "signatures",
        "threshold",
    ]
    assert len(raw["certificate_sig"]["guardian_public_keys"]) == 3
    assert len(raw["certificate_sig"]["signatures"]) == 2


def test_gap_genesis_value_guard_flip_and_destination_record_are_consistent() -> None:
    assert GENESIS_WALLET_WRITE_AUTHORIZED is True

    record = get_genesis_settlement_destination_record()
    assert record["genesis_wallet_write_authorized"] is True
    verify_genesis_settlement_destination_record(record)


def test_gap_genesis_value_public_key_root_matches_receipt() -> None:
    pubkeys = json.loads(PUBKEYS_PATH.read_text(encoding="utf-8"))
    receipt = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    cert = load_and_verify_certificate(CERT_PATH)

    assert pubkeys["guardian_public_key_root"] == cert.guardian_public_key_root
    assert receipt["guardian_public_key_root"] == cert.guardian_public_key_root
    assert receipt["certificate_id"] == cert.certificate_id
    assert receipt["verification_result"] == "pass"


def test_gap_genesis_value_outputs_do_not_contain_private_key_material() -> None:
    forbidden = (
        "/users/",
        "guardian_offrepo_custody_directory",
        "private_key",
        "secret_key",
        "sk_bytes",
        "ed25519privatekey",
    )

    for path in (CERT_PATH, PUBKEYS_PATH, RECEIPT_PATH):
        text = path.read_text(encoding="utf-8").lower()
        assert not any(token in text for token in forbidden)


def test_gap_genesis_value_loader_rejects_mutated_certificate(tmp_path: Path) -> None:
    raw = json.loads(CERT_PATH.read_text(encoding="utf-8"))
    raw["effective_epoch_end"] = 5
    mutated = tmp_path / "mutated_certificate.json"
    mutated.write_text(json.dumps(raw), encoding="utf-8")

    try:
        load_and_verify_certificate(mutated)
    except GenesisValueGuardError as exc:
        assert exc.token == "genesis_value_certificate_window_too_long"
    else:
        raise AssertionError("mutated certificate unexpectedly verified")
