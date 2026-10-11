#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Generate native-submit parity vectors for the Rust QUIC receiver lane."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

from ilc_core.cli.d2e_submit_cli import _build_native_submit_sig_object
from ilc_core.encoding.cidv1 import node_id_from_obj
from ilc_core.epistemic.truth_primitive_graph_store import (
    node_record_from_submission,
    write_truth_primitive_result,
)
from ilc_core.epistemic.truth_primitive_submission_runtime import (
    EpistemicSubmissionError,
    native_submit_replay_record_from_envelope,
    validate_truth_primitive_submission,
)
from ilc_core.identity.bls_backend import (
    keypair_from_ikm_hex,
    verify_native_submit_bytes,
)
from ilc_core.storage.truth_primitive_graph_lmdb_adapter import TruthPrimitiveGraphStore


PHASE = "GAP-NATIVE-QUIC-RECEIVER-PARITY-VECTORS-00"
NETWORK_ID = "ilc-public-rc-01-testnet-harness"
VECTOR_SCHEMA_VERSION = "native_quic_receiver_parity_vectors.v0.2"
IKM_HEXES = ("11" * 32, "22" * 32, "33" * 32, "44" * 32, "55" * 32)


def _canonical_bytes(envelope: dict[str, Any]) -> bytes:
    return json.dumps(
        {key: value for key, value in envelope.items() if key != "sig"},
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _keypairs() -> list[tuple[str, str]]:
    return [keypair_from_ikm_hex(ikm) for ikm in IKM_HEXES]


def _parent_id(label: str) -> str:
    return node_id_from_obj({"phase": PHASE, "parent": label})


def _assert_truth_payload(index: int) -> dict[str, Any]:
    return {
        "content": {
            "claim": f"native QUIC node vector {index}",
            "nested": {"index": index, "reverse": list(reversed(range(index + 1)))},
        },
        "primitive_type": "observation",
        "epistemic_type": "objective" if index % 4 == 0 else "subjective",
        "parent_node_ids": [_parent_id(f"node-parent-{index}")] if index in {2, 4} else [],
    }


def _revise_assert_payload(index: int) -> dict[str, Any]:
    return {
        "source_node_id": _parent_id(f"revise-source-{index}"),
        "revised_content": {
            "primitive_type": "observation",
            "claim": f"native QUIC revised node vector {index}",
            "confidence": "0.91",
            "nested": {"index": index, "correction": True},
        },
        "revision_rationale": f"bounded correction fixture {index}",
    }


def _node_creating_envelopes() -> list[dict[str, Any]]:
    envelopes: list[dict[str, Any]] = []
    for index, (secret_hex, agent_id) in enumerate(_keypairs()):
        primitive = "assert.truth" if index % 2 == 0 else "revise.assert"
        envelope: dict[str, Any] = {
            "v": 1,
            "primitive": primitive,
            "agent_id": agent_id,
            "epoch": index,
            "payload": (
                _assert_truth_payload(index)
                if primitive == "assert.truth"
                else _revise_assert_payload(index)
            ),
        }
        if index == 2:
            envelope["uncertainty_declared"] = "bounded parity-vector uncertainty fixture"
        envelope["sig"] = _build_native_submit_sig_object(
            envelope,
            secret_hex,
            network_id=NETWORK_ID,
        )
        envelopes.append(envelope)
    return envelopes


def _source_case_id(index: int) -> str:
    return f"node-{index}"


def _vector_set_1(envelopes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "case_id": f"canonical-envelope-{index}",
            "source_case_id": _source_case_id(index),
            "input": envelope,
            "expected_output": _canonical_bytes(envelope).hex(),
        }
        for index, envelope in enumerate(envelopes)
    ]


def _vector_set_2(envelopes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "case_id": f"payload-sha256-{index}",
            "source_case_id": _source_case_id(index),
            "input": envelope,
            "expected_output": hashlib.sha256(_canonical_bytes(envelope)).hexdigest(),
        }
        for index, envelope in enumerate(envelopes)
    ]


