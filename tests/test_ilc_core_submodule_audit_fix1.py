# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import os
import stat
import subprocess
import tarfile
import zipfile
from decimal import Decimal, localcontext

import lmdb
import pytest

from ilc_core.agent import EveAgent
from ilc_core.analysis.agent_descriptors import AgentDescriptor
from ilc_core.analysis.competency_kpis import (
    compute_agent_competency_kpis,
    summarize_competency_for_profile,
)
from ilc_core.analysis.fairness_metrics import apply_beta_theta_payouts
from ilc_core.analysis.laplacian_analytics import diagnose_zero_stake_hyperedge
from ilc_core.analysis.routed_tasks_export import export_routed_tasks_to_csv
from ilc_core.analysis.spectral_utils import compute_weight
from ilc_core.analysis.utility_flow_rewards import allocate_rewards_with_governor
from ilc_core.bundle.atlas_local_registry import (
    AtlasLocalRegistryError,
    _resolve_within_root,
)
from ilc_core.bundle.atlas_slice_manifest import (
    MAX_ATLAS_SLICE_MERKLE_ROWS,
    _content_entries_merkle_root,
)
from ilc_core.consensus.attribution_batch_bridge import (
    AttributionBatchBridgeError,
    _require_werner_pressure,
)
from ilc_core.consensus.circuit_breaker_interface import (
    summarize_circuit_breaker_quorum_state,
)
from ilc_core.crypto.cbor_canonical import validate_canonical_cbor_bytes
from ilc_core.crypto.cose_sign1 import cose_sign1_sign
from ilc_core.ccss.contact_gate import ContactGateError, _coerce_commitment
from ilc_core.ecu.ecu_fast_path_intent import ECUFastPathIntent, TransferClass, validate_intent
from ilc_core.ecu.ecu_transfer_adapter import validate_rust_transfer_payload
from ilc_core.encoding.cidv1 import cidv1_from_str, node_id_from_obj
from ilc_core.encoding.dag_cbor import decode_dag_cbor
from ilc_core.encoding.varint import decode_uvarint
from ilc_core.harness.co_attestation_receipt import build_co_attestation_receipt
from ilc_core.harness.local_immutable_store import LocalImmutableStore, build_local_ledger_entry
from ilc_core.harness.provider_usage_adapter import ProviderUsageAdapter
from ilc_core.ledger.canon_bundle_key_registry import KeyRegistry
from ilc_core.ledger.canon_bundle_key_registry_fetch import _extract_archive
from ilc_core.ledger.lmdb_backend import LmdbLedgerBackend, close_lmdb_env_cache
from ilc_core.mcp.service import _compute_digest
from ilc_core.mining.benchmark import PoWBenchmark
from ilc_core.protocol.event_export import (
    flatten_epoch_summary_event,
    flatten_task_outcome_event,
)
from ilc_core.protocol.ilc_cluster_a_conformance import _load_and_extract
from ilc_core.protocol.ilc_cluster_a_ingest import _get_sort_key, ingest_cluster_a_artifact
from ilc_core.protocol.public_wallet_runtime import _epoch_sort_key
from ilc_core.privacy.lane import PrivacyLane, PrivacyLaneConfig, _is_express_bypass
from ilc_core.privacy.metrics import LeakageMetricsCollector
from ilc_core.privacy.monitor import FillMonitor, make_degraded_notifications
from ilc_core.privacy.lane import ReleaseGroup
from ilc_core.reputation.temporal_decay_runtime import compute_decay_multiplier
from ilc_core.schema.d2_schema_baseline_runtime import generate_schema_catalog
from ilc_core.schema.verdict_record_schema import VerdictRecord
from ilc_core.server import _validate_peer_admin_host
from ilc_core.sim.devnet_experiments import _stable_float
from ilc_core.sim.harness_econ_scenarios import default_apply_econ
from ilc_core.sim.sim_fetch_01.sim_fetch_01_harness import _DeterministicRNG
from ilc_core.star_map.debruijn_harness import compute_bucket_histogram
from ilc_core.star_map.route_index import build_route_index_payload
from ilc_core.storage import lmdb_public_runtime
from ilc_core.storage.lmdb_graph_pruning_runtime import prune_lmdb_graph_tier_2_records
from ilc_core.storage.lmdb_public_runtime import LmdbPublicReceiptStore
from ilc_core.testing.phase_commit_manifest import _git_commit_exists
from ilc_core.testing.ratification_mutation_scope_guardrail import _split_markdown_row
from ilc_core.types import ClaimRecord, WeightParams, claim_record_to_node
from ilc_core.value_action.action_nonce_store import ActionNonceStore
from ilc_core.value_action.ilc_transfer_intent import AgentActionEnvelope, ActionType
from ilc_core.value_action.local_signing_provider import LocalEd25519SigningProvider
from ilc_core.work.task_queue import TaskDescriptor, TaskQueue

