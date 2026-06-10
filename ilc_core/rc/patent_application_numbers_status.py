# SPDX-License-Identifier: AGPL-3.0-only
"""US provisional patent application numbers evidence addendum.

PUBLIC_RC_EXCLUDE: patent_application_numbers_internal_record
PUBLIC_RC_EXCLUDE_REASON: Internal USPTO verbal-confirmation evidence addendum.
Verbal phone confirmation only; official written filing receipts still pending.
Not a filing receipt, legal opinion, public-RC authorization, or mutation of
the patent_delivery_status.py historical record.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any


PATENT_APPLICATION_NUMBERS_STATUS_VERSION = (
    "us_provisional_patent_application_numbers_status_2026_06_10.v0.1"
)

US_PROVISIONAL_PATENT_APPLICATION_NUMBERS_RECEIVED_VERBAL_2026_06_10_TOKEN = (
    "us_provisional_patent_application_numbers_received_verbal_2026_06_10"
)
FIVE_PROVISIONAL_APPLICATION_NUMBERS_RECEIVED_2026_06_10_TOKEN = (
    "five_provisional_application_numbers_received_2026_06_10"
)
OFFICIAL_WRITTEN_FILING_RECEIPTS_STILL_PENDING_2026_06_10_TOKEN = (
    "official_written_filing_receipts_still_pending_2026_06_10"
)
PATENT_GATE_UPGRADED_FROM_DELIVERY_ONLY_TO_APPLICATION_NUMBER_CONFIRMED_TOKEN = (
    "patent_gate_upgraded_from_delivery_only_to_application_number_confirmed"
)
PUBLIC_PATH_REMAINS_BLOCKED_PATENT_APPLICATION_NUMBERS_ADDENDUM_TOKEN = (
    "public_path_remains_blocked_patent_application_numbers_addendum"
)

PATENT_APPLICATION_NUMBERS_STATUS_TOKENS: tuple[str, ...] = (
    US_PROVISIONAL_PATENT_APPLICATION_NUMBERS_RECEIVED_VERBAL_2026_06_10_TOKEN,
    FIVE_PROVISIONAL_APPLICATION_NUMBERS_RECEIVED_2026_06_10_TOKEN,
    OFFICIAL_WRITTEN_FILING_RECEIPTS_STILL_PENDING_2026_06_10_TOKEN,
    PATENT_GATE_UPGRADED_FROM_DELIVERY_ONLY_TO_APPLICATION_NUMBER_CONFIRMED_TOKEN,
    PUBLIC_PATH_REMAINS_BLOCKED_PATENT_APPLICATION_NUMBERS_ADDENDUM_TOKEN,
)

# Application numbers received verbally via USPTO phone call, 2026-06-10.
# Format: US provisional application numbers (64/XXX,XXX series).
PATENT_APPLICATION_NUMBERS: dict[str, str] = {
    "Filing 1 - Merkle-Laplacian dual commitment": "64/231,844",
    "Filing 2 - Truth-primitive state machine": "64/231,845",
    "Filing 3 - ECU metering / verified epistemic work": "64/231,846",
    "Filing 4 - Anti-gaming reward invariants": "64/231,847",
    "Filing 5 - Agentic function endpoint layer": "64/231,848",
}

PATENT_APPLICATION_NUMBERS_RECEIPT_METHOD = "verbal_phone_confirmation_from_uspto_2026_06_10"
PATENT_APPLICATION_NUMBERS_DATE_RECEIVED = "2026-06-10"
PATENT_APPLICATION_NUMBERS_COUNT = 5

# Addendum to (not a modification of) the Fix4 delivery status module.
ADDENDUM_TO_MODULE = "ilc_core/rc/patent_delivery_status.py"
ADDENDUM_TO_EVIDENCE_DOC = (
    "docs/specs/ilc_us_provisional_patent_delivery_receipt_1545p_fix4_v0.1.md"
)


def build_patent_application_numbers_status() -> dict[str, Any]:
    """Return the current internal patent application-numbers evidence record."""
    status = {
        "version": PATENT_APPLICATION_NUMBERS_STATUS_VERSION,
        "tokens": list(PATENT_APPLICATION_NUMBERS_STATUS_TOKENS),
        "application_numbers": PATENT_APPLICATION_NUMBERS,
        "application_numbers_count": PATENT_APPLICATION_NUMBERS_COUNT,
        "receipt_method": PATENT_APPLICATION_NUMBERS_RECEIPT_METHOD,
        "date_received": PATENT_APPLICATION_NUMBERS_DATE_RECEIVED,
        "addendum_to_module": ADDENDUM_TO_MODULE,
        "addendum_to_evidence_doc": ADDENDUM_TO_EVIDENCE_DOC,
        "official_written_filing_receipts_received": False,
        "patent_gate_status": (
            "application_numbers_confirmed_verbally_filing_receipts_pending"
        ),
        "fix4_delivery_module_modified": False,
        "public_path_cleared_by_this_record": False,
        "public_rc_authorized_by_this_record": False,
        "legal_opinion_or_counsel_disposition_by_this_record": False,
        "public_path_remains_blocked": True,
    }
    return validate_patent_application_numbers_status(status)


def validate_patent_application_numbers_status(
    status: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate a patent application-numbers status record."""
    active = dict(status)
    if active.get("version") != PATENT_APPLICATION_NUMBERS_STATUS_VERSION:
        raise ValueError(
            "patent_application_numbers_status_version_invalid_2026_06_10"
        )
    if active.get("tokens") != list(PATENT_APPLICATION_NUMBERS_STATUS_TOKENS):
        raise ValueError(
            "patent_application_numbers_status_tokens_invalid_2026_06_10"
        )
    if active.get("application_numbers") != PATENT_APPLICATION_NUMBERS:
        raise ValueError(
            "patent_application_numbers_invalid_2026_06_10"
        )
    if active.get("application_numbers_count") != PATENT_APPLICATION_NUMBERS_COUNT:
        raise ValueError(
            "patent_application_numbers_count_invalid_2026_06_10"
        )
    if active.get("official_written_filing_receipts_received") is not False:
        raise ValueError(
            "patent_filing_receipts_must_remain_pending_application_numbers_addendum"
        )
    if active.get("fix4_delivery_module_modified") is not False:
        raise ValueError(
            "fix4_delivery_module_must_not_be_modified_by_application_numbers_addendum"
        )
    if active.get("public_path_cleared_by_this_record") is not False:
        raise ValueError(
            "application_numbers_addendum_must_not_clear_public_path"
        )
    if active.get("public_rc_authorized_by_this_record") is not False:
        raise ValueError(
            "application_numbers_addendum_must_not_authorize_public_rc"
        )
    if active.get("legal_opinion_or_counsel_disposition_by_this_record") is not False:
        raise ValueError(
            "application_numbers_addendum_not_legal_opinion"
        )
    if active.get("public_path_remains_blocked") is not True:
        raise ValueError(
            "application_numbers_addendum_must_record_public_path_blocked"
        )
    canonical_patent_application_numbers_status_json(active)
    return active


