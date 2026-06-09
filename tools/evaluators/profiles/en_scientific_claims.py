"""Profile: English Scientific Claims

Generic English-language scientific and technical document profile.
Covers common claim forms, evidence types, and scope markers that appear
across disciplines.  This is the default profile loaded when no explicit
profile is specified.

PUBLIC_RC_EXCLUDE: ilc_decomposition_evaluator_profiles_support_only
"""

from __future__ import annotations

import re

PROFILE_ID = "en_scientific_claims"
LANGUAGE_PROFILE = "en"
DOMAIN_PROFILE = "scientific_technical"
UNSUPPORTED_LANGUAGE_POLICY = "warn"
INPUT_SCHEMA = "plain text or markdown document in English"
OUTPUT_SCHEMA = "scope and evidence annotations per claim"
AUTHORITY_POSTURE = "local_only"

# No additional scope-risk patterns beyond the base blocks for this profile.
# The base blocks already cover: non-rival goods treated as rival,
# diminishing returns assumption, human/AI capital transfer.
SCOPE_RISK_PATTERNS: list = []

# No additional evidence-risk patterns for this profile.
EVIDENCE_RISK_PATTERNS: list = []

# Additional domain patterns merged into scope_binder classification.
# These extend (do not replace) the base block's _DOMAIN_PATTERNS.
DOMAIN_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("biology", re.compile(
        r"\b(cell|gene|protein|enzyme|organism|species|evolution|"
        r"phenotype|genotype|metabol|neural|neuron|synapse|cortex)\b",
        re.IGNORECASE,
    )),
    ("physics", re.compile(
        r"\b(mass|energy|momentum|entropy|thermodynamic|quantum|"
        r"relativity|field|particle|photon|electron|gravity|"
        r"wave function|Hamiltonian)\b",
        re.IGNORECASE,
    )),
    ("statistics", re.compile(
        r"\b(distribution|variance|covariance|confidence interval|"
        r"Bayesian|frequentist|prior|likelihood|posterior|"
        r"hypothesis test|power|Type I|Type II|effect size)\b",
        re.IGNORECASE,
    )),
]
