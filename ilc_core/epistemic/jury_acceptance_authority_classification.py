# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 1568-Fix2u jury acceptance authority classification.

This module names the current acceptance-authority surfaces. It is deliberately
classification-only: it does not empanel juries, evaluate finality, authorize
settlement, or clear any production guard.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final, Mapping

JURY_ACCEPTANCE_AUTHORITY_CLASSIFICATION_VERSION: Final[str] = (
    "jury_acceptance_authority_classification_phase_1568_fix2u.v0.1"
)
JURY_ACCEPTANCE_AUTHORITY_CLASSIFICATION_NOT_EXECUTION: Final[bool] = True

PANEL_PROXY_ACCEPTANCE: Final[str] = "panel_proxy_acceptance"
LOCAL_JURY_FINALITY_NONPRODUCTION: Final[str] = "local_jury_finality_nonproduction"
PRODUCTION_ASSIGNMENT_QUOTE_ACTIVE: Final[str] = "production_assignment_quote_active"
PRODUCTION_JURY_FINALITY_NOT_PROVEN: Final[str] = "production_jury_finality_not_proven"
SHARD_TIER_RATIFIED_NOT_ACTIVATED: Final[str] = "shard_tier_ratified_not_activated"
GLOBAL_TIER_DEFERRED_TO_CDL_096: Final[str] = "global_tier_deferred_to_cdl_096"

JURY_ACCEPTANCE_AUTHORITY_LABELS: Final[tuple[str, ...]] = (
    PANEL_PROXY_ACCEPTANCE,
    LOCAL_JURY_FINALITY_NONPRODUCTION,
    PRODUCTION_ASSIGNMENT_QUOTE_ACTIVE,
    PRODUCTION_JURY_FINALITY_NOT_PROVEN,
    SHARD_TIER_RATIFIED_NOT_ACTIVATED,
    GLOBAL_TIER_DEFERRED_TO_CDL_096,
)

JURY_ACCEPTANCE_AUTHORITY_UNCLASSIFIED_TOKEN: Final[str] = (
    "jury_acceptance_authority_unclassified_phase_1568_fix2u"
)
JURY_ACCEPTANCE_AUTHORITY_LABEL_MISMATCH_TOKEN: Final[str] = (
    "jury_acceptance_authority_label_mismatch_phase_1568_fix2u"
)
JURY_ACCEPTANCE_AUTHORITY_POSITIVE_CLAIM_BLOCKED_TOKEN: Final[str] = (
    "jury_acceptance_authority_positive_claim_blocked_phase_1568_fix2u"
)
JURY_ACCEPTANCE_AUTHORITY_PRODUCTION_CLAIM_BLOCKED_TOKEN: Final[str] = (
    "jury_acceptance_authority_production_claim_blocked_phase_1568_fix2u"
)
JURY_ACCEPTANCE_AUTHORITY_MANIFEST_INVALID_TOKEN: Final[str] = (
    "jury_acceptance_authority_manifest_invalid_phase_1568_fix2u"
)


@dataclass(frozen=True)
class JuryAcceptanceAuthorityClassification:
    lane: str
    panel_type: str
    guard_state: str
    label: str
    positive_acceptance_allowed: bool
    production_grade_acceptance: bool
    explanation: str


_CLASSIFICATION_ROWS: Final[tuple[JuryAcceptanceAuthorityClassification, ...]] = (
    JuryAcceptanceAuthorityClassification(
        lane="agent_loop",
        panel_type="panel_proxy",
        guard_state="panel_proxy_nonproduction",
        label=PANEL_PROXY_ACCEPTANCE,
        positive_acceptance_allowed=True,
        production_grade_acceptance=False,
        explanation="Agent-loop panel proxy can support rehearsal accepted-work lineage, not production jury finality.",
    ),
    JuryAcceptanceAuthorityClassification(
        lane="local_jury",
        panel_type="cdl095_regular_panel",
        guard_state="jury_finality_evaluator_not_production",
        label=LOCAL_JURY_FINALITY_NONPRODUCTION,
        positive_acceptance_allowed=True,
        production_grade_acceptance=False,
        explanation="CDL-095 local finality exists behind the non-production evaluator guard.",
    ),
    JuryAcceptanceAuthorityClassification(
        lane="production_assignment",
        panel_type="cdl095_7_plus_1_assignment_quote",
        guard_state="production_assignment_activated_phase_1429_quote_only",
        label=PRODUCTION_ASSIGNMENT_QUOTE_ACTIVE,
        positive_acceptance_allowed=False,
        production_grade_acceptance=False,
        explanation="Phase 1429 activated assignment quote/execution machinery, not production jury finality.",
    ),
    JuryAcceptanceAuthorityClassification(
        lane="production_jury",
        panel_type="cdl095_regular_panel",
        guard_state="production_jury_finality_not_proven",
        label=PRODUCTION_JURY_FINALITY_NOT_PROVEN,
        positive_acceptance_allowed=False,
        production_grade_acceptance=False,
        explanation="No current runtime proves production-grade jury finality.",
    ),
    JuryAcceptanceAuthorityClassification(
        lane="shard_tier",
        panel_type="cdl095_shard_tier_panel",
        guard_state="ratified_not_activated",
        label=SHARD_TIER_RATIFIED_NOT_ACTIVATED,
        positive_acceptance_allowed=False,
        production_grade_acceptance=False,
        explanation="CDL-095 ratified shard-tier architecture but left activation deferred.",
    ),
    JuryAcceptanceAuthorityClassification(
        lane="global_tier",
        panel_type="cdl095_global_review_tier",
        guard_state="deferred_to_cdl_096",
        label=GLOBAL_TIER_DEFERRED_TO_CDL_096,
        positive_acceptance_allowed=False,
        production_grade_acceptance=False,
        explanation="CDL-095 deferred global-tier design and activation to CDL-096.",
    ),
)

