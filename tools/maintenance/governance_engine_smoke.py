# SPDX-License-Identifier: AGPL-3.0-only
# MANUAL MAINTENANCE SCRIPT
# This is a manual smoke test for the Governance and Consensus Engine integration.
# Canonical unit tests live in tests/test_governance_engine.py.

import sys
import os
from pathlib import Path

# Ensure project root is on sys.path when running directly
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ilc_core.graph import EpistemicGraph
from ilc_core.consensus.engine import ConsensusEngine
from ilc_core.mining.benchmark import run_benchmarks_for_agents


def main():
    print("[Maintenance] Starting governance/engine smoke test...")

    # Minimal empty graph
    graph = EpistemicGraph()
    engine = ConsensusEngine(graph)

    # Simulated active agents
    agent_ids = ["agent-cpu-1", "agent-gpu-1"]

    # Run hardware potential benchmarks
    scores_dict = run_benchmarks_for_agents(agent_ids, matrix_size=256)
    potentials = list(scores_dict.values())

    print(f"[Maintenance] Benchmark scores: {scores_dict}")

    # Fake backlog / finalized counts for this "epoch"
    backlog_len = 5
    finalized_last_epoch = 12

    engine.end_epoch_update(
        backlog_len=backlog_len,
        finalized_last_epoch=finalized_last_epoch,
        agent_potentials=potentials,
    )

    # Query ECU fee for a typical task
    fee_ecu = engine.governance.get_task_fee_ecu("claim.submit")
    print(f"[Maintenance] Current claim.submit fee (ECU): {fee_ecu:.8f}")

    # Basic sanity assertion: fee should be positive and not absurd
    if fee_ecu <= 0 or fee_ecu > 10:
        raise AssertionError(
            f"Fee out of expected range: {fee_ecu}"
        )

    print("[Maintenance] ✅ Governance/Engine smoke test completed successfully.")


if __name__ == "__main__":
    main()
