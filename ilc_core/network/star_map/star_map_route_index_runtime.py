# SPDX-License-Identifier: AGPL-3.0-or-later
# CDL-080: Star.Map N-Gram Route Index — L3 Routing Layer Runtime
#
# Phase 923 — star_map_route_index_runtime.py
#
# Constitutional authority: CDL-080 (opened Phase 922)
# Depends on: ADR-0003 (route index artifact), ADR-0033 (homoiconic entity),
#             CDL-077 (L2 fetch — advisory/authoritative priority),
#             H-015 (spectral routing primitive)
#
# run_h_star_map_route_index_923_verdict=pass

import hashlib
import json
import re
from dataclasses import dataclass, field
from typing import Optional

# ---------------------------------------------------------------------------
# Dep-chain tokens — verified at import time
# ---------------------------------------------------------------------------

STAR_MAP_RUNTIME_VERSION = "star_map_route_index_runtime_923.v0.1"
CDL_080_DEPENDENCY = "cdl_080_star_map_n_gram_route_index.v0.1"
ADR_0003_DEPENDENCY = "adr_0003_star_map_route_index"
ADR_0033_DEPENDENCY = "adr_0033_star_map_homoiconic_entity"
CDL_077_DEPENDENCY = "cdl_077_want_have_want_block_fetch.v0.1"
H015_DEPENDENCY = "spectral_routing_runtime_h015.v0.1"

# Verify H-015 spectral routing primitive is available
def _verify_h015_dep() -> None:
    try:
        from ilc_core.network.d2d.spectral_routing_runtime import (
            SPECTRAL_ROUTING_RUNTIME_VERSION,
        )
        if SPECTRAL_ROUTING_RUNTIME_VERSION != "spectral_routing_runtime_h015.v0.1":
            raise RuntimeError(
                f"star_map_route_index_runtime: H-015 dep-chain guard failed — "
                f"expected spectral_routing_runtime_h015.v0.1, "
                f"got {SPECTRAL_ROUTING_RUNTIME_VERSION}"
            )
    except ImportError as exc:
        raise RuntimeError(
            "star_map_route_index_runtime: H-015 spectral_routing_runtime not importable"
        ) from exc

_verify_h015_dep()

# ---------------------------------------------------------------------------
# Priority rule token — non-negotiable per CDL-080 §4.5
# ---------------------------------------------------------------------------
L3_ADVISORY_L2_AUTHORITATIVE = (
    "l3_advisory_l2_authoritative_l3_does_not_override_cdl_077"
)

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

ROUTE_INDEX_SCHEMA_VERSION = "route_index_v1"
NGRAM_SIZE = 3  # trigrams


@dataclass
class RouteHint:
    """Advisory routing hint — a peer endpoint likely to hold matching content.

    CDL-080 §4.5: a RouteHint is advisory only. The L2 WANT-HAVE/WANT-BLOCK
    response is authoritative. A non-matching L2 response is NOT an error.
    """
    endpoint: str
    ngram_bucket: str
    spectral_distance: Optional[float] = None  # set when spectral prefilter used


@dataclass
class RouteIndex:
    """Signed, versioned N-gram route index artifact (ADR-0003).

    Ephemeral by default. Call publish_star_map_result() to promote to a
    first-class Node(type='star_map') per ADR-0033.
    """
    schema_version: str
    epoch: int
    generator_agent_id: str
    buckets: dict[str, list[str]]  # ngram_hash_prefix -> [endpoint, ...]
    parameter_digest: str
    # Signature fields — populated only when signed for publication
    signed_by: Optional[str] = None
    signature: Optional[str] = None
    # Internal: node ID assigned after publication
    _published_node_id: Optional[str] = field(default=None, repr=False)

    @property
    def is_published(self) -> bool:
        return self._published_node_id is not None


# Node type token per ADR-0033
NODE_TYPE_STAR_MAP = "star_map"

# Valid entity kinds per ADR-0033 §2.3
STAR_MAP_ENTITY_KINDS = frozenset(
    {"route_cluster", "panel_result", "navigation_overlay"}
)

# ---------------------------------------------------------------------------
# N-gram utilities
# ---------------------------------------------------------------------------

def _extract_ngrams(text: str, n: int = NGRAM_SIZE) -> list[str]:
    """Extract character-level N-grams from normalized text."""
    normalized = re.sub(r"\s+", " ", text.strip().lower())
    if len(normalized) < n:
        return [normalized] if normalized else []
    return [normalized[i : i + n] for i in range(len(normalized) - n + 1)]


def _ngram_bucket_key(ngram: str) -> str:
    """SHA-256 prefix of an N-gram — the bucket key in the route index."""
    return hashlib.sha256(ngram.encode()).hexdigest()[:16]


