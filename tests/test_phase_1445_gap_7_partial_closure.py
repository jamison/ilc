# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

from ilc_core.rc.gap_7_closure_status import (
    AGPL_LICENSE_HEADER_AUDIT_COMPLETE_PHASE_1443_TOKEN,
    CLA_TEXT_FINALIZED_PHASE_1444_TOKEN,
    GAP_7_CLOSURE_STATUS,
    GAP_7_INTERNAL_MILESTONES_COMPLETE_PHASE_1445_TOKEN,
    GAP_7_NOT_FULLY_CLOSED_PHASE_1445_TOKEN,
    GAP_7_PARTIALLY_CLOSED_PHASE_1445_TOKEN,
    PHASE_1445_GAP_7_CLOSURE_TOKENS,
    PROVISIONAL_PATENT_DEFERRED_EXTERNAL_COUNSEL_REQUIRED_PHASE_1445_TOKEN,
    TRADEMARK_REGISTRATION_DEFERRED_EXTERNAL_ACTION_REQUIRED_PHASE_1445_TOKEN,
)


def test_phase_1445_gap_7_output_tokens_are_recorded() -> None:
    assert (
        GAP_7_INTERNAL_MILESTONES_COMPLETE_PHASE_1445_TOKEN
        == "gap_7_internal_milestones_complete_phase_1445"
    )
    assert GAP_7_PARTIALLY_CLOSED_PHASE_1445_TOKEN == "gap_7_partially_closed_phase_1445"
    assert GAP_7_NOT_FULLY_CLOSED_PHASE_1445_TOKEN == "gap_7_not_fully_closed_phase_1445"
    assert (
        PROVISIONAL_PATENT_DEFERRED_EXTERNAL_COUNSEL_REQUIRED_PHASE_1445_TOKEN
        == "provisional_patent_deferred_external_counsel_required_phase_1445"
    )
    assert (
        TRADEMARK_REGISTRATION_DEFERRED_EXTERNAL_ACTION_REQUIRED_PHASE_1445_TOKEN
        == "trademark_registration_deferred_external_action_required_phase_1445"
    )


def test_phase_1445_gap_7_token_bundle_includes_non_full_closure() -> None:
    assert (
        GAP_7_INTERNAL_MILESTONES_COMPLETE_PHASE_1445_TOKEN
        in PHASE_1445_GAP_7_CLOSURE_TOKENS
    )
    assert GAP_7_PARTIALLY_CLOSED_PHASE_1445_TOKEN in PHASE_1445_GAP_7_CLOSURE_TOKENS
    assert GAP_7_NOT_FULLY_CLOSED_PHASE_1445_TOKEN in PHASE_1445_GAP_7_CLOSURE_TOKENS
    assert (
        PROVISIONAL_PATENT_DEFERRED_EXTERNAL_COUNSEL_REQUIRED_PHASE_1445_TOKEN
        in PHASE_1445_GAP_7_CLOSURE_TOKENS
    )
    assert (
        TRADEMARK_REGISTRATION_DEFERRED_EXTERNAL_ACTION_REQUIRED_PHASE_1445_TOKEN
        in PHASE_1445_GAP_7_CLOSURE_TOKENS
    )


def test_phase_1445_gap_7_status_table_records_partial_closure() -> None:
    assert GAP_7_CLOSURE_STATUS["gap_7_fully_closed"] is False
    assert GAP_7_CLOSURE_STATUS["agpl_license_headers"] == "complete_phase_1443"
    assert GAP_7_CLOSURE_STATUS["cla_text"] == "complete_phase_1444"
    assert (
        GAP_7_CLOSURE_STATUS["provisional_patent_application"]
        == "deferred_external_counsel_required"
    )
    assert (
        GAP_7_CLOSURE_STATUS["trademark_registration"]
        == "deferred_external_action_required"
    )


def test_phase_1445_input_dependencies_are_importable() -> None:
    assert (
        AGPL_LICENSE_HEADER_AUDIT_COMPLETE_PHASE_1443_TOKEN
        == "agpl_license_header_audit_complete_phase_1443"
    )
    assert CLA_TEXT_FINALIZED_PHASE_1444_TOKEN == "cla_text_finalized_phase_1444"
