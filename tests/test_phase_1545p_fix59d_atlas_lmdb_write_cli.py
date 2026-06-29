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
    handle_atlas_apply_edge_batch,
    handle_atlas_apply_node_edge_plan,
    handle_atlas_register_phase_files,
)
from ilc_core.storage.genesis_atlas_candidate_lmdb_adapter import GenesisAtlasCandidateStore
from ilc_core.storage.genesis_atlas_lmdb_writer import (
    AtlasLmdbSafeWriter,
    AtlasPhaseFileRegistration,
    deterministic_edge_id,
)


STATUS_PATH = Path("docs/phases/STATUS.md")
PROMPT_PATH = Path(
    "docs/antigravity_tasks/"
    "antigravity_prompt__phase_1545p_fix59_g10_atlas_lmdb_write_cli_fix59d.md"
)
CLI_HELPER_PATH = Path("ilc_core/cli/atlas_lmdb_cli.py")
CLI_MAIN_PATH = Path("ilc_core/cli/main.py")


def _write_json(path: Path, payload: object) -> None:
    path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False),
        encoding="utf-8",
    )


def _seed_lmdb(root: Path) -> None:
    nodes = [
        {
            "candidate_id": "node:a",
            "graph_delta": "support_only",
            "graph_projection": "support_candidate_graph",
            "node_kind": "support_node",
            "source_path": "a.md",
            "tier": "support_candidate",
        },
        {
            "candidate_id": "node:b",
            "graph_delta": "support_only",
            "graph_projection": "support_candidate_graph",
            "node_kind": "support_node",
            "source_path": "b.md",
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
    edge = {
        "edge_id": deterministic_edge_id("node:a", "REFERENCES_AUTHORITY", "node:b"),
        "edge_type": "REFERENCES_AUTHORITY",
        "source": "node:a",
        "src": "node:a",
        "target": "node:b",
        "tgt": "node:b",
    }
    store = GenesisAtlasCandidateStore(root, allow_synthetic_edge_keys=True)
    try:
        store.put_nodes(nodes)
        store.put_edges([edge])
        store.put_graph_payload({"nodes": nodes, "edges": [edge]})
    finally:
        store.close()


def _inspect(root: Path) -> dict[str, int]:
    writer = AtlasLmdbSafeWriter(root)
    try:
        inspection = writer.inspect()
        return {"edges": inspection["edge_count"], "nodes": inspection["node_count"]}
    finally:
        writer.close()


def _run_cli(*args: str, graph_path: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    active_env = dict(os.environ)
    active_env.pop("ILC_TRUTH_GRAPH_STORE_PATH", None)
    if env:
        active_env.update(env)
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
        env=active_env,
    )


def test_fix59d_prompt_validates_required_surface() -> None:
    text = PROMPT_PATH.read_text(encoding="utf-8")
    assert "Fix59d Atlas LMDB Write CLI" in text
    assert "## LMDB Node Registration" in text
    assert "ILC_ATLAS_AUTHORITY_EDGE_AUTHORIZED=1" in text


def test_fix59d_status_tokens_present() -> None:
    text = STATUS_PATH.read_text(encoding="utf-8")
    assert "fix59d_atlas_write_cli_committed" in text
    assert "fix59d_write_cli_routes_through_safe_writer" in text
    assert "fix59d_phase_file_registration_cli_committed" in text
    assert "fix59d_edge_batch_application_cli_committed" in text
    assert "fix59d_complete" in text


def test_edge_batch_default_dry_run_does_not_mutate_or_write_meta(tmp_path: Path) -> None:
    root = tmp_path / "atlas"
    _seed_lmdb(root)
    batch = tmp_path / "edges.json"
    receipt_path = tmp_path / "receipt.json"
    _write_json(
        batch,
        {
            "edges": [{"edge_type": "TESTS", "source": "node:a", "target": "node:b"}],
            "metadata": {"purpose": "dry_run_test"},
            "phase": "1545p-Fix59d-test",
        },
    )

    receipt = handle_atlas_apply_edge_batch(
        lmdb_path=str(root),
        input_path=str(batch),
        write=False,
        receipt_path=str(receipt_path),
    )

    assert receipt["mutated"] is False
    assert receipt["dry_run"] is True
    assert receipt["accepted_edge_count"] == 1
    assert _inspect(root) == {"nodes": 3, "edges": 1}
    written = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert written == receipt
    store = GenesisAtlasCandidateStore(root, allow_synthetic_edge_keys=True)
    try:
        assert store.get_meta("safe_writer_dry_run:1545p-Fix59d-test") is None
    finally:
        store.close()


def test_node_edge_plan_write_materializes_nodes_and_recomputes_edge_id(tmp_path: Path) -> None:
    root = tmp_path / "atlas"
    _seed_lmdb(root)
    plan_path = tmp_path / "plan.json"
    _write_json(
        plan_path,
        {
            "edges": [{"edge_id": "wrong", "edge_type": "EVIDENCES", "source": "node:c", "target": "node:a"}],
            "metadata": {"purpose": "write_test"},
            "nodes": [
                {
                    "candidate_id": "node:c",
                    "graph_delta": "support_only",
                    "graph_projection": "support_candidate_graph",
                    "node_kind": "support_node",
                    "source_path": "c.md",
                    "tier": "support_candidate",
                }
            ],
            "phase": "1545p-Fix59d-test",
        },
    )

    receipt = handle_atlas_apply_node_edge_plan(
        lmdb_path=str(root),
        input_path=str(plan_path),
        write=True,
    )

    assert receipt["mutated"] is True
    assert receipt["accepted_node_count"] == 1
    assert receipt["accepted_edges"][0]["edge_id"] == deterministic_edge_id(
        "node:c",
        "EVIDENCES",
        "node:a",
    )
    assert _inspect(root) == {"nodes": 4, "edges": 2}


def test_edge_batch_missing_endpoint_is_rejected_without_partial_write(tmp_path: Path) -> None:
    root = tmp_path / "atlas"
    _seed_lmdb(root)
    batch = tmp_path / "dangling.json"
    _write_json(
        batch,
        {
            "edges": [{"edge_type": "TESTS", "source": "node:a", "target": "node:missing"}],
            "phase": "1545p-Fix59d-test",
        },
    )

    receipt = handle_atlas_apply_edge_batch(
        lmdb_path=str(root),
        input_path=str(batch),
        write=True,
    )

    assert receipt["status"] == "FAIL"
    assert receipt["mutated"] is False
    assert receipt["rejected_edge_count"] == 1
    assert receipt["rejected_edges"][0]["reason"] == "target_node_missing"
    assert _inspect(root) == {"nodes": 3, "edges": 1}


def test_authority_edge_requires_write_and_environment_gate(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path / "atlas"
    _seed_lmdb(root)
    plan_path = tmp_path / "authority.json"
    _write_json(
        plan_path,
        {
            "edges": [
                {
                    "edge_type": "GOVERNS",
                    "source": "cdl:075_truth_primitive_graph_persistence",
                    "target": "node:a",
                }
            ],
            "phase": "1545p-Fix59d-test",
        },
    )

    with pytest.raises(AtlasLmdbCliError) as dry_run_exc:
        handle_atlas_apply_edge_batch(lmdb_path=str(root), input_path=str(plan_path), write=False)
    assert dry_run_exc.value.token == "atlas_authority_edge_write_blocked"

    with pytest.raises(AtlasLmdbCliError) as env_exc:
        handle_atlas_apply_edge_batch(lmdb_path=str(root), input_path=str(plan_path), write=True)
    assert env_exc.value.token == "atlas_authority_edge_env_missing"

    monkeypatch.setenv("ILC_ATLAS_AUTHORITY_EDGE_AUTHORIZED", "1")
    receipt = handle_atlas_apply_edge_batch(lmdb_path=str(root), input_path=str(plan_path), write=True)
    assert receipt["mutated"] is True
    assert receipt["accepted_edge_count"] == 1


def test_register_phase_files_cli_write_adds_support_nodes_and_edges(tmp_path: Path) -> None:
    root = tmp_path / "atlas"
    _seed_lmdb(root)

    receipt = handle_atlas_register_phase_files(
        lmdb_path=str(root),
        phase="1545p-Fix59d-test",
        files=("docs/phases/example.md",),
        node_kind="phase_walkthrough",
        graph_projection="support_candidate_graph",
        graph_delta="support_only",
        required_edges=("EVIDENCES:phase:1545p_fix59d_test",),
        write=True,
    )

    assert receipt["mutated"] is True
    assert receipt["rejected_edge_count"] == 0
    assert receipt["accepted_node_count"] == 3
    assert receipt["accepted_edge_count"] == 2


def test_register_phase_files_does_not_duplicate_nodes_when_same_file_listed_twice(tmp_path: Path) -> None:
    root = tmp_path / "atlas"
    _seed_lmdb(root)
    writer = AtlasLmdbSafeWriter(root)
    try:
        registration = AtlasPhaseFileRegistration(
            path="docs/phases/example.md",
            node_kind="phase_walkthrough",
            graph_projection="support_candidate_graph",
            graph_delta="support_only",
        )
        plan = writer.build_phase_file_registration_plan(
            phase="1545p-Fix59d-duplicate-test",
            files=(registration, registration),
            dry_run=True,
        )
        node_ids = [node["candidate_id"] for node in plan.nodes_to_add]

        assert len(node_ids) == len(set(node_ids))
        assert node_ids.count("repo:file_ref:docs_phases_example_md") == 1
        assert len(plan.edges_to_add) == 1

        validation = writer.validate_plan(plan)
        assert len(validation["accepted_edges"]) == 1
        assert validation["accepted_edges"][0]["edge_type"] == "CARRIES_FORWARD"
        assert validation["skipped_edges"] == []
    finally:
        writer.close()


def test_register_phase_files_cli_does_not_multiply_multi_file_inputs(tmp_path: Path) -> None:
    root = tmp_path / "atlas"
    _seed_lmdb(root)

    receipt = handle_atlas_register_phase_files(
        lmdb_path=str(root),
        phase="1545p-Fix59d-multifile-test",
        files=("docs/phases/example-a.md", "docs/phases/example-b.md"),
        node_kind="phase_walkthrough",
        graph_projection="support_candidate_graph",
        graph_delta="support_only",
        required_edges=(),
        write=False,
    )

    assert receipt["metadata"]["registered_file_count"] == 2
    assert receipt["accepted_edge_count"] == 2
    assert receipt["skipped_edge_count"] == 0
    assert sorted(edge["source"] for edge in receipt["accepted_edges"]) == [
        "repo:file_ref:docs_phases_example_a_md",
        "repo:file_ref:docs_phases_example_b_md",
    ]


def test_float_and_self_referential_digest_fields_fail_closed(tmp_path: Path) -> None:
    root = tmp_path / "atlas"
    _seed_lmdb(root)
    float_path = tmp_path / "float.json"
    digest_path = tmp_path / "digest.json"
    float_path.write_text(
        '{"edges":[],"metadata":{"score":1.25},"phase":"1545p-Fix59d-test"}',
        encoding="utf-8",
    )
    _write_json(
        digest_path,
        {
            "edges": [],
            "metadata": {"same_phase_commit_hash": "abc"},
            "phase": "1545p-Fix59d-test",
        },
    )

    with pytest.raises(AtlasLmdbCliError) as float_exc:
        handle_atlas_apply_edge_batch(lmdb_path=str(root), input_path=str(float_path), write=False)
    assert float_exc.value.token == "atlas_float_forbidden"

    with pytest.raises(AtlasLmdbCliError) as digest_exc:
        handle_atlas_apply_edge_batch(lmdb_path=str(root), input_path=str(digest_path), write=False)
    assert digest_exc.value.token == "atlas_self_referential_field_forbidden"


def test_subprocess_apply_edge_batch_write_and_no_graph_state_creation(tmp_path: Path) -> None:
    root = tmp_path / "atlas"
    graph_path = tmp_path / "graph.json"
    batch = tmp_path / "edges.json"
    _seed_lmdb(root)
    _write_json(
        batch,
        {
            "edges": [{"edge_type": "TESTS", "source": "node:a", "target": "node:b"}],
            "phase": "1545p-Fix59d-test",
        },
    )

    result = _run_cli(
        "atlas",
        "apply-edge-batch",
        "--lmdb",
        str(root),
        "--input",
        str(batch),
        "--write",
        graph_path=graph_path,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["data"]["mutated"] is True
    assert _inspect(root) == {"nodes": 3, "edges": 2}
    assert not graph_path.exists()


def test_atlas_help_lists_write_subcommands() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "ilc_core.cli.main", "atlas", "--help"],
        capture_output=True,
        check=False,
        text=True,
    )
    assert result.returncode == 0
    assert "register-phase-files" in result.stdout
    assert "apply-edge-batch" in result.stdout
    assert "apply-node-edge-plan" in result.stdout


def test_atlas_write_cli_routes_through_safe_writer_without_raw_adapter_puts() -> None:
    text = CLI_HELPER_PATH.read_text(encoding="utf-8")
    forbidden = (
        ".put_meta(",
        ".put_graph_payload(",
        ".put_nodes(",
        ".put_edges(",
        ".put_preimages(",
        "GenesisAtlasCandidateStore(",
    )
    for token in forbidden:
        assert token not in text
    assert "AtlasLmdbSafeWriter" in text
    assert "apply_plan(" in text


def test_main_excludes_atlas_from_prototype_state_initializer() -> None:
    text = CLI_MAIN_PATH.read_text(encoding="utf-8")
    assert "stateless_commands = {" in text
    assert '"atlas",' in text
    assert "if command not in stateless_commands:" in text
