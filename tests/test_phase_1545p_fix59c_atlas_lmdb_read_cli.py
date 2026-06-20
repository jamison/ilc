from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from ilc_core.cli.atlas_lmdb_cli import (
    ATLAS_LMDB_CLI_VERSION,
    AtlasLmdbCliError,
    handle_atlas_edges,
    handle_atlas_node,
    handle_atlas_status,
    handle_atlas_validate,
)
from ilc_core.storage.genesis_atlas_candidate_lmdb_adapter import GenesisAtlasCandidateStore
from ilc_core.storage.genesis_atlas_lmdb_writer import deterministic_edge_id


STATUS_PATH = Path("docs/phases/STATUS.md")
PROMPT_PATH = Path(
    "docs/antigravity_tasks/"
    "antigravity_prompt__phase_1545p_fix59_g10_atlas_lmdb_read_cli_fix59c.md"
)
CLI_HELPER_PATH = Path("ilc_core/cli/atlas_lmdb_cli.py")
CLI_MAIN_PATH = Path("ilc_core/cli/main.py")


def _seed_atlas_lmdb(root: Path) -> None:
    nodes = [
        {
            "candidate_id": "repo:file:tests_test_example_py",
            "graph_delta": "support_only",
            "graph_projection": "public_protocol_graph",
            "node_kind": "test_file",
            "source_path": "tests/test_example.py",
            "tier": "support_candidate",
        },
        {
            "candidate_id": "repo:file:ilc_core_example_py",
            "graph_delta": "support_only",
            "graph_projection": "public_protocol_graph",
            "node_kind": "runtime_module",
            "source_path": "ilc_core/example.py",
            "tier": "support_candidate",
        },
        {
            "candidate_id": "cdl:075_truth_primitive_graph_persistence",
            "graph_delta": "support_only",
            "graph_projection": "genesis_core_star_map",
            "node_kind": "cdl_node",
            "source_path": "docs/specs/ilc_constitutional_decision_log_v0.1.md",
            "tier": "genesis_core",
        },
    ]
    edge_with_id = {
        "edge_id": deterministic_edge_id(
            "repo:file:tests_test_example_py",
            "TESTS",
            "repo:file:ilc_core_example_py",
        ),
        "edge_type": "TESTS",
        "source": "repo:file:tests_test_example_py",
        "src": "repo:file:tests_test_example_py",
        "target": "repo:file:ilc_core_example_py",
        "tgt": "repo:file:ilc_core_example_py",
    }
    edge_without_id = {
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "repo:file:ilc_core_example_py",
        "src": "repo:file:ilc_core_example_py",
        "target": "cdl:075_truth_primitive_graph_persistence",
        "tgt": "cdl:075_truth_primitive_graph_persistence",
    }
    store = GenesisAtlasCandidateStore(root, allow_synthetic_edge_keys=True)
    try:
        store.put_nodes(nodes)
        store.put_edges([edge_with_id, edge_without_id])
        store.put_preimages(
            [
                {"node_id": "repo:file:tests_test_example_py", "preimage": "tests"},
                {"node_id": "repo:file:ilc_core_example_py", "preimage": "runtime"},
            ]
        )
        store.put_graph_payload({"nodes": nodes, "edges": [edge_with_id, edge_without_id]})
        store.put_meta(
            "materialization_manifest",
            {
                "candidate": "fixture",
                "phase": "1545p-Fix59c-test",
            },
        )
    finally:
        store.close()


def _run_cli(*args: str, graph_path: Path) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env.pop("ILC_TRUTH_GRAPH_STORE_PATH", None)
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "ilc_core.cli.main",
            "--graph-state",
            str(graph_path),
            *args,
        ],
        capture_output=True,
        check=False,
        text=True,
        env=env,
    )


def test_fix59c_prompt_validates_required_surface() -> None:
    text = PROMPT_PATH.read_text(encoding="utf-8")
    assert "Fix59c Atlas LMDB Read CLI" in text
    assert "## LMDB Node Registration" in text
    assert "Read-only proof: no writer methods called." in text


def test_fix59c_status_tokens_present() -> None:
    text = STATUS_PATH.read_text(encoding="utf-8")
    assert "fix59c_atlas_read_cli_committed" in text
    assert "fix59c_atlas_status_validate_read_only" in text
    assert "fix59c_atlas_node_edges_queries_committed" in text
    assert "fix59c_complete" in text


