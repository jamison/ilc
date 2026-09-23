from __future__ import annotations

import ast
import json
from decimal import Decimal
from pathlib import Path

import pytest

from ilc_core.epoch.ecu_accrual_evidence import (
    EMPTY_ATTRIBUTION_RECEIPT_STATE_ROOT_SHA256,
    UNBOUND_ECU_ACCRUAL_RUNTIME_STATE_ROOT_SHA256,
    EcuAccrualEvidence,
    build_ecu_accrual_evidence,
    is_replay_safe,
    read_ecu_accrual_evidence,
    write_ecu_accrual_evidence,
)
from ilc_core.epoch.ecu_attribution_receipt_store import (
    AttributionOriginAccrualRuntime,
    compute_attribution_receipt_state_root_sha256,
    list_agents_with_attribution_receipts,
    record_attribution_ingest_report,
    record_attribution_origin_receipt,
)
from ilc_core.ledger.ecu_active_layer_runtime import EcuActiveLayerRuntime


AGENT_A = "a" * 96
AGENT_B = "b" * 96
AGENT_C = "c" * 96
AGENT_D = "d" * 96


def _store(tmp_path: Path) -> Path:
    return tmp_path / "attribution_receipts.lmdb"


def _report(
    *balances: dict[str, object],
    epoch: int = 7,
    total_micro_ecu: int | None = None,
    attribution_count: int | None = None,
) -> dict[str, object]:
    return {
        "attribution_count": len(balances) if attribution_count is None else attribution_count,
        "balances": list(balances),
        "dry_run": False,
        "epoch": epoch,
        "input_sha256": "1" * 64,
        "marker": "attribution_batch_ingest_ok",
        "total_micro_ecu": (
            sum(int(item["amount_micro_ecu"]) for item in balances)
            if total_micro_ecu is None
            else total_micro_ecu
        ),
    }


def _batch(*attributions: dict[str, object], epoch: int = 7) -> dict[str, object]:
    return {
        "attribution_count": len(attributions),
        "attributions": [
            {
                "agent_id_hex": item["agent_id_hex"],
                "amount_micro_ecu": item["amount_micro_ecu"],
            }
            for item in attributions
        ],
        "epoch": epoch,
        "marker": "attribution_batch_bridge_ok",
        "total_micro_ecu": sum(int(item["amount_micro_ecu"]) for item in attributions),
    }


def _balance(agent_id: str, micro_ecu: int, *, epoch: int = 7) -> dict[str, object]:
    return {
        "agent_id_hex": agent_id,
        "amount_micro_ecu": micro_ecu,
        "epoch": epoch,
        "version": 0,
    }


def test_list_agents_empty_store(tmp_path: Path) -> None:
    assert list_agents_with_attribution_receipts(_store(tmp_path)) == []


def test_list_agents_after_attribution_batch(tmp_path: Path) -> None:
    record_attribution_ingest_report(
        _store(tmp_path),
        _report(
            _balance(AGENT_C, 1),
            _balance(AGENT_A, 2),
            _balance(AGENT_B, 3),
        ),
        batch_payload=_batch(
            _balance(AGENT_C, 1),
            _balance(AGENT_A, 2),
            _balance(AGENT_B, 3),
        ),
    )

    assert list_agents_with_attribution_receipts(_store(tmp_path)) == [
        AGENT_A,
        AGENT_B,
        AGENT_C,
    ]


def test_get_accrued_ecu_zero_for_unknown_agent(tmp_path: Path) -> None:
    runtime = AttributionOriginAccrualRuntime(_store(tmp_path))

    assert runtime.get_accrued_ecu(AGENT_A) == "0"


def test_get_accrued_ecu_exact_payout(tmp_path: Path) -> None:
    record_attribution_ingest_report(
        _store(tmp_path),
        _report(_balance(AGENT_A, 200000)),
        batch_payload=_batch(_balance(AGENT_A, 200000)),
    )
    runtime = AttributionOriginAccrualRuntime(_store(tmp_path))

    assert runtime.get_accrued_ecu(AGENT_A) == "0.2"


