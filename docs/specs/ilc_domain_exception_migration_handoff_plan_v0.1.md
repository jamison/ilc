# ILC Domain Exception Migration Handoff Plan v0.1

## Purpose

Capture closure state for phases 172-180 and provide a deterministic handoff plan for follow-up work that remains outside this line.

## Closure guarantees from phases 172-180

1. Protocol and replay-proof domain exception hierarchy exists in `ilc_core/exceptions.py`.
2. Scoped migration is complete for these modules:
   - `ilc_core/protocol/schema.py`
   - `ilc_core/protocol/mapper.py`
   - `ilc_core/protocol/ilc_cluster_a_replay_proof_batch.py`
   - `ilc_core/protocol/ilc_cluster_a_replay_proof_package.py`
   - `ilc_core/protocol/ilc_cluster_a_replay_proof_ci_gate.py`
3. Guardrails are active for scoped migration:
   - AST raise-site guardrail test:
     - `tests/test_domain_exception_migration_guardrail.py`
   - Guardrail gate script:
     - `tools/check_domain_exception_migration_guardrails.sh`
   - Ops gate integration:
     - `tools/check_cluster_a_replay_proof_ci_gate.sh`
     - `tools/check_cluster_a_replay_proof_release_gate.sh`
   - CI workflow preflight integration:
     - `.github/workflows/test.yml`

## Active guardrails and where they execute

1. Local gate execution:
   - `bash tools/check_domain_exception_migration_guardrails.sh`
2. Replay-proof ops scripts:
   - `check_cluster_a_replay_proof_ci_gate.sh` Step -2 preflight
   - `check_cluster_a_replay_proof_release_gate.sh` Step -2 preflight
3. GitHub Actions workflow:
   - test job preflight runs `check_domain_exception_migration_guardrails.sh`

## Residual follow-up candidates (proposed order)

1. Extend domain exception migration to non-replay protocol/ledger modules with scoped, phase-bounded contracts.
2. Introduce domain-exception normalization at selected CLI boundaries where user-facing error-code policy benefits from typed catch blocks.
3. Add targeted documentation links from future phase prompts to this handoff artifact for traceability.

## Non-goals for this closed line

1. No broad, repo-wide replacement of all `ValueError` usage.
2. No replay-proof algorithmic or schema behavior changes.
3. No CI workflow matrix or platform expansion.

## Operational recommendation

Keep the guardrail and closure scripts as mandatory preflights for adjacent protocol-contract phases until a broader exception migration track formally supersedes this line.
