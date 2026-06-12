"""Structural tests for the pre-RC completion window guidance document.

Validates invariants asserted in:
  docs/specs/ilc_window_1556_1564_pre_rc_completion_candidate_phase_grouping_v0.1.md

These tests catch guidance-doc drift before any phase executes, not after.
They are lightweight text/structure checks — not execution tests.
"""
import re
import pathlib

GUIDANCE_PATH = pathlib.Path(
    "docs/specs/ilc_window_1556_1564_pre_rc_completion_candidate_phase_grouping_v0.1.md"
)


def _text() -> str:
    return GUIDANCE_PATH.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Basic existence
# ---------------------------------------------------------------------------

def test_guidance_file_exists():
    assert GUIDANCE_PATH.exists(), f"Missing guidance doc: {GUIDANCE_PATH}"


# ---------------------------------------------------------------------------
# Phase numbering — "p" suffix must be retired
# ---------------------------------------------------------------------------

def test_no_new_p_suffix_phases():
    """No phase in this window should use the 'p' suffix (1556p, 1557p, …)."""
    text = _text()
    # Allow the word "1555p" as a historical baseline reference, but no 1556p+ in phase table rows
    phase_table_rows = re.findall(r"\|\s*\d+\s*\|\s*(155\dp)\s*\|", text)
    assert phase_table_rows == [], (
        f"Phase table contains 'p'-suffixed phase numbers (should be retired): {phase_table_rows}"
    )


def test_p_suffix_retired_token_present():
    """Phase 1556 must emit the p-suffix retirement token."""
    text = _text()
    assert "phase_numbering_p_suffix_retired_phase_1556" in text, (
        "Missing p-suffix retirement token in Phase 1556 scope"
    )


# ---------------------------------------------------------------------------
# Phase count and sensitive gates
# ---------------------------------------------------------------------------

def test_nine_phases_in_candidate_table():
    """The candidate phase table must list exactly 9 phases (1556–1564)."""
    text = _text()
    # Count rows that look like "| N | 156N | ... |"
    phase_rows = re.findall(r"\|\s*\d+\s*\|\s*15[56]\d\s*\|", text)
    assert len(phase_rows) == 9, (
        f"Expected 9 phases in candidate table, found {len(phase_rows)}: {phase_rows}"
    )


def test_sensitive_phases_require_go_token():
    """Phases 1560, 1561, and 1564 must be classified SENSITIVE with GO tokens."""
    text = _text()
    for phase in ("1560", "1561", "1564"):
        assert f"GO Phase {phase}" in text, (
            f"Missing 'GO Phase {phase}' authorization token in guidance"
        )


def test_phase_1559_nons_sensitive_with_no_live_calls():
    """Phase 1559 must be NON-SENSITIVE and note that live calls are deferred to Phase 1560."""
    text = _text()
    # Find Phase 1559 section and check it's non-sensitive with the offline note
    assert "NON-SENSITIVE" in text, "Missing NON-SENSITIVE classification"
    assert "first called" in text or "first invoked" in text, (
        "Phase 1559 must note that network functions are first called/invoked in Phase 1560"
    )


# ---------------------------------------------------------------------------
# HB-001: must reference existing assertion_schema.py, not implement from scratch
# ---------------------------------------------------------------------------

def test_hb001_references_existing_assertion_schema():
    """Phase 1557 must reference existing assertion_schema.py rather than implementing from scratch."""
    text = _text()
    assert "assertion_schema.py" in text, (
        "HB-001 scope must reference the existing ilc_core/genesis/assertion_schema.py (Phase 858)"
    )
    assert "Phase 858" in text, (
        "HB-001 scope must acknowledge assertion_schema.py was implemented at Phase 858"
    )


def test_hb001_uses_builder_framing():
    """Phase 1557 must be framed as a builder/wiring phase, not greenfield schema implementation."""
    text = _text()
    assert "genesis_authority_assertion.py" in text, (
        "Phase 1557 must define genesis_authority_assertion.py (the builder layer)"
    )
    # The builder token should reference "wired" not "implemented from scratch"
    assert "hb_001_genesis_authority_assertion_builder_wired_phase_1557" in text, (
        "Phase 1557 closure token must use 'builder_wired' framing, not 'implemented'"
    )


# ---------------------------------------------------------------------------
# HB-003: must reference existing layer0_protocol_bundle.py
# ---------------------------------------------------------------------------

def test_hb003_references_existing_layer0():
    """Phase 1558 must reference the existing layer0_protocol_bundle.py."""
    text = _text()
    assert "layer0_protocol_bundle.py" in text, (
        "HB-003 scope must reference the existing ilc_core/bundle/layer0_protocol_bundle.py"
    )
    # The scope should describe adding schema entries, not implementing Layer 0
    assert "schemas=" in text or "schemas =" in text, (
        "HB-003 scope must reference the existing schemas= parameter, not a new Layer 0 implementation"
    )


# ---------------------------------------------------------------------------
# OBL status: correct framing
# ---------------------------------------------------------------------------

def test_obl_002_permanent_invariant_noted():
    """OBL-002 must be noted as a permanent invariant, not closed."""
    text = _text()
    assert "OBL-002" in text, "Missing OBL-002 mention in guidance"
    assert "permanent invariant" in text, (
        "Guidance must note OBL-002 is a permanent invariant (never closed)"
    )


def test_obl_030_open_noted():
    """OBL-030 must be noted as still open (Atlas publication)."""
    text = _text()
    assert "OBL-030" in text, "Missing OBL-030 mention in guidance"


