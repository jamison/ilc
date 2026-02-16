# ILC Non-Replay Domain Exception Migration Handoff Plan v0.1

## Purpose

Capture closure state for phases 182-190 and provide a deterministic handoff plan for follow-up work that remains outside this line.

## Closure guarantees from phases 182-190

1. Non-replay domain exception hierarchy exists in `ilc_core/exceptions.py` for scoped protocol, ledger, and CLI boundaries.
2. Scoped migration is complete for these modules:
   - `ilc_core/protocol/event_log.py`
   - `ilc_core/protocol/ilc_cluster_a_clause_binding.py`
   - `ilc_core/protocol/ilc_cluster_a_ingest.py` (scoped helper boundaries)
   - `ilc_core/ledger/canon_export_format.py`
   - `ilc_core/ledger/canon_export_bundle.py`
   - `ilc_core/ledger/canon_export_bundle_sign.py`
   - `ilc_core/cli/mcp_cli.py` (payload and tool invocation boundaries)
3. Guardrails are active for scoped migration:
   - AST raise-site guardrail test:
     - `tests/test_non_replay_domain_exception_migration_guardrail.py`
   - Guardrail gate script:
     - `tools/check_non_replay_domain_exception_migration_guardrails.sh`
   - Ops gate integration:
     - `tools/check_cluster_a_replay_proof_ci_gate.sh` Step -3 preflight
     - `tools/check_cluster_a_replay_proof_release_gate.sh` Step -3 preflight
   - CI workflow preflight integration:
     - `.github/workflows/test.yml`

## Active guardrails and where they execute

1. Local gate execution:
   - `bash tools/check_non_replay_domain_exception_migration_guardrails.sh`
2. Replay-proof ops scripts:
   - `check_cluster_a_replay_proof_ci_gate.sh` Step -3 preflight
   - `check_cluster_a_replay_proof_release_gate.sh` Step -3 preflight
3. GitHub Actions workflow:
   - test job preflight runs `check_non_replay_domain_exception_migration_guardrails.sh`

## Residual follow-up candidates (proposed order)

1. Extend non-replay domain exception migration to additional ledger and consensus surfaces still using generic exceptions.
2. Introduce domain-exception normalization on selected non-replay CLI modules outside MCP where stable user-facing error codes benefit.
3. Add cross-line closure orchestration linking replay-proof and non-replay closure gates in a unified handoff checklist.

## Non-goals for this closed line

1. No broad, repo-wide replacement of all `ValueError` usage.
2. No replay-proof algorithmic or schema behavior changes.
3. No CI matrix/platform expansion.

## Operational recommendation

Keep non-replay guardrail and closure scripts as mandatory preflights for adjacent non-replay protocol and ledger contract phases until a broader exception migration program supersedes this line.
