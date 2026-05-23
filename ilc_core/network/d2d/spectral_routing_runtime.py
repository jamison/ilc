# SPDX-License-Identifier: AGPL-3.0-or-later
# H-015: Greedy spectral descent routing with random-walk fallback.
#
# Gate: H-014 positive (SIM-ROUTING-01 verdict=pass).
#
# Algorithm (from SIM-ROUTING-01 §7):
#   1. Primary path: greedy spectral descent
#      At each hop, move to the peer whose spectral fingerprint minimises
#      spectral_distance to the target fingerprint.  Terminate on convergence
#      (convergence_predicate returns True) or cycle detection.
#   2. Fallback: on cycle detection, switch to random walk for the remaining
#      hop budget.  Random walk cannot cycle-fail and captures any missed
#      cluster edges from closely-spaced cluster centres.
#   3. Failure: if the hop budget is exhausted without convergence, return
#      RoutingResult with converged=False and failure_mode="max_hops".
#
# Fingerprint dimensionality note (SIM-ROUTING-01 §2):
#   The simulation used 1D scalar fingerprints (λ₂ only) as a conservative
#   lower bound.  This implementation uses the full k-dimensional fingerprint
#   from HyperEdge.spectral_fingerprint when available, which provides richer
#   cluster separation — particularly for closely-spaced clusters — and is
#   expected to further reduce cycle failures beyond the SIM results.
#   Callers may pass 1D fingerprints; spectral_distance zero-pads shorter vectors.
#
# Activation boundary:
#   This module implements the routing primitive only.  It is NOT wired into
#   D2d gossip.  Gossip wiring requires H-013 (sealed-sender ADR) + explicit
#   authorization.  See SIM-ROUTING-01 §8 operational boundaries.
#
# `run_h015_spectral_routing_runtime_verdict=pass`
from __future__ import annotations

import secrets
from dataclasses import dataclass
from typing import Callable, List, Mapping, Optional, Protocol, Sequence, Tuple, TypeVar

from ilc_core.analysis.spectral_utils import spectral_distance


SPECTRAL_ROUTING_RUNTIME_VERSION = "spectral_routing_runtime_h015.v0.1"
H014_DEPENDENCY = "run_h014_sim_routing_01_verdict=pass"

# Default hop budget: 3 × ⌈log₂(N)⌉ at N=500 testnet = 27.
# Callers should supply a budget matched to their network size.
DEFAULT_MAX_HOPS: int = 27

_T = TypeVar("_T")


class _ChoiceRng(Protocol):
    """Minimal RNG interface required by the random-walk fallback."""

    def choice(self, seq: Sequence[_T]) -> _T:
        ...


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RoutingResult:
    """Outcome of a single routing attempt.

    converged:       True if convergence_predicate returned True at some hop.
    path:            Ordered tuple of node IDs visited, including the source.
                     On failure the path still records hops made before giving up.
                     Immutable: path is a tuple, not a list.
    hops:            Number of hops taken (len(path) - 1).
    failure_mode:    "": success;
                     "max_hops": budget exhausted;
                     "no_peers": adjacency dead end (no outbound edges at current node);
                     "missing_fingerprint": outbound neighbors exist in adjacency but
                     none have entries in peer_fingerprints — indicates metadata lag
                     or misconfiguration, not a topology dead end.
    used_fallback:   True if the random-walk fallback was triggered (cycle detected
                     on the spectral phase).  False if spectral descent reached the
                     target directly or failed without triggering a cycle.
    """
    converged: bool
    path: Tuple[str, ...]
    hops: int
    failure_mode: str
    used_fallback: bool


# ---------------------------------------------------------------------------
# Core routing function
# ---------------------------------------------------------------------------