from cryptography.hazmat.primitives.asymmetric import ed25519


AGENT_A = "a" * 96
AGENT_B = "b" * 96


class _Governance:
    def get_task_fee_ecu(self, _task: str) -> Decimal:
        return Decimal("1")


class _Consensus:
    def __init__(self, *, accept: bool) -> None:
        self.accept = accept
        self.governance = _Governance()
        self.registered: list[tuple[str, Decimal]] = []
        self.contradictions: list[tuple[str, Decimal]] = []

    def register_stake(self, node_id: str, amount: Decimal) -> bool:
        self.registered.append((node_id, amount))
        return self.accept

    def process_contradiction(self, target_id: str, amount: Decimal) -> None:
        self.contradictions.append((target_id, amount))


class _Graph:
    def __init__(self) -> None:
        self.nodes: dict[str, object] = {}
        self.edges: list[tuple[str, str, str]] = []

    def add_node(self, node: object) -> None:
        self.nodes[getattr(node, "id")] = node

    def add_edge_by_ids(self, source: str, target: str, edge_type: str) -> None:
        self.edges.append((source, target, edge_type))


def _intent(*, amount: Decimal = Decimal("1")) -> ECUFastPathIntent:
    return ECUFastPathIntent(
        sender_agent_id=AGENT_A,
        recipient_agent_id=AGENT_B,
        amount_ecu=amount,
        transfer_class=TransferClass.PAYMENT,
        graph_context_anchor=None,
        express_consent=None,
        nonce="nonce-1",
        created_epoch=0,
    )


def test_archive_extraction_rejects_zip_symlink(tmp_path):
    archive = tmp_path / "bad.zip"
    info = zipfile.ZipInfo("bundle/link")
    info.external_attr = (stat.S_IFLNK | 0o777) << 16
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr(info, "target")

    assert _extract_archive(archive, tmp_path / "out") == {
        "ok": False,
        "error": "archive_unsafe_member_type",
    }


def test_archive_extraction_rejects_tar_symlink(tmp_path):
    archive = tmp_path / "bad.tar"
    with tarfile.open(archive, "w") as tf:
        member = tarfile.TarInfo("bundle/link")
        member.type = tarfile.SYMTYPE
        member.linkname = "target"
        tf.addfile(member)

    assert _extract_archive(archive, tmp_path / "out") == {
        "ok": False,
        "error": "archive_unsafe_member_type",
    }


def test_empty_key_registry_is_fail_closed_even_with_env(monkeypatch):
    monkeypatch.setenv("ILC_ALLOW_EMPTY_KEY_REGISTRY", "1")
    assert KeyRegistry().status("a" * 16) == "unknown"


def test_agent_consensus_rejection_does_not_mutate_graph_or_wallet():
    graph = _Graph()
    consensus = _Consensus(accept=False)
    agent = EveAgent(AGENT_A, graph, consensus)  # type: ignore[arg-type]
    agent.wallet_balance = Decimal("10")

    assert agent.mine_thought("claim", "parent", Decimal("1")) is None
    assert graph.nodes == {}
    assert graph.edges == []
    assert agent.wallet_balance == Decimal("10")


def test_negative_refutation_stake_rejected_before_balance_mutation():
    agent = EveAgent(AGENT_A, _Graph(), _Consensus(accept=True))  # type: ignore[arg-type]
    agent.wallet_balance = Decimal("10")
    with pytest.raises(ValueError, match="agent_refutation_stake_must_be_positive"):
        agent.refute_node("target", Decimal("-1"))
    assert agent.wallet_balance == Decimal("10")