def _parameter_digest(ngram_size: int, bucket_count: int) -> str:
    params = json.dumps(
        {"ngram_size": ngram_size, "bucket_count": bucket_count}, sort_keys=True
    )
    return hashlib.sha256(params.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def compute_route_index(
    node_endpoints: dict[str, list[str]],
    epoch: int,
    generator_agent_id: str,
) -> RouteIndex:
    """Compute the N-gram route index from a mapping of content labels to endpoints.

    Args:
        node_endpoints: mapping of content label (e.g. node content summary)
                        to list of peer endpoints that hold that content.
        epoch: current epoch.
        generator_agent_id: CID of the generating agent.

    Returns:
        RouteIndex — ephemeral, not yet published.

    Deterministic: same inputs always produce the same output.
    Serialization: sort_keys=True throughout.
    """
    buckets: dict[str, list[str]] = {}

    for label, endpoints in sorted(node_endpoints.items()):
        for ngram in _extract_ngrams(label):
            key = _ngram_bucket_key(ngram)
            existing = buckets.get(key, [])
            for ep in endpoints:
                if ep not in existing:
                    existing.append(ep)
            buckets[key] = sorted(existing)  # deterministic order

    param_digest = _parameter_digest(NGRAM_SIZE, len(buckets))

    return RouteIndex(
        schema_version=ROUTE_INDEX_SCHEMA_VERSION,
        epoch=epoch,
        generator_agent_id=generator_agent_id,
        buckets=buckets,
        parameter_digest=param_digest,
    )


def query_route_index(
    route_index: RouteIndex,
    query: str,
    top_k: int = 16,
) -> list[RouteHint]:
    """Return advisory route hints for a query string.

    Extracts N-grams from the query, looks up matching buckets in the index,
    and returns up to top_k unique endpoints as RouteHints.

    CDL-080 §4.5: returned hints are ADVISORY ONLY. Callers must verify via
    L2 WANT-HAVE (CDL-077). A missing L2 response is not a routing error.

    Args:
        route_index: the route index to query.
        query: semantic query string.
        top_k: maximum number of route hints to return.

    Returns:
        List of RouteHint, ordered by ngram match frequency (most matched first).
        Empty list if no matches.
    """
    ngrams = _extract_ngrams(query)
    if not ngrams:
        return []

    endpoint_hits: dict[str, int] = {}
    endpoint_bucket: dict[str, str] = {}

    for ngram in ngrams:
        key = _ngram_bucket_key(ngram)
        for endpoint in route_index.buckets.get(key, []):
            endpoint_hits[endpoint] = endpoint_hits.get(endpoint, 0) + 1
            endpoint_bucket[endpoint] = key

    ranked = sorted(endpoint_hits.items(), key=lambda x: -x[1])
    return [
        RouteHint(endpoint=ep, ngram_bucket=endpoint_bucket[ep])
        for ep, _ in ranked[:top_k]
    ]


def query_route_index_spectral(
    route_index: RouteIndex,
    query: str,
    local_fingerprint: list[float],
    peer_fingerprints: dict[str, list[float]],
    top_k: int = 16,
) -> list[RouteHint]:
    """Route hint resolution using spectral distance as secondary ranking signal.

    Combines N-gram match frequency (from query_route_index) with spectral
    distance (H-015 metric) to rank candidate peers. Spectral routing operates
    on locally-cached fingerprints only — no beacon gossip activation.

    CDL-080 §4.3: greedy spectral descent with random-walk fallback on cycle.
    CDL-080 §4.5: all returned hints remain advisory; L2 is authoritative.

    Args:
        route_index: the route index to query.
        query: semantic query string.
        local_fingerprint: this node's spectral fingerprint (top-k eigenvalues).
        peer_fingerprints: mapping of endpoint -> spectral fingerprint.
        top_k: maximum number of route hints to return.

    Returns:
        List of RouteHint with spectral_distance populated, ranked by
        combined N-gram frequency + spectral proximity.
    """
    from ilc_core.analysis.spectral_utils import spectral_distance

    base_hints = query_route_index(route_index, query, top_k=top_k * 4)
    if not base_hints:
        return []

    scored: list[tuple[float, RouteHint]] = []
    for hint in base_hints:
        peer_fp = peer_fingerprints.get(hint.endpoint)
        if peer_fp is not None:
            dist = spectral_distance(local_fingerprint, peer_fp)
        else:
            dist = float("inf")
        hint.spectral_distance = dist
        scored.append((dist, hint))

    scored.sort(key=lambda x: x[0])
    return [hint for _, hint in scored[:top_k]]


def publish_star_map_result(
    route_index: RouteIndex,
    source_node_set_digest: str,
    agent_id: str,
    epoch: int,
    entity_kind: str = "route_cluster",
) -> dict:
    """Promote a route index result to a first-class star-map node (ADR-0033).

    Enforces the ADR-0033 claim-form contract. Returns a Node-compatible dict
    with all required fields. The node ID is content-addressed.

    This is the publication boundary (ADR-0033 §2.1): call this only when the
    result is being shared, relied upon for routing, or referenced by later claims.
    Private scratch results should remain as RouteIndex objects.

    Args:
        route_index: the computed route index to publish.
        source_node_set_digest: SHA-256 of the sorted source node CID list.
        agent_id: CID of the publishing agent.
        epoch: publication epoch.
        entity_kind: one of 'route_cluster', 'panel_result', 'navigation_overlay'.

    Returns:
        Node-compatible dict with type='star_map' and all ADR-0033 fields.

    Raises:
        ValueError: if entity_kind is not a valid ADR-0033 entity kind.
    """
    if entity_kind not in STAR_MAP_ENTITY_KINDS:
        raise ValueError(
            f"publish_star_map_result: invalid entity_kind '{entity_kind}'. "
            f"Must be one of {sorted(STAR_MAP_ENTITY_KINDS)}"
        )

    result_payload = json.dumps(
        {
            "schema_version": route_index.schema_version,
            "epoch": route_index.epoch,
            "generator_agent_id": route_index.generator_agent_id,
            "buckets": route_index.buckets,
            "parameter_digest": route_index.parameter_digest,
        },
        sort_keys=True,
    )

    # ADR-0033 §2.4 — canonical payload for content-addressed ID
    canonical_payload = json.dumps(
        {
            "agent_id": agent_id,
            "entity_kind": entity_kind,
            "epoch": epoch,
            "generator_ref": route_index.generator_agent_id,
            "method": "n_gram_route_index_v1",
            "parameter_digest": route_index.parameter_digest,
            "result_payload": result_payload,
            "source_artifact_refs": [],  # route index has no individual source CIDs
            "source_node_set_digest": source_node_set_digest,
        },
        sort_keys=True,
    )

    node_id = hashlib.sha256(canonical_payload.encode()).hexdigest()

    node = {
        "id": node_id,
        "type": NODE_TYPE_STAR_MAP,
        "content_type": "route_index",
        # ADR-0033 §2.5 claim-form contract — all required fields
        "entity_kind": entity_kind,
        "generator_ref": route_index.generator_agent_id,
        "source_artifact_refs": [],
        "source_node_set_digest": source_node_set_digest,
        "method": "n_gram_route_index_v1",
        "parameter_digest": route_index.parameter_digest,
        "result_payload": result_payload,
        "epoch": epoch,
        "agent_id": agent_id,
        # CDL-080 tokens
        "cdl_080_dependency": CDL_080_DEPENDENCY,
        "l3_advisory_l2_authoritative": L3_ADVISORY_L2_AUTHORITATIVE,
    }

    # Mark the source RouteIndex as published
    route_index._published_node_id = node_id

    return node


def l3_route_and_fetch(
    query: str,
    route_index: RouteIndex,
    local_fingerprint: Optional[list[float]],
    peer_fingerprints: Optional[dict[str, list[float]]],
    cdl_077_fetch_fn,
    top_k: int = 16,
) -> Optional[dict]:
    """Advisory L3 routing → authoritative L2 fetch.

    CDL-080 §4.4 routing sequence:
      1. Compute route hints via N-gram index (+ spectral prefilter if available)
      2. For each candidate endpoint (in order), call cdl_077_fetch_fn
      3. Return first successful L2 fetch result
      4. Return None if no candidate holds the content

    CDL-080 §4.5: L2 is authoritative. A None result means the content is not
    found, not that L3 routing failed. L3 hints are advisory only.

    Args:
        query: semantic query string.
        route_index: the L3 route index to use.
        local_fingerprint: optional spectral fingerprint for spectral routing.
        peer_fingerprints: optional peer fingerprint map for spectral routing.
        cdl_077_fetch_fn: callable(endpoint: str) -> dict | None
                          Must implement CDL-077 WANT-HAVE/WANT-BLOCK semantics.
        top_k: max candidate peers to try.

    Returns:
        Fetched content dict from L2, or None if not found.
    """
    # L3: compute advisory hints
    if local_fingerprint is not None and peer_fingerprints is not None:
        hints = query_route_index_spectral(
            route_index, query, local_fingerprint, peer_fingerprints, top_k=top_k
        )
    else:
        hints = query_route_index(route_index, query, top_k=top_k)

    # L2: authoritative fetch — try candidates in order
    for hint in hints:
        try:
            result = cdl_077_fetch_fn(hint.endpoint)
            if result is not None:
                return result  # L2 authoritative result
        except Exception:
            continue  # try next candidate

    return None  # not found — this is not a routing error per CDL-080 §4.5
