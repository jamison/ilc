import json
from pathlib import Path

import pytest

from ilc_core.storage.genesis_atlas_lmdb_writer import AtlasLmdbSafeWriter
from tools.materialize import register_fix38_backlog as register


def _valid_report() -> dict:
    return {
        "dry_run": True,
        "lmdb_mutated": False,
        "reconciliation_output_token": register.SOURCE_REPORT_TOKEN,
        "ledger_total_entries": 1,
        "not_registered_count": 1,
        "not_registered_unique_count": 1,
        "duplicate_entry_count": 0,
        "not_registered_unique_entries": [
            {
                "repo_path": "docs/specs/a.md",
                "recommended_graph_actions": ["support_only"],
                "proposed_semantic_edges": [],
                "proposed_authority_trace_edges": [],
            }
        ],
        "not_registered_unique_paths": ["docs/specs/a.md"],
        "not_registered_duplicate_metadata_conflict_count": 0,
        "atlas_node_count_before": 10,
        "atlas_edge_count_before": 20,
    }


def test_validate_report_rejects_duplicate_phase_owned_tail_entries() -> None:
    ledger = {
        "annotations": [
            {"repo_path": "docs/specs/a.md"},
            {
                "repo_path": (
                    "docs/phases/"
                    "phase_gap_cdl098_genesis_graph_materialization_0424_00b_walkthrough.md"
                )
            },
            {"repo_path": "tools/materialize/register_fix38_backlog.py"},
            {
                "repo_path": (
                    "docs/phases/"
                    "phase_gap_cdl098_genesis_graph_materialization_0424_00b_walkthrough.md"
                )
            },
            {"repo_path": "tools/materialize/register_fix38_backlog.py"},
        ]
    }

    with pytest.raises(RuntimeError, match="source_report_ledger_count_mismatch"):
        register._validate_report(_valid_report(), ledger)


def test_known_node_ids_ignores_missing_candidate_ids() -> None:
    class _Store:
        def iter_nodes(self) -> list[dict]:
            return [{"candidate_id": "node:a"}, {"candidate_id": None}, {}]

    class _Writer:
        store = _Store()

    assert register._known_node_ids(_Writer()) == {"node:a"}  # type: ignore[arg-type]


def test_group_resume_verification_rejects_stale_phase_receipt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    repo_file = tmp_path / "docs/specs/a.md"
    repo_file.parent.mkdir(parents=True)
    repo_file.write_text("a\n", encoding="utf-8")

    atlas = tmp_path / "atlas.lmdb"
    group_id = "group_001_spec_document_node_support_candidate_graph_support_only"
    group_phase = f"{register.PHASE}:{group_id}"
    file_registration = [
        {
            "path": "docs/specs/a.md",
            "node_kind": "spec_document_node",
            "graph_projection": "support_candidate_graph",
            "graph_delta": "support_only",
        }
    ]
    writer = AtlasLmdbSafeWriter(atlas)
    try:
        dry_data = writer.register_phase_files(group_phase, file_registration, dry_run=True)
        write_data = writer.register_phase_files(group_phase, file_registration, dry_run=False)
    finally:
        writer.close()

    stale_write = dict(write_data)
    stale_write["phase"] = f"{register.PHASE}:different_group"
    with pytest.raises(RuntimeError, match="existing_group_receipt_phase_mismatch"):
        register._verify_group_receipt_and_lmdb(
            atlas=atlas,
            group_id=group_id,
            group_phase=group_phase,
            files=["docs/specs/a.md"],
            dry_data=dry_data,
            write_data=stale_write,
        )