def _vector_set_3(envelopes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for index, envelope in enumerate(envelopes):
        message = _canonical_bytes(envelope)
        public_key_hex = str(envelope["agent_id"])
        signature_hex = str(envelope["sig"]["signature_hex"])
        entries.append(
            {
                "case_id": f"bls-sign-verify-{index}",
                "source_case_id": _source_case_id(index),
                "input": {
                    "message_bytes_hex": message.hex(),
                    "network_id": NETWORK_ID,
                    "public_key_hex": public_key_hex,
                    "signature_hex": signature_hex,
                },
                "expected_output": {
                    "verify_result": verify_native_submit_bytes(
                        public_key_hex, message, signature_hex, NETWORK_ID
                    ),
                    "expected_verify_result": True,
                },
            }
        )

    message = _canonical_bytes(envelopes[0])
    signature_hex = str(envelopes[0]["sig"]["signature_hex"])
    tampered_message = bytes([message[0] ^ 0x01]) + message[1:]
    adversarial_cases = [
        (
            "bls-invalid-tampered-message",
            tampered_message,
            str(envelopes[0]["agent_id"]),
            signature_hex,
            NETWORK_ID,
        ),
        (
            "bls-invalid-wrong-public-key",
            message,
            str(envelopes[1]["agent_id"]),
            signature_hex,
            NETWORK_ID,
        ),
        (
            "bls-invalid-wrong-network-id",
            message,
            str(envelopes[0]["agent_id"]),
            signature_hex,
            "ilc-public-rc-wrong-network",
        ),
        (
            "bls-invalid-zero-signature",
            message,
            str(envelopes[0]["agent_id"]),
            "00" * 96,
            NETWORK_ID,
        ),
        (
            "bls-invalid-short-signature",
            message,
            str(envelopes[0]["agent_id"]),
            "00" * 95,
            NETWORK_ID,
        ),
    ]
    for case_id, message_bytes, public_key_hex, sig_hex, network_id in adversarial_cases:
        entries.append(
            {
                "case_id": case_id,
                "source_case_id": "node-0",
                "input": {
                    "message_bytes_hex": message_bytes.hex(),
                    "network_id": network_id,
                    "public_key_hex": public_key_hex,
                    "signature_hex": sig_hex,
                },
                "expected_output": {
                    "verify_result": verify_native_submit_bytes(
                        public_key_hex, message_bytes, sig_hex, network_id
                    ),
                    "expected_verify_result": False,
                },
            }
        )
    return entries


def _vector_set_4(envelopes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    replay_inputs = envelopes + [envelopes[1]]
    seen: set[str] = set()
    entries: list[dict[str, Any]] = []
    for index, envelope in enumerate(replay_inputs):
        replay_record = native_submit_replay_record_from_envelope(envelope)
        if replay_record is None:
            raise RuntimeError("native_submit_replay_record_missing")
        replay_key, replay_payload = replay_record
        is_replay = replay_key in seen
        seen.add(replay_key)
        entries.append(
            {
                "case_id": f"replay-triple-{index}",
                "source_case_id": _source_case_id(1 if index == len(envelopes) else index),
                "input": envelope,
                "expected_output": {
                    "replay_key": replay_key,
                    "replay_payload": replay_payload,
                    "is_replay": is_replay,
                },
            }
        )
    return entries


def _vector_sets_5_and_6(
    envelopes: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    set_5: list[dict[str, Any]] = []
    set_6: list[dict[str, Any]] = []
    for index, envelope in enumerate(envelopes):
        result = validate_truth_primitive_submission(envelope)
        record = node_record_from_submission(envelope, result)
        node_id = node_id_from_obj(record)
        set_5.append(
            {
                "case_id": f"node-record-{index}",
                "source_case_id": _source_case_id(index),
                "input": envelope,
                "result": {
                    "primitive": result.primitive,
                    "creates_node": result.creates_node,
                    "node_primitive_type": result.node_primitive_type,
                },
                "expected_output": record,
            }
        )
        set_6.append(
            {
                "case_id": f"cidv1-node-record-{index}",
                "source_case_id": _source_case_id(index),
                "input": record,
                "expected_output": node_id,
            }
        )
    return set_5, set_6


def _vector_set_7(envelopes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for index, envelope in enumerate(envelopes):
        temp_root = Path(tempfile.mkdtemp(prefix=f"ilc-native-quic-parity-{index}-"))
        store = TruthPrimitiveGraphStore(temp_root)
        try:
            result = validate_truth_primitive_submission(envelope)
            receipt = write_truth_primitive_result(store, envelope, result)
            second_write_replay_rejected = False
            second_write_error_token = ""
            try:
                write_truth_primitive_result(store, envelope, result)
            except EpistemicSubmissionError as exc:
                if exc.token != "native_submit_sig_replay_rejected_CDL_118":
                    raise
                second_write_replay_rejected = True
                second_write_error_token = exc.token

            replay_record = native_submit_replay_record_from_envelope(envelope)
            if replay_record is None:
                raise RuntimeError("native_submit_replay_record_missing")
            node_rows = store.dump_raw_db_hex(b"nodes")
            edge_rows = store.dump_raw_db_hex(b"edges")
            replay_rows = store.dump_raw_db_hex(b"native_submit_replay")
            if len(node_rows) != 1:
                raise RuntimeError(f"unexpected_node_row_count:{len(node_rows)}")
            if len(replay_rows) != 1:
                raise RuntimeError(f"unexpected_replay_row_count:{len(replay_rows)}")
            entries.append(
                {
                    "case_id": f"lmdb-batch-shape-{index}",
                    "source_case_id": _source_case_id(index),
                    "input": envelope,
                    "receipt": receipt,
                    "expected_output": {
                        "node_key": node_rows[0]["key_hex"],
                        "node_value": node_rows[0]["value_hex"],
                        "edge_keys": [row["key_hex"] for row in edge_rows],
                        "edge_values": [row["value_hex"] for row in edge_rows],
                        "replay_key": replay_rows[0]["key_hex"],
                        "replay_value": replay_rows[0]["value_hex"],
                        "logical_replay_key": replay_record[0],
                        "second_write_replay_rejected": second_write_replay_rejected,
                        "second_write_error_token": second_write_error_token,
                    },
                }
            )
        finally:
            store.close()
            shutil.rmtree(temp_root)
    return entries


def build_vectors() -> dict[str, Any]:
    node_envelopes = _node_creating_envelopes()
    vector_set_5, vector_set_6 = _vector_sets_5_and_6(node_envelopes)
    return {
        "metadata": {
            "phase": PHASE,
            "schema_version": VECTOR_SCHEMA_VERSION,
            "network_id": NETWORK_ID,
            "non_claims": [
                "no_runtime_change",
                "no_vps_action",
                "no_rust_implementation",
                "no_cdl_mutation",
            ],
        },
        "vector_set_1": _vector_set_1(node_envelopes),
        "vector_set_2": _vector_set_2(node_envelopes),
        "vector_set_3": _vector_set_3(node_envelopes),
        "vector_set_4": _vector_set_4(node_envelopes),
        "vector_set_5": vector_set_5,
        "vector_set_6": vector_set_6,
        "vector_set_7": _vector_set_7(node_envelopes),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("out/gap_native_quic_receiver_parity_vectors_00/parity_vectors.json"),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    vectors = build_vectors()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = args.out.with_suffix(args.out.suffix + ".tmp")
    tmp_path.write_text(
        json.dumps(vectors, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    tmp_path.replace(args.out)
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