def canonical_patent_application_numbers_status_json(
    status: Mapping[str, Any],
) -> str:
    """Serialize the status as canonical JSON."""
    return json.dumps(status, allow_nan=False, separators=(",", ":"), sort_keys=True)


__all__ = (
    "PATENT_APPLICATION_NUMBERS_STATUS_VERSION",
    "US_PROVISIONAL_PATENT_APPLICATION_NUMBERS_RECEIVED_VERBAL_2026_06_10_TOKEN",
    "FIVE_PROVISIONAL_APPLICATION_NUMBERS_RECEIVED_2026_06_10_TOKEN",
    "OFFICIAL_WRITTEN_FILING_RECEIPTS_STILL_PENDING_2026_06_10_TOKEN",
    "PATENT_GATE_UPGRADED_FROM_DELIVERY_ONLY_TO_APPLICATION_NUMBER_CONFIRMED_TOKEN",
    "PUBLIC_PATH_REMAINS_BLOCKED_PATENT_APPLICATION_NUMBERS_ADDENDUM_TOKEN",
    "PATENT_APPLICATION_NUMBERS_STATUS_TOKENS",
    "PATENT_APPLICATION_NUMBERS",
    "PATENT_APPLICATION_NUMBERS_RECEIPT_METHOD",
    "PATENT_APPLICATION_NUMBERS_DATE_RECEIVED",
    "PATENT_APPLICATION_NUMBERS_COUNT",
    "ADDENDUM_TO_MODULE",
    "ADDENDUM_TO_EVIDENCE_DOC",
    "build_patent_application_numbers_status",
    "validate_patent_application_numbers_status",
    "canonical_patent_application_numbers_status_json",
)
