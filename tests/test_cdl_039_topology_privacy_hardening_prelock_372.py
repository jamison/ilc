"""Contract tests for Phase 372 CDL-039 topology/privacy hardening prelock artifact."""

from __future__ import annotations

from pathlib import Path
import subprocess


ARTIFACT_PATH = Path("docs/specs/ilc_cdl_039_topology_privacy_hardening_prelock_372_v0.1.md")
DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
SUBJECT_TOKEN = "docs(g8): phase 372 cdl-039 prelock topology privacy hardening"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_artifact_exists_with_required_headings() -> None:
    assert ARTIFACT_PATH.exists()
    text = _read(ARTIFACT_PATH)
    for heading in (
        "## 1. Scope and non-ratifying boundary",
        "## 2. Input evidence and interpretation anchors",
        "## 3. Invariant 1 - transport header non-authorship",
        "## 4. Invariant 2 - partition-state cross-cluster reference rate limiting",
        "## 5. Invariant 3 - cluster membership non-inferrability",
        "## 6. Invariant 4 - private-visibility expiry and promotion boundary",
        "## 7. Invariant 5 - opaque channel routing identifier",
        "## 8. Two-timescale CDL-039 closure requirements",
        "## 9. Phase 373 calibration queue",
        "## 10. Implementation-boundary notes for Window 378+",
        "## 11. Non-goals and unresolved questions",
    ):
        assert heading in text


def test_artifact_contains_required_invariant_and_timescale_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for token in (
        "Modeled outputs are non-ratifying evidence inputs.",
        "This artifact extends the Phase-359 prelock additively; both documents serve as CDL-039 prelock evidence for future ratification.",
        "Transport Envelope routing headers MUST NOT carry creator_agent_id; authorship attribution is resolved from Authored Payload and protocol interpretation.",
        "Current Phase-362 dissemination runtime is v0.1 state; target invariant is enforced at the authorized Window 378+ D2d/network runtime implementation boundary.",
        "When partition-state is asserted by the gossip coordinate system, nodes MUST apply a cross-cluster reference creation rate limit not exceeding R_partition_cross_ref per epoch, emit deterministic backpressure signaling, and maintain release hysteresis H_release.",
        "Dissemination headers and gossip messages MUST NOT enable a passive observer to reconstruct the membership set of any cluster.",
        "Private-visibility nodes without a valid promotion_receipt after retention_epochs MUST be treated as expired and ineligible for direct promotion.",
        "CDL-038 scope boundary for post-expiry recovery semantics remains an explicit open question for prelock text closure.",
        "Transport channel routing field MUST be an opaque identifier (CID or uniformly random bytes); human-readable channel labels are UI-layer concerns only.",
        "Current Phase-362 channel enum usage is v0.1 state; target opaque-identifier invariant is enforced at the authorized Window 378+ D2d/network runtime implementation boundary.",
        "short-timescale CDL-039 context: validation epoch liveness and Levin stress-cascade reconnection handling.",
        "long-timescale CDL-039 context: issuance epoch partition divergence and highest_ecu_wins reconciliation.",
        "Phase 373 calibrates unresolved parameters: R_partition_cross_ref, H_release, retention_epochs, timeout/recovery policy constants.",
        "No decision-log mutation occurred. No ilc_core runtime files were changed.",
    ):
        assert token in text


def test_artifact_references_phase_371_contract_consumption() -> None:
    text = _read(ARTIFACT_PATH)
    for token in (
        "SIM taxonomy table is consumed as canonical numbering for current window",
        "epoch-type interpretation table for SIM-003/SIM-004/SIM-005 is consumed unchanged",
        "constant lock/readiness flags are consumed to separate Phase-372 locks from Phase-373 calibration",
    ):
        assert token in text


def test_artifact_has_phase_373_calibration_queue_and_window_378_notes() -> None:
    text = _read(ARTIFACT_PATH)
    for token in (
        "adversarial stress for partition-state flapping",
        "adversarial stress for timeout false-positive/false-negative tradeoff",
        "Window 378+ carries runtime enforcement for target invariants that diverge from v0.1 runtime state",
        "No standing compatibility/profile dual-mode is introduced as a protocol feature.",
    ):
        assert token in text


def test_window_378_boundary_mentions_invariant_1_and_5() -> None:
    text = _read(ARTIFACT_PATH)
    assert "invariant 1 (non-authorship transport header)" in text
    assert "invariant 5 (opaque channel identifier)" in text


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_372_commit_ref_or_fail() -> str:
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
        "docs/specs/ilc_cdl_039_topology_privacy_hardening_prelock_372_v0.1.md",
        "tests/test_cdl_039_topology_privacy_hardening_prelock_372.py",
    }
    for commit_ref in matching_commits:
        changed = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed):
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_372_commit_subject_present_but_no_qualifying_prelock_commit")
    raise AssertionError("phase_372_commit_not_present_in_local_history")


def test_phase_372_commit_touched_required_paths_and_not_decision_log() -> None:
    commit_ref = _resolve_phase_372_commit_ref_or_fail()
    changed = _changed_paths_for_commit(commit_ref)
    assert DECISION_LOG_PATH not in changed


def test_phase_372_commit_touched_no_ilc_core_paths() -> None:
    commit_ref = _resolve_phase_372_commit_ref_or_fail()
    changed = _changed_paths_for_commit(commit_ref)
    forbidden = [path for path in changed if path.startswith("ilc_core/")]
    assert not forbidden, f"phase_372_runtime_mutations:{forbidden}"
