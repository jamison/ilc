from __future__ import annotations

from pathlib import Path
import itertools
import re


SCHEMA_PATH = Path("docs/specs/ilc_lineage_lifecycle_event_schema_v0.1.md")


def _read() -> str:
    return SCHEMA_PATH.read_text(encoding="utf-8")


def _section(text: str, heading: str) -> str:
    parts = text.split(heading)
    assert len(parts) >= 2, f"missing heading: {heading}"
    tail = parts[1]
    next_idx = tail.find("\n## ")
    if next_idx == -1:
        return tail
    return tail[:next_idx]


def test_phase_240_schema_exists() -> None:
    assert SCHEMA_PATH.exists()


def test_phase_240_schema_has_events_and_states() -> None:
    text = _read()
    assert "### 4.1 register" in text
    assert "### 4.2 rotate" in text
    assert "### 4.3 revoke" in text
    assert "### 4.4 recover" in text

    for state in ["active", "rotated", "revoked", "recovered"]:
        assert f"`{state}`" in text


def test_phase_240_schema_has_allowed_and_disallowed_sections_with_rationale() -> None:
    text = _read()
    assert "## 5. Allowed-transition table" in text
    assert "## 6. Disallowed-transition table" in text

    disallowed = _section(text, "## 6. Disallowed-transition table")
    assert "Disallowed rationale" in disallowed
    assert "cannot" in disallowed.lower() or "invalid" in disallowed.lower()


def test_phase_240_schema_transition_pair_coverage_is_complete() -> None:
    text = _read()
    allowed = _section(text, "## 5. Allowed-transition table")
    disallowed = _section(text, "## 6. Disallowed-transition table")

    pair_pattern = re.compile(r"\|\s*`(active|rotated|revoked|recovered)`\s*\|\s*`(active|rotated|revoked|recovered)`\s*\|")
    allowed_pairs = set(pair_pattern.findall(allowed))
    disallowed_pairs = set(pair_pattern.findall(disallowed))

    states = ["active", "rotated", "revoked", "recovered"]
    expected_pairs = {(src, dst) for src, dst in itertools.product(states, states) if src != dst}

    all_pairs = allowed_pairs | disallowed_pairs
    assert len(expected_pairs) == 12
    assert all_pairs == expected_pairs
    assert allowed_pairs.isdisjoint(disallowed_pairs)


def test_phase_240_schema_has_phase_232_anchor_and_no_ratification_language() -> None:
    text = _read()
    assert "ilc_security_runtime_implementation_plan_232_v0.1.md" in text
    assert "Section 6.1" in text

    lowered = text.lower()
    forbidden = [
        "is hereby ratified",
        "ratified in this phase",
        "this phase ratifies",
        "status changed to ratified",
    ]
    for token in forbidden:
        assert token not in lowered
