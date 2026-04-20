from __future__ import annotations

import subprocess
from pathlib import Path


EVIDENCE_PATH = Path("docs/specs/ilc_row_5_runtime_evidence_package_740_v0.1.md")
SIM_SPEC_PATH = Path("docs/specs/ilc_sim_leakage_01_commissioning_spec_740_v0.1.md")
TEST_PATH = Path("tests/test_phase_740_row_5_runtime_evidence_package.py")
STATUS_PATH = Path("docs/phases/STATUS.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
REQUIRED_HEADINGS_EVIDENCE = (
    "## 1. Purpose and inherited authority",
    "## 2. Remaining gap after Phase 697",
    "## 3. Required live evidence for a runtime-closed row-5 verdict",
    "## 4. Required measurement surfaces and attacker mapping",
    "## 5. Observability-floor mapping",
    "## 6. Current status and carry-forward",
)
REQUIRED_HEADINGS_SIM = (
    "## 1. Commission purpose and non-conflation",
    "## 2. Attacker variants and required evidence channels",
    "## 3. Testbed and instrumentation requirements",
    "## 4. Measurement protocol",
    "## 5. Verdict criteria",
    "## 6. Commissioning posture and non-goals",
)
REQUIRED_TOKENS = (
    "row_5_runtime_evidence_package_740_complete",
    "row_5_runtime_closure_requires_dedicated_live_leakage_measurement",
    "phase_679_observability_floor_bound_to_row_5_runtime_evidence",
    "phase_681_attacker_variants_bound_to_row_5_runtime_measurement",
    "phase_682_narrowing_honored_not_blanket_secrecy",
    "sim_leakage_01_commissioned_phase_740",
    "sim_leakage_01_is_dedicated_measurement_not_m019_default_verdict",
    "sim_leakage_01_commissioning_only_not_execution",
    "row_5_status_after_phase_740=spec_closed_runtime_pending",
)
PHASE_MAIN_SUBJECT = (
    "phase 740",
    "row-5 runtime evidence package",
    "sim-leakage-01",
)
EXACT_REQUIRED_MAIN_PATHS = {
    str(EVIDENCE_PATH),
    str(SIM_SPEC_PATH),
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
    raise AssertionError("phase_740_commit_not_present_in_local_history")


def _try_resolve_commit_ref(subject_tokens: tuple[str, ...], expected_paths: set[str]) -> str | None:
    try:
        return _resolve_commit_ref(subject_tokens, expected_paths)
    except AssertionError:
        return None


def test_output_files_exist_and_contain_required_headings() -> None:
    evidence_text = _read(EVIDENCE_PATH)
    sim_text = _read(SIM_SPEC_PATH)
    evidence_positions = [evidence_text.index(heading) for heading in REQUIRED_HEADINGS_EVIDENCE]
    sim_positions = [sim_text.index(heading) for heading in REQUIRED_HEADINGS_SIM]
    assert evidence_positions == sorted(evidence_positions)
    assert sim_positions == sorted(sim_positions)


def test_required_tokens_are_present() -> None:
    text = _read(EVIDENCE_PATH) + _read(SIM_SPEC_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_row_5_evidence_package_references_all_three_phase_681_attacker_variants() -> None:
    text = _normalized(_read(EVIDENCE_PATH))
    assert "operator-path attacker" in text
    assert "hosted-query attacker" in text
    assert "repeated-contributor attacker" in text


def test_sim_leakage_spec_is_explicitly_distinct_from_m019() -> None:
    text = _normalized(_read(SIM_SPEC_PATH))
    assert "This SIM is distinct from Gemini `M-019`." in text
    assert "the default `M-019` pass/fail verdict is not the row-5 artifact" in text


def test_row_5_status_remains_spec_closed_runtime_pending_without_premature_closure_claim() -> None:
    combined = _normalized(_read(EVIDENCE_PATH) + "\n" + _read(SIM_SPEC_PATH) + "\n" + _read(STATUS_PATH))
    assert "row `5` remains `spec_closed_runtime_pending`" in combined
    assert "row `5` to `runtime_closed`" in combined
    assert "This phase does not execute `SIM-LEAKAGE-01`." in combined


def test_observability_floor_connection_is_present() -> None:
    text = _normalized(_read(EVIDENCE_PATH))
    assert "machine-legible receipts" in text
    assert "receipt lineage intact" in text
    assert "challengeability preserved" in text
    assert "bounded human auditability preserved" in text
    assert "must not trade away receipts or lineage" in text


def test_phase_682_narrowing_is_honored_and_blanket_secrecy_is_rejected() -> None:
    combined = _normalized(_read(EVIDENCE_PATH) + "\n" + _read(SIM_SPEC_PATH))
    assert "correlation minimization and unlinkability, not blanket secrecy" in combined
    assert "The following are not required closure evidence in this lane:" in combined
    assert "blanket secrecy for all private work" in combined


def test_hosted_query_variant_allows_surface_absence_record_when_no_query_surface_exists() -> None:
    combined = _normalized(_read(EVIDENCE_PATH) + "\n" + _read(SIM_SPEC_PATH))
    assert "hosted-query surface-absence record" in combined
    assert "absent-at-runtime rather than omitted" in combined
    assert "or an explicit absent-at-runtime disposition with supporting surface audit" in combined


def test_operator_path_threshold_is_kept_as_inherited_stretch_target_language() -> None:
    combined = _normalized(_read(EVIDENCE_PATH) + "\n" + _read(SIM_SPEC_PATH))
    assert "the operator-path band remains the named stretch target from the same packet rather than a historically locked closure minimum" in combined
    assert "inherited `0.60` stretch target from Phase `681`" in combined


def test_commissioning_posture_for_future_run_is_explicit() -> None:
    text = _normalized(_read(SIM_SPEC_PATH))
    assert "This document commissions a future measurement run. It does not claim that the run has already occurred." in text
    assert "sim_leakage_01_execution_not_yet_performed" in text
    assert "Row `5` remains `spec_closed_runtime_pending` until a future execution of `SIM-LEAKAGE-01`" in text


def test_decision_log_ilc_core_and_ilc_consensus_remain_unmutated_in_this_phase() -> None:
    main_commit = _try_resolve_commit_ref(PHASE_MAIN_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    if main_commit:
        changed_paths = _changed_paths_for_commit(main_commit)
        assert str(DECISION_LOG_PATH) not in changed_paths
        assert not any(path == "ilc_core" or path.startswith("ilc_core/") for path in changed_paths)
        assert not any(
            path == "ilc_consensus" or path.startswith("ilc_consensus/")
            for path in changed_paths
        )
        return

    result_decision = subprocess.run(
        ["git", "diff", "--exit-code", "--", str(DECISION_LOG_PATH)],
        capture_output=True,
        text=True,
    )
    assert result_decision.returncode == 0


def test_phase_740_single_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_MAIN_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS
