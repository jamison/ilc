"""Phase 1545p-Fix56 projection-aware Fiedler rebaseline checks."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "docs/phases/STATUS.md"
REPORT = ROOT / "out/genesis_atlas_fix56_fiedler_rebaseline_report_v0.1.json"
PUBLIC_CLUSTER = ROOT / "out/genesis_atlas_fix56_fiedler_public_eligible_minority_cluster_v0.1.json"
AUTHORITY_CLUSTER = ROOT / "out/genesis_atlas_fix56_fiedler_authority_only_minority_cluster_v0.1.json"
LEDGER = ROOT / "docs/specs/ilc_fix57_public_eligible_minority_audit_ledger_v0.1.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1545p_fix56_projection_aware_fiedler_rebaseline_walkthrough.md"
EVALUATOR = ROOT / "tools/evaluators/sim_genesis_atlas_fix56_projection_aware_fiedler_rebaseline.py"


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_fix56_complete_token_in_status() -> None:
    assert "fix56_complete" in STATUS.read_text(encoding="utf-8")


def test_fix56_report_exists_and_valid() -> None:
    payload = _read_json(REPORT)

    assert payload["status"] == "PASS"
    assert payload["phase"] == "1545p-Fix56"
    assert set(payload["projections"]) == {"all_local", "authority_only", "public_eligible"}


def test_fix56_all_local_lambda2_recorded() -> None:
    payload = _read_json(REPORT)

    assert isinstance(payload["projections"]["all_local"]["lambda2"], float)
    assert payload["projections"]["all_local"]["lambda2"] > 0.0


def test_fix56_public_eligible_minority_cluster_exists() -> None:
    payload = _read_json(PUBLIC_CLUSTER)

    assert payload["projection"] == "public_eligible"
    assert isinstance(payload["nodes"], list)
    assert payload["minority_cluster_size"] == len(payload["nodes"])


def test_fix56_authority_only_projection_nonempty() -> None:
    payload = _read_json(REPORT)

    assert payload["projections"]["authority_only"]["node_count"] > 0
    assert _read_json(AUTHORITY_CLUSTER)["projection"] == "authority_only"


def test_fix56_fix57_ledger_exists() -> None:
    text = LEDGER.read_text(encoding="utf-8")

    assert "| # | node_id | path/description | current_edges | graph_projection | recommended_edge_type | recommended_target | disposition | notes |" in text
    assert "Fix57 fills in recommended_edge_type" in text


def test_fix56_no_private_nodes_in_public_eligible_cluster() -> None:
    payload = _read_json(PUBLIC_CLUSTER)

    assert all(node["graph_projection"] != "excluded_private_material" for node in payload["nodes"])
    assert all(node["graph_projection"] != "review_required" for node in payload["nodes"])


def test_fix56_fiedler_caveat_in_walkthrough() -> None:
    text = WALKTHROUGH.read_text(encoding="utf-8")

    assert "spectral relaxation" in text


def test_fix56_evaluator_does_not_call_lmdb_put_methods() -> None:
    text = EVALUATOR.read_text(encoding="utf-8")

    forbidden = (
        "GenesisAtlasCandidateStore",
        "put_nodes(",
        "put_edges(",
        "put_graph_payload(",
        "put_meta(",
        "_put_json(",
        "write=True",
    )
    assert all(token not in text for token in forbidden)


def test_fix56_evaluator_opens_lmdb_readonly() -> None:
    text = EVALUATOR.read_text(encoding="utf-8")

    assert "readonly=True" in text
    assert "create=False" in text
    assert "lock=False" in text
