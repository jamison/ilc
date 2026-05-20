"""Tests for Phase 1399-1428 sequence lock artifact.

Phase 1399 — Window 1399-1428 sequence lock.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
LOCK_FILE = REPO_ROOT / "docs/specs/ilc_phase_1399_1428_sequence_lock_v0.1.md"
CDL_LOG = REPO_ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"
GATE_SOURCE = REPO_ROOT / "ilc_core/epistemic/jury_activation_gate.py"
GUIDANCE_DOC = REPO_ROOT / "docs/specs/ilc_window_1399_1428_candidate_phase_grouping_v0.1.md"


def _lock_text() -> str:
    return LOCK_FILE.read_text(encoding="utf-8")


def _cdl_text() -> str:
    return CDL_LOG.read_text(encoding="utf-8")


def _gate_text() -> str:
    return GATE_SOURCE.read_text(encoding="utf-8")


class TestSequenceLockExists:
    def test_lock_file_present(self) -> None:
        assert LOCK_FILE.exists(), f"Sequence lock not found at {LOCK_FILE}"

    def test_required_tokens_present(self) -> None:
        text = _lock_text()
        required = [
            "window_1399_1428_sequence_lock_committed_phase_1399_entry",
            "go_window_1399_1428_authorized_2026_05_20",
            "phase_1399_is_first_phase",
        ]
        for token in required:
            assert token in text, f"Required token missing: {token}"

    def test_lock_covers_30_phases(self) -> None:
        text = _lock_text()
        # Phase table should cover 1399 through 1428 (30 phases)
        assert "1399" in text
        assert "1428" in text
        assert "30 " in text or "| 30 |" in text

    def test_baseline_commit_ref_present(self) -> None:
        text = _lock_text()
        # Current commit at lock time
        assert "ec475d48" in text

    def test_cdl_number_assignments_recorded(self) -> None:
        text = _lock_text()
        assert "CDL-091" in text
        assert "CDL-092" in text
        assert "CDL-093" in text
        assert "CDL-094" in text  # next fresh CDL


class TestCdlRegisterGap:
    """Verify the CDL-091 registration gap assertion is accurate."""

    def test_cdl_091_absent_from_register(self) -> None:
        text = _cdl_text()
        # CDL-091 row must not yet appear in the register at sequence lock time
        assert "CDL-091" not in text, (
            "CDL-091 is already in the CDL register. "
            "The registration gap assumption in the sequence lock is stale — "
            "update the lock's §5 and Phase 1399 prompt accordingly."
        )

    def test_cdl_090_is_last_entry(self) -> None:
        text = _cdl_text()
        assert "CDL-090" in text, "CDL-090 should be present in the register"
        # Confirm CDL-090 is ratified
        assert "cdl_090_ratified_phase_1373" in text

    def test_cdl_092_absent_from_register(self) -> None:
        text = _cdl_text()
        assert "CDL-092" not in text, "CDL-092 is already registered; update sequence lock §7"

    def test_cdl_093_absent_from_register(self) -> None:
        text = _cdl_text()
        assert "CDL-093" not in text, "CDL-093 is already registered; update sequence lock §7"


class TestGateStaticStatus:
    """Assert gate is static and not yet showing PASS."""

    def test_gate_module_exists(self) -> None:
        assert GATE_SOURCE.exists(), f"Gate module not found at {GATE_SOURCE}"

    def test_gate_has_not_met_conditions(self) -> None:
        text = _gate_text()
        assert "NOT_MET" in text, "Gate must still have NOT_MET conditions"

    def test_gate_verdict_not_pass(self) -> None:
        from ilc_core.epistemic.jury_activation_gate import evaluate_jury_activation_gate
        report = evaluate_jury_activation_gate()
        assert report.verdict == "INCOMPLETE", (
            f"Gate verdict is '{report.verdict}' — expected INCOMPLETE at sequence lock time. "
            "Phase 1427 re-run will flip this after all conditions are MET."
        )

    def test_gate_seven_blocking_conditions_not_met(self) -> None:
        from ilc_core.epistemic.jury_activation_gate import (
            evaluate_jury_activation_gate,
            GateConditionStatus,
        )
        report = evaluate_jury_activation_gate()
        blocking_not_met = [
            c.condition_id for c in report.conditions
            if c.blocking and c.status == GateConditionStatus.NOT_MET
        ]
        assert len(blocking_not_met) == 7, (
            f"Expected 7 blocking NOT_MET conditions at sequence lock time, "
            f"found {len(blocking_not_met)}: {blocking_not_met}"
        )

    def test_gate_production_not_activated(self) -> None:
        from ilc_core.epistemic.jury_activation_gate import evaluate_jury_activation_gate
        report = evaluate_jury_activation_gate()
        assert report.production_activated is False


class TestPromptFilesPresent:
    """Confirm the first five phase prompts exist."""

    def _prompt(self, slug: str) -> Path:
        return REPO_ROOT / "docs/antigravity_tasks" / slug

    def test_phase_1399_prompt_present(self) -> None:
        f = self._prompt("antigravity_prompt__phase_1399_g8_cdl_091_jury_incentive_economics_prelock.md")
        assert f.exists(), f"Phase 1399 prompt not found: {f}"

    def test_phase_1400_prompt_present(self) -> None:
        f = self._prompt("antigravity_prompt__phase_1400_g8_cdl_091_jury_incentive_economics_ratification.md")
        assert f.exists(), f"Phase 1400 prompt not found: {f}"

    def test_phase_1401_prompt_present(self) -> None:
        f = self._prompt("antigravity_prompt__phase_1401_g8_cdl_091_jury_incentive_runtime_stub.md")
        assert f.exists(), f"Phase 1401 prompt not found: {f}"

    def test_phase_1402_prompt_present(self) -> None:
        f = self._prompt("antigravity_prompt__phase_1402_g8_cdl_092_capproof_opening.md")
        assert f.exists(), f"Phase 1402 prompt not found: {f}"

    def test_phase_1403_prompt_present(self) -> None:
        f = self._prompt("antigravity_prompt__phase_1403_g8_cdl_092_capproof_deliberation.md")
        assert f.exists(), f"Phase 1403 prompt not found: {f}"


class TestGuidanceDocConsistency:
    """Guidance doc and sequence lock must agree on Phase 1399 design."""

    def test_guidance_doc_present(self) -> None:
        assert GUIDANCE_DOC.exists()

    def test_guidance_doc_acknowledges_cdl_091_gap(self) -> None:
        text = GUIDANCE_DOC.read_text(encoding="utf-8")
        assert "Phase 1394" in text and "did not" in text, (
            "Guidance doc should note Phase 1394 did not mutate the CDL register"
        )

    def test_guidance_doc_acknowledges_static_gate(self) -> None:
        text = GUIDANCE_DOC.read_text(encoding="utf-8")
        assert "static" in text.lower() or "hardcoded" in text.lower() or "currently" in text.lower(), (
            "Guidance doc should acknowledge the gate is not auto-flipping"
        )
