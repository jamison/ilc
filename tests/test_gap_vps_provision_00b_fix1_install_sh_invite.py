from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

import pytest

from ilc_core.cli import main as cli_main
from ilc_core.crypto.pq_signature_verify import _MLDSA_PK_HEX_LENGTH


ROOT = Path(__file__).resolve().parents[1]
INSTALL_SH = ROOT / "tools" / "install.sh"


def _run_install_sh(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(INSTALL_SH), *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )


def test_install_sh_dry_run_shows_invite_bundle_flag() -> None:
    result = _run_install_sh(
        "--channel",
        "rc",
        "--dry-run",
        "--invite-bundle",
        "/tmp/public-rc-invite.json",
    )
    assert result.returncode == 0
    assert "install_sh_dry_run" in result.stdout
    assert "invite_bundle=/tmp/public-rc-invite.json" in result.stdout


def test_install_sh_invite_bundle_not_found_exits_1(tmp_path: Path) -> None:
    result = _run_install_sh("--invite-bundle", str(tmp_path / "missing.json"))
    assert result.returncode == 1
    assert "install_sh_invite_bundle_not_found" in result.stderr


def test_install_sh_missing_invite_bundle_required() -> None:
    result = _run_install_sh("--dry-run")
    assert result.returncode == 2
    assert "install_sh_invite_bundle_required" in result.stderr


def test_install_sh_no_onboard_is_not_accepted_bypass() -> None:
    result = _run_install_sh("--dry-run", "--no-onboard")
    assert result.returncode == 2
    assert "install_sh_unknown_argument:--no-onboard" in result.stderr


def test_install_sh_runs_invite_onboard_after_hash_verification() -> None:
    text = INSTALL_SH.read_text(encoding="utf-8")
    hash_check = text.index('if [[ "${actual_hash}" != "${RC_WHEEL_SHA256}" ]]')
    onboard = text.index("install_sh_running_invite_onboard")
    assert hash_check < onboard
    assert "--from-invite" in text
    assert "--target-dir" in text
    assert 'INSTALL_SLICE_DIR="${HOME}/.ilc/installed_slices"' in text
    assert 'INSTALL_RECEIPT="${INSTALL_SLICE_DIR}/install_receipt.json"' in text


