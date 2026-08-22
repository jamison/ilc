from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from ilc_core.validator.validator_key_derivation import derive_validator_key_ikm
from tools import vps_validator_keygen_helper as helper


HELPER = Path("tools/vps_validator_keygen_helper.py")
RUST_KEYGEN = Path("ilc_consensus/src/keygen_main.rs")


def test_helper_is_public_rc_excluded_and_imports_canonical_derivation() -> None:
    text = HELPER.read_text(encoding="utf-8")

    assert "PUBLIC_RC_EXCLUDE" in text
    assert "derive_validator_key_ikm" in text
    assert "identity seed" in text


def test_helper_rejects_bad_identity_seed_hex() -> None:
    with pytest.raises(ValueError, match="identity_seed_hex_must_be_64_lowercase_hex"):
        helper.derive_agent_id_hex_from_identity_seed("A" * 64, keygen_command=["unused"])
    with pytest.raises(ValueError, match="identity_seed_hex_must_not_be_all_zero"):
        helper.derive_agent_id_hex_from_identity_seed("00" * 32, keygen_command=["unused"])


def test_helper_passes_derived_validator_ikm_to_rust_keygen(monkeypatch: pytest.MonkeyPatch) -> None:
    seed_hex = "01" * 32
    expected_ikm_hex = derive_validator_key_ikm(bytes.fromhex(seed_hex)).hex()
    calls: list[list[str]] = []
    inputs: list[object] = []

    def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append(command)
        inputs.append(kwargs.get("input"))
        return subprocess.CompletedProcess(command, 0, stdout="ab" * 48 + "\n", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    agent_id = helper.derive_agent_id_hex_from_identity_seed(
        seed_hex,
        keygen_command=["/tmp/keygen"],
    )

    assert agent_id == "ab" * 48
    assert calls == [["/tmp/keygen", "--pubkey-from-ikm-hex-stdin"]]
    assert inputs == [expected_ikm_hex]


def test_helper_rejects_bad_rust_keygen_output(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(command, 0, stdout="not-an-agent-id\n", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(RuntimeError, match="validator_keygen_output_invalid"):
        helper.derive_agent_id_hex_from_identity_seed("02" * 32, keygen_command=["/tmp/keygen"])


def test_helper_rejects_failed_rust_keygen(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(command, 1, stdout="", stderr="failed")

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(RuntimeError, match="validator_keygen_failed"):
        helper.derive_agent_id_hex_from_identity_seed("03" * 32, keygen_command=["/tmp/keygen"])


def test_rust_keygen_has_public_key_from_ikm_mode_without_printing_secret_key() -> None:
    text = RUST_KEYGEN.read_text(encoding="utf-8")

    assert "--pubkey-from-ikm-hex-stdin" in text
    assert "PubkeyFromIkmHexStdin" in text
    assert "PubkeyFromIkmHex(" not in text
    assert "public_key_from_ikm_hex" in text
    pubkey_branch = text.split("Mode::PubkeyFromIkmHexStdin", 1)[1].split(
        "// ---------------------------------------------------------------------------",
        1,
    )[0]
    assert "sk_hex" not in pubkey_branch
    assert "println!(\"{}\", pk_hex)" in pubkey_branch


def test_keypair_manifest_absent_until_operator_supplies_agent_ids() -> None:
    assert not Path(
        "docs/specs/ilc_cdl017_validator_keypair_manifest_GAP_VPS_PROVISION_00a_v0.1.json"
    ).exists()
