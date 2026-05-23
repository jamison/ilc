"""Regression tests for Phase 1435 CDL-094 TransportPrincipal ratification."""

from __future__ import annotations

from pathlib import Path

from ilc_core.network.d2d.transport_principal_cdl_094_status import (
    CDL_094_RATIFIED_GOVERNANCE_ONLY_NOT_ACTIVATED_PHASE_1435_TOKEN,
    CDL_094_SCOPE_CONSTANTS_LOCKED_PHASE_1435_TOKEN,
    CDL_094_TRANSPORT_PRINCIPAL_RATIFIED_PHASE_1435_TOKEN,
    GAP_10_CDL_GOVERNANCE_CLOSED_PHASE_1435_TOKEN,
    TRANSPORT_PRINCIPAL_CDL_RATIFIED_PHASE_1435_TOKEN,
    transport_principal_cdl_094_opening_status,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
PRELOCK_DOC = (
    REPO_ROOT
    / "docs/specs/ilc_cdl_094_transport_principal_prelock_1435_v0.1.md"
)
EVIDENCE_DOC = (
    REPO_ROOT
    / "docs/specs/ilc_cdl_094_transport_principal_ratification_evidence_1435_v0.1.md"
)
CDL_REGISTER = REPO_ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"
README = REPO_ROOT / "README.md"
PROMPT = (
    REPO_ROOT
    / "docs/antigravity_tasks/antigravity_prompt__phase_1435_g8_transport_principal_cdl_ratification.md"
)

REQUIRED_PHASE_1435_TOKENS = {
    TRANSPORT_PRINCIPAL_CDL_RATIFIED_PHASE_1435_TOKEN,
    CDL_094_TRANSPORT_PRINCIPAL_RATIFIED_PHASE_1435_TOKEN,
    GAP_10_CDL_GOVERNANCE_CLOSED_PHASE_1435_TOKEN,
    CDL_094_RATIFIED_GOVERNANCE_ONLY_NOT_ACTIVATED_PHASE_1435_TOKEN,
    "cdl_094_prelock_committed_phase_1435",
    CDL_094_SCOPE_CONSTANTS_LOCKED_PHASE_1435_TOKEN,
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _cdl_094_row() -> str:
    for line in _read(CDL_REGISTER).splitlines():
        if line.startswith("| CDL-094 |"):
            return line
    raise AssertionError("CDL-094 row not found")


def test_prelock_doc_locks_required_phase_1435_tokens() -> None:
    text = _read(PRELOCK_DOC)

    for token in REQUIRED_PHASE_1435_TOKENS:
        assert token in text

    assert "Phase 1434 C1 `b5152c37`" in text
    assert "TRANSPORT_PRINCIPAL_CDL_RATIFIED=true" in text
    assert "policy_boundary_constant=TRANSPORT_PRINCIPAL_CDL_RATIFIED" in text


def test_prelock_doc_prohibits_unauthenticated_public_path_fallbacks() -> None:
    text = _read(PRELOCK_DOC)

    for phrase in (
        "IP_ONLY_AUTHENTICATION_ALLOWED` | `false`",
        "JSON_REQUESTER_ID_AUTHENTICATION_ALLOWED` | `false`",
        "REQUESTER_ID_FALLBACK_ALLOWED` | `false`",
        "RAW_AGENT_ID_DEFAULT_RATE_LIMIT_KEY_ALLOWED` | `false`",
        "CLIENT_IP_PRIMARY_RATE_LIMIT_KEY_ALLOWED` | `false`",
        "rate_limit_identity_source=authenticated_transport_principal",
        "rate_limit_window_basis=epoch_sequence",
    ):
        assert phrase in text


def test_evidence_doc_records_scope_and_non_activation_boundary() -> None:
    text = _read(EVIDENCE_DOC)

    for token in REQUIRED_PHASE_1435_TOKENS:
        assert token in text

    assert "Opening anchor:** Phase 1434 C1 `b5152c37`" in text
    assert "Phase 1436 is SENSITIVE, not non-sensitive" in text
    assert "runtime_activation_status=not_authorized" in text
    assert "public_fetch_serving_enabled=false" in text
    assert "public_sidecar_projection_enabled=false" in text
    assert "public_p2p_enabled=false" in text
    assert "live_confidential_contact_instruction_added=false" in text


def test_status_module_records_ratified_governance_without_runtime_activation() -> None:
    status = transport_principal_cdl_094_opening_status()

    assert status["cdl"] == "CDL-094"
    assert status["status"] == "ratified"
    assert status["ratified"] is True
    assert status["gap_10_cdl_governance_closed"] is True
    assert status["policy_boundary_constant"] == "TRANSPORT_PRINCIPAL_CDL_RATIFIED"
    assert status["authenticated_principal_required_for_non_loopback"] is True
    assert status["ip_only_authentication_allowed"] is False
    assert status["json_requester_id_authentication_allowed"] is False
    assert status["requester_id_fallback_allowed"] is False
    assert status["raw_agent_id_default_rate_limit_key_allowed"] is False
    assert status["client_ip_primary_rate_limit_key_allowed"] is False
    assert status["rate_limit_policy_id"] == (
        "per_agent_id_bound_transport_principal_epoch_window"
    )
    assert status["rate_limit_identity_source"] == "authenticated_transport_principal"
    assert status["rate_limit_window_basis"] == "epoch_sequence"
    assert status["ban_revocation_interface_required"] is True
    assert status["public_fetch_serving_enabled"] is False
    assert status["public_p2p_enabled"] is False
    assert status["non_loopback_sidecar_projection_enabled"] is False
    assert status["public_confidential_coordination_enabled"] is False
    assert status["live_confidential_contact_instruction_added"] is False
    assert REQUIRED_PHASE_1435_TOKENS.issubset(set(status["tokens"]))


def test_readme_contact_placeholder_remains_not_live() -> None:
    readme = _read(README)

    assert "jamison_confidential_sidecar: planned_not_live" in readme
    assert "local_preview_only_no_public_confidential_messaging" in readme
    assert "current_contact: out_of_band_until_public_confidential_coordination_authorized" in readme
    assert "public_sidecar_activation" in readme
    assert "public_confidential_coordination_authority" in readme


def test_prompt_routes_phase_1436_as_sensitive_after_gap_14() -> None:
    prompt = _read(PROMPT)

    assert "Phase 1436 sidecar/fetch activation SENSITIVE" in prompt
    assert "Phase 1436 sidecar/fetch activation NON-SENSITIVE" not in prompt


def test_cdl_094_register_row_supports_pre_c2_or_post_c2_state() -> None:
    row = _cdl_094_row()

    assert "CDL-094" in row
    assert "cdl_094_transport_principal_opened_phase_1434" in row
    assert "runtime_activation_status: not_authorized" in row

    if "| ratified |" in row:
        assert "ratified_phase: 1435" in row
        assert "ratification_token: transport_principal_cdl_ratified_phase_1435" in row
        assert "authenticated_principal_required_for_non_loopback: true" in row
        assert "ip_only_authentication_allowed: false" in row
        assert "public_confidential_coordination_status: not_enabled" in row
    else:
        assert "| open |" in row
        assert "historical_non_ratification_token: cdl_094_opening_only_not_ratified_phase_1434" in row
