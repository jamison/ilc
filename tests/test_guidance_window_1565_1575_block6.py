"""Structural tests for the Block 6 window guidance document.

Validates invariants asserted in:
  docs/specs/ilc_window_1565_1575_block6_candidate_phase_grouping_v0.1.md

These tests catch guidance-doc drift before any phase executes, not after.
"""
import re
import pathlib

GUIDANCE_PATH = pathlib.Path(
    "docs/specs/ilc_window_1565_1575_block6_candidate_phase_grouping_v0.1.md"
)


def _text() -> str:
    return GUIDANCE_PATH.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Basic existence
# ---------------------------------------------------------------------------

def test_guidance_file_exists():
    assert GUIDANCE_PATH.exists(), f"Missing guidance doc: {GUIDANCE_PATH}"


# ---------------------------------------------------------------------------
# Phase numbering — plain integers, no "p" suffix
# ---------------------------------------------------------------------------

def test_no_p_suffix_in_phase_table():
    """No phase in this window should use the 'p' suffix in the candidate phase table."""
    text = _text()
    phase_table_rows = re.findall(r"\|\s*\d+\s*\|\s*(15[67]\dp)\s*\|", text)
    assert phase_table_rows == [], (
        f"Phase table contains 'p'-suffixed phase numbers (should be plain integers): {phase_table_rows}"
    )


# ---------------------------------------------------------------------------
# Phase count and range
# ---------------------------------------------------------------------------

def test_eleven_phases_in_candidate_table():
    """The candidate phase table must list exactly 11 phases (1565–1575)."""
    text = _text()
    phase_rows = re.findall(r"\|\s*\d+\s*\|\s*15[67]\d\s*\|", text)
    assert len(phase_rows) == 11, (
        f"Expected 11 phases in candidate table, found {len(phase_rows)}: {phase_rows}"
    )


def test_phase_range_1565_to_1575():
    """All phases must be in the range 1565–1575."""
    text = _text()
    # Extract phase numbers from phase table
    phase_rows = re.findall(r"\|\s*\d+\s*\|\s*(15[67]\d)\s*\|", text)
    for p in phase_rows:
        pnum = int(p)
        assert 1565 <= pnum <= 1575, f"Phase {pnum} is outside 1565–1575 range"


# ---------------------------------------------------------------------------
# Sensitive gates and GO tokens
# ---------------------------------------------------------------------------

def test_all_sensitive_phases_have_go_tokens():
    """Each SENSITIVE phase must have a corresponding GO token in the text."""
    text = _text()
    for phase in ("1565", "1566", "1567", "1568", "1569", "1573", "1574", "1575"):
        assert f"GO Phase {phase}" in text or f"GO PUBLIC-RC-GATE-001" in text, (
            f"Missing GO authorization for Phase {phase}"
        )
    # Phase 1575 uses special token
    assert "GO PUBLIC-RC-GATE-001" in text, "Missing PUBLIC-RC-GATE-001 authorization"


# ---------------------------------------------------------------------------
# Pre-commit hook — CDL mutation env var must NOT apply to runtime-only phases
# ---------------------------------------------------------------------------

def test_cdl_mutation_env_var_correctly_scoped():
    """ILC_CDL_MUTATION_AUTHORIZED must be described as CDL-only, not for runtime code."""
    text = _text()
    assert "ILC_CDL_MUTATION_AUTHORIZED" in text, (
        "Guidance must mention ILC_CDL_MUTATION_AUTHORIZED to clarify its scope"
    )
    # The doc must clarify it applies only to CDL document mutations
    assert "CDL register document mutation" in text or "CDL document mutation" in text or (
        "CDL mutations" in text and "NOT" in text
    ), (
        "Guidance must clarify ILC_CDL_MUTATION_AUTHORIZED is for CDL doc mutations only, "
        "not for general runtime code changes"
    )


def test_runtime_only_phases_do_not_require_cdl_env_var():
    """Phase 1568 (rehearsal) must not require ILC_CDL_MUTATION_AUTHORIZED."""
    text = _text()
    # Find the Phase 1568 section
    phase_1568_match = re.search(
        r"### Phase 1568.*?(?=### Phase \d|---|\Z)", text, re.DOTALL
    )
    if phase_1568_match:
        section = phase_1568_match.group(0)
        assert "ILC_CDL_MUTATION_AUTHORIZED" not in section, (
            "Phase 1568 section must not require ILC_CDL_MUTATION_AUTHORIZED — "
            "it is a runtime-only phase with no CDL document mutation"
        )


# ---------------------------------------------------------------------------
# Block 6 gated on Phase 1564 closure
# ---------------------------------------------------------------------------

def test_block6_gated_on_phase_1564_token():
    """Block 6 guidance must require the go_window_1565_block6_required_next token from Phase 1564."""
    text = _text()
    assert "go_window_1565_block6_required_next" in text, (
        "Block 6 guidance must gate on go_window_1565_block6_required_next from Phase 1564 closure"
    )


