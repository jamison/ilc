#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

PROMPT_PATH = Path('docs/antigravity_tasks/antigravity_prompt__phase_606_g8_fix2_mempalace_retrieval_correctness_and_manifest_hardening.md')
SPEC_PATH = Path('docs/specs/ilc_mempalace_retrieval_correctness_and_manifest_hardening_606_fix2_v0.1.md')
GUIDELINES_PATH = Path('docs/specs/ilc_mempalace_agent_usage_and_prompt_guidelines_v0.1.md')
README_PATH = Path('docs/tools/mempalace/README.md')
REQS_PATH = Path('docs/tools/mempalace/requirements-mempalace.txt')
MANIFEST_PATH = Path('docs/tools/mempalace/ilc_mempalace_corpus_manifest_v0.1.json')
AUDIT_PATH = Path('docs/research/ilc_mempalace_retrieval_correctness_and_manifest_hardening_independent_audit_606_fix2_v0.1.md')
INSTALL_SCRIPT_PATH = Path('tools/mempalace/install_local_mempalace_env.sh')
BUILD_SCRIPT_PATH = Path('tools/mempalace/build_tiered_corpus.py')
QUERY_SCRIPT_PATH = Path('tools/mempalace/query_tiered.py')
BRIEF_SCRIPT_PATH = Path('tools/mempalace/render_retrieval_brief.py')

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
AUDIT_HEADINGS = (
    '## 1. Audit scope',
    '## 2. Prompt-hardening review',
    '## 3. Adoption-packet findings',
    '## 4. Fixes applied before closure',
    '## 5. Residual risks',
)
FORBIDDEN_STRINGS = (
    'wallet write authority is now active',
    'native escrow is authorized',
    'market_liquidity is a core protocol lane',
    'node_market_structure is a core protocol lane',
)


def read(path: Path) -> str:
    if not path.exists():
        raise AssertionError(f'missing_file:{path}')
    return path.read_text(encoding='utf-8')


def require_all(text: str, items: tuple[str, ...], label: str) -> None:
    for item in items:
        if item not in text:
            raise AssertionError(f'missing_{label}:{item}')


def main() -> int:
    read(PROMPT_PATH)
    spec = read(SPEC_PATH)
    guidelines = read(GUIDELINES_PATH)
    readme = read(README_PATH)
    reqs = read(REQS_PATH)
    audit = read(AUDIT_PATH)
    install_script = read(INSTALL_SCRIPT_PATH)
    build_script = read(BUILD_SCRIPT_PATH)
    query_script = read(QUERY_SCRIPT_PATH)
    brief_script = read(BRIEF_SCRIPT_PATH)

    require_all(spec, SPEC_HEADINGS, 'spec_heading')
    require_all(spec, SPEC_TOKENS, 'spec_token')
    require_all(audit, AUDIT_HEADINGS, 'audit_heading')

    assert 'mempalace==3.1.0' in reqs
    assert 'chromadb==0.6.3' in reqs
    assert 'requirements-mempalace.txt' in install_script
    assert 'pip install -r "$REQS_PATH"' in install_script
    assert 'distance_metric' in query_script
    assert 'relevance_score' in query_script
    assert 'similarity' not in query_script
    assert 'optional' in build_script
    assert 'missing_optional_manifest_source:' in build_script
    assert 'simulations/...' in spec
    assert 'Wrapper scripts remain the supported ILC workflow' in guidelines
    assert 'wrapper scripts for reproducible' in readme
    assert 'relevance_score' in readme
    assert 'relevance_score' in guidelines
    assert 'if isinstance(entry, dict)' in brief_script

    manifest = json.loads(read(MANIFEST_PATH))
    tier_b = manifest['tiers']['tier_b_planning']['include']
    tier_d = manifest['tiers']['tier_d_historical']['include']
    assert len(tier_b) >= 10
    optional_entries = [entry for entry in tier_d if isinstance(entry, dict) and entry.get('optional')]
    assert optional_entries

    for text in (spec, guidelines, readme, audit):
        for forbidden in FORBIDDEN_STRINGS:
            if forbidden in text:
                raise AssertionError(f'forbidden_scope:{forbidden}')

    print('phase_606_fix2_mempalace_retrieval_correctness_and_manifest_hardening_ok')
    return 0


if __name__ == '__main__':
    sys.exit(main())
