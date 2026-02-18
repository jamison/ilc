# ILC Genesis Distribution Surface Contract v0.1

Status: Phase-225 distribution validation artifact
Date: 2026-02-18
Locked sequence anchor: `docs/specs/ilc_genesis_packaging_distribution_sequence_222_229_v0.1.md`

## 1. Purpose

Define deterministic validation requirements proving the post-227 codebase is installable and operable for external distribution use prior to Phase-228 release artifact generation.

## 2. Contract checks

### 2.1 Packaging metadata and entry-point contract

`pyproject.toml` must define:
- project metadata (`name`, `version`, `requires-python`, `dependencies`),
- `project.scripts` entries for:
  - `ilc-mcp`,
  - `ilc-canon-verify`,
  - `ilc-canon-summary`,
  - `ilc-canon-export`,
  - `ilc-canon-bundle-validate`,
  - `ilc-canon-bundle-sign`,
  - `ilc-canon-bundle-pipeline`,
  - `ilc-canon-bundle-replay`,
  - `ilc-canon-cluster-a-replay-proof`.

### 2.2 Clean-venv install contract

From repository root, clean virtualenv install must pass:
- `pip install .`

### 2.3 Post-install import contract

In installed environment, both probes must pass:
- `import ilc_core`
- `from ilc_core.analysis.node_value_governance_conformance import evaluate_node_value_governance_conformance`

### 2.4 Console entry-point operability contract

In installed environment, each required script must run with `--help` and return success:
- `ilc-mcp`
- `ilc-canon-verify`
- `ilc-canon-summary`
- `ilc-canon-export`
- `ilc-canon-bundle-validate`
- `ilc-canon-bundle-sign`
- `ilc-canon-bundle-pipeline`
- `ilc-canon-bundle-replay`
- `ilc-canon-cluster-a-replay-proof`

### 2.5 Operator tooling script smoke contract

Repository-local scripts must run successfully:
- `python3 tools/genesis_boot.py`
- `python3 tools/demo_walkthrough.py`

## 3. Deterministic enforcement surface

This contract is enforced by:
- `tests/test_genesis_distribution_surface_phase_225.py`
- `tools/check_genesis_distribution_surface_phase_225.sh`

## 4. Explicit boundary to Phase 228

Phase 225 validates installability and operability only. It does not produce release artifacts.

Deferred to Phase 228:
- `sdist`/`wheel` build and install validation,
- checksum provenance,
- release notes artifact.

