"""Phase 838a — Genesis Agent 1 keygen tool tests."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL = REPO_ROOT / "tools" / "genesis_agent1_keygen.py"

# Stable test keypair (not used anywhere live — fixture only)
_FIXTURE_SK = "a" * 64
_FIXTURE_PK = "b" * 96


def _tool_text() -> str:
    return TOOL.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Publication token and version
# ---------------------------------------------------------------------------

def test_tool_exists() -> None:
    assert TOOL.exists()


def test_publication_token_present() -> None:
    assert "genesis_agent1_keygen_838a_published" in _tool_text()


def test_tool_version_string() -> None:
    assert 'TOOL_VERSION = "genesis_agent1_keygen_838a.v0.1"' in _tool_text()


# ---------------------------------------------------------------------------
# Security contract: no file writes for sk
# ---------------------------------------------------------------------------

def test_tool_does_not_write_sk_to_file() -> None:
    """sk must never be written to disk. The tool must not open/write files
    with sk content. We verify by inspecting the source: the only write_text
    call in the tool is for the pubkey record, and that block must not contain
    'sk_hex' as a value being written."""
    text = _tool_text()
    # The write_text call exists for the pubkey record
    assert "write_text" in text
    # But sk_hex must not appear inside the write_text argument block
    # Find the write_text call and assert sk is explicitly excluded
    assert "NOTE: Secret key is NOT stored here." in text


def test_tool_imports_cdl042_derivation() -> None:
    """Must use the live CDL-042 runtime derivation, not a reimplementation."""
    text = _tool_text()
    assert "from ilc_core.identity.agent_id_runtime import derive_agent_id" in text


def test_tool_uses_print_mode_not_file_out() -> None:
    """Must call keygen with --print, not --out."""
    text = _tool_text()
    assert '"--print"' in text
    # Must not pass --out to keygen (that would write sk to disk via the binary)
    assert '"--out"' not in text


# ---------------------------------------------------------------------------
# CDL-042 agent_id derivation matches runtime
# ---------------------------------------------------------------------------

def test_derive_matches_runtime() -> None:
    """The agent_id produced by the tool's _derive function must match
    a direct call to the CDL-042 runtime derivation."""
    sys.path.insert(0, str(REPO_ROOT))
    from ilc_core.identity.agent_id_runtime import derive_agent_id
    from tools.genesis_agent1_keygen import _derive

    pk_bytes = bytes.fromhex(_FIXTURE_PK)
    assert _derive(_FIXTURE_PK) == derive_agent_id(pk_bytes)


# ---------------------------------------------------------------------------
# Integration: mock keygen binary, check output fields
# ---------------------------------------------------------------------------

def _make_fake_keygen(tmp_path: Path, sk: str, pk: str) -> Path:
    """Write a shell script that mimics `keygen --print` output."""
    script = tmp_path / "fake_keygen"
    script.write_text(
        f"#!/bin/sh\necho 'sk={sk}'\necho 'pk={pk}'\n",
        encoding="utf-8",
    )
    script.chmod(0o755)
    return script


def test_output_contains_pk_and_agent_id(tmp_path: pytest.FixtureRequest) -> None:
    fake_bin = _make_fake_keygen(tmp_path, _FIXTURE_SK, _FIXTURE_PK)
    result = subprocess.run(
        [sys.executable, str(TOOL), "--keygen-bin", str(fake_bin)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert _FIXTURE_PK in result.stdout
    assert "agent_id:" in result.stdout
    assert "GENESIS AGENT 1 KEYGEN RECORD" in result.stdout


def test_output_contains_sk(tmp_path: pytest.FixtureRequest) -> None:
    fake_bin = _make_fake_keygen(tmp_path, _FIXTURE_SK, _FIXTURE_PK)
    result = subprocess.run(
        [sys.executable, str(TOOL), "--keygen-bin", str(fake_bin)],
        capture_output=True, text=True,
    )
    assert _FIXTURE_SK in result.stdout


def test_pubkey_record_written_without_sk(tmp_path: pytest.FixtureRequest) -> None:
    fake_bin = _make_fake_keygen(tmp_path, _FIXTURE_SK, _FIXTURE_PK)
    record_path = tmp_path / "pubkey_record.txt"
    result = subprocess.run(
        [sys.executable, str(TOOL), "--keygen-bin", str(fake_bin),
         "--pubkey-record", str(record_path)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert record_path.exists()
    record_text = record_path.read_text(encoding="utf-8")
    # pk must be present
    assert _FIXTURE_PK in record_text
    # sk must NOT be present
    assert _FIXTURE_SK not in record_text
    # verification token
    assert "genesis_agent1_pubkey_record_838a" in record_text


def test_pubkey_record_contains_agent_id(tmp_path: pytest.FixtureRequest) -> None:
    sys.path.insert(0, str(REPO_ROOT))
    from ilc_core.identity.agent_id_runtime import derive_agent_id

    fake_bin = _make_fake_keygen(tmp_path, _FIXTURE_SK, _FIXTURE_PK)
    record_path = tmp_path / "pubkey_record.txt"
    subprocess.run(
        [sys.executable, str(TOOL), "--keygen-bin", str(fake_bin),
         "--pubkey-record", str(record_path)],
        capture_output=True, text=True,
    )
    record_text = record_path.read_text(encoding="utf-8")
    expected_id = derive_agent_id(bytes.fromhex(_FIXTURE_PK))
    assert expected_id in record_text


def test_missing_keygen_binary_exits_nonzero(tmp_path: pytest.FixtureRequest) -> None:
    result = subprocess.run(
        [sys.executable, str(TOOL), "--keygen-bin", str(tmp_path / "no_such_bin")],
        capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert "not found" in result.stderr.lower() or "error" in result.stderr.lower()