def test_get_accrued_ecu_accumulates_across_batches(tmp_path: Path) -> None:
    store = _store(tmp_path)
    record_attribution_ingest_report(
        store,
        _report(_balance(AGENT_A, 200000, epoch=1), epoch=1),
        batch_payload=_batch(_balance(AGENT_A, 200000), epoch=1),
    )
    record_attribution_ingest_report(
        store,
        _report(_balance(AGENT_A, 300000, epoch=2), epoch=2),
        batch_payload=_batch(_balance(AGENT_A, 300000), epoch=2),
    )
    runtime = AttributionOriginAccrualRuntime(store)

    assert runtime.get_accrued_ecu(AGENT_A) == "0.5"


def test_ingest_report_records_batch_delta_not_cumulative_balance(tmp_path: Path) -> None:
    store = _store(tmp_path)
    record_attribution_ingest_report(
        store,
        _report(_balance(AGENT_A, 200000, epoch=1), epoch=1),
        batch_payload=_batch(_balance(AGENT_A, 200000), epoch=1),
    )
    record_attribution_ingest_report(
        store,
        _report(
            _balance(AGENT_A, 500000, epoch=2),
            epoch=2,
            total_micro_ecu=300000,
            attribution_count=1,
        ),
        batch_payload=_batch(_balance(AGENT_A, 300000), epoch=2),
    )

    assert AttributionOriginAccrualRuntime(store).get_accrued_ecu(AGENT_A) == "0.5"


def test_ingest_report_requires_source_batch_payload(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="attribution_batch_payload_required"):
        record_attribution_ingest_report(
            _store(tmp_path),
            _report(_balance(AGENT_A, 200000)),
        )


def test_ingest_report_total_must_match_batch_delta(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="attribution_ingest_report_total_mismatch"):
        record_attribution_ingest_report(
            _store(tmp_path),
            _report(_balance(AGENT_A, 500000), total_micro_ecu=500000),
            batch_payload=_batch(_balance(AGENT_A, 300000)),
        )


def test_build_evidence_auto_enumerates_agents(tmp_path: Path) -> None:
    store = _store(tmp_path)
    record_attribution_ingest_report(
        store,
        _report(_balance(AGENT_A, 200000), _balance(AGENT_B, 300000)),
        batch_payload=_batch(_balance(AGENT_A, 200000), _balance(AGENT_B, 300000)),
    )

    evidence = build_ecu_accrual_evidence(
        AttributionOriginAccrualRuntime(store),
        issuance_interval_id=0,
        accrual_close_validation_epoch=40320,
    )

    assert evidence.agent_ecu_weights == {AGENT_A: "0.2", AGENT_B: "0.3"}
    assert evidence.lmdb_state_root_sha256 == compute_attribution_receipt_state_root_sha256(
        store
    )


def test_build_evidence_explicit_agents_respected(tmp_path: Path) -> None:
    store = _store(tmp_path)
    record_attribution_ingest_report(
        store,
        _report(_balance(AGENT_A, 200000), _balance(AGENT_B, 300000)),
        batch_payload=_batch(_balance(AGENT_A, 200000), _balance(AGENT_B, 300000)),
    )

    evidence = build_ecu_accrual_evidence(
        AttributionOriginAccrualRuntime(store),
        issuance_interval_id=0,
        accrual_close_validation_epoch=40320,
        agent_ids=[AGENT_B],
    )

    assert evidence.agent_ecu_weights == {AGENT_B: "0.3"}


def test_build_evidence_explicit_agents_filters_zero_weights(tmp_path: Path) -> None:
    store = _store(tmp_path)
    record_attribution_origin_receipt(
        store,
        agent_id=AGENT_B,
        amount_ecu="0.3",
        epoch=7,
        receipt_ref="phase-test",
    )

    evidence = build_ecu_accrual_evidence(
        AttributionOriginAccrualRuntime(store),
        issuance_interval_id=0,
        accrual_close_validation_epoch=40320,
        agent_ids=[AGENT_A, AGENT_B],
    )

    assert evidence.agent_ecu_weights == {AGENT_B: "0.3"}


def test_evidence_agent_weights_are_immutable() -> None:
    evidence = EcuAccrualEvidence(
        issuance_interval_id=0,
        agent_ecu_weights={AGENT_A: "1"},
        accrual_close_validation_epoch=40320,
    )

    with pytest.raises(TypeError):
        evidence.agent_ecu_weights[AGENT_B] = "2"  # type: ignore[index]


