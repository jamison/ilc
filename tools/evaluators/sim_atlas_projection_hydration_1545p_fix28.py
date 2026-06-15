#!/usr/bin/env python3
"""Run the Fix28 Atlas projection and hydration SIM.

PUBLIC_RC_EXCLUDE: atlas_projection_hydration_sim_research_only
PUBLIC_RC_EXCLUDE_REASON: Research-only local projection/hydration SIM; no public serving,
live ZKP, canonical Genesis mutation, signing, minting, settlement, or public RC activation.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]

PHASE = "1545p-Fix28"
SIM_ID = "SIM-ATLAS-PROJECTION-HYDRATION-01"
SCHEMA_VERSION = "sim_atlas_projection_hydration_1545p_fix28.v0.1"
NODE0 = "artifact:genesis_intent_attestation_init_authority_map"

FIX22_GRAPH = REPO_ROOT / "out/genesis_atlas_full_repo_candidate_1545p_fix22.json"
FIX27_SUMMARY = REPO_ROOT / "out/sim_atlas_rewrite_candidate_generation_1545p_fix27.json"
FIX27_CANDIDATES = (
    REPO_ROOT / "out/atlas_research/genesis_atlas_rewrite_candidates_1545p_fix27.jsonl"
)

SLICES_OUT = (
    REPO_ROOT / "out/atlas_research/genesis_atlas_projection_hydration_slices_1545p_fix28.json"
)
SUMMARY_OUT = REPO_ROOT / "out/sim_atlas_projection_hydration_1545p_fix28.json"
REPORT_OUT = REPO_ROOT / "docs/sims/sim_atlas_projection_hydration_1545p_fix28_v0.1.md"
REVIEW_OUT = REPO_ROOT / "docs/specs/ilc_atlas_projection_hydration_review_1545p_fix28_v0.1.md"

AUTHORITY_EDGE_TYPES = {"GOVERNS", "ATTESTATION"}
SUPPORT_TRACE_EDGE_TYPES = {
    "IMPLEMENTS",
    "TESTS",
    "EVIDENCES",
    "REFERENCES_AUTHORITY",
    "DERIVED_FROM",
    "CLASSIFIED_BY",
}
CONTAINMENT_EDGE_TYPES = {
    "CONTAINS_FILE",
    "CONTAINS_GROUP",
    "CONTAINS_PARTITION",
    "SOURCE_TREE_MEMBER",
}
ACCEPTED_TYPED_TRACE_EDGE_TYPES = AUTHORITY_EDGE_TYPES | SUPPORT_TRACE_EDGE_TYPES
AUTHORITY_PREFIXES = ("adr:", "cdl:", "truth_primitive:", "policy:", "artifact:", "genesis_agent:")

OUTPUT_TOKENS = [
    "atlas_projection_hydration_sim_committed_phase_1545p_fix28",
    "atlas_transitivity_projection_checks_recorded_phase_1545p_fix28",
    "atlas_hydration_slice_budget_checks_recorded_phase_1545p_fix28",
    "atlas_semantic_loss_annotations_recorded_phase_1545p_fix28",
    "atlas_projection_hydration_not_public_serving_phase_1545p_fix28",
    "public_path_remains_blocked_phase_1545p_fix28",
]

NON_AUTHORIZATION_TOKENS = [
    "projection_hydration_local_only",
    "projection_hydration_not_public_serving_phase_1545p_fix28",
    "projection_hydration_not_live_zkp_phase_1545p_fix28",
    "projection_hydration_not_public_p2p_phase_1545p_fix28",
    "projection_hydration_not_canonical_graph_mutation_phase_1545p_fix28",
    "projection_hydration_not_genesis_signing_phase_1545p_fix28",
    "projection_hydration_not_minting_phase_1545p_fix28",
    "projection_hydration_not_settlement_phase_1545p_fix28",
    "projection_hydration_not_wallet_or_treasury_phase_1545p_fix28",
]

FORBIDDEN_LEAK_TOKENS = {
    "/Users/",
    "private key",
    "private_key",
    "wallet material",
    "route history",
    "sealed payload",
    "raw path",
}


def _canonical_dumps(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"


def _compact_dumps(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _stable_hash(payload: Any, length: int = 24) -> str:
    return hashlib.sha256(_compact_dumps(payload).encode("utf-8")).hexdigest()[:length]


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        dir=str(path.parent),
        prefix=f".{path.name}.",
        suffix=".tmp",
        text=True,
    )
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(tmp_path, path)
        path.chmod(0o644)
    except Exception:
        try:
            tmp_path.unlink()
        finally:
            raise


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"json_object_required:{path}")
    return payload


def _node_id(node: dict[str, Any]) -> str:
    value = node.get("candidate_id")
    if not isinstance(value, str) or not value:
        raise ValueError("atlas_candidate_node_missing_candidate_id")
    return value


def _edge_type(edge: dict[str, Any]) -> str:
    value = edge.get("edge_type")
    if not isinstance(value, str) or not value:
        raise ValueError("atlas_candidate_edge_missing_edge_type")
    return value


def _edge_endpoint(edge: dict[str, Any], key: str) -> str:
    value = edge.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"atlas_candidate_edge_missing_{key}")
    return value


def _ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 1.0
    return round(numerator / denominator, 6)


def _authority_class(node: dict[str, Any]) -> str:
    tier = str(node.get("tier") or node.get("canonicality_tier") or node.get("authority_tier") or "")
    kind = str(node.get("node_kind", ""))
    node_id = str(node.get("candidate_id", ""))
    if node_id == NODE0 or tier == "genesis_core" or kind in {"axiom_node", "authority_map"}:
        return "genesis_core"
    if node_id.startswith("cdl:") or "ratified_cdl" in tier:
        return "ratified_cdl"
    if node_id.startswith("adr:") or "accepted_adr" in tier:
        return "accepted_adr"
    if "runtime" in kind:
        return "runtime_guard"
    if "research" in tier or "generated" in tier:
        return "research_only"
    if "private" in tier or "excluded" in tier:
        return "unknown_private"
    return "support_only"


def _privacy_class(node: dict[str, Any]) -> str:
    fields = " ".join(
        str(node.get(key, ""))
        for key in ("tier", "authority_tier", "node_kind", "source_path", "public_path")
    ).lower()
    if "private" in fields or "excluded" in fields:
        return "private_capability_required"
    if "generated" in fields or "research" in fields:
        return "local_only"
    if "binary" in fields:
        return "redacted"
    return "public_safe"


def _proof_class(node_id: str, node: dict[str, Any], typed_sources: set[str], authority_seen: set[str]) -> str:
    if node_id in authority_seen:
        return "merkle_plus_typed_authority_eligibility_path"
    if node_id in typed_sources or _authority_class(node) in {"accepted_adr", "ratified_cdl", "genesis_core"}:
        return "merkle_plus_typed_non_authority_trace"
    return "merkle_inclusion_only"


def _bfs(seed: set[str], adjacency: dict[str, set[str]], max_hops: int | None = None) -> set[str]:
    seen = set(seed)
    queue: deque[tuple[str, int]] = deque((node_id, 0) for node_id in sorted(seed))
    while queue:
        current, depth = queue.popleft()
        if max_hops is not None and depth >= max_hops:
            continue
        for target in sorted(adjacency.get(current, set())):
            if target not in seen:
                seen.add(target)
                queue.append((target, depth + 1))
    return seen


def _shortest_path(start: str, goals: set[str], adjacency: dict[str, set[str]]) -> tuple[str, ...]:
    if start in goals:
        return (start,)
    queue: deque[tuple[str, tuple[str, ...]]] = deque([(start, (start,))])
    seen = {start}
    while queue:
        current, path = queue.popleft()
        for target in sorted(adjacency.get(current, set())):
            if target in seen:
                continue
            next_path = path + (target,)
            if target in goals:
                return next_path
            seen.add(target)
            queue.append((target, next_path))
    return (start,)


def _source_citation(node: dict[str, Any], *, redact: bool) -> str:
    source_path = node.get("source_path")
    if not isinstance(source_path, str) or not source_path:
        evidence = node.get("evidence")
        if isinstance(evidence, list) and evidence:
            first = evidence[0]
            if isinstance(first, dict):
                source_path = first.get("source_path")
    if not isinstance(source_path, str) or not source_path:
        return f"node:{_node_id(node)}"
    if redact:
        return f"redacted_private_path_sha256:{hashlib.sha256(source_path.encode('utf-8')).hexdigest()}"
    return source_path


def _project_node(node_id: str, node: dict[str, Any], *, redact: bool) -> dict[str, Any]:
    label = str(node.get("label", node_id))
    if redact:
        label = f"redacted:{hashlib.sha256(label.encode('utf-8')).hexdigest()[:16]}"
        projected_id = f"redacted_node:{hashlib.sha256(node_id.encode('utf-8')).hexdigest()[:24]}"
    else:
        projected_id = node_id
    return {
        "authority_class": _authority_class(node),
        "canonical_id_redacted": redact,
        "label": label,
        "node_kind": str(node.get("node_kind", "")),
        "privacy_class": _privacy_class(node),
        "projected_node_id": projected_id,
    }


def _b10_b12_fallback_count(summary: dict[str, Any]) -> tuple[int, str]:
    if not FIX27_CANDIDATES.exists():
        role_counts = summary.get("typed_trace_edge_role_counts", {})
        if isinstance(role_counts, dict):
            return int(role_counts.get("SOURCE_TREE_MEMBER", 0)), "fix27_summary_source_tree_member_count"
        return 0, "fix27_jsonl_unavailable"

    count = 0
    with FIX27_CANDIDATES.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            record = json.loads(line)
            for edge in record.get("right_pattern", {}).get("add_edges", []):
                provenance = str(edge.get("provenance", ""))
                if (
                    edge.get("edge_type") == "SOURCE_TREE_MEMBER"
                    and edge.get("target") == NODE0
                    and any(marker in provenance for marker in ("_b10", "_b11", "_b12"))
                ):
                    count += 1
    return count, "fix27_jsonl_b10_b12_source_tree_member_to_node0_scan"


def _build_graph(graph: dict[str, Any]) -> dict[str, Any]:
    nodes = graph.get("nodes")
    edges = graph.get("edges")
    if not isinstance(nodes, list) or not isinstance(edges, list):
        raise ValueError("fix22_graph_nodes_edges_required")

    node_by_id = {_node_id(node): node for node in nodes}
    undirected: dict[str, set[str]] = defaultdict(set)
    authority_forward: dict[str, set[str]] = defaultdict(set)
    support_forward: dict[str, set[str]] = defaultdict(set)
    accepted_typed_source_nodes: set[str] = set()

    endpoint_errors = 0
    filtered_fallback_edges = 0
    for edge in edges:
        source = _edge_endpoint(edge, "source")
        target = _edge_endpoint(edge, "target")
        edge_type = _edge_type(edge)
        if source not in node_by_id or target not in node_by_id:
            endpoint_errors += 1
            continue
        undirected[source].add(target)
        undirected[target].add(source)
        if edge_type in AUTHORITY_EDGE_TYPES:
            authority_forward[source].add(target)
            accepted_typed_source_nodes.add(source)
        elif edge_type in SUPPORT_TRACE_EDGE_TYPES:
            support_forward[source].add(target)
            accepted_typed_source_nodes.add(source)
        elif edge_type in CONTAINMENT_EDGE_TYPES:
            filtered_fallback_edges += int(edge_type == "SOURCE_TREE_MEMBER")

    authority_seen = _bfs({NODE0}, authority_forward) if NODE0 in node_by_id else set()
    return {
        "accepted_typed_source_nodes": accepted_typed_source_nodes,
        "authority_forward": authority_forward,
        "authority_seen": authority_seen,
        "endpoint_errors": endpoint_errors,
        "node_by_id": node_by_id,
        "support_forward": support_forward,
        "undirected": undirected,
    }


def _select_roots(node_by_id: dict[str, dict[str, Any]]) -> dict[str, list[str]]:
    def by_path(token: str, limit: int = 3) -> list[str]:
        matches = [
            node_id
            for node_id, node in node_by_id.items()
            if token in str(node.get("source_path", "")).lower()
            or token in node_id.lower()
            or token in str(node.get("label", "")).lower()
        ]
        return sorted(matches)[:limit]

    roots = {
        "onboarding_seed": by_path("agent_onboarding_organic_graph_hydration", 2)
        or ["adr:0041_agent_init_ingestion_protocol"],
        "type_definition": by_path("adr_0035", 2) + by_path("cdl_097", 2),
        "sidecar_recipe": by_path("sidecar", 4),
        "maintenance_evidence": by_path("maintenance", 3) + by_path("sim_atlas", 2),
        "public_release_candidate": by_path("public_rc", 4) + by_path("source_allowlist", 2),
        "private_excluded": [
            node_id
            for node_id, node in sorted(node_by_id.items())
            if _privacy_class(node) in {"private_capability_required", "redacted"}
        ][:4],
    }
    for key, values in list(roots.items()):
        roots[key] = [value for value in values if value in node_by_id][:4]
    return roots


def _slice_record(
    *,
    slice_type: str,
    root_node_ids: list[str],
    graph_ctx: dict[str, Any],
    full_authority_reachability: float,
    b10_b12_count: int,
    max_nodes: int,
    max_edges: int,
    max_hops: int,
    max_bytes: int,
    semantic_loss_annotations: list[str],
    permission_decision: str = "allowed_local",
    folded: bool = False,
) -> dict[str, Any]:
    node_by_id = graph_ctx["node_by_id"]
    undirected = graph_ctx["undirected"]
    authority_seen = graph_ctx["authority_seen"]
    typed_sources = graph_ctx["accepted_typed_source_nodes"]

    roots = [root for root in root_node_ids if root in node_by_id]
    selected = _bfs(set(roots), undirected, max_hops=max_hops) if roots else set()
    selected = set(sorted(selected)[:max_nodes])

    redact = slice_type == "private_excluded_slice"
    redaction_map = {
        node_id: f"redacted_node:{hashlib.sha256(node_id.encode('utf-8')).hexdigest()[:24]}"
        for node_id in selected
    } if redact else {}

    slice_edges = []
    roles = set()
    for edge in _read_json(FIX22_GRAPH)["edges"]:
        source = edge.get("source")
        target = edge.get("target")
        edge_type = edge.get("edge_type")
        if source in selected and target in selected:
            if edge_type in ACCEPTED_TYPED_TRACE_EDGE_TYPES:
                roles.add(edge_type)
            if edge_type in CONTAINMENT_EDGE_TYPES:
                continue
            slice_edges.append(
                {
                    "edge_type": edge_type,
                    "source": redaction_map.get(source, source),
                    "target": redaction_map.get(target, target),
                }
            )
        if len(slice_edges) >= max_edges:
            break

    projected_nodes = [_project_node(node_id, node_by_id[node_id], redact=redact) for node_id in sorted(selected)]
    citations = sorted(
        {
            _source_citation(node_by_id[node_id], redact=redact)
            for node_id in selected
            if node_id in node_by_id
        }
    )[:20]
    proof_distribution = Counter(
        _proof_class(node_id, node_by_id[node_id], typed_sources, authority_seen)
        for node_id in selected
    )
    for key in (
        "merkle_inclusion_only",
        "merkle_plus_typed_non_authority_trace",
        "merkle_plus_typed_authority_eligibility_path",
    ):
        proof_distribution.setdefault(key, 0)

    contractualized = {
        node_id
        for node_id in selected
        if node_id in typed_sources
        or node_id in authority_seen
        or _authority_class(node_by_id[node_id]) in {"genesis_core", "accepted_adr", "ratified_cdl"}
    }
    directed_gap_count = len(selected - contractualized)

    slice_authority_seen = selected & authority_seen
    authority_reachability = _ratio(len(slice_authority_seen), len(selected))
    delta = round(authority_reachability - full_authority_reachability, 6)
    reachability_loss = authority_reachability < round(full_authority_reachability - 0.0001, 6)

    authority_goals = {
        node_id
        for node_id in selected
        if node_id in authority_seen or node_id.startswith(AUTHORITY_PREFIXES)
    }
    path_tuples = [
        _shortest_path(node_id, authority_goals, undirected)
        for node_id in sorted(selected)
    ]
    path_family_digest = hashlib.sha256(
        _compact_dumps(sorted(set(path_tuples))).encode("utf-8")
    ).hexdigest()

    non_claims = list(NON_AUTHORIZATION_TOKENS)
    if directed_gap_count:
        non_claims.append(
            f"{directed_gap_count}_nodes_hashed_repo_material_only_not_semantically_rooted"
        )
    if reachability_loss:
        non_claims.append("reachability_loss_requires_human_review_before_hydration_use")

    payload_for_digest = {
        "edges": slice_edges,
        "nodes": projected_nodes,
        "roots": roots,
        "slice_type": slice_type,
    }
    replay_digest = hashlib.sha256(_compact_dumps(payload_for_digest).encode("utf-8")).hexdigest()

    record = {
        "authority_class_filter": "mixed_support_and_authority",
        "authority_reachability": authority_reachability,
        "b10_b12_fallback_edge_count": b10_b12_count,
        "delta_authority_reachability": delta,
        "directed_view_not_yet_contractualized_count": directed_gap_count,
        "edge_count": len(slice_edges),
        "folded_projection": folded,
        "hydrated_edges": slice_edges,
        "hydrated_nodes": projected_nodes,
        "max_bytes": max_bytes,
        "max_edges": max_edges,
        "max_hops": max_hops,
        "max_nodes": max_nodes,
        "node_count": len(projected_nodes),
        "non_authorization_tokens": non_claims,
        "path_family_digest": path_family_digest,
        "permission_decision": permission_decision,
        "privacy_class_filter": "public_safe_and_local_only"
        if not redact
        else "private_capability_required_redacted",
        "proof_class_distribution": dict(sorted(proof_distribution.items())),
        "reachability_loss": reachability_loss,
        "replay_digest": replay_digest,
        "root_node_ids": [redaction_map.get(root, root) for root in roots],
        "root_node_ids_redacted": redact,
        "semantic_loss_annotations": semantic_loss_annotations,
        "slice_id": f"atlas-hydration-slice:{_stable_hash({'roots': roots, 'type': slice_type})}",
        "slice_type": slice_type,
        "source_citations": citations,
        "typed_trace_roles_present": sorted(role for role in roles if role != "SOURCE_TREE_MEMBER"),
    }
    byte_size = len(_compact_dumps(record).encode("utf-8"))
    record["byte_size"] = byte_size
    if byte_size > max_bytes and permission_decision == "allowed_local":
        record["permission_decision"] = "denied_privacy_budget"
        record["semantic_loss_annotations"] = sorted(
            set(record["semantic_loss_annotations"] + ["bounded_context_truncation"])
        )
    return record


def _rejected_slice(full_authority_reachability: float, b10_b12_count: int) -> dict[str, Any]:
    payload = {
        "reason": "requested_budget_exceeds_declared_limits",
        "slice_type": "rejected_budget_exceeded_slice",
    }
    return {
        "authority_class_filter": "mixed_support_and_authority",
        "authority_reachability": 0.0,
        "b10_b12_fallback_edge_count": b10_b12_count,
        "byte_size": len(_compact_dumps(payload).encode("utf-8")),
        "delta_authority_reachability": round(0.0 - full_authority_reachability, 6),
        "directed_view_not_yet_contractualized_count": 0,
        "edge_count": 0,
        "folded_projection": False,
        "hydrated_edges": [],
        "hydrated_nodes": [],
        "max_bytes": 128,
        "max_edges": 1,
        "max_hops": 1,
        "max_nodes": 1,
        "node_count": 0,
        "non_authorization_tokens": NON_AUTHORIZATION_TOKENS
        + ["rejected_slice_not_hydration_source"],
        "path_family_digest": hashlib.sha256(_compact_dumps([]).encode("utf-8")).hexdigest(),
        "permission_decision": "denied_privacy_budget",
        "privacy_class_filter": "public_safe_and_local_only",
        "proof_class_distribution": {
            "merkle_inclusion_only": 0,
            "merkle_plus_typed_authority_eligibility_path": 0,
            "merkle_plus_typed_non_authority_trace": 0,
        },
        "reachability_loss": True,
        "replay_digest": hashlib.sha256(_compact_dumps(payload).encode("utf-8")).hexdigest(),
        "root_node_ids": [],
        "semantic_loss_annotations": ["bounded_context_truncation"],
        "slice_id": f"atlas-hydration-slice:{_stable_hash(payload)}",
        "slice_type": "rejected_budget_exceeded_slice",
        "source_citations": [],
        "typed_trace_roles_present": [],
    }


def _validate_no_leaks(slices: list[dict[str, Any]]) -> list[str]:
    serialized = _compact_dumps(slices).lower()
    leaks = sorted(token for token in FORBIDDEN_LEAK_TOKENS if token.lower() in serialized)
    return leaks


def _build_outputs() -> tuple[dict[str, Any], dict[str, Any]]:
    graph = _read_json(FIX22_GRAPH)
    fix27_summary = _read_json(FIX27_SUMMARY)
    graph_ctx = _build_graph(graph)
    node_by_id = graph_ctx["node_by_id"]
    b10_b12_count, fallback_source = _b10_b12_fallback_count(fix27_summary)
    full_authority_reachability = _ratio(len(graph_ctx["authority_seen"]), len(node_by_id))

    roots = _select_roots(node_by_id)
    slice_specs = [
        (
            "onboarding_seed_slice",
            roots["onboarding_seed"],
            80,
            160,
            2,
            200_000,
            ["lossless_incidence"],
            False,
        ),
        (
            "type_definition_slice",
            roots["type_definition"],
            90,
            180,
            2,
            220_000,
            ["lossless_incidence"],
            False,
        ),
        (
            "sidecar_recipe_slice",
            roots["sidecar_recipe"],
            70,
            140,
            2,
            180_000,
            ["folded_support_summary", "collapsed_hyperedge_identity"],
            True,
        ),
        (
            "maintenance_evidence_slice",
            roots["maintenance_evidence"],
            70,
            140,
            2,
            180_000,
            ["omitted_parallel_paths", "inferred_transitive_support"],
            True,
        ),
        (
            "public_release_candidate_slice",
            roots["public_release_candidate"],
            90,
            180,
            2,
            220_000,
            ["authority_class_downsampled", "inferred_transitive_support"],
            True,
        ),
        (
            "private_excluded_slice",
            roots["private_excluded"],
            50,
            100,
            1,
            160_000,
            ["privacy_redacted_paths"],
            True,
        ),
    ]
    slices = [
        _slice_record(
            slice_type=slice_type,
            root_node_ids=root_ids,
            graph_ctx=graph_ctx,
            full_authority_reachability=full_authority_reachability,
            b10_b12_count=b10_b12_count,
            max_nodes=max_nodes,
            max_edges=max_edges,
            max_hops=max_hops,
            max_bytes=max_bytes,
            semantic_loss_annotations=annotations,
            folded=folded,
        )
        for slice_type, root_ids, max_nodes, max_edges, max_hops, max_bytes, annotations, folded in slice_specs
    ]
    slices.append(_rejected_slice(full_authority_reachability, b10_b12_count))

    leaks = _validate_no_leaks(slices)
    if leaks:
        raise ValueError(f"projection_hydration_forbidden_leak_detected:{','.join(leaks)}")

    slice_payload = {
        "fallback_filter": {
            "b10_b12_fallback_edge_count": b10_b12_count,
            "fallback_count_source": fallback_source,
            "filter_rule": "B10-B12 SOURCE_TREE_MEMBER/provisional fallback edges excluded from authority_reachability and typed_trace_roles_present",
        },
        "full_graph_authority_reachability": full_authority_reachability,
        "non_claims": [
            "Research-only local projection and hydration SIM.",
            "No public serving, public P2P, live ZKP, Genesis signing, canonical graph mutation, minting, settlement, wallet, or treasury activation.",
        ],
        "phase": PHASE,
        "schema_version": SCHEMA_VERSION,
        "sim_id": SIM_ID,
        "slices": slices,
    }

    semantic_loss_counts = Counter(
        annotation
        for record in slices
        for annotation in record.get("semantic_loss_annotations", [])
    )
    summary = {
        "b10_b12_fallback_edge_count": b10_b12_count,
        "b10_b12_fallback_filter_applied": True,
        "fallback_count_source": fallback_source,
        "fix22_edge_count": len(graph["edges"]),
        "fix22_node_count": len(graph["nodes"]),
        "fix27_candidate_record_count": fix27_summary["candidate_record_count"],
        "full_graph_authority_reachability": full_authority_reachability,
        "no_leak_verdict": "pass",
        "non_claims": [
            "projection_hydration_not_public_serving",
            "projection_hydration_not_live_zkp",
            "projection_hydration_not_canonical_graph_mutation",
            "projection_hydration_not_genesis_signing",
            "projection_hydration_not_minting_or_settlement",
        ],
        "output_tokens": OUTPUT_TOKENS,
        "phase": PHASE,
        "rejected_slice_count": sum(1 for item in slices if item["permission_decision"] != "allowed_local"),
        "schema_version": SCHEMA_VERSION,
        "semantic_loss_counts": dict(sorted(semantic_loss_counts.items())),
        "sim_id": SIM_ID,
        "slice_count": len(slices),
        "slice_types": [item["slice_type"] for item in slices],
        "status": "pass",
        "transitivity_projection_checks": {
            "path_family_digest_present_for_all_slices": all(
                bool(item.get("path_family_digest")) for item in slices
            ),
            "reachability_checked_for_all_slices": all(
                "authority_reachability" in item and "delta_authority_reachability" in item
                for item in slices
            ),
            "reachability_loss_count": sum(1 for item in slices if item["reachability_loss"]),
        },
    }
    return slice_payload, summary


def _report(summary: dict[str, Any], slice_payload: dict[str, Any]) -> str:
    rows = "\n".join(
        "| {slice_type} | {node_count} | {edge_count} | {authority_reachability} | {reachability_loss} | {permission_decision} |".format(
            **record
        )
        for record in slice_payload["slices"]
    )
    loss_rows = "\n".join(
        f"| `{key}` | {value} |" for key, value in sorted(summary["semantic_loss_counts"].items())
    )
    return f"""<!-- PUBLIC_RC_EXCLUDE: atlas_projection_hydration_sim_research_only -->
