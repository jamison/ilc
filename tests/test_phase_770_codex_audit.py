from __future__ import annotations

from pathlib import Path
import unittest


AUDIT = Path("docs/specs/ilc_sec_004_m007_activation_codex_audit_770_v0.1.md")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class TestPhase770CodexAudit(unittest.TestCase):
    def test_audit_exists_with_required_sections(self) -> None:
        text = _read(AUDIT)
        headings = (
            "## 1. Constitutional compliance",
            "## 2. SEC-004 implementation review",
            "## 3. M-007 implementation review",
            "## 4. Concurrency hazard review",
            "## 5. Non-conflation verification",
            "## 6. Unresolved findings (if any)",
            "## 7. Audit verdict",
        )
        positions = [text.index(heading) for heading in headings]
        self.assertEqual(positions, sorted(positions))

    def test_required_governance_tokens_present(self) -> None:
        text = _read(AUDIT)
        tokens = (
            "phase_770_audit_cdl_017_constitutional_compliance=confirmed",
            "phase_770_audit_sec_004_acceptance_test=confirmed",
            "phase_770_audit_m007_hooks_activated=confirmed",
            "phase_770_audit_live_settlement_wiring_deferred=confirmed",
            "phase_770_audit_first_validator_deployment_gate_preserved=confirmed",
        )
        for token in tokens:
            self.assertIn(f"`{token}`", text)

    def test_audit_confirms_real_live_surfaces(self) -> None:
        text = _read(AUDIT)
        self.assertIn("ilc_consensus/src/fast_path.rs", text)
        self.assertIn("ilc_consensus/src/testnet_client_main.rs", text)
        self.assertIn("ilc_consensus/src/validator.rs", text)
        self.assertIn("rebuild_with(...)", text)

    def test_audit_records_no_blocking_findings(self) -> None:
        text = _read(AUDIT)
        self.assertIn("No unresolved BLOCKING findings.", text)
        self.assertIn("Audit verdict: `CLEAR`.", text)
        self.assertIn("Non-blocking note:", text)


if __name__ == "__main__":
    unittest.main()
