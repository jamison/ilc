#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import json
import sys
from pathlib import Path

PROMPT_PATH = Path('docs/antigravity_tasks/antigravity_prompt__phase_606_g8_mempalace_internal_retrieval_adoption_and_boundary.md')
SPEC_PATH = Path('docs/specs/ilc_mempalace_internal_retrieval_adoption_and_boundary_606_v0.1.md')
GUIDELINES_PATH = Path('docs/specs/ilc_mempalace_agent_usage_and_prompt_guidelines_v0.1.md')
README_PATH = Path('docs/tools/mempalace/README.md')
MANIFEST_PATH = Path('docs/tools/mempalace/ilc_mempalace_corpus_manifest_v0.1.json')
AUDIT_PATH = Path('docs/research/ilc_mempalace_adoption_independent_audit_606_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')

SPEC_HEADINGS = (
    '## 1. Purpose and boundary',
    '## 2. Suitability assessment',
    '## 3. Authority-tier retrieval model',
    '## 4. Internal developer adoption plan',
    '## 5. Future local FAQ/oracle boundary',
    '## 6. Non-goals and deferred items',
)
SPEC_TOKENS = (
    'mempalace_is_retrieval_only_not_canonical_authority',
    'approved_context_pack_and_repo_canon_remain_authoritative',
    'external_payment_and_wallet_boundaries_remain_unchanged',
    'tier_a_canonical_sources_default_for_answers',
    'public_faq_oracle_must_not_answer_from_unvetted_historical_corpus',
)
GUIDELINES_HEADINGS = (
    '## 1. Operating rules',
    '## 2. Query protocol',
    '## 3. Prompt snippet',
    '## 4. Maintenance triggers',
    '## 5. Forbidden uses',
)
README_HEADINGS = (
    '## 1. Purpose',
    '## 2. Boundary rules',
    '## 3. Corpus tiers',
    '## 4. Suggested local workflow',
    '## 5. Query examples',
    '## 6. Maintenance notes',
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


def _read(path: Path) -> str:
    if not path.exists():
        raise AssertionError(f'missing_file:{path}')
    return path.read_text(encoding='utf-8')


def _require_all(text: str, items: tuple[str, ...], *, label: str) -> None:
    for item in items:
        if item not in text:
            raise AssertionError(f'missing_{label}:{item}')


def main() -> int:
    _read(PROMPT_PATH)
    spec = _read(SPEC_PATH)
    guidelines = _read(GUIDELINES_PATH)
    readme = _read(README_PATH)
    audit = _read(AUDIT_PATH)
    _read(DECISION_LOG_PATH)

    _require_all(spec, SPEC_HEADINGS, label='spec_heading')
    _require_all(spec, SPEC_TOKENS, label='spec_token')
    _require_all(guidelines, GUIDELINES_HEADINGS, label='guidelines_heading')
    _require_all(readme, README_HEADINGS, label='readme_heading')
    _require_all(audit, AUDIT_HEADINGS, label='audit_heading')

    for text in (spec, guidelines, readme, audit):
        for forbidden in FORBIDDEN_STRINGS:
            if forbidden in text:
                raise AssertionError(f'forbidden_scope:{forbidden}')

    manifest = json.loads(_read(MANIFEST_PATH))
    assert manifest['retrieval_only'] is True
    assert manifest['default_answer_tier'] == 'tier_a_canonical'
    assert manifest['public_oracle_default_tier'] == 'tier_a_canonical'
    assert manifest['historical_material_requires_label'] is True
    tiers = manifest['tiers']
    assert set(tiers) == {
        'tier_a_canonical',
        'tier_b_planning',
        'tier_c_evidence',
        'tier_d_historical',
    }
    for key in tiers:
        include = tiers[key].get('include')
        assert isinstance(include, list) and include
    forbidden_uses = manifest.get('forbidden_uses')
    assert isinstance(forbidden_uses, list) and forbidden_uses

    print('phase_606_mempalace_adoption_ok')
    return 0


if __name__ == '__main__':
    sys.exit(main())
