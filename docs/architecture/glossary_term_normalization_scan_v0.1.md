# Glossary Term Normalization Scan v0.1

**Status:** DRAFT  
**Date:** 2026-02-16  
**Scope:** Markdown docs under `docs/`

## 1. Purpose

Confirm whether legacy aliases are still used in active architecture/spec/walkthrough text and identify any normalization cleanups needed after glossary canon updates.

## 2. Method

Commands used:

```bash
rg -n -i "\bPoIW\b|Proof of Useful Work|Proof of Useful Intelligent Labor|Proof of Intelligence Work" docs --glob "*.md"
rg -n -i "\bcommit epoch\b|epoch commit event" docs --glob "*.md"
rg -n -i "Token Graph Sharding|token graph shard" docs --glob "*.md"
rg -n -i "\bNodeManager\b|node manager" docs --glob "*.md"
```

## 3. Findings

### 3.1 PoIL Legacy Aliases

Observed in:
- `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md`
- `docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md`

Assessment:
- **No active-doc drift detected.**
- Mentions are policy/historical references and are intentional.

### 3.2 Commit.Epoch Naming Drift

Observed at scan start (pre-fix) in:
- `docs/specs/commit_epoch_event_schema_v0.1.md` (title used "Commit Epoch")
- `docs/phases/phase_78_g6_code_health_refactor_batch_3_walkthrough.md` ("Commit Epoch events")

Assessment:
- These are low-risk documentation drifts.
- Preferred canonical form is `Commit.Epoch`.

### 3.3 Token Graph Sharding

Observed in:
- `docs/reference/ilc_comprehensive_reference_glossary_v0.1.md`
- `docs/research/constitution_dredge_matrix_v0.2.md`
- `docs/research/constitution_drop_ledger_v0.1.md`

Assessment:
- **Intentional historical retention.**
- Correctly appears in deprecated/discussed contexts.

### 3.4 NodeManager Alias

Observed in:
- `docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md` guideline text ("Use `PeerManager` instead of `NodeManager`")

Assessment:
- **No drift.**
- This is an explicit migration rule, not active naming usage.

## 4. Actions

Completed in this pass:
- Normalize walkthrough phrasing to `Commit.Epoch` in:
  - `docs/phases/phase_78_g6_code_health_refactor_batch_3_walkthrough.md`
- Normalize spec heading to `Commit.Epoch` in:
  - `docs/specs/commit_epoch_event_schema_v0.1.md`

Deferred:
- Keep legacy aliases in reference/research docs for searchability and historical traceability.

## 5. Conclusion

Canonical naming is now stable in active docs. Remaining legacy terms are confined to intentional synonym-policy, historical, or research contexts.