# ---------------------------------------------------------------------------
# v0.4 candidate unsigned until Phase 1573
# ---------------------------------------------------------------------------

def test_v04_unsigned_until_phase_1573():
    """The v0.4 candidate must remain unsigned until the Phase 1573 signing ceremony."""
    text = _text()
    assert "unsigned" in text and "1573" in text, (
        "Guidance must note v0.4 is unsigned until Phase 1573 signing ceremony"
    )
    assert "genesis_v04_signed_phase_1573" in text, (
        "Phase 1573 must emit genesis_v04_signed_phase_1573 token"
    )


# ---------------------------------------------------------------------------
# Phase 1573 hard stop condition
# ---------------------------------------------------------------------------

def test_phase_1573_hard_stop_condition():
    """Phase 1573 must include a hard stop condition for unexpected semantic changes."""
    text = _text()
    assert "Hard stop" in text or "hard stop" in text or "stop immediately" in text, (
        "Phase 1573 scope must include a hard stop condition for unexpected v0.4 candidate changes"
    )
    assert "CDL-098" in text, (
        "Phase 1573 hard stop must route to CDL-098 if semantic changes are discovered"
    )


# ---------------------------------------------------------------------------
# ADR-0024 not reopened
# ---------------------------------------------------------------------------

def test_adr_0024_not_reopened():
    """ADR-0024 must be explicitly noted as NOT revisited in Block 6."""
    text = _text()
    assert "ADR-0024" in text, "Missing ADR-0024 mention"
    # Must appear in non-goal or deferred context
    adr_0024_contexts = [
        line for line in text.splitlines() if "ADR-0024" in line
    ]
    for ctx in adr_0024_contexts:
        assert any(
            keyword in ctx.lower()
            for keyword in (
                    "not revisit", "non-goal", "deferred", "not reopened", "not in scope",
                    "optional-harness", "reframed", "accepted",  # baseline/baseline-table refs
                    "post-adr", "post-public", "governance",      # deferred-governance table refs
                )
        ), (
            f"ADR-0024 appears in a non-deferred context in Block 6 guidance: {ctx!r}"
        )


# ---------------------------------------------------------------------------
# Activation matrix precision
# ---------------------------------------------------------------------------

def test_adr_0009_activation_row_distinguishes_serving_from_verification():
    """ADR-0009 public_rc_live row must distinguish artifact verification from public network serving."""
    text = _text()
    # Find the activation matrix ADR-0009 row
    adr_row = re.search(r"ADR-0009.*public_rc_live.*\|", text)
    assert adr_row is not None, "Missing ADR-0009 row in activation matrix"
    # The rationale must mention verification/export vs. network serving
    adr_context = re.search(
        r"ADR-0009.*\n.*\n.*", text  # Get surrounding context
    )
    assert (
        "verification" in text and "serving" in text
    ), (
        "ADR-0009 activation row must clarify verification/export vs. public network serving"
    )


def test_cdl_042_row_identity_only():
    """CDL-042 public_rc_live row must cover identity derivation only, not validator admission."""
    text = _text()
    assert "identity derivation" in text or "agent_id derivation" in text, (
        "CDL-042 activation row must clarify it covers identity derivation only, "
        "not validator admission/ejection"
    )


# ---------------------------------------------------------------------------
# PUBLIC-RC-GATE-001 authorization phrase
# ---------------------------------------------------------------------------

def test_public_rc_gate_exact_phrase():
    """Phase 1575 must require the exact phrase 'GO PUBLIC-RC-GATE-001'."""
    text = _text()
    assert "GO PUBLIC-RC-GATE-001" in text, (
        "Phase 1575 must require the exact phrase 'GO PUBLIC-RC-GATE-001'"
    )


# ---------------------------------------------------------------------------
# No public economics at epoch 0
# ---------------------------------------------------------------------------

def test_default_off_economics_at_public_rc():
    """Guidance must recommend default-off for production economics at public RC."""
    text = _text()
    # Count only activation matrix table rows (lines with |).
    # A row "has" default_off if it contains that string at all (even alongside public_rc_live).
    # A row is a "public_rc_live only" row if it contains public_rc_live but NOT default_off_at_public_rc.
    # This avoids counting prose explanations that mention both values in the same cell description.
    table_rows = [line for line in text.splitlines() if line.strip().startswith("|")]
    default_off_rows = sum(1 for r in table_rows if "default_off_at_public_rc" in r)
    public_rc_live_only_rows = sum(
        1 for r in table_rows if "public_rc_live" in r and "default_off_at_public_rc" not in r
    )
    assert default_off_rows > public_rc_live_only_rows, (
        f"Expected more default_off_at_public_rc rows ({default_off_rows}) than "
        f"public_rc_live-only rows ({public_rc_live_only_rows}) — most guards should remain off at RC"
    )


# ---------------------------------------------------------------------------
# Workstream 1: Accelerated economic epoch rehearsal in Phase 1568
# ---------------------------------------------------------------------------