def test_privacy_lane_caps_single_sender_and_rejects_spoofed_object_bypass():
    lane = PrivacyLane(PrivacyLaneConfig(k=20, max_pending_per_sender=1), current_epoch=0)
    assert lane.submit({"agent_id": "agent-1", "transfer_class": "Contribution"}, 0) is None
    with pytest.raises(ValueError, match="privacy_lane_sender_pending_cap_exceeded"):
        lane.submit({"agent_id": "agent-1", "transfer_class": "Contribution"}, 0)

    class Payment:
        express = type("Express", (), {"agent_acknowledged_timing_disclosure": True})()

    assert _is_express_bypass(Payment()) is False


def test_encoding_rejects_noncanonical_and_out_of_range_values():
    with pytest.raises(ValueError, match="Non-canonical uvarint"):
        decode_uvarint(b"\x81\x00")
    with pytest.raises(ValueError, match="Non-minimal CBOR"):
        decode_dag_cbor(b"\x18\x17")
    with pytest.raises(ValueError, match="signed_64bit"):
        decode_dag_cbor(b"\x1b\x80\x00\x00\x00\x00\x00\x00\x00")
    node_id = node_id_from_obj({"x": 1})
    with pytest.raises(ValueError, match="base32lower"):
        cidv1_from_str(node_id.upper())


def test_schema_verdict_and_temporal_decay_hardening():
    with pytest.raises(ValueError) as duplicate_field:
        generate_schema_catalog(
            [
                {
                    "schema_id": "x",
                    "fields": [
                        {"name": "a", "type": "string"},
                        {"name": "a", "type": "int"},
                    ],
                }
            ]
        )
    assert duplicate_field.value.token == "d2_schema_duplicate_field"
    payload = VerdictRecord(
        verdict_id="v",
        jury_panel_id="j",
        petition_node_id="p",
        verdict="approved",
        quorum_count=2,
        total_votes=3,
        approve_votes=2,
        reject_votes=1,
        abstain_votes=0,
        epoch_committed=0,
        ecus_at_stake=Decimal("1.2300"),
    ).canonical_payload()
    assert payload["ecus_at_stake"] == "1.23"

    with localcontext() as ctx:
        ctx.prec = 8
        low_precision = compute_decay_multiplier(
            elapsed_issuance_epochs="10",
            half_life_epochs="3",
            floor_multiplier="0.01",
        )
    with localcontext() as ctx:
        ctx.prec = 80
        high_precision = compute_decay_multiplier(
            elapsed_issuance_epochs="10",
            half_life_epochs="3",
            floor_multiplier="0.01",
        )
    assert low_precision == high_precision
    assert compute_decay_multiplier(
        elapsed_issuance_epochs="1000000000000",
        half_life_epochs="1",
        floor_multiplier="0.01",
    ) == Decimal("0.010000000000")


def test_ecu_intent_and_signature_validation():
    with pytest.raises(ValueError, match="invalid_amount_sub_micro_precision"):
        validate_intent(_intent(amount=Decimal("0.0000001")))
    payload = {
        "object_ref": {"agent": AGENT_A, "version": 0},
        "to": AGENT_B,
        "amount_micro_ecu": 1_000_000,
        "transfer_class": {"Payment": {"express": None}},
        "sender_sig": b"x",
    }
    with pytest.raises(ValueError, match="rust_ecu_transfer_sender_sig_invalid"):
        validate_rust_transfer_payload(payload, _intent())


def test_action_nonce_abandoned_issuance_can_be_reissued(tmp_path):
    env = lmdb.open(str(tmp_path / "nonce"), max_dbs=4)
    try:
        store = ActionNonceStore(env)
        first = store.next_nonce(AGENT_A)
        assert store.next_nonce(AGENT_A) == first
        store.consume_nonce(AGENT_A, first)
        assert store.next_nonce(AGENT_A).endswith("00000000000000000002")
    finally:
        env.close()