def route(
    source_id: str,
    target_fingerprint: List[float],
    peer_fingerprints: Mapping[str, List[float]],
    peer_adjacency: Mapping[str, List[str]],
    convergence_predicate: Callable[[str], bool],
    *,
    max_hops: int = DEFAULT_MAX_HOPS,
    rng: Optional[_ChoiceRng] = None,
) -> RoutingResult:
    """Route from source toward the target epistemic cluster.

    Args:
        source_id:
            ID of the starting node.
        target_fingerprint:
            k-dimensional spectral fingerprint of the target node (or its
            cluster centre).  Should be the full HyperEdge.spectral_fingerprint
            vector; 1D scalar is accepted and treated as a conservative lower
            bound (SIM-ROUTING-01 §2).
        peer_fingerprints:
            Mapping from node ID → spectral fingerprint.  Must include entries
            for source_id and all peers reachable via peer_adjacency.  Nodes
            absent from this mapping trigger failure_mode="missing_fingerprint"
            when ALL neighbors lack fingerprints, or are skipped during greedy
            selection when only some are absent.
        peer_adjacency:
            Mapping from node ID → list of peer node IDs (directed; the routing
            function follows outbound edges only).
        convergence_predicate:
            Called with the current node ID at each step (including source before
            the first hop).  Return True to signal that the node is in the target
            epistemic cluster and routing is complete.
        max_hops:
            Maximum number of hops before declaring failure.  Defaults to
            DEFAULT_MAX_HOPS (27, calibrated for N=500 testnet per SIM-ROUTING-01).
        rng:
            Optional object implementing ``choice(seq)`` for the random-walk
            fallback.  If None, a secrets.SystemRandom() instance is used — the
            correct default for production routing (PRNG ban, ILC Coding
            Security Standards §2).  Tests may pass a deterministic fake that
            implements the same minimal interface.

    Returns:
        RoutingResult with the outcome, path (immutable tuple), and diagnostics.

    Note on gossip wiring:
        This function operates on an in-process graph.  It does NOT perform any
        network I/O.  Integration with D2d gossip requires H-013 (sealed-sender
        ADR) and is explicitly out of scope for H-015.

    Note on target_fingerprint / convergence_predicate coupling:
        These two arguments are independent.  Routing greedily descends toward
        target_fingerprint; convergence_predicate determines when the destination
        is reached.  Callers must ensure they point at the same cluster; a mismatch
        produces a valid RoutingResult but with potentially misleading path geometry.
    """
    if max_hops < 1:
        raise ValueError(
            f"max_hops must be >= 1; got {max_hops}. "
            "Pass at least 1 to allow any routing attempt."
        )
    if not target_fingerprint:
        raise ValueError(
            "target_fingerprint must be a non-empty list; got empty sequence. "
            "Pass at least a 1D fingerprint (λ₂ scalar) per SIM-ROUTING-01 §2."
        )

    if rng is None:
        rng = secrets.SystemRandom()

    # Check convergence at source before the first hop.
    if convergence_predicate(source_id):
        return RoutingResult(
            converged=True,
            path=(source_id,),
            hops=0,
            failure_mode="",
            used_fallback=False,
        )

    path: List[str] = [source_id]
    current = source_id
    visited: set[str] = {current}

    # -----------------------------------------------------------------------
    # Phase 1: greedy spectral descent
    # -----------------------------------------------------------------------
    for _ in range(max_hops):
        neighbors_in_adj = list(peer_adjacency.get(current, []))
        if not neighbors_in_adj:
            return RoutingResult(
                converged=False,
                path=tuple(path),
                hops=len(path) - 1,
                failure_mode="no_peers",
                used_fallback=False,
            )

        neighbors = [nb for nb in neighbors_in_adj if nb in peer_fingerprints]
        if not neighbors:
            # Adjacency exists but no neighbor has a fingerprint entry.
            # This is a metadata lag / misconfiguration, not a topology dead end.
            return RoutingResult(
                converged=False,
                path=tuple(path),
                hops=len(path) - 1,
                failure_mode="missing_fingerprint",
                used_fallback=False,
            )

        best = min(
            neighbors,
            key=lambda nb: spectral_distance(peer_fingerprints[nb], target_fingerprint),
        )

        if best in visited:
            # Before triggering fallback, check for an equally-close unvisited
            # neighbor.  Equal-distance ties should not force fallback when a
            # valid unvisited alternative exists.
            best_dist = spectral_distance(peer_fingerprints[best], target_fingerprint)
            alternative = next(
                (
                    nb for nb in neighbors
                    if nb not in visited
                    and spectral_distance(peer_fingerprints[nb], target_fingerprint) == best_dist
                ),
                None,
            )
            if alternative is not None:
                best = alternative
            else:
                # Genuine cycle: hand off to random-walk fallback.
                return _random_walk_fallback(
                    current=current,
                    path=path,
                    peer_adjacency=peer_adjacency,
                    convergence_predicate=convergence_predicate,
                    remaining_hops=max_hops - (len(path) - 1),
                    rng=rng,
                )

        visited.add(best)
        current = best
        path.append(current)

        if convergence_predicate(current):
            return RoutingResult(
                converged=True,
                path=tuple(path),
                hops=len(path) - 1,
                failure_mode="",
                used_fallback=False,
            )

    return RoutingResult(
        converged=False,
        path=tuple(path),
        hops=len(path) - 1,
        failure_mode="max_hops",
        used_fallback=False,
    )


# ---------------------------------------------------------------------------
# Random-walk fallback
# ---------------------------------------------------------------------------

def _random_walk_fallback(
    current: str,
    path: List[str],
    peer_adjacency: Mapping[str, List[str]],
    convergence_predicate: Callable[[str], bool],
    remaining_hops: int,
    rng: _ChoiceRng,
) -> RoutingResult:
    """Random walk from `current` using the remaining hop budget.

    Called exclusively by route() on cycle detection.  Cannot itself cycle-fail
    because it does not track visited nodes — the budget is the only termination
    criterion besides convergence.  This matches the SIM-ROUTING-01 design: random
    walk with a generous budget achieves 99.85–100% convergence.

    The rng argument must be a secrets.SystemRandom() instance for production use
    (ILC Coding Security Standards §2).  Deterministic test fakes are accepted
    only when they implement the same minimal ``choice(seq)`` interface.
    """
    for _ in range(remaining_hops):
        neighbors = list(peer_adjacency.get(current, []))
        if not neighbors:
            return RoutingResult(
                converged=False,
                path=tuple(path),
                hops=len(path) - 1,
                failure_mode="no_peers",
                used_fallback=True,
            )
        current = rng.choice(neighbors)
        path.append(current)
        if convergence_predicate(current):
            return RoutingResult(
                converged=True,
                path=tuple(path),
                hops=len(path) - 1,
                failure_mode="",
                used_fallback=True,
            )

    return RoutingResult(
        converged=False,
        path=tuple(path),
        hops=len(path) - 1,
        failure_mode="max_hops",
        used_fallback=True,
    )
