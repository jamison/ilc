"""Regression tests for Phase 1434 CDL-094 TransportPrincipal opening."""

from __future__ import annotations

from pathlib import Path

from ilc_core.network.d2d.transport_principal_cdl_094_status import (
    CDL_094_OPENING_ONLY_NOT_RATIFIED_PHASE_1434_TOKEN,
    CDL_094_TRANSPORT_PRINCIPAL_OPENED_PHASE_1434_TOKEN,
    GAP_10_CDL_OPENING_COMMITTED_PHASE_1434_TOKEN,
    TRANSPORT_PRINCIPAL_CDL_OPENED_PHASE_1434_TOKEN,
    transport_principal_cdl_094_opening_status,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
OPENING_DOC = (
    REPO_ROOT
    / "docs/specs/ilc_cdl_094_transport_principal_public_path_opening_1434_v0.1.md"
)
CDL_REGISTER = REPO_ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"
README = REPO_ROOT / "README.md"
STATUS = REPO_ROOT / "docs/phases/STATUS.md"
SEQUENCE_LOCK = REPO_ROOT / "docs/specs/ilc_phase_1429_1458_sequence_lock_v0.1.md"


REQUIRED_TOKENS = {
    TRANSPORT_PRINCIPAL_CDL_OPENED_PHASE_1434_TOKEN,
    CDL_094_TRANSPORT_PRINCIPAL_OPENED_PHASE_1434_TOKEN,
    GAP_10_CDL_OPENING_COMMITTED_PHASE_1434_TOKEN,
    CDL_094_OPENING_ONLY_NOT_RATIFIED_PHASE_1434_TOKEN,
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _cdl_094_row() -> str:
    for line in _read(CDL_REGISTER).splitlines():
        if line.startswith("| CDL-094 |"):
            return line
    raise AssertionError("CDL-094 row not found")


def test_opening_doc_present_with_required_tokens() -> None:
    text = _read(OPENING_DOC)

    for token in REQUIRED_TOKENS:
        assert token in text


def test_cdl_register_opens_cdl_094_without_ratification() -> None:
    row = _cdl_094_row()

    assert "| open |" in row or "| ratified |" in row
    assert "opened_phase: 1434" in row
    assert "opening_token: cdl_094_transport_principal_opened_phase_1434" in row
    assert "historical_non_ratification_token: cdl_094_opening_only_not_ratified_phase_1434" in row
    assert "runtime_activation_status: not_authorized" in row
    assert "public_fetch_serving_status: not_enabled" in row
    assert "public_p2p_status: not_enabled" in row
    assert "public_confidential_coordination_status: not_enabled" in row


def test_opening_scope_records_gap_10_and_policy_boundaries() -> None:
    text = _read(OPENING_DOC)

    assert "Gap 10 blocks public P2P" in text
    assert "IP address" in text
    assert "JSON body `requester_id`" in text
    assert "rate_limit_identity_source=authenticated_transport_principal" in text
    assert "requester_id_fallback_allowed=false" in text
    assert "client_ip_primary_rate_limit_key_allowed=false" in text
    assert "agent_id_default_rate_limit_key_allowed=false" in text


def test_opening_preserves_readme_contact_placeholder_as_non_claim() -> None:
    readme = _read(README)
    text = _read(OPENING_DOC)

    assert "jamison_confidential_sidecar: planned_not_live" in readme
    assert "current_contact: out_of_band_until_public_confidential_coordination_authorized" in readme
    assert "phase_1434_transport_principal_scope_review" in readme
    assert "phase_1435_transport_principal_ratification_review" in readme
    assert "jamison_confidential_sidecar=planned_not_live" in text
    assert "live_contact_instruction_added=false" in text
    assert "No live confidential contact instruction is added in Phase 1434" in text


def test_opening_status_module_is_default_off() -> None:
    status = transport_principal_cdl_094_opening_status()

    assert status["cdl"] == "CDL-094"
    assert status["status"] in {"open", "ratified"}
    assert isinstance(status["ratified"], bool)
    assert isinstance(status["gap_10_closed"], bool)
    assert status["public_fetch_serving_enabled"] is False
    assert status["public_p2p_enabled"] is False
    assert status["non_loopback_sidecar_projection_enabled"] is False
    assert status["public_confidential_coordination_enabled"] is False
    assert status["jamison_confidential_sidecar"] == "planned_not_live"
    assert REQUIRED_TOKENS.issubset(set(status["tokens"]))


def test_status_and_sequence_lock_route_to_phase_1435() -> None:
    status = _read(STATUS)
    sequence = _read(SEQUENCE_LOCK)

    assert "Phase 1434 / TransportPrincipal CDL Opening" in status
    assert "transport_principal_cdl_opened_phase_1434" in status
    assert "cdl_094_opening_only_not_ratified_phase_1434" in status
    assert "Phase 1435 TransportPrincipal CDL prelock + ratification is next" in status
    assert "Phase 1434 TransportPrincipal CDL opening is complete" in sequence
    assert "Phase 1435 TransportPrincipal CDL prelock + ratification is next" in sequence


def test_opening_records_no_runtime_activation_or_value_path() -> None:
    text = _read(OPENING_DOC)

    for phrase in (
        "public_fetch_serving_enabled=false",
        "public_p2p_enabled=false",
        "non_loopback_sidecar_projection_enabled=false",
        "public_confidential_coordination_enabled=false",
        "runtime_activation_status=not_authorized",
        "wallet writes",
        "ECU minting",
        "ILC settlement",
        "epoch 0-to-1 transition",
    ):
        assert phrase in text
