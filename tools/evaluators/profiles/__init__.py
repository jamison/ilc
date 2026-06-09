"""Domain profiles for the ILC decomposition evaluator.

A profile is a Python module that provides supplementary pattern sets for one
domain or language context. The generic evaluator (ilc_decomposition_evaluator.py)
loads one or more profiles and passes them to the base blocks.

Profile contract:
  PROFILE_ID: str            — unique profile name
  LANGUAGE_PROFILE: str      — "en" | "multilingual" | etc.
  DOMAIN_PROFILE: str        — primary domain label
  UNSUPPORTED_LANGUAGE_POLICY: str — "reject" | "warn" | "passthrough"
  INPUT_SCHEMA: str          — what the profile expects as input
  OUTPUT_SCHEMA: str         — what the profile adds to each claim record
  AUTHORITY_POSTURE: str     — "local_only" | ...

  SCOPE_RISK_PATTERNS: list[tuple[re.Pattern, re.Pattern | None, str]]
    — additional (trigger, amplifier, warning_token) triples merged into
      scope_binder's _HIGH_RISK_SCOPES list

  EVIDENCE_RISK_PATTERNS: list[tuple[re.Pattern, re.Pattern, str]]
    — additional (trigger, amplifier, warning_token) triples

  DOMAIN_PATTERNS: list[tuple[str, re.Pattern]]
    — additional (domain_label, pattern) pairs merged into scope_binder

Available profiles:
  en_scientific_claims      — English scientific/technical documents
  romer_macro_ai_transition — Romer/Solow growth models + AI-capital bridge risks
  ilc_protocol_claims       — ILC protocol specs, ADR/CDL/OBL/runtime claims
"""
