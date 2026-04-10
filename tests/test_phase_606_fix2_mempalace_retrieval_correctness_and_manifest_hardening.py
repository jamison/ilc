from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

PROMPT_PATH = Path('docs/antigravity_tasks/antigravity_prompt__phase_606_g8_fix2_mempalace_retrieval_correctness_and_manifest_hardening.md')
SPEC_PATH = Path('docs/specs/ilc_mempalace_retrieval_correctness_and_manifest_hardening_606_fix2_v0.1.md')
GUIDELINES_PATH = Path('docs/specs/ilc_mempalace_agent_usage_and_prompt_guidelines_v0.1.md')
README_PATH = Path('docs/tools/mempalace/README.md')
REQS_PATH = Path('docs/tools/mempalace/requirements-mempalace.txt')
MANIFEST_PATH = Path('docs/tools/mempalace/ilc_mempalace_corpus_manifest_v0.1.json')
AUDIT_PATH = Path('docs/research/ilc_mempalace_retrieval_correctness_and_manifest_hardening_independent_audit_606_fix2_v0.1.md')
CHECK_SCRIPT = Path('tools/check_phase_606_fix2_mempalace_retrieval_correctness_and_manifest_hardening.py')
INSTALL_SCRIPT = Path('tools/mempalace/install_local_mempalace_env.sh')
BUILD_SCRIPT = Path('tools/mempalace/build_tiered_corpus.py')
QUERY_SCRIPT = Path('tools/mempalace/query_tiered.py')
BRIEF_SCRIPT = Path('tools/mempalace/render_retrieval_brief.py')

SPEC_HEADINGS = (
    '## 1. Purpose and bounded scope',
    '## 2. Retrieval score correctness',
    '## 3. Runtime dependency single source of truth',
    '## 4. Manifest resilience for local-only historical material',
    '## 5. Planning-tier expansion and retrieval-brief coverage',
    '## 6. Verification and maintenance',
)
SPEC_TOKENS = (
    'distance_values_must_not_be_labeled_as_raw_similarity',
    'requirements_file_is_single_source_of_truth_for_mempalace_runtime_pins',
    'optional_manifest_entries_allow_local_historical_absence_without_tier_failure',
    'tier_b_planning_manifest_expansion_is_required_for_window_606_plus_utility',
    'retrieval_brief_path_extraction_must_cover_simulations_and_other_repo_files',
)
FORBIDDEN_SCOPE_STRINGS = (
    'wallet write authority is now active',
    'native escrow is authorized',
    'market_liquidity is a core protocol lane',
    'node_market_structure is a core protocol lane',
)


