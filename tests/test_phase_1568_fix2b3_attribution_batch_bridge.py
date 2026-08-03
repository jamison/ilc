from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from ilc_core.consensus.attribution_batch_bridge import (
    AttributionBatchBridgeError,
    MAX_BACKWARD_ATTRIBUTION_EVENTS_PER_BATCH,
    _backward_attribution_batch_root,
    apply_attribution_batch_with_rust,
    build_attribution_batch_from_claims,
)
from tools import agent_loop_v1
from tests.test_agent_loop_v1_runtime import _cdl069_seed, _legacy_seed, _submission, _task


ROOT = Path(__file__).resolve().parents[1]
AGENT_A = "a" * 96
AGENT_B = "b" * 96


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


def _passing_claim_payload() -> dict[str, object]:
    submissions = [
        _submission(1, _cdl069_seed("01"), "cluster-a"),
        _submission(2, _cdl069_seed("02"), "cluster-b"),
        _submission(3, _cdl069_seed("03"), "cluster-c"),
        _submission(4, _cdl069_seed("04"), "cluster-a"),
        _submission(5, _cdl069_seed("05"), "cluster-b"),
        _submission(6, _cdl069_seed("06"), "cluster-c"),
        _submission(7, _cdl069_seed("07"), "cluster-d", variant="divergent"),
    ]
    outsider = agent_loop_v1._build_outsider_submission(_task(), _legacy_seed("08"), "cluster-e", "ilc-node-1")
    panel_payload = agent_loop_v1.evaluate_panel(task=_task(), submissions=submissions, outsider_submission=outsider)
    return agent_loop_v1.build_ecu_claim_batch(_task(), panel_payload)


def _simple_claim_payload() -> dict[str, object]:
    return {
        "claims": [
            {
                "agent_id": AGENT_B,
                "amount": "1",
                "claim_id": "claim-1",
                "epoch": 7,
            }
        ],
        "marker": "agent_loop_claims_ok",
    }


def _backward_node(agent_id: str) -> dict[str, object]:
    return {
        "artifact_type": "claim",
        "created_epoch": 0,
        "novelty_score": "1",
        "recipient_agent_id": agent_id,
        "status_quality_weight": "1",
    }


def _backward_edge(source: str, target: str) -> dict[str, object]:
    return {
        "edge_confidence": "1",
        "edge_type": "PROVENANCE",
        "source_node_id": source,
        "target_node_id": target,
    }


def _simple_backward_context() -> dict[str, object]:
    return {
        "edges": [_backward_edge("source", "upstream")],
        "events": [
            {
                "event_budget_ecu": "100",
                "event_epoch": 7,
                "event_id": "event-1",
                "source_node_id": "source",
            }
        ],
        "nodes": {
            "source": _backward_node(AGENT_B),
            "upstream": _backward_node(AGENT_A),
        },
    }


def _simple_werner_backward_context() -> dict[str, object]:
    context = _simple_backward_context()
    context["werner_context_by_agent_id"] = {
        AGENT_A: {
            "agent_id": AGENT_A,
            "epoch": 7,
            "raw_werner_pressure": "0.10",
        }
    }
    return context


def test_claim_payload_converts_to_consensus_attribution_batch_with_dust_accounting() -> None:
    claim_payload = _passing_claim_payload()

    batch = build_attribution_batch_from_claims(claim_payload)

    assert batch["marker"] == "attribution_batch_bridge_ok"
    assert batch["epoch"] == 574
    assert batch["rounding"] == "floor_to_micro_ecu_no_over_credit"
    assert batch["source_claim_count"] == 6
    assert batch["attribution_count"] == 6
    assert batch["total_source_ecu"] == "5.8173828125"
    assert batch["total_micro_ecu"] == 5817378
    assert batch["total_dust_ecu"] == "0.0000048125"
    assert [item["agent_id_hex"] for item in batch["attributions"]] == sorted(
        item["agent_id_hex"] for item in batch["attributions"]
    )
    assert all(item["amount_micro_ecu"] > 0 for item in batch["attributions"])


def test_bridge_rejects_malformed_agent_id() -> None:
    claim_payload = _passing_claim_payload()
    claim_payload["claims"][0]["agent_id"] = "AA"

    with pytest.raises(AttributionBatchBridgeError) as excinfo:
        build_attribution_batch_from_claims(claim_payload)

    assert excinfo.value.token == "agent_id_hex_must_be_96_lower_hex"


def test_bridge_rejects_duplicate_claim_id_in_same_batch() -> None:
    claim_payload = _passing_claim_payload()
    claim_payload["claims"][1]["claim_id"] = claim_payload["claims"][0]["claim_id"]

    with pytest.raises(AttributionBatchBridgeError) as excinfo:
        build_attribution_batch_from_claims(claim_payload)

    assert excinfo.value.token == "claim_id_duplicate_in_batch"


