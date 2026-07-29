#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Validate authority-graph invariants for Genesis Atlas candidates."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict, deque
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_epistemic_gap_nodes import validate_candidate as validate_gap_nodes  # noqa: E402


NODE0 = "artifact:genesis_intent_attestation_init_authority_map"
STRICT_PHASES = {"phase_1545p_fix50", "phase_1545p_fix51", "negative_control"}
AUTHORITY_PREFIXES = ("adr:", "cdl:")
RULE_PREFIXES = ("policy:", "invariant:")
FORBIDDEN_SOURCE_PREFIXES = ("repo:file:", "test:", "phase:", "sim:", "target:")
FORBIDDEN_TARGET_PREFIXES = ("repo:file:", "test:", "phase:", "sim:", "target:")


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _node_ids(candidate: dict[str, Any]) -> set[str]:
    return {
        str(node["candidate_id"])
        for node in candidate.get("nodes", [])
        if isinstance(node, dict) and "candidate_id" in node
    }


def _gap_ids(candidate: dict[str, Any]) -> set[str]:
    return {
        str(node["candidate_id"])
        for node in candidate.get("nodes", [])
        if isinstance(node, dict) and node.get("node_kind") == "epistemic_gap"
    }


def _is_strict_edge(edge: dict[str, Any]) -> bool:
    return edge.get("annotation_phase") in STRICT_PHASES or bool(edge.get("fix52_negative_control"))


def _governs_edges(candidate: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        edge
        for edge in candidate.get("edges", [])
        if isinstance(edge, dict) and edge.get("edge_type") == "GOVERNS"
    ]


def _cycle_errors(edges: list[dict[str, Any]]) -> list[str]:
    graph: dict[str, set[str]] = defaultdict(set)
    for edge in edges:
        graph[str(edge.get("source"))].add(str(edge.get("target")))

    errors: list[str] = []
    for start in graph:
        queue: deque[str] = deque(graph[start])
        seen: set[str] = set()
        while queue:
            node = queue.popleft()
            if node == start:
                errors.append(f"GOVERNS cycle detected at {start}")
                break
            if node in seen:
                continue
            seen.add(node)
            queue.extend(graph.get(node, ()))
    return errors


def validate_authority(candidate: dict[str, Any]) -> list[str]:
    errors = validate_gap_nodes(candidate)
    node_ids = _node_ids(candidate)
    gaps = _gap_ids(candidate)

    governs_edges = _governs_edges(candidate)
    for edge in governs_edges:
        source = str(edge.get("source", ""))
        target = str(edge.get("target", ""))
        strict = _is_strict_edge(edge)

        if source in gaps:
            errors.append(f"{source}->{target}: gap node cannot be GOVERNS source")
        if target in gaps:
            errors.append(f"{source}->{target}: gap node cannot be GOVERNS target")

        if source.startswith(FORBIDDEN_SOURCE_PREFIXES):
            errors.append(f"{source}->{target}: forbidden GOVERNS source prefix")
        if target.startswith(FORBIDDEN_TARGET_PREFIXES):
            errors.append(f"{source}->{target}: forbidden GOVERNS target prefix")

        if source.startswith("policy:") and target.startswith(AUTHORITY_PREFIXES):
            errors.append(f"{source}->{target}: GOVERNS must flow authority downward")

        if strict:
            if source == NODE0:
                if not target.startswith(AUTHORITY_PREFIXES):
                    errors.append(f"{source}->{target}: NODE0 strict GOVERNS must target CDL/ADR")
            elif source.startswith(AUTHORITY_PREFIXES):
                if not target.startswith(AUTHORITY_PREFIXES + RULE_PREFIXES + ("artifact:",)):
                    errors.append(f"{source}->{target}: strict GOVERNS target outside authority/rule/artifact")
            else:
                errors.append(f"{source}->{target}: strict GOVERNS source must be NODE0, CDL, or ADR")

        if source not in node_ids:
            errors.append(f"{source}->{target}: GOVERNS source missing node")
        if target not in node_ids:
            errors.append(f"{source}->{target}: GOVERNS target missing node")

    errors.extend(_cycle_errors(governs_edges))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", type=Path)
    args = parser.parse_args()
    candidate = _load(args.candidate)
    errors = validate_authority(candidate)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"VALID: {args.candidate}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
