"""Regression tests for Phase 1403 CDL-092 CapProof deliberation."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DELIBERATION_DOC = REPO_ROOT / "docs/specs/ilc_cdl_092_capproof_deliberation_1403_v0.1.md"
CDL_REGISTER = REPO_ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _cdl_092_row() -> str:
    for line in _read(CDL_REGISTER).splitlines():
        if line.startswith("| CDL-092 |"):
            return line
    raise AssertionError("CDL-092 row not found")


def test_deliberation_doc_exists_with_required_tokens() -> None:
    text = _read(DELIBERATION_DOC)

    assert "cdl_092_deliberation_complete_phase_1403" in text
    assert "cdl_092_not_ratified_phase_1403" in text
    assert "cdl_092_candidate_prelock_constants_recorded_phase_1403" in text


def test_all_q1_q4_questions_are_resolved() -> None:
    text = _read(DELIBERATION_DOC)

    assert "## 3. Q1 Resolution: Content-Address Input" in text
    assert "## 4. Q2 Resolution: Capability Vector Signing Chain" in text
    assert "## 5. Q3 Resolution: Pricing-Band Rule" in text
    assert "## 6. Q4 Resolution: Work-Type Applicability" in text
    assert "explicit_lane_allowlist" in text


def test_content_address_resolution_requires_canonical_json() -> None:
    text = _read(DELIBERATION_DOC)

    assert "sort_keys=True" in text
    assert "allow_nan=False" in text
    assert "separators=(\",\", \":\")" in text
    assert "CAPPROOF_WALL_CLOCK_IN_HASH_INPUT" in text
    assert "| `CAPPROOF_WALL_CLOCK_IN_HASH_INPUT` | `false` |" in text


def test_signing_chain_resolution_anchors_to_adr0038() -> None:
    text = _read(DELIBERATION_DOC)

    assert "CAPPROOF_CV_SIGNATURE_DOMAIN" in text
    assert "ILC_CAPPROOF_CV_V1" in text
    assert "CAPPROOF_IDENTITY_ANCHOR_REQUIRED" in text
    assert "adr_0038_agent_birth_attestation_genesis_rooted" in text
    assert "CAPPROOF_SECRET_MATERIAL_IN_PAYLOAD_ALLOWED" in text


def test_pricing_band_resolution_uses_decimal_multiplicative_bounds() -> None:
    text = _read(DELIBERATION_DOC)

    assert 'Decimal("0.85")' in text
    assert 'Decimal("1.00")' in text
    assert 'Decimal("1.15")' in text
    assert "multiplicative_decimal_multiplier" in text
    assert "CAPPROOF_DIRECT_ILC_REWARD_ALLOWED" in text


def test_applicability_is_allowlist_not_all_ecu_work() -> None:
    text = _read(DELIBERATION_DOC)

    assert "CAPPROOF_APPLICABILITY_MODE" in text
    assert "explicit_lane_allowlist" in text
    assert "CAPPROOF_DEFAULT_FOR_UNLISTED_LANES" in text
    assert "Subjective jury review" in text
    assert "excluded" in text
    assert "Validator BFT voting weight or safety quorum" in text


def test_cdl_092_register_remains_open_and_unratified() -> None:
    row = _cdl_092_row()

    assert "| open |" in row
    assert "opened_phase: 1402" in row
    assert "ratification_status: not_ratified_pending_phase_1405" in row
    assert "ratified_phase: 1403" not in row
    assert "ratification_token: cdl_092_ratified" not in row


def test_deliberation_doc_does_not_prematurely_ratify_or_activate() -> None:
    text = _read(DELIBERATION_DOC)

    assert "cdl_092_ratified_phase_1403" not in text
    assert "capproof_pricing_active" not in text
    assert "CapProof does not apply automatically to all ECU-earning work" in text
