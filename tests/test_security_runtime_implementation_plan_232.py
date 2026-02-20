from __future__ import annotations

from pathlib import Path


PLAN_PATH = Path("docs/specs/ilc_security_runtime_implementation_plan_232_v0.1.md")


def _text() -> str:
    return PLAN_PATH.read_text(encoding="utf-8")


def _section(text: str, header: str) -> str:
    parts = text.split(header)
    assert len(parts) >= 2, f"missing section header: {header}"
    tail = parts[1]
    next_header_index = tail.find("\n## ")
    if next_header_index == -1:
        return tail
    return tail[:next_header_index]


def test_phase_232_plan_exists() -> None:
    assert PLAN_PATH.exists()


def test_phase_232_required_sections_present() -> None:
    text = _text()
    assert "## 1. Purpose and scope" in text
    assert "## 2. CDL implementation sequence" in text
    assert "## 3. Deferred-from-Phase-227 mapping per CDL" in text
    assert "## 4. Test strategy per CDL" in text
    assert "## 5. Risk and rollback plan per CDL" in text
    assert "## 6. Entry criteria for implementation phases" in text
    assert "## 7. Non-goals and canonical anchors" in text


def test_phase_232_sequence_names_all_cdls_and_dependency_order() -> None:
    text = _text()
    assert "`CDL-001`" in text
    assert "`CDL-002`" in text
    assert "`CDL-007`" in text
    assert "Must start only after `CDL-001` trust-root runtime is active" in text


def test_phase_232_cdl007_parallelism_and_negative_paths_present() -> None:
    text = _text()
    assert "Partial parallelism allowed" in text
    assert "Final closure must occur after `CDL-001` runtime establishment" in text
    assert "negative-path replay rejection tests" in text
    assert "negative-path conflict rejection tests" in text


def test_phase_232_entry_criteria_uses_non_hedged_language() -> None:
    text = _text()
    section = _section(text, "## 6. Entry criteria for implementation phases")
    assert "must be true before" in section
    assert "must pass" in section
    assert "must exist" in section

    lower = section.lower()
    assert " should " not in lower
    assert " may " not in lower
    assert "when possible" not in lower


def test_phase_232_risk_rollback_and_non_goals_tokens_present() -> None:
    text = _text()
    assert "### 5.1 `CDL-001` risk and rollback" in text
    assert "### 5.2 `CDL-002` risk and rollback" in text
    assert "### 5.3 `CDL-007` risk and rollback" in text
    assert "does not implement `ilc_core/` runtime behavior" in text
    assert "does not mutate CDL status fields" in text