def test_lmdb_state_root_sha256_present(tmp_path: Path) -> None:
    store = _store(tmp_path)
    record_attribution_origin_receipt(
        store,
        agent_id=AGENT_A,
        amount_ecu="1.25",
        epoch=5,
        receipt_ref="phase-test",
    )

    evidence = build_ecu_accrual_evidence(
        AttributionOriginAccrualRuntime(store),
        issuance_interval_id=0,
        accrual_close_validation_epoch=40320,
    )

    assert len(evidence.lmdb_state_root_sha256) == 64
    int(evidence.lmdb_state_root_sha256, 16)
    assert evidence.lmdb_state_root_sha256 != EMPTY_ATTRIBUTION_RECEIPT_STATE_ROOT_SHA256


def test_lmdb_state_root_sha256_deterministic(tmp_path: Path) -> None:
    store = _store(tmp_path)
    record_attribution_origin_receipt(
        store,
        agent_id=AGENT_A,
        amount_ecu="1.25",
        epoch=5,
        receipt_ref="phase-test",
    )

    assert compute_attribution_receipt_state_root_sha256(
        store
    ) == compute_attribution_receipt_state_root_sha256(store)


def test_lmdb_state_root_sha256_changes_after_new_batch(tmp_path: Path) -> None:
    store = _store(tmp_path)
    before = compute_attribution_receipt_state_root_sha256(store)
    record_attribution_origin_receipt(
        store,
        agent_id=AGENT_A,
        amount_ecu="1.25",
        epoch=5,
        receipt_ref="phase-test",
    )

    assert compute_attribution_receipt_state_root_sha256(store) != before


def test_attribution_origin_not_from_rust_aggregate(tmp_path: Path) -> None:
    store = _store(tmp_path)
    aggregate_runtime = EcuActiveLayerRuntime()
    aggregate_runtime.set_accrued_ecu(AGENT_A, "99")
    attribution_runtime = AttributionOriginAccrualRuntime(store)

    assert aggregate_runtime.get_accrued_ecu(AGENT_A) == "99"
    assert attribution_runtime.get_accrued_ecu(AGENT_A) == "0"


def test_contribution_transfer_excluded_by_default(tmp_path: Path) -> None:
    store = _store(tmp_path)
    transfer_aggregate_runtime = EcuActiveLayerRuntime()
    transfer_aggregate_runtime.set_accrued_ecu(AGENT_D, "100")

    evidence = build_ecu_accrual_evidence(
        AttributionOriginAccrualRuntime(store),
        issuance_interval_id=0,
        accrual_close_validation_epoch=40320,
    )

    assert transfer_aggregate_runtime.get_accrued_ecu(AGENT_D) == "100"
    assert AGENT_D not in evidence.agent_ecu_weights


def test_zero_weight_agent_excluded_from_eligible_agents(tmp_path: Path) -> None:
    store = _store(tmp_path)
    record_attribution_ingest_report(
        store,
        _report(_balance(AGENT_A, 0), _balance(AGENT_B, 1)),
        batch_payload=_batch(_balance(AGENT_A, 0), _balance(AGENT_B, 1)),
    )

    assert list_agents_with_attribution_receipts(store) == [AGENT_B]


def test_float_ban_enforced(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="attribution_receipt_amount_must_be_exact_decimal"):
        record_attribution_origin_receipt(
            _store(tmp_path),
            agent_id=AGENT_A,
            amount_ecu=1.25,  # type: ignore[arg-type]
            epoch=1,
            receipt_ref="float-test",
        )


def test_int_amount_ban_enforced(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="attribution_receipt_amount_must_be_exact_decimal"):
        record_attribution_origin_receipt(
            _store(tmp_path),
            agent_id=AGENT_A,
            amount_ecu=1,  # type: ignore[arg-type]
            epoch=1,
            receipt_ref="int-test",
        )


def test_decimal_canonical_form_enforced_symmetrically(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="attribution_receipt_amount_must_be_canonical_decimal"):
        record_attribution_origin_receipt(
            _store(tmp_path),
            agent_id=AGENT_A,
            amount_ecu=Decimal("1.50"),
            epoch=1,
            receipt_ref="decimal-scale-test",
        )


@pytest.mark.parametrize("amount", [Decimal("NaN"), Decimal("Infinity")])
def test_non_finite_decimal_rejected(tmp_path: Path, amount: Decimal) -> None:
    with pytest.raises(ValueError, match="attribution_receipt_amount_must_be_non_negative_decimal"):
        record_attribution_origin_receipt(
            _store(tmp_path),
            agent_id=AGENT_A,
            amount_ecu=amount,
            epoch=1,
            receipt_ref="non-finite-test",
        )


