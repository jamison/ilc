"""Evidence Classifier — labels the evidence type backing each claim.

A claim's epistemic strength depends on the type of evidence that supports
or could support it.  This block inspects a ScopeRecord (or ClaimRecord) and
attaches an evidence classification.

Evidence types (in order of typical epistemic strength in ILC terms):
  experimental      — claim is backed by or calls for a controlled experiment
  empirical         — claim is backed by real-world data / statistical estimation
  computational     — claim is backed by simulation, calibration, or algorithmic proof
  theoretical       — claim is backed by mathematical derivation / formal proof
  descriptive       — claim describes a pattern or mechanism without a test condition
  definitional      — claim is true by definition (not empirically testable)
  asserted          — claim has no explicit backing; author asserts without evidence

This block also identifies evidence-strength warnings:
  - theoretical result used as empirical prediction without a bridge
  - simulation result generalized beyond its parameter range
  - definitional claim repurposed as a causal claim
  - empirical result from one domain applied to another

Return format (EvidenceRecord dict — extends ScopeRecord with evidence fields):
    {
        ...ScopeRecord fields...,
        "evidence_type": str,         # one of the types above
        "evidence_markers": list[str], # phrases that triggered the classification
        "evidence_warnings": list[str],# warning tokens
        "cites_source": bool,         # True if text contains a citation pattern
    }
"""

from __future__ import annotations

import re
from typing import Any

# ---------------------------------------------------------------------------
# Evidence type patterns
# ---------------------------------------------------------------------------

_EVIDENCE_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    # Experimental evidence — controlled intervention
    ("experimental", re.compile(
        r"\b(randomized|controlled (trial|experiment)|RCT|treatment (group|effect)|"
        r"placebo|A/B test|exogenous (variation|shock)|instrumental variable|"
        r"difference[\s-]in[\s-]differences|natural experiment|quasi[\s-]experimental)\b",
        re.IGNORECASE,
    )),
    # Empirical — real data, estimation
    ("empirical", re.compile(
        r"\b(data show|empirically|estimate|coefficient|regression|"
        r"cross[\s-]country evidence|survey data|time[\s-]series|panel data|"
        r"calibrate(d)? to|consistent with (the )?data|"
        r"as observed|in practice|historically)\b",
        re.IGNORECASE,
    )),
    # Theoretical — formal derivation, mathematical proof (before computational:
    # "we prove/show/derive" is a stronger signal than simulation vocabulary)
    ("theoretical", re.compile(
        r"\b(we (prove|show|derive|can show|can verify)|"
        r"it (follows|can be shown) that|theorem|lemma|corollary|QED|"
        r"by (induction|contradiction|construction)|"
        r"follows from|can be derived|formally|analytically)\b",
        re.IGNORECASE,
    )),
    # Computational — simulation, benchmark, algorithm proof
    ("computational", re.compile(
        r"\b(simulation shows?|simulated|benchmark(ed)?|numerically?|"
        r"algorithm (produces?|guarantees?)|runtime is|"
        r"in the (model|simulation)|we (run|solve|simulate)|"
        r"by construction|Lyapunov|fixed[\s-]point iteration)\b",
        re.IGNORECASE,
    )),
    # Descriptive — explanation without test condition
    ("descriptive", re.compile(
        r"\b(typically|generally|in general|is characterized by|"
        r"tends? to|often|usually|commonly|frequently)\b",
        re.IGNORECASE,
    )),
    # Definitional — true by definition
    ("definitional", re.compile(
        r"\b(by definition|we define|is defined as|denote by|"
        r"let .{1,30} be|notation:|convention:)\b",
        re.IGNORECASE,
    )),
]

# Citation pattern (author-year, footnote, bracket)
_CITATION_RE = re.compile(
    r"(\([A-Z][a-z]+(?:,\s*\d{4})?(?:\s*et al\.?)?\)|"  # (Author, YYYY) or (Author et al.)
    r"\[\d+\]|"                                             # [N]
    r"(?:see|cf\.?|as in|following|shown by|by)\s+[A-Z][a-z]+\s*\(\d{4}\)|"  # see/by Author (YYYY)
    r"[A-Z][a-z]+\s*\(\d{4}\))",  # bare Author (YYYY)
    re.IGNORECASE,
)

# Evidence-bridge risk patterns
_BRIDGE_RISKS: list[tuple[re.Pattern[str], re.Pattern[str], str]] = [
    # Theoretical result stated as an empirical prediction
    (
        re.compile(r"\b(theorem|lemma|we (prove|can show))\b", re.IGNORECASE),
        re.compile(r"\b(in practice|empirically|in (the|real) (world|economy))\b",
                   re.IGNORECASE),
        "evidence_risk:theoretical_result_stated_as_empirical_prediction",
    ),
    # Simulation/calibration result generalized universally
    (
        re.compile(r"\b(simulation|calibrated|in the model)\b", re.IGNORECASE),
        re.compile(r"\b(always|universally|for all (economies|agents|cases))\b",
                   re.IGNORECASE),
        "evidence_risk:simulation_result_overgeneralized",
    ),
    # Definitional claim repurposed as causal
    (
        re.compile(r"\b(by definition|we define|is defined as)\b", re.IGNORECASE),
        re.compile(r"\b(causes?|leads? to|results? in|drives?)\b", re.IGNORECASE),
        "evidence_risk:definitional_claim_repurposed_as_causal",
    ),
]

# AI-capital specific risk: result from human-labor economy applied to AI
_AI_CAPITAL_RE = re.compile(
    r"\b(AI|artificial intelligence|machine|algorithm|software|compute)\b",
    re.IGNORECASE,
)
_HUMAN_LABOR_RESULT_RE = re.compile(
    r"\b(labor[\s-]augmenting|human capital|worker|person[\s-]hour|"
    r"diminishing returns to (labor|capital))\b",
    re.IGNORECASE,
)


def _classify_evidence(text: str) -> tuple[str, list[str]]:
    """Return (evidence_type, [marker_strings]) — first match wins."""
    for evidence_type, pattern in _EVIDENCE_PATTERNS:
        matches = pattern.findall(text)
        if matches:
            # Flatten to strings
            markers = [m if isinstance(m, str) else " ".join(m) for m in matches]
            return evidence_type, markers
    return "asserted", []


def _check_evidence_warnings(text: str, evidence_type: str) -> list[str]:
    warnings: list[str] = []
    for trigger_re, amplifier_re, warning_token in _BRIDGE_RISKS:
        if trigger_re.search(text) and amplifier_re.search(text):
            warnings.append(warning_token)
    if _AI_CAPITAL_RE.search(text) and _HUMAN_LABOR_RESULT_RE.search(text):
        warnings.append(
            "evidence_risk:human_labor_result_applied_to_AI_capital_context"
        )
    return warnings


def classify_evidence(claim: dict[str, Any]) -> dict[str, Any]:
    """Annotate a ScopeRecord (or ClaimRecord) with evidence classification.

    Args:
        claim: A ScopeRecord or ClaimRecord dict.

    Returns:
        An EvidenceRecord dict: input extended with evidence fields.
        The input dict is not mutated; a new dict is returned.
    """
    text = claim.get("text", "") + " " + claim.get("raw_sentence", "")
    evidence_type, markers = _classify_evidence(text)
    evidence_warnings = _check_evidence_warnings(text, evidence_type)
    cites_source = bool(_CITATION_RE.search(text))

    result = dict(claim)
    result.update({
        "evidence_type": evidence_type,
        "evidence_markers": markers,
        "evidence_warnings": evidence_warnings,
        "cites_source": cites_source,
    })
    return result
