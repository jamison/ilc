"""Contract tests for Phase 422 coherence and capsule v1.6 artifact set."""

from __future__ import annotations

from pathlib import Path
import subprocess


COHERENCE_PATH = Path("docs/specs/ilc_integration_coherence_report_422_v0.1.md")
CAPSULE_PATH = Path("docs/specs/ilc_antigravity_context_capsule_v1.6.md")
DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
SUBJECT_TOKEN = "docs(g8): phase 422 coherence and capsule v1.6"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_coherence_artifact_exists_with_required_headings() -> None:
    assert COHERENCE_PATH.exists()
    text = _read(COHERENCE_PATH)
    for heading in (
        "## 1. Scope and non-ratifying boundary",
        "## 2. Constitutional settlement state (CDL-047/048)",
        "## 3. D2e CLI integration state",
        "## 4. Runtime-integrity and wallet boundary carry-forward",
        "## 5. Phase-417 Popperian review carry-forward",
        "## 6. Window-423 closure readiness and 424+ forward boundary",
        "## 7. Non-goals and canonical anchors",
    ):
        assert heading in text


def test_coherence_contains_required_tokens_and_424_plus_obligations() -> None:
    text = _read(COHERENCE_PATH)
    for token in (
        "No decision-log mutation occurred. No ilc_core runtime files were changed.",
        "CDL-047 is ratified as of Phase 418 with bounty cap 0.15 x B_e, burn floor 0.05, and velocity alert floor 0.91.",
        "CDL-048 is ratified as of Phase 419 with ecu_conversion_deadline = 4 issuance epochs.",
        'D2E_AGENT_CLI_VERSION = "d2e_agent_cli_420.v0.1"',
        'D2E_LIFECYCLE_CLI_VERSION = "d2e_lifecycle_cli_421.v0.1"',
        "Runtime-integrity note: CDL-V1/V2/V3/V7 validators reject non-finite numeric inputs (NaN/Inf).",
        "Wallet-agnostic signing remains mandatory at protocol boundary.",
        "Window 424+ obligations include CDL-049 bounded-existential alignment, follow-on D2e CLI expansion if needed, and SIM-009 commissioning only if new coherence gaps warrant it.",
    ):
        assert token in text


def test_capsule_v1_6_exists_self_contained_and_supersedes_v1_5() -> None:
    assert CAPSULE_PATH.exists()
    text = _read(CAPSULE_PATH)
    assert "Supersedes: docs/specs/ilc_antigravity_context_capsule_v1.5.md" in text
    assert "This capsule is self-contained." in text
    for heading in (
        "## 1. Project identity",
        "## 2. Core architectural invariants",
        "## 3. Project state (as of Phase 422 completion)",
        "## 4. Constitutional ratification state",
        "## 5. Runtime implementation state",
        "## 6. Runtime-integrity and validation guarantees",
        "## 7. Wallet-agnostic signing continuity",
        "## 8. Window 423 and 424+ forward boundary",
        "## 9. Change log from v1.5",
        "## 10. Key canonical anchors",
    ):
        assert heading in text


def test_capsule_contains_required_state_and_forward_boundary_tokens() -> None:
    text = _read(CAPSULE_PATH)
    for token in (
        "CDL-047 and CDL-048 are ratified in the current constitutional register.",
        "CDL-049 remains unopened and is reserved as the Window-424+ planning boundary for bounded-existential alignment.",
        'D2E_AGENT_CLI_VERSION = "d2e_agent_cli_420.v0.1"',
        'D2E_LIFECYCLE_CLI_VERSION = "d2e_lifecycle_cli_421.v0.1"',
        "Runtime-integrity note: V-series validators reject non-finite numeric inputs (NaN/Inf).",
        "Wallet-agnostic signing remains mandatory: signer-lineage lifecycle is protocol-layer and signing-provider key custody is an operator concern.",
        "Window 423 is the closure-gate lane for Window 414-423.",
        "Window 424+ is the earliest authorized boundary for CDL-049 planning, possible D2e CLI expansion, and any SIM-009 follow-on modeling.",
    ):
        assert token in text


def test_coherence_and_capsule_cover_cli_runtime_state_and_phase_417_carry_forward() -> None:
    coherence_text = _read(COHERENCE_PATH)
    capsule_text = _read(CAPSULE_PATH)
    for token in (
        'D2E_AGENT_CLI_VERSION = "d2e_agent_cli_420.v0.1"',
        'D2E_LIFECYCLE_CLI_VERSION = "d2e_lifecycle_cli_421.v0.1"',
        "Phase 417 recorded no CDL-047-specific or CDL-048-specific CRITICAL findings; CDL-049 remains a Window-424+ planning boundary for bounded-existential alignment.",
        "`docs/specs/ilc_popperian_claim_form_governance_review_417_v0.1.md`",
        "`docs/specs/ilc_d2e_agent_cli_handoff_420_v0.1.md`",
        "`docs/specs/ilc_d2e_lifecycle_cli_handoff_421_v0.1.md`",
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


def _resolve_phase_422_commit_ref_or_fail() -> str:
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
        "docs/specs/ilc_integration_coherence_report_422_v0.1.md",
        "docs/specs/ilc_antigravity_context_capsule_v1.6.md",
        "tests/test_phase_422_coherence_and_capsule_v1_6.py",
    }
    for commit_ref in matching_commits:
        changed = _changed_paths_for_commit(commit_ref)
        if changed == required_paths:
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_422_commit_subject_present_but_no_qualifying_coherence_commit")
    raise AssertionError("phase_422_commit_not_present_in_local_history")


def test_phase_422_commit_touched_required_paths_and_not_decision_log() -> None:
    commit_ref = _resolve_phase_422_commit_ref_or_fail()
    changed = _changed_paths_for_commit(commit_ref)
    assert DECISION_LOG_PATH not in changed


def test_phase_422_commit_touched_no_ilc_core_paths() -> None:
    commit_ref = _resolve_phase_422_commit_ref_or_fail()
    changed = _changed_paths_for_commit(commit_ref)
    forbidden = [path for path in changed if path.startswith("ilc_core/")]
    assert not forbidden, f"phase_422_runtime_mutations:{forbidden}"
