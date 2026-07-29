# SPDX-License-Identifier: AGPL-3.0-only
"""Falsifiability Checker — tests whether a claim has an operational falsification condition.

A claim is falsifiable (in the operational ILC sense) if it contains or implies
a condition under which it would be wrong, and that condition is in principle
observable or decidable.

This is NOT a strict Popperian test — it is a practical test for whether a claim
can participate in the ILC truth-primitive grammar.  In ILC, a claim that cannot
be refuted cannot be meaningfully submitted to a jury, cannot receive a refutation
edge, and cannot accumulate reputation through dispute resolution.

Falsifiability assessment dimensions:
  has_falsification_condition — bool: True if text contains a falsification marker
  falsification_conditions    — list[str]: the extracted conditions
  falsification_type          — "empirical" | "logical" | "protocol" | "none"
  falsification_warnings      — list[str]: warning tokens for unfalsifiable or
                                  problematic claim forms

Claim forms that are structurally unfalsifiable in ILC terms:
  - purely normative claims ("ought to", "should") without a verification test
  - definitional claims (true by construction)
  - claims with no observable prediction and no contradiction condition
  - tautological forms

Return format (FalsifiabilityRecord dict — extends EvidenceRecord with falsifiability fields):
    {
        ...EvidenceRecord fields...,
        "has_falsification_condition": bool,
        "falsification_conditions": list[str],
        "falsification_type": str,
        "falsification_warnings": list[str],
        "ilc_refutable": bool,  # True if the claim can be submitted to ILC jury
        "ilc_refutable_reason": str,
    }
"""

from __future__ import annotations

import re
from typing import Any

# ---------------------------------------------------------------------------
# Falsification condition markers
# ---------------------------------------------------------------------------

# Empirical falsification — an observable prediction that can be checked
_EMPIRICAL_FALSIFICATION_RE = re.compile(
    r"\b(would (fail|be falsified|be wrong|not hold|break down) if|"
    r"fails? when|fails? if|breaks? down (when|if)|does not hold (when|if)|"
    r"unless .{0,60}|except when .{0,60}|"
    r"this (prediction|implication|claim) fails?|"
    r"is inconsistent with|contradicts?|"
    r"empirically (testable|verifiable|falsifiable)|"
    r"we can (test|check|verify|reject) this|"
    r"the null hypothesis|reject(ed)? at|"
    r"(counter)?example:|counterexample|would be (wrong|falsified)|"
    r"can be (falsified|refuted) (if|by|when))\b",
    re.IGNORECASE,
)

# Logical falsification — mathematical contradiction condition
_LOGICAL_FALSIFICATION_RE = re.compile(
    r"\b(proof by contradiction|assume for contradiction|"
    r"if not .{0,40} then|this would require .{0,40} which (is )?impossible|"
    r"cannot be (true|satisfied) if|violates?|"
    r"by contrapositive|the negation of|this fails? when)\b",
    re.IGNORECASE,
)

# Protocol falsification — ILC-specific: refutation edge, jury verdict, truth primitive
_PROTOCOL_FALSIFICATION_RE = re.compile(
    r"\b(refutation (edge|report|node)|truth[\s-]primitive:refute|"
    r"refute\.claim|contradict\.assert|jury (verdict|rejects?)|"
    r"can be (refuted|challenged|disputed) via|"
    r"ILC (refutation|jury|challenge)|descent (step|trace) rejects?)\b",
    re.IGNORECASE,
)

