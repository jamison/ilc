from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
    parse_decision_register_rows,
)


DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
ARTIFACT_PATH = Path(
    "docs/specs/ilc_cdl_039_p2p_transport_baseline_and_topology_privacy_evidence_prelock_359_v0.1.md"
)
PHASE_359_SUBJECT_TOKEN = "phase 359 cdl-039 open and p2p transport baseline prelock"
EXPECTED_ROW = (
    "| CDL-039 | ADR-0011 / Open Requirements 354 v0.1 | P2P transport baseline, no-central-broker invariant, and gossip-topology privacy constraints | "
    "open | centrally coordinated relay transport, federated relay mesh, brokerless peer-to-peer gossip baseline | "
    "brokerless peer-to-peer gossip baseline (proposed) | no-central-broker invariant, topology-privacy constraints, partition evidence requirements |"
)


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


def _resolve_phase_359_commit_ref() -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    matching: list[str] = []
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if PHASE_359_SUBJECT_TOKEN in subject.lower():
            matching.append(commit_hash)

    required_paths = {
        str(DECISION_LOG_PATH),
        str(ARTIFACT_PATH),
        "tests/test_cdl_039_open_and_p2p_transport_baseline_prelock_359.py",
    }
    for commit_ref in matching:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref

    if matching:
        raise AssertionError("phase_359_commit_subject_present_but_no_constitutional_opening_commit")
    raise AssertionError("phase_359_commit_not_present_in_local_history")


def _decision_log_text_at_ref(ref: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{ref}:{DECISION_LOG_PATH}"],
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(f"unable_to_read_decision_log_at_ref:{ref}: {result.stderr.strip()}")
    return result.stdout


def _decision_register_lines(text: str) -> list[str]:
    lines = text.splitlines()
    start = None
    for idx, line in enumerate(lines):
        if line.startswith("| decision_id | related_clause | decision_topic | status | options | current_candidate | required_artifacts |"):
            start = idx + 2
            break
    if start is None:
        raise AssertionError("decision_register_header_not_found")

    register_lines: list[str] = []
    for line in lines[start:]:
        if not line.startswith("|"):
            break
        register_lines.append(line)
    return register_lines


def test_artifact_exists_and_has_required_headings() -> None:
    assert ARTIFACT_PATH.exists()
    text = _read(ARTIFACT_PATH)
    for heading in (
        "## 1. Purpose and scope",
        "## 2. CDL-039 opening state",
        "## 3. Option inventory and current candidate",
        "## 4. No-central-broker baseline constraints",
        "## 5. Topology privacy constraints",
        "## 6. Authoritative prelock evidence requirements (open, not finalized)",
        "## 7. Deferral and phase-boundary constraints",
        "## 8. Canonical anchors",
    ):
        assert heading in text


def test_artifact_has_required_tokens_and_authoritative_items() -> None:
    text = _read(ARTIFACT_PATH)
    for token in (
        "CDL-039",
        "status: open",
        "brokerless peer-to-peer gossip baseline",
        "centrally coordinated relay transport",
        "federated relay mesh",
        "no-central-broker invariant",
        "topology-opaque",
        "cluster membership comparison must not be derivable from public protocol data",
        "COSE kid must be a protocol-internal opaque identifier",
        "D2d wire protocol is elevated from technical plumbing to a communication resilience layer.",
        "Gossip-based discovery is the protocol immune system.",
        "partition-tolerant epoch consensus",
        "gossip topology privacy constraints",
        "No finalized CDL-039 prelock invariants are locked in Phase 359.",
        "Phase 374 finalizes CDL-039 prelock design after SIM-004 and SIM-005 evidence.",
        "Levin gossip + coordinate mechanism proposals are deferred to Window 368 sequence-lock drafting.",
        "Section 6 is authoritative for later ratification when it is more specific than the compressed CDL row shorthand.",
        "Schema changes still require CDL opening, evidence prelock, ratification, and closure-gate process.",
        "no-central-broker invariant evidence requirement",
        "topology privacy constraint requirement set",
        "partition divergence evidence dependency",
        "epoch timing attack-surface evidence dependency",
        "transport identity opacity requirement",
        "candidate mechanism comparison requirement",
        "docs/specs/ilc_phase_358_367_sequence_lock_v0.1.md",
        "docs/specs/ilc_distribution_architecture_roadmap_v0.4.md",
        "docs/specs/ilc_open_requirements_and_unknown_unknowns_analysis_354_v0.1.md",
    ):
        assert token in text


def test_decision_log_contains_exact_new_row() -> None:
    # The Phase-359 `CDL-039` row is a historical prelock reference.
    historical_text = _decision_log_text_at_ref(_resolve_phase_359_commit_ref())
    assert EXPECTED_ROW in historical_text


def test_new_row_has_no_ratification_metadata() -> None:
    historical_rows = parse_decision_register_rows(_decision_log_text_at_ref(_resolve_phase_359_commit_ref()))
    row = historical_rows["CDL-039"]
    assert row["status"] == "open"
    assert "ratified_phase" not in row
    assert "ratified_date" not in row
    assert "evidence_document" not in row


def test_new_row_is_appended_after_cdl_038_in_raw_line_order() -> None:
    register_lines = _decision_register_lines(_decision_log_text_at_ref(_resolve_phase_359_commit_ref()))
    idx = next(i for i, line in enumerate(register_lines) if line.startswith("| CDL-038 |"))
    assert register_lines[idx + 1] == EXPECTED_ROW


def test_full_additive_only_non_target_shield_for_phase_359() -> None:
    commit_ref = _resolve_phase_359_commit_ref()
    old_rows = parse_decision_register_rows(_decision_log_text_at_ref(f"{commit_ref}^1"))
    new_rows = parse_decision_register_rows(_decision_log_text_at_ref(commit_ref))
    added_ids = set(new_rows) - set(old_rows)
    assert added_ids == {"CDL-039"}
    for cdl_id in old_rows:
        assert old_rows[cdl_id] == new_rows[cdl_id], f"row_{cdl_id}_unlawfully_mutated_in_phase_359"


def test_phase_359_commit_touched_no_runtime_files() -> None:
    commit_ref = _resolve_phase_359_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
