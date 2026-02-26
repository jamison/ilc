"""Phase-314 runtime tests for epoch snapshot implementation tranche."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from ilc_core.epoch import (
    EPOCH_SNAPSHOT_RUNTIME_VERSION,
    GENESIS_BUNDLE_DEPENDENCY,
    SCHEMA_BASELINE_DEPENDENCY,
    EpochSnapshotValidationError,
    canonical_epoch_snapshot_vectors,
    generate_epoch_snapshot,
    verify_epoch_snapshot,
)


CLI_CMD = [sys.executable, "-m", "ilc_core.cli.main"]
DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
PHASE_314_COMMIT_SUBJECT = "feat(g8): phase 314 epoch snapshot initial implementation tranche"


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


def _resolve_phase_314_commit_ref() -> str:
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
        if subject.strip() == PHASE_314_COMMIT_SUBJECT:
            return commit_hash
    raise AssertionError("phase_314_commit_not_present_in_local_history")


def test_runtime_surface_is_invocable() -> None:
    vectors = canonical_epoch_snapshot_vectors()
    snapshot = generate_epoch_snapshot(vectors[0])
    verified = verify_epoch_snapshot(snapshot)

    assert snapshot["runtime_version"] == EPOCH_SNAPSHOT_RUNTIME_VERSION
    assert snapshot["schema_dependency"] == SCHEMA_BASELINE_DEPENDENCY
    assert snapshot["genesis_dependency"] == GENESIS_BUNDLE_DEPENDENCY
    assert isinstance(snapshot["snapshot_sha256"], str)

    assert verified["valid"] is True
    assert verified["runtime_version"] == EPOCH_SNAPSHOT_RUNTIME_VERSION
    assert verified["schema_dependency"] == SCHEMA_BASELINE_DEPENDENCY
    assert verified["genesis_dependency"] == GENESIS_BUNDLE_DEPENDENCY


def test_deterministic_output_for_repeated_identical_input_vectors() -> None:
    vector = canonical_epoch_snapshot_vectors()[0]
    one = generate_epoch_snapshot(vector)
    two = generate_epoch_snapshot(vector)

    assert one == two
    assert verify_epoch_snapshot(one) == verify_epoch_snapshot(two)


def test_invalid_snapshot_inputs_fail_with_deterministic_error_tokens() -> None:
    invalid = {
        "snapshot": {
            "snapshot_id": "snapshot-mainnet-100",
            "network": "mainnet",
            "epoch": 100,
            "retained_epochs": [],
            "checkpoint_refs": [{"kind": "state_root", "ref": "state-root-100"}],
        },
        "bootstrap": {
            "start_epoch": 98,
            "target_epoch": 100,
            "required_artifacts": ["genesis_bundle", "snapshot_chain"],
        },
        "retention": {
            "keep_last_n_epochs": 3,
            "minimum_epoch": 98,
        },
    }

    try:
        generate_epoch_snapshot(invalid)
        raise AssertionError("expected_epoch_snapshot_validation_error")
    except EpochSnapshotValidationError as exc:
        assert exc.token == "epoch_snapshot_retained_epochs_empty"

    try:
        generate_epoch_snapshot(invalid)
        raise AssertionError("expected_epoch_snapshot_validation_error_repeat")
    except EpochSnapshotValidationError as exc_repeat:
        assert exc_repeat.token == "epoch_snapshot_retained_epochs_empty"


def test_invalid_bootstrap_or_retention_inputs_fail_with_deterministic_error_tokens() -> None:
    vector = canonical_epoch_snapshot_vectors()[0]
    invalid_bootstrap = {
        "snapshot": vector["snapshot"],
        "bootstrap": {
            "start_epoch": 101,
            "target_epoch": 100,
            "required_artifacts": ["genesis_bundle", "snapshot_chain"],
        },
        "retention": vector["retention"],
    }

    try:
        generate_epoch_snapshot(invalid_bootstrap)
        raise AssertionError("expected_epoch_snapshot_bootstrap_validation_error")
    except EpochSnapshotValidationError as exc:
        assert exc.token == "epoch_snapshot_bootstrap_epoch_range_invalid"

    invalid_retention = {
        "snapshot": vector["snapshot"],
        "bootstrap": vector["bootstrap"],
        "retention": {
            "keep_last_n_epochs": 3,
            "minimum_epoch": 0,
        },
    }

    try:
        generate_epoch_snapshot(invalid_retention)
        raise AssertionError("expected_epoch_snapshot_retention_validation_error")
    except EpochSnapshotValidationError as exc:
        assert exc.token == "epoch_snapshot_retention_window_invalid"


def test_canonical_test_vectors_validate_generator_and_verifier_surface() -> None:
    vectors = canonical_epoch_snapshot_vectors()
    assert len(vectors) == 2

    for vector in vectors:
        snapshot = generate_epoch_snapshot(vector)
        verified = verify_epoch_snapshot(snapshot)
        assert verified["valid"] is True
        checks = verified["checks"]
        assert [item["check_type"] for item in checks] == [
            "runtime_version_supported",
            "schema_dependency_locked",
            "genesis_dependency_locked",
            "bootstrap_window_valid",
            "retention_policy_valid",
            "snapshot_digest_matches",
        ]
        assert all(item["passed"] is True for item in checks)


def test_runtime_constants_lock_exact_dependency_and_version_tokens() -> None:
    assert EPOCH_SNAPSHOT_RUNTIME_VERSION == "epoch_snapshot_runtime_314.v0.1"
    assert SCHEMA_BASELINE_DEPENDENCY == "d2_schema_baseline_310.v0.1"
    assert GENESIS_BUNDLE_DEPENDENCY == "genesis_state_bundle_312.v0.1"


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
    commit_ref = _resolve_phase_314_commit_ref()
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    changed = {line.strip() for line in result.stdout.splitlines() if line.strip()}
    assert DECISION_LOG_PATH not in changed


def test_commit_anchored_runtime_mutation_scope_is_limited() -> None:
    commit_ref = _resolve_phase_314_commit_ref()
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
        if not (path.startswith("ilc_core/epoch/") or path == "ilc_core/cli/main.py")
    ]
    assert not disallowed_runtime_changes, f"phase_314_runtime_scope_violation:{disallowed_runtime_changes}"

    forbidden_prefixes = (
        "ilc_core/consensus/",
        "ilc_core/security/",
        "ilc_core/ledger/",
        "ilc_core/network/",
        "ilc_core/schema/",
        "ilc_core/genesis/",
    )
    forbidden_mutations = [path for path in changed if path.startswith(forbidden_prefixes)]
    assert not forbidden_mutations, f"phase_314_forbidden_runtime_mutations:{forbidden_mutations}"
