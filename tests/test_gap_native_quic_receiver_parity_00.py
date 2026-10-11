from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from ilc_core.identity.bls_backend import verify_native_submit_bytes


GENERATOR = Path("tools/generate_native_submit_parity_vectors.py")
REPLAY_TOKEN = "native_submit_sig_replay_rejected_CDL_118"


def _run_generator(out_path: Path) -> dict[str, object]:
    result = subprocess.run(
        [sys.executable, str(GENERATOR), "--out", str(out_path)],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(out_path.read_text(encoding="utf-8"))


def _walk_json(value: Any) -> list[Any]:
    seen = [value]
    if isinstance(value, dict):
        for key, child in value.items():
            seen.append(key)
            seen.extend(_walk_json(child))
    elif isinstance(value, list):
        for child in value:
            seen.extend(_walk_json(child))
    return seen


@pytest.fixture(scope="module")
def parity_vectors(tmp_path_factory: pytest.TempPathFactory) -> dict[str, object]:
    return _run_generator(tmp_path_factory.mktemp("parity") / "vectors.json")


def test_generator_is_stable_across_runs(tmp_path: Path) -> None:
    first = _run_generator(tmp_path / "first.json")
    second = _run_generator(tmp_path / "second.json")

    assert first == second


def test_all_vector_sets_have_at_least_five_entries(parity_vectors: dict[str, object]) -> None:
    for index in range(1, 8):
        vector_set = parity_vectors[f"vector_set_{index}"]
        assert isinstance(vector_set, list)
        assert len(vector_set) >= 5


def test_vectors_do_not_commit_secret_material(parity_vectors: dict[str, object]) -> None:
    all_values = _walk_json(parity_vectors)
    assert "secret_hex" not in all_values


def test_bls_verify_vectors_match_expected_results(parity_vectors: dict[str, object]) -> None:
    adversarial_ids = {
        "bls-invalid-tampered-message",
        "bls-invalid-wrong-public-key",
        "bls-invalid-wrong-network-id",
        "bls-invalid-zero-signature",
        "bls-invalid-short-signature",
    }
    observed_adversarial: set[str] = set()
    for entry in parity_vectors["vector_set_3"]:
        input_payload = entry["input"]
        expected = entry["expected_output"]["expected_verify_result"]
        observed = verify_native_submit_bytes(
            input_payload["public_key_hex"],
            bytes.fromhex(input_payload["message_bytes_hex"]),
            input_payload["signature_hex"],
            input_payload["network_id"],
        )
        assert observed == expected
        assert entry["expected_output"]["verify_result"] == expected
        if entry["case_id"] in adversarial_ids:
            observed_adversarial.add(entry["case_id"])
            assert expected is False
    assert observed_adversarial == adversarial_ids


def test_replay_vectors_use_signed_envelope_sig_payload_sha256(
    parity_vectors: dict[str, object],
) -> None:
    replay_seen = False
    for entry in parity_vectors["vector_set_4"]:
        envelope = entry["input"]
        expected = entry["expected_output"]
        assert isinstance(envelope["sig"], dict)
        assert expected["replay_payload"]["payload_sha256"] == envelope["sig"]["payload_sha256"]
        assert expected["replay_payload"]["agent_id"] == envelope["agent_id"]
        assert expected["replay_payload"]["epoch"] == envelope["epoch"]
        replay_seen = replay_seen or bool(expected["is_replay"])
    assert replay_seen is True


def test_node_record_vectors_use_real_validation_results(parity_vectors: dict[str, object]) -> None:
    primitives: set[str] = set()
    for entry in parity_vectors["vector_set_5"]:
        result = entry["result"]
        record = entry["expected_output"]
        primitive = result["primitive"]
        primitives.add(primitive)
        assert primitive in {"assert.truth", "revise.assert"}
        assert result["creates_node"] is True
        assert result["node_primitive_type"] == record["primitive_type"]
        assert record["primitive"] == primitive
        assert record["native_submit_sig"] == entry["input"]["sig"]
    assert primitives == {"assert.truth", "revise.assert"}


def test_cross_set_trace_consistency(parity_vectors: dict[str, object]) -> None:
    set_1 = {entry["source_case_id"]: entry for entry in parity_vectors["vector_set_1"]}
    set_2 = {entry["source_case_id"]: entry for entry in parity_vectors["vector_set_2"]}
    set_3_valid = {
        entry["source_case_id"]: entry
        for entry in parity_vectors["vector_set_3"]
        if str(entry["case_id"]).startswith("bls-sign-verify-")
    }
    set_5 = {entry["source_case_id"]: entry for entry in parity_vectors["vector_set_5"]}
    set_6 = {entry["source_case_id"]: entry for entry in parity_vectors["vector_set_6"]}
    set_7 = {entry["source_case_id"]: entry for entry in parity_vectors["vector_set_7"]}

    assert set(set_1) == set(set_2) == set(set_3_valid) == set(set_5) == set(set_6) == set(set_7)
    for source_case_id, canonical_entry in set_1.items():
        canonical_bytes = bytes.fromhex(canonical_entry["expected_output"])
        assert hashlib.sha256(canonical_bytes).hexdigest() == set_2[source_case_id][
            "expected_output"
        ]
        assert set_3_valid[source_case_id]["input"]["message_bytes_hex"] == canonical_entry[
            "expected_output"
        ]
        assert set_5[source_case_id]["expected_output"] == set_6[source_case_id]["input"]
        assert set_6[source_case_id]["expected_output"] == bytes.fromhex(
            set_7[source_case_id]["expected_output"]["node_key"]
        ).decode("utf-8")


def test_lmdb_batch_vectors_capture_physical_keys_values_and_replay_rejection(
    parity_vectors: dict[str, object],
) -> None:
    for entry in parity_vectors["vector_set_7"]:
        expected = entry["expected_output"]
        assert bytes.fromhex(expected["node_key"]).decode("utf-8").startswith("b")
        assert bytes.fromhex(expected["node_value"]).startswith(b"{")
        assert expected["edge_keys"]
        assert all(bytes.fromhex(edge_key) for edge_key in expected["edge_keys"])
        assert bytes.fromhex(expected["replay_key"]).decode("utf-8").startswith(
            "native_submit_replay:v1:"
        )
        assert bytes.fromhex(expected["replay_value"]).startswith(b"{")
        assert expected["logical_replay_key"] == bytes.fromhex(
            expected["replay_key"]
        ).decode("utf-8")
        assert expected["second_write_replay_rejected"] is True
        assert expected["second_write_error_token"] == REPLAY_TOKEN
