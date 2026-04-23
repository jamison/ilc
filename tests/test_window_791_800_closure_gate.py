from __future__ import annotations

import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

PHASE_DOCS = [
    REPO_ROOT / "docs/phases/phase_791_sequence_lock_acknowledgment.md",
    REPO_ROOT / "docs/phases/phase_792_h010_embedding_pipeline.md",
    REPO_ROOT / "docs/phases/phase_793_h014_sim_routing_01.md",
    REPO_ROOT / "docs/phases/phase_794_h013_d2d_sealed_sender_adr.md",
    REPO_ROOT / "docs/phases/phase_795_h015_wiring.md",
    REPO_ROOT / "docs/phases/phase_796_subgraph_laplacian_memo.md",
    REPO_ROOT / "docs/phases/phase_797_private_shard_proposal.md",
    REPO_ROOT / "docs/phases/phase_798_jury_deliberation_memo.md",
    REPO_ROOT / "docs/phases/phase_799_tier3_assessment.md",
    REPO_ROOT / "docs/phases/phase_800_coherence_report.md",
    REPO_ROOT / "docs/phases/phase_800_closure_gate.md",
]

RESEARCH_DOCS = [
    REPO_ROOT / "docs/research/ilc_sim_routing_01_results_v0.1.md",
    REPO_ROOT / "docs/research/ilc_subgraph_laplacian_research_memo_791_v0.1.md",
    REPO_ROOT / "docs/research/ilc_private_shard_architecture_proposal_791_v0.1.md",
    REPO_ROOT / "docs/research/ilc_jury_deliberation_research_memo_791_v0.1.md",
    REPO_ROOT / "docs/research/ilc_tier_3_assessment_artifact_791_v0.1.md",
]

CAPSULE = REPO_ROOT / "docs/specs/ilc_antigravity_context_capsule_v5.10.md"
ADR_0034 = REPO_ROOT / "docs/adr/ADR_0034_D2d_Sealed_Sender_Mechanism.md"
H_LANE = REPO_ROOT / "docs/research/ilc_hypergraph_implementation_lane_h_series_v0.1.md"
DECISION_LOG = REPO_ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _all_window_text() -> str:
    return "\n".join(
        _read(path) for path in [*PHASE_DOCS, *RESEARCH_DOCS, CAPSULE, ADR_0034, H_LANE]
    )


def test_all_window_outputs_exist() -> None:
    for path in [
        *PHASE_DOCS,
        *RESEARCH_DOCS,
        CAPSULE,
        ADR_0034,
        H_LANE,
        REPO_ROOT / "ilc_core/analysis/embedding_pipeline.py",
        REPO_ROOT / "ilc_core/network/d2d/spectral_routing_runtime.py",
    ]:
        assert path.exists(), f"missing window output: {path}"


def test_required_verdict_tokens_are_present() -> None:
    text = _all_window_text()
    for token in (
        "phase_791_sequence_lock_acknowledged",
        "run_h010_embedding_pipeline_verdict=pass",
        "run_h014_sim_routing_01_verdict=pass",
        "run_h013_d2d_sealed_sender_adr_verdict=accepted",
        "run_h015_spectral_routing_verdict=pass",
        "phase_796_subgraph_laplacian_memo_complete",
        "phase_797_private_shard_proposal_complete",
        "phase_798_jury_deliberation_memo_complete",
        "tier_3_status=deferred_pending_prerequisites",
        "phase_800_coherence_report_complete",
        "phase_800_window_791_800_verdict=pass",
    ):
        assert token in text


def test_capsule_advances_from_v59_to_v510_not_v58() -> None:
    text = _read(CAPSULE)
    assert "capsule_v5_10_supersedes_v5_9" in text
    assert "docs/specs/ilc_antigravity_context_capsule_v5.9.md" in text
    assert "capsule_v5_8" not in text


def test_h014_topology_classes_and_thresholds_are_locked() -> None:
    text = _read(REPO_ROOT / "docs/research/ilc_sim_routing_01_results_v0.1.md")
    for token in (
        "T1_random",
        "T2_panel_heavy",
        "T3_coalition_sparse",
        "T4_partition_near",
        "Healthy greedy convergence floor",
        "Partition-near greedy convergence floor",
        "Two-phase convergence floor",
        "0.85",
        "0.60",
        "0.80",
    ):
        assert token in text


def test_h015_boundary_does_not_claim_gossip_activation() -> None:
    text = _read(REPO_ROOT / "docs/phases/phase_795_h015_wiring.md")
    assert "does not activate spectral beacon gossip" in text
    assert "does not implement H-013 sealed sender" in text
    assert "run_h015_spectral_routing_verdict=pass" in text
    assert "gossip activation blocked" in _read(CAPSULE).lower()


def test_tier3_and_patent_boundaries_are_preserved() -> None:
    text = _all_window_text()
    assert "tier_3_status=deferred_pending_prerequisites" in text
    assert "tier_3_activation_not_claimed" in text
    assert "no_patent_publication_in_window_791_800" in text
    assert "No patent-sensitive publication occurred" in text


def test_no_ellipsis_in_window_walkthroughs() -> None:
    for path in PHASE_DOCS:
        assert "..." not in _read(path), f"ellipsis found in {path}"


def test_decision_log_not_mutated_in_worktree() -> None:
    result = subprocess.run(
        ["git", "diff", "--name-only", "--", str(DECISION_LOG.relative_to(REPO_ROOT))],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == ""
