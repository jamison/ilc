from __future__ import annotations

from pathlib import Path
import re


PACKAGE_PATH = Path("docs/specs/ilc_post_genesis_readiness_package_238_v0.1.md")


def _read() -> str:
    return PACKAGE_PATH.read_text(encoding="utf-8")


def _section(text: str, heading: str) -> str:
    parts = text.split(heading)
    assert len(parts) >= 2, f"missing heading: {heading}"
    tail = parts[1]
    next_idx = tail.find("\n## ")
    if next_idx == -1:
        return tail
    return tail[:next_idx]


def test_phase_238_package_exists_and_required_sections_present() -> None:
    assert PACKAGE_PATH.exists()
    text = _read()

    required = [
        "## 1. Scope and window",
        "## 2. Phase-by-phase completion summary",
        "## 3. Open carry-forward items",
        "## 4. Test evidence summary",
        "## 5. Non-goal boundaries",
    ]
    for token in required:
        assert token in text


def test_phase_238_section2_mentions_phases_230_through_237() -> None:
    text = _read()
    section = _section(text, "## 2. Phase-by-phase completion summary")
    for n in range(230, 238):
        assert f"Phase {n}" in section


def test_phase_238_section3_includes_required_open_items() -> None:
    text = _read()
    section = _section(text, "## 3. Open carry-forward items")

    assert "CDL-001" in section
    assert "CDL-002" in section
    assert "CDL-007" in section
    assert "lineage lifecycle" in section.lower()
    assert "CDL-032" in section
    assert "D2e" in section


def test_phase_238_no_ratification_language() -> None:
    text = _read().lower()
    forbidden = [
        "is hereby ratified",
        "ratified in this phase",
        "this phase ratifies",
        "status changed to ratified",
    ]
    for token in forbidden:
        assert token not in text


def test_phase_238_anchor_paths_exist() -> None:
    text = _read()
    section = _section(text, "## 1. Scope and window")
    anchors = re.findall(r"`(docs/[^`]+|tools/[^`]+)`", section)
    assert anchors, "no canonical anchors found"
    for anchor in anchors:
        assert Path(anchor).exists(), f"missing anchor path: {anchor}"