<!-- PUBLIC_RC_EXCLUDE_REASON: Research-only projection/hydration SIM report; no public serving, live ZKP, canonical graph mutation, signing, minting, settlement, or public RC activation. -->

# SIM Atlas Projection And Hydration - Phase 1545p-Fix28

## Summary

Phase 1545p-Fix28 generated deterministic local-only projection and hydration
slices over the Fix22 full-repo Atlas candidate. The SIM applied the Fix28
`b10_b12_fallback_edge_filter`: provisional B10-B12 source-tree fallback edges
are separately accounted as `{summary["b10_b12_fallback_edge_count"]}` edges and
do not count as authority reachability or semantic Genesis-rootedness.

## Slice Metrics

| Slice | Nodes | Edges | Authority reachability | Reachability loss | Permission |
|---|---:|---:|---:|---|---|
{rows}

## Semantic Loss Annotations

| Annotation | Count |
|---|---:|
{loss_rows}

## Non-Claims

- No public serving, public P2P, live ZKP, Genesis signing, canonical graph
  mutation, minting, settlement, wallet, treasury, sidecar activation, ADR/CDL
  mutation, or public RC activation occurred.
- Projection usefulness is local support only and does not create authority,
  claimability, eligibility, or economic effect.
"""


def _review(summary: dict[str, Any]) -> str:
    return f"""<!-- PUBLIC_RC_EXCLUDE: atlas_projection_hydration_review_research_only -->