def test_atlas_status_reports_counts_and_manifest(tmp_path: Path) -> None:
    root = tmp_path / "atlas"
    _seed_atlas_lmdb(root)

    result = handle_atlas_status(str(root))

    assert result["version"] == ATLAS_LMDB_CLI_VERSION
    assert result["counts"]["nodes"] == 3
    assert result["counts"]["edges"] == 2
    assert result["counts"]["preimages"] == 2
    assert result["counts"]["graph_payload_nodes"] == 3
    assert result["counts"]["graph_payload_edges"] == 2
    assert result["edge_id_coverage"]["present_edge_id_count"] == 1
    assert result["edge_id_coverage"]["missing_edge_id_count"] == 1
    assert result["materialization_manifest"]["candidate"] == "fixture"
    assert result["read_only"] is True


def test_atlas_validate_reports_hard_checks_and_edge_id_debt(tmp_path: Path) -> None:
    root = tmp_path / "atlas"
    _seed_atlas_lmdb(root)

    result = handle_atlas_validate(str(root))

    assert result["verdict"] == "pass"
    assert all(result["checks"].values())
    assert result["edge_id_status"] == "debt_present_carried_to_fix60"
    assert result["edge_id_coverage"]["present_fraction"] == "1/2"


def test_atlas_node_returns_record_and_typed_miss(tmp_path: Path) -> None:
    root = tmp_path / "atlas"
    _seed_atlas_lmdb(root)

    result = handle_atlas_node(str(root), "repo:file:ilc_core_example_py")
    assert result["node_record"]["node_kind"] == "runtime_module"

    with pytest.raises(AtlasLmdbCliError) as exc_info:
        handle_atlas_node(str(root), "repo:file:missing")
    assert exc_info.value.token == "atlas_node_not_found"


def test_atlas_edges_returns_source_or_target_matches(tmp_path: Path) -> None:
    root = tmp_path / "atlas"
    _seed_atlas_lmdb(root)

    result = handle_atlas_edges(str(root), "repo:file:ilc_core_example_py")

    assert result["count"] == 2
    edge_types = {edge["edge_type"] for edge in result["edges"]}
    assert edge_types == {"TESTS", "REFERENCES_AUTHORITY"}


def test_atlas_missing_lmdb_path_fails_closed(tmp_path: Path) -> None:
    with pytest.raises(AtlasLmdbCliError) as exc_info:
        handle_atlas_status(str(tmp_path / "missing"))
    assert exc_info.value.token == "atlas_lmdb_not_found"


def test_atlas_subprocess_status_is_json_first_and_does_not_write_graph_state(tmp_path: Path) -> None:
    root = tmp_path / "atlas"
    graph_path = tmp_path / "graph.json"
    _seed_atlas_lmdb(root)

    result = _run_cli("atlas", "status", "--lmdb", str(root), graph_path=graph_path)

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["command"] == "atlas"
    assert payload["data"]["counts"]["nodes"] == 3
    assert not graph_path.exists()


def test_atlas_subprocess_node_miss_uses_deterministic_error(tmp_path: Path) -> None:
    root = tmp_path / "atlas"
    graph_path = tmp_path / "graph.json"
    _seed_atlas_lmdb(root)

    result = _run_cli(
        "atlas",
        "node",
        "--lmdb",
        str(root),
        "--node-id",
        "repo:file:missing",
        graph_path=graph_path,
    )

    assert result.returncode == 1
    payload = json.loads(result.stderr)
    assert payload["ok"] is False
    assert "atlas_node_not_found" in payload["message"]
    assert not graph_path.exists()


def test_atlas_help_lists_read_subcommands() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "ilc_core.cli.main", "atlas", "--help"],
        capture_output=True,
        check=False,
        text=True,
    )
    assert result.returncode == 0
    assert "status" in result.stdout
    assert "validate" in result.stdout
    assert "node" in result.stdout
    assert "edges" in result.stdout


def test_atlas_cli_helper_has_no_raw_adapter_mutating_store_calls() -> None:
    text = CLI_HELPER_PATH.read_text(encoding="utf-8")
    forbidden = (
        ".put_meta(",
        ".put_graph_payload(",
        ".put_nodes(",
        ".put_edges(",
        ".put_preimages(",
    )
    for token in forbidden:
        assert token not in text


def test_main_wires_atlas_without_prototype_state_initializer() -> None:
    text = CLI_MAIN_PATH.read_text(encoding="utf-8")
    assert '"atlas"' in text
    assert "run_atlas_command" in text
    assert '{"query", "verify", "bundle", "agent", "node", "sidecar", "ccss", "atlas"}' in text
