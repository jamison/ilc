from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)

COHERENCE_PATH = Path("docs/specs/ilc_integration_coherence_report_513_v0.1.md")
CAPSULE_PATH = Path("docs/specs/ilc_antigravity_context_capsule_v2.4.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
TEST_PATH = Path("tests/test_phase_513_coherence_report_and_capsule_v2_4.py")
PHASE_513_SUBJECT_TOKEN = "phase 513 coherence report and capsule"
EXACT_REQUIRED_MAIN_PATHS = {
    str(COHERENCE_PATH),
    str(CAPSULE_PATH),
    str(TEST_PATH),
}
COHERENCE_HEADINGS = (
    "## 1. Window summary",
    "## 2. CDL-055/056 runtime integration review",
    "## 3. Epoch-boundary CDL ratification",
    "## 4. re_admission_boundary scoping",
    "## 5. Deferred carry-forwards",
    "## 6. Snapshot isolation proof",
)
COHERENCE_TOKENS = (
    "CDL-055 runtime is implemented in Phase 506.",
    "CDL-056 runtime is implemented in Phase 507.",
    "re_admission_boundary is constitutionally excluded from the CDL-055 runtime.",
    "CDL-058 opening is a Window 515+ carry-forward.",
    "ADR-0023 quality signal architecture remains a research carry-forward.",
    "No ilc_core/ mutation occurs in Phase 513.",
    "No decision-log mutation occurs in Phase 513.",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _commit_text(path: str, commit_ref: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{commit_ref}:{path}"],
        capture_output=True,
        check=True,
        text=True,
    )
    return result.stdout


def _resolve_phase_513_commit_ref() -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    matching: list[str] = []
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if PHASE_513_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError("phase_513_commit_subject_present_but_no_qualifying_synthesis_commit")
    raise AssertionError("phase_513_commit_not_present_in_local_history")


def test_coherence_report_contains_required_headings_and_tokens() -> None:
    text = _read(COHERENCE_PATH)
    for heading in COHERENCE_HEADINGS:
        assert heading in text
    for token in COHERENCE_TOKENS:
        assert token in text


def test_capsule_v2_4_supersedes_v2_3() -> None:
    text = _read(CAPSULE_PATH)
    assert "Supersedes: docs/specs/ilc_antigravity_context_capsule_v2.3.md" in text
    assert "Capsule v2.4 supersedes v2.3." in text
    assert "Window 505-514 remains active at Phase 513." in text
    assert "Phase 514 is the next authorized phase." in text


def test_capsule_v2_4_contains_required_carry_forward_items() -> None:
    text = _read(CAPSULE_PATH)
    assert "CDL-058 opening is deferred to Window 515+." in text
    assert "ADR-0023 Multi-Layer Quality Signal Architecture is a research carry-forward." in text
    assert "Epoch-boundary witness runtime implementation is deferred (`CDL-057` ratified, no ilc_core/ impl in Window 505-514)." in text
    assert "re_admission_boundary CDL-058 opening prerequisites documented in Phase 512." in text
    assert "CDL-053 Werner credit architecture remains reserved and separate." in text
    assert "ADR-0022 private/gated boundary remains separate from validator and epoch-boundary work." in text


def test_live_decision_log_preserves_required_statuses_and_absences() -> None:
    commit_ref = _resolve_phase_513_commit_ref()
    # The Phase-513 CDL-058 absent check is a historical prelock reference.
    rows = parse_decision_register_rows(_commit_text(str(DECISION_LOG_PATH), commit_ref))
    assert rows["CDL-055"]["status"] == "ratified"
    assert rows["CDL-056"]["status"] == "ratified"
    assert rows["CDL-057"]["status"] == "ratified"
    assert "CDL-053" not in rows
    assert "CDL-058" not in rows


def test_head_commit_touches_no_runtime_files() -> None:
    assert_head_commit_touched_no_runtime_files(commit_ref=_resolve_phase_513_commit_ref())


def test_phase_513_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_513_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_513_main_commit_does_not_touch_cdl_log_or_ilc_core() -> None:
    commit_ref = _resolve_phase_513_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith("ilc_core/") for path in changed_paths)
