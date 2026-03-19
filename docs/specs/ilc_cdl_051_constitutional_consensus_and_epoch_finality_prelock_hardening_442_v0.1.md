# ILC CDL-051 Constitutional Consensus and Epoch-Finality Prelock Hardening 442 v0.1

Status: prelock hardening artifact
Date: 2026-03-19
Owner lane: G8 Constitution Cluster A

## 1. Scope and non-ratifying boundary

This artifact publishes the full non-ratifying prelock evidence record for `CDL-051`.

status: open

CDL-051 prelock hardening confirms the winning candidate: minimal epoch-state and quorum-record constitutional contract with deterministic fork/tie-break rules.

No CDL row mutation occurs in Phase 442.

Phase 443 is the targeted CDL-051 ratification lane; this hardening artifact constitutes the primary prelock evidence.

Consensus constants and rule-like defaults introduced before ratification must remain clearly marked as prototype-local rather than constitutional law.

Any pre-ratification consensus prototype must separate ratified constitutional obligations from operator-local or harness-local defaults.

Raw Z_Past_Chats are treated as hypothesis input only and do not constitute constitutional evidence.

These prelock inputs do not become constitutional constants until CDL-051 ratification in Phase 443.

## 2. CDL-051 open-state evidence anchor

The live constitutional register remains in the Phase-441 opening state: `CDL-051` is present and remains `open`.

The authoritative open-state anchor for this lane is `docs/specs/ilc_cdl_051_constitutional_consensus_and_epoch_finality_opening_stub_441_v0.1.md` together with the Phase-441 decision-log snapshot where `CDL-051` first entered the register as `status: open`.

The Phase-441 opening row and opening stub remain the authoritative historical open-state anchor for CDL-051.

## 3. Inherited constitutional anchors review

CDL-051 inherits quorum-diversity, brokerless transport, admission control, and emergency-response constraints from CDL-V3, CDL-039, CDL-040, and CDL-045; this inheritance is reviewed and confirmed in Phase 442 prelock hardening.

Inherited anchor review summary:
- `CDL-V3` remains the ratified quorum-diversity floor for any consensus or finality path that depends on multi-validator legitimacy.
- `CDL-039` remains the brokerless transport and topology-privacy boundary; Phase 442 does not authorize a central coordinator or transport rewrite.
- `CDL-040` remains the admission-control and identity-envelope boundary for validators and related attestations.
- `CDL-045` remains the emergency-response override boundary for any finalized state that would require exceptional intervention after ordinary finality processing.

These inherited anchors constrain CDL-051 without reopening their historical ratification evidence or mutating any of the prior ratified artifacts.

## 4. Winning candidate confirmation and rejected candidates

The winning candidate is confirmed: minimal epoch-state and quorum-record constitutional contract with deterministic fork/tie-break rules; both rejected candidates remain excluded.

Defer consensus lane indefinitely is rejected because CDL-051 carries an active constitutional obligation inherited from CDL-V3, CDL-039, CDL-040, and CDL-045; deferral would leave inherited quorum and finality obligations ungrounded.

Full production consensus architecture with storage-format cutover is rejected because the storage-format cutover decision is not constitutionally ripe in Window 441-449 and full production architecture exceeds the bounded constitutional scope of this lane.

The winning candidate is constitutionally narrow: it locks the minimum epoch-state and quorum-record contract needed for later runtime implementation while preserving a separate future decision point for storage-format cutover and broader production-architecture concerns.

## 5. Conflict-state terminology lock

These definitions are prototype-local until CDL-051 ratification.

**epoch**: a numbered protocol window bounded by a start and end slot; the primitive unit of finality measurement.
**quorum-state**: the registered set of validators and associated voting weights active at an epoch boundary.
**quorum-threshold**: the minimum aggregate voting weight required to finalize a block; the specific value is a prototype-local default until CDL-051 ratification.
**finality**: the irreversibility guarantee assigned to a block or state-transition after quorum-threshold confirmation; a finalized block cannot be reversed except through an emergency-response protocol governed by CDL-045.
**fork**: a divergence in chain state producing two competing continuation histories from a common ancestor block.
**fork-resolution rule**: the deterministic, operator-independent algorithm for selecting exactly one fork as canonical; must not depend on external oracle input.
**epoch-state record**: the minimal on-chain artifact capturing quorum-state and finality status at an epoch boundary; corresponds to the `epoch-state` surface targeted in Phases 444-445.
**quorum-record**: a single attestation from a validator tied to a specific block hash and epoch number.
**conflict**: any state where two or more fork heads both satisfy local validity rules; conflict-state triggers the fork-resolution rule.

## 6. Evidence-source ladder and prototype-default provenance boundary

1. Tier 1 — Ratified constitutional decisions (CDL-V3, CDL-039, CDL-040, CDL-045) and active window handoffs: highest authority; may not be overridden by lower tiers.
2. Tier 2 — Active specs and runtime artifacts (sequence lock, CDL-051 stub, this hardening artifact, test files): authoritative for the current window; supersede prior windows on overlapping scope.
3. Tier 3 — Filtered historical extracts (prior phase walkthroughs, prior window handoffs, evidence assembly reports): informative; must not override Tier 1 or Tier 2.
4. Tier 4 — Raw Z_Past_Chats: hypothesis input only; zero constitutional authority; must not be cited as binding design constraints.

Prototype-default provenance statement: any consensus constant or rule introduced in Phases 444-446 before ratification is prototype-local and must be annotated as such; it does not bind future phases as constitutional law until CDL-051 is ratified in Phase 443.

## 7. Section-7 ratification readiness evidence checklist satisfaction

1. The Phase-441 opening row and opening stub remain the authoritative historical open-state anchor for CDL-051.
2. CDL-051 inherits quorum-diversity, brokerless transport, admission control, and emergency-response constraints from CDL-V3, CDL-039, CDL-040, and CDL-045; this inheritance is reviewed and confirmed in Phase 442 prelock hardening.
3. The winning candidate is confirmed: minimal epoch-state and quorum-record constitutional contract with deterministic fork/tie-break rules; both rejected candidates remain excluded.
4. The evidence-source ladder is constitutionally published: ratified CDL and active handoffs first, then active specs and runtime artifacts, then filtered historical extracts, with raw Z_Past_Chats treated as hypothesis input only.
5. All pre-ratification consensus prototype defaults introduced in this window must remain separated from constitutional law and from operator-local or harness-local overrides until CDL-051 ratification in Phase 443.

## 8. Non-goals

Phase 442 does not ratify CDL-051.

Phase 442 does not mutate the constitutional decision log.

Phase 442 does not open `CDL-050`.

Phase 442 does not modify any `ilc_core/` runtime file.

Phase 442 does not mutate the Phase 441 opening stub, the Phase 441 sequence lock, or any of the four inherited historical ratification artifacts for CDL-V3, CDL-039, CDL-040, and CDL-045.

Phase 442 does not authorize consensus runtime implementation, storage-format cutover, packaging/bootstrap merge work, or Treasury `P_e` governance assessment.
