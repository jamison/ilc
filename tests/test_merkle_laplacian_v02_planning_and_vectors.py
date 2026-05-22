import json
from pathlib import Path

import pytest

from ilc_core.analysis.spectral_utils import (
    quantize_spectral_eigenvalues_fixed_point,
    spectral_hash,
    spectral_hash_fixed_point_int64_le,
)


ROOT = Path(__file__).resolve().parents[1]
VECTOR_JSON = (
    ROOT
    / "docs/specs/ilc_merkle_laplacian_v02_canonical_vectors_2026_05_22_v0.1.json"
)
TRANSCRIPT_SPEC = (
    ROOT
    / "docs/specs/ilc_merkle_laplacian_v02_canonicalization_and_posk_transcript_spec_v0.1.md"
)
FORWARD_1429 = (
    ROOT
    / "docs/specs/ilc_window_1429_1458_public_rc_activation_forward_plan_v0.1.md"
)
FORWARD_1459 = ROOT / "docs/specs/ilc_window_1459_forward_plan_v0.1.md"


def test_v02_spectral_hash_vectors_reproduce() -> None:
    data = json.loads(VECTOR_JSON.read_text(encoding="utf-8"))

    assert data["PUBLIC_RC_EXCLUDE"] == "internal_research_patent_sensitive_pre_cdl"
    assert data["q"] == 1_000_000
    for vector in data["vectors"]:
        values = vector["input_eigenvalues"]
        k = vector["k"]
        expected_mu = vector["expected_mu"]
        expected_hash = vector["expected_hash"]

        assert quantize_spectral_eigenvalues_fixed_point(values, k=k) == expected_mu
        assert spectral_hash_fixed_point_int64_le(values, k=k) == expected_hash


def test_v02_hash_rejects_invalid_inputs_and_legacy_hash_differs() -> None:
    with pytest.raises(ValueError, match="spectral_hash_eigenvalue_non_finite"):
        spectral_hash_fixed_point_int64_le([0.0, float("nan")])

    with pytest.raises(ValueError, match="spectral_hash_q_must_be_positive"):
        quantize_spectral_eigenvalues_fixed_point([0.0], q=0)

    eigenvalues = [0.5, 0.0, 1.25, 0.3333333333]
    assert spectral_hash(eigenvalues) != spectral_hash_fixed_point_int64_le(
        eigenvalues,
        k=3,
    )


def test_posk_transcript_spec_records_required_controls() -> None:
    text = TRANSCRIPT_SPEC.read_text(encoding="utf-8")

    required = [
        "PUBLIC_RC_EXCLUDE",
        "edge_set_root_r_c",
        "challenge_expires_at_epoch",
        "response timeout or local-storage attestation",
        "Single-challenge stale-cache detection is probabilistic",
        "Opening any ADR-0029/Merkle-Laplacian CDL | SENSITIVE",
        "Activating PoSK as an admission gate | SENSITIVE",
    ]
    for token in required:
        assert token in text


def test_forward_plans_route_merkle_laplacian_lane() -> None:
    plan_1429 = FORWARD_1429.read_text(encoding="utf-8")
    plan_1459 = FORWARD_1459.read_text(encoding="utf-8")

    assert "Post-public-RC ADR-0029 Merkle-Laplacian / PoSK hardening lane" in plan_1429
    assert "no_merkle_laplacian_epoch_commitment_activation_from_v0_2" in plan_1429
    assert "public_rc_exclude_retained_for_merkle_laplacian_artifacts" in plan_1429

    assert "G — ADR-0029 Merkle-Laplacian hardening" in plan_1459
    assert "Phase 1478 — Merkle-Laplacian canonical vectors" in plan_1459
    assert "Phase 1481 — IP/counsel/publication disposition (SENSITIVE)" in plan_1459
    assert "Phase 1482 — ADR-0029 Merkle-Laplacian CDL readiness verdict" in plan_1459
    assert "PoSK admission-gate activation without a SENSITIVE CDL" in plan_1459
