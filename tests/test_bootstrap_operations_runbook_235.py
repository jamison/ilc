from __future__ import annotations

from pathlib import Path
import re


RUNBOOK_PATH = Path("docs/specs/ilc_bootstrap_operations_runbook_235_v0.1.md")


def _text() -> str:
    return RUNBOOK_PATH.read_text(encoding="utf-8")


def _section(text: str, heading: str) -> str:
    parts = text.split(heading)
    assert len(parts) >= 2, f"missing heading: {heading}"
    tail = parts[1]
    next_idx = tail.find("\n## ")
    if next_idx == -1:
        return tail
    return tail[:next_idx]


def test_phase_235_runbook_exists_and_required_sections_present() -> None:
    assert RUNBOOK_PATH.exists()

    text = _text()
    required = [
        "## 1. Purpose and scope",
        "## 2. Genesis fleet composition baseline",
        "## 3. Phase A bootstrap sequence",
        "## 4. Phase A->B transition criteria",
        "## 5. Observability plan",
        "## 6. Failure modes and recovery posture",
        "## 7. Non-goal boundaries",
        "## 8. Deterministic acceptance checklist",
    ]

    for token in required:
        assert token in text

    # Ensure required sections remain in deterministic order.
    offsets = [text.index(token) for token in required]
    assert offsets == sorted(offsets)


def test_phase_235_transition_criteria_cover_gate_a_and_starmap_deferral() -> None:
    text = _text()
    section = _section(text, "## 4. Phase A->B transition criteria")

    assert "CapProof" in section
    assert "fail-closed" in section or "Phase 231 Gate A" in section
    assert "user-supplied" in section and "backend" in section

    assert "CDL-001" in section
    assert "CDL-002" in section
    assert "CDL-007" in section

    lower = section.lower()
    assert "star.map" in lower or "cross-shard" in lower
    assert "phase b/c" in lower


def test_phase_235_acceptance_checklist_has_minimum_checkboxes() -> None:
    text = _text()
    section = _section(text, "## 8. Deterministic acceptance checklist")
    checklist_items = re.findall(r"^\s*- \[ \] .+", section, flags=re.MULTILINE)
    assert len(checklist_items) >= 8


def test_phase_235_observability_has_minimum_signal_categories() -> None:
    text = _text()
    section = _section(text, "## 5. Observability plan")

    categories = re.findall(r"^\s*\d+\.\s+\*\*.+\*\*", section, flags=re.MULTILINE)
    assert len(categories) >= 3

    lower = section.lower()
    assert "epoch transition" in lower
    assert "capproof" in lower and "probe" in lower
    assert (
        "stake/balance" in lower
        or "error" in lower
        or "refutation" in lower
    )


def test_phase_235_no_ratification_language_and_anchor_paths_exist() -> None:
    text = _text().lower()

    forbidden = [
        "is hereby ratified",
        "ratified in this phase",
        "this phase ratifies",
        "status changed to ratified",
    ]
    for token in forbidden:
        assert token not in text

    original_text = _text()
    section = _section(original_text, "## 1. Purpose and scope")
    anchors = re.findall(r"`(docs/[^`]+)`", section)
    assert anchors, "no canonical anchor paths listed"
    for anchor in anchors:
        assert Path(anchor).exists(), f"missing canonical anchor path: {anchor}"
