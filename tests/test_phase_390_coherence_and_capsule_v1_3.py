"""Contract tests for Phase 390 coherence and capsule v1.3 artifact set."""

from __future__ import annotations

from pathlib import Path
import subprocess


COHERENCE_PATH = Path("docs/specs/ilc_integration_coherence_report_390_v0.1.md")
CAPSULE_PATH = Path("docs/specs/ilc_antigravity_context_capsule_v1.3.md")
DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
SUBJECT_TOKEN = "docs(g8): phase 390 coherence and capsule v1.3"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_coherence_artifact_exists_with_required_headings() -> None:
    assert COHERENCE_PATH.exists()
    text = _read(COHERENCE_PATH)
    for heading in (
        "## 1. Scope and non-ratifying boundary",
        "## 2. CDL-039 ratification and hardening closure",
        "## 3. D2d runtime implementation state",
        "## 4. CDL-040/041/043 prelock state and ratification boundary",
        "## 5. SIM-006/007 governance evidence state",
        "## 6. CDL-V1/V2 runtime implementation state",
        "## 7. CDL-V3/V7 declaration and Window 392+ forward boundary",
        "## 8. Non-goals and canonical anchors",
    ):
        assert heading in text


def test_coherence_contains_required_tokens_and_coverage() -> None:
    text = _read(COHERENCE_PATH)
    for token in (
        "CDL-039 ratification created a named forward obligation: retention_epochs operational value requires a subsequent CDL amendment before deployment. This amendment must be opened as the first constitutional action of Window 392+.",
        "No decision-log mutation occurred. No ilc_core runtime files were changed.",
        "CDL-036 header-field reconciliation is in effect",
        "four-prelock hardening chain (`359`, `372`, `373`, `374`)",
        "ilc_core/network/d2d/",
        "CDL-V1 temporal decay runtime implemented",
        "CDL-V2 sybil-resistance runtime implemented",
    ):
        assert token in text


def test_capsule_v1_3_exists_self_contained_and_supersedes_v1_2() -> None:
    assert CAPSULE_PATH.exists()
    text = _read(CAPSULE_PATH)
    assert "Supersedes: docs/specs/ilc_antigravity_context_capsule_v1.2.md" in text
    assert "This capsule is self-contained." in text
    for heading in (
        "## 1. Project identity",
        "## 2. Core architectural invariants",
        "## 3. Project state (as of Phase 390 completion)",
        "## 4. CDL-039 ratification and carry-forward obligation state",
        "## 5. D2d runtime enforcement state",
        "## 6. CDL-040/041/043 prelock state",
        "## 7. V-series runtime state",
        "## 8. CDL-V3/V7 governance state",
        "## 9. Window 392+ forward boundary",
        "## 10. Change log from v1.2",
        "## 11. Key canonical anchors",
    ):
        assert heading in text


def test_capsule_contains_required_state_and_boundary_tokens() -> None:
    text = _read(CAPSULE_PATH)
    for token in (
        "CDL-039 is ratified as of Phase 379 with calibration constants locked.",
        "CDL-039 ratification forward obligation: retention_epochs requires a named CDL amendment to be opened as the first constitutional action of Window 392+.",
        "D2d wire protocol is implemented in ilc_core/network/d2d/ and enforces CDL-039 transport invariants.",
        "CDL-V1 temporal decay and CDL-V2 sybil resistance are computationally enforced as of Phases 388/389.",
        "CDL-040/041/043 prelocks are complete and non-ratifying; ratification is deferred to Window 392+.",
        "CDL-V3 and CDL-V7 governance resolution: deferred to Window 392+.",
    ):
        assert token in text


def test_coherence_and_capsule_include_d2d_and_v_series_runtime_state() -> None:
    coherence = _read(COHERENCE_PATH)
    capsule = _read(CAPSULE_PATH)
    assert "`interface.py` (Phase 380)" in coherence
    assert "`peer.py` (Phase 381)" in coherence
    assert "`gossip.py` (Phase 382)" in coherence
    assert "CDL_V1_DEPENDENCY = \"cdl_v1_temporal_decay_388.v0.1\"" in coherence
    assert "CDL_V2_DEPENDENCY = \"cdl_v2_sybil_resistance_389.v0.1\"" in coherence
    assert "ilc_core/reputation/temporal_decay_runtime.py" in capsule
    assert "ilc_core/identity/sybil_resistance_runtime.py" in capsule


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_390_commit_ref_or_fail() -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    matching_commits: list[str] = []
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if subject.strip().lower() == SUBJECT_TOKEN.lower():
            matching_commits.append(commit_hash)

    required_paths = {
        "docs/specs/ilc_integration_coherence_report_390_v0.1.md",
        "docs/specs/ilc_antigravity_context_capsule_v1.3.md",
        "tests/test_phase_390_coherence_and_capsule_v1_3.py",
    }
    for commit_ref in matching_commits:
        changed = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed):
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_390_commit_subject_present_but_no_qualifying_coherence_commit")
    raise AssertionError("phase_390_commit_not_present_in_local_history")


def test_phase_390_commit_touched_required_paths_and_not_decision_log() -> None:
    commit_ref = _resolve_phase_390_commit_ref_or_fail()
    changed = _changed_paths_for_commit(commit_ref)
    assert DECISION_LOG_PATH not in changed


def test_phase_390_commit_touched_no_ilc_core_paths() -> None:
    commit_ref = _resolve_phase_390_commit_ref_or_fail()
    changed = _changed_paths_for_commit(commit_ref)
    forbidden = [path for path in changed if path.startswith("ilc_core/")]
    assert not forbidden, f"phase_390_runtime_mutations:{forbidden}"
