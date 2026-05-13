from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from ilc_core.sidecars import claimability_receipt_verifier as crv
from ilc_core.sidecars import local_graph_memory_projection as lgmp
from ilc_core.sidecars import public_fetch_p2p_readiness as pfp
from ilc_core.sidecars import registry_manifest as registry
from ilc_core.sidecars import transport_principal_admission as tpa


ROOT = Path(__file__).resolve().parents[1]
FRONTIER_DOCS = (
    ROOT / "docs/specs/ilc_phase_1324_fix2_sidecar_harness_cross_module_hardening_v0.1.md",
    ROOT / "docs/phases/phase_1324_fix2_sidecar_harness_cross_module_hardening_walkthrough.md",
    ROOT / "docs/phases/STATUS.md",
    ROOT / "docs/PLANNING_INDEX.md",
    ROOT / "docs/specs/ilc_antigravity_context_capsule_v5.54.md",
)


def _error_token(error: BaseException) -> str:
    return str(getattr(error, "token", error))


@pytest.mark.parametrize(
    ("canonical", "error_type", "token"),
    (
        (
            registry.canonical_sidecar_registry_manifest_json,
            ValueError,
            "sidecar_registry_text_invalid_phase_1307",
        ),
        (
            crv.canonical_json,
            crv.ClaimabilityReceiptVerifierError,
            "claimability_payload_text_invalid_phase_1305",
        ),
        (
            tpa.canonical_transport_principal_admission_json,
            tpa.TransportPrincipalAdmissionSidecarError,
            "transport_principal_admission_text_invalid_phase_1309",
        ),
        (
            lgmp.canonical_local_graph_memory_projection_json,
            lgmp.LocalGraphMemoryProjectionError,
            "local_graph_memory_projection_text_invalid_phase_1311",
        ),
        (
            pfp.canonical_public_fetch_p2p_readiness_candidate_json,
            pfp.PublicFetchP2PReadinessError,
            "public_fetch_p2p_text_invalid_phase_1313",
        ),
    ),
)
def test_sidecar_canonical_payloads_reject_control_characters(
    canonical: Callable[[Any], str],
    error_type: type[BaseException],
    token: str,
) -> None:
    with pytest.raises(error_type) as exc_info:
        canonical({"alpha": "bad\tvalue"})

    assert _error_token(exc_info.value) == token


@pytest.mark.parametrize(
    ("module", "canonical", "error_type", "token"),
    (
        (
            registry,
            registry.canonical_sidecar_registry_manifest_json,
            ValueError,
            "sidecar_registry_payload_size_exceeded_phase_1307",
        ),
        (
            crv,
            crv.canonical_json,
            crv.ClaimabilityReceiptVerifierError,
            "claimability_payload_size_exceeded_phase_1305",
        ),
        (
            tpa,
            tpa.canonical_transport_principal_admission_json,
            tpa.TransportPrincipalAdmissionSidecarError,
            "transport_principal_admission_payload_size_exceeded_phase_1309",
        ),
        (
            lgmp,
            lgmp.canonical_local_graph_memory_projection_json,
            lgmp.LocalGraphMemoryProjectionError,
            "local_graph_memory_projection_payload_size_exceeded_phase_1311",
        ),
        (
            pfp,
            pfp.canonical_public_fetch_p2p_readiness_candidate_json,
            pfp.PublicFetchP2PReadinessError,
            "public_fetch_p2p_payload_size_exceeded_phase_1313",
        ),
    ),
)
def test_sidecar_canonical_json_output_caps_are_enforced(
    monkeypatch: pytest.MonkeyPatch,
    module: object,
    canonical: Callable[[Any], str],
    error_type: type[BaseException],
    token: str,
) -> None:
    monkeypatch.setattr(module, "_MAX_CANONICAL_JSON_BYTES", 5)

    with pytest.raises(error_type) as exc_info:
        canonical({"alpha": "beta"})

    assert _error_token(exc_info.value) == token


