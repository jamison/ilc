from __future__ import annotations

import subprocess
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
FAST_PATH = REPO_ROOT / "ilc_consensus" / "src" / "fast_path.rs"
CLIENT_PATH = REPO_ROOT / "ilc_consensus" / "src" / "testnet_client_main.rs"
VALIDATOR_PATH = REPO_ROOT / "ilc_consensus" / "src" / "validator.rs"
AUDIT_PATH = REPO_ROOT / "docs" / "specs" / "ilc_sec_004_m007_activation_codex_audit_770_v0.1.md"
LANE_DOC = REPO_ROOT / "docs" / "research" / "ilc_mysticeti_implementation_lane_m_series_v0.1.md"
CAPSULE_PATH = REPO_ROOT / "docs" / "specs" / "ilc_antigravity_context_capsule_v5.6.md"
GATE_PATH = REPO_ROOT / "docs" / "specs" / "ilc_window_767_774_closure_gate_774_v0.1.md"
PLANNING_INDEX = REPO_ROOT / "docs" / "PLANNING_INDEX.md"
INTEGRATION_GATE_TEST = REPO_ROOT / "tests" / "test_window_767_774_integration_gate_772.py"
DECISION_LOG = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
VENV_PYTHON = REPO_ROOT / ".venv" / "bin" / "python"
WINDOW_START_COMMIT = "25e21b5c"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    return " ".join(text.split())


def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


def _window_commits() -> list[tuple[str, str]]:
    result = _run(
        ["git", "log", "--format=%H%x09%s", f"{WINDOW_START_COMMIT}^..HEAD"],
        REPO_ROOT,
    )
    if result.returncode != 0:
        raise AssertionError(
            "failed to read window commit history\n"
            f"stdout:\n{result.stdout}\n\nstderr:\n{result.stderr}"
        )
    commits: list[tuple[str, str]] = []
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        commits.append((commit_hash, subject))
    return commits


def _changed_paths(commit_hash: str) -> set[str]:
    result = _run(["git", "show", "--name-only", "--pretty=", commit_hash], REPO_ROOT)
    if result.returncode != 0:
        raise AssertionError(
            "failed to inspect commit paths\n"
            f"stdout:\n{result.stdout}\n\nstderr:\n{result.stderr}"
        )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


class TestWindow767774ClosureGate(unittest.TestCase):
    def test_output_files_and_required_tokens_exist(self) -> None:
        gate = _read(GATE_PATH)
        planning = _read(PLANNING_INDEX)
        self.assertIn("`window_767_774_closed`", gate)
        self.assertIn("`sec_004_activation_complete_phase_768`", gate)
        self.assertIn("`m007_hooks_activated_phase_769`", gate)
        self.assertIn("`live_settlement_wiring_explicitly_deferred`", gate)
        self.assertIn("`first_non_genesis_validator_deployment_human_gate_named`", gate)
        self.assertIn("`capsule_v5_6_is_current_frontier`", gate)
        self.assertIn("`no_cdl_mutation_in_window_767_774`", gate)
        self.assertIn("Window `767-774` CLOSED via Phase `774` closure gate", planning)
        self.assertIn("Context Capsule v5.6", planning)

    def test_required_runtime_and_audit_markers_are_present(self) -> None:
        fast_path = _read(FAST_PATH)
        client = _read(CLIENT_PATH)
        validator = _read(VALIDATOR_PATH)
        audit = _read(AUDIT_PATH)
        lane = _read(LANE_DOC)
        capsule = _read(CAPSULE_PATH)
        self.assertIn("test_ejected_validator_sig_rejected_after_epoch_boundary", fast_path)
        self.assertNotIn("epoch: EpochSeq(1)", client)
        self.assertNotIn("unimplemented!()", validator)
        self.assertIn("phase_770_audit_cdl_017_constitutional_compliance=confirmed", audit)
        self.assertIn("SEC-004 CLOSED phase_768", lane)
        self.assertIn("M-007 hooks ACTIVATED phase_769", lane)
        self.assertIn("`capsule_v5_6_supersedes_v5_5`", capsule)

    def test_closure_gate_names_handoff_and_deferral_boundaries(self) -> None:
        text = _normalized(_read(GATE_PATH))
        self.assertIn("Window `803+` or later as planned", text)
        self.assertIn(
            "an operator must explicitly authorize the first non-Genesis validator admission after reviewing the CDL-017 production governance delivery design",
            text,
        )
        self.assertIn("that gate was not crossed in Window `767-774`", text)
        self.assertIn("row `5`, row `8`, and Option B are unaffected by this window", text)
        self.assertIn("live settlement wiring explicitly deferred", text)

    def test_integration_gate_file_passes(self) -> None:
        result = _run(
            [str(VENV_PYTHON), "-m", "pytest", str(INTEGRATION_GATE_TEST), "-q"],
            REPO_ROOT,
        )
        if result.returncode != 0:
            self.fail(
                "phase 772 integration gate no longer passes\n"
                f"stdout:\n{result.stdout}\n\nstderr:\n{result.stderr}"
            )
        self.assertIn("3 passed", result.stdout)

    def test_no_decision_log_mutation_in_window_commit_span(self) -> None:
        commits = _window_commits()
        subjects = " ".join(subject for _, subject in commits).lower()
        self.assertIn("phase 768", subjects)
        self.assertIn("phase 769", subjects)
        self.assertIn("phase 770", subjects)
        self.assertIn("phase 771", subjects)
        self.assertIn("phase 772", subjects)
        self.assertIn("phase 773", subjects)
        for commit_hash, _subject in commits:
            self.assertNotIn(DECISION_LOG, _changed_paths(commit_hash))


if __name__ == "__main__":
    unittest.main()
