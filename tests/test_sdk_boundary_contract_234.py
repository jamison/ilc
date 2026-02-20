from __future__ import annotations

from pathlib import Path
import re


CONTRACT_PATH = Path("docs/specs/ilc_sdk_boundary_contract_234_v0.1.md")


def _text() -> str:
    return CONTRACT_PATH.read_text(encoding="utf-8")


def _section(text: str, heading: str) -> str:
    parts = text.split(heading)
    assert len(parts) >= 2, f"missing heading: {heading}"
    tail = parts[1]
    next_idx = tail.find("\n## ")
    if next_idx == -1:
        return tail
    return tail[:next_idx]


def test_phase_234_contract_file_and_sections_exist() -> None:
    assert CONTRACT_PATH.exists()
    text = _text()
    required = [
        "## 1. Purpose and scope",
        "## 2. Boundary definition",
        "## 3. Protocol surface (SDK owns)",
        "## 4. Orchestration surface (SDK does not own)",
        "## 5. Runtime surface (SDK does not own)",
        "## 6. Anti-leakage rules",
        "## 7. Boundary examples",
        "## 8. ADM-002 relationship",
        "## 9. Non-goal boundaries",
        "## 10. Canonical anchors",
    ]
    for token in required:
        assert token in text


def test_phase_234_protocol_surface_and_io_coverage() -> None:
    text = _text()
    section = _section(text, "## 3. Protocol surface (SDK owns)")

    for primitive in [
        "`assert`",
        "`validate`",
        "`contradict`",
        "`refute`",
        "`revise`",
        "`link`",
        "`epoch`",
    ]:
        assert primitive in section

    for op in [
        "`query`",
        "`verify`",
        "`balance`",
        "`identity`",
        "`bundle`",
        "`shard`",
        "`capproof`",
        "`config`",
    ]:
        assert op in section

    assert "exit codes: `0`" in section
    assert "`1`" in section
    assert "`2`" in section
    assert "`3`" in section
    assert "COSE Sign1" in section
    assert "CID computation" in section
    assert "fail-closed" in section
    assert "no-user-supplied-kernels/backend-hints" in section


def test_phase_234_anti_leakage_rules_and_keywords() -> None:
    text = _text()
    section = _section(text, "## 6. Anti-leakage rules")

    numbered = re.findall(r"^\s*\d+\.\s+", section, flags=re.MULTILINE)
    assert len(numbered) >= 7

    lower = section.lower()
    assert "model-provider" in lower or "model provider" in lower
    assert "session state" in lower or "stateless" in lower
    assert "key material" in lower
    assert "star.map" in lower or "starmap" in lower


def test_phase_234_boundary_examples_table_requirements() -> None:
    text = _text()
    section = _section(text, "## 7. Boundary examples")

    lines = [line for line in section.splitlines() if line.strip().startswith("|")]
    # header + divider + at least 8 rows
    assert len(lines) >= 10

    data_rows = [
        row for row in lines[2:] if row.count("|") >= 3
    ]
    assert len(data_rows) >= 8

    joined = "\n".join(data_rows)
    assert "In boundary" in joined
    assert "Out of boundary" in joined
    assert "star.map" in joined or "cross-shard" in joined
    assert "capproof" in joined.lower()
    assert "user-supplied" in joined.lower() or "kernel" in joined.lower()


def test_phase_234_anchor_paths_exist_and_no_ratification_tokens() -> None:
    text = _text()
    section = _section(text, "## 10. Canonical anchors")

    paths = re.findall(r"`([^`]+)`", section)
    assert paths, "no canonical anchor paths found"
    for path in paths:
        assert Path(path).exists(), f"missing anchor path: {path}"

    lowered = text.lower()
    forbidden = [
        "is hereby ratified",
        "ratified in this phase",
        "this phase ratifies",
        "status changed to ratified",
    ]
    for token in forbidden:
        assert token not in lowered
