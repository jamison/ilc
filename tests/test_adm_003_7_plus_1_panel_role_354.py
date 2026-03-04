from __future__ import annotations

import subprocess
from pathlib import Path


ARTIFACT_PATH = Path("docs/specs/ilc_adm_003_reference_agent_architecture_v0.1.md")
PHASE_339_TEST_PATH = Path("tests/test_adm_003_role_resolution_339.py")
DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
PHASE_354_COMMIT_SUBJECT = "docs(g8): phase 354 adm-003 7 plus 1 panel role resolution"


def _read_artifact() -> str:
    return ARTIFACT_PATH.read_text(encoding="utf-8")


def _read_phase_339_test_source() -> str:
    return PHASE_339_TEST_PATH.read_text(encoding="utf-8")


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_354_commit_ref() -> str:
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
        if subject.strip() == PHASE_354_COMMIT_SUBJECT:
            matches.append(commit_hash)

    required_paths = {
        str(ARTIFACT_PATH),
        str(PHASE_339_TEST_PATH),
        "tests/test_adm_003_7_plus_1_panel_role_354.py",
    }
    for commit_ref in matches:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref

    if matches:
        raise AssertionError("phase_354_commit_subject_present_but_no_qualifying_role_resolution_commit")
    raise AssertionError("phase_354_commit_not_present_in_local_history")


def test_phase_339_historical_prelock_hardening_patch_is_active() -> None:
    text = _read_phase_339_test_source()
    assert "# The Phase-339 ADM-003 role split is a historical prelock reference." in text
    assert "def _read_phase_339_artifact_text() -> str:" in text
    assert 'historical_text = _read_phase_339_artifact_text()' in text
    assert 'def test_phase_292_boundary_invariants_are_preserved() -> None:' in text
    assert 'text = _read().lower()' in text


def test_live_artifact_contains_panel_architecture_and_governance_boundary_tokens() -> None:
    text = _read_artifact()
    for token in (
        "## 1. Purpose and scope",
        "## 2. Architecture layers and responsibilities",
        "## 3. Signing and key-isolation boundaries",
        "## 4. Protocol/SDK/runtime dependency map",
        "## 5. Security and privacy invariants",
        "## 6. Non-goals and phased rollout",
        "## 7. Canonical anchors",
        "7+1 evaluation panel",
        "panel_size=8",
        "independence_k=3",
        "outsider_seat=true",
        "Quorum: k=5 of m=7 reviewers with VRF-selected outsider seat",
        "VRF-selected outsider seat is the anti-capture mechanism",
        "trust-tier quorum ladder: L0=3, L1=5, L2=7, L3=9, appeals escalate by +2",
        "CDL-V3 cluster diversity floor operationalizes independence_k=3",
        "CDL-V7 Popperian gate is the test specification; the 7+1 panel is the testing mechanism",
        "L0=3 is architecturally safe because CDL-V7's Popperian gate ensures L0 basic statements are independently and directly verifiable.",
        "The quorum ladder L-tiers correspond to graph epistemic tiers, not protocol/genesis-layer authority tiers and not agent reputation tiers.",
        "The 7+1 panel quorum mechanism governs knowledge claim evaluation for task outputs, decomposition validity, and ILC attribution; it does not govern constitutional or genesis-layer protocol changes.",
        "Evaluation Panel Member",
        "Graph Observation / Schema Evolution Analyst",
        "The 7+1 evaluation panel is case-evaluation infrastructure, not a standing constitutional authority.",
        "Continuous graph observation and schema-evolution preparation are analytics/governance-preparation functions, not ratification authority.",
        "ADM-003 defines role boundaries; a separate governance artifact defines schema-evolution workflow.",
        "The graph-observation role may prepare evidence summaries for future CDL lanes but may not open or ratify CDL rows by itself.",
        "Schema changes still require CDL opening, evidence prelock, ratification, and closure-gate process.",
    ):
        assert token in text


def test_live_artifact_preserves_phase_292_boundaries_and_canonical_anchors() -> None:
    text = _read_artifact().lower()
    for token in (
        "wallet-agnostic signing is mandatory",
        "kid values are opaque routing identifiers only",
        "no runtime changes in `ilc_core/`",
        "no mutation of `docs/specs/ilc_constitutional_decision_log_v0.1.md`",
        "docs/specs/ilc_adm_001_protocol_native_bundle_distribution_v0.2.md",
        "docs/specs/ilc_antigravity_context_capsule_v0.9.md",
        "docs/specs/ilc_integration_coherence_report_336_v0.1.md",
        "docs/specs/ilc_reputation_and_agent_profile_adjoint_contract_345_v0.1.md",
    ):
        assert token in text


def test_live_artifact_keeps_implementation_authorization_boundary() -> None:
    text = _read_artifact()
    assert "This Phase-354 role resolution remains a prerequisite for Window-358+ implementation authorization; it does not itself authorize implementation." in text
    assert "no implementation authorization in this phase." in text
    assert "implementation remains deferred until Window 357 closure and explicit Window 358+ authorization" in text


def test_no_decision_log_mutation_in_phase_354_commit() -> None:
    commit_ref = _resolve_phase_354_commit_ref()
    changed = _changed_paths_for_commit(commit_ref)
    assert DECISION_LOG_PATH not in changed


def test_no_ilc_core_runtime_mutation_in_phase_354_commit() -> None:
    commit_ref = _resolve_phase_354_commit_ref()
    changed = _changed_paths_for_commit(commit_ref)
    forbidden = [path for path in changed if path.startswith("ilc_core/")]
    assert not forbidden, f"phase_354_runtime_mutations:{forbidden}"
