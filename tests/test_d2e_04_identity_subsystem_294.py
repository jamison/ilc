"""Phase 294 implementation tests for D2e-04 identity subsystem."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from ilc_core.genesis.invitation_provenance_record import (
    build_invite_batch_record,
    derive_invite_redemption_nullifier,
)
from ilc_core.genesis.invite_nullifier_lmdb_store import InviteNullifierLmdbRegistry
from ilc_core.testing.phase_commit_manifest import resolve_phase_commit_ref_or_skip


CLI_CMD = [sys.executable, "-m", "ilc_core.cli.main"]
DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"


def _run_cli(args: list[str], env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        CLI_CMD + args,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


def _json_payload(result: subprocess.CompletedProcess[str]) -> dict:
    blob = result.stdout.strip() or result.stderr.strip()
    assert blob, "expected_json_payload"
    return json.loads(blob)


def _seed_identity_state(path: Path, *, lineage_id: str, key_ref: str) -> None:
    path.write_text(
        json.dumps(
            {
                "key_ref": key_ref,
                "lineage_id": lineage_id,
                "rotation_count": 0,
                "status": "active",
                "updated_at": "1970-01-01T00:00:00Z",
            },
            sort_keys=True,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def test_identity_commands_return_json_envelopes(tmp_path: Path) -> None:
    env = os.environ.copy()
    env["ILC_CLI_GRAPH_STATE_PATH"] = str(tmp_path / "graph.json")
    env["ILC_IDENTITY_STATE_PATH"] = str(tmp_path / "identity.json")

    _seed_identity_state(tmp_path / "identity.json", lineage_id="lineage-a", key_ref="key-a")

    show_res = _run_cli(["identity", "show"], env)
    assert show_res.returncode == 0
    show_payload = _json_payload(show_res)
    assert show_payload["ok"] is True
    assert show_payload["data"]["action"] == "show"

    rotate_res = _run_cli(["identity", "rotate", "--new-key-ref", "key-b"], env)
    assert rotate_res.returncode == 0
    rotate_payload = _json_payload(rotate_res)
    assert rotate_payload["ok"] is True
    assert rotate_payload["data"]["action"] == "rotate"
    assert rotate_payload["data"]["state"]["key_ref"] == "key-b"

    export_res = _run_cli(["identity", "export"], env)
    assert export_res.returncode == 0
    export_payload = _json_payload(export_res)
    assert export_payload["ok"] is True
    assert export_payload["data"]["action"] == "export"


def test_error_conditions_return_contract_exit_codes(tmp_path: Path) -> None:
    env = os.environ.copy()
    env["ILC_CLI_GRAPH_STATE_PATH"] = str(tmp_path / "graph.json")
    env["ILC_IDENTITY_STATE_PATH"] = str(tmp_path / "identity.json")

    # Public enrollment is invite-gated; legacy identity init must not create state.
    init_res = _run_cli(["identity", "init"], env)
    assert init_res.returncode == 1
    init_payload = _json_payload(init_res)
    assert init_payload["ok"] is False
    assert "invite_required_for_enrollment" in init_payload["message"]
    assert not (tmp_path / "identity.json").exists()

    # Operational failure: show before init.
    show_res = _run_cli(["identity", "show"], env)
    assert show_res.returncode == 1
    show_payload = _json_payload(show_res)
    assert show_payload["ok"] is False
    assert show_payload["code"] == "1"
    assert "identity_not_initialized" in show_payload["message"]

    # Usage failure: unknown subcommand.
    bad_res = _run_cli(["identity", "bogus"], env)
    assert bad_res.returncode == 2
    bad_payload = _json_payload(bad_res)
    assert bad_payload["ok"] is False
    assert bad_payload["code"] == "2"


def test_behavior_is_deterministic_for_repeated_export(tmp_path: Path) -> None:
    env = os.environ.copy()
    env["ILC_CLI_GRAPH_STATE_PATH"] = str(tmp_path / "graph.json")
    env["ILC_IDENTITY_STATE_PATH"] = str(tmp_path / "identity.json")

    _seed_identity_state(tmp_path / "identity.json", lineage_id="lineage-d", key_ref="key-d")

    export_one = _json_payload(_run_cli(["identity", "export"], env))
    export_two = _json_payload(_run_cli(["identity", "export"], env))

    assert export_one["ok"] is True
    assert export_two["ok"] is True
    assert export_one["data"] == export_two["data"]


def test_legacy_identity_invite_builder_cannot_bypass_pop_or_consume_nullifier(
    tmp_path: Path,
) -> None:
    home = tmp_path / "home"
    home.mkdir()
    identity_path = tmp_path / "identity.json"
    invite_path = tmp_path / "invite.json"
    nonce = b"r3d-legacy-identity-invite".ljust(32, b"0")
    batch, private_nonces = build_invite_batch_record(
        inviter_cid="inviter-r3d",
        batch_id="r3d-legacy-identity",
        count=1,
        created_epoch=0,
        inviter_sig="structural-only",
        nonces=(nonce,),
    )
    invite_path.write_text(
        json.dumps(
            {
                "invite_batch_record": batch.to_dict(),
                "private_invite_nonces": list(private_nonces),
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    expected_nullifier = derive_invite_redemption_nullifier(batch.batch_id, nonce)
    env = os.environ.copy()
    env["HOME"] = str(home)
    env["ILC_CLI_GRAPH_STATE_PATH"] = str(tmp_path / "graph.json")
    env["ILC_IDENTITY_STATE_PATH"] = str(identity_path)

    result = _run_cli(
        [
            "identity",
            "init",
            "--invite",
            str(invite_path),
            "--enable-invites",
            "--identity-seed-hex",
            "11" * 32,
            "--redeemer-pubkey-cid",
            "fixture:redeemer-key",
        ],
        env,
    )

    assert result.returncode == 1
    assert "invite_redemption_redeemer_key_binding_required" in _json_payload(result)["message"]
    assert not identity_path.exists()
    with InviteNullifierLmdbRegistry(home / ".ilc" / "lmdb" / "nullifiers") as registry:
        assert registry.is_known(expected_nullifier) is False


def test_bare_identity_command_preserves_d2e03_compatibility(tmp_path: Path) -> None:
    env = os.environ.copy()
    env["ILC_CLI_GRAPH_STATE_PATH"] = str(tmp_path / "graph.json")
    env["ILC_IDENTITY_STATE_PATH"] = str(tmp_path / "identity.json")

    result = _run_cli(["identity"], env)
    assert result.returncode == 0
    payload = _json_payload(result)
    assert payload["ok"] is True
    assert payload["command"] == "identity"
    assert payload["data"]["mode"] == "prototype_compat"
    assert payload["data"]["lineage_id"] == "lineage-local"
    assert payload["data"]["export_ref"] == "identity-local"


def _resolve_phase_294_commit_ref() -> str:
    return resolve_phase_commit_ref_or_skip("phase_294")


def test_no_decision_log_file_changed_in_phase_commit() -> None:
    commit_ref = _resolve_phase_294_commit_ref()
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        check=True,
        capture_output=True,
        text=True,
    )
    changed = {line.strip() for line in result.stdout.splitlines() if line.strip()}
    assert DECISION_LOG_PATH not in changed