def test_local_signing_payload_omits_absent_optional_fields():
    env = AgentActionEnvelope(
        action_type=ActionType.ILC_TRANSFER,
        sender_agent_id=AGENT_A,
        recipient_agent_id=AGENT_B,
        amount_ilc=Decimal("1"),
        epoch=0,
        nonce=f"{AGENT_A}:nonce:00000000000000000001",
    )
    payload = LocalEd25519SigningProvider().canonical_payload_dict(env)
    assert "memo" not in payload
    assert "signed_at_epoch" not in payload
    assert "graph_context_anchor" not in payload


def test_task_queue_capacity_and_analysis_diagnostics(tmp_path):
    queue = TaskQueue(max_size=1)
    queue.add_task(TaskDescriptor(task_id="t1", task_type="claim.submit"))
    with pytest.raises(OverflowError, match="task_queue_capacity_exceeded"):
        queue.add_task(TaskDescriptor(task_id="t2", task_type="claim.submit"))

    csv_path = tmp_path / "empty.csv"
    export_routed_tasks_to_csv([], csv_path)
    assert csv_path.read_text(encoding="utf-8").strip() == "agent_id,task_id,task_type"
    assert AgentDescriptor(agent_id="a", total_tasks=0, problem_space_counts={"X": 0}).dominant_problem_space == "OTHER"
    assert diagnose_zero_stake_hyperedge([1.0, 0.0]) is True
    report = allocate_rewards_with_governor([])
    assert report["unallocated_budget"] == 100.0
    assert report["unallocated_budget_reason"] == "zero_eligible_utility_flow"


def test_competency_weighted_average_and_barrier_validation():
    rows = [
        {"agent_id": "a", "problem_space": "LOCAL_CONSISTENCY", "success": True, "barrier_level": "low"},
        {"agent_id": "a", "problem_space": "LOCAL_CONSISTENCY", "success": False, "barrier_level": "low"},
        {"agent_id": "a", "problem_space": "EPISTEMIC_SYNTHESIS", "success": True, "barrier_level": "high"},
    ]
    summary = summarize_competency_for_profile(compute_agent_competency_kpis(rows))
    assert summary["a"]["global"]["avg_success_rate"] == pytest.approx(2 / 3)
    with pytest.raises(ValueError, match="competency_barrier_level_invalid"):
        compute_agent_competency_kpis([{"agent_id": "a", "barrier_level": "extreme"}])


def test_misc_boundary_hardening(tmp_path):
    with pytest.raises(ValueError, match="theta_must_be_unit_interval"):
        apply_beta_theta_payouts({"a": 1.0}, {"a": 1.0}, beta=1.0, theta=1.1)
    assert apply_beta_theta_payouts({"a": 1.0}, {"a": 1.0}, beta=10.0, theta=1.0)["a"] == 1.0
    with pytest.raises(ValueError, match="heads must be an integer"):
        compute_bucket_histogram(["a", "b"], n=2, heads=True)
    assert build_route_index_payload([], [], 1, created_at=__import__("datetime").datetime(2026, 1, 1))[
        "created_at"
    ].endswith("Z")
    with pytest.raises(ValueError, match="claim_record_timestamp_invalid"):
        claim_record_to_node(
            ClaimRecord(
                id="c",
                type="claim",
                content="x",
                agent_id=AGENT_A,
                signature="sig",
                timestamp="not-a-date",
            )
        )
    with pytest.raises(ValueError, match="weight_reuse_count_invalid"):
        WeightParams(stake=Decimal("1"), reuse_count=-1, decay_rate="0", edge_type_coefficient="1")
    assert compute_weight(
        WeightParams(stake=Decimal("1"), reuse_count=0, decay_rate="0", edge_type_coefficient="1"),
        current_epoch=0,
    ) == 1.0


def test_crypto_boundaries_and_lmdb_cache(tmp_path):
    with pytest.raises(TypeError, match="CBOR data must be bytes"):
        validate_canonical_cbor_bytes("not-bytes")  # type: ignore[arg-type]
    key = ed25519.Ed25519PrivateKey.generate()
    payload = b"\xa1ax\x01"
    with pytest.raises(ValueError, match="COSE protected kid length invalid"):
        cose_sign1_sign(payload, key, kid=b"")

    root = tmp_path / "ledger"
    one = LmdbLedgerBackend(root)
    two = LmdbLedgerBackend(root)
    assert one.env is two.env
    close_lmdb_env_cache(root)