def test_build_evidence_without_agents_requires_enumerator() -> None:
    runtime = EcuActiveLayerRuntime()

    with pytest.raises(ValueError, match="ecu_accrual_agent_ids_required_without_enumerator"):
        build_ecu_accrual_evidence(
            runtime,
            issuance_interval_id=0,
            accrual_close_validation_epoch=40320,
        )


def test_runtime_without_state_root_uses_unbound_root_not_empty_store_root() -> None:
    runtime = EcuActiveLayerRuntime()
    runtime.set_accrued_ecu(AGENT_A, "1")

    evidence = build_ecu_accrual_evidence(
        runtime,
        issuance_interval_id=0,
        accrual_close_validation_epoch=40320,
        agent_ids=[AGENT_A],
    )

    assert evidence.lmdb_state_root_sha256 == UNBOUND_ECU_ACCRUAL_RUNTIME_STATE_ROOT_SHA256
    assert evidence.lmdb_state_root_sha256 != EMPTY_ATTRIBUTION_RECEIPT_STATE_ROOT_SHA256


def test_evidence_write_read_roundtrip(tmp_path: Path) -> None:
    evidence = EcuAccrualEvidence(
        issuance_interval_id=0,
        agent_ecu_weights={AGENT_A: "1"},
        accrual_close_validation_epoch=40320,
        lmdb_state_root_sha256="2" * 64,
    )
    target = tmp_path / "evidence.json"

    write_ecu_accrual_evidence(evidence, target)
    readback = read_ecu_accrual_evidence(target)

    assert readback.to_canonical_record() == evidence.to_canonical_record()


def test_evidence_read_rejects_tampered_hash(tmp_path: Path) -> None:
    evidence = EcuAccrualEvidence(
        issuance_interval_id=0,
        agent_ecu_weights={AGENT_A: "1"},
        accrual_close_validation_epoch=40320,
        lmdb_state_root_sha256="2" * 64,
    )
    target = tmp_path / "evidence.json"
    write_ecu_accrual_evidence(evidence, target)
    payload = read_ecu_accrual_evidence(target).to_canonical_record()
    payload["lmdb_state_root_sha256"] = "3" * 64
    target.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="ecu_accrual_evidence_sha256_mismatch"):
        read_ecu_accrual_evidence(target)


def test_evidence_read_rejects_invalid_utf8(tmp_path: Path) -> None:
    target = tmp_path / "evidence.json"
    target.write_bytes(b"\xff")

    with pytest.raises(ValueError, match="ecu_accrual_evidence_json_invalid"):
        read_ecu_accrual_evidence(target)


def test_is_replay_safe_checks_interval_and_close_epoch() -> None:
    evidence = EcuAccrualEvidence(
        issuance_interval_id=3,
        agent_ecu_weights={AGENT_A: "1"},
        accrual_close_validation_epoch=40320,
    )

    assert is_replay_safe(
        evidence,
        issuance_interval_id=3,
        accrual_close_validation_epoch=40320,
    )
    assert not is_replay_safe(
        evidence,
        issuance_interval_id=4,
        accrual_close_validation_epoch=40320,
    )
    assert not is_replay_safe(
        evidence,
        issuance_interval_id=3,
        accrual_close_validation_epoch=40321,
    )


def test_evidence_hash_binds_state_root() -> None:
    evidence = EcuAccrualEvidence(
        issuance_interval_id=0,
        agent_ecu_weights={AGENT_A: "1"},
        accrual_close_validation_epoch=40320,
        lmdb_state_root_sha256="2" * 64,
    )

    with pytest.raises(ValueError, match="ecu_accrual_evidence_sha256_mismatch"):
        EcuAccrualEvidence(
            issuance_interval_id=0,
            agent_ecu_weights={AGENT_A: "1"},
            accrual_close_validation_epoch=40320,
            lmdb_state_root_sha256="3" * 64,
            evidence_sha256=evidence.evidence_sha256,
        )


def test_no_float_literals_in_new_epoch_receipt_store() -> None:
    source = Path(__file__).resolve().parents[1] / "ilc_core/epoch/ecu_attribution_receipt_store.py"
    tree = ast.parse(source.read_text(encoding="utf-8"))

    for node in ast.walk(tree):
        assert not (isinstance(node, ast.Constant) and isinstance(node.value, float))
