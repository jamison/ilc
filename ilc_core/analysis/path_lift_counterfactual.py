from __future__ import annotations

from typing import Iterable, Mapping, Sequence, TypedDict, cast

from ilc_core.exceptions import NodeValueKernelError


class PathWitnessNode(TypedDict):
    node_id: str
    agent_id: str


class PathWitness(TypedDict):
    witness_id: str
    source_id: str
    target_id: str
    nodes: list[PathWitnessNode]
    path_weight: float
    path_cost: float


class PathLiftCounterfactualRow(TypedDict):
    node_id: str
    raw_path_lift: float
    normalized_path_lift: float
    witness_count: int
    supporting_agents: list[str]
    unique_agent_count: int


class PathLiftCounterfactualReport(TypedDict):
    rows: list[PathLiftCounterfactualRow]
    max_raw_path_lift: float
    witness_count: int


_ALLOWED_NODE_KEYS = {"node_id", "agent_id"}
_ALLOWED_WITNESS_KEYS = {
    "witness_id",
    "source_id",
    "target_id",
    "nodes",
    "path_weight",
    "path_cost",
}


def _expect_non_empty_str(payload: Mapping[str, object], key: str, token: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or value == "":
        raise NodeValueKernelError(token)
    return value


def _expect_non_negative_float(payload: Mapping[str, object], key: str, token: str) -> float:
    value = payload.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise NodeValueKernelError(token)
    out = float(value)
    if out < 0.0:
        raise NodeValueKernelError(token)
    return out


def _expect_positive_float(payload: Mapping[str, object], key: str, token: str) -> float:
    out = _expect_non_negative_float(payload, key, token)
    if out <= 0.0:
        raise NodeValueKernelError(token)
    return out


def validate_path_witness_node(node: Mapping[str, object]) -> PathWitnessNode:
    if set(node.keys()) != _ALLOWED_NODE_KEYS:
        raise NodeValueKernelError("path_lift_invalid_node_keys")
    return {
        "node_id": _expect_non_empty_str(node, "node_id", "path_lift_missing_node_id"),
        "agent_id": _expect_non_empty_str(node, "agent_id", "path_lift_missing_agent_id"),
    }


def validate_path_witness(witness: Mapping[str, object]) -> PathWitness:
    if set(witness.keys()) != _ALLOWED_WITNESS_KEYS:
        raise NodeValueKernelError("path_lift_invalid_witness_keys")

    nodes_value = witness.get("nodes")
    if not isinstance(nodes_value, Sequence) or isinstance(nodes_value, (str, bytes)):
        raise NodeValueKernelError("path_lift_invalid_nodes")

    normalized_nodes: list[PathWitnessNode] = []
    seen_node_ids: set[str] = set()
    for raw_node in nodes_value:
        if not isinstance(raw_node, Mapping):
            raise NodeValueKernelError("path_lift_invalid_node_shape")
        node = validate_path_witness_node(cast(Mapping[str, object], raw_node))
        if node["node_id"] in seen_node_ids:
            raise NodeValueKernelError("path_lift_duplicate_node_in_witness")
        seen_node_ids.add(node["node_id"])
        normalized_nodes.append(node)

    if len(normalized_nodes) == 0:
        raise NodeValueKernelError("path_lift_empty_nodes")

    return {
        "witness_id": _expect_non_empty_str(
            witness,
            "witness_id",
            "path_lift_missing_witness_id",
        ),
        "source_id": _expect_non_empty_str(
            witness,
            "source_id",
            "path_lift_missing_source_id",
        ),
        "target_id": _expect_non_empty_str(
            witness,
            "target_id",
            "path_lift_missing_target_id",
        ),
        "nodes": normalized_nodes,
        "path_weight": _expect_non_negative_float(
            witness,
            "path_weight",
            "path_lift_invalid_path_weight",
        ),
        "path_cost": _expect_positive_float(
            witness,
            "path_cost",
            "path_lift_invalid_path_cost",
        ),
    }


def collect_path_witnesses(
    witnesses: Iterable[Mapping[str, object]],
) -> list[PathWitness]:
    out: list[PathWitness] = []
    seen_ids: set[str] = set()
    for raw_witness in witnesses:
        witness = validate_path_witness(raw_witness)
        witness_id = witness["witness_id"]
        if witness_id in seen_ids:
            raise NodeValueKernelError("path_lift_duplicate_witness_id")
        seen_ids.add(witness_id)
        out.append(witness)
    return sorted(out, key=lambda row: row["witness_id"])


def compute_path_lift_counterfactual(
    witnesses: Iterable[Mapping[str, object]],
) -> PathLiftCounterfactualReport:
    normalized_witnesses = collect_path_witnesses(witnesses)

    raw_lift_by_node: dict[str, float] = {}
    witness_count_by_node: dict[str, int] = {}
    supporting_agents_by_node: dict[str, set[str]] = {}

    for witness in normalized_witnesses:
        baseline_efficiency = witness["path_weight"] / witness["path_cost"]
        path_agent_ids = {node["agent_id"] for node in witness["nodes"]}

        for node in witness["nodes"]:
            node_id = node["node_id"]
            raw_lift_by_node[node_id] = raw_lift_by_node.get(node_id, 0.0) + baseline_efficiency
            witness_count_by_node[node_id] = witness_count_by_node.get(node_id, 0) + 1
            supporting_agents_by_node.setdefault(node_id, set()).update(path_agent_ids)

    max_raw_lift = max(raw_lift_by_node.values(), default=0.0)
    rows: list[PathLiftCounterfactualRow] = []
    for node_id in sorted(raw_lift_by_node.keys()):
        raw_lift = raw_lift_by_node[node_id]
        normalized_lift = (raw_lift / max_raw_lift) if max_raw_lift > 0.0 else 0.0
        supporting_agents = sorted(supporting_agents_by_node.get(node_id, set()))
        rows.append(
            {
                "node_id": node_id,
                "raw_path_lift": raw_lift,
                "normalized_path_lift": normalized_lift,
                "witness_count": witness_count_by_node[node_id],
                "supporting_agents": supporting_agents,
                "unique_agent_count": len(supporting_agents),
            }
        )

    return {
        "rows": rows,
        "max_raw_path_lift": max_raw_lift,
        "witness_count": len(normalized_witnesses),
    }


def rank_path_lift_rows(
    rows: Iterable[PathLiftCounterfactualRow],
) -> list[PathLiftCounterfactualRow]:
    return sorted(
        rows,
        key=lambda row: (
            -float(row["normalized_path_lift"]),
            -float(row["raw_path_lift"]),
            str(row["node_id"]),
        ),
    )


def build_normalized_path_lift_by_node(
    report: PathLiftCounterfactualReport,
) -> dict[str, float]:
    return {
        row["node_id"]: float(row["normalized_path_lift"])
        for row in report["rows"]
    }