def test_build_receipt_separates_phase_cumulative_and_current_run_counts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    repo_file = tmp_path / "docs/specs/a.md"
    repo_file.parent.mkdir(parents=True)
    repo_file.write_text("a\n", encoding="utf-8")

    ledger_path = tmp_path / "ledger.json"
    report_path = tmp_path / "report.json"
    ledger_path.write_text(
        json.dumps({"annotations": [{"repo_path": "docs/specs/a.md"}]}),
        encoding="utf-8",
    )
    report_path.write_text(json.dumps(_valid_report()), encoding="utf-8")

    statuses = [
        {
            "counts": {
                "nodes": 12,
                "edges": 22,
                "payload_nodes": 12,
                "payload_edges": 22,
                "preimages": 0,
            }
        },
        {
            "counts": {
                "nodes": 15,
                "edges": 25,
                "payload_nodes": 15,
                "payload_edges": 25,
                "preimages": 0,
            },
            "invariants": {"node_id_coverage": True},
        },
    ]
    monkeypatch.setattr(register, "_status_counts", lambda _atlas: statuses.pop(0))
    monkeypatch.setattr(
        register,
        "_register_groups",
        lambda **_kwargs: (
            [{"group_id": "g", "resume_lmdb_verified": True}],
            [
                {
                    "group_id": "g",
                    "resume_reused_existing_receipt": True,
                    "resume_lmdb_verified": True,
                    "skipped_node_count": 0,
                }
            ],
        ),
    )
    monkeypatch.setattr(
        register,
        "_materialize_sanitized_edges",
        lambda **_kwargs: {"sanitized_edges_written": 1},
    )
    monkeypatch.setattr(register, "_validate_atlas", lambda _atlas: {"verdict": "pass"})
    monkeypatch.setattr(register, "_write_per_file_summaries", lambda **_kwargs: 1)

    args = type(
        "Args",
        (),
        {
            "ledger": ledger_path,
            "backlog_report": report_path,
            "atlas": tmp_path / "atlas.lmdb",
            "out": tmp_path / "out",
        },
    )()
    receipt = register.build_receipt(args)

    assert receipt["nodes_registered"] == 5
    assert receipt["edges_registered"] == 5
    assert receipt["phase_cumulative_nodes_registered"] == 5
    assert receipt["phase_cumulative_edges_registered"] == 5
    assert receipt["current_run_nodes_registered"] == 3
    assert receipt["current_run_edges_registered"] == 3
    assert receipt["resume_mode_detected"] is True
    assert receipt["resume_reused_group_count"] == 1
    assert receipt["before_counts_source"] == "source_report_pre_phase_baseline"


