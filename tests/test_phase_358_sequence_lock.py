"""Contract tests for Phase 358 sequence-lock and roadmap artifacts."""

from __future__ import annotations

from pathlib import Path
import subprocess


SEQUENCE_LOCK_PATH = Path("docs/specs/ilc_phase_358_367_sequence_lock_v0.1.md")
ROADMAP_PATH = Path("docs/specs/ilc_distribution_architecture_roadmap_v0.4.md")
DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
SUBJECT_TOKEN = "phase 358 window 358-367 sequence lock and roadmap"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_sequence_lock_exists_and_has_required_headings() -> None:
    assert SEQUENCE_LOCK_PATH.exists()
    text = _read(SEQUENCE_LOCK_PATH)
    for heading in (
        "## 1. Purpose and window character",
        "## 2. Entry state from phase-357 closure",
        "## 3. Implementation authorization and dependency chain",
        "## 4. Locked phase table (358-367)",
        "## 5. Per-phase sensitivity classification",
        "## 6. Runtime module naming convention",
        "## 7. Mandatory entry and exit gates per phase",
        "## 8. CDL-039 opening constraints (phase 359)",
        "## 9. No-runtime-before-window-367-closure",
        "## 10. Phase-specific forward constraints (359-367)",
        "## 11. Non-goals and explicit boundaries",
        "## 12. Forward pointer",
    ):
        assert heading in text


def test_sequence_lock_has_authorization_and_deferral_tokens() -> None:
    text = _read(SEQUENCE_LOCK_PATH)
    for token in (
        "CDL-034 -> CDL-035 -> CDL-036 -> CDL-037 -> CDL-038",
        "CDL-034 through CDL-038 runtime implementation is authorized for Window 358-367.",
        "V-series enforcement runtime implementation (CDL-V1 through CDL-V7) is NOT authorized in this window.",
        "deferred to Window 368-377",
    ):
        assert token in text


def test_sequence_lock_has_runtime_naming_and_mutation_scope_tokens() -> None:
    text = _read(SEQUENCE_LOCK_PATH)
    for token in (
        "_assert_runtime_mutation_scope(commit_ref)",
        "assert_head_commit_touched_no_runtime_files is an anti-pattern for runtime implementation phases",
        "Window 368 sequence-lock drafting must evaluate Levin gossip + coordinate mechanism proposals as D2d wire-protocol inputs.",
    ):
        assert token in text


def test_sequence_lock_has_cdl039_constraints_and_locked_phase_rows() -> None:
    text = _read(SEQUENCE_LOCK_PATH)
    for token in (
        "Phase 359 opens CDL-039 as an additive-only row mutation.",
        "No finalized CDL-039 prelock invariants are locked in Phase 359.",
        "Phase 374 finalizes CDL-039 prelock design after SIM-004 and SIM-005 evidence.",
        "topology-opaque",
        "cluster membership comparison must not be derivable from public protocol data",
        "COSE kid must be a protocol-internal opaque identifier",
        "Phase 358",
        "Phase 359",
        "Phase 360",
        "Phase 361",
        "Phase 362",
        "Phase 363",
        "Phase 364",
        "Phase 365",
        "Phase 366",
        "Phase 367",
    ):
        assert token in text


def test_roadmap_v04_supersedes_v03_and_contains_required_tokens() -> None:
    assert ROADMAP_PATH.exists()
    text = _read(ROADMAP_PATH)
    for token in (
        "Status: non-normative planning artifact — subject to decision-log ratification",
        "Date: 2026-03-05",
        "Supersedes: ilc_distribution_architecture_roadmap_v0.3.md",
        "Phase: 358",
        "D2d wire protocol is elevated from technical plumbing to a communication resilience layer.",
        "Gossip-based discovery is the protocol immune system.",
        "geographic and jurisdictional interference",
        "Implementation remains scheduled for Window 378+",
        "partition-tolerant epoch consensus",
        "gossip topology privacy constraints",
        "Node schema implementation",
        "V-series enforcement",
        "SIM commissioning",
        "CDL-039",
        "1000-series remediation",
        "wallet-agnostic",
        "signing provider",
        "CDL-034",
        "CDL-038",
        "CDL-040 through CDL-044",
        "| D1 Genesis reproducibility | completed |",
        "| D2 Protocol bundle/type system | completed |",
        "| D2b Genesis state bundle | completed |",
        "| D2c Epoch snapshots | completed |",
        "| D2d Wire protocol | partial/incomplete |",
        "| D2e Agent SDK/CLI | partial/incomplete |",
        "| D3 OpenClaw integration | partial/incomplete |",
    ):
        assert token in text


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_358_commit_ref_or_fail() -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    saw_subject_match = False
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if SUBJECT_TOKEN not in subject.lower():
            continue
        saw_subject_match = True
        changed = _changed_paths_for_commit(commit_hash)
        if {
            "docs/specs/ilc_phase_358_367_sequence_lock_v0.1.md",
            "docs/specs/ilc_distribution_architecture_roadmap_v0.4.md",
        }.issubset(changed):
            return commit_hash
    if saw_subject_match:
        raise AssertionError(
            "phase_358_commit_subject_present_but_no_qualifying_sequence_lock_commit"
        )
    raise AssertionError("phase_358_commit_not_present_in_local_history")


def test_phase_commit_touched_required_paths_and_not_decision_log() -> None:
    commit_ref = _resolve_phase_358_commit_ref_or_fail()
    changed = _changed_paths_for_commit(commit_ref)
    assert "docs/specs/ilc_phase_358_367_sequence_lock_v0.1.md" in changed
    assert "docs/specs/ilc_distribution_architecture_roadmap_v0.4.md" in changed
    assert DECISION_LOG_PATH not in changed


def test_phase_commit_touched_no_ilc_core_paths() -> None:
    commit_ref = _resolve_phase_358_commit_ref_or_fail()
    changed = _changed_paths_for_commit(commit_ref)
    forbidden = [path for path in changed if path.startswith("ilc_core/")]
    assert not forbidden, f"phase_358_runtime_mutations:{forbidden}"