def test_bridge_rejects_claim_count_above_maximum() -> None:
    claim_payload = _passing_claim_payload()
    claim_payload["claims"] = [claim_payload["claims"][0]] * 10_001

    with pytest.raises(AttributionBatchBridgeError) as excinfo:
        build_attribution_batch_from_claims(claim_payload)

    assert excinfo.value.token == "claim_count_exceeds_maximum"


def test_bridge_rejects_single_attribution_amount_above_rust_u64() -> None:
    claim_payload = {
        "claims": [
            {
                "agent_id": AGENT_A,
                "amount": "18446744073709.551616",
                "claim_id": "claim-over-u64",
                "epoch": 7,
            }
        ],
        "marker": "agent_loop_claims_ok",
    }

    with pytest.raises(AttributionBatchBridgeError) as excinfo:
        build_attribution_batch_from_claims(claim_payload)

    assert excinfo.value.token == "claim_amount_micro_ecu_exceeds_u64"


def test_bridge_rejects_total_attribution_amount_above_rust_u64() -> None:
    claim_payload = {
        "claims": [
            {
                "agent_id": AGENT_A,
                "amount": "9223372036854.775808",
                "claim_id": "claim-half-a",
                "epoch": 7,
            },
            {
                "agent_id": AGENT_B,
                "amount": "9223372036854.775808",
                "claim_id": "claim-half-b",
                "epoch": 7,
            },
        ],
        "marker": "agent_loop_claims_ok",
    }

    with pytest.raises(AttributionBatchBridgeError) as excinfo:
        build_attribution_batch_from_claims(claim_payload)

    assert excinfo.value.token == "attribution_batch_total_micro_ecu_exceeds_u64"


def test_backward_root_requires_canonical_sorted_entries() -> None:
    sorted_entries = [
        {"event_id": "a", "recipient_agent_id": AGENT_A, "upstream_artifact_id": "node-a"},
        {"event_id": "b", "recipient_agent_id": AGENT_B, "upstream_artifact_id": "node-b"},
    ]
    unsorted_entries = list(reversed(sorted_entries))

    assert isinstance(_backward_attribution_batch_root(sorted_entries), str)
    with pytest.raises(AttributionBatchBridgeError) as excinfo:
        _backward_attribution_batch_root(unsorted_entries)

    assert excinfo.value.token == "backward_attribution_entries_must_be_canonical_sorted"


def test_attribution_event_log_retry_does_not_silently_overwrite(tmp_path: Path) -> None:
    build_attribution_batch_from_claims(
        _simple_claim_payload(),
        backward_attribution_graph_context=_simple_backward_context(),
        attribution_event_log_dir=tmp_path,
    )

    with pytest.raises(AttributionBatchBridgeError) as excinfo:
        build_attribution_batch_from_claims(
            _simple_claim_payload(),
            backward_attribution_graph_context=_simple_backward_context(),
            attribution_event_log_dir=tmp_path,
        )

    assert excinfo.value.token == "attribution_event_log_file_exists"


def test_bridge_rejects_duplicate_backward_event_id_in_same_batch() -> None:
    context = _simple_backward_context()
    context["events"].append(dict(context["events"][0]))

    with pytest.raises(AttributionBatchBridgeError) as excinfo:
        build_attribution_batch_from_claims(
            _simple_claim_payload(),
            backward_attribution_graph_context=context,
        )

    assert excinfo.value.token == "backward_event_id_duplicate_in_batch"


def test_bridge_rejects_backward_event_count_above_maximum() -> None:
    context = _simple_backward_context()
    template = context["events"][0]
    context["events"] = [
        {
            **template,
            "event_id": f"event-{index}",
        }
        for index in range(MAX_BACKWARD_ATTRIBUTION_EVENTS_PER_BATCH + 1)
    ]

    with pytest.raises(AttributionBatchBridgeError) as excinfo:
        build_attribution_batch_from_claims(
            _simple_claim_payload(),
            backward_attribution_graph_context=context,
        )

    assert excinfo.value.token == "backward_attribution_event_count_exceeds_maximum"


def test_zero_credit_backward_recipient_agent_id_is_still_validated() -> None:
    nodes = {"source": _backward_node(AGENT_B)}
    edges: list[dict[str, object]] = []
    for index in range(6):
        node_id = f"N{index}"
        recipient = "not-a-hex-agent" if index == 5 else f"{index:x}" * 96
        nodes[node_id] = _backward_node(recipient)
        edges.append(_backward_edge("source", node_id))
        edges.append(_backward_edge(node_id, "source"))
    context = {
        "edges": edges,
        "events": [
            {
                "event_budget_ecu": "1000",
                "event_epoch": 7,
                "event_id": "event-cluster",
                "source_node_id": "source",
            }
        ],
        "nodes": nodes,
    }

    with pytest.raises(AttributionBatchBridgeError) as excinfo:
        build_attribution_batch_from_claims(
            _simple_claim_payload(),
            backward_attribution_graph_context=context,
        )

    assert excinfo.value.token == "agent_id_hex_must_be_96_lower_hex"