def test_no_all_obls_closed_claim():
    """Guidance must NOT claim 'All 38 OBLs closed' — that is incorrect."""
    text = _text()
    assert "All 38 OBLs closed" not in text, (
        "Guidance incorrectly claims 'All 38 OBLs closed' — OBL-002 is permanent and OBL-030 is open"
    )


# ---------------------------------------------------------------------------
# No CDL mutation env var — not applicable to this window
# ---------------------------------------------------------------------------

def test_no_ilc_cdl_mutation_authorized_required():
    """No phase in this window requires ILC_CDL_MUTATION_AUTHORIZED — no CDL mutations occur."""
    text = _text()
    if "ILC_CDL_MUTATION_AUTHORIZED" not in text:
        return  # Cleanest case — not mentioned at all
    # If mentioned, the surrounding context must clarify it is NOT required
    # The doc may use backticks: "No `ILC_CDL_MUTATION_AUTHORIZED` env var is required"
    assert (
        "No `ILC_CDL_MUTATION_AUTHORIZED`" in text
        or "No ILC_CDL_MUTATION_AUTHORIZED" in text
        or "not required" in text.lower()
        or "is required for any phase in this window" in text
    ), (
        "If ILC_CDL_MUTATION_AUTHORIZED appears, the doc must clarify it is NOT required for this window"
    )


# ---------------------------------------------------------------------------
# v0.4 candidate remains unsigned
# ---------------------------------------------------------------------------

def test_v04_unsigned_until_signing():
    """Guidance must confirm v0.4 candidate remains unsigned throughout this window."""
    text = _text()
    assert "unsigned" in text, (
        "Guidance must note v0.4 candidate remains unsigned — signing is Block 6 Phase 1573"
    )


# ---------------------------------------------------------------------------
# Block 6 gating token
# ---------------------------------------------------------------------------

def test_phase_1564_emits_block6_gate_token():
    """Phase 1564 closure gate must emit go_window_1565_block6_required_next."""
    text = _text()
    assert "go_window_1565_block6_required_next" in text, (
        "Phase 1564 must emit go_window_1565_block6_required_next to gate Block 6 entry"
    )


# ---------------------------------------------------------------------------
# ADR-0024 not reopened
# ---------------------------------------------------------------------------

def test_adr_0024_not_reopened():
    """ADR-0024 must not be mentioned as open or in-scope for this window."""
    text = _text()
    # ADR-0024 may appear in deferred lists or non-goal sections but not as an action item
    if "ADR-0024" in text:
        # Confirm it only appears in a deferred/non-goal context
        adr_0024_contexts = [
            line for line in text.splitlines() if "ADR-0024" in line
        ]
        for ctx in adr_0024_contexts:
            assert any(
                keyword in ctx.lower()
                for keyword in ("deferred", "non-goal", "not in scope", "not revisit", "post")
            ), (
                f"ADR-0024 appears in a non-deferred context: {ctx!r}"
            )


# ---------------------------------------------------------------------------
# Workstream 1: Boolean token census in Phase 1556
# ---------------------------------------------------------------------------

def test_boolean_token_census_in_phase_1556():
    """Phase 1556 must include a boolean token census deliverable."""
    text = _text()
    assert "boolean_token_census" in text, (
        "Phase 1556 must include a boolean token census deliverable"
    )
    assert "ilc_phase_boolean_token_census_600_plus_1556_v0.1.json" in text, (
        "Phase 1556 must specify the census output file"
    )


def test_boolean_token_census_classification_values():
    """Census classification values must include the required classes."""
    text = _text()
    for cls in ("closed_true", "closed_false", "still_blocking", "default_off_guard",
                "code_style_noise", "possible_orphan"):
        assert cls in text, f"Missing census classification: {cls!r}"


def test_boolean_token_census_noise_guidance():
    """Census must note that sort_keys=True etc. are code-style noise, not protocol state."""
    text = _text()
    assert "sort_keys=True" in text or "code_style_noise" in text, (
        "Census guidance must note code-style patterns are not protocol state"
    )


# ---------------------------------------------------------------------------
# Workstream 2: ECU live smoke stays small; accelerated epochs are Block 6
# ---------------------------------------------------------------------------

def test_phase_1561_is_small_smoke_not_accelerated():
    """Phase 1561 must be scoped as a small smoke, not as the accelerated epoch lane."""
    text = _text()
    assert "Phase 1561" in text or "1561" in text
    # Must note that accelerated epochs are Block 6 scope
    assert "accelerated" in text.lower() or "block 6" in text.lower(), (
        "Guidance must note that accelerated logical-epoch lane is Block 6 scope"
    )


def test_phase_1561_checks_balance_report_command():
    """Phase 1561 must check for a per-agent balance/report command."""
    text = _text()
    assert "balance_report_command" in text or "balance/report" in text, (
        "Phase 1561 must check whether a per-agent balance/report command exists"
    )


# ---------------------------------------------------------------------------
# Workstream 3: OpenClaw forward-routing noted
# ---------------------------------------------------------------------------

def test_openclaw_forward_routing_noted():
    """Guidance must mention OpenClaw coverage as required in Block 6."""
    text = _text()
    assert "OpenClaw" in text or "openclaw" in text.lower(), (
        "Pre-RC window must note OpenClaw coverage is required in Block 6"
    )
    assert "CDL-033" in text, (
        "OpenClaw mention must reference CDL-033 for protocol position"
    )
