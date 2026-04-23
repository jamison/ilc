from __future__ import annotations

import subprocess
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = REPO_ROOT / "ilc_consensus" / "src" / "validator.rs"
NODE_PATH = REPO_ROOT / "ilc_consensus" / "src" / "node.rs"
CLIENT_PATH = REPO_ROOT / "ilc_consensus" / "src" / "testnet_client_main.rs"
LAYER2_SPEC = REPO_ROOT / "docs" / "specs" / "ilc_row_5_layer2_mechanism_implementation_778_v0.1.md"
RUN1_ARTIFACT = REPO_ROOT / "docs" / "research" / "ilc_sim_leakage_01_run1_post_layer1_results_777_v0.1.md"
RUN2_ARTIFACT = REPO_ROOT / "docs" / "research" / "ilc_sim_leakage_01_run2_post_both_layers_results_779_v0.1.md"
EVAL_ARTIFACT = REPO_ROOT / "docs" / "specs" / "ilc_row_5_evaluation_780_v0.1.md"
CAPSULE_PATH = REPO_ROOT / "docs" / "specs" / "ilc_antigravity_context_capsule_v5.7.md"
GATE_PATH = REPO_ROOT / "docs" / "specs" / "ilc_window_775_782_closure_gate_782_v0.1.md"
PLANNING_INDEX = REPO_ROOT / "docs" / "PLANNING_INDEX.md"
DECISION_LOG = REPO_ROOT / "docs" / "specs" / "ilc_constitutional_decision_log_v0.1.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    return " ".join(text.split())


def _run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


class TestWindow775782ClosureGate(unittest.TestCase):
    def test_output_files_and_required_tokens_exist(self) -> None:
        gate = _read(GATE_PATH)
        planning = _read(PLANNING_INDEX)
        for marker in (
            "`window_775_782_closed`",
            "`row_5_remediation_complete_phase_780_verdict_recorded`",
            "`layer_1_log_hygiene_deployed`",
            "`layer_2_batching_multi_relay_deployed`",
            "`sim_leakage_01_rerun_complete_two_iterations`",
            "`zk_nullifier_path_named_in_closure`",
            "`no_cdl_mutation_in_window_775_782`",
            "`capsule_v5_7_is_current_frontier`",
        ):
            self.assertIn(marker, gate)
        self.assertIn("Latest closed main-lane closure (775-782)", planning)
        self.assertIn("Window 775-782 closed through Phase `782`", planning)
        self.assertIn("Context Capsule v5.9", planning)

    def test_required_runtime_and_artifact_markers_are_present(self) -> None:
        validator = _read(VALIDATOR_PATH)
        node = _read(NODE_PATH)
        client = _read(CLIENT_PATH)
        layer2 = _read(LAYER2_SPEC)
        run1 = _read(RUN1_ARTIFACT)
        run2 = _read(RUN2_ARTIFACT)
        evaluation = _read(EVAL_ARTIFACT)
        capsule = _read(CAPSULE_PATH)
        self.assertIn("sec_warn_bft_fault_tolerance_zero", validator)
        self.assertIn("sec_warn_full_transfer_epoch_defaulted_to_1", client)
        self.assertIn("layer1_agentid_log_hygiene_applied", node)
        self.assertIn("layer2_batching_multi_relay_implemented", layer2)
        self.assertIn("sim_leakage_01_run1_post_layer1_complete", run1)
        self.assertIn("sim_leakage_01_run2_post_both_layers_complete", run2)
        self.assertIn("row_5_honest_nonclosure_verdict=bands_not_met", evaluation)
        self.assertIn("`capsule_v5_7_supersedes_v5_6`", capsule)

    def test_zk_note_and_observability_floor_are_named(self) -> None:
        layer2 = _normalized(_read(LAYER2_SPEC))
        evaluation = _normalized(_read(EVAL_ARTIFACT))
        gate = _normalized(_read(GATE_PATH))
        self.assertIn("TransferCertificate carries no client-side timing or routing metadata", layer2)
        self.assertIn("receipts remain discoverable", evaluation)
        self.assertIn("lineage remains legible", evaluation)
        self.assertIn("challengeability remains preserved", evaluation)
        self.assertIn("bounded human auditability remains intact", evaluation)
        self.assertIn("ZK nullifier / selective-disclosure path", gate)

    def test_decision_log_is_untouched_in_current_window_worktree(self) -> None:
        result = _run(["git", "diff", "--name-only", "--", str(DECISION_LOG.relative_to(REPO_ROOT))])
        if result.returncode != 0:
            self.fail(
                "failed to inspect decision-log diff\n"
                f"stdout:\n{result.stdout}\n\nstderr:\n{result.stderr}"
            )
        self.assertEqual(result.stdout.strip(), "")


if __name__ == "__main__":
    unittest.main()
