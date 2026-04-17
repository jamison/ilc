from __future__ import annotations

import subprocess
from pathlib import Path


GOV_PATH = Path("docs/specs/ilc_governance_minimization_inventory_and_sunset_taxonomy_708_v0.1.md")
ADR_PATH = Path("docs/specs/ilc_adr_0019_governance_compilation_boundary_disposition_708_v0.1.md")
EVIDENCE_PATH = Path(
    "docs/specs/ilc_cdl_066_agent_sender_authorization_ratification_evidence_708_v0.1.md"
)
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
TEST_PATH = Path("tests/test_phase_708_governance_minimization_inventory_and_cdl_066_ratification.py")
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_708_g8_governance_minimization_inventory_adr_0019_and_cdl_066_ratification_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")

REQUIRED_GOV_HEADINGS = (
    "## 1. Inventory target and inherited boundary",
    "## 2. Governance lever taxonomy",
    "## 3. Sunset logic and observable triggers",
    "## 4. Surfaces explicitly kept outside graph-native governance",
    "## 5. Carry-forward implications",
)
REQUIRED_GOV_TOKENS = (
    "governance_minimization_inventory_published",
    "graph_native_governance_surfaces_classified",
    "bootstrap_safety_steward_forbidden_manual_taxonomy_locked",
    "sunset_expectations_require_observable_trigger_logic",
    "rhetorical_governance_claims_do_not_create_runtime_law",
)
REQUIRED_ADR_HEADINGS = (
    "## 1. Inherited ADR statement",
    "## 2. Explanatory framing that remains explanatory",
    "## 3. Surfaces promoted to active planning / spec boundary",
    "## 4. Boundary preserved in current window",
    "## 5. Explicit non-goals",
)
REQUIRED_ADR_TOKENS = (
    "adr_0019_disposition_published",
    "adr_0019_explanatory_boundary_preserved",
    "bounded_graph_compilation_surfaces_remain_preferred_direction",
    "compiled_artifacts_not_raw_nodes_feed_runtime",
    "governance_compilation_boundary_remains_explicit",
)
REQUIRED_EVIDENCE_HEADINGS = (
    "## 1. Evidence basis",
    "## 2. Narrow ratified rule",
    "## 3. Implementation closure and runtime basis",
    "## 4. Preserved exclusions and orthogonality",
    "## 5. Decision-log consequence",
)
REQUIRED_EVIDENCE_TOKENS = (
    "cdl_066_ratified_narrow_sender_authorization_lane",
    "sec_001_implementation_closed_before_cdl_066_ratification",
    "sender_auth_verification_precedes_quorum_and_execution",
    "cdl_066_remains_orthogonal_to_cdl_017_and_cdl_039",
    "cdl_066_does_not_broaden_into_generalized_transfer_redesign",
)
PHASE_MAIN_SUBJECT = ("phase 708", "governance minimization", "cdl-066 ratification")
PHASE_BACKFILL_SUBJECT = ("phase 708", "walkthrough", "backfill")
EXACT_REQUIRED_MAIN_PATHS = {
    str(GOV_PATH),
    str(ADR_PATH),
    str(EVIDENCE_PATH),
    str(DECISION_LOG_PATH),
    str(TEST_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}


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
    raise AssertionError("phase_708_commit_not_present_in_local_history")


def test_governance_inventory_contains_required_headings_and_tokens() -> None:
    text = _read(GOV_PATH)
    for heading in REQUIRED_GOV_HEADINGS:
        assert heading in text
    for token in REQUIRED_GOV_TOKENS:
        assert token in text


def test_governance_inventory_records_taxonomy_and_sunset_logic() -> None:
    text = _read(GOV_PATH)
    assert "### 2.1 Bootstrap-only surfaces" in text
    assert "### 2.2 Safety-only surfaces" in text
    assert "### 2.3 Steward / infrastructure continuity surfaces" in text
    assert "### 2.4 Forbidden / manual surfaces" in text
    assert "ratified CDL replacement" in text
    assert "Unacceptable triggers include:" in text


def test_adr_disposition_contains_required_headings_and_tokens() -> None:
    text = _read(ADR_PATH)
    for heading in REQUIRED_ADR_HEADINGS:
        assert heading in text
    for token in REQUIRED_ADR_TOKENS:
        assert token in text


def test_adr_disposition_preserves_boundary_and_non_goals() -> None:
    text = _read(ADR_PATH)
    assert "kernel-resident:" in text
    assert "graph-compilation candidates:" in text
    assert "unrestricted executable code loaded from governance nodes" in text
    assert "automatic runtime self-modification" in text


def test_cdl_066_ratification_evidence_contains_required_headings_and_tokens() -> None:
    text = _read(EVIDENCE_PATH)
    for heading in REQUIRED_EVIDENCE_HEADINGS:
        assert heading in text
    for token in REQUIRED_EVIDENCE_TOKENS:
        assert token in text


def test_cdl_066_ratification_stays_narrow_and_decision_log_marks_ratified() -> None:
    text = _read(EVIDENCE_PATH)
    assert "fast-path ECU transfers require sender authorization" in text
    assert "`CDL-017` validator admission / ejection governance" in text
    assert "`CDL-039` transport invariants and topology privacy" in text
    log_text = _read(DECISION_LOG_PATH)
    line = next(line for line in log_text.splitlines() if line.startswith("| CDL-066 |"))
    assert "| ratified |" in line
    assert "ratified_phase: 708" in line
    assert (
        "evidence_document: docs/specs/ilc_cdl_066_agent_sender_authorization_ratification_evidence_708_v0.1.md"
        in line
    )


def test_phase_708_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_MAIN_SUBJECT, EXACT_REQUIRED_MAIN_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_708_backfill_commit_touches_walkthrough_and_status_only() -> None:
    commit_ref = _resolve_commit_ref(PHASE_BACKFILL_SUBJECT, EXACT_REQUIRED_BACKFILL_PATHS)
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS
