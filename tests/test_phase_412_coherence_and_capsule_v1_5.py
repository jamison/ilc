"""Contract tests for Phase 412 coherence and capsule v1.5 artifact set."""

from __future__ import annotations

from pathlib import Path
import subprocess


COHERENCE_PATH = Path("docs/specs/ilc_integration_coherence_report_412_v0.1.md")
CAPSULE_PATH = Path("docs/specs/ilc_antigravity_context_capsule_v1.5.md")
DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
SUBJECT_TOKEN = "docs(g8): phase 412 coherence and capsule v1.5"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_coherence_artifact_exists_with_required_headings() -> None:
    assert COHERENCE_PATH.exists()
    text = _read(COHERENCE_PATH)
    for heading in (
        "## 1. Scope and non-ratifying boundary",
        "## 2. Constitutional settlement state (CDL-042/045/046)",
        "## 3. D2e runtime implementation state",
        "## 4. Historical-test hardening continuity",
        "## 5. Runtime-integrity carry-forward note",
        "## 6. Wallet-agnostic signing and boundary continuity",
        "## 7. Window-413 closure readiness and 414+ forward boundary",
        "## 8. Non-goals and canonical anchors",
    ):
        assert heading in text


def test_coherence_contains_required_tokens_and_closure_state() -> None:
    text = _read(COHERENCE_PATH)
    for token in (
        "No decision-log mutation occurred. No ilc_core runtime files were changed.",
        "CDL-042 ratification closes the agent identity namespace gate for D2e Agent SDK implementation.",
        "CDL-045 is ratified as of Phase 408 with the automated circuit breaker with CDL-V3 diversity quorum trigger and CDL-V6 sunset.",
        "CDL-046 ratification closes the CDL-035 timed_out amendment obligation for orphan recovery.",
        "Wallet-agnostic signing carry-forward remains active: ILC protocol signing is wallet-agnostic, signer-lineage lifecycle is protocol-layer, and signing-provider key custody remains an operator concern.",
        "Runtime-integrity note: CDL-V1/V2/V3/V7 validators reject non-finite numeric inputs (NaN/Inf).",
        "`CDL-039`: ratified",
        "`CDL-040`: ratified",
        "`CDL-041`: ratified",
        "`CDL-043`: ratified",
        "`CDL-044`: ratified",
    ):
        assert token in text


def test_capsule_v1_5_exists_self_contained_and_supersedes_v1_4() -> None:
    assert CAPSULE_PATH.exists()
    text = _read(CAPSULE_PATH)
    assert "Supersedes: docs/specs/ilc_antigravity_context_capsule_v1.4.md" in text
    assert "This capsule is self-contained." in text
    for heading in (
        "## 1. Project identity",
        "## 2. Core architectural invariants",
        "## 3. Project state (as of Phase 412 completion)",
        "## 4. Constitutional ratification state",
        "## 5. Runtime implementation state",
        "## 6. Runtime-integrity and validation guarantees",
        "## 7. Wallet-agnostic signing continuity",
        "## 8. Window 413 and 414+ forward boundary",
        "## 9. Change log from v1.4",
        "## 10. Key canonical anchors",
    ):
        assert heading in text


def test_capsule_contains_required_state_and_boundary_tokens() -> None:
    text = _read(CAPSULE_PATH)
    for token in (
        "CDL-042 is ratified as of Phase 407 and closes the agent identity namespace gate for D2e Agent SDK implementation.",
        "CDL-045 is ratified as of Phase 408 with the automated circuit breaker with CDL-V3 diversity quorum trigger and CDL-V6 sunset.",
        "CDL-046 is ratified as of Phase 409 and closes the CDL-035 timed_out amendment obligation for orphan recovery.",
        "CDL-V1 temporal decay, CDL-V2 sybil resistance, CDL-V3 diversity floor, and CDL-V7 Popperian gate are computationally enforced.",
        "Runtime-integrity note: V-series validators reject non-finite numeric inputs (NaN/Inf).",
        "Wallet-agnostic signing remains mandatory: signer-lineage lifecycle is protocol-layer and signing-provider key custody is an operator concern.",
        "SIM-008 post-issuance transition modeling results are available as evidence for Window-414+ Treasury Governance and ECU mandatory conversion deadline CDL planning.",
    ):
        assert token in text


def test_coherence_and_capsule_cover_d2e_runtime_state() -> None:
    coherence_text = _read(COHERENCE_PATH)
    capsule_text = _read(CAPSULE_PATH)
    for token in (
        'AGENT_ID_RUNTIME_VERSION = "agent_id_runtime_410.v0.1"',
        'CDL_042_DEPENDENCY = "cdl_042_ratified_407.v0.1"',
        'NODE_SCHEMA_DEPENDENCY = "cdl_038_ratified_353.v0.1"',
        'TIMED_OUT_LIFECYCLE_RUNTIME_VERSION = "timed_out_lifecycle_runtime_411.v0.1"',
        'CDL_046_DEPENDENCY = "cdl_046_ratified_409.v0.1"',
        'LIFECYCLE_BASE_DEPENDENCY = "cdl_035_ratified_350.v0.1"',
        '`ilc_core/identity/agent_id_runtime.py`',
        '`ilc_core/node/timed_out_lifecycle_runtime_411.py`',
    ):
        assert token in coherence_text or token in capsule_text
    assert "SIM-008 commissioning results remain evidence-only carry-forward for Window-414+ economic CDL planning" in coherence_text


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_412_commit_ref_or_fail() -> str:
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
        "docs/specs/ilc_integration_coherence_report_412_v0.1.md",
        "docs/specs/ilc_antigravity_context_capsule_v1.5.md",
        "tests/test_phase_412_coherence_and_capsule_v1_5.py",
    }
    for commit_ref in matching_commits:
        changed = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed):
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_412_commit_subject_present_but_no_qualifying_coherence_commit")
    raise AssertionError("phase_412_commit_not_present_in_local_history")


def test_phase_412_commit_touched_required_paths_and_not_decision_log() -> None:
    commit_ref = _resolve_phase_412_commit_ref_or_fail()
    changed = _changed_paths_for_commit(commit_ref)
    assert DECISION_LOG_PATH not in changed


def test_phase_412_commit_touched_no_ilc_core_paths() -> None:
    commit_ref = _resolve_phase_412_commit_ref_or_fail()
    changed = _changed_paths_for_commit(commit_ref)
    forbidden = [path for path in changed if path.startswith("ilc_core/")]
    assert not forbidden, f"phase_412_runtime_mutations:{forbidden}"