def test_consensus_and_privacy_exact_boundaries():
    summary = summarize_circuit_breaker_quorum_state(
        [
            {"validator_id": "v1", "cluster_id": "a", "vote_weight": 1, "circuit_breaker_requested": True},
            {"validator_id": "v2", "cluster_id": "b", "vote_weight": 1, "circuit_breaker_requested": True},
            {"validator_id": "v3", "cluster_id": "c", "vote_weight": 1, "circuit_breaker_requested": False},
        ]
    )
    assert summary["quorum_ok"] is True
    with pytest.raises(AttributionBatchBridgeError) as pressure_error:
        _require_werner_pressure("-0.1")
    assert pressure_error.value.token == "werner_raw_pressure_must_be_non_negative"

    monitor = FillMonitor(max_wait_epochs=1)
    monitor.record_force_release(0)
    assert monitor.fallback_active is True
    notifications = make_degraded_notifications(
        ReleaseGroup(
            release_epoch=1,
            transfers=[1, 2],
            agent_ids=["a", "a"],
            anonymity_set_size=1,
            degraded_anonymity=True,
        )
    )
    assert len(notifications) == 1
    collector = LeakageMetricsCollector()
    assert collector.check_bounds()["A"] is True


def test_mining_benchmark_has_no_genesis_bypass(monkeypatch):
    bench = PoWBenchmark(matrix_size=1)
    monkeypatch.setattr(bench, "_run_gpu_or_numpy_matrix", lambda *args, **kwargs: None)
    monkeypatch.setattr(bench, "_run_numpy_or_python_matrix", lambda *args, **kwargs: None)
    monkeypatch.setattr(bench, "_run_prime_search", lambda *args, **kwargs: None)
    result = bench.run("contains-genesis-substring")
    assert result["tier"] != "genesis"
    assert result["task"] == "FIXED_MATRIX_AND_INTEGER_SEARCH"


def test_local_dev_peer_admin_still_rejects_malformed_host():
    with pytest.raises(Exception) as excinfo:
        _validate_peer_admin_host("bad host", allow_private_literal=True)
    assert getattr(excinfo.value, "detail", "") == "peer_admin_unsafe_host_rejected_phase_1573ak"


def test_public_receipt_index_capacity_is_enforced(tmp_path, monkeypatch):
    monkeypatch.setattr(lmdb_public_runtime, "MAX_PUBLIC_RECEIPT_INDEX_IDS", 1)
    store = LmdbPublicReceiptStore(tmp_path / "receipts")
    try:
        store.put_receipt(
            "r1",
            {"signer_agent_id": AGENT_A, "artifact_kind": "x", "epoch_id": "epoch_0"},
        )
        with pytest.raises(ValueError, match="public_receipt_index_capacity_exceeded"):
            store.put_receipt(
                "r2",
                {"signer_agent_id": AGENT_A, "artifact_kind": "x", "epoch_id": "epoch_0"},
            )
    finally:
        store.close()


def test_graph_pruning_skips_invalid_records_instead_of_aborting(tmp_path):
    env = lmdb.open(str(tmp_path / "prune"), max_dbs=2, map_size=8 * 1024 * 1024)
    try:
        db = env.open_db(b"graph")
        with env.begin(write=True, db=db) as txn:
            txn.put(b"bad", b"{not-json")
        result = prune_lmdb_graph_tier_2_records(
            env,
            db,
            current_issuance_epoch=10,
            minting_confirmed=True,
            dry_run=True,
        )
        assert result["skipped_invalid_records"] == 1
        assert result["retained"] == 1
    finally:
        env.close()


def test_protocol_flatteners_preserve_empty_payload_and_zero_strings():
    task = flatten_task_outcome_event({"payload": {}})
    epoch = flatten_epoch_summary_event({"payload": {}})
    assert task["stake_spent"] == "0"
    assert task["reward_paid"] == "0"
    assert epoch["total_ecu_spent"] == "0"
    assert epoch["total_reward_paid"] == "0"
    assert epoch["clearing_price_ilc_per_ecu"] == "0"