<!-- PUBLIC_RC_EXCLUDE_REASON: Research-only review of local projection/hydration SIM; no public serving or canonical graph mutation. -->

# ILC Atlas Projection And Hydration Review - Phase 1545p-Fix28

## Verdict

`PASS` for research-only projection and hydration simulation.

## Findings

- Generated `{summary["slice_count"]}` deterministic local-only slices.
- Applied `b10_b12_fallback_edge_filter` and separately accounted
  `{summary["b10_b12_fallback_edge_count"]}` provisional fallback edges.
- Recorded path-family digests for every slice.
- Recorded reachability deltas for every slice.
- Preserved no-serving, no-live-ZKP, no-canonical-mutation, no-signing,
  no-minting, and no-settlement boundaries.

## Carry-Forward

- Fix29 may consume the slice metrics for non-excisability diagnostics.
- Fix30 may use the slice records as local hydration evidence, but it must not
  convert projection usefulness into authority.
- Fix31 must still require typed trace role, terminal, traversal direction, and
  governing condition records before signing-batch classification.
"""


def main() -> None:
    slice_payload, summary = _build_outputs()
    _atomic_write(SLICES_OUT, _canonical_dumps(slice_payload))
    _atomic_write(SUMMARY_OUT, _canonical_dumps(summary))
    _atomic_write(REPORT_OUT, _report(summary, slice_payload))
    _atomic_write(REVIEW_OUT, _review(summary))


if __name__ == "__main__":
    main()
