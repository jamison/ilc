from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from ilc_core.ccss.runtime import (
    CCSSRuntimeError,
    build_allow_reply_message,
    generate_identity,
    seal_message,
    unseal_message,
)


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "ilc_core.cli.main", *args],
        capture_output=True,
        check=False,
        text=True,
    )


def _payload(result: subprocess.CompletedProcess[str]) -> dict:
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_sidecar_recipe_namespace_lists_confidential_contact() -> None:
    result = _run_cli("sidecar", "recipe", "list")
    payload = _payload(result)
    recipes = payload["data"]["recipes"]
    assert payload["command"] == "sidecar"
    assert recipes == [
        {
            "alias_commands": ["ilc ccss"],
            "recipe_id": "confidential-contact",
            "status": "available_local_bootstrap",
        }
    ]


def test_sidecar_recipe_inspect_declares_ccss_modules() -> None:
    result = _run_cli("sidecar", "recipe", "inspect", "confidential-contact")
    payload = _payload(result)
    modules = payload["data"]["recipe"]["modules"]
    assert "confidential_coordination_private_gated_shard" in modules
    assert "confidential_coordination_capability_membership_boundary" in modules
    assert "confidential_coordination_sealed_sender_local_delivery" in modules
    assert "confidential_coordination_gossip_jitter_cover_policy" in modules


def test_ccss_apply_recipe_creates_identity_and_placeholder_genesis_contact(tmp_path: Path) -> None:
    result = _run_cli("ccss", "apply-recipe", "--home", str(tmp_path))
    payload = _payload(result)
    assert payload["command"] == "ccss"
    assert payload["data"]["identity_created"] is True
    assert "genesis_contact_contains_placeholders" in payload["data"]["warnings"][0]
    assert (tmp_path / "identity.json").exists()
    assert (tmp_path / "contacts.json").exists()

    contacts = _payload(_run_cli("ccss", "contacts", "--home", str(tmp_path)))
    genesis = contacts["data"]["contacts"][0]
    assert genesis["id"] == "genesis"
    assert genesis["configured"] is False
    assert genesis["transports"] == []


def test_ccss_send_to_placeholder_genesis_fails_closed(tmp_path: Path) -> None:
    _payload(_run_cli("ccss", "apply-recipe", "--home", str(tmp_path)))
    result = _run_cli("ccss", "send", "--home", str(tmp_path), "genesis", "hello")
    assert result.returncode == 1
    payload = json.loads(result.stderr)
    assert payload["command"] == "ccss"
    assert "contact_pubkey_not_configured:genesis" in payload["message"]


def test_packaged_ccss_identity_can_unseal_envelope(tmp_path: Path) -> None:
    generate_identity(home=tmp_path, contact_id="recipient", name="Recipient")
    identity = json.loads((tmp_path / "identity.json").read_text(encoding="utf-8"))
    envelope = seal_message("hello packaged ccss", identity["ccss_recipient_pubkey"])
    opened = unseal_message(envelope, home=tmp_path)
    assert opened["message"] == "hello packaged ccss"
    assert opened["message_bytes"] == len("hello packaged ccss".encode("utf-8"))


def test_allow_reply_uses_local_identity_endpoint(tmp_path: Path) -> None:
    generate_identity(
        home=tmp_path,
        contact_id="sender",
        name="Sender",
        peer_endpoint="100.111.172.103:9001",
    )

    payload = json.loads(build_allow_reply_message("hello", home=tmp_path))

    assert payload["msg"] == "hello"
    assert payload["reply_to"]["endpoint"] == "100.111.172.103:9001"
    assert payload["reply_to"]["name"] == "Sender"
    assert len(payload["reply_to"]["pubkey"]) == 64


def test_allow_reply_fails_without_local_reply_endpoint(tmp_path: Path) -> None:
    generate_identity(home=tmp_path, contact_id="sender", name="Sender")

    with pytest.raises(CCSSRuntimeError, match="identity_reply_endpoint_not_configured"):
        build_allow_reply_message("hello", home=tmp_path)


def test_apply_recipe_updates_existing_identity_reply_endpoint(tmp_path: Path) -> None:
    _payload(_run_cli("ccss", "apply-recipe", "--home", str(tmp_path)))

    result = _run_cli(
        "ccss",
        "apply-recipe",
        "--home",
        str(tmp_path),
        "--peer-endpoint",
        "100.111.172.103:9001",
    )
    payload = _payload(result)
    identity = json.loads((tmp_path / "identity.json").read_text(encoding="utf-8"))

    assert payload["data"]["identity_created"] is False
    assert payload["data"]["identity_reply_route_updated"] is True
    assert "local_ccss_reply_route_updated" in payload["data"]["steps"]
    assert identity["ccss_peer_endpoint"] == "100.111.172.103:9001"


def test_main_py_registers_sidecar_and_ccss_operational_commands() -> None:
    from ilc_core.cli.main import OPERATIONAL_COMMANDS

    assert "sidecar" in OPERATIONAL_COMMANDS
    assert "ccss" in OPERATIONAL_COMMANDS
