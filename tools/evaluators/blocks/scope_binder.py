# SPDX-License-Identifier: AGPL-3.0-only
"""Scope Binder — tags each claim with conditions of applicability.

A claim's scope defines the domain, assumptions, and regime in which it is
asserted to hold.  Claims without explicit scope are ambiguously universal —
a common source of drift when repurposing results across contexts (e.g.,
treating a result from a Cobb-Douglas economy as applying to an economy with
AI-as-capital, which violates the diminishing-returns assumption that the
original result depends on).

This block operates on a ClaimRecord (as produced by claim_extractor) and
returns a ScopeRecord: the original claim annotated with scope annotations.

Scope dimensions detected:
  domain          — "economics" | "mathematics" | "computation" | "protocol" |
                    "epistemology" | "empirical" | "legal" | "general"
  regime          — "equilibrium" | "transition" | "limit" | "steady_state" |
                    "discrete" | "continuous" | "unspecified"
  assumptions     — list of assumption strings found in or near the claim text
  universality    — "universal" | "conditional" | "existential" | "scoped"
  scope_explicit  — True if the text contains an explicit scoping marker
  scope_warnings  — list of warning strings for underspecified or risky scopes

Return format (ScopeRecord dict — extends ClaimRecord with scope fields):
    {
        ...ClaimRecord fields...,
        "domain": str,
        "regime": str,
        "assumptions": list[str],
        "universality": str,
        "scope_explicit": bool,
        "scope_warnings": list[str],
    }
"""

from __future__ import annotations

import re
from typing import Any

# ---------------------------------------------------------------------------
# Domain classifiers
# ---------------------------------------------------------------------------

_DOMAIN_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("economics", re.compile(
        r"\b(GDP|output|capital|labor|wage|price|profit|utility|welfare|"
        r"economy|economic|market|firm|household|consumer|producer|"
        r"production function|savings rate|investment|depreciation|"
        r"steady[\s-]state|growth model|Solow|Romer|Ramsey|DSGE|macro)\b",
        re.IGNORECASE,
    )),
    ("mathematics", re.compile(
        r"\b(theorem|lemma|corollary|proof|converges?|diverges?|"
        r"bounded|continuous|differentiable|integral|derivative|"
        r"matrix|vector|eigenvalue|Lagrangian|Hamiltonian|ODE|PDE|"
        r"differential equation|saddle[\s-]path)\b",
        re.IGNORECASE,
    )),
    ("computation", re.compile(
        r"\b(algorithm|runtime|complexity|O\(|polynomial|NP[\s-]hard|"
        r"computable|decidable|halting|hash|cryptographic|blockchain|"
        r"protocol|network|consensus|Byzantine|Byzantine fault)\b",
        re.IGNORECASE,
    )),
    ("protocol", re.compile(
        r"\b(ILC|ECU|CDL|ADR|OBL|epoch|validator|agent|node|truth[\s-]primitive|"
        r"sidecar|graph[\s-]native|star[\s-]map|refutation|claim node|"
        r"descent step|descent trace|jury|quorum|reputation)\b",
        re.IGNORECASE,
    )),
    ("epistemology", re.compile(
        r"\b(knowledge|belief|justification|evidence|falsif|refut|"
        r"conjecture|hypothesis|epistemic|claim|assertion|inference|"
        r"Popperian|Bayesian|posterior|prior|scientific method)\b",
        re.IGNORECASE,
    )),
    ("empirical", re.compile(
        r"\b(data|dataset|regression|estimate|coefficient|standard error|"
        r"p[\s-]value|significance|survey|experiment|observation|"
        r"cross[\s-]country|panel|time series|calibration)\b",
        re.IGNORECASE,
    )),
    ("legal", re.compile(
        r"\b(patent|copyright|license|trademark|claim|infringement|"
        r"prior art|provisional|USPTO|statute|regulation|liability)\b",
        re.IGNORECASE,
    )),
]

# ---------------------------------------------------------------------------
# Regime classifiers
# ---------------------------------------------------------------------------

_REGIME_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("steady_state", re.compile(
        r"\b(steady[\s-]state|balanced growth|long[\s-]run equilibrium|"
        r"stationary)\b",
        re.IGNORECASE,
    )),
    ("equilibrium", re.compile(
        r"\b(equilibrium|market[\s-]clearing|Nash|competitive equilibrium)\b",
        re.IGNORECASE,
    )),
    ("limit", re.compile(
        r"\b(as t\s*→\s*∞|in the limit|asymptotically|t\s*→\s*infinity|"
        r"large[\s-]N|large[\s-]t|goes to infinity)\b",
        re.IGNORECASE,
    )),
    ("transition", re.compile(
        r"\b(transition (path|dynamics)|outside (the )?steady[\s-]state|"
        r"convergence speed|saddle[\s-]path|adjustment path)\b",
        re.IGNORECASE,
    )),
    ("continuous", re.compile(
        r"\b(continuous[\s-]time|differential equation|flow|rate of change)\b",
        re.IGNORECASE,
    )),
    ("discrete", re.compile(
        r"\b(discrete[\s-]time|difference equation|period t|period t\+1)\b",
        re.IGNORECASE,
    )),
]

