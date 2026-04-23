# ADR-0028: Settlement Substrate Graduation and Governance Route

**Status:** Accepted (amended 2026-04-23 - graduation clause added)
**Date:** 2026-04-11
**Authors:** Jamison (ILC), Codex
**Classification:** Governance routing and architectural graduation rule

---

## Context

Window 607-612 separated four things that had drifted together:
- historical strategy,
- current runtime truth,
- current bounded public-claims surfaces,
- and the unresolved long-run public settlement substrate for `ILC`.

Phase 610 kept the deferred-substrate ledger-interface posture as the near-term
architectural path. That was correct. It also creates a risk: if no durable
routing rule exists, `Option D` can drift from a disciplined bridge into an
indefinite holding pattern.

The project therefore needs a governance route that:
- preserves the current `Option D` posture,
- does not pretend the final substrate is already selected,
- defines what must be true before a later `Option B`-like sovereign path
  becomes selectable,
- and avoids unnecessary constitutional mutation while those prerequisites are
  still open.

## Decision

### 1. Phase 611 selects memo plus ADR as the current governance route

The selected route is:
- Phase 611 governance memo,
- plus this accepted ADR,
- with no decision-log mutation and no opening of `CDL-062` in Window 607-612.

This route is sufficient because it locks the graduation rule and blocker
routing with more durability than memo-only while remaining lower-authority than
an unnecessary constitutional opening.

### 2. `Option D` remains the active posture until explicit graduation criteria are met

The deferred-substrate ledger-interface posture remains the active
architectural path.

This is not permission for indefinite deferral. It is a bounded bridge. The
project may not treat `Option B` as selected until the published graduation
checklist is satisfied.

### 3. Future substrate choice must satisfy protocol-first legitimacy

Any later public settlement substrate must preserve these constraints:
- protocol truth and graph legitimacy remain upstream of settlement backend
  choice,
- public auditability remains distinct from public identity exposure,
- censorship-resistance is a named future-substrate criterion,
- independence from external constitutional centers remains a named future
  selection criterion,
- local graph work remains cheap, fast, and abundant while canonical
  legitimacy and settlement remain scarce, auditable, and hard to fake.

### 4. A CDL opening is deferred unless memo plus ADR becomes insufficient

A future `CDL-062` opening is not authorized by this ADR.

A constitutional opening becomes admissible only if a later phase shows that:
- memo plus ADR cannot preserve the needed boundary,
- the graduation checklist is materially closed enough that constitutional
  opening becomes necessary,
- and the human explicitly authorizes that opening lane.

## Consequences

### Immediate

- Phase 611 closes with no decision-log mutation.
- Phase 612 must produce an MVP-gated handoff rather than new governance
  sub-lanes.
- The blocker matrix and graduation checklist become the carry-forward contract
  for post-612 work.

### Near-term

The next planning/output phases should prioritize:
- public init/admission contract,
- receipt issuance/query contract,
- visible ECU -> ILC lifecycle contract,
- public wallet touchpoint contract,
- and the minimum participant-touch package.

### Non-goals

- This ADR does not select the final sovereign public substrate.
- This ADR does not authorize wallet widening.
- This ADR does not authorize payment runtime.
- This ADR does not authorize chain implementation.
- This ADR does not authorize `CDL-062` opening in Window 607-612.

## Related references

- `docs/specs/ilc_phase_607_612_sequence_lock_v0.1.md`
- `docs/specs/ilc_settlement_substrate_historical_lineage_audit_608_v0.1.md`
- `docs/specs/ilc_settlement_substrate_authority_tier_classification_608_v0.1.md`
- `docs/specs/ilc_ecu_ilc_runtime_boundary_reconciliation_609_v0.1.md`
- `docs/specs/ilc_public_ledger_substrate_options_and_rejection_matrix_610_v0.1.md`
- `docs/research/ilc_cryptographic_economic_coupling_memo_v0.1.md`
- `docs/adr/ADR_0022_Local_First_Private_Use_and_Publication_Bound_Economics.md`
- `docs/adr/ADR_0026_Protocol_vs_Harness_Product_Boundary.md`

## Amendment - Window 811-822 (2026-04-23)

This amendment clarifies Section 2's phrase "the published graduation
checklist is satisfied" without reopening or replacing the original ADR text.
The clarification exists to prevent constitutional drift when a checklist row
has an honest fail or partial verdict together with a bounded carry-forward
plan.

For Option B selection, checklist rows are divided into two classes:

- **Hard-closure rows**: rows whose open status reflects missing design,
  missing governance, or a condition that is a prerequisite for safe
  operation. These rows block Option B selection until they are `closed`,
  `runtime_closed`, or otherwise explicitly recorded as fully satisfied by the
  governing checklist artifact.
- **Parallel-obligation rows**: rows whose open status reflects an honestly
  recorded fail or partial verdict where the design is fully understood, the
  failure mode does not change Byzantine safety, epoch finality, or
  censorship-resistance posture, a bounded implementation plan exists, and the
  human explicitly acknowledges the open status before selection.

At the Window 811-822 frontier, row 5
(`privacy-preserving public legitimacy mechanism at the settlement layer`) is
defined as a parallel-obligation row because:

- CW-2 recorded an honest fail verdict together with the named carry-forward:
  log hygiene plus transfer privacy.
- The failure mode is a participant-privacy gap. It does not alter Byzantine
  safety, epoch finality, or the row-7 censorship-resistance posture.
- Rows 1-4, 6, 7, 8, and 9 are otherwise closed, runtime-closed, or pass at
  the current frontier.
- The human explicitly acknowledged the open status while authorizing Option B
  selection on 2026-04-23.

Under this amendment, Option B selection is permitted when:

- every hard-closure row in the governing checklist is closed, runtime-closed,
  or otherwise explicitly satisfied,
- any parallel-obligation row is named as such in the governing checklist with
  its evidence basis and bounded carry-forward plan, and
- the human explicitly authorizes Option B selection.

Parallel-obligation status does not waive the underlying work. Row 5 remains a
required pre-public-RC obligation and must close before broader public RC
claims or broader public participant claims are made.
