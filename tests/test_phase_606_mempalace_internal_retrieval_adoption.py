from __future__ import annotations

import json
import subprocess
from pathlib import Path

SPEC_PATH = Path('docs/specs/ilc_mempalace_internal_retrieval_adoption_and_boundary_606_v0.1.md')
GUIDELINES_PATH = Path('docs/specs/ilc_mempalace_agent_usage_and_prompt_guidelines_v0.1.md')
README_PATH = Path('docs/tools/mempalace/README.md')
MANIFEST_PATH = Path('docs/tools/mempalace/ilc_mempalace_corpus_manifest_v0.1.json')
AUDIT_PATH = Path('docs/research/ilc_mempalace_adoption_independent_audit_606_v0.1.md')
CHECK_SCRIPT = Path('tools/check_phase_606_mempalace_adoption.py')
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
FORBIDDEN_SCOPE_STRINGS = (
    'wallet write authority is now active',
    'native escrow is authorized',
    'market_liquidity is a core protocol lane',
    'node_market_structure is a core protocol lane',
)


def _read(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def test_adoption_spec_exists_and_contains_all_required_headings() -> None:
    text = _read(SPEC_PATH)
    for heading in SPEC_HEADINGS:
        assert heading in text


def test_adoption_spec_contains_all_required_spec_tokens() -> None:
    text = _read(SPEC_PATH)
    for token in SPEC_TOKENS:
        assert token in text


def test_guidelines_doc_exists_and_contains_required_headings_and_core_rules() -> None:
    text = _read(GUIDELINES_PATH)
    for heading in GUIDELINES_HEADINGS:
        assert heading in text
    assert 'MemPalace retrieval never overrides ratified or accepted repo artifacts' in text
    assert 'verify against the authoritative tier' in text
    assert 'must not treat retrieval results as canon' in text or 'must not treat retrieval results as canon without source checking' in text


def test_readme_exists_and_contains_required_headings_and_optional_tooling_rule() -> None:
    text = _read(README_PATH)
    for heading in README_HEADINGS:
        assert heading in text
    assert 'MemPalace is optional internal tooling' in text
    assert 'tier-A corpus and repo canon' in text


def test_corpus_manifest_parses_as_json_and_contains_required_tiers_and_keys() -> None:
    manifest = json.loads(_read(MANIFEST_PATH))
    assert manifest['retrieval_only'] is True
    assert manifest['default_answer_tier'] == 'tier_a_canonical'
    assert manifest['public_oracle_default_tier'] == 'tier_a_canonical'
    assert manifest['historical_material_requires_label'] is True
    assert set(manifest['tiers']) == {
        'tier_a_canonical',
        'tier_b_planning',
        'tier_c_evidence',
        'tier_d_historical',
    }
    for tier in manifest['tiers'].values():
        assert tier['include']
    assert manifest['forbidden_uses']


def test_independent_audit_doc_exists_and_records_hardening_findings_fixes_and_risks() -> None:
    text = _read(AUDIT_PATH)
    for heading in AUDIT_HEADINGS:
        assert heading in text
    assert 'context-pack downgrade rejected' in text
    assert 'MemPalace-as-canon drift rejected' in text
    assert 'wallet-authority widening rejected' in text
    assert 'native-escrow defaulting rejected' in text


def test_check_script_passes_on_valid_artifacts() -> None:
    result = subprocess.run(
        ['python3', str(CHECK_SCRIPT)],
        capture_output=True,
        check=True,
        text=True,
    )
    assert 'phase_606_mempalace_adoption_ok' in result.stdout


def test_no_artifact_widens_ilc_core_decision_log_wallet_authority_or_public_scope() -> None:
    texts = [
        _read(SPEC_PATH),
        _read(GUIDELINES_PATH),
        _read(README_PATH),
        _read(AUDIT_PATH),
    ]
    _read(DECISION_LOG_PATH)
    for text in texts:
        for forbidden in FORBIDDEN_SCOPE_STRINGS:
            assert forbidden not in text
        assert 'modify `ilc_core/`' not in text
        assert 'mutate the decision log' not in text
        assert 'wallet authority is widened' not in text
