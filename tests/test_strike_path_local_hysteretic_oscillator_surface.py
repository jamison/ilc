from __future__ import annotations

from pathlib import Path

from simulations import sim_treasury_scenario5_local_hysteretic_oscillator_recovery_rule as local_module

SURFACE_PATH = Path('simulations/sim_treasury_scenario5_local_hysteretic_oscillator_recovery_rule.py')
RESEARCH_NOTE_PATH = Path('docs/research/ilc_strike_path_local_hysteretic_oscillator_search_2026_03_27_v0.1.md')

EXPECTED_IDS = {
    'local_hysteretic_oscillator_t65_l45_g11_f12_e1_r2',
    'local_hysteretic_oscillator_t55_l30_g15_f04_e4_r4',
    'local_hysteretic_oscillator_t55_l30_g15_f20_e4_r4',
    'local_hysteretic_oscillator_t55_l30_g15_f04_e1_r4',
    'mixed_queue_and_production',
}


def test_local_surface_exists_and_exposes_expected_constants() -> None:
    assert SURFACE_PATH.exists()
    assert local_module.LOCAL_HYSTERETIC_OSCILLATOR_STATUS == 'implemented'
    assert local_module.LOCAL_HYSTERETIC_OSCILLATOR_LABEL == 'local_hysteretic_oscillator_recovery_rule'
    assert local_module.LOCAL_HYSTERETIC_OSCILLATOR_CODENAME == 'Shard Thermostat'
    assert local_module.CONTRAST_FIELD_SIZE == 4
    assert 'weak bounded local smoothing' in local_module.OPTIONAL_EXTENSION_NOTE
    assert 'randomized graph jumping' in local_module.RANDOM_JUMP_NOTE


def test_local_surface_registry_matches_frozen_field() -> None:
    assert set(local_module.CANDIDATE_REGISTRY) == EXPECTED_IDS
    assert set(local_module.list_candidate_ids()) == EXPECTED_IDS


def test_local_surface_returns_expected_outputs_and_diagnostics() -> None:
    leader = local_module.evaluate_recovery_rule('local_hysteretic_oscillator_t65_l45_g11_f12_e1_r2')
    weak = local_module.evaluate_recovery_rule('local_hysteretic_oscillator_t55_l30_g15_f04_e1_r4')
    diagnostics = local_module.get_candidate_diagnostics('local_hysteretic_oscillator_t65_l45_g11_f12_e1_r2')
    assert leader == {
        'organic_ecu_production_rate': 0.984,
        'pe_clamp_respect_rate': 0.919,
        'intervention_duration_epochs': 10,
        'intervention_cost_units': 0.226,
    }
    assert weak == {
        'organic_ecu_production_rate': 0.872,
        'pe_clamp_respect_rate': 0.861,
        'intervention_duration_epochs': 13,
        'intervention_cost_units': 0.244,
    }
    assert diagnostics == {
        'mean_enforce_share': 0.500,
        'mean_local_state': 0.248,
        'mean_switch_rate': 0.036,
    }


def test_research_note_records_threshold_clearance_and_extension_boundary() -> None:
    assert RESEARCH_NOTE_PATH.exists()
    text = RESEARCH_NOTE_PATH.read_text(encoding='utf-8')
    assert 'one rule for all shards' in text
    assert 'organic: `0.984 - 0.872 = 11.2pp`' in text
    assert 'clamp: `0.919 - 0.861 = 5.8pp`' in text
    assert 'weak bounded local smoothing' in text
    assert 'randomized graph jumping should not be part of the default local mechanism' in text
