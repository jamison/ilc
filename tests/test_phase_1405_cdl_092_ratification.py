"""Regression tests for Phase 1405 CDL-092 CapProof ratification."""

from __future__ import annotations

import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DOC = (
    REPO_ROOT / "docs/specs/ilc_cdl_092_capproof_ratification_evidence_1405_v0.1.md"
)
CDL_REGISTER = REPO_ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"
GATE_SOURCE = REPO_ROOT / "ilc_core/epistemic/jury_activation_gate.py"


REQUIRED_TOKENS = [
    "cdl_092_ratified_phase_1405",
    "cdl_092_capproof_ratification_evidence_committed",
    "cdl_092_historical_hardening_phase_1402_ref_asserted",
    "capproof_pricing_activation_not_authorized_phase_1405",
]

REQUIRED_CONSTANTS = [
    "CAPPROOF_CONTENT_ADDRESS_SCHEMA",
    "CAPPROOF_CONTENT_ADDRESS_SERIALIZATION",
    "CAPPROOF_CONTENT_ADDRESS_OUTPUT_FORMAT",
    "CAPPROOF_CONTENT_ADDRESS_TIME_FIELD",
    "CAPPROOF_WALL_CLOCK_IN_HASH_INPUT",
    "CAPPROOF_CV_SIGNATURE_DOMAIN",
    "CAPPROOF_CV_SIGNER_ROLE",
    "CAPPROOF_IDENTITY_ANCHOR_REQUIRED",
    "CAPPROOF_SECRET_MATERIAL_IN_PAYLOAD_ALLOWED",
    "CAPPROOF_PRICE_MULTIPLIER_MIN",
    "CAPPROOF_PRICE_MULTIPLIER_BASELINE",
    "CAPPROOF_PRICE_MULTIPLIER_MAX",
    "CAPPROOF_PRICE_BAND_MODE",
    "CAPPROOF_PRICE_BAND_CLAMP_ORDER",
    "CAPPROOF_DIRECT_ILC_REWARD_ALLOWED",
    "CAPPROOF_APPLICABILITY_MODE",
    "CAPPROOF_DEFAULT_FOR_UNLISTED_LANES",
    "CAPPROOF_SUBJECTIVE_JURY_REVIEW_APPLICABILITY",
    "CAPPROOF_VALIDATOR_BFT_WEIGHT_APPLICABILITY",
    "CAPPROOF_PUBLIC_CLAIMABILITY_APPLICABILITY",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _cdl_092_row(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("| CDL-092 |"):
            return line
    raise AssertionError("CDL-092 row not found")


def test_evidence_doc_present_with_required_tokens() -> None:
    text = _read(EVIDENCE_DOC)

    for token in REQUIRED_TOKENS:
        assert token in text


def test_all_phase_1404_scope_constants_are_ratified_in_evidence_doc() -> None:
    text = _read(EVIDENCE_DOC)

    for constant in REQUIRED_CONSTANTS:
        assert f"`{constant}`" in text

    assert 'Decimal("0.85")' in text
    assert 'Decimal("1.00")' in text
    assert 'Decimal("1.15")' in text
    assert "sort_keys=True" in text
    assert "allow_nan=False" in text
    assert "adr_0001_nodeid_cidv1_dag_cbor_sha2_256_multihash" in text


def test_historical_hardening_cdl_092_open_at_phase_1402_c2() -> None:
    result = subprocess.run(
        [
            "git",
            "show",
            "5d3ef87d:docs/specs/ilc_constitutional_decision_log_v0.1.md",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    row = _cdl_092_row(result.stdout)

    assert "| open |" in row
    assert "opened_phase: 1402" in row
    assert "opening_token: cdl_092_capproof_opened_phase_1402" in row
    assert "historical_non_ratification_token: cdl_092_not_ratified_phase_1402" in row
    assert "ratification_token: cdl_092_ratified_phase_1405" not in row


def test_current_cdl_register_ratifies_cdl_092_after_phase_1405_c2() -> None:
    row = _cdl_092_row(_read(CDL_REGISTER))

    assert "| ratified |" in row
    assert "opened_phase: 1402" in row
    assert "ratified_phase: 1405" in row
    assert "ratification_token: cdl_092_ratified_phase_1405" in row
    assert (
        "evidence_document: "
        "docs/specs/ilc_cdl_092_capproof_ratification_evidence_1405_v0.1.md"
    ) in row


def test_cdl_092_ratification_preserves_non_activation_boundaries() -> None:
    row = _cdl_092_row(_read(CDL_REGISTER))
    text = _read(EVIDENCE_DOC)

    assert "capproof_pricing_activation_not_authorized_phase_1405" in text
    assert "capproof_pricing_activation_status: not_authorized" in row
    assert "production_probe_execution_status: not_authorized" in row
    assert "direct_ilc_reward_status: not_authorized" in row
    assert "runtime_activation_status: not_authorized" in row


def test_j008_gate_not_flipped_by_phase_1405() -> None:
    text = _read(GATE_SOURCE)

    assert 'condition_id="CAPPROOF_CDL_RATIFIED"' in text
    assert "status=GateConditionStatus.NOT_MET" in text
    assert "capproof_cdl_not_opened_phase_j008" in text
