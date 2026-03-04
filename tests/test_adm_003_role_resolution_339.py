from __future__ import annotations

import subprocess
from pathlib import Path


ARTIFACT_PATH = Path("docs/specs/ilc_adm_003_reference_agent_architecture_v0.1.md")
DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
PHASE_339_COMMIT_SUBJECT = "docs(g8): phase 339 adm-003 role resolution"


def _read() -> str:
    return ARTIFACT_PATH.read_text(encoding="utf-8")


def _read_phase_339_artifact_text() -> str:
    return subprocess.run(
        ["git", "show", f"{_resolve_phase_339_commit_ref()}:{ARTIFACT_PATH.as_posix()}"],
        capture_output=True,
        check=True,
        text=True,
    ).stdout


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_339_commit_ref() -> str:
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
        if subject.strip() == PHASE_339_COMMIT_SUBJECT:
            matching_commits.append(commit_hash)

    required_paths = {
        str(ARTIFACT_PATH),
        "tests/test_adm_003_role_resolution_339.py",
    }
    for commit_ref in matching_commits:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_339_commit_subject_present_but_no_qualifying_role_resolution_commit")
    raise AssertionError("phase_339_commit_not_present_in_local_history")


def test_original_headings_are_preserved() -> None:
    text = _read()
    for heading in (
        "## 1. Purpose and scope",
        "## 2. Architecture layers and responsibilities",
        "## 3. Signing and key-isolation boundaries",
        "## 4. Protocol/SDK/runtime dependency map",
        "## 5. Security and privacy invariants",
        "## 6. Non-goals and phased rollout",
        "## 7. Canonical anchors",
    ):
        assert heading in text


# The Phase-339 ADM-003 role split is a historical prelock reference.
def test_role_split_tokens_are_present() -> None:
    historical_text = _read_phase_339_artifact_text()
    for token in (
        "Evaluation Panel Member",
        "Graph Observation / Schema Evolution Analyst",
        "The 7+1 evaluation panel is case-evaluation infrastructure, not a standing constitutional authority.",
        "Evaluation Panel Member evaluates task outputs, decomposition validity, and ILC attribution; it does not continuously survey the whole graph.",
        "Graph Observation / Schema Evolution Analyst monitors public-graph patterns, surfaces candidate field-elevation proposals, and publishes evidence summaries for governance lanes; it does not directly ratify schema changes.",
    ):
        assert token in historical_text


# The Phase-339 ADM-003 role split is a historical prelock reference.
def test_governance_boundary_and_authorization_tokens_are_present() -> None:
    historical_text = _read_phase_339_artifact_text()
    for token in (
        "Continuous graph observation and schema-evolution preparation are analytics/governance-preparation functions, not ratification authority.",
        "ADM-003 defines role boundaries; a separate governance artifact defines schema-evolution workflow.",
        "The graph-observation role may prepare evidence summaries for future CDL lanes but may not open or ratify CDL rows by itself.",
        "Schema changes still require CDL opening, evidence prelock, ratification, and closure-gate process.",
        "This role resolution authorizes Window 340-344 schema-opening work but does not itself open a CDL row.",
        "Custom-field elevation and validation-lifecycle governance remain blocked until this role split is explicit.",
        "Private or semi-private graph activity is not sufficient input for schema-elevation monitoring; the graph-observation role monitors public-graph patterns only.",
    ):
        assert token in historical_text


def test_phase_292_boundary_invariants_are_preserved() -> None:
    text = _read().lower()
    assert "wallet-agnostic signing is mandatory" in text
    assert "kid values are opaque routing identifiers only" in text
    assert "no runtime changes in `ilc_core/`" in text
    assert "no mutation of `docs/specs/ilc_constitutional_decision_log_v0.1.md`" in text
    for token in (
        "docs/specs/ilc_phase_348_357_sequence_lock_v0.1.md",
        "docs/specs/ilc_integration_coherence_report_336_v0.1.md",
        "docs/specs/ilc_antigravity_context_capsule_v0.9.md",
        "docs/specs/ilc_reputation_and_agent_profile_adjoint_contract_345_v0.1.md",
    ):
        assert token in text


def test_no_decision_log_mutation_in_phase_339_commit() -> None:
    commit_ref = _resolve_phase_339_commit_ref()
    changed = _changed_paths_for_commit(commit_ref)
    assert DECISION_LOG_PATH not in changed


def test_no_ilc_core_runtime_mutation_in_phase_339_commit() -> None:
    commit_ref = _resolve_phase_339_commit_ref()
    changed = _changed_paths_for_commit(commit_ref)
    forbidden = [path for path in changed if path.startswith("ilc_core/")]
    assert not forbidden, f"phase_339_runtime_mutations:{forbidden}"