# Condition extractors — what the falsification condition is
_CONDITION_EXTRACTOR_RE = re.compile(
    r"(?:unless?|except when?|would fail if|fails? when?|"
    r"inconsistent with|if not .{0,20}|"
    r"would be wrong if|contradicts?|counterexample:?)\s*(.{0,80}?)(?:[,;.]|\Z)",
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# Unfalsifiability warning patterns
# ---------------------------------------------------------------------------

# Purely normative — "ought to", "should", "must" without verification hook
_NORMATIVE_ONLY_RE = re.compile(
    r"\b(ought to|should|must)\b",
    re.IGNORECASE,
)
# Tautological forms — "X is X", "by definition", "necessarily true"
_TAUTOLOGY_RE = re.compile(
    r"\b(by definition|necessarily (true|the case)|tautologically|"
    r"is trivially true|trivially follows|is obviously true)\b",
    re.IGNORECASE,
)
# Claims about unfalsifiable entities
_UNFALSIFIABLE_ENTITY_RE = re.compile(
    r"\b(God|soul|consciousness|qualia|free will|noumenal)\b",
    re.IGNORECASE,
)
# Universal hedges that prevent falsification
_UNIVERSAL_HEDGE_RE = re.compile(
    r"\b(in some sense|broadly speaking|loosely|to a first approximation|"
    r"one could argue|it could be said)\b",
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# Falsification type classifier
# ---------------------------------------------------------------------------

def _classify_falsification_type(text: str) -> str:
    if _PROTOCOL_FALSIFICATION_RE.search(text):
        return "protocol"
    if _LOGICAL_FALSIFICATION_RE.search(text):
        return "logical"
    if _EMPIRICAL_FALSIFICATION_RE.search(text):
        return "empirical"
    return "none"


def _extract_falsification_conditions(text: str) -> list[str]:
    return [
        m.group(0).strip()
        for m in _CONDITION_EXTRACTOR_RE.finditer(text)
        if m.group(0).strip()
    ]


def _check_falsification_warnings(
    text: str,
    claim_form: str,
    evidence_type: str,
    has_falsification_condition: bool,
) -> list[str]:
    warnings: list[str] = []

    if claim_form == "definitional":
        warnings.append(
            "falsifiability_warning:definitional_claim_structurally_unfalsifiable"
        )
    if _TAUTOLOGY_RE.search(text):
        warnings.append(
            "falsifiability_warning:tautological_form_detected"
        )
    if _UNFALSIFIABLE_ENTITY_RE.search(text):
        warnings.append(
            "falsifiability_warning:claim_about_unfalsifiable_entity"
        )
    if _NORMATIVE_ONLY_RE.search(text) and not has_falsification_condition:
        warnings.append(
            "falsifiability_warning:normative_claim_without_verification_hook"
        )
    if _UNIVERSAL_HEDGE_RE.search(text):
        warnings.append(
            "falsifiability_warning:universal_hedge_prevents_precise_falsification"
        )
    if not has_falsification_condition and evidence_type == "asserted":
        warnings.append(
            "falsifiability_warning:asserted_claim_with_no_falsification_condition"
        )
    return warnings


def _ilc_refutable(
    has_falsification_condition: bool,
    claim_form: str,
    evidence_type: str,
    falsification_type: str,
    warnings: list[str],
) -> tuple[bool, str]:
    """Determine if the claim can meaningfully participate in ILC jury arbitration.

    A claim is ILC-refutable if:
    - It has at least one falsification condition, OR
    - Its form is not purely definitional/tautological, AND
    - It is not blocked by an unfalsifiable entity marker.

    Returns (ilc_refutable: bool, reason: str).
    """
    if any("unfalsifiable_entity" in w for w in warnings):
        return False, "blocked:unfalsifiable_entity"
    if any("tautological" in w for w in warnings):
        return False, "blocked:tautological_form"
    if claim_form == "definitional" and not has_falsification_condition:
        return False, "blocked:definitional_with_no_extension"
    if has_falsification_condition:
        return True, f"refutable_via:{falsification_type}"
    if evidence_type in ("theoretical", "computational", "empirical", "experimental"):
        return True, "refutable_via:evidence_type_implies_testability"
    if claim_form in ("causal", "quantitative", "existence"):
        return True, "refutable_via:claim_form_implies_testability"
    # Normative claims without verification hook are borderline
    if any("normative_claim_without_verification_hook" in w for w in warnings):
        return False, "blocked:normative_without_verification_hook"
    # Default: ambiguous but allow with warning
    return True, "refutable_via:inferred_from_assertion_form"


def check_falsifiability(claim: dict[str, Any]) -> dict[str, Any]:
    """Annotate an EvidenceRecord (or ScopeRecord / ClaimRecord) with
    falsifiability assessment.

    Args:
        claim: An EvidenceRecord, ScopeRecord, or ClaimRecord dict.

    Returns:
        A FalsifiabilityRecord dict: input extended with falsifiability fields.
        The input dict is not mutated; a new dict is returned.
    """
    text = claim.get("text", "") + " " + claim.get("raw_sentence", "")
    claim_form = claim.get("form", "unknown")
    evidence_type = claim.get("evidence_type", "asserted")

    falsification_type = _classify_falsification_type(text)
    has_condition = falsification_type != "none"
    conditions = _extract_falsification_conditions(text) if has_condition else []
    warnings = _check_falsification_warnings(
        text, claim_form, evidence_type, has_condition
    )
    refutable, reason = _ilc_refutable(
        has_condition, claim_form, evidence_type, falsification_type, warnings
    )

    result = dict(claim)
    result.update({
        "has_falsification_condition": has_condition,
        "falsification_conditions": conditions,
        "falsification_type": falsification_type,
        "falsification_warnings": warnings,
        "ilc_refutable": refutable,
        "ilc_refutable_reason": reason,
    })
    return result
