from __future__ import annotations

import importlib.util
import json
import re
import subprocess
from pathlib import Path

from ilc_core.consensus.epoch_state_runtime import (
    canonical_epoch_state_vectors,
    generate_epoch_state_record,
    generate_quorum_record,
)
from ilc_core.consensus.finality_evaluator import evaluate_epoch_finality, resolve_fork
from ilc_core.network.peer import PeerManager


RUNTIME_BASELINE_PATH = Path("tools/runtime_baseline.py")
PHASE_436_TEST_PATH = Path("tests/test_phase_436_runtime_tranche_benchmark_harness_and_tranche_completion.py")
HANDOFF_PATH = Path("docs/specs/ilc_consensus_runtime_harness_integration_handoff_446_v0.1.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_446_SUBJECT_TOKEN = "runtime(g8): phase 446 consensus harness integration and network bridge exercise"
REQUIRED_CONSENSUS_BUDGET_KEYS = (
    "quorum_record_generation_ms",
    "epoch_state_generation_ms",
    "finality_evaluation_ms",
    "fork_resolution_ms",
)
REQUIRED_HANDOFF_HEADINGS = (
    "## 1. Phase 446 runtime scope summary",
    "## 2. Ratified constitutional anchors",
    "## 3. Harness integration and network bridge exercise",
    "## 4. Consensus benchmark results",
    "## 5. Bounded hotspot cleanup record",
    "## 6. Test evidence and remaining runtime scope",
    "## 7. Non-goals and Phase 447 pointer",
)
REQUIRED_HANDOFF_TOKENS = (
    "Phase 446 completed harness integration for the CDL-051 consensus runtime tranche.",
    "CDL-051 ratification evidence anchor: docs/specs/ilc_cdl_051_constitutional_consensus_and_epoch_finality_ratification_evidence_443_v0.1.md",
    "Phase 446 did not mutate the constitutional decision log.",
    "Phase 446 did not perform DAG-CBOR or storage-format cutover.",
    "Phase 446 did not open or modify a native P2P transport layer.",
    "CDL-050 remains unopened and unaffected by Phase 446.",
    "Phase 447 is the next authorized phase.",
)
MINIMUM_REQUIRED_PATHS = {
    str(RUNTIME_BASELINE_PATH),
    "tests/test_phase_446_consensus_runtime_iii_harness_integration.py",
    str(HANDOFF_PATH),
}
PROTECTED_CONSTITUTIONAL_PATHS = {
    "docs/specs/ilc_phase_441_449_sequence_lock_v0.1.md",
    "docs/specs/ilc_cdl_051_constitutional_consensus_and_epoch_finality_opening_stub_441_v0.1.md",
    "docs/specs/ilc_cdl_051_constitutional_consensus_and_epoch_finality_prelock_hardening_442_v0.1.md",
    "docs/specs/ilc_cdl_051_constitutional_consensus_and_epoch_finality_ratification_evidence_443_v0.1.md",
    "docs/specs/ilc_consensus_runtime_epoch_state_and_quorum_record_handoff_444_v0.1.md",
    "docs/specs/ilc_consensus_runtime_finality_evaluator_handoff_445_v0.1.md",
}
PROTECTED_PRIOR_PHASE_TESTS = {
    "tests/test_phase_441_cdl_051_opening.py",
    "tests/test_phase_442_cdl_051_constitutional_consensus_and_epoch_finality_prelock_hardening.py",
    "tests/test_phase_443_cdl_051_ratification.py",
    "tests/test_phase_444_consensus_runtime_i_epoch_state_and_quorum_record_surfaces.py",
    "tests/test_phase_445_consensus_runtime_ii_finality_evaluator_and_fork_resolution.py",
}


class _Response:
    def __init__(self, status_code: int = 202) -> None:
        self.status_code = status_code
        self.ok = 200 <= status_code < 300


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_runtime_baseline_module():
    spec = importlib.util.spec_from_file_location("phase_446_runtime_baseline", RUNTIME_BASELINE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _is_qualifying_main_commit(changed_paths: set[str]) -> bool:
    if not MINIMUM_REQUIRED_PATHS.issubset(changed_paths):
        return False
    if str(PHASE_436_TEST_PATH) not in changed_paths:
        return False
    allowed_paths = set(MINIMUM_REQUIRED_PATHS)
    allowed_paths.add(str(PHASE_436_TEST_PATH))
    return all(path in allowed_paths or path.startswith("ilc_core/consensus/") for path in changed_paths)


def _resolve_phase_446_commit_ref() -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    saw_subject = False
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if subject.strip() != PHASE_446_SUBJECT_TOKEN:
            continue
        saw_subject = True
        if _is_qualifying_main_commit(_changed_paths_for_commit(commit_hash)):
            return commit_hash
    if saw_subject:
        raise AssertionError("phase_446_commit_subject_present_but_no_qualifying_harness_commit")
    raise AssertionError("phase_446_commit_not_present_in_local_history")


def test_runtime_baseline_imports_consensus_modules() -> None:
    text = _read(RUNTIME_BASELINE_PATH)

    assert "ilc_core.consensus.epoch_state_runtime" in text
    assert "ilc_core.consensus.finality_evaluator" in text


def test_consensus_budget_keys_registered_in_baseline() -> None:
    text = _read(RUNTIME_BASELINE_PATH)

    for key in REQUIRED_CONSENSUS_BUDGET_KEYS:
        assert key in text


def test_consensus_benchmark_section_executes_and_returns_structured_output() -> None:
    module = _load_runtime_baseline_module()

    section = module.build_consensus_baseline_section(1)

    assert set(section) == {"budgets", "measurements"}
    assert set(section["budgets"]) == set(REQUIRED_CONSENSUS_BUDGET_KEYS)
    assert set(section["measurements"]) == set(REQUIRED_CONSENSUS_BUDGET_KEYS)
    for key in REQUIRED_CONSENSUS_BUDGET_KEYS:
        assert section["measurements"][key]["avg_ms"] > 0.0
        assert section["measurements"][key]["min_ms"] > 0.0
        assert section["measurements"][key]["max_ms"] > 0.0
        assert section["budgets"][key]["observed_avg_ms"] > 0.0


def test_finality_evaluation_and_fork_resolution_pipeline_is_exercised() -> None:
    conflict_vector = canonical_epoch_state_vectors()[1]
    threshold = conflict_vector["epoch_state"]["quorum_threshold"]

    first_finality = evaluate_epoch_finality(conflict_vector["quorum_records"], threshold)
    second_finality = evaluate_epoch_finality(conflict_vector["quorum_records"], threshold)

    base_state = dict(conflict_vector["epoch_state"])
    candidate_a = generate_epoch_state_record(base_state)
    candidate_b_state = dict(base_state)
    candidate_b_state["candidate_block_hash"] = "block-gamma"
    candidate_b_state["quorum_record_digests"] = sorted(
        {f"{digest}-alt" for digest in base_state["quorum_record_digests"]}
    )
    candidate_b = generate_epoch_state_record(candidate_b_state)

    first_resolution = resolve_fork([candidate_a, candidate_b])
    second_resolution = resolve_fork([candidate_a, candidate_b])

    assert first_finality == second_finality
    assert first_finality["finality_status"] == "conflict"
    assert first_resolution == second_resolution
    assert first_resolution["selected_state_digest"] == min(
        candidate_a["state_digest"],
        candidate_b["state_digest"],
    )


def test_network_bridge_consensus_record_roundtrip() -> None:
    raw_record = canonical_epoch_state_vectors()[0]["quorum_records"][0]
    quorum_record = generate_quorum_record(raw_record)
    captured_payloads: list[dict[str, object]] = []

    def sender(url: str, payload: dict[str, object], timeout_s: float) -> _Response:
        captured_payloads.append(json.loads(json.dumps(payload, sort_keys=True)))
        return _Response(202)

    manager = PeerManager(
        local_port=8000,
        fanout_limit=1,
        request_timeout_s=0.1,
        sender=sender,
        allow_private_peer_endpoints_for_tests=True,
    )
    manager.add_peer("127.0.0.2", 8101)

    result = manager.broadcast("/consensus/receive", quorum_record)

    assert result["attempted"] == 1
    assert result["succeeded"] == 1
    assert captured_payloads[0]["record_digest"] == quorum_record["record_digest"]


def test_handoff_exists_and_contains_required_headings_and_tokens() -> None:
    text = _read(HANDOFF_PATH)

    assert HANDOFF_PATH.exists()
    for heading in REQUIRED_HANDOFF_HEADINGS:
        assert heading in text
    for token in REQUIRED_HANDOFF_TOKENS:
        assert token in text
    for key in REQUIRED_CONSENSUS_BUDGET_KEYS:
        assert key in text
        assert re.search(rf"{key}[^\n]*[0-9]+(?:\.[0-9]+)?\s*ms", text)


def test_phase_446_commit_touches_exactly_required_paths() -> None:
    commit_ref = _resolve_phase_446_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)

    assert _is_qualifying_main_commit(changed_paths)


def test_phase_446_commit_respects_non_mutation_boundaries() -> None:
    commit_ref = _resolve_phase_446_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)

    assert str(DECISION_LOG_PATH) not in changed_paths
    assert str(PHASE_436_TEST_PATH) in changed_paths
    assert not any(
        path.startswith("ilc_core/") and not path.startswith("ilc_core/consensus/")
        for path in changed_paths
    )
    assert PROTECTED_CONSTITUTIONAL_PATHS.isdisjoint(changed_paths)
    assert PROTECTED_PRIOR_PHASE_TESTS.isdisjoint(changed_paths)
    assert not any(path.startswith("docs/antigravity_tasks/") for path in changed_paths)
    assert not any(path.startswith("docs/phases/") for path in changed_paths)
    assert not any(path.startswith("ILC_release_track/") for path in changed_paths)
    assert not any(path.startswith("release_engineering/") for path in changed_paths)