def test_identity_invite_bundle_can_attach_signed_bootstrap_material(
    tmp_path: Path,
) -> None:
    batch = cli_main._run_identity_invite_subcommand(
        argparse.Namespace(
            batch_id="batch-with-bootstrap-material",
            count=1,
            created_epoch=0,
            enable_invites=True,
            identity_invite_subcommand="create",
            inviter_cid="genesis_agent:01",
            inviter_sig="genesis",
            output="",
        )
    )["output"]
    batch_path = tmp_path / "batch.json"
    batch_path.write_text(
        json.dumps(batch, sort_keys=True, separators=(",", ":")),
        encoding="utf-8",
    )
    hints_path = tmp_path / "bootstrap_peer_hints.json"
    hints_path.write_text(
        json.dumps(
            {
                "known_peer_hint_key_bindings": {
                    "mldsa:key:relay-node-2": "a" * _MLDSA_PK_HEX_LENGTH
                },
                "known_peer_hints": [{"schema_version": "peer_advertisement.v0.1"}],
                "schema_version": "bootstrap_peer_hints.v0.1",
            },
            sort_keys=True,
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )

    result = cli_main._run_identity_invite_subcommand(
        argparse.Namespace(
            batch_json_path=str(batch_path),
            bootstrap_fetch_bundle_cid="bafybootstrap",
            bootstrap_fetch_genesis_authority_pubkey_hex="b" * _MLDSA_PK_HEX_LENGTH,
            bootstrap_fetch_seed_peer_endpoint="https://seed.ilc.example:443",
            enable_invites=True,
            genesis_state_root="sha256:" + ("c" * 64),
            identity_invite_subcommand="bundle",
            intended_epoch=0,
            intended_profile="public_rc_validator_bootstrap",
            inviter_connectivity_mode="relay_reachable",
            known_peer_hints_path=str(hints_path),
            nonce_index=0,
            output="",
            starmap_path="",
        )
    )["output"]

    assert result["genesis_state_root"] == "sha256:" + ("c" * 64)
    assert result["inviter_connectivity_mode"] == "relay_reachable"
    assert len(result["known_peer_hints"]) == 1
    assert result["known_peer_hint_key_bindings"] == {
        "mldsa:key:relay-node-2": "a" * _MLDSA_PK_HEX_LENGTH
    }
    assert result["bootstrap_fetch_bundle_cid"] == "bafybootstrap"
    assert result["bootstrap_fetch_seed_peer_endpoint"] == "https://seed.ilc.example:443"
    assert result["bootstrap_fetch_genesis_authority_pubkey_hex"] == (
        "b" * _MLDSA_PK_HEX_LENGTH
    )


def test_identity_invite_bundle_rejects_partial_bootstrap_fetch_material(
    tmp_path: Path,
) -> None:
    batch = cli_main._run_identity_invite_subcommand(
        argparse.Namespace(
            batch_id="batch-partial-bootstrap-fetch",
            count=1,
            created_epoch=0,
            enable_invites=True,
            identity_invite_subcommand="create",
            inviter_cid="genesis_agent:01",
            inviter_sig="genesis",
            output="",
        )
    )["output"]
    batch_path = tmp_path / "batch.json"
    batch_path.write_text(
        json.dumps(batch, sort_keys=True, separators=(",", ":")),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="invite_bundle_bootstrap_fetch_material_incomplete"):
        cli_main._run_identity_invite_subcommand(
            argparse.Namespace(
                batch_json_path=str(batch_path),
                bootstrap_fetch_bundle_cid="bafybootstrap",
                bootstrap_fetch_genesis_authority_pubkey_hex="",
                bootstrap_fetch_seed_peer_endpoint="",
                enable_invites=True,
                genesis_state_root="",
                identity_invite_subcommand="bundle",
                intended_epoch=0,
                intended_profile="public_rc_validator_bootstrap",
                inviter_connectivity_mode="",
                known_peer_hints_path="",
                nonce_index=0,
                output="",
                starmap_path="",
            )
        )


def test_identity_invite_bundle_rejects_oversized_known_peer_hints(
    tmp_path: Path,
) -> None:
    hints_path = tmp_path / "oversized_hints.json"
    hints_path.write_bytes(b"{" + (b'"x":' + b'"a"' * 600_000) + b"}")

    with pytest.raises(ValueError, match="invite_bundle_known_peer_hints_too_large"):
        cli_main._invite_bundle_optional_bootstrap_fields(
            argparse.Namespace(
                bootstrap_fetch_bundle_cid="",
                bootstrap_fetch_genesis_authority_pubkey_hex="",
                bootstrap_fetch_seed_peer_endpoint="",
                genesis_state_root="",
                inviter_connectivity_mode="",
                known_peer_hints_path=str(hints_path),
            )
        )


def test_identity_invite_bundle_rejects_too_many_known_peer_hints(
    tmp_path: Path,
) -> None:
    hints_path = tmp_path / "too_many_hints.json"
    hints_path.write_text(
        json.dumps(
            {
                "known_peer_hint_key_bindings": {},
                "known_peer_hints": [
                    {"schema_version": "peer_advertisement.v0.1"}
                    for _ in range(cli_main.INSTALL_KNOWN_PEER_HINTS_MAX_COUNT + 1)
                ],
                "schema_version": "bootstrap_peer_hints.v0.1",
            },
            sort_keys=True,
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="invite_bundle_known_peer_hints_too_many"):
        cli_main._invite_bundle_optional_bootstrap_fields(
            argparse.Namespace(
                bootstrap_fetch_bundle_cid="",
                bootstrap_fetch_genesis_authority_pubkey_hex="",
                bootstrap_fetch_seed_peer_endpoint="",
                genesis_state_root="",
                inviter_connectivity_mode="",
                known_peer_hints_path=str(hints_path),
            )
        )


def test_identity_invite_bundle_rejects_non_object_known_peer_hint(
    tmp_path: Path,
) -> None:
    hints_path = tmp_path / "bad_hint.json"
    hints_path.write_text(
        json.dumps(
            {
                "known_peer_hint_key_bindings": {},
                "known_peer_hints": ["not-an-object"],
                "schema_version": "bootstrap_peer_hints.v0.1",
            },
            sort_keys=True,
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="invite_bundle_known_peer_hint_invalid"):
        cli_main._invite_bundle_optional_bootstrap_fields(
            argparse.Namespace(
                bootstrap_fetch_bundle_cid="",
                bootstrap_fetch_genesis_authority_pubkey_hex="",
                bootstrap_fetch_seed_peer_endpoint="",
                genesis_state_root="",
                inviter_connectivity_mode="",
                known_peer_hints_path=str(hints_path),
            )
        )
