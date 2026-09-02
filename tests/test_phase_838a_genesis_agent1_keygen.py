"""Phase 838a — Genesis Agent 1 PQ keygen tool tests (CDL-069 compliant)."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL = REPO_ROOT / "tools" / "genesis_agent1_keygen.py"
PQ_KEYGEN_BIN = (
    REPO_ROOT / "ilc_consensus" / "target" / "debug" / "pq_keygen"
)

# ---------------------------------------------------------------------------
# Fixture: fake pq_keygen binary that emits deterministic test output
# ---------------------------------------------------------------------------

# 32-byte identity_seed expressed as 24 BIP-39 words (fixture only, never live)
_PLATE1_WORDS = (
    "abandon abandon abandon abandon abandon abandon abandon abandon "
    "abandon abandon abandon abandon abandon abandon abandon abandon "
    "abandon abandon abandon abandon abandon abandon abandon art"
)
# 32-byte mldsa_seed words
_PLATE2_WORDS = (
    "zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo "
    "zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo vote"
)
# 32-byte sphincs_seed words
_PLATE3_WORDS = (
    "legal winner thank year wave sausage worth useful legal winner "
    "thank year wave sausage worth useful legal winner thank year "
    "wave sausage worth title"
)

# 96-char hex agent_id (SHA-384 output — Tier 3, 48 bytes)
_FIXTURE_AGENT_ID = "a" * 96
# 3904-char hex ML-DSA-65 pk
_FIXTURE_MLDSA_PK = "b" * 3904
# 32-char hex SPHINCS+ pk (SLH-DSA-SHA2-128s pk = 32 bytes)
_FIXTURE_SPHINCS_PK = "c" * 64
# 96-char hex commitments
_FIXTURE_ID_COMMIT = "d" * 96
_FIXTURE_REC_COMMIT = "e" * 96


def _make_fake_pq_keygen(tmp_path: Path) -> Path:
    """Shell script that mimics `pq_keygen` stdout output."""
    script = tmp_path / "fake_pq_keygen"
    script.write_text(
        "#!/bin/sh\n"
        f"echo '========================================================================';\n"
        f"echo '  GENESIS AGENT 1 PQ KEYGEN RECORD';\n"
        f"echo '  tool:    pq_keygen_838a.v0.1';\n"
        f"echo '========================================================================';\n"
        f"echo '';\n"
        f"echo '  PUBLIC MATERIAL (safe to write to USB, repo, anywhere)';\n"
        f"echo '  --------------------------------------------------------';\n"
        f"echo '  agent_id:                    {_FIXTURE_AGENT_ID}';\n"
        f"echo '  mldsa_pk (hex):              {_FIXTURE_MLDSA_PK}';\n"
        f"echo '  sphincs_pk (hex):            {_FIXTURE_SPHINCS_PK}';\n"
        f"echo '  identity_seed_commitment:    {_FIXTURE_ID_COMMIT}';\n"
        f"echo '  recovery_commitment:         {_FIXTURE_REC_COMMIT}';\n"
        f"echo '';\n"
        f"echo '  SECRET MATERIAL — WRITE DOWN EACH SECTION, THEN CLOSE THIS TERMINAL';\n"
        f"echo '';\n"
        f"echo '  [PLATE 1] identity_seed — 24 words';\n"
        f"echo '  {_PLATE1_WORDS}';\n"
        f"echo '';\n"
        f"echo '  [PLATE 2] ML-DSA-65 canonical root seed — 24 words';\n"
        f"echo '  {_PLATE2_WORDS}';\n"
        f"echo '';\n"
        f"echo '  [PLATE 3] SPHINCS+ recovery seed — 24 words';\n"
        f"echo '  {_PLATE3_WORDS}';\n"
        "if [ -n \"$1\" ] && [ \"$1\" = '--pubkey-record' ] && [ -n \"$2\" ]; then\n"
        f"  printf "
        f"'GENESIS AGENT 1 PUBKEY VERIFICATION RECORD\\n"
        f"agent_id:                 {_FIXTURE_AGENT_ID}\\n"
        f"mldsa_pk_hex:             {_FIXTURE_MLDSA_PK}\\n"
        f"sphincs_pk_hex:           {_FIXTURE_SPHINCS_PK}\\n"
        f"identity_seed_commitment: {_FIXTURE_ID_COMMIT}\\n"
        f"recovery_commitment:      {_FIXTURE_REC_COMMIT}\\n"
        f"NOTE: No secret seed material is stored in this file.\\n"
        f"genesis_agent1_pubkey_record_838a\\n"
        f"pq_keygen_838a_binary_present\\n' > \"$2\";\n"
        "fi\n",
        encoding="utf-8",
    )
    script.chmod(0o755)
    return script


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
    assert 'TOOL_VERSION = "genesis_agent1_keygen_838a.v0.2"' in _tool_text()


# ---------------------------------------------------------------------------
# Security contract: no file writes for secret seeds
# ---------------------------------------------------------------------------

def test_tool_does_not_write_secret_seeds_to_file() -> None:
    """The tool must not write secret seed material to disk.
    The pubkey-record path is forwarded to the binary which writes public
    fields only.  The Python wrapper itself never writes files."""
    text = _tool_text()
    # Wrapper must not call write_text or open() with seed content
    assert "write_text" not in text
    # Safety comment from security contract
    assert "NO secret seeds" in text


def test_tool_imports_cdl042_derivation() -> None:
    """Must import the CDL-042 runtime derivation (legacy contract, kept for
    module importability)."""
    text = _tool_text()
    assert "from ilc_core.identity.agent_id_runtime import derive_agent_id" in text


def test_tool_calls_pq_keygen_not_old_keygen() -> None:
    """Must call pq_keygen, not the old BLS-only keygen binary."""
    text = _tool_text()
    assert "pq_keygen" in text
    # Must not reference old --print flag (BLS keygen pattern)
    assert '"--print"' not in text


# ---------------------------------------------------------------------------
# CDL-042 _derive function — legacy BLS agent_id (importability contract)
# ---------------------------------------------------------------------------

def test_derive_importable_from_tool() -> None:
    """_derive must be importable and call the CDL-042 runtime derivation."""
    sys.path.insert(0, str(REPO_ROOT))
    from tools.genesis_agent1_keygen import _derive  # noqa: F401
    # Smoke: function exists and is callable
    assert callable(_derive)


# ---------------------------------------------------------------------------
# Integration: fake pq_keygen binary — stdout fields
# ---------------------------------------------------------------------------

def test_output_contains_plate_labels(tmp_path: Path) -> None:
    fake_bin = _make_fake_pq_keygen(tmp_path)
    result = subprocess.run(
        [sys.executable, str(TOOL), "--pq-keygen-bin", str(fake_bin)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "[PLATE 1]" in result.stdout
    assert "[PLATE 2]" in result.stdout
    assert "[PLATE 3]" in result.stdout


def test_output_contains_agent_id(tmp_path: Path) -> None:
    fake_bin = _make_fake_pq_keygen(tmp_path)
    result = subprocess.run(
        [sys.executable, str(TOOL), "--pq-keygen-bin", str(fake_bin)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert _FIXTURE_AGENT_ID in result.stdout


def test_output_contains_mldsa_pk(tmp_path: Path) -> None:
    fake_bin = _make_fake_pq_keygen(tmp_path)
    result = subprocess.run(
        [sys.executable, str(TOOL), "--pq-keygen-bin", str(fake_bin)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert _FIXTURE_MLDSA_PK in result.stdout


def test_output_contains_sphincs_pk(tmp_path: Path) -> None:
    fake_bin = _make_fake_pq_keygen(tmp_path)
    result = subprocess.run(
        [sys.executable, str(TOOL), "--pq-keygen-bin", str(fake_bin)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert _FIXTURE_SPHINCS_PK in result.stdout


def test_output_contains_genesis_keygen_record_header(tmp_path: Path) -> None:
    fake_bin = _make_fake_pq_keygen(tmp_path)
    result = subprocess.run(
        [sys.executable, str(TOOL), "--pq-keygen-bin", str(fake_bin)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "GENESIS AGENT 1 PQ KEYGEN RECORD" in result.stdout


# ---------------------------------------------------------------------------
# Integration: pubkey record written to path — public fields only, no seeds
# ---------------------------------------------------------------------------

def test_pubkey_record_written(tmp_path: Path) -> None:
    fake_bin = _make_fake_pq_keygen(tmp_path)
    record_path = tmp_path / "pubkey_record.txt"
    result = subprocess.run(
        [sys.executable, str(TOOL), "--pq-keygen-bin", str(fake_bin),
         "--pubkey-record", str(record_path)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert record_path.exists()


def test_pubkey_record_contains_agent_id(tmp_path: Path) -> None:
    fake_bin = _make_fake_pq_keygen(tmp_path)
    record_path = tmp_path / "pubkey_record.txt"
    subprocess.run(
        [sys.executable, str(TOOL), "--pq-keygen-bin", str(fake_bin),
         "--pubkey-record", str(record_path)],
        capture_output=True, text=True,
    )
    text = record_path.read_text(encoding="utf-8")
    assert _FIXTURE_AGENT_ID in text


def test_pubkey_record_contains_mldsa_pk(tmp_path: Path) -> None:
    fake_bin = _make_fake_pq_keygen(tmp_path)
    record_path = tmp_path / "pubkey_record.txt"
    subprocess.run(
        [sys.executable, str(TOOL), "--pq-keygen-bin", str(fake_bin),
         "--pubkey-record", str(record_path)],
        capture_output=True, text=True,
    )
    text = record_path.read_text(encoding="utf-8")
    assert _FIXTURE_MLDSA_PK in text


def test_pubkey_record_contains_sphincs_pk(tmp_path: Path) -> None:
    fake_bin = _make_fake_pq_keygen(tmp_path)
    record_path = tmp_path / "pubkey_record.txt"
    subprocess.run(
        [sys.executable, str(TOOL), "--pq-keygen-bin", str(fake_bin),
         "--pubkey-record", str(record_path)],
        capture_output=True, text=True,
    )
    text = record_path.read_text(encoding="utf-8")
    assert _FIXTURE_SPHINCS_PK in text


def test_pubkey_record_contains_verification_token(tmp_path: Path) -> None:
    fake_bin = _make_fake_pq_keygen(tmp_path)
    record_path = tmp_path / "pubkey_record.txt"
    subprocess.run(
        [sys.executable, str(TOOL), "--pq-keygen-bin", str(fake_bin),
         "--pubkey-record", str(record_path)],
        capture_output=True, text=True,
    )
    text = record_path.read_text(encoding="utf-8")
    assert "genesis_agent1_pubkey_record_838a" in text


def test_pubkey_record_does_not_contain_plate1_words(tmp_path: Path) -> None:
    """Plate 1 words (identity_seed) must NOT appear in the pubkey record."""
    fake_bin = _make_fake_pq_keygen(tmp_path)
    record_path = tmp_path / "pubkey_record.txt"
    subprocess.run(
        [sys.executable, str(TOOL), "--pq-keygen-bin", str(fake_bin),
         "--pubkey-record", str(record_path)],
        capture_output=True, text=True,
    )
    text = record_path.read_text(encoding="utf-8")
    # identity_seed words must not be written to disk
    assert _PLATE1_WORDS[:30] not in text


def test_pubkey_record_does_not_contain_plate2_words(tmp_path: Path) -> None:
    """Plate 2 words (mldsa_seed) must NOT appear in the pubkey record."""
    fake_bin = _make_fake_pq_keygen(tmp_path)
    record_path = tmp_path / "pubkey_record.txt"
    subprocess.run(
        [sys.executable, str(TOOL), "--pq-keygen-bin", str(fake_bin),
         "--pubkey-record", str(record_path)],
        capture_output=True, text=True,
    )
    text = record_path.read_text(encoding="utf-8")
    assert _PLATE2_WORDS[:30] not in text


def test_pubkey_record_does_not_contain_plate3_words(tmp_path: Path) -> None:
    """Plate 3 words (sphincs_seed) must NOT appear in the pubkey record."""
    fake_bin = _make_fake_pq_keygen(tmp_path)
    record_path = tmp_path / "pubkey_record.txt"
    subprocess.run(
        [sys.executable, str(TOOL), "--pq-keygen-bin", str(fake_bin),
         "--pubkey-record", str(record_path)],
        capture_output=True, text=True,
    )
    text = record_path.read_text(encoding="utf-8")
    assert _PLATE3_WORDS[:30] not in text


# ---------------------------------------------------------------------------
# Error handling: missing binary exits non-zero
# ---------------------------------------------------------------------------

def test_missing_pq_keygen_binary_exits_nonzero(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(TOOL), "--pq-keygen-bin", str(tmp_path / "no_such_bin")],
        capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert "not found" in result.stderr.lower() or "error" in result.stderr.lower()


# ---------------------------------------------------------------------------
# Binary smoke test: real pq_keygen binary produces correct field structure
# ---------------------------------------------------------------------------

@pytest.mark.skipif(
    not PQ_KEYGEN_BIN.exists(),
    reason="pq_keygen binary not built — run: cd ilc_consensus && cargo build --bin pq_keygen",
)
def test_real_binary_produces_plate_labels() -> None:
    result = subprocess.run(
        [str(PQ_KEYGEN_BIN)], capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "[PLATE 1]" in result.stdout
    assert "[PLATE 2]" in result.stdout
    assert "[PLATE 3]" in result.stdout


@pytest.mark.skipif(
    not PQ_KEYGEN_BIN.exists(),
    reason="pq_keygen binary not built",
)
def test_real_binary_agent_id_is_96_hex_chars() -> None:
    result = subprocess.run(
        [str(PQ_KEYGEN_BIN)], capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    # Extract agent_id line
    for line in result.stdout.splitlines():
        if "agent_id:" in line:
            agent_id = line.split("agent_id:")[-1].strip()
            assert len(agent_id) == 96, f"Expected 96-char agent_id, got {len(agent_id)}"
            assert all(c in "0123456789abcdef" for c in agent_id)
            break
    else:
        pytest.fail("agent_id not found in pq_keygen output")


@pytest.mark.skipif(
    not PQ_KEYGEN_BIN.exists(),
    reason="pq_keygen binary not built",
)
def test_real_binary_pubkey_record_excludes_seed_words(tmp_path: Path) -> None:
    record_path = tmp_path / "live_pubkey_record.txt"
    # Run twice: once for stdout (to get seed words), once for record check
    result = subprocess.run(
        [str(PQ_KEYGEN_BIN), "--pubkey-record", str(record_path)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert record_path.exists()

    # Extract plate 1 words from stdout to verify they are absent from record
    plate1_words: str | None = None
    in_plate1 = False
    for line in result.stdout.splitlines():
        if "[PLATE 1]" in line:
            in_plate1 = True
            continue
        if in_plate1 and line.strip():
            plate1_words = line.strip()
            break

    record_text = record_path.read_text(encoding="utf-8")
    assert "genesis_agent1_pubkey_record_838a" in record_text
    assert "pq_keygen_838a_binary_present" in record_text
    if plate1_words:
        assert plate1_words[:20] not in record_text, (
            "identity_seed words found in pubkey record — security violation"
        )
