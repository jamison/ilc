from __future__ import annotations

from pathlib import Path

import pytest

from ilc_core.graph.sidecar_public_path_preflight import (
    build_sidecar_public_path_preflight,
    validate_sidecar_public_path_preflight,
)
from ilc_core.ledger.cdl048_conversion_sweeper_runtime import (
    Cdl048ConversionSweeperRuntimeError,
    canonical_json as sweeper_canonical_json,
)
from ilc_core.ledger.claimability_proof_binding_runtime import (
    ClaimabilityProofBindingRuntimeError,
    canonical_json as claimability_canonical_json,
)
from ilc_core.network.d2d.transport_principal_pre_public_path import (
    build_transport_principal_context,
)
from ilc_core.network.d2d.transport_principal_public_path_preflight import (
    build_transport_principal_public_path_preflight,
    validate_transport_principal_public_path_preflight,
)
from tools.check_sensitive_runtime_coding_taboos import find_violations


ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING = ROOT / "docs/PLANNING_INDEX.md"
CAPSULE = ROOT / "docs/specs/ilc_antigravity_context_capsule_v5.51.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1288_fix1_runtime_deep_audit_hardening_walkthrough.md"
GUARDRAIL = ROOT / "tools/check_sensitive_runtime_coding_taboos.py"

REQUIRED_TOKENS = (
    "phase_1288_fix1_runtime_deep_audit_hardening",
    "canonical_payload_float_rejection_hardened_phase_1288_fix1",
    "untrusted_payload_cycle_depth_bounds_hardened_phase_1288_fix1",
    "public_path_preflight_key_shape_hardened_phase_1288_fix1",
    "public_rc_remains_blocked_after_phase_1288_fix1",
)


def _deep_payload(depth: int) -> dict[str, object]:
    value: object = "leaf"
    for _ in range(depth):
        value = {"child": value}
    return {"root": value}


def _transport_preflight() -> dict[str, object]:
    context = build_transport_principal_context(
        credential_kind="signed_transport_handshake",
        credential_material="phase-1288-fix1-authenticated-handshake-material",
        handshake_nonce="phase-1288-fix1-nonce",
        issued_epoch=40,
        expires_epoch=44,
        current_epoch=42,
    )
    return build_transport_principal_public_path_preflight(
        transport_principal_context=context,
        current_epoch=42,
    )


def _sidecar_preflight() -> dict[str, object]:
    return build_sidecar_public_path_preflight(
        transport_principal_preflight=_transport_preflight(),
        current_epoch=42,
    )


def _error_token(exc_info: pytest.ExceptionInfo[BaseException]) -> str | None:
    return getattr(exc_info.value, "token", None)


def test_phase_1288_fix1_canonical_json_rejects_finite_floats_and_bad_keys() -> None:
    with pytest.raises(Cdl048ConversionSweeperRuntimeError) as sweeper_float:
        sweeper_canonical_json({"amount_ecu": 1.25})
    assert _error_token(sweeper_float) == "cdl048_float_forbidden"

    with pytest.raises(ClaimabilityProofBindingRuntimeError) as claimability_float:
        claimability_canonical_json({"reward_delta_ilc": 1.25})
    assert _error_token(claimability_float) == "claimability_float_forbidden"

    with pytest.raises(Cdl048ConversionSweeperRuntimeError) as sweeper_key:
        sweeper_canonical_json({1: "not-a-json-object-key"})
    assert _error_token(sweeper_key) == "cdl048_payload_key_invalid"

    with pytest.raises(ClaimabilityProofBindingRuntimeError) as claimability_key:
        claimability_canonical_json({1: "not-a-json-object-key"})
    assert _error_token(claimability_key) == "claimability_payload_key_invalid"


