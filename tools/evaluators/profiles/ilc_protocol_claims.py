"""Profile: ILC Protocol Claims

Domain profile for ILC protocol specifications, ADR/CDL/OBL documents,
runtime module claims, and phase prompts.  Adds protocol-native scope risks
and evidence-bridge patterns.

PRIMARY USE: Evaluating ILC specs, architecture docs, CDL deliberation
claims, and phase prompts for internal epistemic quality.

PUBLIC_RC_EXCLUDE: ilc_decomposition_evaluator_profiles_support_only
"""

from __future__ import annotations

import re

PROFILE_ID = "ilc_protocol_claims"
LANGUAGE_PROFILE = "en"
DOMAIN_PROFILE = "ilc_protocol"
UNSUPPORTED_LANGUAGE_POLICY = "reject"
INPUT_SCHEMA = "ILC protocol spec, ADR, CDL, OBL, or phase prompt (markdown)"
OUTPUT_SCHEMA = (
    "scope annotations with protocol-layer detection; "
    "evidence annotations with pre-canon/post-canon and overclaim flags"
)
AUTHORITY_POSTURE = "local_only"

# ---------------------------------------------------------------------------
# Scope-risk patterns specific to ILC protocol claims
# ---------------------------------------------------------------------------

_PRE_CANON_RE = re.compile(
    r"\b(pre[\s-]canon|not yet ratified|deferred|in one embodiment|"
    r"direction accepted|pending CDL|pending ADR|proposed|forward planning|"
    r"candidate|draft spec|not yet committed)\b",
    re.IGNORECASE,
)
_RATIFIED_CLAIM_RE = re.compile(
    r"\b(is ratified|ratified law|is constitutional|is binding|"
    r"is runtime law|is in force|is activated|is production|"
    r"governs|constitutionally requires)\b",
    re.IGNORECASE,
)
_DEFAULT_OFF_RE = re.compile(
    r"\b(NOT_ACTIVATED|default[\s-]off|guard (is|remains) True|"
    r"production.*not.*activated|activation guard)\b",
    re.IGNORECASE,
)
_PRODUCTION_CLAIM_RE = re.compile(
    r"\b(is (live|active|running|deployed|in production)|"
    r"production (runtime|minting|settlement|emission)|"
    r"epoch 1|live network|mainnet)\b",
    re.IGNORECASE,
)
_SIDECAR_RE = re.compile(
    r"\b(sidecar|L3 app|app[\s-]plane|IPC boundary|"
    r"harness adapter|external consumer)\b",
    re.IGNORECASE,
)
_CORE_CLAIM_RE = re.compile(
    r"\b(ilc_core|core runtime|L0|L1 core|graph store|"
    r"canonical (graph|ledger|state)|protocol[\s-]native)\b",
    re.IGNORECASE,
)

SCOPE_RISK_PATTERNS = [
    # Pre-canon item described as ratified
    (
        _PRE_CANON_RE,
        _RATIFIED_CLAIM_RE,
        "scope_risk:pre_canon_item_described_as_ratified",
    ),
    # Default-off guard described as active/production
    (
        _DEFAULT_OFF_RE,
        _PRODUCTION_CLAIM_RE,
        "scope_risk:default_off_guard_described_as_production_active",
    ),
    # Sidecar behavior claimed as core runtime behavior
    (
        _SIDECAR_RE,
        _CORE_CLAIM_RE,
        "scope_risk:sidecar_behavior_claimed_as_core_runtime",
    ),
]

# ---------------------------------------------------------------------------
# Evidence-risk patterns specific to ILC protocol claims
# ---------------------------------------------------------------------------

_ASSERTION_ONLY_RE = re.compile(
    r"\b(is designed to|is intended to|should|will (eventually|later)|"
    r"is planned to|we intend|the goal is)\b",
    re.IGNORECASE,
)
_RUNTIME_CLAIM_RE = re.compile(
    r"\b(implements?|is implemented|runtime (does|handles?|enforces?)|"
    r"the code (does|handles?|enforces?|checks?)|"
    r"at runtime|enforced by|validated by)\b",
    re.IGNORECASE,
)
_SIMULATION_RE = re.compile(
    r"\b(SIM[\s-]\w+|simulation (shows?|result|evidence)|"
    r"simulated|synthetic (agent|network|topology)|"
    r"advisory|SIM verdict)\b",
    re.IGNORECASE,
)
_LIVE_NETWORK_RE = re.compile(
    r"\b(live network|real (operator|peer|network)|"
    r"observed (in|from) (production|mainnet|live)|"
    r"epoch \d+ data|real topology)\b",
    re.IGNORECASE,
)

EVIDENCE_RISK_PATTERNS = [
    # Design-intent claim stated as implementation fact
    (
        _ASSERTION_ONLY_RE,
        _RUNTIME_CLAIM_RE,
        "evidence_risk:design_intent_stated_as_implementation_fact",
    ),
    # Simulation result applied as live network evidence
    (
        _SIMULATION_RE,
        _LIVE_NETWORK_RE,
        "evidence_risk:simulation_advisory_overgeneralized_to_live_network_fact",
    ),
]

# ---------------------------------------------------------------------------
# Additional domain patterns for ILC protocol layer detection
# ---------------------------------------------------------------------------

DOMAIN_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("ilc_governance", re.compile(
        r"\b(CDL|ADR|OBL|truth[\s-]primitive|jury|quorum|epoch|"
        r"reputation|sybil|refutation|claim node|star[\s-]map|"
        r"genesis authority|validator|agent identity|ECU|ILC|"
        r"peer[\s-]funded|bounty|treasury|Werner|flow[\s-]governor)\b",
        re.IGNORECASE,
    )),
    ("ilc_runtime", re.compile(
        r"\b(ilc_core|NOT_ACTIVATED|guard|default[\s-]off|"
        r"production emission|epoch transition|signing ceremony|"
        r"hash anchor|canonical JSON|Decimal|sort_keys)\b",
        re.IGNORECASE,
    )),
]
