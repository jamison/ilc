"""
Phase 1173 — ADR-0036 + ADR-0037 Acceptance Gate Tests

ILC_PHASE_1173_GATE_SELFTEST=1
"""

import json
import os
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).parent.parent
SIGNED_V01 = ROOT / "out" / "genesis_core_star_map_v0.1.json"
GENESIS_HASH = "ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c"
ADR_0037 = ROOT / "docs" / "adr" / "ADR_0037_Genesis_Canonical_Lineage_Contract.md"
ADR_0036 = ROOT / "docs" / "adr" / "ADR_0036_Operational_Release_Key_Genesis_Binding.md"
REVIEW_0037 = ROOT / "docs" / "adr" / "adr_0037_acceptance_review_1173_v0.1.md"
REVIEW_0036 = ROOT / "docs" / "adr" / "adr_0036_acceptance_review_1173_v0.1.md"


def test_adr_0037_review_exists_with_explicit_verdict():
    """T3-1: ADR-0037 review record exists with explicit accept/defer verdict."""
    assert REVIEW_0037.exists(), f"Missing: {REVIEW_0037}"
    text = REVIEW_0037.read_text()
    assert "adr_0037_accepted_phase_1173" in text, (
        "ADR-0037 review record must contain acceptance token"
    )
    # Verify it has a Verdict line
    assert "ACCEPTED" in text or "DEFERRED" in text, (
        "Review record must contain explicit ACCEPTED or DEFERRED verdict"
    )


def test_adr_0036_review_exists_with_explicit_verdict():
    """T3-2: ADR-0036 review record exists with explicit accept/defer verdict."""
    assert REVIEW_0036.exists(), f"Missing: {REVIEW_0036}"
    text = REVIEW_0036.read_text()
    assert "adr_0036_accepted_phase_1173" in text, (
        "ADR-0036 review record must contain acceptance token"
    )
    assert "ACCEPTED" in text or "DEFERRED" in text, (
        "Review record must contain explicit ACCEPTED or DEFERRED verdict"
    )


def test_adr_0037_status_accepted():
    """T3-3a: ADR-0037 file status field reads Accepted after review."""
    assert ADR_0037.exists(), f"Missing: {ADR_0037}"
    text = ADR_0037.read_text()
    # Check Status line specifically
    assert re.search(r"\*\*Status:\*\*\s+Accepted", text), (
        "ADR-0037 Status field must read Accepted"
    )


def test_adr_0036_status_accepted():
    """T3-3b: ADR-0036 file status field reads Accepted after review."""
    assert ADR_0036.exists(), f"Missing: {ADR_0036}"
    text = ADR_0036.read_text()
    assert re.search(r"\*\*Status:\*\*\s+Accepted", text), (
        "ADR-0036 Status field must read Accepted"
    )


def test_signed_v01_unchanged():
    """T3-4: Signed v0.1 star map unchanged."""
    if os.environ.get("ILC_PHASE_1173_GATE_SELFTEST") == "1":
        pytest.skip("selftest guard")
    assert SIGNED_V01.exists(), f"Missing: {SIGNED_V01}"
    data = json.loads(SIGNED_V01.read_text())
    # Node count
    nodes = data.get("nodes", data.get("node_count"))
    if isinstance(nodes, list):
        count = len(nodes)
    else:
        count = int(nodes)
    assert count == 32, f"Signed v0.1 must have 32 nodes; found {count}"
    # Hash guard: root_envelope_hash field if present
    root_hash = data.get("root_envelope_hash") or data.get("envelope_hash")
    if root_hash:
        assert root_hash == GENESIS_HASH, (
            f"Root envelope hash mismatch: {root_hash}"
        )


def test_adr_0037_pec_section_present():
    """ADR-0037 must contain Popperian Equivalence Criterion section."""
    assert ADR_0037.exists()
    text = ADR_0037.read_text()
    assert "Popperian Equivalence Criterion" in text, (
        "ADR-0037 must define the Popperian Equivalence Criterion"
    )
    assert "CDL-V7" in text, (
        "ADR-0037 PEC section must reference CDL-V7 as the single-claim Popperian gate"
    )


def test_adr_0037_six_equivalence_domains():
    """ADR-0037 must contain all six equivalence domain sections."""
    assert ADR_0037.exists()
    text = ADR_0037.read_text()
    for domain in ["Claim Equivalence", "Provenance Equivalence", "Version Equivalence",
                   "Governance Equivalence", "Fork Equivalence", "Economic Equivalence"]:
        assert domain in text, f"ADR-0037 missing domain section: {domain}"


def test_adr_0037_multi_slice_encrustation():
    """ADR-0037 must contain multi-slice encrustation section with all six slices."""
    assert ADR_0037.exists()
    text = ADR_0037.read_text()
    for slice_name in ["Authority", "Claim-composition", "Runtime-binding",
                       "Economic-flow", "Gossip", "Provenance"]:
        assert slice_name in text, f"ADR-0037 missing observer slice: {slice_name}"


def test_adr_0036_scope_boundary_present():
    """ADR-0036 must contain explicit scope boundary listing what it does NOT cover."""
    assert ADR_0036.exists()
    text = ADR_0036.read_text()
    assert "ADR-0036 does not define" in text, (
        "ADR-0036 must explicitly state what it does not cover"
    )
    assert "genesis_canonical_lineage_contract_adr_required_separate_from_adr_0036" in text, (
        "ADR-0036 must carry the lineage contract separation token"
    )