def test_build_receipt_rejects_empty_invariant_map(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    repo_file = tmp_path / "docs/specs/a.md"
    repo_file.parent.mkdir(parents=True)
    repo_file.write_text("a\n", encoding="utf-8")
    ledger_path = tmp_path / "ledger.json"
    report_path = tmp_path / "report.json"
    ledger_path.write_text(
        json.dumps({"annotations": [{"repo_path": "docs/specs/a.md"}]}),
        encoding="utf-8",
    )
    report_path.write_text(json.dumps(_valid_report()), encoding="utf-8")

    statuses = [
        {"counts": {"nodes": 10, "edges": 20}},
        {"counts": {"nodes": 11, "edges": 21}, "invariants": {}},
    ]
    monkeypatch.setattr(register, "_status_counts", lambda _atlas: statuses.pop(0))
    monkeypatch.setattr(register, "_register_groups", lambda **_kwargs: ([], []))
    monkeypatch.setattr(
        register,
        "_materialize_sanitized_edges",
        lambda **_kwargs: {"sanitized_edges_written": 0},
    )
    monkeypatch.setattr(register, "_validate_atlas", lambda _atlas: {"verdict": "pass"})
    monkeypatch.setattr(register, "_write_per_file_summaries", lambda **_kwargs: 1)

    args = type(
        "Args",
        (),
        {
            "ledger": ledger_path,
            "backlog_report": report_path,
            "atlas": tmp_path / "atlas.lmdb",
            "out": tmp_path / "out",
        },
    )()
    with pytest.raises(RuntimeError, match="atlas_status_invariants_empty"):
        register.build_receipt(args)


def test_build_receipt_rejects_edge_only_baseline_drift_without_resume(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    repo_file = tmp_path / "docs/specs/a.md"
    repo_file.parent.mkdir(parents=True)
    repo_file.write_text("a\n", encoding="utf-8")
    ledger_path = tmp_path / "ledger.json"
    report_path = tmp_path / "report.json"
    ledger_path.write_text(
        json.dumps({"annotations": [{"repo_path": "docs/specs/a.md"}]}),
        encoding="utf-8",
    )
    report_path.write_text(json.dumps(_valid_report()), encoding="utf-8")

    statuses = [
        {"counts": {"nodes": 10, "edges": 21}},
        {"counts": {"nodes": 11, "edges": 22}, "invariants": {"node_id_coverage": True}},
    ]
    monkeypatch.setattr(register, "_status_counts", lambda _atlas: statuses.pop(0))
    monkeypatch.setattr(register, "_register_groups", lambda **_kwargs: ([], []))
    monkeypatch.setattr(
        register,
        "_materialize_sanitized_edges",
        lambda **_kwargs: {"sanitized_edges_written": 0},
    )
    monkeypatch.setattr(register, "_validate_atlas", lambda _atlas: {"verdict": "pass"})
    monkeypatch.setattr(register, "_write_per_file_summaries", lambda **_kwargs: 1)

    args = type(
        "Args",
        (),
        {
            "ledger": ledger_path,
            "backlog_report": report_path,
            "atlas": tmp_path / "atlas.lmdb",
            "out": tmp_path / "out",
        },
    )()
    with pytest.raises(
        RuntimeError,
        match="atlas_live_counts_differ_from_source_baseline_without_resume",
    ):
        register.build_receipt(args)


def test_materialize_sanitized_edges_reuses_existing_verified_receipt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    phase = f"{register.PHASE}:sanitized_proposed_edges"
    dry_receipt = {
        "status": "PASS",
        "phase": phase,
        "dry_run": True,
        "metadata": {"proposed_edge_count": 1},
        "accepted_edge_count": 1,
    }
    write_receipt = {
        "status": "PASS",
        "phase": phase,
        "dry_run": False,
        "metadata": {"proposed_edge_count": 1},
        "accepted_edge_count": 1,
        "skipped_edge_count": 0,
    }
    (out_dir / "sanitized_proposed_edges_dry_run_receipt.json").write_text(
        json.dumps(dry_receipt),
        encoding="utf-8",
    )
    (out_dir / "sanitized_proposed_edges_write_receipt.json").write_text(
        json.dumps(write_receipt),
        encoding="utf-8",
    )

    source = register.repo_file_ref_id("docs/specs/a.md")
    target = "target:node"

    class _Store:
        def iter_nodes(self) -> list[dict]:
            return [{"candidate_id": source}, {"candidate_id": target}]

        def iter_edges(self) -> list[dict]:
            return [{"source": source, "edge_type": "TESTS", "target": target}]

    class _Writer:
        store = _Store()

        def __init__(self, _atlas: Path) -> None:
            return None

        def apply_plan(self, _plan: object) -> dict:
            raise AssertionError("resume path must not rewrite sanitized edge receipts")

        def close(self) -> None:
            return None

    monkeypatch.setattr(register, "AtlasLmdbSafeWriter", _Writer)
    receipt = register._materialize_sanitized_edges(
        atlas=tmp_path / "atlas.lmdb",
        out_dir=out_dir,
        entries=[
            {
                "repo_path": "docs/specs/a.md",
                "proposed_semantic_edges": [{"edge_type": "TESTS", "target": target}],
                "proposed_authority_trace_edges": [],
            }
        ],
    )

    assert receipt["resume_reused_existing_receipt"] is True
    assert receipt["resume_lmdb_verified"] is True
    assert receipt["sanitized_edges_written"] == 1
    assert receipt["current_run_sanitized_edges_written"] == 0


def test_run_cli_rejects_non_bool_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Completed:
        returncode = 0
        stdout = json.dumps({"ok": 1, "data": {}})
        stderr = ""

    monkeypatch.setattr(register.subprocess, "run", lambda *_args, **_kwargs: _Completed())
    with pytest.raises(RuntimeError, match="atlas_cli_not_ok"):
        register._run_cli(["atlas", "status"])
