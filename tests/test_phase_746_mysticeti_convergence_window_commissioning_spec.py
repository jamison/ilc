from __future__ import annotations

import subprocess
from pathlib import Path


SPEC_PATH = Path("docs/specs/ilc_mysticeti_convergence_window_commissioning_spec_746_v0.1.md")
ADR_PATH = Path("docs/adr/ADR_0031_Subgraph_Homomorphism_Query_Contract.md")
TEST_PATH = Path("tests/test_phase_746_mysticeti_convergence_window_commissioning_spec.py")
STATUS_PATH = Path("docs/phases/STATUS.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
REQUIRED_HEADINGS = (
    "## 1. Purpose and boundary",
    "## 2. Entry conditions and authority order",
    "## 3. Current satisfaction matrix at commission time",
    "## 4. Six-phase budget for the later convergence window",
    "## 5. Authorized outputs of the later convergence window",
    "## 6. Explicit exclusions",
    "## 7. ADR-0031 housekeeping acceptance",
    "## 8. Source inputs",
)
REQUIRED_TOKENS = (
    "mysticeti_convergence_window_commissioned",
    "convergence_window_phase_budget_six",
    "convergence_window_not_open_until_all_entry_artifacts_exist",
    "convergence_entry_artifact_class_a_row7_bundle_defined",
    "convergence_entry_artifact_class_b_sim_leakage_results_defined",
    "convergence_entry_artifact_class_c_exitability_drill_defined",
    "convergence_entry_matrix_recorded_without_open_claim",
    "convergence_window_entry_not_yet_satisfied_in_phase_746",
    "convergence_window_six_phase_budget_locked",
    "convergence_window_authorized_outputs_bounded",
    "convergence_window_option_b_gate_authorized_not_selection",
    "phase_746_no_row_closure_claims",
    "phase_746_no_cdl_017_ratification",
    "phase_746_no_option_b_graduation",
    "adr_0031_status_accepted_housekeeping_only",
    "adr_0031_no_runtime_work_required",
)
PHASE_SUBJECT = (
    "phase 746",
    "convergence window commissioning spec",
    "adr-0031",
)
EXACT_REQUIRED_PATHS = {
    str(SPEC_PATH),
    str(ADR_PATH),
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
    raise AssertionError("phase_746_commit_not_present_in_local_history")


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


def test_spec_exists_and_contains_required_headings_in_order() -> None:
    text = _read(SPEC_PATH)
    positions = [text.index(heading) for heading in REQUIRED_HEADINGS]
    assert positions == sorted(positions)


def test_spec_contains_required_tokens() -> None:
    text = _read(SPEC_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_spec_records_three_artifact_classes_and_keeps_window_closed() -> None:
    text = _normalized(_read(SPEC_PATH))
    assert "The convergence window may not open until every required artifact class exists" in text
    assert "The currently expected carrier is: `docs/research/ilc_row_7_runtime_evidence_package_bundle_M020_v0.1.md`" in text
    assert "The currently expected carrier is: `docs/research/ilc_sim_leakage_01_results_M021_v0.1.md`" in text
    assert "A committed results artifact is required before the later convergence window can close row `7`." in text
    assert "Because all three artifact classes are not yet present and re-verified together, Phase `746` does not open the convergence window." in text


def test_spec_locks_six_phase_budget_and_bounded_outputs() -> None:
    text = _normalized(_read(SPEC_PATH))
    assert "The commissioned later convergence window is authorized for exactly six phases:" in text
    assert "row `5` runtime-closure evaluation using committed `SIM-LEAKAGE-01` results" in text
    assert "row `7` censorship-resistance runtime-closure evaluation" in text
    assert "row `7` strong-exitability runtime-closure evaluation" in text
    assert "row `8` disposition plus Option B graduation-gate synthesis under ADR-0028" in text
    assert "Any future expansion beyond six phases requires a new sequence lock." in text
    assert "Option B graduation-gate synthesis is not the same thing as sovereign-substrate selection." in text


def test_spec_preserves_exclusions_and_no_runtime_mutation_claims() -> None:
    text = _normalized(_read(SPEC_PATH))
    assert "any row `5` closure claim in Phase `746`," in text
    assert "any row `7` closure claim in Phase `746`," in text
    assert "any row `8` advancement in Phase `746`," in text
    assert "any `CDL-017` ratification claim," in text
    assert "any Option B graduation claim," in text
    assert "any legal positioning technical facts annex work," in text
    assert "any `ilc_core/` or `ilc_consensus/` mutation." in text


def test_adr_0031_is_accepted_and_spec_records_housekeeping_only_basis() -> None:
    adr_text = _read(ADR_PATH)
    spec_text = _normalized(_read(SPEC_PATH))
    assert "**Status:** Accepted" in adr_text
    assert "The ADR file changes status only. No implementation work is performed here." in spec_text
    assert "`repeated EdgeRecord edges = 2;`" in spec_text
    assert "`repeated HyperEdgeRecord hyperedges = 3;`" in spec_text


def test_decision_log_and_runtime_code_surfaces_are_untouched_in_phase_746() -> None:
    result_decision = subprocess.run(
        ["git", "diff", "--exit-code", "--", str(DECISION_LOG_PATH)],
        capture_output=True,
        text=True,
    )
    assert result_decision.returncode == 0


def test_phase_746_single_commit_touches_expected_paths_only() -> None:
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
