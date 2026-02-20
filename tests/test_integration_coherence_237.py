from __future__ import annotations

from pathlib import Path
import re


CAPSULE_PATH = Path("docs/specs/ilc_antigravity_context_capsule_v0.3.md")
COHERENCE_PATH = Path("docs/specs/ilc_integration_coherence_report_237_v0.1.md")
CDL_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _section(text: str, heading: str) -> str:
    parts = text.split(heading)
    assert len(parts) >= 2, f"missing heading: {heading}"
    tail = parts[1]
    next_idx = tail.find("\n## ")
    if next_idx == -1:
        return tail
    return tail[:next_idx]


def test_phase_237_capsule_exists_and_has_required_updates() -> None:
    assert CAPSULE_PATH.exists()
    text = _read(CAPSULE_PATH)
    lower = text.lower()

    assert "supersedes" in lower
    assert "v0.2" in lower
    assert "## 17. SDK/CLI Architecture" in text
    assert "## 18. OpenClaw Integration Model" in text
    assert "ADM-002" in text or "ilc_adm_002" in text
    assert "CDL-032" in text
    assert "CDL-033" in text


def test_phase_237_coherence_report_exists_and_sections_present() -> None:
    assert COHERENCE_PATH.exists()
    text = _read(COHERENCE_PATH)

    required = [
        "## 1. Scope",
        "## 2. Capsule alignment check",
        "## 3. Roadmap alignment check",
        "## 4. CDL log alignment check",
        "## 5. Cross-reference integrity",
        "## 6. Non-goal boundaries",
    ]
    for token in required:
        assert token in text


def test_phase_237_cdl_rows_present() -> None:
    text = _read(CDL_PATH)
    for cdl in ["CDL-020", "CDL-021", "CDL-022", "CDL-023", "CDL-024", "CDL-032", "CDL-033"]:
        assert cdl in text


def test_phase_237_no_ratification_language_in_new_artifacts() -> None:
    forbidden = [
        "is hereby ratified",
        "ratified in this phase",
        "this phase ratifies",
        "status changed to ratified",
    ]

    for text in (_read(CAPSULE_PATH).lower(), _read(COHERENCE_PATH).lower()):
        for token in forbidden:
            assert token not in text


def test_phase_237_anchor_paths_exist() -> None:
    paths: set[str] = set()
    capsule = _read(CAPSULE_PATH)
    coherence = _read(COHERENCE_PATH)

    # Keep anchor validation scoped to new Phase-237 additions and coherence report
    # so v0.2 historical anchors remain unchanged by this phase.
    for section_heading in [
        "## 17. SDK/CLI Architecture",
        "## 18. OpenClaw Integration Model",
    ]:
        section = _section(capsule, section_heading)
        paths.update(re.findall(r"`(docs/[^`]+)`", section))

    paths.update(re.findall(r"`(docs/[^`]+)`", coherence))

    assert paths, "no canonical anchor paths found"
    for path in paths:
        assert Path(path).exists(), f"missing anchor path: {path}"
