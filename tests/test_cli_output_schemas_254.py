from __future__ import annotations

from pathlib import Path


SPEC_PATH = Path("docs/specs/ilc_cli_output_schemas_254_v0.1.md")

PRIMITIVES = [
    "assert",
    "validate",
    "contradict",
    "refute",
    "revise",
    "link",
    "epoch",
]

OPS = [
    "query",
    "verify",
    "balance",
    "identity",
    "bundle",
    "shard",
    "capproof",
    "config",
]


def _read() -> str:
    return SPEC_PATH.read_text(encoding="utf-8")


def test_spec_exists() -> None:
    assert SPEC_PATH.exists()


def test_contains_all_primitive_command_schemas() -> None:
    text = _read()
    for command in PRIMITIVES:
        assert f"`{command}`" in text


def test_contains_all_operational_command_schemas() -> None:
    text = _read()
    for command in OPS:
        assert f"`{command}`" in text


def test_contains_shared_error_response_schema() -> None:
    text = _read()
    assert "Error payload shape" in text
    assert '"error": true' in text
    assert '"code": "<exit_code>"' in text


def test_contains_exit_code_semantics_section() -> None:
    text = _read()
    assert "## 3. Exit-code semantics" in text
    for code in ["`0`", "`1`", "`2`", "`3`"]:
        assert code in text


def test_contains_schema_version_field() -> None:
    text = _read()
    assert '"schema_version": "254.v0.1"' in text


def test_contains_success_and_error_examples_per_primitive() -> None:
    text = _read()
    for command in PRIMITIVES:
        section = text.split(f"### 4.{PRIMITIVES.index(command) + 1} `{command}`", 1)[1]
        assert "Success example:" in section
        assert "Error example:" in section


def test_references_phase_253_cli_surface_lock_and_adm_002_v0_2() -> None:
    text = _read()
    assert "ilc_cli_command_surface_lock_253_v0.1.md" in text
    assert "ilc_adm_002_cli_first_agent_sdk_v0.2.md" in text


def test_contains_no_ratification_language() -> None:
    text = _read().lower()
    assert "ratified" not in text
    assert "ratification" not in text
