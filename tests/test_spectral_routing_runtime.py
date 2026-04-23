"""
H-015 gate tests: greedy spectral descent routing with random-walk fallback.

Tests cover:
  - Version token and dependency guard
  - Convergence at source (0-hop)
  - Greedy descent topology (deterministic small graph)
  - Cycle detection → random-walk fallback
  - Max-hops budget exhaustion (no fallback and with fallback)
  - Dead-end (no peers) in both phases
  - Fallback used_fallback flag accuracy
  - Multi-dimensional fingerprint routing
  - Reproducible results with seeded rng
  - No gossip wiring in this module (scope guard)
"""

from __future__ import annotations

import random
from typing import Dict, List

import pytest

from ilc_core.network.d2d.spectral_routing_runtime import (
    DEFAULT_MAX_HOPS,
    H014_DEPENDENCY,
    SPECTRAL_ROUTING_RUNTIME_VERSION,
    RoutingResult,
    route,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fp(v: float) -> List[float]:
    """1D fingerprint helper."""
    return [v]


def _make_cluster_graph() -> tuple[
    Dict[str, List[float]],
    Dict[str, List[str]],
]:
    """Simple 8-node graph with two clusters separated in fingerprint space.

    Cluster A (fingerprint ≈ 0.1):  n0, n1, n2, n3
    Cluster B (fingerprint ≈ 0.9):  n4, n5, n6, n7

    Topology (directed):
      n0 → n1, n4
      n1 → n2, n4
      n2 → n3
      n3 → n4
      n4 → n5
      n5 → n6, n7
      n6 → n7
      n7 → (none)

    Greedy descent from n0 toward target_fp=[0.9] follows n0→n4 on hop 1
    (n4 fp=0.9 is closer to target than n1 fp=0.12).
    """
    fps: Dict[str, List[float]] = {
        "n0": [0.10],
        "n1": [0.12],
        "n2": [0.11],
        "n3": [0.13],
        "n4": [0.90],
        "n5": [0.91],
        "n6": [0.89],
        "n7": [0.88],
    }
    adj: Dict[str, List[str]] = {
        "n0": ["n1", "n4"],
        "n1": ["n2", "n4"],
        "n2": ["n3"],
        "n3": ["n4"],
        "n4": ["n5"],
        "n5": ["n6", "n7"],
        "n6": ["n7"],
        "n7": [],
    }
    return fps, adj


def _cluster_b_predicate(node_id: str) -> bool:
    return node_id in {"n4", "n5", "n6", "n7"}


# ---------------------------------------------------------------------------
# Version / dependency guards
# ---------------------------------------------------------------------------

def test_version_token_identifies_h015() -> None:
    assert "spectral_routing_runtime_h015" in SPECTRAL_ROUTING_RUNTIME_VERSION


def test_h014_dependency_token_correct() -> None:
    assert H014_DEPENDENCY == "run_h014_sim_routing_01_verdict=pass"


def test_default_max_hops_is_testnet_calibrated() -> None:
    # SIM-ROUTING-01: 3 × ⌈log₂(500)⌉ = 27 for N=500 testnet.
    assert DEFAULT_MAX_HOPS == 27


# ---------------------------------------------------------------------------
# Convergence at source (0-hop)
# ---------------------------------------------------------------------------

def test_source_already_converged_returns_zero_hops() -> None:
    fps, adj = _make_cluster_graph()
    result = route(
        source_id="n4",
        target_fingerprint=_fp(0.9),
        peer_fingerprints=fps,
        peer_adjacency=adj,
        convergence_predicate=_cluster_b_predicate,
    )
    assert result.converged
    assert result.hops == 0
    assert result.path == ("n4",)
    assert result.failure_mode == ""
    assert not result.used_fallback


# ---------------------------------------------------------------------------
# Greedy descent — direct 1-hop path
# ---------------------------------------------------------------------------

def test_greedy_descent_reaches_target_in_one_hop() -> None:
    # n0 has peers n1 (fp=0.12) and n4 (fp=0.90).
    # Target fingerprint is 0.9 → n4 is closer → greedy picks n4 in 1 hop.
    fps, adj = _make_cluster_graph()
    result = route(
        source_id="n0",
        target_fingerprint=_fp(0.9),
        peer_fingerprints=fps,
        peer_adjacency=adj,
        convergence_predicate=_cluster_b_predicate,
    )
    assert result.converged
    assert result.hops == 1
    assert result.path == ("n0", "n4")
    assert not result.used_fallback


def test_greedy_descent_path_is_monotonically_descending() -> None:
    # From n1: peers are n2 (fp=0.11) and n4 (fp=0.90).
    # Greedy should pick n4 in 1 hop.
    fps, adj = _make_cluster_graph()
    result = route(
        source_id="n1",
        target_fingerprint=_fp(0.9),
        peer_fingerprints=fps,
        peer_adjacency=adj,
        convergence_predicate=_cluster_b_predicate,
    )
    assert result.converged
    assert result.hops == 1
    assert result.path[-1] in {"n4", "n5", "n6", "n7"}
    assert not result.used_fallback


# ---------------------------------------------------------------------------
# Multi-hop greedy path (no shortcut to cluster B)
# ---------------------------------------------------------------------------

def test_greedy_descent_multi_hop() -> None:
    # Graph where the only path to cluster B is n2 → n3 → n4.
    fps: Dict[str, List[float]] = {
        "n2": [0.11],
        "n3": [0.13],
        "n4": [0.90],
    }
    adj: Dict[str, List[str]] = {
        "n2": ["n3"],
        "n3": ["n4"],
        "n4": [],
    }
    result = route(
        source_id="n2",
        target_fingerprint=_fp(0.9),
        peer_fingerprints=fps,
        peer_adjacency=adj,
        convergence_predicate=lambda nid: nid == "n4",
    )
    assert result.converged
    assert result.hops == 2
    assert result.path == ("n2", "n3", "n4")
    assert not result.used_fallback


# ---------------------------------------------------------------------------
# Cycle detection → random-walk fallback
# ---------------------------------------------------------------------------

def test_cycle_triggers_fallback_and_converges() -> None:
    # Topology that GUARANTEES a greedy cycle, then fallback converges.
    #
    # Fingerprints:  S=0.90, X=0.50, C=0.10
    # Adjacency:     S→[X],  X→[S, C]
    # target_fp = [0.90]
    #
    # Greedy from S: only neighbor X (distance |0.50-0.90|=0.40).  Hop to X.
    # Greedy from X: neighbors [S, C].
    #   distance(S=0.90, target=0.90) = 0.00  ← closest
    #   distance(C=0.10, target=0.90) = 0.80
    #   Greedy selects S — but S is in visited → CYCLE DETECTED.
    # Fallback from X: rng.choice([S, C]).
    #   If C is chosen → convergence_predicate("C") = True → converged.
    #   If S is chosen → from S, only neighbor X; from X, try again. Budget=50.
    # With max_hops=50 and 50% per fallback step the probability of never
    # picking C is (0.5)^25 ≈ 3×10^-8 — effectively impossible.
    fps: Dict[str, List[float]] = {
        "S": [0.90],
        "X": [0.50],
        "C": [0.10],   # convergence target — fp far from target_fp (tests predicate-vs-fp split)
    }
    adj: Dict[str, List[str]] = {
        "S": ["X"],
        "X": ["S", "C"],
        "C": [],
    }
    rng = random.Random(42)
    result = route(
        source_id="S",
        target_fingerprint=_fp(0.9),
        peer_fingerprints=fps,
        peer_adjacency=adj,
        convergence_predicate=lambda nid: nid == "C",
        max_hops=50,
        rng=rng,
    )
    assert result.converged
    assert result.used_fallback
    assert "C" in result.path
    assert result.failure_mode == ""


def test_cycle_detection_does_not_revisit_before_fallback() -> None:
    # Verify that cycle detection fires exactly at the second visit to a node,
    # not later — i.e., the visited set is maintained correctly.
    fps = {"S": [0.1], "X": [0.5], "T": [0.9]}
    adj: Dict[str, List[str]] = {
        "S": ["X"],
        "X": ["S"],   # only back-edge → cycle immediately
        "T": [],
    }
    rng = random.Random(0)
    result = route(
        source_id="S",
        target_fingerprint=_fp(0.9),
        peer_fingerprints=fps,
        peer_adjacency=adj,
        convergence_predicate=lambda nid: nid == "T",
        max_hops=5,
        rng=rng,
    )
    # Fallback from X: only neighbor is S, which doesn't converge; budget runs out.
    assert not result.converged
    assert result.used_fallback
    assert result.failure_mode == "max_hops"


# ---------------------------------------------------------------------------
# Max-hops budget exhaustion
# ---------------------------------------------------------------------------

def test_max_hops_exhausted_without_convergence() -> None:
    # Long chain: S→A→B→C→... all in cluster A, target is at the far end.
    # Budget = 2 steps — not enough to reach T.
    fps = {"S": [0.1], "A": [0.3], "B": [0.5], "T": [0.9]}
    adj: Dict[str, List[str]] = {"S": ["A"], "A": ["B"], "B": ["T"], "T": []}
    result = route(
        source_id="S",
        target_fingerprint=_fp(0.9),
        peer_fingerprints=fps,
        peer_adjacency=adj,
        convergence_predicate=lambda nid: nid == "T",
        max_hops=2,
    )
    assert not result.converged
    assert result.failure_mode == "max_hops"
    assert result.hops == 2
    assert not result.used_fallback


def test_max_hops_exhausted_during_fallback() -> None:
    # Force fallback then let budget run out.
    fps = {"S": [0.1], "X": [0.5]}
    adj: Dict[str, List[str]] = {"S": ["X"], "X": ["S"]}
    rng = random.Random(7)
    result = route(
        source_id="S",
        target_fingerprint=_fp(0.9),
        peer_fingerprints=fps,
        peer_adjacency=adj,
        convergence_predicate=lambda nid: False,  # never converges
        max_hops=4,
        rng=rng,
    )
    assert not result.converged
    assert result.failure_mode == "max_hops"
    assert result.used_fallback


# ---------------------------------------------------------------------------
# Dead-end (no peers) in both phases
# ---------------------------------------------------------------------------

def test_dead_end_in_spectral_phase() -> None:
    fps = {"S": [0.1], "D": [0.5]}
    adj: Dict[str, List[str]] = {"S": ["D"], "D": []}  # D has no outbound edges
    result = route(
        source_id="S",
        target_fingerprint=_fp(0.9),
        peer_fingerprints=fps,
        peer_adjacency=adj,
        convergence_predicate=lambda nid: nid == "T",
        max_hops=10,
    )
    assert not result.converged
    assert result.failure_mode == "no_peers"
    assert not result.used_fallback


def test_dead_end_in_fallback_phase() -> None:
    # Topology that forces cycle → fallback → dead end or budget exhaustion.
    #
    # Fingerprints:  S=0.90, X=0.50, D=0.10
    # Adjacency:     S→[X],  X→[S, D],  D→[]
    # target_fp = [0.90]
    #
    # Greedy from S: picks X (only neighbor).
    # Greedy from X: neighbors [S, D].
    #   distance(S=0.90, 0.90) = 0.00  ← closest → but S is visited → CYCLE.
    # Fallback from X: rng.choice([S, D]).
    #   D → dead end (no outgoing edges) → failure_mode="no_peers", used_fallback=True.
    #   S → X → fallback again → eventually D or budget expires.
    fps: Dict[str, List[float]] = {
        "S": [0.90],
        "X": [0.50],
        "D": [0.10],
    }
    adj: Dict[str, List[str]] = {
        "S": ["X"],
        "X": ["S", "D"],
        "D": [],
    }
    rng = random.Random(0)
    result = route(
        source_id="S",
        target_fingerprint=_fp(0.9),
        peer_fingerprints=fps,
        peer_adjacency=adj,
        convergence_predicate=lambda nid: nid == "T",  # T unreachable
        max_hops=10,
        rng=rng,
    )
    assert not result.converged
    assert result.used_fallback
    assert result.failure_mode in {"no_peers", "max_hops"}


# ---------------------------------------------------------------------------
# Multi-dimensional fingerprints
# ---------------------------------------------------------------------------

def test_multidimensional_fingerprint_routing() -> None:
    # Full k=4 fingerprint vectors — confirms spectral_distance zero-padding
    # and that the routing metric works in higher dimensions.
    fps: Dict[str, List[float]] = {
        "S":  [0.12, 0.08, 0.05, 0.03],
        "N1": [0.15, 0.10, 0.07, 0.04],   # cluster A — closer to S
        "N2": [0.45, 0.38, 0.30, 0.22],   # midpoint
        "T":  [0.92, 0.85, 0.78, 0.70],   # cluster B — target
    }
    adj: Dict[str, List[str]] = {
        "S":  ["N1", "T"],   # T is much closer in L2 → greedy picks T directly
        "N1": ["N2"],
        "N2": ["T"],
        "T":  [],
    }
    target_fp = [0.92, 0.85, 0.78, 0.70]
    result = route(
        source_id="S",
        target_fingerprint=target_fp,
        peer_fingerprints=fps,
        peer_adjacency=adj,
        convergence_predicate=lambda nid: nid == "T",
        max_hops=10,
    )
    assert result.converged
    assert result.hops == 1
    assert result.path == ("S", "T")
    assert not result.used_fallback


def test_mixed_dimension_fingerprints_zero_padded() -> None:
    # Source has 1D fp; peers have 3D fps.  spectral_distance pads to equal length.
    fps: Dict[str, List[float]] = {
        "S":  [0.1],
        "A":  [0.1, 0.1, 0.1],   # L2 distance from target [0.9,0.9,0.9] ≈ 1.39
        "B":  [0.8, 0.8, 0.8],   # L2 distance from target ≈ 0.17 — B is much closer
    }
    adj: Dict[str, List[str]] = {"S": ["A", "B"], "A": [], "B": []}
    result = route(
        source_id="S",
        target_fingerprint=[0.9, 0.9, 0.9],
        peer_fingerprints=fps,
        peer_adjacency=adj,
        convergence_predicate=lambda nid: nid == "B",
        max_hops=5,
    )
    assert result.converged
    assert result.hops == 1
    assert result.path[-1] == "B"


# ---------------------------------------------------------------------------
# Reproducibility with seeded rng
# ---------------------------------------------------------------------------

def test_seeded_rng_produces_reproducible_paths() -> None:
    # Graph with genuine randomness in the fallback phase.
    # S→X, then cycle (greedy from X picks S=visited), then fallback wanders
    # among [S, X_alt, A, B] for several hops before budget exhaustion.
    # The key property: two independent Random(seed) instances with the same
    # seed must produce identical paths (reproducibility is determined by seed,
    # not shared mutable state).
    fps = {"S": [0.9], "X": [0.5], "A": [0.3], "B": [0.1], "C": [0.2]}
    adj: Dict[str, List[str]] = {
        "S": ["X"],
        "X": ["S", "A", "B", "C"],  # cycle at S; fallback picks among A/B/C/S repeatedly
        "A": ["B", "C"],
        "B": ["A", "C"],
        "C": ["A", "B"],
    }

    def _run(seed: int) -> RoutingResult:
        return route(
            source_id="S",
            target_fingerprint=_fp(0.9),
            peer_fingerprints=fps,
            peer_adjacency=adj,
            convergence_predicate=lambda nid: False,  # never converges; path determined by rng
            max_hops=10,
            rng=random.Random(seed),
        )

    # Same seed must always produce the same path — the core reproducibility property.
    # Each call uses a fresh Random(99) instance; equality proves seed-determinism.
    results = [_run(99) for _ in range(5)]
    assert all(r.path == results[0].path for r in results), \
        "same seed must always produce the same path"

    # Confirm the fallback was actually exercised (rng calls happened).
    assert results[0].used_fallback
    assert results[0].hops > 1


# ---------------------------------------------------------------------------
# RoutingResult immutability
# ---------------------------------------------------------------------------

def test_routing_result_is_frozen() -> None:
    fps, adj = _make_cluster_graph()
    result = route(
        source_id="n0",
        target_fingerprint=_fp(0.9),
        peer_fingerprints=fps,
        peer_adjacency=adj,
        convergence_predicate=_cluster_b_predicate,
    )
    with pytest.raises((AttributeError, TypeError)):
        result.converged = False  # type: ignore[misc]


def test_routing_result_path_is_immutable_tuple() -> None:
    # path must be a tuple, not a list.  The original implementation used List[str]
    # which allowed result.path.append("MUTATED") to succeed silently despite
    # the frozen dataclass.  A tuple path prevents this class of post-return mutation.
    fps, adj = _make_cluster_graph()
    result = route(
        source_id="n0",
        target_fingerprint=_fp(0.9),
        peer_fingerprints=fps,
        peer_adjacency=adj,
        convergence_predicate=_cluster_b_predicate,
    )
    assert isinstance(result.path, tuple)
    with pytest.raises(AttributeError):
        result.path.append("MUTATED")  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# Scope guard: no gossip wiring in this module
# ---------------------------------------------------------------------------

def test_module_does_not_import_gossip_transport() -> None:
    import ilc_core.network.d2d.spectral_routing_runtime as mod
    import sys
    # The routing primitive must not pull in gossip_transport or D2d wiring.
    # D2d gossip wiring requires H-013 (sealed-sender ADR) — not yet authorized.
    assert "ilc_core.network.d2d.gossip_transport" not in sys.modules or (
        "gossip_transport" not in dir(mod)
    )
    assert not hasattr(mod, "GossipPeerRegistry")
    assert not hasattr(mod, "GossipTransport")


# ---------------------------------------------------------------------------
# Input validation: max_hops=0 and empty target_fingerprint
# ---------------------------------------------------------------------------

def test_max_hops_zero_raises_value_error() -> None:
    # max_hops=0 would produce RoutingResult(hops=0, failure_mode="max_hops"),
    # which is paradoxical (budget exhausted before any attempt).  The guard
    # at the entry of route() rejects this explicitly.
    fps, adj = _make_cluster_graph()
    with pytest.raises(ValueError, match="max_hops must be >= 1"):
        route(
            source_id="n0",
            target_fingerprint=_fp(0.9),
            peer_fingerprints=fps,
            peer_adjacency=adj,
            convergence_predicate=_cluster_b_predicate,
            max_hops=0,
        )


def test_empty_target_fingerprint_raises_value_error() -> None:
    # An empty target_fingerprint collapses all spectral distances to zero,
    # making greedy selection effectively arbitrary and almost certainly a
    # caller bug.  The guard at route() entry rejects it explicitly.
    fps, adj = _make_cluster_graph()
    with pytest.raises(ValueError, match="target_fingerprint must be a non-empty list"):
        route(
            source_id="n0",
            target_fingerprint=[],
            peer_fingerprints=fps,
            peer_adjacency=adj,
            convergence_predicate=_cluster_b_predicate,
        )


def test_module_does_not_wire_gossip_channel() -> None:
    import ilc_core.network.d2d.spectral_routing_runtime as mod
    # No CDL-060 or CDL-061 gossip channel present — those are for centrality
    # and transport; H-015 is a primitive only.
    assert not hasattr(mod, "CDL_060_DEPENDENCY")
    assert not hasattr(mod, "CDL_061_DEPENDENCY")


# ---------------------------------------------------------------------------
# PRNG policy: default rng must be secrets.SystemRandom (ILC Security §2)
# ---------------------------------------------------------------------------

def test_default_rng_is_system_random() -> None:
    # When no rng is passed, the fallback must use secrets.SystemRandom, not
    # random.Random (Mersenne Twister is banned in ilc_core/ per ILC Coding
    # Security Standards §2 — predictable PRNG compromises Sybil protections).
    import secrets
    fps = {"S": [0.1], "X": [0.5]}
    adj: Dict[str, List[str]] = {"S": ["X"], "X": ["S"]}
    # Force fallback to exercise the default rng path.  convergence never fires.
    result = route(
        source_id="S",
        target_fingerprint=_fp(0.9),
        peer_fingerprints=fps,
        peer_adjacency=adj,
        convergence_predicate=lambda nid: False,
        max_hops=4,
        # rng omitted — must default to secrets.SystemRandom()
    )
    # Result is deterministic in structure even with SystemRandom.
    assert not result.converged
    assert result.used_fallback
    # Verify the module attribute, not just runtime behavior.
    import inspect
    import ilc_core.network.d2d.spectral_routing_runtime as mod
    src = inspect.getsource(mod.route)
    assert "secrets.SystemRandom()" in src


# ---------------------------------------------------------------------------
# Tie-breaking: equal-distance unvisited neighbor must not trigger fallback
# ---------------------------------------------------------------------------

def test_equal_distance_tie_prefers_unvisited_over_fallback() -> None:
    # Topology:  S → [X, T]  where both X and T are equidistant from target.
    # S is the source; after one hop to X, greedy from X finds:
    #   neighbors: [S, T]
    #   distance(S, target) == distance(T, target)  [equal tie]
    #   S is visited; T is not.
    # Correct behavior: take T (equally-close unvisited alternative), converge.
    # Incorrect behavior (pre-fix): pick S (min() returns first minimum, which
    # could be visited) → trigger fallback unnecessarily.
    #
    # Fingerprints: S=0.90, X=0.50, T=0.90  (S and T equidistant from target 0.90)
    fps: Dict[str, List[float]] = {
        "S": [0.90],
        "X": [0.50],
        "T": [0.90],
    }
    adj: Dict[str, List[str]] = {
        "S": ["X"],
        "X": ["S", "T"],
        "T": [],
    }
    result = route(
        source_id="S",
        target_fingerprint=_fp(0.90),
        peer_fingerprints=fps,
        peer_adjacency=adj,
        convergence_predicate=lambda nid: nid == "T",
        max_hops=10,
        rng=random.Random(0),
    )
    assert result.converged
    assert result.path[-1] == "T"
    assert not result.used_fallback


# ---------------------------------------------------------------------------
# Missing fingerprint: distinct failure mode from no adjacency peers
# ---------------------------------------------------------------------------

def test_missing_fingerprint_returns_distinct_failure_mode() -> None:
    # S → M → T where M exists in adjacency but has no fingerprint entry.
    # This simulates fingerprint metadata lag: topology is intact but the
    # fingerprint propagation for M has not arrived yet.
    # Expected: failure_mode="missing_fingerprint", NOT "no_peers".
    # "no_peers" would imply a topology dead-end; this is a metadata issue.
    fps: Dict[str, List[float]] = {
        "S": [0.1],
        # M deliberately absent from peer_fingerprints
        "T": [0.9],
    }
    adj: Dict[str, List[str]] = {
        "S": ["M"],   # S can reach M; M has adjacency
        "M": ["T"],
        "T": [],
    }
    result = route(
        source_id="S",
        target_fingerprint=_fp(0.9),
        peer_fingerprints=fps,
        peer_adjacency=adj,
        convergence_predicate=lambda nid: nid == "T",
        max_hops=10,
    )
    assert not result.converged
    assert result.failure_mode == "missing_fingerprint"
    assert not result.used_fallback
