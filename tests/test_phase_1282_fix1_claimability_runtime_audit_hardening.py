from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from ilc_core.ledger.cdl048_conversion_sweeper_runtime import (
    Cdl048ConversionSweeperRuntimeError,
    canonical_json as sweeper_canonical_json,
    conversion_receipt_payload,
    convert_ecu_lot,
    empty_conversion_sweeper_state,
    register_ecu_lot,
)
from ilc_core.ledger.claimability_proof_binding_runtime import (
    ClaimabilityProofBindingRuntimeError,
    build_claimability_proof_binding,
    canonical_json as claimability_canonical_json,
)


ROOT = Path(__file__).resolve().parents[1]

SWEEPER_RUNTIME = ROOT / "ilc_core/ledger/cdl048_conversion_sweeper_runtime.py"
CLAIMABILITY_RUNTIME = ROOT / "ilc_core/ledger/claimability_proof_binding_runtime.py"
SWEEPER_SPEC = ROOT / "docs/specs/ilc_cdl048_conversion_sweeper_runtime_skeleton_1274_v0.1.md"
CLAIMABILITY_SPEC = ROOT / "docs/specs/ilc_claimability_proof_binding_runtime_boundary_1275_v0.1.md"
ROADMAP = ROOT / "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md"
CAPSULE = ROOT / "docs/specs/ilc_antigravity_context_capsule_v5.51.md"
PLANNING = ROOT / "docs/PLANNING_INDEX.md"
STATUS = ROOT / "docs/phases/STATUS.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1282_fix1_claimability_runtime_audit_hardening_walkthrough.md"

REQUIRED_TOKENS = (
    "phase_1282_fix1_claimability_runtime_audit_hardening",
    "claimability_conversion_receipt_semantics_hardened_phase_1282_fix1",
    "settled_runtime_root_domain_separation_hardened_phase_1282_fix1",
    "balance_receipt_decimal_boundary_hardened_phase_1282_fix1",
    "cdl048_conversion_sweeper_public_rc_exclude_marked_phase_1282_fix1",
    "public_rc_remains_blocked_after_phase_1282_fix1",
)


def _sha_ref(prefix: str, char: str) -> str:
    return f"{prefix}:{char * 64}"


def _receipt() -> dict[str, object]:
    state = register_ecu_lot(
        empty_conversion_sweeper_state(),
        lot_id="lot:phase-1282-fix1",
        agent_id="agent:phase-1282-fix1",
        amount_ecu="10.5",
        issue_epoch=8,
        origin="epoch-attribution:phase-1282-fix1",
        funding_provenance=["receipt:phase-1282-fix1"],
    )
    result = convert_ecu_lot(
        state,
        lot_id="lot:phase-1282-fix1",
        agent_id="agent:phase-1282-fix1",
        conversion_epoch=12,
        settled_runtime_epoch=12,
        wallet_state_root=_sha_ref("wallet_state_sha256", "a"),
        settled_runtime_root=_sha_ref("settled_runtime_sha256", "b"),
    )
    return conversion_receipt_payload(result.receipt)


def _balance_receipt(**overrides: str) -> dict[str, str]:
    payload = {
        "epoch_id": "epoch:0012",
        "reward_delta_ilc": "1.25",
        "balance_after_ilc": "1.25",
        "settlement_status": "applied",
    }
    payload.update(overrides)
    return payload


def _rehash_receipt(payload: dict[str, object]) -> dict[str, object]:
    active = dict(payload)
    active.pop("receipt_sha256", None)
    active["receipt_sha256"] = hashlib.sha256(
        claimability_canonical_json(active).encode("utf-8")
    ).hexdigest()
    return active


def _build_binding(receipt: dict[str, object], **overrides: object):
    kwargs: dict[str, object] = {
        "agent_id": "agent:phase-1282-fix1",
        "epoch_id": "epoch:0012",
        "settled_runtime_root": _sha_ref("settled_runtime_sha256", "b"),
        "wallet_state_root": _sha_ref("wallet_state_sha256", "a"),
        "latest_balance_receipt": _balance_receipt(),
        "history_digest": "c" * 64,
        "conversion_receipt": receipt,
    }
    kwargs.update(overrides)
    return build_claimability_proof_binding(**kwargs)


def _error_token(exc_info: pytest.ExceptionInfo[BaseException]) -> str | None:
    return getattr(exc_info.value, "token", None)


def test_phase_1282_fix1_rejects_hash_consistent_late_conversion_receipts() -> None:
    forged = _receipt()
    forged["conversion_epoch"] = 99
    forged["settled_runtime_epoch"] = 99
    forged = _rehash_receipt(forged)

    with pytest.raises(ClaimabilityProofBindingRuntimeError) as exc_info:
        _build_binding(forged)

    assert _error_token(exc_info) == "claimability_conversion_receipt_invalid"


def test_phase_1282_fix1_rejects_hash_consistent_wrong_conversion_key() -> None:
    forged = _receipt()
    forged["conversion_key_sha256"] = "d" * 64
    forged = _rehash_receipt(forged)

    with pytest.raises(ClaimabilityProofBindingRuntimeError) as exc_info:
        _build_binding(forged)

    assert _error_token(exc_info) == "claimability_conversion_key_sha256_invalid"


