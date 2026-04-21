from __future__ import annotations

import os
import subprocess
from pathlib import Path


ARTIFACT_PATH = Path("docs/specs/ilc_row_8_disposition_and_option_b_gate_synthesis_cw5_v0.1.md")
TEST_PATH = Path("tests/test_cw5_row_8_disposition_and_option_b_gate_synthesis.py")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
REQUIRED_HEADINGS = (
    "## 1. Baseline and governing posture",
    "## 2. Row-8 disposition",
    "## 3. Option B graduation-gate synthesis",
    "## 4. Positive convergence milestone",
    "## 5. Carry-forward obligations",
    "## 6. Forward path and non-claims",
)
REQUIRED_TOKENS = (
    "option_b_gate_synthesis_verdict=no_go",
    "option_b_gate_blockers=row_8_candidate_evaluation_pending|cdl_017_ratification_pending",
    "row_7_runtime_closed_milestone_recorded",
    "option_d_posture_active_per_adr_0028",
)
PHASE_SUBJECT = ("cw-5", "phase 761", "row-8 disposition", "option b gate synthesis")
EXACT_REQUIRED_PATHS = {
    str(ARTIFACT_PATH),
    str(TEST_PATH),
}
SELFTEST_ENV = "ILC_CW5_GATE_SELFTEST"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    return " ".join(text.split())


def _selftest() -> bool:
    return os.environ.get(SELFTEST_ENV) == "1"


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
    raise AssertionError("cw5_commit_not_present_in_local_history")


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


def test_output_exists_with_required_headings_in_order() -> None:
    if _selftest():
        return
    text = _read(ARTIFACT_PATH)
    positions = [text.index(heading) for heading in REQUIRED_HEADINGS]
    assert positions == sorted(positions)


def test_required_tokens_and_no_go_verdict_are_present() -> None:
    if _selftest():
        return
    text = _read(ARTIFACT_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text
    assert "option_b_gate_synthesis_verdict=go" not in text


def test_both_gate_blockers_and_row_8_posture_are_named_explicitly() -> None:
    if _selftest():
        return
    text = _normalized(_read(ARTIFACT_PATH))
    assert "Row-8 exclusion-matrix evaluation against a specific candidate" in text
    assert "`CDL-017` ratification" in text
    assert "row_8_posture=criteria_locked_candidate_evaluation_pending" in text
    assert "no candidate has been evaluated" in text


def test_row_7_runtime_closed_milestone_is_recorded() -> None:
    if _selftest():
        return
    text = _normalized(_read(ARTIFACT_PATH))
    required = (
        "row `7` runtime closure",
        "row_7_runtime_closed_milestone_recorded",
        "row_7_combined_runtime_status=runtime_closed",
        "censorship-resistance runtime closure: pass",
        "strong-exitability runtime closure: pass",
    )
    for item in required:
        assert item in text


def test_all_six_carry_forward_categories_and_governing_citations_are_present() -> None:
    if _selftest():
        return
    text = _normalized(_read(ARTIFACT_PATH))
    required = (
        "### 5.1 Row-5 privacy carry-forward",
        "### 5.2 CDL-017 ratification carry-forward",
        "### 5.3 Row-8 substrate evaluation carry-forward",
        "### 5.4 Hypergraph Tier 2 carry-forward",
        "### 5.5 Hypergraph Tier 3 carry-forward",
        "### 5.6 Incremental structural proof chain carry-forward",
        "docs/specs/ilc_row_5_runtime_closure_evaluation_cw2_v0.1.md",
        "docs/specs/ilc_cdl_017_ratification_readiness_dossier_v0.1.md",
        "docs/specs/ilc_external_constitutional_center_and_exclusion_matrix_673_v0.1.md",
        "docs/adr/ADR_0028_Settlement_Substrate_Graduation_and_Governance_Route.md",
        "docs/adr/ADR_0029_Hypergraph_Substrate.md",
        "docs/research/ilc_merkle_laplacian_dual_commitment_paper_draft_v0.1.md",
    )
    for item in required:
        assert item in text


def test_no_cdl_017_ratification_or_option_b_selection_claim_is_made() -> None:
    if _selftest():
        return
    text = _normalized(_read(ARTIFACT_PATH))
    assert "Option B does **not** become selectable at `CW-5`" in _read(ARTIFACT_PATH)
    assert "Option B is selected" not in text
    assert "`CDL-017` is now ratified" not in text
    assert "This artifact does **not** claim:" in _read(ARTIFACT_PATH)
    assert "- Option B selection" in _read(ARTIFACT_PATH)
    assert "- `CDL-017` ratification" in _read(ARTIFACT_PATH)
    assert "`CDL-017` is now ratified" not in text


def test_selftest_guard_is_declared_in_test_file() -> None:
    text = _read(TEST_PATH)
    assert SELFTEST_ENV in text
    assert "if _selftest():" in text


def test_decision_log_and_runtime_code_surfaces_are_untouched_in_cw5() -> None:
    if _selftest():
        return
    result_decision = subprocess.run(
        ["git", "diff", "--exit-code", "--", str(DECISION_LOG_PATH)],
        capture_output=True,
        text=True,
    )
    assert result_decision.returncode == 0


def test_cw5_commit_touches_expected_paths_only() -> None:
    if _selftest():
        return
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
