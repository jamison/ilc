from __future__ import annotations

from pathlib import Path


PLAN_PATH = Path("docs/specs/ilc_issuance_governance_plan_233_v0.1.md")


def _text() -> str:
    return PLAN_PATH.read_text(encoding="utf-8")


def _section(text: str, heading: str) -> str:
    parts = text.split(heading)
    assert len(parts) >= 2, f"missing heading: {heading}"
    tail = parts[1]
    next_idx = tail.find("\n## ")
    if next_idx == -1:
        return tail
    return tail[:next_idx]


def test_phase_233_plan_exists() -> None:
    assert PLAN_PATH.exists()


def test_phase_233_required_sections_present() -> None:
    text = _text()
    assert "## 1. Purpose and scope" in text
    assert "## 2. CDL-019 scope analysis" in text
    assert "## 3. Open issuance parameter inventory" in text
    assert "## 4. Hard cap vs. tail emission reconciliation" in text
    assert "## 5. Decision-log queue mapping" in text
    assert "## 6. Dependency map" in text
    assert "## 7. Non-goal boundaries" in text
    assert "## 8. Canonical anchors" in text


def test_phase_233_cdl019_components_and_floor_protection_present() -> None:
    text = _text()
    section = _section(text, "## 2. CDL-019 scope analysis")
    assert "flat `1.2x` multiplier" in section
    assert "invariant floor cannot be relaxed" in section
    assert "dynamic ranking-based multiplier path" in section.lower()
    assert "R(refute) > R(validate)" in section


def test_phase_233_open_issuance_inventory_and_models_present() -> None:
    text = _text()
    inventory = _section(text, "## 3. Open issuance parameter inventory")
    for token in [
        "`C_max`",
        "halving period `H` or continuous decay rate `lambda`",
        "tail emission mint rate",
        "fee-burn split ratio",
        "allocation split (performer/auditor/genesis)",
        "ECU price clamp bounds (`P_min`, `P_max`)",
    ]:
        assert token in inventory

    section = _section(text, "## 4. Hard cap vs. tail emission reconciliation")
    assert "Model A" in section
    assert "Model B" in section
    assert "Model C" in section
    assert "Model B" in section and "recommended" in section.lower()


def test_phase_233_queue_mapping_and_dependency_ordering_present() -> None:
    text = _text()
    queue = _section(text, "## 5. Decision-log queue mapping")
    assert "| Queue topic | CDL entry | Current status | Target ratification window |" in queue
    assert "TBD" not in queue
    assert "CDL-019" in queue
    assert "CDL-025" in queue
    assert "CDL-030" in queue
    assert "CDL-031" in queue

    deps = _section(text, "## 6. Dependency map")
    assert "must precede" in deps
    assert "must be resolved before" in deps
    assert "must follow" in deps
    assert "must be validated against `theta_hard = 1/20`" in deps


def test_phase_233_non_goals_and_no_ratification_phrases() -> None:
    text = _text()
    non_goals = _section(text, "## 7. Non-goal boundaries")
    assert "QATPS/CIT economic coupling" in non_goals
    assert "ADAPT profile governance ratification" in non_goals

    lowered = text.lower()
    forbidden = [
        "is hereby ratified",
        "ratified in this phase",
        "this phase ratifies",
        "status changed to ratified",
    ]
    for token in forbidden:
        assert token not in lowered