_CLASSIFICATION_BY_KEY: Final[dict[tuple[str, str, str], JuryAcceptanceAuthorityClassification]] = {
    (row.lane, row.panel_type, row.guard_state): row for row in _CLASSIFICATION_ROWS
}


def acceptance_authority_table() -> tuple[JuryAcceptanceAuthorityClassification, ...]:
    return _CLASSIFICATION_ROWS


def classify_acceptance_authority(
    *,
    lane: str,
    panel_type: str,
    guard_state: str,
) -> JuryAcceptanceAuthorityClassification:
    if not all(isinstance(value, str) and value for value in (lane, panel_type, guard_state)):
        raise ValueError(JURY_ACCEPTANCE_AUTHORITY_UNCLASSIFIED_TOKEN)
    key = (lane, panel_type, guard_state)
    try:
        return _CLASSIFICATION_BY_KEY[key]
    except KeyError as exc:
        raise ValueError(
            f"{JURY_ACCEPTANCE_AUTHORITY_UNCLASSIFIED_TOKEN}:"
            f"lane={lane}:panel_type={panel_type}:guard_state={guard_state}"
        ) from exc


def validate_manifest_acceptance_authority(
    manifest: Mapping[str, Any],
) -> JuryAcceptanceAuthorityClassification:
    try:
        label = manifest["acceptance_authority_label"]
        lane = manifest["acceptance_authority_lane"]
        panel_type = manifest["acceptance_authority_panel_type"]
        guard_state = manifest["acceptance_authority_guard_state"]
    except KeyError as exc:
        raise ValueError(f"{JURY_ACCEPTANCE_AUTHORITY_MANIFEST_INVALID_TOKEN}:missing={exc.args[0]}") from exc

    classification = classify_acceptance_authority(
        lane=lane,
        panel_type=panel_type,
        guard_state=guard_state,
    )
    if label != classification.label:
        raise ValueError(
            f"{JURY_ACCEPTANCE_AUTHORITY_LABEL_MISMATCH_TOKEN}:"
            f"expected={classification.label}:actual={label}"
        )

    positive_claim = manifest.get("acceptance_authority_positive_acceptance_claim", False)
    if not isinstance(positive_claim, bool):
        raise ValueError(
            f"{JURY_ACCEPTANCE_AUTHORITY_MANIFEST_INVALID_TOKEN}:"
            "acceptance_authority_positive_acceptance_claim_not_bool"
        )
    if positive_claim and not classification.positive_acceptance_allowed:
        raise ValueError(
            f"{JURY_ACCEPTANCE_AUTHORITY_POSITIVE_CLAIM_BLOCKED_TOKEN}:"
            f"label={classification.label}"
        )

    production_claim = manifest.get("acceptance_authority_production_grade_claim", False)
    if not isinstance(production_claim, bool):
        raise ValueError(
            f"{JURY_ACCEPTANCE_AUTHORITY_MANIFEST_INVALID_TOKEN}:"
            "acceptance_authority_production_grade_claim_not_bool"
        )
    if production_claim and not classification.production_grade_acceptance:
        raise ValueError(
            f"{JURY_ACCEPTANCE_AUTHORITY_PRODUCTION_CLAIM_BLOCKED_TOKEN}:"
            f"label={classification.label}"
        )

    return classification
