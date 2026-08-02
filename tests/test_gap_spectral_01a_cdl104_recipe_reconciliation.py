from __future__ import annotations

import hashlib
import re
from pathlib import Path

from ilc_core.analysis.spectral_utils import (
    SPECTRAL_HASH_V02_Q,
    quantize_spectral_eigenvalues_fixed_point,
    spectral_hash,
    spectral_hash_fixed_point_int64_le,
)


ROOT = Path(__file__).resolve().parents[1]
CDL104 = ROOT / "docs/specs/ilc_cdl_104_spectral_hash_epoch_commitment_opening_gap_spectral_01a_v0.1.md"
CDL_REGISTER = ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"
STATUS = ROOT / "docs/phases/STATUS.md"
RUST_TYPES = ROOT / "ilc_consensus/src/types.rs"


def _rust_epoch_settlement_record_block() -> str:
    source = RUST_TYPES.read_text(encoding="utf-8")
    match = re.search(r"pub struct EpochSettlementRecord \{(?P<body>.*?)\n\}", source, re.S)
    assert match is not None
    return match.group("body")


def test_cdl104_opening_records_fixed_point_sha256_recipe() -> None:
    text = CDL104.read_text(encoding="utf-8")
    assert "CDL-104" in text
    assert "Status:** OPEN" in text
    assert "spectral_hash_fixed_point_int64_le" in text
    assert "round_ties_to_even(lambda_i * 1_000_000)" in text
    assert "Signed int64 little-endian" in text
    assert "[u8; 32]" in text
    assert "SHA-384" in text
    assert "rejected" in text.lower()


def test_fixed_point_helper_matches_independent_sha256_preimage() -> None:
    eigenvalues = [1.25, 0.0, 2.0, 0.5]
    expected_mus = [0, 500_000, 1_250_000]
    assert SPECTRAL_HASH_V02_Q == 1_000_000
    assert quantize_spectral_eigenvalues_fixed_point(eigenvalues, k=3) == expected_mus

    packed = b"".join(value.to_bytes(8, "little", signed=True) for value in expected_mus)
    expected = hashlib.sha256(packed).hexdigest()
    assert spectral_hash_fixed_point_int64_le(eigenvalues, k=3) == expected


def test_legacy_float_hash_is_not_candidate_epoch_commitment_recipe() -> None:
    eigenvalues = [1.25, 0.0, 2.0, 0.5]
    assert spectral_hash(eigenvalues) != spectral_hash_fixed_point_int64_le(eigenvalues)

    text = CDL104.read_text(encoding="utf-8")
    assert "legacy raw" in text
    assert "not acceptable for the epoch commitment" in text


def test_rust_epoch_settlement_record_boundary_tracks_ratified_successor() -> None:
    body = _rust_epoch_settlement_record_block()
    status = STATUS.read_text(encoding="utf-8")
    assert "proposal_commitment_sha256" in body
    assert "not_before_unix_ms" in body
    if "cdl_104_ratified_phase_1582" in status:
        assert "pub spectral_hash: [u8; 32]," in body
    else:
        assert "spectral_hash" not in body
        assert "spectral" not in body.lower()


def test_cdl_register_and_status_record_opening_tokens() -> None:
    register = CDL_REGISTER.read_text(encoding="utf-8")
    status = STATUS.read_text(encoding="utf-8")
    assert "| CDL-104 |" in register
    assert "cdl_104_opened_gap_spectral_01a" in register
    assert "cdl_104_opened_gap_spectral_01a" in status
    assert "spectral_digest_recipe_canonicalized_gap_spectral_01a" in status


def test_spectral_route_token_namespace_remains_separate() -> None:
    text = CDL104.read_text(encoding="utf-8")
    route_token = (ROOT / "ilc_core/network/d2d/spectral_route_token.py").read_text(
        encoding="utf-8"
    )
    assert "SpectralRouteToken" in route_token
    assert "CCSS-SPECTRAL-01" in route_token
    assert "SpectralRouteToken" not in text
    assert "CCSS-SPECTRAL-01" not in text
