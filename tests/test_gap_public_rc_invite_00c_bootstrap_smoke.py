# SPDX-License-Identifier: AGPL-3.0-only
"""Public-RC invite bootstrap smoke tests."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pytest

import ilc_core
from ilc_core.cli import main as cli_main
from ilc_core.genesis import invite_enforcement
from ilc_core.genesis.invitation_provenance_record import (
    build_invite_batch_record,
    build_invite_redemption_record,
    derive_agent_id_from_identity_seed,
)
from ilc_core.genesis.invite_nullifier_lmdb_store import InviteNullifierLmdbRegistry
from ilc_core.sidecars.openclaw_invite_bootstrap import build_synthetic_invite_bundle


ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "docs/phases/STATUS.md"
EVIDENCE = ROOT / "out/gap_public_rc_invite_00c/smoke_evidence.json"
FIXTURE_MANIFEST = ROOT / "tests/fixtures/starmap/core_public_rc_slice_fixture.json"
IDENTITY_SEED_HEX = "99" * 32
REDEEMER_AGENT_ID = derive_agent_id_from_identity_seed(IDENTITY_SEED_HEX)
OUTPUT_TOKEN = "invite_bootstrap_smoke_pass_GAP_PUBLIC_RC_INVITE_00c"


def _redemption(nonce_byte: str = "ab") -> tuple[dict[str, object], str]:
    nonce = bytes.fromhex(nonce_byte * 32)
    batch, private_nonces = build_invite_batch_record(
        inviter_cid="genesis_agent:01",
        batch_id=f"public-rc-00c-smoke-{nonce_byte}",
        count=1,
        created_epoch=0,
        inviter_sig="synthetic-smoke-signature",
        nonces=(nonce,),
    )
    redemption = build_invite_redemption_record(
        batch=batch,
        nonce=private_nonces[0],
        nonce_membership_proof=(),
        redeemer_pubkey_cid="pubkey:redeemer-smoke",
        identity_seed=IDENTITY_SEED_HEX,
        redemption_epoch=0,
    )
    return redemption.to_dict(), str(redemption.redemption_nullifier)


def _install_bundle(nonce_hex: str = "22" * 32) -> dict[str, object]:
    bundle = build_synthetic_invite_bundle(
        batch_id="public-rc-00c-shortcode-smoke",
        nonce_hex=nonce_hex,
        intended_profile="openclaw_public_rc_bootstrap",
        intended_epoch=0,
    )
    bundle["atlas_slice_manifest_witness"] = {"slice_id": "test-slice"}
    bundle["starmap_manifest_payload"] = json.loads(
        FIXTURE_MANIFEST.read_text(encoding="utf-8")
    )
    return bundle


def _install_args(code: str, target: Path, receipt: Path) -> argparse.Namespace:
    return argparse.Namespace(
        enable_upnp=False,
        force_reprovision=False,
        from_invite="",
        invite_code=code,
        output_receipt=str(receipt),
        probe_observer=[],
        relay_admission_material="",
        relay_internal_port=7101,
        relay_network_id="public-rc",
        relay_tls_cert_der_sha256="",
        relay_url="",
        target_dir=str(target),
    )


def _install_fake_bls_helpers(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    keygen = tmp_path / "fake_keygen.py"
    keygen.write_text(
        "\n".join(
            [
                "import pathlib, sys",
                "out = pathlib.Path(sys.argv[sys.argv.index('--out') + 1])",
                "out.write_text('344dc8b38c3d76ded943ea518dfcd0184c8730f1d1a9a444e0bdd6ecc9742825\\n', encoding='utf-8')",
                "print('8e5a712e4cb2c51893c27ae19afb3455f3efcc66030dc25e13eb1afc2edf397317a0bb2d28a55513a32d7dcc404be3ba')",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    invite_pop = tmp_path / "fake_invite_pop.py"
    invite_pop.write_text(
        "\n".join(
            [
                "import sys",
                "sys.stdin.read()",
                "if sys.argv[1] == 'verify':",
                "    print('invite_pop_bls_valid')",
                "else:",
                "    print('" + ("c" * 192) + "')",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("ILC_ONBOARDING_BLS_KEYGEN_COMMAND", f"{sys.executable} {keygen}")
    monkeypatch.setenv("ILC_ONBOARDING_BLS_POP_COMMAND", f"{sys.executable} {invite_pop}")


def test_enforcement_is_active_for_smoke() -> None:
    assert invite_enforcement.INVITE_ENFORCEMENT_ENABLED is True


def test_first_redemption_accepted_lmdb(tmp_path: Path) -> None:
    redemption, nullifier = _redemption("ac")
    with InviteNullifierLmdbRegistry(tmp_path / "nullifiers") as registry:
        invite_enforcement.require_invite_for_enrollment(
            REDEEMER_AGENT_ID,
            redemption,
            nullifier_registry=registry,
            register_nullifier=True,
            require_redeemer_key_binding=False,
        )
        assert registry.is_known(nullifier)


def test_replay_rejected_after_lmdb_reopen(tmp_path: Path) -> None:
    redemption, _nullifier = _redemption("ad")
    store = tmp_path / "nullifiers"
    with InviteNullifierLmdbRegistry(store) as registry:
        invite_enforcement.require_invite_for_enrollment(
            REDEEMER_AGENT_ID,
            redemption,
            nullifier_registry=registry,
            register_nullifier=True,
            require_redeemer_key_binding=False,
        )

    with InviteNullifierLmdbRegistry(store) as restarted:
        with pytest.raises(ValueError, match="invite_nullifier_already_used"):
            invite_enforcement.require_invite_for_enrollment(
                REDEEMER_AGENT_ID,
                redemption,
                nullifier_registry=restarted,
                register_nullifier=True,
                require_redeemer_key_binding=False,
            )


def test_shortcode_path_registers_nullifier_durably(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import ilc_core.bundle.atlas_slice_verifier as verifier

    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setattr(Path, "home", lambda: home)
    monkeypatch.setattr(
        verifier,
        "verify_portable_manifest_witness",
        lambda witness: {"verified": True, "slice_id": witness["slice_id"]},
    )
    _install_fake_bls_helpers(tmp_path, monkeypatch)
    monkeypatch.setattr(
        cli_main,
        "_fetch_invite_bundle_by_shortcode",
        lambda code: _install_bundle() if code == "ILC-H7K2-X9P4" else {},
    )

    first = cli_main._run_install_subcommand(
        _install_args("ilch7k2x9p4", tmp_path / "target1", tmp_path / "receipt1.json")
    )
    assert first["status"] == "ok"
    assert first["invite_verification"]["enrollment_nullifier_status"] == "recorded"

    with pytest.raises(ValueError, match="invite_verification_failed:invite_nullifier_already_seen"):
        cli_main._run_install_subcommand(
            _install_args("ILC-H7K2-X9P4", tmp_path / "target2", tmp_path / "receipt2.json")
        )


def test_smoke_evidence_exists_and_all_pass() -> None:
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert evidence["package_version_confirmed"] == "0.4.19"
    assert evidence["invite_enforcement_enabled"] is True
    assert set(evidence["scenarios"]) == {
        "issue_test_batch",
        "redeem_invite_lmdb",
        "replay_rejected_after_restart",
        "shortcode_path_nullifier_durable",
    }
    assert all(value == "PASS" for value in evidence["scenarios"].values())


def test_package_version_is_0419() -> None:
    assert ilc_core.__version__ == "0.4.19"


def test_output_token_in_status() -> None:
    status = STATUS.read_text(encoding="utf-8")
    assert f"**Output token:** `{OUTPUT_TOKEN}`" in status
