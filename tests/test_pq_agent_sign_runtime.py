"""Phase 1568 Fix2b-2/Fix2b-2a — pq_agent_sign runtime tests.

These tests build the current Rust binaries before exercising them. That avoids
the stale-binary failure mode where Python tests pass against an older
`target/debug/pq_agent_sign` unrelated to the current worktree.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
CONSENSUS_ROOT = REPO_ROOT / "ilc_consensus"
SIGNER = CONSENSUS_ROOT / "target/debug/pq_agent_sign"
KEYGEN = CONSENSUS_ROOT / "target/debug/pq_keygen"
MANIFEST = REPO_ROOT / "docs/specs/ilc_rehearsal_agent_identity_manifest_1431_v0.1.md"

_VALIDATOR_A1_AGENT_ID = (
    "d6592166bf9c15841e8c249007f261760b9808b5a85f3c0ebb8b7cd3527155cca279870dca142eb3bc9f42eb2f20b36c"
)
_GENESIS_AGENT_01_ID = (
    "c43f69fcc4dfd021f5e468824c9560c03c45c601f8d004be4d244356ce6043849b9cf2af38bc51a40c1c4bc3e71b04d9"
)

_ZERO_SIG_HEX = "00" * 3309
_SHORT_SIG_HEX = "aa" * 100


@pytest.fixture(scope="session", autouse=True)
def _build_pq_agent_sign() -> None:
    cargo = shutil.which("cargo") or str(Path.home() / ".cargo/bin/cargo")
    subprocess.run(
        [cargo, "build", "--bin", "pq_agent_sign", "--bin", "pq_keygen"],
        cwd=CONSENSUS_ROOT,
        check=True,
        timeout=120,
    )


def _run(args: list[str], *, stdin: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(SIGNER)] + args,
        cwd=REPO_ROOT,
        input=stdin,
        capture_output=True,
        text=True,
        timeout=30,
    )


def _extract(pattern: str, text: str) -> str:
    match = re.search(pattern, text, re.DOTALL)
    assert match, pattern
    return match.group(1).strip()


@pytest.fixture()
def generated_identity(tmp_path: Path) -> dict[str, str | Path]:
    pubkey_record = tmp_path / "pubkey_record.txt"
    result = subprocess.run(
        [str(KEYGEN), "--pubkey-record", str(pubkey_record)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
        timeout=30,
    )
    agent_id = _extract(r"agent_id:\s+([0-9a-f]{96})", result.stdout)
    mldsa_pk = _extract(r"mldsa_pk \(hex\):\s+([0-9a-f]+)", result.stdout)
    mldsa_seed_words = _extract(
        r"\[PLATE 2\] ML-DSA-65 canonical root seed.*?\n\s+([a-z]+(?:\s+[a-z]+){23})\s*\n",
        result.stdout,
    )
    manifest = tmp_path / "manifest.md"
    manifest.write_text(
        "\n".join(
            [
                "# Test Agent Manifest",
                "",
                "```",
                f"agent_id:                 {agent_id}",
                f"mldsa_pk_hex:             {mldsa_pk}",
                "```",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return {
        "agent_id": agent_id,
        "manifest": manifest,
        "mldsa_pk": mldsa_pk,
        "mldsa_seed_words": mldsa_seed_words,
    }


def test_binary_present() -> None:
    assert SIGNER.is_file()


def test_help_exits_zero_and_documents_domain_context() -> None:
    result = _run(["--help"])
    assert result.returncode == 0
    assert "ILC_AGENT_SUBMISSION_V1" in result.stderr
    assert "ILC_GENESIS_ROOT_ENVELOPE_V1" not in result.stderr
    assert "mldsa_seed" in result.stderr
    assert "identity_seed" in result.stderr
    assert "--envelope-json" in result.stderr


def test_missing_agent_id_exits_nonzero(tmp_path: Path) -> None:
    payload = tmp_path / "payload.json"
    payload.write_text("{}", encoding="utf-8")
    result = _run(["--input-file", str(payload)])
    assert result.returncode != 0
    assert "--agent-id" in result.stderr


def test_missing_input_file_exits_nonzero() -> None:
    result = _run(["--agent-id", _VALIDATOR_A1_AGENT_ID])
    assert result.returncode != 0
    assert "--input-file" in result.stderr


@pytest.mark.parametrize("flag", ["--seed", "--seed-hex", "--mnemonic"])
def test_secret_material_on_cli_rejected(flag: str, tmp_path: Path) -> None:
    payload = tmp_path / "payload.json"
    payload.write_text("{}", encoding="utf-8")
    result = _run(
        [
            "--agent-id",
            _VALIDATOR_A1_AGENT_ID,
            "--input-file",
            str(payload),
            flag,
            "aaaa",
        ]
    )
    assert result.returncode != 0
    assert "stdin" in result.stderr.lower()


def test_sign_mode_rejects_signature_hex_arg(tmp_path: Path) -> None:
    payload = tmp_path / "payload.json"
    payload.write_text("{}", encoding="utf-8")
    result = _run(
        [
            "--agent-id",
            _VALIDATOR_A1_AGENT_ID,
            "--input-file",
            str(payload),
            "--signature-hex",
            _ZERO_SIG_HEX,
        ]
    )
    assert result.returncode != 0
    assert "--signature-hex is only valid in verify mode" in result.stderr


def test_non_ascii_agent_id_rejected_without_panic(tmp_path: Path) -> None:
    payload = tmp_path / "payload.json"
    payload.write_text("{}", encoding="utf-8")
    result = _run(
        [
            "verify",
            "--agent-id",
            "€" * 48,
            "--input-file",
            str(payload),
            "--signature-hex",
            _ZERO_SIG_HEX,
        ]
    )
    assert result.returncode != 0
    assert "panicked" not in result.stderr.lower()
    assert "agent_id_" in result.stderr


def test_unknown_agent_id_not_found_in_manifest(tmp_path: Path) -> None:
    payload = tmp_path / "payload.json"
    payload.write_text("{}", encoding="utf-8")
    result = _run(
        [
            "verify",
            "--agent-id",
            "ab" * 48,
            "--input-file",
            str(payload),
            "--signature-hex",
            _ZERO_SIG_HEX,
        ]
    )
    assert result.returncode != 0
    assert "agent_id_not_found_in_manifest" in result.stderr


def test_duplicate_agent_id_in_manifest_rejected(tmp_path: Path) -> None:
    payload = tmp_path / "payload.json"
    payload.write_text("{}", encoding="utf-8")
    manifest_text = MANIFEST.read_text(encoding="utf-8")
    agent_block = re.search(
        rf"### Agent 4.*?(```\n.*?agent_id:\s+{_VALIDATOR_A1_AGENT_ID}.*?```)",
        manifest_text,
        re.DOTALL,
    )
    assert agent_block
    duplicate_manifest = tmp_path / "duplicate_manifest.md"
    duplicate_manifest.write_text(
        manifest_text + "\n\n" + agent_block.group(1) + "\n",
        encoding="utf-8",
    )
    result = _run(
        [
            "verify",
            "--agent-id",
            _VALIDATOR_A1_AGENT_ID,
            "--input-file",
            str(payload),
            "--signature-hex",
            _ZERO_SIG_HEX,
            "--manifest",
            str(duplicate_manifest),
        ]
    )
    assert result.returncode != 0
    assert "duplicate_agent_id_in_manifest" in result.stderr


def test_manifest_public_key_schema_validated(tmp_path: Path) -> None:
    payload = tmp_path / "payload.json"
    payload.write_text("{}", encoding="utf-8")
    bad_manifest = tmp_path / "bad_manifest.md"
    bad_manifest.write_text(
        "\n".join(
            [
                "```",
                f"agent_id: {_VALIDATOR_A1_AGENT_ID}",
                "mldsa_pk_hex: aa",
                "```",
            ]
        ),
        encoding="utf-8",
    )
    result = _run(
        [
            "verify",
            "--agent-id",
            _VALIDATOR_A1_AGENT_ID,
            "--input-file",
            str(payload),
            "--signature-hex",
            _ZERO_SIG_HEX,
            "--manifest",
            str(bad_manifest),
        ]
    )
    assert result.returncode != 0
    assert "mldsa_public_key_wrong_length" in result.stderr


def test_verify_requires_signature_hex(tmp_path: Path) -> None:
    payload = tmp_path / "payload.json"
    payload.write_text("{}", encoding="utf-8")
    result = _run(
        [
            "verify",
            "--agent-id",
            _VALIDATOR_A1_AGENT_ID,
            "--input-file",
            str(payload),
        ]
    )
    assert result.returncode != 0
    assert "--signature-hex" in result.stderr


def test_verify_wrong_length_signature_rejected(tmp_path: Path) -> None:
    payload = tmp_path / "payload.json"
    payload.write_text("{}", encoding="utf-8")
    result = _run(
        [
            "verify",
            "--agent-id",
            _VALIDATOR_A1_AGENT_ID,
            "--input-file",
            str(payload),
            "--signature-hex",
            _SHORT_SIG_HEX,
        ]
    )
    assert result.returncode != 0
    assert "mldsa_agent_submission_signature_wrong_length" in result.stderr


def test_generated_identity_sign_verify_and_envelope(
    generated_identity: dict[str, str | Path],
    tmp_path: Path,
) -> None:
    payload = tmp_path / "payload.json"
    payload.write_text('{"claim":"local-signature-test"}', encoding="utf-8")
    agent_id = str(generated_identity["agent_id"])
    manifest = Path(generated_identity["manifest"])
    mldsa_seed_words = str(generated_identity["mldsa_seed_words"])

    sign_result = _run(
        [
            "--agent-id",
            agent_id.upper(),
            "--input-file",
            str(payload),
            "--manifest",
            str(manifest),
            "--envelope-json",
        ],
        stdin=mldsa_seed_words,
    )
    assert sign_result.returncode == 0, sign_result.stderr
    envelope = json.loads(sign_result.stdout)
    assert envelope["agent_id"] == agent_id
    assert envelope["algorithm"] == "ML-DSA-65"
    assert envelope["signing_context"] == "ILC_AGENT_SUBMISSION_V1"
    assert len(envelope["signature_hex"]) == 3309 * 2
    assert envelope["input_sha256"]
    assert envelope["manifest_sha256"]

    verify_result = _run(
        [
            "verify",
            "--agent-id",
            agent_id,
            "--input-file",
            str(payload),
            "--manifest",
            str(manifest),
            "--signature-hex",
            envelope["signature_hex"],
        ]
    )
    assert verify_result.returncode == 0, verify_result.stderr
    assert "agent_submission_signature_verified" in verify_result.stdout

    wrong_payload = tmp_path / "wrong_payload.json"
    wrong_payload.write_text('{"claim":"tampered"}', encoding="utf-8")
    wrong_verify = _run(
        [
            "verify",
            "--agent-id",
            agent_id,
            "--input-file",
            str(wrong_payload),
            "--manifest",
            str(manifest),
            "--signature-hex",
            envelope["signature_hex"],
        ]
    )
    assert wrong_verify.returncode != 0
    assert "mldsa_agent_submission_signature_verification_failed" in wrong_verify.stderr


def test_raw_sign_output_remains_signature_hex_for_bridge_compatibility(
    generated_identity: dict[str, str | Path],
    tmp_path: Path,
) -> None:
    payload = tmp_path / "payload.json"
    payload.write_text("{}", encoding="utf-8")
    result = _run(
        [
            "--agent-id",
            str(generated_identity["agent_id"]),
            "--input-file",
            str(payload),
            "--manifest",
            str(generated_identity["manifest"]),
        ],
        stdin=str(generated_identity["mldsa_seed_words"]),
    )
    assert result.returncode == 0, result.stderr
    assert re.fullmatch(r"[0-9a-f]{6618}\n?", result.stdout)


def test_oversized_input_rejected_before_signing(
    generated_identity: dict[str, str | Path],
    tmp_path: Path,
) -> None:
    payload = tmp_path / "oversized.bin"
    payload.write_bytes(b"x" * (4 * 1024 * 1024 + 1))
    result = _run(
        [
            "--agent-id",
            str(generated_identity["agent_id"]),
            "--input-file",
            str(payload),
            "--manifest",
            str(generated_identity["manifest"]),
        ],
        stdin=str(generated_identity["mldsa_seed_words"]),
    )
    assert result.returncode != 0
    assert "input_file_exceeds_max_bytes" in result.stderr


def test_manifest_lookup_finds_all_seven_agent_ids() -> None:
    manifest_text = MANIFEST.read_text(encoding="utf-8")
    agent_ids = [
        "c43f69fcc4dfd021f5e468824c9560c03c45c601f8d004be4d244356ce6043849b9cf2af38bc51a40c1c4bc3e71b04d9",
        "09feeae6017ac091f6cf8dc410f6814bbfe018843ac76dffb835e5c44f18e2823daf4922c1be03ee87a4d9e70d4971e5",
        "5d7e8e092f42722dd7f92a504e29ed88c72ae44323d8786025fb3a380f841d6c2a448e9426ac3460bae3abb33881b6fc",
        "d6592166bf9c15841e8c249007f261760b9808b5a85f3c0ebb8b7cd3527155cca279870dca142eb3bc9f42eb2f20b36c",
        "bfc75431f3941080d4723063b17c6c7086f5b010952b5273839d250b30d70ab0f1799c0831a4ba6b1ad7ea8f09793c74",
        "4842b1bee669793b03e7cfbb01f3b5ae7e54a34a093bd7c88f95539d67ce973c084029e00abc79e4410398f6f712dec1",
        "dc6f1d4775c9c0a6c40ec57dd81c1fc0741d924013060ad0c9323099f12196ddabe007e0f4ba3fd89aed0e397c622ad7",
    ]
    for agent_id in agent_ids:
        assert agent_id in manifest_text


def test_verify_with_genesis_agent_01_uses_manifest_not_only_validator_a1(
    tmp_path: Path,
) -> None:
    payload = tmp_path / "payload.json"
    payload.write_text('{"agent": "genesis"}', encoding="utf-8")
    result = _run(
        [
            "verify",
            "--agent-id",
            _GENESIS_AGENT_01_ID,
            "--input-file",
            str(payload),
            "--signature-hex",
            _ZERO_SIG_HEX,
        ]
    )
    assert result.returncode != 0
    assert "agent_id_not_found_in_manifest" not in result.stderr
