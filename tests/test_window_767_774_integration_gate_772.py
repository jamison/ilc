from __future__ import annotations

from pathlib import Path
import subprocess
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
CONSENSUS_DIR = REPO_ROOT / "ilc_consensus"
VENV_PYTHON = REPO_ROOT / ".venv" / "bin" / "python"
CARGO = Path.home() / ".cargo" / "bin" / "cargo"


def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


class TestWindow767774IntegrationGate772(unittest.TestCase):
    def test_cargo_test_with_testnet_fault_sim_passes(self) -> None:
        result = _run(
            [str(CARGO), "test", "--features", "testnet_fault_sim"],
            CONSENSUS_DIR,
        )
        if result.returncode != 0:
            self.fail(
                "cargo test --features testnet_fault_sim failed\n"
                f"stdout:\n{result.stdout}\n\nstderr:\n{result.stderr}"
            )
        self.assertIn(
            "test_ejected_validator_sig_rejected_after_epoch_boundary ... ok",
            result.stdout,
        )
        self.assertIn(
            "test_admit_validator_adds_validator_and_recomputes_f ... ok",
            result.stdout,
        )
        self.assertIn(
            "test_eject_validator_rejects_invalid_collapse ... ok",
            result.stdout,
        )

    def test_phase_specific_pytest_subset_passes(self) -> None:
        result = _run(
            [
                str(VENV_PYTHON),
                "-m",
                "pytest",
                "tests/",
                "-q",
                "-k",
                "m015 or m016 or m017 or m018 or m019 or m020 or m021 or m022 or phase_768 or phase_769 or phase_770 or phase_771",
            ],
            REPO_ROOT,
        )
        if result.returncode != 0:
            self.fail(
                "phase-specific pytest subset failed\n"
                f"stdout:\n{result.stdout}\n\nstderr:\n{result.stderr}"
            )
        self.assertIn("passed", result.stdout)

    def test_constitutional_decision_log_unchanged(self) -> None:
        result = _run(
            ["git", "diff", "--exit-code", "--", "docs/specs/ilc_constitutional_decision_log_v0.1.md"],
            REPO_ROOT,
        )
        if result.returncode != 0:
            self.fail(
                "decision log changed during window 767-774\n"
                f"stdout:\n{result.stdout}\n\nstderr:\n{result.stderr}"
            )


if __name__ == "__main__":
    unittest.main()