@pytest.mark.parametrize(
    ("module", "canonical", "error_type", "token"),
    (
        (
            registry,
            registry.canonical_sidecar_registry_manifest_json,
            ValueError,
            "sidecar_registry_payload_too_large_phase_1307",
        ),
        (
            crv,
            crv.canonical_json,
            crv.ClaimabilityReceiptVerifierError,
            "claimability_payload_too_large_phase_1305",
        ),
        (
            tpa,
            tpa.canonical_transport_principal_admission_json,
            tpa.TransportPrincipalAdmissionSidecarError,
            "transport_principal_admission_payload_too_large_phase_1309",
        ),
        (
            lgmp,
            lgmp.canonical_local_graph_memory_projection_json,
            lgmp.LocalGraphMemoryProjectionError,
            "local_graph_memory_projection_payload_too_large_phase_1311",
        ),
        (
            pfp,
            pfp.canonical_public_fetch_p2p_readiness_candidate_json,
            pfp.PublicFetchP2PReadinessError,
            "public_fetch_p2p_payload_too_large_phase_1313",
        ),
    ),
)
def test_sidecar_payload_node_budgets_count_mapping_keys(
    monkeypatch: pytest.MonkeyPatch,
    module: object,
    canonical: Callable[[Any], str],
    error_type: type[BaseException],
    token: str,
) -> None:
    max_nodes_name = (
        "_MAX_CANONICAL_PAYLOAD_NODES"
        if module is crv
        else "_MAX_PAYLOAD_NODES"
    )
    monkeypatch.setattr(module, max_nodes_name, 2)

    with pytest.raises(error_type) as exc_info:
        canonical({"alpha": "beta"})

    assert _error_token(exc_info.value) == token


def test_sidecar_epoch_zero_is_rejected_on_epoch_surfaces() -> None:
    with pytest.raises(crv.ClaimabilityReceiptVerifierError) as crv_exc:
        crv._require_non_negative_int(0, token="claimability_conversion_receipt_invalid_phase_1305")
    assert crv_exc.value.token == "claimability_conversion_receipt_invalid_phase_1305"

    with pytest.raises(tpa.TransportPrincipalAdmissionSidecarError) as tpa_exc:
        tpa._require_epoch("current", 0)
    assert tpa_exc.value.token == "transport_principal_admission_current_epoch_invalid_phase_1309"

    with pytest.raises(lgmp.LocalGraphMemoryProjectionError) as lgmp_exc:
        lgmp._require_epoch("projection", 0)
    assert lgmp_exc.value.token == "local_graph_memory_projection_projection_epoch_invalid_phase_1311"

    with pytest.raises(pfp.PublicFetchP2PReadinessError) as pfp_exc:
        pfp._require_epoch("current", 0)
    assert pfp_exc.value.token == "public_fetch_p2p_current_epoch_invalid_phase_1313"


def test_public_fetch_default_export_uses_positive_epoch() -> None:
    payload = json.loads(pfp.export_public_fetch_p2p_readiness_candidate_json())

    assert payload["current_epoch"] == 1


def test_sidecar_registry_rejects_unbounded_integer_payloads() -> None:
    with pytest.raises(ValueError, match="sidecar_registry_payload_int_invalid_phase_1307"):
        registry.canonical_sidecar_registry_manifest_json({"too_large": 10**100})


def test_phase_1324_fix2_frontier_docs_record_hardening_tokens() -> None:
    combined = "\n".join(path.read_text(encoding="utf-8") for path in FRONTIER_DOCS)

    for token in (
        "phase_1324_fix2_sidecar_harness_cross_module_hardening.v0.1",
        "sidecar_registry_canonical_json_guarded_phase_1324_fix2",
        "sidecar_epoch_zero_rejected_cross_module_phase_1324_fix2",
        "sidecar_control_character_rejection_cross_module_phase_1324_fix2",
        "sidecar_canonical_json_byte_caps_cross_module_phase_1324_fix2",
        "sidecar_payload_key_counting_cross_module_phase_1324_fix2",
        "public_rc_remains_blocked_after_phase_1324_fix2",
        "phase_1325_ccss_capability_membership_boundary_next_after_fix2",
    ):
        assert token in combined
