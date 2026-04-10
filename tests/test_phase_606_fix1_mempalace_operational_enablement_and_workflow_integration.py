from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

PROMPT_PATH = Path('docs/antigravity_tasks/antigravity_prompt__phase_606_g8_fix1_mempalace_operational_enablement_and_workflow_integration.md')
SPEC_PATH = Path('docs/specs/ilc_mempalace_operational_enablement_and_workflow_integration_606_fix1_v0.1.md')
GUIDELINES_PATH = Path('docs/specs/ilc_mempalace_agent_usage_and_prompt_guidelines_v0.1.md')
README_PATH = Path('docs/tools/mempalace/README.md')
REQS_PATH = Path('docs/tools/mempalace/requirements-mempalace.txt')
WINDOW_SCHEMA_PATH = Path('docs/specs/ilc_window_guidance_doc_schema_v0.1.md')
AUDIT_PATH = Path('docs/research/ilc_mempalace_operational_enablement_independent_audit_606_fix1_v0.1.md')
MANIFEST_PATH = Path('docs/tools/mempalace/ilc_mempalace_corpus_manifest_v0.1.json')
CHECK_SCRIPT = Path('tools/check_phase_606_fix1_mempalace_operational_enablement.py')
INSTALL_SCRIPT = Path('tools/mempalace/install_local_mempalace_env.sh')
BUILD_SCRIPT = Path('tools/mempalace/build_tiered_corpus.py')
QUERY_SCRIPT = Path('tools/mempalace/query_tiered.py')
BRIEF_SCRIPT = Path('tools/mempalace/render_retrieval_brief.py')

SPEC_HEADINGS = (
    '## 1. Purpose and boundary',
    '## 2. Supported local runtime',
    '## 3. Tiered corpus build workflow',
    '## 4. Tiered query workflow',
    '## 5. Prompt and window-guidance integration',
    '## 6. Verification and maintenance',
)
SPEC_TOKENS = (
    'mempalace_local_runtime_requires_supported_python',
    'staged_tiered_corpus_build_is_required_for_authority_control',
    'prompt_and_window_guidance_workflow_may_use_rendered_retrieval_briefs',
    'mempalace_queries_must_not_override_direct_repo_reads',
    'main_repo_ci_must_not_require_mempalace_installation',
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


def test_operational_spec_exists_and_contains_required_headings_and_tokens() -> None:
    text = _read(SPEC_PATH)
    for heading in SPEC_HEADINGS:
        assert heading in text
    for token in SPEC_TOKENS:
        assert token in text


def test_install_script_contains_supported_python_order_and_version_pin() -> None:
    text = _read(INSTALL_SCRIPT)
    assert 'python3.12 python3.11 python3.10 python3.9' in text
    assert 'MEMPALACE_VERSION="3.1.0"' in text
    assert 'mempalace==${MEMPALACE_VERSION}' in text
    assert 'chromadb==0.6.3' in text


def test_stage_manifest_stages_files_and_writes_per_tier_config(tmp_path: Path) -> None:
    build = _load_module(BUILD_SCRIPT, 'phase606_fix1_build')
    repo_root = tmp_path / 'repo'
    repo_root.mkdir()
    (repo_root / 'docs').mkdir()
    (repo_root / 'docs' / 'a.md').write_text('A', encoding='utf-8')
    (repo_root / 'docs' / 'b.md').write_text('B', encoding='utf-8')
    manifest = {
        'tiers': {
            'tier_a_canonical': {'include': ['docs/a.md']},
            'tier_b_planning': {'include': ['docs/b.md']},
        }
    }
    staged_root = tmp_path / 'stage'
    summary = build.stage_manifest(manifest, repo_root=repo_root, staged_root=staged_root, mode='copy')
    assert (staged_root / 'tier_a_canonical' / 'mempalace.yaml').exists()
    assert (staged_root / 'tier_a_canonical' / 'docs' / 'a.md').read_text(encoding='utf-8') == 'A'
    assert summary['tier_b_planning']['file_count'] == 1


def test_build_mine_commands_use_tier_name_wings() -> None:
    build = _load_module(BUILD_SCRIPT, 'phase606_fix1_build_cmds')
    cmds = build.build_mine_commands('mempalace', Path('out/palace'), Path('out/stage'), ['tier_a_canonical', 'tier_b_planning'])
    assert '--wing' in cmds[0]
    assert cmds[0][0:4] == ['mempalace', '--palace', 'out/palace', 'mine']
    assert cmds[0][-3:] == ['--wing', 'tier_a_canonical', '--no-gitignore']
    assert 'tier_b_planning' in cmds[1]


def test_query_helper_preserves_tier_filters_and_source_paths(monkeypatch) -> None:
    query = _load_module(QUERY_SCRIPT, 'phase606_fix1_query')

    def fake_run(cmd, check, capture_output, text):
        assert cmd[0] == 'fake-python'
        payload = {
            'query': 'q',
            'wing': 'tier_a_canonical',
            'room': None,
            'results': [
                {
                    'text': 'hello',
                    'source_file': 'docs/specs/example.md',
                    'wing': 'tier_a_canonical',
                    'room': 'general',
                    'similarity': 0.9,
                },
                {
                    'text': 'other',
                    'source_file': 'docs/research/other.md',
                    'wing': 'tier_a_canonical',
                    'room': 'general',
                    'similarity': 0.1,
                }
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
    assert payload['wing'] == 'tier_a_canonical'
    assert payload['source_filters'] == ['docs/specs/']
    assert len(payload['results']) == 1
    assert payload['results'][0]['source_file'] == 'docs/specs/example.md'


def test_retrieval_brief_renderer_extracts_repo_paths_and_labels_tiers(tmp_path: Path) -> None:
    brief = _load_module(BRIEF_SCRIPT, 'phase606_fix1_brief')
    repo_root = tmp_path / 'repo'
    (repo_root / 'docs' / 'specs').mkdir(parents=True)
    (repo_root / 'docs' / 'specs' / 'x.md').write_text('x', encoding='utf-8')
    doc = tmp_path / 'prompt.md'
    doc.write_text('# Phase 606-G8 Example\n\nRead `docs/specs/x.md` first.\n', encoding='utf-8')
    manifest = {'tiers': {'tier_a_canonical': {'include': ['docs/specs/x.md']}}}
    rendered = brief.render_brief(doc, manifest, repo_root)
    assert '`docs/specs/x.md` (tier_a_canonical)' in rendered
    assert 'Advisory only. Direct repo reads remain authoritative.' in rendered


def test_check_script_passes_on_valid_artifacts() -> None:
    result = subprocess.run(['python3', str(CHECK_SCRIPT)], capture_output=True, check=True, text=True)
    assert 'phase_606_fix1_mempalace_operational_enablement_ok' in result.stdout


def test_no_artifact_widens_ilc_core_decision_log_wallet_authority_or_public_scope() -> None:
    texts = [
        _read(SPEC_PATH),
        _read(GUIDELINES_PATH),
        _read(README_PATH),
        _read(AUDIT_PATH),
        _read(WINDOW_SCHEMA_PATH),
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
