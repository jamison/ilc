from __future__ import annotations

import json
from pathlib import Path

import pytest

from ilc_core.epistemic.node_submission_runtime import EpistemicSubmissionError
from ilc_core.epistemic.truth_primitive_submission_runtime import validate_truth_primitive_submission
from tools.native_submit.run_multi_agent_smoke import (
    NETWORK_ID,
    build_signed_envelope,
    run_smoke,
)


def _run(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict[str, object]:
    store_path = tmp_path / "truth_graph.lmdb"
    monkeypatch.setenv("ILC_TRUTH_GRAPH_STORE_PATH", str(store_path))
    return run_smoke(out_dir=tmp_path / "out", store_path=store_path)


def _scenario(evidence: dict[str, object], name: str) -> dict[str, object]:
    rows = evidence["scenario_results"]
    assert isinstance(rows, list)
    matches = [row for row in rows if isinstance(row, dict) and row.get("name") == name]
    assert len(matches) == 1
    return matches[0]


def test_agent_a_signed_submission_accepted(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    evidence = _run(tmp_path, monkeypatch)
    row = _scenario(evidence, "agent_a_accept")
    assert row["pass"] is True
    assert isinstance(row["node_id"], str)
    assert str(row["node_id"]).startswith("bafyrei")
    assert row["nodes_written"] == 1
    assert row["graph_persistence"] == "persisted"


def test_agent_b_signed_submission_accepted_with_distinct_node(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    evidence = _run(tmp_path, monkeypatch)
    agent_a = _scenario(evidence, "agent_a_accept")
    agent_b = _scenario(evidence, "agent_b_accept")
    assert agent_b["pass"] is True
    assert agent_b["nodes_written"] == 1
    assert agent_b["node_id"] != agent_a["node_id"]
    assert evidence["agent_a_pk_hex"] != evidence["agent_b_pk_hex"]


def test_graph_write_idempotency_without_revalidation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    evidence = _run(tmp_path, monkeypatch)
    agent_a = _scenario(evidence, "agent_a_accept")
    row = _scenario(evidence, "graph_write_idempotent")
    assert row["pass"] is True
    assert row["node_id"] == agent_a["node_id"]
    assert row["nodes_written"] == 0


def test_invalid_signature_is_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    evidence = _run(tmp_path, monkeypatch)
    row = _scenario(evidence, "invalid_sig_rejected")
    assert row["pass"] is True
    assert row["rejection_token"] == "native_submit_sig_bls_verification_failed_CDL_118"


def test_key_ref_mismatch_is_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    evidence = _run(tmp_path, monkeypatch)
    row = _scenario(evidence, "key_ref_mismatch_rejected")
    assert row["pass"] is True
    assert row["rejection_token"] == "native_submit_sig_key_ref_agent_id_mismatch_CDL_118"


def test_signature_length_invalid_is_rejected(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    evidence = _run(tmp_path, monkeypatch)
    row = _scenario(evidence, "sig_length_invalid_rejected")
    assert row["pass"] is True
    assert row["rejection_token"] == "native_submit_sig_signature_hex_length_invalid_CDL_118"


def test_replay_is_rejected_by_lmdb_durable_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    evidence = _run(tmp_path, monkeypatch)
    row = _scenario(evidence, "replay_rejected")
    assert row["pass"] is True
    assert row["rejection_token"] == "native_submit_sig_replay_rejected_CDL_118"
    assert "ILC_TRUTH_GRAPH_STORE_PATH" in __import__("os").environ


def test_node_id_is_content_addressed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    evidence = _run(tmp_path, monkeypatch)
    row = _scenario(evidence, "node_id_deterministic")
    assert row["pass"] is True
    assert row["node_id_matches"] is True
    assert isinstance(row["node_id"], str)
    assert str(row["node_id"]).startswith("bafyrei")


def test_evidence_file_is_written_atomically_shaped(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    out_dir = tmp_path / "out"
    store_path = tmp_path / "truth_graph.lmdb"
    monkeypatch.setenv("ILC_TRUTH_GRAPH_STORE_PATH", str(store_path))
    evidence = run_smoke(out_dir=out_dir, store_path=store_path)
    evidence_path = out_dir / "smoke_evidence.json"
    assert evidence_path.exists()
    loaded = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert loaded == evidence
    assert loaded["all_scenarios_pass"] is True
    assert loaded["network_id"] == NETWORK_ID


def test_build_signed_envelope_rejects_if_tampered_after_signing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    evidence = _run(tmp_path, monkeypatch)
    agent_id = str(evidence["agent_a_pk_hex"])
    # Reuse public key only for shape; this adversarial case proves payload hash
    # mismatch is caught before any graph write.
    envelope = build_signed_envelope(
        secret_key_hex="11" * 32,
        agent_id=agent_id,
        claim="tamper test",
        epoch=99,
    )
    assert isinstance(envelope["payload"], dict)
    envelope["payload"]["content"] = {"claim": "tampered"}
    with pytest.raises(EpistemicSubmissionError) as exc_info:
        validate_truth_primitive_submission(envelope)
    assert exc_info.value.token == "native_submit_sig_payload_sha256_mismatch_IMPL_00"
