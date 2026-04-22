from __future__ import annotations

from pathlib import Path
import unittest


VALIDATOR_RS = Path("ilc_consensus/src/validator.rs")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class TestPhase769M007HookActivation(unittest.TestCase):
    def test_validator_hooks_no_longer_unimplemented(self) -> None:
        text = _read(VALIDATOR_RS)
        self.assertIn("pub fn admit_validator(&mut self, id: ValidatorID, key: ValidatorKey)", text)
        self.assertIn("pub fn eject_validator(&mut self, id: ValidatorID)", text)
        self.assertNotIn(
            'unimplemented!("CDL-017: validator admission requires ratification before activation")',
            text,
        )
        self.assertNotIn(
            'unimplemented!("CDL-017: validator ejection requires ratification before activation")',
            text,
        )

    def test_hooks_recompute_f_from_resulting_cardinality(self) -> None:
        text = _read(VALIDATOR_RS)
        self.assertIn("fn rebuild_with(validators: Vec<(ValidatorID, ValidatorKey)>)", text)
        self.assertIn("let f = validators.len().saturating_sub(1) / 3;", text)
        self.assertIn("ValidatorSet::new(validators, f)", text)

    def test_hooks_cover_duplicate_and_missing_validator_errors(self) -> None:
        text = _read(VALIDATOR_RS)
        self.assertIn('\"validator {} already present\"', text)
        self.assertIn('\"validator {} not present\"', text)

    def test_validator_unit_tests_cover_edge_cases(self) -> None:
        text = _read(VALIDATOR_RS)
        required_tests = (
            "fn test_admit_validator_adds_validator_and_recomputes_f()",
            "fn test_admit_validator_rejects_duplicate_id()",
            "fn test_eject_validator_removes_validator_and_recomputes_f()",
            "fn test_eject_validator_rejects_missing_id()",
            "fn test_eject_validator_rejects_invalid_collapse()",
        )
        for marker in required_tests:
            self.assertIn(marker, text)


if __name__ == "__main__":
    unittest.main()
