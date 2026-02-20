from __future__ import annotations

import re
from pathlib import Path


CAPSULE_PATH = Path("docs/specs/ilc_antigravity_context_capsule_v0.4.md")
REPORT_PATH = Path("docs/specs/ilc_integration_coherence_report_248_v0.1.md")

REQUIRED_REPORT_SECTIONS = [
    "## 1. Scope",
    "## 2. Capsule alignment check",
    "## 3. Roadmap alignment check",
    "## 4. CDL log alignment check",
    "## 5. Cross-reference integrity",
    "## 6. Non-goal boundaries",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_248_capsule_v0_4_exists_and_supersedes_v0_3() -> None:
    assert CAPSULE_PATH.exists()
    text = _read(CAPSULE_PATH)
    assert "# ILC Antigravity Context Capsule v0.4" in text
    assert "Supersedes: `ilc_antigravity_context_capsule_v0.3.md`" in text


def test_phase_248_capsule_has_new_sections_19_and_20() -> None:
    text = _read(CAPSULE_PATH)
    assert "## 19. Security Runtime Implementation Status (NEW in v0.4)" in text
    assert "## 20. D2e Pipeline Bootstrap (NEW in v0.4)" in text


def test_phase_248_coherence_report_exists_with_sections_1_through_6() -> None:
    assert REPORT_PATH.exists()
    text = _read(REPORT_PATH)
    for section in REQUIRED_REPORT_SECTIONS:
        assert section in text


def test_phase_248_report_confirms_cdl_001_002_007_remain_open() -> None:
    text = _read(REPORT_PATH)
    assert "CDL-001` remains `open`" in text
    assert "CDL-002` remains `open`" in text
    assert "CDL-007` remains `open`" in text


def test_phase_248_anchor_paths_in_report_exist() -> None:
    text = _read(REPORT_PATH)
    anchors = re.findall(r"`(docs/[^`]+)`", text)
    assert anchors, "expected at least one anchor path in report"
    missing = [anchor for anchor in anchors if not Path(anchor).exists()]
    assert not missing, f"missing anchor files: {missing}"


def test_phase_248_no_ratification_language() -> None:
    text = (_read(CAPSULE_PATH) + "\n" + _read(REPORT_PATH)).lower()
    forbidden = [
        "is hereby ratified",
        "ratified in this phase",
        "this phase ratifies",
        "status changed to ratified",
    ]
    for token in forbidden:
        assert token not in text
