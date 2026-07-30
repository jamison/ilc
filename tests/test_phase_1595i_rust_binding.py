from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from ilc_core.consensus.attribution_batch_bridge import (
    AttributionBatchBridgeError,
    apply_attribution_batch_with_rust,
    build_attribution_batch_from_claims,
)


ROOT = Path(__file__).resolve().parents[1]
AGENT_A = "a" * 96
AGENT_1 = "1" * 96


def _cargo() -> str:
    discovered = shutil.which("cargo")
    if discovered:
        return discovered
    fallback = Path.home() / ".cargo" / "bin" / "cargo"
    if fallback.exists():
        return str(fallback)
    return "cargo"


@pytest.fixture(scope="session")
def attribution_binary() -> Path:
    result = subprocess.run(
        [
            _cargo(),
            "build",
            "--manifest-path",
            str(ROOT / "ilc_consensus" / "Cargo.toml"),
            "--bin",
            "attribution_batch_ingest",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=180,
    )
    assert result.returncode == 0, result.stderr
    binary = ROOT / "ilc_consensus" / "target" / "debug" / "attribution_batch_ingest"
    assert binary.exists()
    return binary


def _node(agent_id: str, *, novelty: str = "1", status: str = "1") -> dict[str, object]:
    return {
        "artifact_type": "claim",
        "created_epoch": 0,
        "novelty_score": novelty,
        "recipient_agent_id": agent_id,
        "status_quality_weight": status,
    }


def _edge(source: str, target: str) -> dict[str, object]:
    return {
        "edge_confidence": "1",
        "edge_type": "PROVENANCE",
        "source_node_id": source,
        "target_node_id": target,
    }


def _claim_payload() -> dict[str, object]:
    return {
        "claims": [
            {
                "agent_id": AGENT_A,
                "amount": "1",
                "claim_id": "claim-direct",
                "epoch": 9,
            }
        ],
        "marker": "agent_loop_claims_ok",
    }


def _graph_context(*, event_budget_ecu: str = "100") -> dict[str, object]:
    return {
        "edges": [_edge("source", "upstream")],
        "events": [
            {
                "event_budget_ecu": event_budget_ecu,
                "event_epoch": 9,
                "event_id": "event-rust-root",
                "source_node_id": "source",
            }
        ],
        "nodes": {"source": _node(AGENT_A), "upstream": _node(AGENT_1)},
    }


def _batch_with_backward_root(*, event_budget_ecu: str = "100") -> dict[str, object]:
    return build_attribution_batch_from_claims(
        _claim_payload(),
        backward_attribution_graph_context=_graph_context(event_budget_ecu=event_budget_ecu),
    )


def test_backward_attribution_root_present_when_credits_exist() -> None:
    batch = _batch_with_backward_root()

    root = batch["backward_attribution_batch_root"]
    assert isinstance(root, str)
    assert re.fullmatch(r"[0-9a-f]{64}", root)
    assert batch["backward_attribution_entry_count"] == 1


def test_backward_attribution_root_none_when_no_credits() -> None:
    batch = build_attribution_batch_from_claims(
        _claim_payload(),
        backward_attribution_graph_context={
            "edges": [_edge("source", "upstream")],
            "events": [
                {
                    "already_settled_by_cdl084": True,
                    "event_budget_ecu": "100",
                    "event_epoch": 9,
                    "event_id": "event-no-root",
                    "source_node_id": "source",
                }
            ],
            "nodes": {"source": _node(AGENT_A), "upstream": _node(AGENT_1)},
        },
        cdl084_settled_event_ids={"event-no-root"},
    )

    assert batch["backward_attribution_entry_count"] == 0
    assert batch["backward_attribution_batch_root"] is None


def test_backward_attribution_root_deterministic() -> None:
    first = _batch_with_backward_root()
    second = _batch_with_backward_root()

    assert first["backward_attribution_batch_root"] == second["backward_attribution_batch_root"]
    assert json.dumps(first["backward_attribution_entries"], sort_keys=True) == json.dumps(
        second["backward_attribution_entries"],
        sort_keys=True,
    )


def test_backward_attribution_root_changes_on_different_credits() -> None:
    first = _batch_with_backward_root(event_budget_ecu="100")
    second = _batch_with_backward_root(event_budget_ecu="101")

    assert first["backward_attribution_batch_root"] != second["backward_attribution_batch_root"]
    assert first["backward_attribution_entries"] != second["backward_attribution_entries"]


def test_rust_ingestion_accepts_batch_with_root(
    attribution_binary: Path,
    tmp_path: Path,
) -> None:
    batch = _batch_with_backward_root()
    report = apply_attribution_batch_with_rust(
        batch,
        consensus_lmdb=tmp_path / "store.lmdb",
        rust_binary=attribution_binary,
        dry_run=True,
    )

    assert report["marker"] == "attribution_batch_ingest_ok"
    assert report["dry_run"] is True
    assert report["backward_attribution_batch_root"] == batch["backward_attribution_batch_root"]


def test_rust_ingestion_accepts_batch_without_root(
    attribution_binary: Path,
    tmp_path: Path,
) -> None:
    batch = build_attribution_batch_from_claims(_claim_payload())
    report = apply_attribution_batch_with_rust(
        batch,
        consensus_lmdb=tmp_path / "store.lmdb",
        rust_binary=attribution_binary,
        dry_run=True,
    )

    assert report["marker"] == "attribution_batch_ingest_ok"
    assert report["backward_attribution_batch_root"] is None


def test_epoch_settlement_record_schema_not_modified() -> None:
    source = (ROOT / "ilc_consensus" / "src" / "types.rs").read_text(encoding="utf-8")
    settlement_match = re.search(
        r"struct EpochSettlementRecord \{(?P<body>.*?)\n\}",
        source,
        flags=re.DOTALL,
    )
    attribution_match = re.search(
        r"struct AttributionBatch \{(?P<body>.*?)\n\}",
        source,
        flags=re.DOTALL,
    )
    assert settlement_match is not None
    assert attribution_match is not None
    assert "backward_attribution_batch_root" not in settlement_match.group("body")
    assert "backward_attribution_batch_root: Option<[u8; 32]>" in attribution_match.group("body")


def test_rust_ingestion_rejects_malformed_backward_root(
    attribution_binary: Path,
    tmp_path: Path,
) -> None:
    batch = _batch_with_backward_root()
    batch["backward_attribution_batch_root"] = "0" * 63

    with pytest.raises(AttributionBatchBridgeError) as excinfo:
        apply_attribution_batch_with_rust(
            batch,
            consensus_lmdb=tmp_path / "store.lmdb",
            rust_binary=attribution_binary,
            dry_run=True,
        )

    assert excinfo.value.token == "rust_attribution_batch_ingest_failed"
    assert "backward_attribution_batch_root_must_be_64_hex" in str(excinfo.value)
