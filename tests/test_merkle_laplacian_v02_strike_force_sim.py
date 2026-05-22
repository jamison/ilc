import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/sim/sim_merkle_laplacian_v02_strike_force.py"
RESULTS_JSON = (
    ROOT
    / "docs/sims/sim_merkle_laplacian_v02/strike_force_results_2026_05_22_v0.1.json"
)
RESULTS_MD = (
    ROOT
    / "docs/sims/sim_merkle_laplacian_v02/strike_force_results_2026_05_22_v0.1.md"
)
PAPER = ROOT / "docs/research/ilc_merkle_laplacian_dual_commitment_paper_draft_v0.2.md"


def test_strike_force_script_replays_to_temp_outputs(tmp_path: Path) -> None:
    json_out = tmp_path / "results.json"
    md_out = tmp_path / "results.md"

    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--json-out",
            str(json_out),
            "--md-out",
            str(md_out),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "sim_spectral_01_rerun_quantized_smallest_k_viable=true" in completed.stdout
    assert json_out.exists()
    assert md_out.exists()

    data = json.loads(json_out.read_text(encoding="utf-8"))
    assert data["overall_verdict"] == "research_positive_with_publication_gates_remaining"
    assert set(data["sims"]) == {
        "SIM-SPECTRAL-01-RERUN",
        "SIM-SPECTRAL-COST-01",
        "SIM-POSK-01",
        "SIM-DUALCOMMIT-01",
        "SIM-DIRECTED-CLOSURE-01",
        "SIM-REUSE-STABILITY-01",
    }


def test_committed_results_record_all_required_gate_tokens() -> None:
    data = json.loads(RESULTS_JSON.read_text(encoding="utf-8"))
    text = RESULTS_MD.read_text(encoding="utf-8")

    required_tokens = {
        "sim_spectral_01_rerun_quantized_smallest_k_viable=true",
        "sim_spectral_cost_01_dense_10k_fast_path_viable=false",
        "sim_posk_01_copy_attack_blocked=true",
        "sim_dualcommit_01_layer_separation_confirmed=true",
        "sim_directed_closure_01_direction_lost_in_s=true",
        "sim_reuse_stability_01_linear_unsafe_log_capped_preferred=true",
    }
    assert set(data["gate_tokens"]) == required_tokens
    for token in required_tokens:
        assert token in text


def test_posk_result_binds_edge_set_root_and_keeps_fetch_caveat() -> None:
    posk = json.loads(RESULTS_JSON.read_text(encoding="utf-8"))["sims"]["SIM-POSK-01"]

    assert posk["edge_set_root_bound"] is True
    assert posk["copy_the_quorum_value_blocked"] is True
    assert posk["partial_graph_detected"] is True
    assert posk["pass_rates"]["copy_global_s_hash"] == 0.0
    assert posk["pass_rates"]["copy_global_lambda2_only"] == 0.0
    assert posk["pass_rates"]["partial_80_percent_graph"] == 0.0
    assert posk["post_challenge_full_fetch_caveat"] is True


def test_strike_force_updates_paper_posk_definition() -> None:
    text = PAPER.read_text(encoding="utf-8")

    assert "*R_c* = SHA256(sort(hyperedge_declaration_hash(e) for e in G_c(*t*)))" in text
    assert "Binding *R_c* prevents a stale or partial node" in text
    assert "both the prover's *R_c* and spectrum-bound hash match" in text
