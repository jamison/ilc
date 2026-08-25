from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
from pathlib import Path

import pytest
from py_ecc.optimized_bls12_381 import curve_order

import ilc_core
from ilc_core.identity import bls_backend
from ilc_core.identity.first_run_provisioning import (
    IdentityAlreadyExistsError,
    existing_identity_summary,
    identity_root,
    migrate_identity_schema_if_needed,
    provision_new_identity,
)
from ilc_core.identity.bls_backend import keypair_from_ikm_hex, sign_invite_pop_digest
from ilc_core.validator.validator_key_derivation import derive_validator_key_ikm


AGENT_ID_HEX = "a" * 96
SIGNING_KEY_HEX = "b" * 64
KNOWN_SEED = bytes.fromhex("01" * 32)


@pytest.fixture()
def fake_keygen(tmp_path: Path) -> list[str]:
    script = tmp_path / "fake_keygen.py"
    script.write_text(
        "\n".join(
            [
                "import pathlib, sys",
                "data = sys.stdin.read()",
                "if len(data.strip()) != 64:",
                "    raise SystemExit(3)",
                "out = pathlib.Path(sys.argv[sys.argv.index('--out') + 1])",
                f"out.write_text('{SIGNING_KEY_HEX}\\n', encoding='utf-8')",
                f"print('{AGENT_ID_HEX}')",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return [sys.executable, str(script)]


def _provision(tmp_path: Path, fake_keygen: list[str]) -> tuple[dict[str, str], Path]:
    receipt = provision_new_identity(
        tmp_path,
        invite_id="invite-test",
        epoch=0,
        keygen_command=fake_keygen,
        emit_warning=False,
    )
    return receipt, identity_root(tmp_path)


def test_provision_creates_required_files(
    tmp_path: Path, fake_keygen: list[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("secrets.token_bytes", lambda size: KNOWN_SEED)

    receipt, root = _provision(tmp_path, fake_keygen)

    assert receipt["agent_id"] == AGENT_ID_HEX
    assert (root / "agent_id").is_file()
    assert (root / "signing_key.hex").is_file()
    assert (root / "birth_attestation.json").is_file()
    assert (root / "recovery_policy.json").is_file()
    assert (root / "onboarding_receipt.json").is_file()


def test_onboarding_receipt_uses_package_version(
    tmp_path: Path, fake_keygen: list[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("secrets.token_bytes", lambda size: KNOWN_SEED)
    _, root = _provision(tmp_path, fake_keygen)

    receipt = json.loads((root / "onboarding_receipt.json").read_text(encoding="utf-8"))

    assert receipt["software_version"] == ilc_core.__version__


def test_default_backend_is_packageable_without_rust_command(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("ILC_ONBOARDING_BLS_KEYGEN_COMMAND", raising=False)
    monkeypatch.setattr("secrets.token_bytes", lambda size: KNOWN_SEED)
    expected_sk, expected_agent_id = keypair_from_ikm_hex(
        derive_validator_key_ikm(KNOWN_SEED).hex()
    )

    receipt = provision_new_identity(tmp_path, invite_id="invite-test", emit_warning=False)
    root = identity_root(tmp_path)

    assert receipt["agent_id"] == expected_agent_id
    assert (root / "agent_id").read_text(encoding="utf-8").strip() == expected_agent_id
    assert (root / "signing_key.hex").read_text(encoding="utf-8").strip() == expected_sk


def test_default_backend_rejects_all_zero_ikm() -> None:
    with pytest.raises(ValueError, match="onboarding_bls_ikm_must_not_be_all_zero"):
        keypair_from_ikm_hex("0" * 64)


def test_default_backend_uses_public_curve_order_not_private_py_ecc_api() -> None:
    assert "_is_valid_privkey" not in Path(bls_backend.__file__).read_text(encoding="utf-8")
    with pytest.raises(ValueError, match="onboarding_bls_private_key_invalid"):
        sign_invite_pop_digest(f"{curve_order:064x}", "a" * 96)


def test_signing_key_has_0600_permissions(
    tmp_path: Path, fake_keygen: list[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("secrets.token_bytes", lambda size: KNOWN_SEED)
    _, root = _provision(tmp_path, fake_keygen)

    mode = stat.S_IMODE((root / "signing_key.hex").stat().st_mode)

    assert mode == 0o600


def test_signing_key_not_in_receipt(
    tmp_path: Path, fake_keygen: list[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("secrets.token_bytes", lambda size: KNOWN_SEED)
    receipt, root = _provision(tmp_path, fake_keygen)
    receipt_json = json.loads((root / "onboarding_receipt.json").read_text())

    assert SIGNING_KEY_HEX not in json.dumps(receipt, sort_keys=True)
    assert SIGNING_KEY_HEX not in json.dumps(receipt_json, sort_keys=True)


def test_identity_seed_not_written_to_disk(
    tmp_path: Path, fake_keygen: list[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("secrets.token_bytes", lambda size: KNOWN_SEED)
    _, root = _provision(tmp_path, fake_keygen)
    seed_hex = KNOWN_SEED.hex()

    for path in root.iterdir():
        payload = path.read_bytes()
        assert KNOWN_SEED not in payload
        assert seed_hex.encode("ascii") not in payload


def test_agent_id_survives_restart(
    tmp_path: Path, fake_keygen: list[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("secrets.token_bytes", lambda size: KNOWN_SEED)
    _, root = _provision(tmp_path, fake_keygen)

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "from pathlib import Path; "
                "print((Path(__import__('sys').argv[1]) / 'agent_id').read_text().strip())"
            ),
            str(root),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert result.stdout.strip() == AGENT_ID_HEX


def test_second_install_does_not_overwrite_key(
    tmp_path: Path, fake_keygen: list[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("secrets.token_bytes", lambda size: KNOWN_SEED)
    _, root = _provision(tmp_path, fake_keygen)
    original = (root / "signing_key.hex").read_text(encoding="utf-8")

    with pytest.raises(IdentityAlreadyExistsError, match="identity_signing_key_already_exists"):
        provision_new_identity(tmp_path, keygen_command=fake_keygen, emit_warning=False)

    assert (root / "signing_key.hex").read_text(encoding="utf-8") == original


def test_recovery_policy_default_is_none(
    tmp_path: Path, fake_keygen: list[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("secrets.token_bytes", lambda size: KNOWN_SEED)
    _, root = _provision(tmp_path, fake_keygen)
    recovery = json.loads((root / "recovery_policy.json").read_text(encoding="utf-8"))

    assert recovery["type"] == "none"
    assert recovery["cdl_authority"] == "cdl-002-section-0a"
    assert recovery["credentials"] == []


def test_birth_attestation_has_no_secret_material(
    tmp_path: Path, fake_keygen: list[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("secrets.token_bytes", lambda size: KNOWN_SEED)
    _, root = _provision(tmp_path, fake_keygen)
    birth = (root / "birth_attestation.json").read_text(encoding="utf-8")

    assert SIGNING_KEY_HEX not in birth
    assert '"agent_id":"' + AGENT_ID_HEX + '"' in birth
    assert '"ceremony_mode":"agent_mode"' in birth


def test_existing_identity_summary_is_public_safe(
    tmp_path: Path, fake_keygen: list[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("secrets.token_bytes", lambda size: KNOWN_SEED)
    _, root = _provision(tmp_path, fake_keygen)

    summary = existing_identity_summary(tmp_path)

    assert summary["agent_id"] == AGENT_ID_HEX
    assert summary["status"] == "existing_identity_reused"
    assert SIGNING_KEY_HEX not in json.dumps(summary, sort_keys=True)
    assert (root / "signing_key.hex").read_text(encoding="utf-8").strip() == SIGNING_KEY_HEX


def test_update_migration_adds_missing_key_store_profile(
    tmp_path: Path, fake_keygen: list[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("secrets.token_bytes", lambda size: KNOWN_SEED)
    _, root = _provision(tmp_path, fake_keygen)
    birth_path = root / "birth_attestation.json"
    birth = json.loads(birth_path.read_text(encoding="utf-8"))
    birth.pop("key_store_profile")
    birth_path.write_text(json.dumps(birth, sort_keys=True, separators=(",", ":")) + "\n")

    migration = migrate_identity_schema_if_needed(tmp_path)
    updated = json.loads(birth_path.read_text(encoding="utf-8"))

    assert migration["migration_status"] == "updated"
    assert updated["key_store_profile"] == "file_0600_unencrypted"
    assert (root / "migration_receipt.json").is_file()


def test_missing_keygen_command_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("secrets.token_bytes", lambda size: KNOWN_SEED)

    with pytest.raises(ValueError, match="onboarding_bls_keygen_unavailable"):
        provision_new_identity(
            tmp_path,
            keygen_command=["/definitely/not/present/ilc-keygen"],
            emit_warning=False,
        )


def test_force_reprovision_requires_explicit_flag(
    tmp_path: Path, fake_keygen: list[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("secrets.token_bytes", lambda size: KNOWN_SEED)
    _, root = _provision(tmp_path, fake_keygen)
    (root / "agent_id").write_text("c" * 96 + "\n", encoding="utf-8")

    receipt = provision_new_identity(
        tmp_path,
        keygen_command=fake_keygen,
        force_reprovision=True,
        emit_warning=False,
    )

    assert receipt["agent_id"] == AGENT_ID_HEX
    assert (root / "agent_id").read_text(encoding="utf-8").strip() == AGENT_ID_HEX
    assert os.stat(root / "signing_key.hex").st_mode & 0o777 == 0o600


def test_force_reprovision_failure_preserves_existing_identity(
    tmp_path: Path, fake_keygen: list[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("secrets.token_bytes", lambda size: KNOWN_SEED)
    _, root = _provision(tmp_path, fake_keygen)
    original_agent_id = (root / "agent_id").read_text(encoding="utf-8")
    original_key = (root / "signing_key.hex").read_text(encoding="utf-8")

    with pytest.raises(ValueError, match="onboarding_bls_keygen_unavailable"):
        provision_new_identity(
            tmp_path,
            keygen_command=["/definitely/not/present/ilc-keygen"],
            force_reprovision=True,
            emit_warning=False,
        )

    assert (root / "agent_id").read_text(encoding="utf-8") == original_agent_id
    assert (root / "signing_key.hex").read_text(encoding="utf-8") == original_key
