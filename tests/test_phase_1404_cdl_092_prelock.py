"""Regression tests for Phase 1404 CDL-092 CapProof prelock."""

from __future__ import annotations

import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PRELOCK_DOC = REPO_ROOT / "docs/specs/ilc_cdl_092_capproof_prelock_1404_v0.1.md"
CDL_REGISTER = REPO_ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"


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


def test_prelock_doc_present_with_required_tokens() -> None:
    text = _read(PRELOCK_DOC)

    assert "cdl_092_prelock_committed_phase_1404" in text
    assert "cdl_092_not_ratified_phase_1404" in text
    assert "cdl_092_scope_constants_locked_phase_1404" in text


def test_all_scope_constants_are_locked() -> None:
    text = _read(PRELOCK_DOC)

    for constant in REQUIRED_CONSTANTS:
        assert f"`{constant}`" in text


def test_content_address_output_format_uses_adr0001_profile() -> None:
    text = _read(PRELOCK_DOC)

    assert (
        "CAPPROOF_CONTENT_ADDRESS_OUTPUT_FORMAT` | "
        "`adr_0001_nodeid_cidv1_dag_cbor_sha2_256_multihash`"
    ) in text
    assert "ADR-0001" in text
    assert "node_id_from_obj(obj)" in text
    assert "cidv1_sha2_256_candidate` placeholder is therefore superseded" in text


def test_serialization_and_pricing_constants_are_safe() -> None:
    text = _read(PRELOCK_DOC)

    assert "sort_keys=True" in text
    assert "allow_nan=False" in text
    assert 'Decimal("0.85")' in text
    assert 'Decimal("1.00")' in text
    assert 'Decimal("1.15")' in text
    assert "multiplicative_decimal_multiplier" in text


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


def test_current_cdl_register_still_open_and_unratified() -> None:
    row = _cdl_092_row(_read(CDL_REGISTER))

    assert "| open |" in row
    assert "ratification_status: not_ratified_pending_phase_1405" in row
    assert "ratified_phase: 1405" not in row


def test_prelock_does_not_ratify_or_activate() -> None:
    text = _read(PRELOCK_DOC)

    assert "cdl_092_ratified_phase_1405" not in text
    assert "capproof_pricing_activated" not in text
    assert "probe_execution_authorized" not in text
    assert "CDL-092 remains open and unratified after Phase 1404" in text