def test_phase_1282_fix1_rejects_hash_consistent_noncanonical_conversion_amount() -> None:
    forged = _receipt()
    forged["amount_ecu"] = "010.5000"
    forged = _rehash_receipt(forged)

    with pytest.raises(ClaimabilityProofBindingRuntimeError) as exc_info:
        _build_binding(forged)

    assert _error_token(exc_info) == "claimability_conversion_receipt_invalid"


def test_phase_1282_fix1_rejects_wallet_namespace_as_settled_runtime_root() -> None:
    wallet_root = _sha_ref("wallet_state_sha256", "a")
    forged = _receipt()
    forged["settled_runtime_root"] = wallet_root
    forged = _rehash_receipt(forged)

    with pytest.raises(ClaimabilityProofBindingRuntimeError) as exc_info:
        _build_binding(
            forged,
            settled_runtime_root=wallet_root,
            wallet_state_root=wallet_root,
        )

    assert _error_token(exc_info) == "claimability_settled_runtime_root_invalid"


@pytest.mark.parametrize("bad_value", ("NaN", "Infinity", "not-a-number"))
def test_phase_1282_fix1_rejects_non_finite_or_non_numeric_balance_receipts(
    bad_value: str,
) -> None:
    with pytest.raises(ClaimabilityProofBindingRuntimeError) as exc_info:
        _build_binding(
            _receipt(),
            latest_balance_receipt=_balance_receipt(balance_after_ilc=bad_value),
        )

    assert _error_token(exc_info) == "claimability_latest_balance_receipt_invalid"


def test_phase_1282_fix1_sweeper_rejects_placeholder_roots_and_direct_float_receipts() -> None:
    state = register_ecu_lot(
        empty_conversion_sweeper_state(),
        lot_id="lot:bad-root",
        agent_id="agent:phase-1282-fix1",
        amount_ecu="10.5",
        issue_epoch=8,
        origin="epoch-attribution:phase-1282-fix1",
        funding_provenance=["receipt:phase-1282-fix1"],
    )
    with pytest.raises(Cdl048ConversionSweeperRuntimeError) as root_exc:
        convert_ecu_lot(
            state,
            lot_id="lot:bad-root",
            agent_id="agent:phase-1282-fix1",
            conversion_epoch=12,
            settled_runtime_epoch=12,
            wallet_state_root="wallet_state_sha256:placeholder",
            settled_runtime_root=_sha_ref("settled_runtime_sha256", "b"),
        )
    assert _error_token(root_exc) == "cdl048_wallet_state_root_required"

    receipt = _receipt()
    receipt["amount_ecu"] = 1.25
    with pytest.raises(Cdl048ConversionSweeperRuntimeError) as amount_exc:
        conversion_receipt_payload(
            type("ReceiptLike", (), receipt)()  # type: ignore[arg-type]
        )
    assert _error_token(amount_exc) == "cdl048_amount_invalid"


def test_phase_1282_fix1_canonical_helpers_remain_strict_json() -> None:
    assert sweeper_canonical_json({"b": 1, "a": 2}) == '{"a":2,"b":1}'
    assert claimability_canonical_json({"b": 1, "a": 2}) == '{"a":2,"b":1}'
    with pytest.raises(ValueError):
        sweeper_canonical_json({"bad": float("nan")})
    with pytest.raises(ValueError):
        claimability_canonical_json({"bad": float("nan")})


def test_phase_1282_fix1_docs_and_frontier_records_are_published() -> None:
    for path in (
        SWEEPER_RUNTIME,
        CLAIMABILITY_RUNTIME,
        SWEEPER_SPEC,
        CLAIMABILITY_SPEC,
        ROADMAP,
        CAPSULE,
        PLANNING,
        STATUS,
        WALKTHROUGH,
    ):
        text = path.read_text(encoding="utf-8")
        for token in REQUIRED_TOKENS:
            assert token in text

    planning = PLANNING.read_text(encoding="utf-8")
    assert "Window 1281-1288 is OPEN through Phase 1282 Fix1" in planning
    assert "Phase 1283 is sensitive" in planning
    assert "wallet withdrawal, wallet transfer, wallet spend" in planning


def test_phase_1282_fix1_public_rc_exclusion_and_non_authorization_are_explicit() -> None:
    sweeper_header = "\n".join(SWEEPER_RUNTIME.read_text(encoding="utf-8").splitlines()[:6])
    claimability_header = "\n".join(
        CLAIMABILITY_RUNTIME.read_text(encoding="utf-8").splitlines()[:6]
    )
    assert "PUBLIC_RC_EXCLUDE: internal_phase_helper_not_public_rc_launch_surface" in sweeper_header
    assert (
        "PUBLIC_RC_EXCLUDE: internal_phase_helper_not_public_rc_launch_surface"
        in claimability_header
    )

    for path in (ROADMAP, CAPSULE, PLANNING, STATUS, WALKTHROUGH):
        text = path.read_text(encoding="utf-8")
        assert "public_rc_remains_blocked_after_phase_1282_fix1" in text
        assert "No public claimability activation" in text or "public claimability" in text
