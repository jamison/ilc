# ILC Genesis Release Notes v0.1

Status: Phase-228 release notes artifact
Date: 2026-02-18
Release baseline: post-Phase-225 distribution validation, post-Phase-227 open-CDL remediation scope lock

## Shipped in Genesis v0.1

- Deterministic scoring/reward/invariant stack with contractual gates:
  - refutation profitability invariant,
  - path-lift counterfactual harness,
  - reuse-diversity anti-Sybil weighting,
  - freshness gate with Genesis exemption,
  - Genesis accrual governor cap/taper checks,
  - consolidated node-value/governance conformance surface.
- Packaging/installability surface validated (`pip install .`, imports, CLI entry-point help probes).
- Release artifacts produced and checksum-provenanced:
  - `ilc_core-0.1.0.tar.gz` (sdist)
  - `ilc_core-0.1.0-py3-none-any.whl` (wheel)

## Explicitly Deferred (Post-Genesis)

- Runtime implementation for open security CDLs (`CDL-001`, `CDL-002`, `CDL-007`) beyond bounded remediation contracts.
- SDK product boundary formalization and bootstrap operations runbook hardening.
- Coalition anti-gaming controls beyond current single-agent concentration proxy.
- Advanced capability-proof activation surfaces and research-track mechanism set.

## Boundary Clarity (SG-06)

This Genesis release ships the scoring and invariant layer with deterministic conformance contracts, not the complete simulated consensus/economic control stack.

## Intentional Simplification Note (SG-07)

Genesis uses a flat 1.2x refutation multiplier as an intentional simplification for deterministic constitutional enforcement; higher-complexity ranking-based alternatives remain post-Genesis exploration work.

## Known operator-facing follow-up items

- `tools/genesis_boot.py`: error-path exit-code semantics and explicit mock-signature messaging are tracked follow-up improvements.
- `tools/demo_walkthrough.py`: failure-path exit-code and non-hermetic runtime behavior are tracked follow-up improvements.

## Provenance reference

- `docs/specs/ilc_genesis_release_artifact_provenance_phase_228_v0.1.md`