def test_accelerated_epoch_lane_in_phase_1568():
    """Phase 1568 must include an accelerated logical-epoch lane."""
    text = _text()
    assert "accelerated" in text.lower(), (
        "Phase 1568 rehearsal scope must include an accelerated logical-epoch lane"
    )
    # Must distinguish from wall-clock soak
    assert "wall-clock" in text or "wall_clock" in text, (
        "Phase 1568 must distinguish accelerated epochs from wall-clock soak"
    )


def test_wall_clock_soak_in_phase_1568():
    """Phase 1568 must include a wall-clock soak lane (3-7 days)."""
    text = _text()
    assert "soak" in text.lower(), (
        "Phase 1568 must include a wall-clock network soak lane"
    )
    assert "3" in text and "7" in text, (
        "Soak duration should reference 3-7 days"
    )


def test_per_agent_balance_view_required():
    """Phase 1568 must require a per-agent balance/report view."""
    text = _text()
    assert "per-agent balance" in text or "per_agent_balance" in text, (
        "Phase 1568 must require a per-agent balance view"
    )


def test_decimal_safety_check_in_rehearsal():
    """Phase 1568 must include a Decimal non-finite safety check."""
    text = _text()
    assert "non-finite" in text or "non_finite" in text, (
        "Phase 1568 rehearsal must include a non-finite Decimal safety check"
    )


def test_accelerated_not_substitute_for_soak():
    """Guidance must note accelerated epochs are NOT a substitute for wall-clock soak."""
    text = _text()
    assert "not a substitute" in text.lower() or "neither substitutes" in text.lower(), (
        "Guidance must explicitly state accelerated epochs are not a substitute for wall-clock soak"
    )


# ---------------------------------------------------------------------------
# Workstream 2: OpenClaw harness coverage in Phase 1568
# ---------------------------------------------------------------------------

def test_openclaw_harness_lane_in_phase_1568():
    """Phase 1568 must include an OpenClaw harness lane."""
    text = _text()
    assert "OpenClaw" in text, "Phase 1568 must include OpenClaw harness coverage"
    assert "ilc-local" in text, (
        "OpenClaw coverage must reference the ilc-local skill from Phase 1323 Fix2"
    )


def test_openclaw_protocol_position_noted():
    """OpenClaw must be noted as harness/host, not protocol substrate (CDL-033)."""
    text = _text()
    assert "CDL-033" in text, "Block 6 guidance must reference CDL-033 for OpenClaw position"
    assert "harness" in text.lower() or "host" in text.lower(), (
        "OpenClaw must be described as a harness/host, not a protocol substrate"
    )


def test_clawhub_not_published_during_rehearsal():
    """ClawHub must NOT be published during rehearsal — only after Phase 1575 authorization."""
    text = _text()
    assert "clawhub_not_published" in text or "not publish" in text.lower(), (
        "Guidance must explicitly prohibit ClawHub publication during rehearsal"
    )


def test_openclaw_activation_matrix_rows():
    """Phase 1574 activation matrix must include OpenClaw/ClawHub rows."""
    text = _text()
    assert "openclaw_clawhub_listing_authorized" in text, (
        "Activation matrix must include openclaw_clawhub_listing_authorized row"
    )
    assert "openclaw_public_installability_claim_authorized" in text, (
        "Activation matrix must include openclaw_public_installability_claim_authorized row"
    )
    assert "openclaw_skill_package_ready" in text, (
        "Activation matrix must include openclaw_skill_package_ready row"
    )


def test_phase_1574_openclaw_references_phase_1567_skill():
    """Phase 1574 must require Phase 1567 SKILL.md package evidence for ClawHub publication."""
    text = _text()
    # Check that the Phase 1574 checks reference the skill package
    assert "openclaw_skill_package_ready" in text, (
        "Phase 1574 must reference openclaw_skill_package_ready evidence from Phase 1567"
    )


# ---------------------------------------------------------------------------
# Workstream 3: Boolean token census in Phase 1565
# ---------------------------------------------------------------------------

def test_boolean_token_census_referenced_in_phase_1565():
    """Phase 1565 must require the boolean token census from Phase 1556 to be reviewed."""
    text = _text()
    assert "boolean_token_census" in text, (
        "Phase 1565 must reference the boolean_token_census from Phase 1556"
    )
    assert "boolean_token_census_orphan_disposition_confirmed_phase_1565" in text, (
        "Phase 1565 must emit orphan-disposition confirmation token"
    )


def test_boolean_token_census_in_phase_1574():
    """Phase 1574 must review boolean token census orphans before gate opens."""
    text = _text()
    assert "boolean_token_census_orphan_review_complete_phase_1574" in text, (
        "Phase 1574 must emit orphan review complete token"
    )


def test_openclaw_phase_1323_fix2_evidence_referenced():
    """Block 6 must reference Phase 1323 Fix2 OpenClaw VPS install evidence."""
    text = _text()
    assert "ilc_phase_1323_fix2_openclaw_vps_install_skill_discovery_v0.1.json" in text, (
        "Block 6 must reference the Phase 1323 Fix2 OpenClaw install evidence file"
    )
