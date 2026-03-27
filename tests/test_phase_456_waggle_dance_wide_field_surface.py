from __future__ import annotations

from pathlib import Path

from simulations import sim_treasury_scenario5_waggle_dance_wide_field as wide_field_module

WIDE_FIELD_MODULE_PATH = Path('simulations/sim_treasury_scenario5_waggle_dance_wide_field.py')
CHARACTERIZATION_DOC_PATH = Path('docs/research/ilc_waggle_dance_wide_field_characterization_v0.1.md')

EXPECTED_CANDIDATE_IDS = {
    # Group 1 — Structural archetypes
    'nonlinear_curve_k20_g06_f22_frontier_first',
    'nonlinear_curve_k20_g35_f22_frontier_first',
    'nonlinear_curve_k20_g18_f22_frontier_first',
    'nonlinear_curve_k85_g06_f22_frontier_first',
    'nonlinear_curve_k85_g35_f22_frontier_first',
    'nonlinear_curve_k85_g18_f22_frontier_first',
    'nonlinear_curve_k40_g06_f22_frontier_first',
    'nonlinear_curve_k75_g35_f22_frontier_first',
    # Group 2 — Release floor sensitivity
    'nonlinear_curve_k58_g18_f06_frontier_first',
    'nonlinear_curve_k58_g18_f44_frontier_first',
    'nonlinear_curve_k40_g15_f06_frontier_first',
    'nonlinear_curve_k75_g22_f44_frontier_first',
    # Group 3 — Bias mode variants
    'nonlinear_curve_k58_g18_f22_uniform',
    'nonlinear_curve_k58_g18_f22_backpressure_first',
    'nonlinear_curve_k40_g15_f18_backpressure_first',
    # Group 4 — Extreme weak candidates
    'nonlinear_curve_k85_g35_f44_backpressure_first',
    'nonlinear_curve_k20_g35_f06_backpressure_first',
    'nonlinear_curve_k85_g06_f06_uniform',
    # Anchor
    'mixed_queue_and_production',
}

REQUIRED_DOC_HEADINGS = (
    '## 1. Purpose and scope',
    '## 2. Surrogate model basis',
    '## 3. Wide-field parameter grid surveyed',
    '## 4. Organic rate distribution',
    '## 5. Structural diversity rationale',
    '## 6. Mechanism response surface summary',
    '## 7. Limitation note',
    '## 8. Connection to Phase 458 prelock',
)


def test_wide_field_module_exposes_required_surface() -> None:
    assert WIDE_FIELD_MODULE_PATH.exists()
    assert hasattr(wide_field_module, 'evaluate_recovery_rule')
    assert callable(wide_field_module.evaluate_recovery_rule)
    assert hasattr(wide_field_module, 'list_candidate_ids')
    assert callable(wide_field_module.list_candidate_ids)
    assert hasattr(wide_field_module, 'get_candidate_definition')
    assert callable(wide_field_module.get_candidate_definition)
    assert wide_field_module.NONLINEAR_CONTROL_CURVE_STATUS == 'implemented'
    assert wide_field_module.WAGGLE_DANCE_CODENAME == 'Waggle Dance'
    assert wide_field_module.WIDE_FIELD_CANDIDATE_COUNT == 18
    assert wide_field_module.WIDE_FIELD_ORGANIC_RANGE == (0.873, 0.969)
    assert 'Legacy production-band carry-forwards' in wide_field_module.WIDE_FIELD_BOUNDARY_STATEMENT


def test_wide_field_candidate_registry_contains_expected_ids() -> None:
    assert set(wide_field_module.CANDIDATE_REGISTRY) == EXPECTED_CANDIDATE_IDS
    assert set(wide_field_module.list_candidate_ids()) == EXPECTED_CANDIDATE_IDS
    diverse_ids = EXPECTED_CANDIDATE_IDS - {'mixed_queue_and_production'}
    assert len(diverse_ids) == wide_field_module.WIDE_FIELD_CANDIDATE_COUNT


def test_all_wide_field_candidates_return_valid_metrics() -> None:
    for candidate_id in EXPECTED_CANDIDATE_IDS:
        candidate = wide_field_module.get_candidate_definition(candidate_id)
        outputs = wide_field_module.evaluate_recovery_rule(candidate_id, candidate.parameters)
        assert set(outputs) == set(wide_field_module.REQUIRED_OUTPUT_KEYS), (
            f'missing_output_keys:{candidate_id}'
        )
        assert 0.0 <= outputs['organic_ecu_production_rate'] <= 1.0, (
            f'organic_out_of_range:{candidate_id}'
        )
        assert 0.0 <= outputs['pe_clamp_respect_rate'] <= 1.0, (
            f'clamp_out_of_range:{candidate_id}'
        )
        assert outputs['intervention_duration_epochs'] > 0, (
            f'duration_not_positive:{candidate_id}'
        )
        assert outputs['intervention_cost_units'] >= 0, (
            f'cost_negative:{candidate_id}'
        )
    organic_values = [
        wide_field_module.evaluate_recovery_rule(cid)['organic_ecu_production_rate']
        for cid in EXPECTED_CANDIDATE_IDS - {'mixed_queue_and_production'}
    ]
    assert min(organic_values) == wide_field_module.WIDE_FIELD_ORGANIC_RANGE[0]
    assert max(organic_values) == wide_field_module.WIDE_FIELD_ORGANIC_RANGE[1]


def test_characterization_doc_exists_and_contains_required_headings() -> None:
    assert CHARACTERIZATION_DOC_PATH.exists()
    text = CHARACTERIZATION_DOC_PATH.read_text(encoding='utf-8')
    for heading in REQUIRED_DOC_HEADINGS:
        assert heading in text, f'missing_heading:{heading}'
    assert 'blocker_1_fix_8_verdict=cleared' in text
    assert 'oscillator evidence chain remains controlling' in text
    assert 'single smooth peak' in text
