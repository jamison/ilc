# SPDX-License-Identifier: AGPL-3.0-only
"""Tests for GAP-MONTHLY-CLOSE-GRAPH-BINDING-LMDB-FIX1-00a."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import lmdb
import pytest

from ilc_core.consensus.validator_endpoint_assertion import (
    VALIDATOR_ENDPOINT_ASSERTION_NODE_KIND,
    VALIDATOR_ENDPOINT_ASSERTION_SCHEMA_VERSION,
    ValidatorEndpointAssertion,
    assertion_is_superseded,
    load_from_atlas,
    validator_assertion_candidate_id,
)
from ilc_core.storage.lmdb_public_runtime import LmdbGraphStore


SCRIPT_PATH = Path("tools/monthly_close/run_monthly_close.py")
AGENT_ID = "a" * 96


def _load_script_module():
    spec = importlib.util.spec_from_file_location("gap_run_monthly_close", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _minimal_node(*, revised_by: str | None = None) -> dict[str, object]:
    return {
        "asserted_at_epoch": 0,
        "bls_public_key_hex": "b" * 96,
        "bls_signature_hex": "c" * 192,
        "genesis_witness": True,
        "grpc_endpoint": "164.90.201.11:50151",
        "node_kind": VALIDATOR_ENDPOINT_ASSERTION_NODE_KIND,
        "schema_version": VALIDATOR_ENDPOINT_ASSERTION_SCHEMA_VERSION,
        "tls_cert_not_after_utc": None,
        "tls_cert_not_before_utc": "2026-01-01T00:00:00Z",
        "tls_cert_sha256_fingerprint": "f" * 64,
        "validator_agent_id": AGENT_ID,
        "revised_by": revised_by,
    }


def _write_assertion(path: Path, *, revised_by: str | None = None) -> None:
    store = LmdbGraphStore(path)
    try:
        store.put_node(
            validator_assertion_candidate_id(AGENT_ID),
            _minimal_node(revised_by=revised_by),
        )
    finally:
        store.close()


def _write_minimal_nodes_only_lmdb(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    env = lmdb.open(str(path), subdir=True, max_dbs=4, map_size=1024 * 1024)
    try:
        nodes_db = env.open_db(b"nodes")
        with env.begin(write=True, db=nodes_db) as txn:
            txn.put(
                validator_assertion_candidate_id(AGENT_ID).encode("utf-8"),
                json.dumps(
                    _minimal_node(),
                    sort_keys=True,
                    separators=(",", ":"),
                    allow_nan=False,
                ).encode("utf-8"),
            )
    finally:
        env.close()


def test_graph_binding_atlas_loader_accepts_lmdb_directory(tmp_path):
    module = _load_script_module()
    lmdb_path = tmp_path / "assertions_lmdb"
    _write_assertion(lmdb_path)

    store = module._load_graph_binding_atlas(lmdb_path)
    try:
        assert isinstance(store, module.ReadOnlyLmdbGraphStore)
        assertion = load_from_atlas(store, AGENT_ID)
        assert isinstance(assertion, ValidatorEndpointAssertion)
        assert assertion.validator_agent_id == AGENT_ID
    finally:
        store.close()


def test_graph_binding_atlas_loader_rejects_json_file(tmp_path):
    module = _load_script_module()
    json_path = tmp_path / "manifest.json"
    json_path.write_text("{}", encoding="utf-8")

    with pytest.raises(ValueError, match="graph_binding_atlas_path_not_an_lmdb_directory"):
        module._load_graph_binding_atlas(json_path)


def test_graph_binding_path_validation_rejects_json_file(tmp_path):
    module = _load_script_module()
    cert_path = tmp_path / "cert.pem"
    cert_path.write_text("fixture", encoding="utf-8")
    evidence_path = tmp_path / "evidence.json"
    evidence_path.write_text("{}", encoding="utf-8")
    json_path = tmp_path / "manifest.json"
    json_path.write_text("{}", encoding="utf-8")
    args = SimpleNamespace(
        tls_root_ca=cert_path,
        client_cert=cert_path,
        client_key=cert_path,
        evidence_path=evidence_path,
        graph_binding_atlas_path=json_path,
        out=tmp_path / "out",
    )

    with pytest.raises(ValueError, match="graph_binding_atlas_path_dir_not_found"):
        module._validate_paths(args)


def test_graph_binding_atlas_loader_rejects_missing_path(tmp_path):
    module = _load_script_module()

    with pytest.raises(ValueError, match="graph_binding_atlas_path_not_an_lmdb_directory"):
        module._load_graph_binding_atlas(tmp_path / "missing_lmdb")


def test_graph_binding_atlas_loader_rejects_empty_lmdb(tmp_path):
    module = _load_script_module()
    lmdb_path = tmp_path / "empty_lmdb"
    _write_minimal_nodes_only_lmdb(lmdb_path)
    env = lmdb.open(str(lmdb_path), max_dbs=4)
    try:
        with env.begin(write=True, db=env.open_db(b"nodes")) as txn:
            cursor = txn.cursor()
            for key, _ in list(cursor):
                txn.delete(key)
    finally:
        env.close()

    with pytest.raises(ValueError, match="graph_binding_atlas_lmdb_no_nodes_found"):
        module._load_graph_binding_atlas(lmdb_path)


def test_graph_binding_atlas_loader_does_not_create_missing_named_dbs(tmp_path):
    module = _load_script_module()
    lmdb_path = tmp_path / "nodes_only_lmdb"
    _write_minimal_nodes_only_lmdb(lmdb_path)
    before = {
        path.name: path.read_bytes()
        for path in sorted(lmdb_path.iterdir())
        if path.name in {"data.mdb", "lock.mdb"}
    }

    store = module._load_graph_binding_atlas(lmdb_path)
    try:
        assert load_from_atlas(store, AGENT_ID).validator_agent_id == AGENT_ID
        assert store.iter_edges() == []
    finally:
        store.close()

    after = {
        path.name: path.read_bytes()
        for path in sorted(lmdb_path.iterdir())
        if path.name in {"data.mdb", "lock.mdb"}
    }
    assert after == before


def test_graph_binding_supersession_preserved_through_lmdb_store(tmp_path):
    module = _load_script_module()
    lmdb_path = tmp_path / "assertions_lmdb"
    _write_assertion(
        lmdb_path,
        revised_by="replacement_candidate_id_or_any_non_empty_string",
    )

    store = module._load_graph_binding_atlas(lmdb_path)
    try:
        assertion = load_from_atlas(store, AGENT_ID)
        assert assertion_is_superseded(store, assertion) is True
    finally:
        store.close()
