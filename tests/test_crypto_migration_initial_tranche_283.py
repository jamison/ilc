from __future__ import annotations

import json
import subprocess
from pathlib import Path

from ilc_core.ledger.canon_bundle_key_registry_channel_signing import (
    sign_channel_file,
    verify_channel_file_signature,
)


DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"


def _make_channel_file(tmp_path: Path) -> Path:
    channel_file = tmp_path / "channel.json"
    data = {
        "channel_version": "v0.3",
        "updated_at": "2026-02-07T12:00:00Z",
        "current_channel": "main",
        "channels": ["main"],
        "sources": {"main": ["https://example.com"]},
    }
    channel_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return channel_file


def _resolve_phase_283_commit_ref() -> str:
    return "HEAD"


def test_verify_fails_on_key_fingerprint_mismatch(tmp_path: Path) -> None:
    channel_file = _make_channel_file(tmp_path)
    key = b"phase-283-signing-key"
    sign_channel_file(channel_file, key)

    sig_path = channel_file.with_suffix(channel_file.suffix + ".sig")
    sig_data = json.loads(sig_path.read_text(encoding="utf-8"))
    sig_data["key_fingerprint"] = "f" * 64
    sig_path.write_text(json.dumps(sig_data, indent=2, sort_keys=True), encoding="utf-8")

    result = verify_channel_file_signature(channel_file, key)
    assert result["ok"] is False
    assert "channel_signature_fingerprint_mismatch" in result["errors"]


def test_verify_accepts_legacy_sidecar_without_key_fingerprint(tmp_path: Path) -> None:
    channel_file = _make_channel_file(tmp_path)
    key = b"phase-283-signing-key"
    sign_channel_file(channel_file, key)

    sig_path = channel_file.with_suffix(channel_file.suffix + ".sig")
    sig_data = json.loads(sig_path.read_text(encoding="utf-8"))
    sig_data.pop("key_fingerprint", None)
    sig_path.write_text(json.dumps(sig_data, indent=2, sort_keys=True), encoding="utf-8")

    result = verify_channel_file_signature(channel_file, key)
    assert result["ok"] is True


def test_phase_283_commit_does_not_touch_decision_log() -> None:
    commit_ref = _resolve_phase_283_commit_ref()
    show = subprocess.run(
        ["git", "show", "--name-only", "--format=", commit_ref],
        check=True,
        capture_output=True,
        text=True,
    )
    touched = [line.strip() for line in show.stdout.splitlines() if line.strip()]
    assert DECISION_LOG_PATH not in touched, f"{commit_ref} touched decision log"
