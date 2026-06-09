# SPDX-License-Identifier: AGPL-3.0-only
"""US provisional patent package physical-delivery status.

PUBLIC_RC_EXCLUDE: patent_delivery_status_internal_record
PUBLIC_RC_EXCLUDE_REASON: Internal filing-delivery evidence record; not a
public patent notice, filing receipt, application-number record, legal opinion,
or public-RC authorization.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any


PATENT_DELIVERY_STATUS_VERSION = "us_provisional_patent_delivery_status_1545p_fix4.v0.1"

US_PROVISIONAL_PATENT_PACKAGE_DELIVERED_TO_USPTO_PHASE_1545P_FIX4_TOKEN = (
    "us_provisional_patent_package_delivered_to_uspto_phase_1545p_fix4"
)
FIVE_US_PROVISIONAL_PACKETS_DELIVERED_TO_USPTO_PHASE_1545P_FIX4_TOKEN = (
    "five_us_provisional_packets_delivered_to_uspto_phase_1545p_fix4"
)
USPTO_APPLICATION_NUMBERS_PENDING_PHASE_1545P_FIX4_TOKEN = (
    "uspto_application_numbers_pending_phase_1545p_fix4"
)
PATENT_FILING_RECEIPTS_PENDING_PHASE_1545P_FIX4_TOKEN = (
    "patent_filing_receipts_pending_phase_1545p_fix4"
)
PUBLIC_PATH_NOT_CLEARED_BY_PATENT_DELIVERY_PHASE_1545P_FIX4_TOKEN = (
    "public_path_not_cleared_by_patent_delivery_phase_1545p_fix4"
)
PUBLIC_PATH_REMAINS_BLOCKED_PHASE_1545P_FIX4_TOKEN = (
    "public_path_remains_blocked_phase_1545p_fix4"
)

PATENT_DELIVERY_STATUS_TOKENS: tuple[str, ...] = (
    US_PROVISIONAL_PATENT_PACKAGE_DELIVERED_TO_USPTO_PHASE_1545P_FIX4_TOKEN,
    FIVE_US_PROVISIONAL_PACKETS_DELIVERED_TO_USPTO_PHASE_1545P_FIX4_TOKEN,
    USPTO_APPLICATION_NUMBERS_PENDING_PHASE_1545P_FIX4_TOKEN,
    PATENT_FILING_RECEIPTS_PENDING_PHASE_1545P_FIX4_TOKEN,
    PUBLIC_PATH_NOT_CLEARED_BY_PATENT_DELIVERY_PHASE_1545P_FIX4_TOKEN,
    PUBLIC_PATH_REMAINS_BLOCKED_PHASE_1545P_FIX4_TOKEN,
)

PATENT_DELIVERY_TRACKING_NUMBER = "872685541879"
PATENT_DELIVERY_SHIP_DATE = "2026-06-05"
PATENT_DELIVERY_ACTUAL_DELIVERY_DATE = "2026-06-08"
PATENT_DELIVERY_ACTUAL_DELIVERY_TIME_REPORTED = "13:18"
PATENT_DELIVERY_SIGNER_REPORTED = "J.Hederson"
PATENT_DELIVERY_DESTINATION = (
    "USPTO Patent Customer Service Window, Knox Building Room 1D80, "
    "501 Dulany St, Alexandria, VA 22314 US"
)
PATENT_DELIVERY_SERVICE_REPORTED = "FedEx International Priority"


def build_patent_delivery_status() -> dict[str, Any]:
    """Return the current internal patent-delivery status record."""
    status = {
        "version": PATENT_DELIVERY_STATUS_VERSION,
        "tokens": list(PATENT_DELIVERY_STATUS_TOKENS),
        "tracking_number": PATENT_DELIVERY_TRACKING_NUMBER,
        "ship_date": PATENT_DELIVERY_SHIP_DATE,
        "actual_delivery_date": PATENT_DELIVERY_ACTUAL_DELIVERY_DATE,
        "actual_delivery_time_reported": PATENT_DELIVERY_ACTUAL_DELIVERY_TIME_REPORTED,
        "delivery_evidence_source": "FedEx mobile tracking screenshots provided by human operator",
        "destination": PATENT_DELIVERY_DESTINATION,
        "recipient_signer_reported": PATENT_DELIVERY_SIGNER_REPORTED,
        "service_reported": PATENT_DELIVERY_SERVICE_REPORTED,
        "package_count_reported": 1,
        "packet_count_inside_package_reported": 5,
        "packets_inside_package": [
            "Filing 1 - Merkle-Laplacian dual commitment",
            "Filing 2 - Truth-primitive state machine",
            "Filing 3 - ECU metering / verified epistemic work",
            "Filing 4 - Anti-gaming reward invariants",
            "Filing 5 - Agentic function endpoint layer",
        ],
        "physical_delivery_to_uspto_recorded": True,
        "official_uspto_filing_receipts_received": False,
        "official_uspto_application_numbers_received": False,
        "phase_1448a_patent_blocker_status": (
            "delivery_recorded_application_numbers_and_filing_receipts_pending"
        ),
        "public_path_cleared_by_this_record": False,
        "public_rc_authorized_by_this_record": False,
        "legal_opinion_or_counsel_disposition_by_this_record": False,
        "public_path_remains_blocked": True,
    }
    return validate_patent_delivery_status(status)


def validate_patent_delivery_status(status: Mapping[str, Any]) -> dict[str, Any]:
    """Validate a patent-delivery status record."""
    active = dict(status)
    if active.get("version") != PATENT_DELIVERY_STATUS_VERSION:
        raise ValueError("patent_delivery_status_version_invalid_phase_1545p_fix4")
    if active.get("tokens") != list(PATENT_DELIVERY_STATUS_TOKENS):
        raise ValueError("patent_delivery_status_tokens_invalid_phase_1545p_fix4")
    if active.get("tracking_number") != PATENT_DELIVERY_TRACKING_NUMBER:
        raise ValueError("patent_delivery_tracking_number_invalid_phase_1545p_fix4")
    if active.get("actual_delivery_date") != PATENT_DELIVERY_ACTUAL_DELIVERY_DATE:
        raise ValueError("patent_delivery_date_invalid_phase_1545p_fix4")
    if active.get("physical_delivery_to_uspto_recorded") is not True:
        raise ValueError("patent_delivery_not_recorded_phase_1545p_fix4")
    if active.get("official_uspto_filing_receipts_received") is not False:
        raise ValueError("patent_filing_receipts_must_remain_pending_phase_1545p_fix4")
    if active.get("official_uspto_application_numbers_received") is not False:
        raise ValueError("patent_application_numbers_must_remain_pending_phase_1545p_fix4")
    if active.get("public_path_cleared_by_this_record") is not False:
        raise ValueError("patent_delivery_must_not_clear_public_path_phase_1545p_fix4")
    if active.get("public_rc_authorized_by_this_record") is not False:
        raise ValueError("patent_delivery_must_not_authorize_public_rc_phase_1545p_fix4")
    if active.get("legal_opinion_or_counsel_disposition_by_this_record") is not False:
        raise ValueError("patent_delivery_not_legal_opinion_phase_1545p_fix4")
    if active.get("public_path_remains_blocked") is not True:
        raise ValueError("patent_delivery_must_record_public_path_blocked_phase_1545p_fix4")
    canonical_patent_delivery_status_json(active)
    return active


def canonical_patent_delivery_status_json(status: Mapping[str, Any]) -> str:
    """Serialize the status as canonical JSON."""
    return json.dumps(status, allow_nan=False, separators=(",", ":"), sort_keys=True)


__all__ = (
    "PATENT_DELIVERY_STATUS_VERSION",
    "US_PROVISIONAL_PATENT_PACKAGE_DELIVERED_TO_USPTO_PHASE_1545P_FIX4_TOKEN",
    "FIVE_US_PROVISIONAL_PACKETS_DELIVERED_TO_USPTO_PHASE_1545P_FIX4_TOKEN",
    "USPTO_APPLICATION_NUMBERS_PENDING_PHASE_1545P_FIX4_TOKEN",
    "PATENT_FILING_RECEIPTS_PENDING_PHASE_1545P_FIX4_TOKEN",
    "PUBLIC_PATH_NOT_CLEARED_BY_PATENT_DELIVERY_PHASE_1545P_FIX4_TOKEN",
    "PUBLIC_PATH_REMAINS_BLOCKED_PHASE_1545P_FIX4_TOKEN",
    "PATENT_DELIVERY_STATUS_TOKENS",
    "PATENT_DELIVERY_TRACKING_NUMBER",
    "PATENT_DELIVERY_SHIP_DATE",
    "PATENT_DELIVERY_ACTUAL_DELIVERY_DATE",
    "PATENT_DELIVERY_ACTUAL_DELIVERY_TIME_REPORTED",
    "PATENT_DELIVERY_SIGNER_REPORTED",
    "PATENT_DELIVERY_DESTINATION",
    "PATENT_DELIVERY_SERVICE_REPORTED",
    "build_patent_delivery_status",
    "validate_patent_delivery_status",
    "canonical_patent_delivery_status_json",
)