def test_phase_1288_fix1_canonical_json_rejects_cycles_and_excess_depth() -> None:
    sweeper_cycle: dict[str, object] = {}
    sweeper_cycle["self"] = sweeper_cycle
    with pytest.raises(Cdl048ConversionSweeperRuntimeError) as sweeper_cycle_exc:
        sweeper_canonical_json(sweeper_cycle)
    assert _error_token(sweeper_cycle_exc) == "cdl048_payload_cycle_forbidden"

    claimability_cycle: dict[str, object] = {}
    claimability_cycle["self"] = claimability_cycle
    with pytest.raises(ClaimabilityProofBindingRuntimeError) as claimability_cycle_exc:
        claimability_canonical_json(claimability_cycle)
    assert _error_token(claimability_cycle_exc) == "claimability_payload_cycle_forbidden"

    with pytest.raises(Cdl048ConversionSweeperRuntimeError) as sweeper_depth:
        sweeper_canonical_json(_deep_payload(40))
    assert _error_token(sweeper_depth) == "cdl048_payload_too_deep"

    with pytest.raises(ClaimabilityProofBindingRuntimeError) as claimability_depth:
        claimability_canonical_json(_deep_payload(40))
    assert _error_token(claimability_depth) == "claimability_payload_too_deep"


def test_phase_1288_fix1_transport_preflight_rejects_recursive_untrusted_payloads() -> None:
    preflight = _transport_preflight()

    cyclic = dict(preflight)
    cyclic["self"] = cyclic
    with pytest.raises(
        ValueError,
        match="transport_principal_public_path_payload_cycle_forbidden",
    ):
        validate_transport_principal_public_path_preflight(cyclic, current_epoch=42)

    non_string_key = dict(preflight)
    non_string_key[1] = "bad-key"
    with pytest.raises(
        ValueError,
        match="transport_principal_public_path_payload_key_invalid",
    ):
        validate_transport_principal_public_path_preflight(non_string_key, current_epoch=42)

    too_deep = dict(preflight)
    too_deep["deep"] = _deep_payload(40)
    with pytest.raises(
        ValueError,
        match="transport_principal_public_path_payload_too_deep",
    ):
        validate_transport_principal_public_path_preflight(too_deep, current_epoch=42)


def test_phase_1288_fix1_sidecar_preflight_rejects_recursive_untrusted_payloads() -> None:
    preflight = _sidecar_preflight()

    cyclic = dict(preflight)
    cyclic["self"] = cyclic
    with pytest.raises(ValueError, match="sidecar_public_path_payload_cycle_forbidden"):
        validate_sidecar_public_path_preflight(cyclic, current_epoch=42)

    non_string_key = dict(preflight)
    non_string_key[1] = "bad-key"
    with pytest.raises(ValueError, match="sidecar_public_path_payload_key_invalid"):
        validate_sidecar_public_path_preflight(non_string_key, current_epoch=42)

    too_deep = dict(preflight)
    too_deep["deep"] = _deep_payload(40)
    with pytest.raises(ValueError, match="sidecar_public_path_payload_too_deep"):
        validate_sidecar_public_path_preflight(too_deep, current_epoch=42)


def test_phase_1288_fix1_guardrail_tracks_untrusted_payload_bound_contracts() -> None:
    assert find_violations() == []

    guardrail = GUARDRAIL.read_text(encoding="utf-8")
    for required in (
        "UNTRUSTED_PAYLOAD_BOUND_CONTRACTS",
        "ilc_core/ledger/cdl048_conversion_sweeper_runtime.py",
        "ilc_core/ledger/claimability_proof_binding_runtime.py",
        "ilc_core/network/d2d/transport_principal_public_path_preflight.py",
        "ilc_core/graph/sidecar_public_path_preflight.py",
    ):
        assert required in guardrail


def test_phase_1288_fix1_docs_and_frontier_records_are_published() -> None:
    for path in (STATUS, PLANNING, CAPSULE, WALKTHROUGH):
        text = path.read_text(encoding="utf-8")
        for token in REQUIRED_TOKENS:
            assert token in text
