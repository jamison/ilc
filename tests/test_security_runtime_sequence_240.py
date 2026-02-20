from __future__ import annotations

from pathlib import Path
import re


SEQUENCE_PATH = Path("docs/specs/ilc_security_runtime_implementation_sequence_240_249_v0.1.md")


def _read() -> str:
    return SEQUENCE_PATH.read_text(encoding="utf-8")


def _section(text: str, heading: str) -> str:
    parts = text.split(heading)
    assert len(parts) >= 2, f"missing heading: {heading}"
    tail = parts[1]
    next_idx = tail.find("\n## ")
    if next_idx == -1:
        return tail
    return tail[:next_idx]


def test_phase_240_sequence_file_exists() -> None:
    assert SEQUENCE_PATH.exists()


def test_phase_240_sequence_lists_phases_240_to_249() -> None:
    text = _read()
    for phase in range(240, 250):
        assert f"| {phase} |" in text


def test_phase_240_sequence_has_sensitivity_table_and_sensitive_set() -> None:
    text = _read()
    section = _section(text, "## 4. Per-phase sensitivity classification")
    for phase in range(240, 245):
        assert f"| {phase} | sensitive |" in section


def test_phase_240_sequence_carry_forward_mentions_cdl_025_and_d2e() -> None:
    text = _read()
    section = _section(text, "## 8. Forward pointer and carry-forward debt list")
    assert "CDL-025" in section
    assert "D2e" in section


def test_phase_240_sequence_anchor_paths_exist() -> None:
    text = _read()
    anchors = re.findall(r"`(docs/[^`]+|tools/[^`]+)`", text)
    assert anchors, "no anchor paths found"

    for anchor in anchors:
        assert Path(anchor).exists(), f"missing anchor path: {anchor}"
