from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import pytest

from ilc_core.cli import main as cli_main
from ilc_core.identity.first_run_provisioning import validate_invite_bootstrap_capsule_fields
from ilc_core.network.d2d.gossip_peer_registry import GossipPeerRegistry

BOOTSTRAP_PEER_HINTS_SCHEMA_VERSION = "bootstrap_peer_hints.v0.1"


def _args(
    output: Path,
    *,
    relay_url: str = "https://127.0.0.1:51151",
    peer_epoch: int | bool = 0,
    ttl_epochs: int | bool = 4,
    protocol_version: str = "ilc.v0.4",
    label: str = "bootstrap-hint",
    enable_invites: bool = True,
) -> argparse.Namespace:
    return argparse.Namespace(
        enable_invites=enable_invites,
        identity_invite_subcommand="hint",
        label=label,
        output=str(output),
        peer_epoch=peer_epoch,
        protocol_version=protocol_version,
        relay_url=relay_url,
        ttl_epochs=ttl_epochs,
    )


def test_identity_invite_hint_round_trips_through_gossip_registry(tmp_path: Path) -> None:
    output = tmp_path / "bootstrap_peer_hints.json"

    result = cli_main._run_identity_invite_subcommand(_args(output))

    assert result["action"] == "peer_hint_created"
    assert result["output_path"] == str(output)
    assert len(result["agent_id"]) == 96
    assert len(result["mldsa_pubkey_hex"]) == 3904
    registry = GossipPeerRegistry([], allow_private_address_literals=True)
    assert registry.load_bootstrap_hints(output, current_epoch=0) == 1


def test_identity_invite_hint_rejects_http_relay_url(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="peer_hint_relay_url_must_be_https"):
        cli_main._run_identity_invite_subcommand(
            _args(tmp_path / "bootstrap_peer_hints.json", relay_url="http://127.0.0.1:51151")
        )


def test_identity_invite_hint_writes_bootstrap_peer_hints_schema(tmp_path: Path) -> None:
    output = tmp_path / "bootstrap_peer_hints.json"

    cli_main._run_identity_invite_subcommand(_args(output))
    payload = json.loads(output.read_text(encoding="utf-8"))

    assert payload["schema_version"] == BOOTSTRAP_PEER_HINTS_SCHEMA_VERSION
    assert len(payload["known_peer_hints"]) == 1
    assert len(payload["known_peer_hint_key_bindings"]) == 1
    serialized = json.dumps(payload, sort_keys=True)
    assert "private" not in serialized.lower()
    assert "secret" not in serialized.lower()


def test_identity_invite_hint_output_validates_after_invite_bundle_assembly(
    tmp_path: Path,
) -> None:
    hints_path = tmp_path / "bootstrap_peer_hints.json"
    cli_main._run_identity_invite_subcommand(
        _args(hints_path, relay_url="https://164.90.201.11:51151")
    )
    batch = cli_main._run_identity_invite_subcommand(
        argparse.Namespace(
            batch_id="batch-with-generated-peer-hint",
            count=1,
            created_epoch=0,
            enable_invites=True,
            identity_invite_subcommand="create",
            inviter_cid="genesis_agent:01",
            inviter_sig="genesis",
            output="",
        )
    )["output"]
    batch_path = tmp_path / "invite_batch.json"
    batch_path.write_text(
        json.dumps(batch, sort_keys=True, separators=(",", ":"), ensure_ascii=True),
        encoding="utf-8",
    )

    bundle = cli_main._run_identity_invite_subcommand(
        argparse.Namespace(
            batch_json_path=str(batch_path),
            bootstrap_fetch_bundle_cid="",
            bootstrap_fetch_genesis_authority_pubkey_hex="",
            bootstrap_fetch_seed_peer_endpoint="",
            enable_invites=True,
            genesis_state_root="",
            identity_invite_subcommand="bundle",
            intended_epoch=0,
            intended_profile="public_rc_validator_bootstrap",
            inviter_connectivity_mode="",
            known_peer_hints_path=str(hints_path),
            nonce_index=0,
            output="",
            relay_bootstrap_capsule_path="",
            starmap_path="",
        )
    )["output"]
    evidence = validate_invite_bootstrap_capsule_fields(bundle, current_epoch=0)

    assert evidence["known_peer_hints_offered"] == 1
    assert evidence["known_peer_hints_verified"] == 1


def test_identity_invite_hint_console_script_can_build_valid_bundle(tmp_path: Path) -> None:
    ilc_exe = Path(sys.executable).with_name("ilc")
    if not ilc_exe.exists():
        pytest.skip("ilc console script unavailable in this test environment")
    hints_path = tmp_path / "bootstrap_peer_hints.json"
    batch_path = tmp_path / "invite_batch.json"
    bundle_path = tmp_path / "invite_bundle.json"

    subprocess.run(
        [
            str(ilc_exe),
            "identity",
            "invite",
            "hint",
            "--relay-url",
            "https://164.90.201.11:51151",
            "--output",
            str(hints_path),
            "--enable-invites",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        [
            str(ilc_exe),
            "identity",
            "invite",
            "create",
            "--count",
            "1",
            "--output",
            str(batch_path),
            "--enable-invites",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        [
            str(ilc_exe),
            "identity",
            "invite",
            "bundle",
            str(batch_path),
            "--nonce-index",
            "0",
            "--known-peer-hints-path",
            str(hints_path),
            "--output",
            str(bundle_path),
            "--enable-invites",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    evidence = validate_invite_bootstrap_capsule_fields(bundle, current_epoch=0)
    assert evidence["known_peer_hints_verified"] == 1


def test_identity_invite_hint_requires_enable_invites(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="invite_cli_not_enabled_use_enable_invites"):
        cli_main._run_identity_invite_subcommand(
            _args(tmp_path / "bootstrap_peer_hints.json", enable_invites=False)
        )


@pytest.mark.parametrize(
    ("field", "value", "error"),
    [
        ("peer_epoch", True, "peer_hint_peer_epoch_invalid"),
        ("peer_epoch", -1, "peer_hint_peer_epoch_invalid"),
        ("ttl_epochs", False, "peer_hint_ttl_epochs_out_of_range"),
        ("ttl_epochs", 0, "peer_hint_ttl_epochs_out_of_range"),
        ("ttl_epochs", 5, "peer_hint_ttl_epochs_out_of_range"),
        ("protocol_version", "ilc v0.4", "peer_hint_protocol_version_invalid"),
        ("label", "bad label", "peer_hint_label_invalid"),
    ],
)
def test_identity_invite_hint_rejects_malformed_args(
    tmp_path: Path,
    field: str,
    value: object,
    error: str,
) -> None:
    kwargs = {field: value}
    with pytest.raises(ValueError, match=error):
        cli_main._run_identity_invite_subcommand(
            _args(tmp_path / "bootstrap_peer_hints.json", **kwargs)  # type: ignore[arg-type]
        )


def test_identity_invite_hint_help_lists_required_flags() -> None:
    result = subprocess.run(
        [".venv/bin/ilc", "identity", "invite", "hint", "--help"],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0
    for flag in (
        "--relay-url",
        "--output",
        "--peer-epoch",
        "--ttl-epochs",
        "--protocol-version",
        "--label",
        "--enable-invites",
    ):
        assert flag in result.stdout
