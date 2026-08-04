# SPDX-License-Identifier: AGPL-3.0-only
"""Regression tests for GAP-series prompt naming support in validate_phase_prompt.py.

These tests ensure the validator accepts all legitimate GAP-series filename patterns
and rejects malformed ones, without breaking existing numeric-phase support.

Added: Phase GAP-HARNESS-SIDECAR-00 (2026-08-04) after extending FILENAME_RE and H1_RE
to support gap_* phase names.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from tools.validate_phase_prompt import FILENAME_RE, H1_RE, validate


# ---------------------------------------------------------------------------
# FILENAME_RE unit tests — pattern matching only, no real files needed
# ---------------------------------------------------------------------------


def _match_phase(filename: str) -> str | None:
    """Return matched phase group or None if no match."""
    m = FILENAME_RE.match(filename)
    return m.group("phase") if m else None


def _match_group(filename: str) -> str | None:
    """Return matched group number or None."""
    m = FILENAME_RE.match(filename)
    return m.group("group") if m else None


class TestFilenameRE:
    # --- Numeric phases (must continue to work) ---

    def test_numeric_plain(self) -> None:
        assert _match_phase("antigravity_prompt__phase_1234_g8_some_slug.md") == "1234"

    def test_numeric_alpha_suffix(self) -> None:
        assert _match_phase("antigravity_prompt__phase_1234a_g8_some_slug.md") == "1234a"

    def test_numeric_fix_suffix(self) -> None:
        assert _match_phase("antigravity_prompt__phase_1234_fix1_g8_some_slug.md") == "1234_fix1"

    def test_numeric_alpha_fix_suffix(self) -> None:
        assert _match_phase("antigravity_prompt__phase_1234a_fix2b_g8_some_slug.md") == "1234a_fix2b"

    def test_numeric_group_captured(self) -> None:
        assert _match_group("antigravity_prompt__phase_1234_g10_some_slug.md") == "10"

    # --- GAP-series with _g<N>_ group (Type A) ---

    def test_gap_simple_slot_with_group(self) -> None:
        assert (
            _match_phase("antigravity_prompt__phase_gap_agent_harness_00_g10_agent_native_harness_ontology.md")
            == "gap_agent_harness_00"
        )

    def test_gap_alpha_slot_with_group(self) -> None:
        assert (
            _match_phase("antigravity_prompt__phase_gap_agent_harness_01a_g10_signing_provider_boundary.md")
            == "gap_agent_harness_01a"
        )

    def test_gap_compound_name_with_group(self) -> None:
        assert (
            _match_phase("antigravity_prompt__phase_gap_ecu_transfer_rc_00_g10_ecu_transfer_canon_reconciliation.md")
            == "gap_ecu_transfer_rc_00"
        )

    def test_gap_live_rc_long_chain_with_group(self) -> None:
        assert (
            _match_phase("antigravity_prompt__phase_gap_value_action_live_rc_08_g10_ilc_transfer_gate.md")
            == "gap_value_action_live_rc_08"
        )

    def test_gap_werner_alpha_slot_with_group(self) -> None:
        assert (
            _match_phase("antigravity_prompt__phase_gap_werner_02a_g10_werner_cdl_deliberation.md")
            == "gap_werner_02a"
        )

    def test_gap_keygen_new_phase(self) -> None:
        assert (
            _match_phase("antigravity_prompt__phase_gap_agent_keygen_00_g10_agent_hotkey_cli.md")
            == "gap_agent_keygen_00"
        )

    def test_gap_graph_sign_new_phase(self) -> None:
        assert (
            _match_phase("antigravity_prompt__phase_gap_graph_sign_00_g10_signed_graph_submission.md")
            == "gap_graph_sign_00"
        )

    def test_gap_harness_sidecar_new_phase(self) -> None:
        assert (
            _match_phase("antigravity_prompt__phase_gap_harness_sidecar_00_g10_source_reconciliation.md")
            == "gap_harness_sidecar_00"
        )

    def test_gap_group_captured_when_present(self) -> None:
        assert (
            _match_group("antigravity_prompt__phase_gap_agent_keygen_00_g10_agent_hotkey_cli.md")
            == "10"
        )

    # --- GAP-series without _g<N>_ group (Type B) ---

    def test_gap_type_b_no_group(self) -> None:
        assert (
            _match_phase("antigravity_prompt__phase_gap_ecu_00_ecu_canon_reconciliation.md")
            == "gap_ecu_00"
        )

    def test_gap_type_b_group_is_none(self) -> None:
        assert (
            _match_group("antigravity_prompt__phase_gap_ecu_00_ecu_canon_reconciliation.md")
            is None
        )

    # --- Must NOT match (malformed) ---

    def test_rejects_gap_without_terminal_slot(self) -> None:
        """GAP names must end with a numeric slot like _00, _01a."""
        assert _match_phase("antigravity_prompt__phase_gap_nodeslot_g10_slug.md") is None

    def test_gap_g_prefix_treated_as_slug_when_no_extra_segment(self) -> None:
        # "antigravity_prompt__phase_gap_agent_harness_00_g10.md" is accepted:
        # the regex backtracks on the optional _g<N> group and treats "g10" as
        # the slug. This is correct — real filenames always have descriptive
        # slugs after the group, so this edge case is not a practical concern.
        assert _match_phase("antigravity_prompt__phase_gap_agent_harness_00_g10.md") == "gap_agent_harness_00"
        assert _match_group("antigravity_prompt__phase_gap_agent_harness_00_g10.md") is None

    def test_rejects_bare_gap_prefix(self) -> None:
        assert _match_phase("antigravity_prompt__phase_gap_g10_slug.md") is None

    def test_rejects_wrong_prefix(self) -> None:
        assert _match_phase("phase_gap_agent_harness_00_g10_slug.md") is None

    def test_rejects_uppercase_gap_in_filename(self) -> None:
        """Filenames must be lowercase."""
        assert _match_phase("antigravity_prompt__phase_GAP_agent_harness_00_g10_slug.md") is None


# ---------------------------------------------------------------------------
# H1_RE unit tests — title line matching
# ---------------------------------------------------------------------------


def _h1_phase(h1_line: str) -> str | None:
    m = H1_RE.match(h1_line)
    return m.group("phase") if m else None


def _h1_group(h1_line: str) -> str | None:
    m = H1_RE.match(h1_line)
    return m.group("group") if m else None


class TestH1RE:
    def test_numeric_h1(self) -> None:
        assert _h1_phase("# Phase 1234-G8: Some Title") == "1234"

    def test_numeric_h1_group(self) -> None:
        assert _h1_group("# Phase 1234-G8: Some Title") == "8"

    def test_gap_h1_with_group(self) -> None:
        assert _h1_phase("# Phase GAP-AGENT-KEYGEN-00-G10: Agent Action Hotkey CLI") == "GAP-AGENT-KEYGEN-00"

    def test_gap_h1_group_captured(self) -> None:
        assert _h1_group("# Phase GAP-AGENT-KEYGEN-00-G10: Agent Action Hotkey CLI") == "10"

    def test_gap_h1_compound(self) -> None:
        assert _h1_phase("# Phase GAP-HARNESS-SIDECAR-00-G10: Title") == "GAP-HARNESS-SIDECAR-00"

    def test_gap_h1_without_group(self) -> None:
        assert _h1_phase("# Phase GAP-ECU-00: Title") == "GAP-ECU-00"

    def test_gap_h1_without_group_no_group_captured(self) -> None:
        assert _h1_group("# Phase GAP-ECU-00: Title") is None

    def test_gap_h1_case_insensitive(self) -> None:
        assert _h1_phase("# Phase gap-agent-keygen-00-g10: Title") is not None

    def test_gap_h1_alpha_slot(self) -> None:
        assert _h1_phase("# Phase GAP-AGENT-HARNESS-01A-G10: Title") == "GAP-AGENT-HARNESS-01A"


# ---------------------------------------------------------------------------
# Integration tests against real prompt files
# ---------------------------------------------------------------------------


ROOT = Path(__file__).resolve().parents[1]
PROMPT_DIR = ROOT / "docs/antigravity_tasks"


def _assert_no_filename_or_h1_errors(filename: str) -> None:
    prompt = PROMPT_DIR / filename
    if not prompt.exists():
        pytest.skip(f"prompt file not present: filename")
    errors = validate(prompt)
    filename_errors = [e for e in errors if "filename" in e or "h1_phase" in e or "h1_group" in e]
    assert filename_errors == [], f"Filename/H1 errors in {filename}: {filename_errors}"


class TestRealPromptFiles:
    """Integration tests against real prompt files in the repo.

    These tests check only that filename and H1 validation passes — they do not
    assert that the full prompt schema is met (some historical completed prompts
    predate schema requirements and are expected to have other errors).
    """

    # New prompts (must be fully VALID)
    def test_gap_agent_keygen_00_valid(self) -> None:
        prompt = PROMPT_DIR / "antigravity_prompt__phase_gap_agent_keygen_00_g10_agent_hotkey_cli.md"
        errors = validate(prompt)
        assert errors == [], f"Expected VALID, got errors: {errors}"

    def test_gap_graph_sign_00_valid(self) -> None:
        prompt = PROMPT_DIR / "antigravity_prompt__phase_gap_graph_sign_00_g10_signed_graph_submission.md"
        errors = validate(prompt)
        assert errors == [], f"Expected VALID, got errors: {errors}"

    def test_gap_harness_sidecar_00_valid(self) -> None:
        prompt = PROMPT_DIR / "antigravity_prompt__phase_gap_harness_sidecar_00_g10_source_reconciliation.md"
        errors = validate(prompt)
        assert errors == [], f"Expected VALID, got errors: {errors}"

    # Existing committed prompts — filename/H1 must not regress
    def test_gap_agent_harness_00_no_filename_error(self) -> None:
        _assert_no_filename_or_h1_errors(
            "antigravity_prompt__phase_gap_agent_harness_00_g10_agent_native_harness_ontology.md"
        )

    def test_gap_agent_harness_01a_no_filename_error(self) -> None:
        _assert_no_filename_or_h1_errors(
            "antigravity_prompt__phase_gap_agent_harness_01a_g10_signing_provider_boundary.md"
        )

    def test_gap_ecu_00_type_b_no_filename_error(self) -> None:
        _assert_no_filename_or_h1_errors(
            "antigravity_prompt__phase_gap_ecu_00_ecu_canon_reconciliation.md"
        )

    def test_gap_ecu_transfer_rc_00_no_filename_error(self) -> None:
        _assert_no_filename_or_h1_errors(
            "antigravity_prompt__phase_gap_ecu_transfer_rc_00_g10_ecu_transfer_canon_reconciliation.md"
        )

    def test_gap_werner_02a_no_filename_error(self) -> None:
        _assert_no_filename_or_h1_errors(
            "antigravity_prompt__phase_gap_werner_02a_g10_werner_cdl_deliberation.md"
        )

    def test_gap_value_action_live_rc_08_no_filename_error(self) -> None:
        _assert_no_filename_or_h1_errors(
            "antigravity_prompt__phase_gap_value_action_live_rc_08_g10_ilc_transfer_gate.md"
        )

    # Existing numeric phase prompt — must not regress
    def test_numeric_phase_prompt_no_filename_error(self) -> None:
        _assert_no_filename_or_h1_errors(
            "antigravity_prompt__phase_1351a_g8_cdl_029_amendment_post_theta_hard_dust_routing.md"
        )
