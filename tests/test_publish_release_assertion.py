from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from ilc_core.release import upgrade_check
from tools import publish_release_assertion as tooling


FIXTURE_BLS_SECRET_HEX = "11" * 32
FIXTURE_RELEASE_SECRET_HEX = "22" * 32


def _payload(tmp_path: Path | None = None) -> dict:
    return tooling.build_release_assertion(
        version="0.4.33",
        artifact_sha256="aa" * 32,
        artifact_cid=None,
        artifact_size=1234,
        source_commit="b" * 40,
        channel="stable",
        release_date="2026-10-06T12:00:00Z",
        fixture_release_signing_key_hex=FIXTURE_RELEASE_SECRET_HEX,
        fixture_bls_signing_key_hex=FIXTURE_BLS_SECRET_HEX,
    )


def test_build_release_assertion_validates_with_upgrade_checker(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = _payload()
    release_pubkey = tooling._release_public_key_hex(FIXTURE_RELEASE_SECRET_HEX)
    monkeypatch.setattr(upgrade_check, "release_signer_public_key_hex", lambda: release_pubkey)

    result = upgrade_check.validate_release_assertion(payload)

    assert result["available_version"] == "0.4.33"
    assert result["release_signature_verified"] is True
    assert result["verified_attestation_count"] == 1
    assert result["graph_provenance_status"] == "verified_native_submit_sig_v0.1"
    assert result["graph_provenance_delegation_valid_at_submission"] is False


def test_native_envelope_uses_nested_fixture_sig_without_secret_material() -> None:
    payload = _payload()
    envelope = payload["native_submit_envelope"]

    assert envelope["primitive"] == "assert.truth"
    assert isinstance(envelope["sig"], dict)
    assert envelope["sig"]["schema_version"] == "native_submit_sig.v0.1"
    assert envelope["sig"]["key_ref"] == envelope["agent_id"]
    assert FIXTURE_BLS_SECRET_HEX not in json.dumps(payload, sort_keys=True)
    assert FIXTURE_RELEASE_SECRET_HEX not in json.dumps(payload, sort_keys=True)


def test_release_attestation_edge_carries_artifact_id_and_preimage() -> None:
    payload = _payload()
    edge = payload["release_attestation_edges"][0]

    assert edge["artifact_id"] == "ilc-artifact:ilc-core-python-wheel-0433@phase-1626"
    expected_preimage = tooling.compute_signed_preimage_sha256(
        release_id="ilc-core-0.4.33",
        artifact_id=edge["artifact_id"],
        artifact_sha256=edge["artifact_sha256"],
    )
    assert edge["signed_preimage_sha256"] == expected_preimage


def test_atomic_output_write_replaces_existing_file(tmp_path: Path) -> None:
    output = tmp_path / "release_assertion.json"
    output.write_text("stale\n", encoding="utf-8")
    payload = _payload()

    written = tooling._atomic_write_json(output, payload)

    assert written == output
    decoded = json.loads(output.read_text(encoding="utf-8"))
    assert decoded["software_release_node"]["version"] == "0.4.33"
    assert not list(tmp_path.glob(".release_assertion.json.*.tmp"))


def test_cli_requires_dry_run_and_writes_output(tmp_path: Path) -> None:
    output = tmp_path / "assertion.json"
    command = [
        sys.executable,
        "tools/publish_release_assertion.py",
        "--version",
        "0.4.33",
        "--artifact-sha256",
        "aa" * 32,
        "--artifact-size",
        "1234",
        "--source-commit",
        "b" * 40,
        "--release-date",
        "2026-10-06T12:00:00Z",
        "--fixture-signing-key-hex",
        FIXTURE_BLS_SECRET_HEX,
        "--fixture-release-signing-key-hex",
        FIXTURE_RELEASE_SECRET_HEX,
        "--output",
        str(output),
        "--dry-run",
    ]
    result = subprocess.run(command, check=True, capture_output=True, text=True)

    stdout_payload = json.loads(result.stdout)
    file_payload = json.loads(output.read_text(encoding="utf-8"))
    assert stdout_payload == file_payload
    assert "fixture_release_authority" not in stdout_payload
    assert "non_claims" not in stdout_payload


def test_cli_without_dry_run_rejects_live_publish() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "tools/publish_release_assertion.py",
            "--version",
            "0.4.33",
            "--artifact-sha256",
            "aa" * 32,
            "--artifact-size",
            "1234",
            "--source-commit",
            "b" * 40,
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert "live_publish_not_authorized_in_tooling_phase" in result.stdout


def test_tool_source_has_no_live_submit_or_real_key_path() -> None:
    source = Path("tools/publish_release_assertion.py").read_text(encoding="utf-8")
    forbidden = [
        "ilc_native_submit_client",
        "~/.ilc/identity/signing_key.hex",
        "genesis_public_submit_ingress_bls_sk",
    ]
    assert all(token not in source for token in forbidden)
    assert "subprocess" not in source
