"""Profile: Romer/Solow Macroeconomics + AI-Capital Transition Risks

Domain profile for growth-model economics literature and AI-as-capital
transition analysis.  This profile adds Solow/Romer-specific scope risks and
evidence-bridge patterns that the generic English profile does not cover.

Primary use case: Atlas of Cliffs project — analyzing Romer's Advanced
Macroeconomics for model discontinuities under AI-as-capital.

PUBLIC_RC_EXCLUDE: ilc_decomposition_evaluator_profiles_support_only
"""

from __future__ import annotations

import re

PROFILE_ID = "romer_macro_ai_transition"
LANGUAGE_PROFILE = "en"
DOMAIN_PROFILE = "growth_economics_ai_transition"
UNSUPPORTED_LANGUAGE_POLICY = "reject"
INPUT_SCHEMA = "English economics text (papers, textbook chapters, analysis notes)"
OUTPUT_SCHEMA = (
    "scope annotations with growth-model regime detection; "
    "evidence annotations with AI-capital bridge risk flags"
)
AUTHORITY_POSTURE = "local_only"

# ---------------------------------------------------------------------------
# Scope-risk patterns specific to this profile
# (merged into scope_binder._HIGH_RISK_SCOPES at evaluator load time)
# ---------------------------------------------------------------------------

_RIVAL_GOOD_RE = re.compile(
    r"\b(rival|excludable|physical capital|equipment|machinery|"
    r"plant|land|raw material)\b",
    re.IGNORECASE,
)
_NON_RIVAL_CONTEXT_RE = re.compile(
    r"\b(AI|artificial intelligence|software|code|knowledge|idea|"
    r"algorithm|model|data|information|digital)\b",
    re.IGNORECASE,
)
_AK_MODEL_RE = re.compile(
    r"\b(AK model|constant returns to (capital|scale)|"
    r"endogenous growth|Romer 1990|Aghion|Howitt|"
    r"non[\s-]diminishing|non[\s-]rival)\b",
    re.IGNORECASE,
)
_SOLOW_ASSUMPTION_RE = re.compile(
    r"\b(Solow|neoclassical|Inada condition|convergence|"
    r"steady[\s-]state|balanced growth path|"
    r"diminishing returns to capital|Cobb[\s-]Douglas)\b",
    re.IGNORECASE,
)
_AI_AGENT_RE = re.compile(
    r"\b(AI (agent|worker|system|capital)|artificial (worker|labor|agent)|"
    r"LLM|large language model|GPT|Claude|Gemini)\b",
    re.IGNORECASE,
)
_HUMAN_ANALOG_RE = re.compile(
    r"\b(human (capital|worker|labor)|person[\s-]hour|"
    r"skilled worker|unskilled worker|wage rate)\b",
    re.IGNORECASE,
)

SCOPE_RISK_PATTERNS = [
    # Applying rival-good result to non-rival AI/software capital
    (
        _RIVAL_GOOD_RE,
        _NON_RIVAL_CONTEXT_RE,
        "scope_risk:rival_good_result_applied_to_non_rival_AI_capital",
    ),
    # Solow/neoclassical steady-state result applied where AK model conditions hold
    (
        _SOLOW_ASSUMPTION_RE,
        _AK_MODEL_RE,
        "scope_risk:neoclassical_convergence_result_may_not_hold_in_AK_regime",
    ),
    # Human-labor result applied to AI agents
    (
        _HUMAN_ANALOG_RE,
        _AI_AGENT_RE,
        "scope_risk:human_labor_result_applied_to_AI_agent",
    ),
    # AK/endogenous growth result applied without non-rival assumption check
    (
        _AK_MODEL_RE,
        re.compile(r"\b(finite|bounded|diminishing)\b", re.IGNORECASE),
        "scope_risk:AK_model_applied_in_context_assuming_diminishing_returns",
    ),
]

# ---------------------------------------------------------------------------
# Evidence-risk patterns specific to this profile
# ---------------------------------------------------------------------------

_CALIBRATION_RE = re.compile(
    r"\b(calibrated? to|calibration|calibrated? (for|against)|"
    r"model match(es)? (data|moments)|moments match)\b",
    re.IGNORECASE,
)
_UNIVERSAL_CLAIM_RE = re.compile(
    r"\b(always|universally|for all (economies|countries|models)|"
    r"in any economy|across all|regardless of)\b",
    re.IGNORECASE,
)
_MACRO_REGRESSION_RE = re.compile(
    r"\b(cross[\s-]country (regression|evidence|data)|"
    r"panel (regression|data)|time[\s-]series evidence|"
    r"OLS|IV (regression|estimate)|GMM)\b",
    re.IGNORECASE,
)
_MICRO_TO_MACRO_RE = re.compile(
    r"\b(individual (firm|agent|worker)|micro[\s-]level|"
    r"partial equilibrium|single (firm|sector))\b",
    re.IGNORECASE,
)
_AGGREGATE_CLAIM_RE = re.compile(
    r"\b(aggregate|economy[\s-]wide|macroeconomic|GDP|"
    r"national income|general equilibrium)\b",
    re.IGNORECASE,
)

EVIDENCE_RISK_PATTERNS = [
    # Calibration result stated as universal
    (
        _CALIBRATION_RE,
        _UNIVERSAL_CLAIM_RE,
        "evidence_risk:calibration_result_overgeneralized_to_universal_claim",
    ),
    # Micro-level evidence applied to aggregate claim
    (
        _MICRO_TO_MACRO_RE,
        _AGGREGATE_CLAIM_RE,
        "evidence_risk:micro_level_evidence_applied_to_macro_aggregate_claim",
    ),
    # Cross-country regression applied to specific-country prediction
    (
        _MACRO_REGRESSION_RE,
        re.compile(r"\b(this country|the US|the EU|China|specific)\b", re.IGNORECASE),
        "evidence_risk:cross_country_average_applied_to_specific_country",
    ),
]

# ---------------------------------------------------------------------------
# Additional domain patterns
# ---------------------------------------------------------------------------

DOMAIN_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("growth_economics", re.compile(
        r"\b(Solow|Romer|endogenous growth|AK model|balanced growth path|"
        r"Ramsey[\s-]Cass|Koopmans|Aghion|Howitt|Schumpeterian|"
        r"total factor productivity|TFP|human capital accumulation|"
        r"savings rate|depreciation rate|capital[\s-]output ratio)\b",
        re.IGNORECASE,
    )),
    ("ai_economics", re.compile(
        r"\b(AI capital|artificial intelligence (as|and) (capital|labor|factor)|"
        r"automation|task[\s-]based model|Acemoglu|Autor|"
        r"routine[\s-]biased|skill[\s-]biased|labor[\s-]augmenting AI|"
        r"capital[\s-]augmenting AI|intelligence[\s-]per[\s-]token|"
        r"epistemic compute|ECU)\b",
        re.IGNORECASE,
    )),
]
