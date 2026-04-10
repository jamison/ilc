#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

PROMPT_PATH = Path('docs/antigravity_tasks/antigravity_prompt__phase_606_g8_fix1_mempalace_operational_enablement_and_workflow_integration.md')
SPEC_PATH = Path('docs/specs/ilc_mempalace_operational_enablement_and_workflow_integration_606_fix1_v0.1.md')
GUIDELINES_PATH = Path('docs/specs/ilc_mempalace_agent_usage_and_prompt_guidelines_v0.1.md')
README_PATH = Path('docs/tools/mempalace/README.md')
REQS_PATH = Path('docs/tools/mempalace/requirements-mempalace.txt')
WINDOW_SCHEMA_PATH = Path('docs/specs/ilc_window_guidance_doc_schema_v0.1.md')
AUDIT_PATH = Path('docs/research/ilc_mempalace_operational_enablement_independent_audit_606_fix1_v0.1.md')
INSTALL_SCRIPT_PATH = Path('tools/mempalace/install_local_mempalace_env.sh')
BUILD_SCRIPT_PATH = Path('tools/mempalace/build_tiered_corpus.py')
QUERY_SCRIPT_PATH = Path('tools/mempalace/query_tiered.py')
BRIEF_SCRIPT_PATH = Path('tools/mempalace/render_retrieval_brief.py')
MANIFEST_PATH = Path('docs/tools/mempalace/ilc_mempalace_corpus_manifest_v0.1.json')

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
    window_schema = read(WINDOW_SCHEMA_PATH)
    audit = read(AUDIT_PATH)
    install_script = read(INSTALL_SCRIPT_PATH)
    read(BUILD_SCRIPT_PATH)
    read(QUERY_SCRIPT_PATH)
    read(BRIEF_SCRIPT_PATH)

    require_all(spec, SPEC_HEADINGS, 'spec_heading')
    require_all(spec, SPEC_TOKENS, 'spec_token')
    require_all(audit, AUDIT_HEADINGS, 'audit_heading')
    assert 'python3.12' in install_script and 'python3.11' in install_script
    assert 'requirements-mempalace.txt' in install_script
    assert 'pip install -r "$REQS_PATH"' in install_script
    assert 'mempalace==3.1.0' in reqs
    assert 'chromadb==0.6.3' in reqs
    assert 'Python 3.9-3.12' in guidelines
    assert 'render_retrieval_brief.py' in guidelines
    assert 'render_retrieval_brief.py' in readme
    assert 'optional MemPalace retrieval appendix' in window_schema

    manifest = json.loads(read(MANIFEST_PATH))
    assert set(manifest['tiers']) == {
        'tier_a_canonical', 'tier_b_planning', 'tier_c_evidence', 'tier_d_historical'
    }

    for text in (spec, guidelines, readme, audit):
        for forbidden in FORBIDDEN_STRINGS:
            if forbidden in text:
                raise AssertionError(f'forbidden_scope:{forbidden}')

    print('phase_606_fix1_mempalace_operational_enablement_ok')
    return 0


if __name__ == '__main__':
    sys.exit(main())
