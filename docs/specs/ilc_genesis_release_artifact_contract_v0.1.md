# ILC Genesis Release Artifact Contract v0.1

Status: Phase-228 release artifact contract
Date: 2026-02-18
Sequence anchor: `docs/specs/ilc_genesis_packaging_distribution_sequence_222_229_v0.1.md`

## 1. Purpose

Define deterministic checks for Genesis release artifact production and provenance prior to Phase-229 closure.

## 2. Artifact build contract

Release artifact build must produce both:
- `sdist` archive (`*.tar.gz`)
- `wheel` archive (`*.whl`)

Reference output path for Phase 228 evidence:
- `out/phase_228_release_artifacts/dist`

## 3. Artifact install validation contract

Both artifacts must be install-validated in clean virtual environments:
- install from wheel and run public import probe,
- install from sdist and run public import probe.

Required import probe:
- `from ilc_core.analysis.node_value_governance_conformance import evaluate_node_value_governance_conformance`

## 4. Checksum provenance contract

Phase 228 must publish SHA-256 checksums for each built artifact in:
- `docs/specs/ilc_genesis_release_artifact_provenance_phase_228_v0.1.md`

Provenance artifact must include:
- artifact filename,
- artifact type (`sdist` or `wheel`),
- SHA-256 digest,
- source output path.

## 5. Release notes boundary contract

Phase 228 release notes in `docs/specs/ilc_genesis_release_notes_v0.1.md` must include:
1. shipped Genesis scope,
2. explicit deferred scope,
3. SG-06 boundary clarity statement (Genesis is scoring + invariant layer, not the complete simulated consensus/economic control stack),
4. SG-07 simplification statement (flat refutation multiplier is intentional Genesis simplification relative to advanced simulated ranking-based variants).

## 6. Deterministic enforcement surface

This contract is enforced by:
- `tests/test_genesis_release_artifacts_phase_228.py`
- `tools/check_genesis_release_artifacts_phase_228.sh`