# ---------------------------------------------------------------------------
# Assumption extractors
# ---------------------------------------------------------------------------

_ASSUMPTION_RE = re.compile(
    r"(?:assuming?|given that|under the assumption that|suppose that|"
    r"provided that|if we assume|conditional on|subject to|"
    r"holding .{0,20} constant|ceteris paribus|all else equal|"
    r"in a (world|model|setting|economy) (where|with|in which))"
    r"(.{0,80}?)(?:[,;.]|\Z)",
    re.IGNORECASE,
)

# Scope markers: words that explicitly delimit applicability
_SCOPE_MARKER_RE = re.compile(
    r"\b(in the (standard|baseline|benchmark|canonical|classical|general|"
    r"special|limiting|simplified) (model|case|setting|economy|version)|"
    r"under (the|a|our|this) (model|assumption|specification|setup)|"
    r"within the (framework|context|scope) of|"
    r"for (small|large|positive|negative|finite|infinite) .{0,30}|"
    r"when .{0,40} (holds?|is satisfied|is assumed)|"
    r"if (and only if|the|a|we) .{0,40})\b",
    re.IGNORECASE,
)

# Universality classifiers
_UNIVERSAL_RE = re.compile(
    r"\b(always|universally|for all|in all cases|"
    r"regardless of|necessarily|inevitably)\b",
    re.IGNORECASE,
)
_CONDITIONAL_RE = re.compile(
    r"\b(if|when|provided|assuming|given|conditional|subject to|"
    r"only if|unless|except when)\b",
    re.IGNORECASE,
)
_EXISTENTIAL_RE = re.compile(
    r"\b(there exists?|there is a|for some|in some cases?|"
    r"under certain|it is possible that)\b",
    re.IGNORECASE,
)

# Risk patterns — scopes that warrant a warning
_HIGH_RISK_SCOPES = [
    (
        re.compile(r"\b(human|labor|worker)s?\b", re.IGNORECASE),
        re.compile(r"\b(AI|artificial intelligence|machine|algorithm|software|robot)s?\b",
                   re.IGNORECASE),
        "scope_risk:human_capital_result_applied_to_AI_capital",
    ),
    (
        re.compile(r"\b(diminishing returns|decreasing returns)\b", re.IGNORECASE),
        None,
        "scope_risk:diminishing_returns_assumption_may_not_hold_for_AI_capital",
    ),
    (
        re.compile(r"\b(finite|bounded|exhaustible)\b", re.IGNORECASE),
        re.compile(r"\b(knowledge|ideas?|information|code|data)\b", re.IGNORECASE),
        "scope_risk:non_rival_good_treated_as_rival",
    ),
]


def _classify_domain(text: str) -> str:
    for domain, pattern in _DOMAIN_PATTERNS:
        if pattern.search(text):
            return domain
    return "general"


def _classify_regime(text: str) -> str:
    for regime, pattern in _REGIME_PATTERNS:
        if pattern.search(text):
            return regime
    return "unspecified"


def _extract_assumptions(text: str) -> list[str]:
    matches = _ASSUMPTION_RE.finditer(text)
    return [m.group(0).strip() for m in matches if m.group(0).strip()]


def _classify_universality(text: str) -> str:
    if _UNIVERSAL_RE.search(text):
        return "universal"
    if _EXISTENTIAL_RE.search(text):
        return "existential"
    if _CONDITIONAL_RE.search(text):
        return "conditional"
    return "scoped"


def _check_scope_warnings(text: str, domain: str, regime: str) -> list[str]:
    warnings: list[str] = []
    for trigger_re, context_re, warning_token in _HIGH_RISK_SCOPES:
        if not trigger_re.search(text):
            continue
        if context_re is None or context_re.search(text):
            warnings.append(warning_token)
    if regime == "unspecified":
        warnings.append("scope_warning:regime_unspecified")
    return warnings


def bind_scope(claim: dict[str, Any]) -> dict[str, Any]:
    """Annotate a ClaimRecord with scope metadata.

    Args:
        claim: A ClaimRecord dict as produced by extract_claims().

    Returns:
        A ScopeRecord dict: the original ClaimRecord extended with scope fields.
        The input dict is not mutated; a new dict is returned.
    """
    text = claim.get("text", "") + " " + claim.get("raw_sentence", "")
    domain = _classify_domain(text)
    regime = _classify_regime(text)
    assumptions = _extract_assumptions(text)
    universality = _classify_universality(text)
    scope_explicit = bool(_SCOPE_MARKER_RE.search(text))
    scope_warnings = _check_scope_warnings(text, domain, regime)

    result = dict(claim)
    result.update({
        "domain": domain,
        "regime": regime,
        "assumptions": assumptions,
        "universality": universality,
        "scope_explicit": scope_explicit,
        "scope_warnings": scope_warnings,
    })
    return result
