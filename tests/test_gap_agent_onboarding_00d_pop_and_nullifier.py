# SPDX-License-Identifier: AGPL-3.0-only
"""GAP-AGENT-ONBOARDING-00d PoP and durable nullifier tests."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from ilc_core.cli import main as cli_main
from ilc_core.genesis import invite_enforcement
from ilc_core.genesis.invite_nullifier_lmdb_store import InviteNullifierLmdbRegistry
from ilc_core.identity.first_run_provisioning import (
    POP_DOMAIN,
    generate_invite_pop,
    identity_root,
    provision_new_identity,
    verify_invite_pop,
)
from ilc_core.sidecars.openclaw_invite_bootstrap import (
    build_synthetic_invite_bundle,
    derive_redemption_nullifier,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_MANIFEST = ROOT / "tests/fixtures/starmap/core_public_rc_slice_fixture.json"
INVITE_ID = "invite-gap-agent-onboarding-00d"
PROFILE = "openclaw_public_rc_bootstrap"
NONCE_HEX = "44" * 32


@pytest.fixture(scope="session")
def bls_bins() -> dict[str, str]:
    cargo = shutil.which("cargo") or str(Path.home() / ".cargo" / "bin" / "cargo")
    if not Path(cargo).exists():
        pytest.skip("cargo unavailable for BLS PoP test binaries")
    subprocess.run(
        [
            cargo,
            "build",
            "--quiet",
            "--manifest-path",
            str(ROOT / "ilc_consensus/Cargo.toml"),
            "--bin",
            "keygen",
            "--bin",
            "invite_pop_bls",
        ],
        check=True,
        cwd=ROOT,
    )
    return {
        "keygen": str(ROOT / "ilc_consensus/target/debug/keygen"),
        "pop": str(ROOT / "ilc_consensus/target/debug/invite_pop_bls"),
    }


def _bundle(*, batch_id: str = "batch-gap-agent-onboarding-00d") -> dict[str, object]:
    bundle = build_synthetic_invite_bundle(
        batch_id=batch_id,
        nonce_hex=NONCE_HEX,
        intended_profile=PROFILE,
        intended_epoch=0,
    )
    bundle["invite_id"] = INVITE_ID
    bundle["atlas_slice_manifest_witness"] = {"slice_id": "test-slice"}
    bundle["starmap_manifest_payload"] = json.loads(FIXTURE_MANIFEST.read_text(encoding="utf-8"))
    return bundle


def _write_bundle(path: Path, payload: dict[str, object]) -> Path:
    path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return path


def _args(invite: Path, target: Path, receipt: Path) -> argparse.Namespace:
    return argparse.Namespace(
        force_reprovision=False,
        from_invite=str(invite),
        output_receipt=str(receipt),
        target_dir=str(target),
    )


@pytest.fixture()
def install_env(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    bls_bins: dict[str, str],
) -> Path:
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setattr(Path, "home", lambda: home)
    monkeypatch.setenv("ILC_ONBOARDING_BLS_KEYGEN_COMMAND", bls_bins["keygen"])
    monkeypatch.setenv("ILC_ONBOARDING_BLS_POP_COMMAND", bls_bins["pop"])

    import ilc_core.bundle.atlas_slice_verifier as verifier

    monkeypatch.setattr(
        verifier,
        "verify_portable_manifest_witness",
        lambda witness: {"verified": True, "slice_id": witness["slice_id"]},
    )
    return home


def test_pop_signature_is_valid(tmp_path: Path, bls_bins: dict[str, str]) -> None:
    provision_new_identity(
        tmp_path,
        invite_id=INVITE_ID,
        keygen_command=[bls_bins["keygen"]],
        emit_warning=False,
    )
    root = identity_root(tmp_path)
    agent_id = (root / "agent_id").read_text(encoding="utf-8").strip()
    nullifier = derive_redemption_nullifier("batch-pop-valid", NONCE_HEX)

    invite_pop = generate_invite_pop(
        agent_id,
        nullifier,
        root / "signing_key.hex",
        invite_id=INVITE_ID,
        epoch=0,
        pop_command=[bls_bins["pop"]],
    )

    assert verify_invite_pop(
        agent_id_hex=agent_id,
        invite_nullifier=nullifier,
        invite_id=INVITE_ID,
        epoch=0,
        invite_pop=invite_pop,
        pop_command=[bls_bins["pop"]],
    )
    assert not verify_invite_pop(
        agent_id_hex=agent_id,
        invite_nullifier=derive_redemption_nullifier("batch-pop-wrong", NONCE_HEX),
        invite_id=INVITE_ID,
        epoch=0,
        invite_pop=invite_pop,
        pop_command=[bls_bins["pop"]],
    )


def test_pop_domain_separator_is_distinct() -> None:
    assert POP_DOMAIN == "ilc-invite-pop-v1"
    assert POP_DOMAIN not in {
        "ilc-agent-id-v1",
        "ilc-validator-key-v1",
        "ilc-invite-nullifier-v1",
        "ILC_AGENT_TRANSFER_V1",
    }


def test_nullifier_persists_across_restart(
    tmp_path: Path,
    install_env: Path,
) -> None:
    invite_path = _write_bundle(tmp_path / "invite.json", _bundle())
    result = cli_main._run_install_subcommand(
        _args(invite_path, tmp_path / "target", tmp_path / "install_receipt.json")
    )
    nullifier = result["invite_verification"]["redemption_nullifier"]

    with InviteNullifierLmdbRegistry(install_env / ".ilc/lmdb/nullifiers") as restarted:
        assert restarted.is_known(str(nullifier))


def test_duplicate_nullifier_rejected(
    tmp_path: Path,
    install_env: Path,
) -> None:
    invite_path = _write_bundle(tmp_path / "invite.json", _bundle())
    cli_main._run_install_subcommand(
        _args(invite_path, tmp_path / "target-a", tmp_path / "install_receipt_a.json")
    )

    with pytest.raises(ValueError, match="invite_verification_failed:invite_nullifier_already_seen"):
        cli_main._run_install_subcommand(
            _args(invite_path, tmp_path / "target-b", tmp_path / "install_receipt_b.json")
        )


def test_enforcement_gate_still_false_after_this_phase(
    tmp_path: Path,
    install_env: Path,
) -> None:
    invite_path = _write_bundle(tmp_path / "invite.json", _bundle(batch_id="batch-guard-false"))
    result = cli_main._run_install_subcommand(
        _args(invite_path, tmp_path / "target", tmp_path / "install_receipt.json")
    )

    assert invite_enforcement.INVITE_ENFORCEMENT_ENABLED is False
    invite_enforcement.require_invite_for_enrollment(
        result["identity_provisioning"]["agent_id"],
        result["invite_redemption_record"],
    )


def test_pop_not_in_signing_key_position(
    tmp_path: Path,
    install_env: Path,
) -> None:
    invite_path = _write_bundle(tmp_path / "invite.json", _bundle(batch_id="batch-pop-distinct"))
    cli_main._run_install_subcommand(
        _args(invite_path, tmp_path / "target", tmp_path / "install_receipt.json")
    )
    root = identity_root(install_env)
    receipt = json.loads((root / "onboarding_receipt.json").read_text(encoding="utf-8"))
    signing_key = (root / "signing_key.hex").read_text(encoding="utf-8").strip()

    assert receipt["invite_pop"] != signing_key
    assert len(receipt["invite_pop"]) == 192
    assert len(signing_key) == 64


def test_transferred_invite_replay_rejected(
    tmp_path: Path,
    install_env: Path,
) -> None:
    invite_path = _write_bundle(tmp_path / "invite.json", _bundle(batch_id="batch-transfer"))
    cli_main._run_install_subcommand(
        _args(invite_path, tmp_path / "target-a", tmp_path / "install_receipt_a.json")
    )
    shutil.rmtree(identity_root(install_env))

    with pytest.raises(ValueError, match="invite_verification_failed:invite_nullifier_already_seen"):
        cli_main._run_install_subcommand(
            _args(invite_path, tmp_path / "target-b", tmp_path / "install_receipt_b.json")
        )
