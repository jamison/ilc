# SPDX-License-Identifier: AGPL-3.0-only

import json

import pytest

from ilc_core.rc.patent_application_numbers_status import (
    ADDENDUM_TO_MODULE,
    FIVE_PROVISIONAL_APPLICATION_NUMBERS_RECEIVED_2026_06_10_TOKEN,
    OFFICIAL_WRITTEN_FILING_RECEIPTS_STILL_PENDING_2026_06_10_TOKEN,
    PATENT_APPLICATION_NUMBERS,
    PATENT_APPLICATION_NUMBERS_COUNT,
    PATENT_APPLICATION_NUMBERS_DATE_RECEIVED,
    PATENT_APPLICATION_NUMBERS_RECEIPT_METHOD,
    PATENT_APPLICATION_NUMBERS_STATUS_TOKENS,
    PATENT_APPLICATION_NUMBERS_STATUS_VERSION,
    PATENT_GATE_UPGRADED_FROM_DELIVERY_ONLY_TO_APPLICATION_NUMBER_CONFIRMED_TOKEN,
    PUBLIC_PATH_REMAINS_BLOCKED_PATENT_APPLICATION_NUMBERS_ADDENDUM_TOKEN,
    US_PROVISIONAL_PATENT_APPLICATION_NUMBERS_RECEIVED_VERBAL_2026_06_10_TOKEN,
    build_patent_application_numbers_status,
    canonical_patent_application_numbers_status_json,
    validate_patent_application_numbers_status,
)


def test_patent_application_numbers_facts_and_tokens() -> None:
    status = build_patent_application_numbers_status()

    assert status["version"] == PATENT_APPLICATION_NUMBERS_STATUS_VERSION
    assert status["tokens"] == list(PATENT_APPLICATION_NUMBERS_STATUS_TOKENS)
    assert status["tokens"] == [
        US_PROVISIONAL_PATENT_APPLICATION_NUMBERS_RECEIVED_VERBAL_2026_06_10_TOKEN,
        FIVE_PROVISIONAL_APPLICATION_NUMBERS_RECEIVED_2026_06_10_TOKEN,
        OFFICIAL_WRITTEN_FILING_RECEIPTS_STILL_PENDING_2026_06_10_TOKEN,
        PATENT_GATE_UPGRADED_FROM_DELIVERY_ONLY_TO_APPLICATION_NUMBER_CONFIRMED_TOKEN,
        PUBLIC_PATH_REMAINS_BLOCKED_PATENT_APPLICATION_NUMBERS_ADDENDUM_TOKEN,
    ]
    assert status["application_numbers"] == PATENT_APPLICATION_NUMBERS
    assert status["application_numbers_count"] == PATENT_APPLICATION_NUMBERS_COUNT
    assert status["application_numbers_count"] == 5
    assert status["receipt_method"] == PATENT_APPLICATION_NUMBERS_RECEIPT_METHOD
    assert status["date_received"] == PATENT_APPLICATION_NUMBERS_DATE_RECEIVED
    assert status["date_received"] == "2026-06-10"
    assert status["addendum_to_module"] == ADDENDUM_TO_MODULE


def test_patent_application_numbers_exact_values() -> None:
    """Each application number must match exactly what was received verbally."""
    nums = PATENT_APPLICATION_NUMBERS
    assert nums["Filing 1 - Merkle-Laplacian dual commitment"] == "64/231,844"
    assert nums["Filing 2 - Truth-primitive state machine"] == "64/231,845"
    assert nums["Filing 3 - ECU metering / verified epistemic work"] == "64/231,846"
    assert nums["Filing 4 - Anti-gaming reward invariants"] == "64/231,847"
    assert nums["Filing 5 - Agentic function endpoint layer"] == "64/231,848"
    assert len(nums) == 5


def test_patent_application_numbers_does_not_clear_public_path() -> None:
    status = build_patent_application_numbers_status()

    assert status["official_written_filing_receipts_received"] is False
    assert status["fix4_delivery_module_modified"] is False
    assert status["public_path_cleared_by_this_record"] is False
    assert status["public_rc_authorized_by_this_record"] is False
    assert status["legal_opinion_or_counsel_disposition_by_this_record"] is False
    assert status["public_path_remains_blocked"] is True
    assert (
        status["patent_gate_status"]
        == "application_numbers_confirmed_verbally_filing_receipts_pending"
    )


@pytest.mark.parametrize(
    ("field", "value", "token"),
    [
        (
            "official_written_filing_receipts_received",
            True,
            "filing_receipts_must_remain_pending",
        ),
        (
            "fix4_delivery_module_modified",
            True,
            "fix4_delivery_module_must_not_be_modified",
        ),
        (
            "public_path_cleared_by_this_record",
            True,
            "must_not_clear_public_path",
        ),
        (
            "public_rc_authorized_by_this_record",
            True,
            "must_not_authorize_public_rc",
        ),
        (
            "public_path_remains_blocked",
            False,
            "must_record_public_path_blocked",
        ),
    ],
)
def test_patent_application_numbers_validation_rejects_overclaiming_clearance(
    field: str,
    value: bool,
    token: str,
) -> None:
    status = build_patent_application_numbers_status()
    status[field] = value

    with pytest.raises(ValueError, match=token):
        validate_patent_application_numbers_status(status)


def test_patent_application_numbers_status_json_is_canonical() -> None:
    status = build_patent_application_numbers_status()
    encoded = canonical_patent_application_numbers_status_json(status)

    assert encoded == json.dumps(
        status,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    assert "64/231,844" in encoded
    assert "64/231,848" in encoded


def test_fix4_delivery_module_still_records_application_numbers_pending() -> None:
    """Confirm the Fix4 historical record is NOT modified by this addendum."""
    from ilc_core.rc.patent_delivery_status import build_patent_delivery_status

    delivery = build_patent_delivery_status()
    # Fix4 validator enforces official_uspto_application_numbers_received is False.
    # This must remain True (i.e., pending=False) as the historical point-in-time record.
    assert delivery["official_uspto_application_numbers_received"] is False
