# SPDX-License-Identifier: AGPL-3.0-only

import json

import pytest

from ilc_core.rc.patent_delivery_status import (
    FIVE_US_PROVISIONAL_PACKETS_DELIVERED_TO_USPTO_PHASE_1545P_FIX4_TOKEN,
    PATENT_DELIVERY_ACTUAL_DELIVERY_DATE,
    PATENT_DELIVERY_ACTUAL_DELIVERY_TIME_REPORTED,
    PATENT_DELIVERY_DESTINATION,
    PATENT_DELIVERY_SERVICE_REPORTED,
    PATENT_DELIVERY_SIGNER_REPORTED,
    PATENT_DELIVERY_STATUS_TOKENS,
    PATENT_DELIVERY_STATUS_VERSION,
    PATENT_DELIVERY_TRACKING_NUMBER,
    PATENT_FILING_RECEIPTS_PENDING_PHASE_1545P_FIX4_TOKEN,
    PUBLIC_PATH_NOT_CLEARED_BY_PATENT_DELIVERY_PHASE_1545P_FIX4_TOKEN,
    PUBLIC_PATH_REMAINS_BLOCKED_PHASE_1545P_FIX4_TOKEN,
    US_PROVISIONAL_PATENT_PACKAGE_DELIVERED_TO_USPTO_PHASE_1545P_FIX4_TOKEN,
    USPTO_APPLICATION_NUMBERS_PENDING_PHASE_1545P_FIX4_TOKEN,
    build_patent_delivery_status,
    canonical_patent_delivery_status_json,
    validate_patent_delivery_status,
)


def test_phase_1545p_fix4_delivery_record_facts_and_tokens() -> None:
    status = build_patent_delivery_status()

    assert status["version"] == PATENT_DELIVERY_STATUS_VERSION
    assert status["tokens"] == list(PATENT_DELIVERY_STATUS_TOKENS)
    assert status["tokens"] == [
        US_PROVISIONAL_PATENT_PACKAGE_DELIVERED_TO_USPTO_PHASE_1545P_FIX4_TOKEN,
        FIVE_US_PROVISIONAL_PACKETS_DELIVERED_TO_USPTO_PHASE_1545P_FIX4_TOKEN,
        USPTO_APPLICATION_NUMBERS_PENDING_PHASE_1545P_FIX4_TOKEN,
        PATENT_FILING_RECEIPTS_PENDING_PHASE_1545P_FIX4_TOKEN,
        PUBLIC_PATH_NOT_CLEARED_BY_PATENT_DELIVERY_PHASE_1545P_FIX4_TOKEN,
        PUBLIC_PATH_REMAINS_BLOCKED_PHASE_1545P_FIX4_TOKEN,
    ]
    assert status["tracking_number"] == PATENT_DELIVERY_TRACKING_NUMBER
    assert status["actual_delivery_date"] == PATENT_DELIVERY_ACTUAL_DELIVERY_DATE
    assert (
        status["actual_delivery_time_reported"]
        == PATENT_DELIVERY_ACTUAL_DELIVERY_TIME_REPORTED
    )
    assert status["recipient_signer_reported"] == PATENT_DELIVERY_SIGNER_REPORTED
    assert status["destination"] == PATENT_DELIVERY_DESTINATION
    assert status["service_reported"] == PATENT_DELIVERY_SERVICE_REPORTED
    assert status["physical_delivery_to_uspto_recorded"] is True
    assert status["packet_count_inside_package_reported"] == 5


def test_phase_1545p_fix4_delivery_record_does_not_clear_public_path() -> None:
    status = build_patent_delivery_status()

    assert status["official_uspto_filing_receipts_received"] is False
    assert status["official_uspto_application_numbers_received"] is False
    assert status["public_path_cleared_by_this_record"] is False
    assert status["public_rc_authorized_by_this_record"] is False
    assert status["legal_opinion_or_counsel_disposition_by_this_record"] is False
    assert status["public_path_remains_blocked"] is True
    assert (
        status["phase_1448a_patent_blocker_status"]
        == "delivery_recorded_application_numbers_and_filing_receipts_pending"
    )


@pytest.mark.parametrize(
    ("field", "value", "token"),
    [
        ("official_uspto_filing_receipts_received", True, "receipts_must_remain_pending"),
        ("official_uspto_application_numbers_received", True, "numbers_must_remain_pending"),
        ("public_path_cleared_by_this_record", True, "must_not_clear_public_path"),
        ("public_rc_authorized_by_this_record", True, "must_not_authorize_public_rc"),
        ("public_path_remains_blocked", False, "must_record_public_path_blocked"),
    ],
)
def test_phase_1545p_fix4_validation_rejects_overclaiming_clearance(
    field: str,
    value: bool,
    token: str,
) -> None:
    status = build_patent_delivery_status()
    status[field] = value

    with pytest.raises(ValueError, match=token):
        validate_patent_delivery_status(status)


def test_phase_1545p_fix4_status_json_is_canonical() -> None:
    status = build_patent_delivery_status()
    encoded = canonical_patent_delivery_status_json(status)

    assert encoded == json.dumps(
        status,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    assert PATENT_DELIVERY_TRACKING_NUMBER in encoded