def test_bridge_wraps_rust_ingest_timeout(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    def _timeout_run(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        raise subprocess.TimeoutExpired(cmd=["attribution_batch_ingest"], timeout=1)

    fake_binary = tmp_path / "attribution_batch_ingest"
    fake_binary.touch()
    monkeypatch.setattr(subprocess, "run", _timeout_run)

    with pytest.raises(AttributionBatchBridgeError) as excinfo:
        apply_attribution_batch_with_rust(
            build_attribution_batch_from_claims(_passing_claim_payload()),
            consensus_lmdb=tmp_path / "store.lmdb",
            rust_binary=fake_binary,
            dry_run=True,
            timeout_seconds=1,
        )

    assert excinfo.value.token == "rust_attribution_batch_ingest_timeout"


def test_agent_loop_cli_builds_attribution_batch(tmp_path: Path) -> None:
    claims_path = tmp_path / "ecu_claims.json"
    claims_path.write_text(
        json.dumps(_passing_claim_payload(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            "python3",
            "tools/agent_loop_v1.py",
            "build-attribution-batch",
            "--ecu-claims-file",
            str(claims_path),
            "--emit-dir",
            str(tmp_path),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["marker"] == "attribution_batch_bridge_ok"
    assert (tmp_path / "consensus_attribution_batch.json").exists()


def test_rust_ingest_applies_batch_and_rejects_same_epoch_replay(
    attribution_binary: Path,
    tmp_path: Path,
) -> None:
    batch = build_attribution_batch_from_claims(_passing_claim_payload())
    lmdb_path = tmp_path / "consensus-balances.lmdb"

    dry_run = apply_attribution_batch_with_rust(
        batch,
        consensus_lmdb=lmdb_path,
        rust_binary=attribution_binary,
        dry_run=True,
    )
    assert dry_run["marker"] == "attribution_batch_ingest_ok"
    assert dry_run["dry_run"] is True
    assert dry_run["total_micro_ecu"] == 5817378
    assert not lmdb_path.exists()

    applied = apply_attribution_batch_with_rust(
        batch,
        consensus_lmdb=lmdb_path,
        rust_binary=attribution_binary,
    )
    assert applied["marker"] == "attribution_batch_ingest_ok"
    assert applied["dry_run"] is False
    assert applied["attribution_count"] == 6
    assert sum(item["amount_micro_ecu"] for item in applied["balances"]) == 5817378
    assert all(item["epoch"] == 574 for item in applied["balances"])

    with pytest.raises(AttributionBatchBridgeError) as excinfo:
        apply_attribution_batch_with_rust(
            batch,
            consensus_lmdb=lmdb_path,
            rust_binary=attribution_binary,
        )
    assert excinfo.value.token == "rust_attribution_batch_ingest_failed"
    assert "Invalid epoch reference" in str(excinfo.value)


def test_rust_ingest_accepts_werner_context_backward_batch(
    attribution_binary: Path,
    tmp_path: Path,
) -> None:
    batch = build_attribution_batch_from_claims(
        _simple_claim_payload(),
        backward_attribution_graph_context=_simple_werner_backward_context(),
    )

    assert batch["werner_context_count"] == 1
    assert batch["backward_attribution_batch_root"] is not None
    dry_run = apply_attribution_batch_with_rust(
        batch,
        consensus_lmdb=tmp_path / "werner-context.lmdb",
        rust_binary=attribution_binary,
        dry_run=True,
    )

    assert dry_run["marker"] == "attribution_batch_ingest_ok"
    assert dry_run["dry_run"] is True


def test_agent_loop_cli_apply_attribution_batch(
    attribution_binary: Path,
    tmp_path: Path,
) -> None:
    batch_path = tmp_path / "consensus_attribution_batch.json"
    batch_path.write_text(
        json.dumps(build_attribution_batch_from_claims(_passing_claim_payload()), sort_keys=True) + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            "python3",
            "tools/agent_loop_v1.py",
            "apply-attribution-batch",
            "--attribution-batch-file",
            str(batch_path),
            "--consensus-lmdb",
            str(tmp_path / "store.lmdb"),
            "--rust-binary",
            str(attribution_binary),
            "--emit-dir",
            str(tmp_path),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["marker"] == "attribution_batch_ingest_ok"
    assert (tmp_path / "consensus_attribution_apply_receipt.json").exists()
