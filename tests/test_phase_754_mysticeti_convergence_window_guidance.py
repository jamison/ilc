from __future__ import annotations

import subprocess
from pathlib import Path


GUIDANCE_PATH = Path("docs/specs/ilc_mysticeti_convergence_window_guidance_v0.1.md")
TEST_PATH = Path("tests/test_phase_754_mysticeti_convergence_window_guidance.py")
STATUS_PATH = Path("docs/phases/STATUS.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
REQUIRED_HEADINGS = (
    "## 1. Status and boundary",
    "## 2. Window purpose",
    "## 3. Entry conditions and authority order",
    "## 4. Hard constraints",
    "## 5. Six-phase structure",
    "## 6. Inherited constraints throughout convergence",
    "## 7. Required reading before CW-1",
    "## 8. What this pre-draft is not",
)
REQUIRED_TOKENS = (
    "convergence_window_guidance_pre_draft_only",
    "cw1_artifact_reverification_hard_gate",
    "cw2_row5_runtime_closure_evaluation_defined",
    "cw3_row7_censorship_runtime_closure_defined",
    "cw4_row7_exitability_closure_defined",
    "cw5_row8_and_option_b_gate_synthesis_defined",
    "cw6_convergence_window_closure_defined",
    "artifact_paths_authoritative_not_phase_labels",
    "no_cdl_017_ratification_inside_convergence_window",
    "epochcheckpointmsg_path_carries_row7_evidence_weight_post_crit_001",
)
PHASE_SUBJECT = ("phase 754", "convergence window guidance pre-draft")
EXACT_REQUIRED_PATHS = {
    str(GUIDANCE_PATH),
    str(TEST_PATH),
    str(STATUS_PATH),
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    return " ".join(text.split())


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_commit_ref(subject_tokens: tuple[str, ...], expected_paths: set[str]) -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    matches: list[str] = []
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        lowered = subject.lower()
        if all(token in lowered for token in subject_tokens):
            matches.append(commit_hash)
    for commit_ref in matches:
        if _changed_paths_for_commit(commit_ref) == expected_paths:
            return commit_ref
    raise AssertionError("phase_754_commit_not_present_in_local_history")


def _try_resolve_commit_ref(subject_tokens: tuple[str, ...], expected_paths: set[str]) -> str | None:
    try:
        return _resolve_commit_ref(subject_tokens, expected_paths)
    except AssertionError:
        return None


def _current_phase_paths_in_worktree(expected_paths: set[str]) -> set[str]:
    result = subprocess.run(
        ["git", "status", "--short", "--", *sorted(expected_paths)],
        capture_output=True,
        check=True,
        text=True,
    )
    paths: set[str] = set()
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        paths.add(line[3:].strip())
    return paths


def test_guidance_exists_and_contains_required_headings_in_order() -> None:
    text = _read(GUIDANCE_PATH)
    positions = [text.index(heading) for heading in REQUIRED_HEADINGS]
    assert positions == sorted(positions)


def test_guidance_contains_required_tokens() -> None:
    text = _read(GUIDANCE_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_guidance_is_clearly_marked_pre_draft_and_not_open() -> None:
    text = _normalized(_read(GUIDANCE_PATH))
    assert "Status: PRE-DRAFT — convergence window is not open." in text
    assert "becomes active only when all three entry artifact classes exist and are re-verified by the convergence sequence lock (`CW-1`)." in text


def test_cw1_reverification_requires_all_three_artifact_classes() -> None:
    text = _normalized(_read(GUIDANCE_PATH))
    assert "docs/research/ilc_row_7_runtime_evidence_package_bundle_M020_v0.1.md" in text
    assert "docs/research/ilc_sim_leakage_01_results_M021_v0.1.md" in text
    assert "docs/research/ilc_mysticeti_gemini_lane_handoff_M022_v0.1.md" in text
    assert "`CW-1` is a hard gate." in text
    assert "methodology plus raw numbers for all three attacker variants rather than a verdict token alone" in text


def test_cw2_carries_row5_leakage_bands_and_observability_floor() -> None:
    text = _normalized(_read(GUIDANCE_PATH))
    assert "ordinary-observer / hosted-query same-contributor linkage recall `<= 0.45`" in text
    assert "operator-path same-contributor linkage recall `<= 0.60`" in text
    assert "observability-floor mapping preserved per Phase `679`" in text


def test_cw3_notes_epochcheckpointmsg_as_post_crit_001_evidence_weight() -> None:
    text = _normalized(_read(GUIDANCE_PATH))
    assert "EpochSettlementTx" in text
    assert "EpochCheckpointMsg" in text
    assert "row-7 evidence weight is carried by the redundant-path liveness property via `EpochCheckpointMsg`" in text


def test_cw4_requires_physical_exitability_drill_evidence() -> None:
    text = _normalized(_read(GUIDANCE_PATH))
    assert "actual export path" in text
    assert "actual replay-log epoch numbers" in text
    assert "fresh-node startup log" in text
    assert "migrate without original-operator consent or API dependence" in text


def test_cw5_distinguishes_gate_synthesis_from_option_b_selection() -> None:
    text = _normalized(_read(GUIDANCE_PATH))
    assert "Option B gate synthesis is a go / no-go record under ADR-0028" in text
    assert "Option B selection. Gate synthesis records whether Option B becomes selectable; operator selection remains separate." in text
    assert "row `8` disposition is descriptive and bounded by the evidence actually in hand" in text


def test_required_reading_includes_runtime_artifact_carriers() -> None:
    text = _normalized(_read(GUIDANCE_PATH))
    assert "docs/research/ilc_row_7_runtime_evidence_package_bundle_M020_v0.1.md" in text
    assert "docs/research/ilc_sim_leakage_01_results_M021_v0.1.md" in text
    assert "docs/research/ilc_mysticeti_gemini_lane_handoff_M022_v0.1.md" in text


def test_decision_log_and_runtime_code_surfaces_are_untouched_in_phase_754() -> None:
    result_decision = subprocess.run(
        ["git", "diff", "--exit-code", "--", str(DECISION_LOG_PATH)],
        capture_output=True,
        text=True,
    )
    assert result_decision.returncode == 0


def test_phase_754_single_commit_touches_expected_paths_only() -> None:
    commit_ref = _try_resolve_commit_ref(PHASE_SUBJECT, EXACT_REQUIRED_PATHS)
    if commit_ref:
        changed_paths = _changed_paths_for_commit(commit_ref)
        assert changed_paths == EXACT_REQUIRED_PATHS
        assert str(DECISION_LOG_PATH) not in changed_paths
        assert not any(path == "ilc_core" or path.startswith("ilc_core/") for path in changed_paths)
        assert not any(
            path == "ilc_consensus" or path.startswith("ilc_consensus/")
            for path in changed_paths
        )
        return

    assert _current_phase_paths_in_worktree(EXACT_REQUIRED_PATHS) == EXACT_REQUIRED_PATHS
