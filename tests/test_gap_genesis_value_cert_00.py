# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import json
from pathlib import Path

import pytest

from ilc_core.epoch.genesis_settlement_destination import (
    GENESIS_WALLET_WRITE_AUTHORIZED,
    get_genesis_settlement_destination_record,
    verify_genesis_settlement_destination_record,
)
from ilc_core.genesis import load_and_verify_certificate
from ilc_core.genesis.genesis_value_action_guard import (
    GENESIS_VALUE_NETWORK_ID,
    GENESIS_VALUE_MAX_CERTIFICATE_JSON_BYTES,
    GenesisValueGuardError,
    enforce_genesis_value_guard,
)


CERT_PATH = Path("out/gap_genesis_value_cert_00/genesis_value_action_policy_certificate.json")
PUBKEYS_PATH = Path("out/gap_genesis_value_cert_00/guardian_pubkeys.json")
RECEIPT_PATH = Path("out/gap_genesis_value_cert_00/cert_issue_receipt.json")
RECIPIENT_AGENT_ID = "b" * 96


def _write_mutated_certificate(tmp_path: Path, **updates: object) -> Path:
    raw = json.loads(CERT_PATH.read_text(encoding="utf-8"))
    raw.update(updates)
    mutated = tmp_path / "mutated_certificate.json"
    mutated.write_text(json.dumps(raw, sort_keys=True, separators=(",", ":")), encoding="utf-8")
    return mutated


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
    mutated = _write_mutated_certificate(tmp_path, effective_epoch_end=5)

    try:
        load_and_verify_certificate(mutated)
    except GenesisValueGuardError as exc:
        assert exc.token == "genesis_value_certificate_window_too_long"
    else:
        raise AssertionError("mutated certificate unexpectedly verified")


def test_gap_genesis_value_guard_accepts_live_certificate_at_epoch_window_edges() -> None:
    cert = load_and_verify_certificate(CERT_PATH)

    for epoch in (cert.effective_epoch_start, cert.effective_epoch_end):
        enforce_genesis_value_guard(
            source_agent_id=cert.genesis_agent_id,
            certificate=cert,
            action_class="PAYMENT",
            amount_micro_unit=1,
            current_epoch=epoch,
            recipient_agent_id=RECIPIENT_AGENT_ID,
            graph_context_anchor="graph:gap-genesis-value-cert",
            consent_or_agreement_reference="agreement:gap-genesis-value-cert",
            unit="ILC",
            current_epoch_spent_micro_unit=0,
            network_id=cert.network_id,
        )


def test_gap_genesis_value_guard_rejects_live_certificate_outside_epoch_window() -> None:
    cert = load_and_verify_certificate(CERT_PATH)

    for epoch, token in (
        (cert.effective_epoch_start - 1, "genesis_value_certificate_not_yet_active"),
        (cert.effective_epoch_end + 1, "genesis_value_certificate_expired"),
    ):
        try:
            enforce_genesis_value_guard(
                source_agent_id=cert.genesis_agent_id,
                certificate=cert,
                action_class="PAYMENT",
                amount_micro_unit=1,
                current_epoch=epoch,
                recipient_agent_id=RECIPIENT_AGENT_ID,
                graph_context_anchor="graph:gap-genesis-value-cert",
                consent_or_agreement_reference="agreement:gap-genesis-value-cert",
                unit="ILC",
                current_epoch_spent_micro_unit=0,
                network_id=cert.network_id,
            )
        except GenesisValueGuardError as exc:
            assert exc.token == token
        else:
            raise AssertionError(f"certificate unexpectedly accepted at epoch {epoch}")


def test_gap_genesis_value_loader_rejects_non_string_action_class(tmp_path: Path) -> None:
    mutated = _write_mutated_certificate(tmp_path, allowed_action_classes=["PAYMENT", 7])

    with pytest.raises(
        GenesisValueGuardError,
        match="genesis_value_certificate_action_classes_invalid",
    ):
        load_and_verify_certificate(mutated)


def test_gap_genesis_value_loader_rejects_over_limit_without_stat_race(tmp_path: Path) -> None:
    oversized = tmp_path / "oversized_certificate.json"
    oversized.write_bytes(b"{" + (b" " * GENESIS_VALUE_MAX_CERTIFICATE_JSON_BYTES))

    with pytest.raises(
        GenesisValueGuardError,
        match="genesis_value_certificate_json_too_large",
    ):
        load_and_verify_certificate(oversized)


def test_gap_genesis_value_loader_rejects_corrupt_cose_signature(tmp_path: Path) -> None:
    raw = json.loads(CERT_PATH.read_text(encoding="utf-8"))
    signatures = raw["certificate_sig"]["signatures"]
    corrupted = dict(signatures[0])
    last = corrupted["cose_sign1_hex"][-2:]
    corrupted["cose_sign1_hex"] = corrupted["cose_sign1_hex"][:-2] + (
        "00" if last != "00" else "01"
    )
    signatures[0] = corrupted
    mutated = tmp_path / "corrupt_certificate.json"
    mutated.write_text(json.dumps(raw, sort_keys=True, separators=(",", ":")), encoding="utf-8")

    with pytest.raises(
        GenesisValueGuardError,
        match="genesis_value_certificate_signature_invalid",
    ):
        load_and_verify_certificate(mutated)
