"""Contract tests for Phase 432 coherence and capsule v1.7 artifact set."""

from __future__ import annotations

from pathlib import Path
import subprocess


COHERENCE_PATH = Path("docs/specs/ilc_integration_coherence_report_432_v0.1.md")
CAPSULE_PATH = Path("docs/specs/ilc_antigravity_context_capsule_v1.7.md")
DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
SUBJECT_TOKEN = "docs(g8): phase 432 coherence and capsule v1.7"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_coherence_artifact_exists_with_required_headings() -> None:
    assert COHERENCE_PATH.exists()
    text = _read(COHERENCE_PATH)
    for heading in (
        "## 1. Scope and non-ratifying boundary",
        "## 2. Constitutional settlement state (CDL-049 and window outcome)",
        "## 3. Treasury P_e branch disposition state",
        "## 4. Runtime and D2e continuity state",
        "## 5. Window-433 closure readiness and Window-434+ obligations",
        "## 6. Non-goals and canonical anchors",
    ):
        assert heading in text


def test_coherence_contains_required_tokens_and_window_434_plus_obligations() -> None:
    text = _read(COHERENCE_PATH)
    for token in (
        "No decision-log mutation occurred. No ilc_core runtime files were changed.",
        "CDL-049 is ratified as of Phase 428 with bounded_existential promoted into the active Popperian runtime and forward-facing analysis corpus.",
        "Phase 431 published the Treasury P_e carry-forward decision under Scenario B with Window 434+ as the default continuation target.",
        "The SIM-009 recommendation pair 0.2 / 0.02 remains a provisional planning anchor only and not a constitutional lock.",
        'D2E_AGENT_CLI_VERSION = "d2e_agent_cli_420.v0.1"',
        'D2E_LIFECYCLE_CLI_VERSION = "d2e_lifecycle_cli_421.v0.1"',
        "Runtime-integrity note: CDL-V1/V2/V3/V7 validators reject non-finite numeric inputs (NaN/Inf).",
        "Wallet-agnostic signing remains mandatory at protocol boundary.",
        "Window 433 is the closure-gate lane for Window 424-433.",
        "Window 434+ obligations include Treasury P_e constitutional advancement only after satisfying at least one Phase 430 or Phase 431 prerequisite, while CDL-050 remains unopened unless a future opening phase explicitly authorizes it.",
    ):
        assert token in text


def test_capsule_v1_7_exists_self_contained_and_supersedes_v1_6() -> None:
    assert CAPSULE_PATH.exists()
    text = _read(CAPSULE_PATH)
    assert "Supersedes: docs/specs/ilc_antigravity_context_capsule_v1.6.md" in text
    assert "This capsule is self-contained." in text
    for heading in (
        "## 1. Project identity",
        "## 2. Core architectural invariants",
        "## 3. Project state (as of Phase 432 completion)",
        "## 4. Constitutional ratification and carry-forward state",
        "## 5. Runtime implementation state",
        "## 6. Treasury P_e branch state",
        "## 7. Wallet-agnostic signing and runtime-integrity continuity",
        "## 8. Window 433 and 434+ forward boundary",
        "## 9. Change log from v1.6",
        "## 10. Key canonical anchors",
    ):
        assert heading in text


def test_capsule_contains_required_state_and_forward_boundary_tokens() -> None:
    text = _read(CAPSULE_PATH)
    for token in (
        "CDL-047, CDL-048, and CDL-049 are ratified in the current constitutional register.",
        "Treasury P_e constitutional lane carries into Window 434+ with provisional planning anchor 0.2 / 0.02 and no locked P_e constants.",
        "The active Popperian runtime and forward-facing analysis corpus now use bounded_existential as the admitted bounded claim-form token.",
        'D2E_AGENT_CLI_VERSION = "d2e_agent_cli_420.v0.1"',
        'D2E_LIFECYCLE_CLI_VERSION = "d2e_lifecycle_cli_421.v0.1"',
        "Runtime-integrity note: V-series validators reject non-finite numeric inputs (NaN/Inf).",
        "Wallet-agnostic signing remains mandatory: signer-lineage lifecycle is protocol-layer and signing-provider key custody is an operator concern.",
        "Window 433 is the closure-gate lane for Window 424-433.",
        "Window 434+ is the default continuation boundary for Treasury P_e constitutional work; any future CDL-050 opening remains contingent and not pre-authorized by Window 424-433.",
    ):
        assert token in text


def test_coherence_and_capsule_cover_cdl_049_settlement_pe_carry_forward_and_runtime_continuity() -> None:
    coherence_text = _read(COHERENCE_PATH)
    capsule_text = _read(CAPSULE_PATH)
    for token in (
        "CDL-049 is ratified as of Phase 428 with bounded_existential promoted into the active Popperian runtime and forward-facing analysis corpus.",
        "Phase 431 published the Treasury P_e carry-forward decision under Scenario B with Window 434+ as the default continuation target.",
        "The SIM-009 recommendation pair 0.2 / 0.02 remains a provisional planning anchor only and not a constitutional lock.",
        'D2E_AGENT_CLI_VERSION = "d2e_agent_cli_420.v0.1"',
        'D2E_LIFECYCLE_CLI_VERSION = "d2e_lifecycle_cli_421.v0.1"',
        "`docs/specs/ilc_sim_009_results_synthesis_and_pe_stabilization_disposition_430_v0.1.md`",
        "`docs/specs/ilc_pe_stabilization_carry_forward_decision_431_v0.1.md`",
    ):
        assert token in coherence_text or token in capsule_text


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_432_commit_ref_or_fail() -> str:
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
        "docs/specs/ilc_integration_coherence_report_432_v0.1.md",
        "docs/specs/ilc_antigravity_context_capsule_v1.7.md",
        "tests/test_phase_432_coherence_and_capsule_v1_7.py",
    }
    for commit_ref in matching_commits:
        changed = _changed_paths_for_commit(commit_ref)
        if changed == required_paths:
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_432_commit_subject_present_but_no_qualifying_coherence_commit")
    raise AssertionError("phase_432_commit_not_present_in_local_history")


def test_phase_432_commit_touched_required_paths_and_not_decision_log() -> None:
    commit_ref = _resolve_phase_432_commit_ref_or_fail()
    changed = _changed_paths_for_commit(commit_ref)
    assert DECISION_LOG_PATH not in changed


def test_phase_432_commit_touched_no_ilc_core_paths() -> None:
    commit_ref = _resolve_phase_432_commit_ref_or_fail()
    changed = _changed_paths_for_commit(commit_ref)
    forbidden = [path for path in changed if path.startswith("ilc_core/")]
    assert not forbidden, f"phase_432_runtime_mutations:{forbidden}"
