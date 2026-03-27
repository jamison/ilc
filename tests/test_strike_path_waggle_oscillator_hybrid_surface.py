from __future__ import annotations

from pathlib import Path

from simulations import sim_treasury_scenario5_waggle_oscillator_hybrid_recovery_rule as hybrid_module

SURFACE_PATH = Path('simulations/sim_treasury_scenario5_waggle_oscillator_hybrid_recovery_rule.py')
PROMOTION_NOTE_PATH = Path('docs/research/ilc_waggle_oscillator_hybrid_formal_lane_promotion_2026_03_27_v0.1.md')

EXPECTED_IDS = {
    'hybrid_nonlinear_curve_k58_g18_f22_frontier_first_p5_a09_enforce_first_rq100_ab100_dc060_cp095_ss160_rb050_bs150_adj100',
    'hybrid_nonlinear_curve_k58_g18_f22_frontier_first_p5_a09_enforce_first_rq100_ab095_dc060_cp095_ss160_rb050_bs150_adj090',
    'hybrid_nonlinear_curve_k58_g18_f22_frontier_first_p5_a09_enforce_first_rq095_ab095_dc060_cp095_ss160_rb055_bs150_adj090',
    'hybrid_nonlinear_curve_k58_g18_f22_frontier_first_p5_a09_enforce_first_rq095_ab090_dc060_cp095_ss160_rb050_bs150_adj090',
    'hybrid_nonlinear_curve_k58_g18_f22_frontier_first_p5_a09_enforce_first_rq105_ab095_dc060_cp095_ss160_rb050_bs150_adj090',
    'hybrid_nonlinear_curve_k58_g18_f22_frontier_first_p5_a09_enforce_first_rq100_ab100_dc060_cp095_ss160_rb055_bs150_adj090',
    'mixed_queue_and_production',
}


def test_hybrid_surface_exists_and_exposes_expected_constants() -> None:
    assert SURFACE_PATH.exists()
    assert hybrid_module.HYBRID_MECHANISM_STATUS == 'strike_path_frozen'
    assert hybrid_module.HYBRID_MECHANISM_LABEL == 'waggle_oscillator_hybrid_recovery_rule'
    assert hybrid_module.HYBRID_CODENAME == 'Waggle-Oscillator Hybrid'
    assert hybrid_module.CONSTRAINED_FIELD_SIZE == 6
    assert set(hybrid_module.REQUIRED_OUTPUT_KEYS) == {
        'organic_ecu_production_rate',
        'pe_clamp_respect_rate',
        'intervention_duration_epochs',
        'intervention_cost_units',
    }
    assert set(hybrid_module.GRAPH_DIAGNOSTIC_KEYS) == {
        'frontier_mean_enforcement',
        'core_mean_enforcement',
        'frontier_core_gradient',
    }


def test_hybrid_surface_registry_matches_frozen_field() -> None:
    assert set(hybrid_module.CANDIDATE_REGISTRY) == EXPECTED_IDS
    assert set(hybrid_module.list_candidate_ids()) == EXPECTED_IDS


def test_hybrid_surface_returns_expected_outputs_and_diagnostics() -> None:
    leader_id = 'hybrid_nonlinear_curve_k58_g18_f22_frontier_first_p5_a09_enforce_first_rq100_ab100_dc060_cp095_ss160_rb050_bs150_adj100'
    leader = hybrid_module.get_candidate_definition(leader_id)
    outputs = hybrid_module.evaluate_recovery_rule(leader_id, leader.parameters)
    diagnostics = hybrid_module.get_candidate_diagnostics(leader_id)
    assert outputs == {
        'organic_ecu_production_rate': 0.992,
        'pe_clamp_respect_rate': 0.933,
        'intervention_duration_epochs': 10,
        'intervention_cost_units': 0.277,
    }
    assert diagnostics == {
        'frontier_mean_enforcement': 0.697,
        'core_mean_enforcement': 0.426,
        'frontier_core_gradient': 0.272,
    }


def test_hybrid_formal_lane_promotion_note_exists() -> None:
    assert PROMOTION_NOTE_PATH.exists()
    text = PROMOTION_NOTE_PATH.read_text(encoding='utf-8')
    assert 'formal mechanism lane' in text
    assert 'simulations/sim_treasury_scenario5_waggle_oscillator_hybrid_recovery_rule.py' in text
    assert 'candidate neighborhood' in text