def test_cluster_a_conformance_and_ingest_reject_bad_root_and_signature_rows():
    obj, binding, errors = _load_and_extract(["not", "a", "dict"])
    assert obj == {}
    assert binding == {}
    assert errors == ["schema_violation:invalid_type:root"]
    result = ingest_cluster_a_artifact({"gov_record_id": "g", "signatures": ["bad"]})
    assert "schema_violation:invalid_type:signature" in result["errors"]
    assert _get_sort_key({"timestamp": 7, "event_kind": 1, "event_id": 2}) == ("7", "1", "2")


def test_epoch_sort_key_orders_numeric_epochs_numerically():
    values = ["epoch_10", "epoch_2", "epoch_1", "alpha"]
    assert sorted(values, key=_epoch_sort_key) == ["epoch_1", "epoch_2", "epoch_10", "alpha"]


def test_bundle_boundaries_reject_absolute_paths_and_oversized_merkle_inputs(tmp_path):
    with pytest.raises(AtlasLocalRegistryError, match="absolute_forbidden"):
        _resolve_within_root(root=tmp_path, local_path=str(tmp_path / "inside"), token_prefix="local_path")
    with pytest.raises(ValueError, match="atlas_slice_manifest_merkle_row_cap_exceeded"):
        _content_entries_merkle_root(
            [
                {"node_id": f"n-{idx}", "record_sha256": "a" * 64}
                for idx in range(MAX_ATLAS_SLICE_MERKLE_ROWS + 1)
            ]
        )


def test_manifest_merkle_root_binds_node_id_to_record_hash():
    left = _content_entries_merkle_root(
        [
            {"node_id": "node-a", "record_sha256": "a" * 64},
            {"node_id": "node-b", "record_sha256": "b" * 64},
        ]
    )
    swapped = _content_entries_merkle_root(
        [
            {"node_id": "node-a", "record_sha256": "b" * 64},
            {"node_id": "node-b", "record_sha256": "a" * 64},
        ]
    )
    assert left != swapped


def test_testing_helpers_fail_closed_on_missing_git_and_escaped_markdown_pipe(monkeypatch):
    def raise_missing(*_args, **_kwargs):
        raise FileNotFoundError("git")

    monkeypatch.setattr(subprocess, "run", raise_missing)
    assert _git_commit_exists("deadbeef") is False
    assert _split_markdown_row(r"| CDL-1 | topic with \| escaped pipe | open |") == [
        "CDL-1",
        "topic with | escaped pipe",
        "open",
    ]


def test_ccss_harness_mcp_and_sim_boundary_fixes(tmp_path):
    with pytest.raises(ContactGateError, match="invalid_hex"):
        _coerce_commitment("0xnot-hex", field="capability")
    with pytest.raises(ValueError, match="co_attestation_invalid_signature"):
        build_co_attestation_receipt(
            receipt_id="r",
            artifact_sha256="a" * 64,
            attestation_signatures=["not-a-mapping"],  # type: ignore[list-item]
        )
    entry = build_local_ledger_entry(
        artifact_sha256="b" * 64,
        consent_gate_decision_id="consent-1",
        committed_at_epoch=0,
    )
    store = LocalImmutableStore(tmp_path / "store")
    store.write(entry)
    assert stat.S_IMODE((tmp_path / "store" / f"{entry.entry_id}.json").stat().st_mode) == 0o600

    usage = ProviderUsageAdapter()
    usage.record_usage(provider_id="p", input_tokens=1, output_tokens=1, cost_proxy="0", quota_headers={"x-ratelimit-remaining-tokens": "9"})
    usage.record_usage(provider_id="p", input_tokens=1, output_tokens=1, cost_proxy="0", quota_headers={"x-ratelimit-remaining-tokens": "11"})
    assert usage.snapshot("p").remaining_tokens == 11
    assert len(_compute_digest(set())) == 64
    assert _stable_float(1 / 3) == 0.333333333333
    assert default_apply_econ({}).__class__.__name__ == "ProtocolParams"
    rng_one = _DeterministicRNG(123)
    rng_two = _DeterministicRNG(123)
    assert rng_one.sample(range(100), 5) == rng_two.sample(range(100), 5)
