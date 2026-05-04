"""Phase 1174 — coherence report and capsule v5.42."""

from __future__ import annotations

import json
import pathlib
from decimal import Decimal

from ilc_core.economics.epoch_attribution_settle_runtime import (
    EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION,
)
from ilc_core.types import PROVENANCE_DECAY_ALPHA


ROOT = pathlib.Path(__file__).resolve().parents[1]
ROOT_HASH = "ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c"
COMPILE_V01_SHA256 = "5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56"


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _json(path: str) -> object:
    return json.loads(_read(path))


def test_coherence_report_records_sim_spectral_05_pass_and_tracks() -> None:
    text = _read("docs/specs/ilc_integration_coherence_report_1174_v0.1.md")
    assert "coherence_report_1174_verdict=pass" in text
    assert "sim_spectral_05_gate_pass" in text
    assert "track_a_pass" in text
    assert "track_b_pass" in text
    assert "S1 legitimate branchial paths | 0.85" in text
    assert "S3 branchial Sybil paths | 0.25" in text


def test_coherence_report_records_cdl_085_open_and_opening_only_boundary() -> None:
    text = _read("docs/specs/ilc_integration_coherence_report_1174_v0.1.md")
    assert "CDL-085 status is `open`" in text
    assert "cdl_085_sim_gate_lifted_phase_1172_sim_spectral_05_gate_pass" in text
    assert "`EDGE_MINT_PHI_BOUND` remains" in text
    assert "runtime constant" in text
    assert "ratification occurred" in text


def test_coherence_report_records_adr_outcomes() -> None:
    text = _read("docs/specs/ilc_integration_coherence_report_1174_v0.1.md")
    assert "adr_0037_accepted_phase_1173" in text
    assert "adr_0036_accepted_phase_1173" in text
    assert "Genesis Canonical Lineage Contract | Accepted" in text
    assert "Operational Release Key Genesis Binding | Accepted" in text


def test_capsule_v542_supersedes_v541_and_sets_frontier() -> None:
    text = _read("docs/specs/ilc_antigravity_context_capsule_v5.42.md")
    assert "capsule_v5_42_supersedes_v5_41" in text
    assert "Phase 1174 complete" in text
    assert "Phase 1175 closure gate pending" in text
    assert "sim_spectral_05_gate_pass" in text
    assert "cdl_085_open_phase_1172" in text


def test_capsule_records_remaining_deferred_observer_slices_and_signing_boundary() -> None:
    text = _read("docs/specs/ilc_antigravity_context_capsule_v5.42.md")
    for token in (
        "sim_spectral_05_runtime_binding_slice_deferred_window_1176",
        "sim_spectral_05_economic_flow_slice_deferred_window_1176",
        "sim_spectral_05_gossip_slice_deferred_window_1176",
    ):
        assert token in text
    assert "explicit signing authorization still required" in text


def test_signed_v01_and_v02_candidate_shapes_are_unchanged() -> None:
    star_map = _json("out/genesis_core_star_map_v0.1.json")
    envelope = _json("out/genesis_signing_root_envelope_v0.1.json")
    candidate = _json("out/genesis_core_star_map_v0.2_candidate.json")
    assert isinstance(star_map, dict)
    assert len(star_map["nodes"]) == 32
    assert len(star_map["edges"]) == 55
    assert isinstance(envelope, dict)
    assert envelope["envelope_hash"] == ROOT_HASH
    assert isinstance(candidate, dict)
    assert len(candidate["nodes"]) == 41
    assert len(candidate["edges"]) == 73


def test_compile_coverage_v01_hash_and_runtime_are_unchanged() -> None:
    import hashlib

    digest = hashlib.sha256(
        (ROOT / "out/genesis_compile_coverage_diagnostic_v0.1.json").read_bytes()
    ).hexdigest()
    assert digest == COMPILE_V01_SHA256
    assert EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION == "epoch_attribution_settle_runtime_1129_fix1.v0.5"
    assert PROVENANCE_DECAY_ALPHA == Decimal("0.45")
    assert isinstance(PROVENANCE_DECAY_ALPHA, Decimal)
