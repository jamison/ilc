from __future__ import annotations

import inspect
import os

import pytest

from ilc_core.network.d2d.transport_principal_pre_public_path import (
    build_transport_principal_context,
)
from ilc_core.rc import package_profile_ci_gate
from ilc_core.sidecars.claimability_receipt_verifier import (
    ClaimabilityReceiptVerifierError,
    _require_decimal_string,
    canonical_json,
)
from ilc_core.sidecars.local_graph_memory_projection import (
    LocalGraphMemoryProjectionError,
    export_public_safe_projection_envelope_json,
)
from ilc_core.sidecars.transport_principal_admission import (
    TransportPrincipalAdmissionSidecarError,
    build_transport_principal_admission_decision,
    export_transport_principal_admission_decision_json,
)


def _transport_context() -> dict[str, object]:
    return build_transport_principal_context(
        credential_kind="signed_transport_handshake",
        credential_material="window-1303-1316-audit-material",
        handshake_nonce="window-1303-1316-audit-nonce",
        issued_epoch=7,
        expires_epoch=12,
        current_epoch=9,
    )


def test_claimability_decimal_rejects_exponent_bomb_before_fixed_format() -> None:
    with pytest.raises(ClaimabilityReceiptVerifierError) as exc_info:
        _require_decimal_string("1E+1000000000", token="audit_decimal_invalid")

    assert exc_info.value.token == "audit_decimal_invalid"


def test_claimability_canonical_json_rejects_unbounded_integer_payloads() -> None:
    with pytest.raises(ClaimabilityReceiptVerifierError) as exc_info:
        canonical_json({"n": 10**100})

    assert exc_info.value.token == "claimability_payload_int_invalid_phase_1305"


def test_transport_context_rejects_unexpected_keys_before_hashing_decision() -> None:
    context = _transport_context()
    context["unexpected_public_hint"] = "forbidden"

    with pytest.raises(TransportPrincipalAdmissionSidecarError) as exc_info:
        build_transport_principal_admission_decision(
            transport_principal_context=context,
            current_epoch=9,
        )

    assert exc_info.value.token == (
        "transport_principal_admission_context_keys_invalid_phase_1310"
    )


def test_transport_export_rejects_non_mapping_with_stable_error_token() -> None:
    with pytest.raises(TransportPrincipalAdmissionSidecarError) as exc_info:
        export_transport_principal_admission_decision_json("not-a-mapping")  # type: ignore[arg-type]

    assert exc_info.value.token == (
        "transport_principal_admission_decision_invalid_phase_1309"
    )


def test_projection_export_rejects_non_mapping_with_stable_error_token() -> None:
    with pytest.raises(LocalGraphMemoryProjectionError) as exc_info:
        export_public_safe_projection_envelope_json("not-a-mapping")  # type: ignore[arg-type]

    assert exc_info.value.token == (
        "local_graph_memory_projection_envelope_invalid_phase_1311"
    )


@pytest.mark.skipif(not hasattr(os, "symlink"), reason="symlink unavailable")
def test_package_profile_measurement_rejects_symlink_inputs(tmp_path) -> None:
    target = tmp_path / "target.py"
    target.write_text("print('target')\n", encoding="utf-8")
    symlink = tmp_path / "link.py"
    symlink.symlink_to(target)

    with pytest.raises(ValueError, match="package_profile_ci_gate_symlink_forbidden"):
        package_profile_ci_gate._measure_file(symlink)


def test_package_profile_audit_writes_use_atomic_replace() -> None:
    source = inspect.getsource(package_profile_ci_gate._write_text)

    assert "tempfile.mkstemp" in source
    assert "os.replace" in source