def _read(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_fix2_spec_exists_and_contains_required_headings_and_tokens() -> None:
    text = _read(SPEC_PATH)
    for heading in SPEC_HEADINGS:
        assert heading in text
    for token in SPEC_TOKENS:
        assert token in text


def test_requirements_file_is_single_source_of_truth_for_runtime_pins() -> None:
    reqs = _read(REQS_PATH)
    install = _read(INSTALL_SCRIPT)
    assert 'mempalace==3.1.0' in reqs
    assert 'chromadb==0.6.3' in reqs
    assert 'requirements-mempalace.txt' in install
    assert 'pip install -r "$REQS_PATH"' in install
    assert 'MEMPALACE_VERSION=' not in install


def test_query_helper_emits_distance_and_relevance_score_without_similarity_label(monkeypatch) -> None:
    query = _load_module(QUERY_SCRIPT, 'phase606_fix2_query_score')

    def fake_run(cmd, check, capture_output, text):
        payload = {
            'query': 'q',
            'wing': 'tier_b_planning',
            'room': None,
            'distance_metric': 'l2',
            'results': [
                {
                    'text': 'hello',
                    'source_file': 'docs/specs/example.md',
                    'wing': 'tier_b_planning',
                    'room': 'general',
                    'distance': 2.75,
                    'relevance_score': 0.266667,
                }
            ],
        }
        return subprocess.CompletedProcess(cmd, 0, stdout=json.dumps(payload), stderr='')

    monkeypatch.setattr(query.subprocess, 'run', fake_run)
    payload = query.query_memories(
        'fake-python',
        palace_path=Path('palace'),
        query='q',
        tier='tier_b_planning',
        room=None,
        results=1,
        source_filters=None,
    )
    result = payload['results'][0]
    assert result['distance'] == 2.75
    assert result['relevance_score'] == 0.266667
    assert 'similarity' not in result


def test_query_helper_reports_metric_metadata_and_preserves_source_filters(monkeypatch) -> None:
    query = _load_module(QUERY_SCRIPT, 'phase606_fix2_query_filter')

    def fake_run(cmd, check, capture_output, text):
        payload = {
            'query': 'q',
            'wing': 'tier_a_canonical',
            'room': None,
            'distance_metric': 'cosine',
            'results': [
                {
                    'text': 'hello',
                    'source_file': 'docs/specs/example.md',
                    'wing': 'tier_a_canonical',
                    'room': 'general',
                    'distance': 0.18,
                    'relevance_score': 0.847458,
                },
                {
                    'text': 'other',
                    'source_file': 'docs/research/other.md',
                    'wing': 'tier_a_canonical',
                    'room': 'general',
                    'distance': 1.82,
                    'relevance_score': 0.35461,
                },
            ],
        }
        return subprocess.CompletedProcess(cmd, 0, stdout=json.dumps(payload), stderr='')

    monkeypatch.setattr(query.subprocess, 'run', fake_run)
    payload = query.query_memories(
        'fake-python',
        palace_path=Path('palace'),
        query='q',
        tier='tier_a_canonical',
        room=None,
        results=3,
        source_filters=['docs/specs/'],
    )
    assert payload['distance_metric'] == 'cosine'
    assert payload['source_filters'] == ['docs/specs/']
    assert len(payload['results']) == 1
    assert payload['results'][0]['source_file'] == 'docs/specs/example.md'


def test_stage_manifest_accepts_optional_entries_and_records_warnings(tmp_path: Path) -> None:
    build = _load_module(BUILD_SCRIPT, 'phase606_fix2_build_optional')
    repo_root = tmp_path / 'repo'
    repo_root.mkdir()
    (repo_root / 'docs').mkdir()
    (repo_root / 'docs' / 'a.md').write_text('A', encoding='utf-8')
    manifest = {
        'tiers': {
            'tier_d_historical': {
                'include': [
                    'docs/a.md',
                    {'path': 'out/missing.md', 'optional': True},
                ]
            }
        }
    }
    staged_root = tmp_path / 'stage'
    summary = build.stage_manifest(manifest, repo_root=repo_root, staged_root=staged_root, mode='copy')
    assert summary['tier_d_historical']['file_count'] == 1
    assert summary['tier_d_historical']['warnings'] == ['missing_optional_manifest_source:out/missing.md']


def test_stage_manifest_fails_clearly_on_missing_required_files_and_malformed_tiers(tmp_path: Path) -> None:
    build = _load_module(BUILD_SCRIPT, 'phase606_fix2_build_errors')
    repo_root = tmp_path / 'repo'
    repo_root.mkdir()
    staged_root = tmp_path / 'stage'

    missing_required_manifest = {
        'tiers': {'tier_a_canonical': {'include': ['docs/missing.md']}},
    }
    malformed_tier_manifest = {
        'tiers': {'tier_a_canonical': {}},
    }

    try:
        build.stage_manifest(malformed_tier_manifest, repo_root=repo_root, staged_root=staged_root, mode='copy')
    except ValueError as exc:
        assert 'tier_missing_include:tier_a_canonical' in str(exc)
    else:
        raise AssertionError('expected ValueError for missing include')

    try:
        build.stage_manifest(missing_required_manifest, repo_root=repo_root, staged_root=staged_root, mode='copy')
    except FileNotFoundError as exc:
        assert 'missing_manifest_source:docs/missing.md' in str(exc)
    else:
        raise AssertionError('expected FileNotFoundError for missing required file')


def test_manifest_contains_tier_b_expansion_and_optional_tier_d_history() -> None:
    manifest = json.loads(_read(MANIFEST_PATH))
    tier_b = manifest['tiers']['tier_b_planning']['include']
    tier_d = manifest['tiers']['tier_d_historical']['include']
    assert len(tier_b) >= 10
    assert 'docs/research/ilc_rc_gap_context_pack_v0.1.md' in tier_b
    assert 'docs/specs/ilc_phase_596_605_sequence_lock_v0.1.md' in tier_b
    optional_paths = {entry['path'] for entry in tier_d if isinstance(entry, dict) and entry.get('optional')}
    assert 'out/thread_dredge_20260409/thread_context_triage_memo.md' in optional_paths
    assert 'out/thread_dredge_20260409/thread_memory_context_summary.md' in optional_paths


def test_retrieval_brief_renderer_captures_repo_relative_simulation_paths(tmp_path: Path) -> None:
    brief = _load_module(BRIEF_SCRIPT, 'phase606_fix2_brief')
    repo_root = tmp_path / 'repo'
    (repo_root / 'simulations').mkdir(parents=True)
    (repo_root / 'simulations' / 'sim_example.py').write_text('print("x")\n', encoding='utf-8')
    doc = tmp_path / 'prompt.md'
    doc.write_text('# Phase 606-G8 Fix2\n\nCheck `simulations/sim_example.py` now.\n', encoding='utf-8')
    manifest = {'tiers': {'tier_d_historical': {'include': ['simulations/sim_example.py']}}}
    rendered = brief.render_brief(doc, manifest, repo_root)
    assert '`simulations/sim_example.py` (tier_d_historical)' in rendered


def test_check_script_passes_on_valid_artifacts() -> None:
    result = subprocess.run(['python3', str(CHECK_SCRIPT)], capture_output=True, check=True, text=True)
    assert 'phase_606_fix2_mempalace_retrieval_correctness_and_manifest_hardening_ok' in result.stdout


def test_no_artifact_widens_ilc_core_decision_log_wallet_authority_or_public_scope() -> None:
    texts = [
        _read(SPEC_PATH),
        _read(GUIDELINES_PATH),
        _read(README_PATH),
        _read(AUDIT_PATH),
    ]
    _read(PROMPT_PATH)
    _read(REQS_PATH)
    _read(MANIFEST_PATH)
    for text in texts:
        for forbidden in FORBIDDEN_SCOPE_STRINGS:
            assert forbidden not in text
        assert 'modify `ilc_core/`' not in text
        assert 'mutate the decision log' not in text
        assert 'wallet authority is widened' not in text
