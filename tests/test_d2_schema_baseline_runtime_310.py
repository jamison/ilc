"""Phase-310 runtime tests for D2 schema baseline implementation tranche."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from ilc_core.schema import (
    D2SchemaValidationError,
    SCHEMA_BASELINE_VERSION,
    canonical_schema_vectors,
    generate_schema_catalog,
    verify_schema_catalog,
)


CLI_CMD = [sys.executable, "-m", "ilc_core.cli.main"]
DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
PHASE_310_COMMIT_SUBJECT = "feat(g8): phase 310 d2 schema baseline initial implementation tranche"


def _payload(result: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    blob = result.stdout.strip() or result.stderr.strip()
    assert blob, "expected_json_payload"
    return json.loads(blob)


def _run_cli(args: list[str], env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(CLI_CMD + args, capture_output=True, text=True, env=env, check=False)


def _write_graph_state(path: Path) -> None:
    state = {
        "schema_version": "d2e03.v0.1",
        "nodes": [{"id": "node-1", "claim_id": "claim-a", "payload": {"text": "alpha"}}],
        "edges": [],
        "epochs": [{"epoch": 9}],
    }
    path.write_text(json.dumps(state, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _write_bundle_state(path: Path) -> None:
    manifest = {"bundle_version": "v1", "entries": [{"cid": "node-1", "kind": "knowledge_node"}]}
    stable = json.dumps(manifest, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(stable.encode("utf-8")).hexdigest()
    state = {
        "schema_version": "d2e07.v0.1",
        "bundles": [
            {
                "bundle_cid": "bafy-bundle-1",
                "provider": "local",
                "manifest": manifest,
                "integrity": {"manifest_sha256": digest},
                "graph_refs": {"node_ids": ["node-1"], "claim_ids": ["claim-a"]},
            }
        ],
    }
    path.write_text(json.dumps(state, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _resolve_phase_310_commit_ref() -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if subject.strip() == PHASE_310_COMMIT_SUBJECT:
            return commit_hash
    pytest.skip("phase_310_commit_not_present_in_local_history")


def test_runtime_surface_is_invocable() -> None:
    vectors = canonical_schema_vectors()
    catalog = generate_schema_catalog(vectors)
    verified = verify_schema_catalog(catalog)

    assert catalog["catalog_version"] == SCHEMA_BASELINE_VERSION
    assert isinstance(catalog["catalog_sha256"], str)
    assert len(catalog["entries"]) == 2
    assert verified["valid"] is True
    assert verified["catalog_version"] == SCHEMA_BASELINE_VERSION


def test_deterministic_output_for_repeated_identical_input_vectors() -> None:
    vectors = canonical_schema_vectors()
    one = generate_schema_catalog(vectors)
    two = generate_schema_catalog(vectors)
    assert one == two
    assert verify_schema_catalog(one) == verify_schema_catalog(two)


@pytest.mark.parametrize(
    ("entries", "token"),
    [
        ([{"schema_id": "d2.bad.v1", "fields": "not-a-list"}], "d2_schema_fields_not_list"),
        ([{"schema_id": "", "fields": [{"name": "x", "type": "string"}]}], "d2_schema_missing_schema_id"),
        (
            [
                {
                    "schema_id": "d2.bad.v2",
                    "fields": [{"name": "x", "type": "unknown"}],
                }
            ],
            "d2_schema_invalid_field_type",
        ),
    ],
)
def test_invalid_schema_inputs_fail_with_deterministic_tokens(entries: list[dict[str, Any]], token: str) -> None:
    with pytest.raises(D2SchemaValidationError) as exc:
        generate_schema_catalog(entries)
    assert exc.value.token == token

    with pytest.raises(D2SchemaValidationError) as exc_repeat:
        generate_schema_catalog(entries)
    assert exc_repeat.value.token == token


def test_canonical_test_vectors_validate_generator_and_verifier_surface() -> None:
    vectors = canonical_schema_vectors()
    catalog = generate_schema_catalog(vectors)
    verified = verify_schema_catalog(catalog)

    assert verified["entry_count"] == len(vectors)
    assert verified["catalog_sha256"] == catalog["catalog_sha256"]
    checks = verified["checks"]
    assert [item["check_type"] for item in checks] == [
        "catalog_version_supported",
        "catalog_entries_canonical",
        "catalog_digest_matches",
    ]
    assert all(item["passed"] is True for item in checks)


def test_runtime_integration_does_not_regress_query_verify_bundle_or_identity_envelopes(tmp_path: Path) -> None:
    graph_path = tmp_path / "graph.json"
    bundle_path = tmp_path / "bundle.json"
    identity_path = tmp_path / "identity.json"
    _write_graph_state(graph_path)
    _write_bundle_state(bundle_path)

    env = os.environ.copy()
    env["ILC_CLI_GRAPH_STATE_PATH"] = str(graph_path)
    env["ILC_BUNDLE_STATE_PATH"] = str(bundle_path)
    env["ILC_IDENTITY_STATE_PATH"] = str(identity_path)

    query = _run_cli(["query", "node", "--node-id", "node-1"], env)
    assert query.returncode == 0
    query_payload = _payload(query)
    assert query_payload["meta"]["schema_version"] == "299.v0.1"

    verify = _run_cli(["verify", "claim", "--claim-id", "claim-a"], env)
    assert verify.returncode == 0
    verify_payload = _payload(verify)
    assert verify_payload["meta"]["schema_version"] == "301.v0.1"

    bundle = _run_cli(["bundle", "inspect", "--bundle-cid", "bafy-bundle-1"], env)
    assert bundle.returncode == 0
    bundle_payload = _payload(bundle)
    assert bundle_payload["meta"]["schema_version"] == "303.v0.1"

    identity = _run_cli(["identity", "init"], env)
    assert identity.returncode == 0
    identity_payload = _payload(identity)
    assert identity_payload["schema_version"] == "254.v0.1"
    assert "meta" not in identity_payload


def test_no_decision_log_mutation_in_phase_commit() -> None:
    commit_ref = _resolve_phase_310_commit_ref()
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    changed = {line.strip() for line in result.stdout.splitlines() if line.strip()}
    assert DECISION_LOG_PATH not in changed


def test_commit_anchored_runtime_mutation_scope_is_limited() -> None:
    commit_ref = _resolve_phase_310_commit_ref()
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    changed = {line.strip() for line in result.stdout.splitlines() if line.strip()}

    runtime_changes = [path for path in changed if path.startswith("ilc_core/")]
    disallowed_runtime_changes = [
        path
        for path in runtime_changes
        if not (path.startswith("ilc_core/schema/") or path == "ilc_core/cli/main.py")
    ]
    assert not disallowed_runtime_changes, f"phase_310_runtime_scope_violation:{disallowed_runtime_changes}"

    forbidden_prefixes = (
        "ilc_core/consensus/",
        "ilc_core/security/",
        "ilc_core/ledger/",
        "ilc_core/network/",
    )
    forbidden_mutations = [path for path in changed if path.startswith(forbidden_prefixes)]
    assert not forbidden_mutations, f"phase_310_forbidden_runtime_mutations:{forbidden_mutations}"
