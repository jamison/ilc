# ILC Window 475-484: Candidate Phase Grouping

**Author:** Claude Sonnet 4.6 (local architectural reviewer)
**Date:** 2026-03-28
**Baseline:** Window 469-474 CLOSED (Phase 474 complete). CDL-050, CDL-051, and CDL-052 all
ratified. Genesis validator and OpenClaw architectures scoped in Phase 468. Diversity-aware
finality evaluation path complete (Phase 470). Adversarial hardening findings published
(Phase 473). Phase 475 is the next numbered phase.

---

## 1. Track inventory arriving from Phase 474

### Constitutionally complete, awaiting runtime implementation

- **CDL-052 epistemic evaluation architecture** — ratified Phase 466. Scoping for SDK surface
  (four graph operations: node submission, refutation, novelty-check, reuse-centrality) done
  in Phase 468. Mode 2 (Popperian elevation via `refutation_criterion`) and Mode 3 (bounded
  auditor review) boundaries locked. Runtime implementation deliberately deferred until now.
  Key prerequisite documents: `ilc_refutation_criterion_schema_specification_462_v0.1.md`,
  `ilc_minimal_staking_contract_specification_463_v0.1.md`,
  `ilc_cdl_052_epistemic_evaluation_architecture_ratification_evidence_466_v0.1.md`.

- **CDL-V7 Popperian gate** — ratified Phase 335, runtime Phase 398. This is the existing
  gate that CDL-052 Mode 2 builds on. The CDL-052 runtime should reference and integrate
  this existing surface, not replace it.

### Scoped but not implemented

- **Genesis validator minimum viable configuration** — scoped Phase 468. Deferred items:
  runtime validator bootstrap tooling, key-loading and ceremony integration, epoch-zero
  state materialization in executable form, admission-control runtime enforcement, validator
  network join and recovery flow. Key prerequisite:
  `ilc_genesis_validator_architecture_scoping_468_v0.1.md`.

### Explicitly out of scope for Window 475-484

- Mode 3 (auditor-review hooks and execution) — most complex CDL-052 piece, warrants its
  own future window lane.
- Staking constant calibration — all numeric parameters remain TBD pending a future
  simulation lane, per Phase 463 deferral.
- Validator network join and recovery flow — deferred to a later bootstrap extension lane.
- CDL-V1 temporal decay parameter calibration — no new mandate.
- Treasury P_e CDL lane — prerequisites not yet fully satisfied; remain Window 434+ carry-
  forward items, not unlocked by Window 469-474.
- CDL-021 (Rust/WASM) — defer indefinitely.

---

## 2. Candidate Window 475-484: "CDL-052 Epistemic Runtime + Genesis Validator Bootstrap" (10 phases)

| Phase | Topic | Sensitivity | Track |
|---|---|---|---|
| 475 | Sequence lock + scope freeze | SENSITIVE | Foundation |
| 476 | CDL-052 epistemic evaluation contract specification (SDK-level typed contracts) | SENSITIVE | CDL-052 |
| 477 | CDL-052 epistemic runtime Part 1 — `ilc_core/epistemic/` package, node-submission envelope, mode-routing | SENSITIVE | CDL-052 |
| 478 | CDL-052 epistemic runtime Part 2 — refutation submission, novelty-check, reuse-centrality query | SENSITIVE | CDL-052 |
| 479 | Genesis validator bootstrap specification — key format, enrollment record, ceremony protocol | SENSITIVE | Genesis |
| 480 | Genesis validator bootstrap runtime Part 1 — epoch-zero state materialization, enrollment tooling | SENSITIVE | Genesis |
| 481 | Genesis validator bootstrap runtime Part 2 — admission-control enforcement for genesis validators | SENSITIVE | Genesis |
| 482 | CDL-052 and genesis validator integration findings memo | SENSITIVE | Integration |
| 483 | Coherence report + capsule v2.2 | SENSITIVE | Synthesis |
| 484 | Closure gate + handoff | SENSITIVE | Gate |

---

## 3. CDL-052 runtime track detail (Phases 476-478)

### Phase 476 — Contract Specification (no ilc_core/ mutation)

Phase 476 publishes the typed SDK contracts before any runtime code is written. This mirrors
the role Phase 462/463 played before CDL-052 opening: establishing the surface boundary
before committing runtime behaviour.

Deliverable: `ilc_core/epistemic/` does NOT yet exist. Phase 476 publishes a spec document
only: typed envelope definitions for `EpistemicNodeSubmission`, `EpistemicRefutationSubmission`,
`EpistemicNoveltyCheckQuery`, and `EpistemicReuseCentralityQuery`. Error codes for malformed
`refutation_criterion` and mode-boundary violations. CDL-033 extension requirements. No code.

### Phase 477 — Runtime Part 1 (ilc_core/epistemic/ package skeleton + node submission + mode routing)

New package: `ilc_core/epistemic/__init__.py` and
`ilc_core/epistemic/node_submission_runtime.py`.

Scope:
- `EpistemicNodeSubmission` typed envelope validator,
- CDL-052 mode-routing gate (Mode 1 default if no `refutation_criterion`; Mode 2 if
  `refutation_criterion` present and valid; Mode 3 boundary detection only — no execution),
- integration hook to existing CDL-V7 Popperian gate for Mode 2 path,
- `normative: true` + `refutation_criterion` collision rejection (Phase 462 rule),
- `CDL_052_DEPENDENCY = "cdl_052_ratified_466.v0.1"` version token.

Out of scope in Phase 477: refutation submission logic, novelty-check, reuse-centrality.

### Phase 478 — Runtime Part 2 (refutation + novelty-check + reuse-centrality)

Adds to `ilc_core/epistemic/`:
- `ilc_core/epistemic/refutation_runtime.py` — typed refutation submission handler,
  stake-return path on failed novelty, slash-record path on successful challenge,
  reputation feed-through hooks (staking constants remain TBD per Phase 463).
- `ilc_core/epistemic/novelty_check_runtime.py` — novelty-check query surface with
  deterministic failure tokens and deduplication boundary.
- `ilc_core/epistemic/reuse_centrality_runtime.py` — reuse-centrality query contract
  (PageRank-style interface stub; computation backend deferred to future window).

Mode 3 execution hooks are **not implemented** in Phase 478. The Mode 3 boundary detection
from Phase 477 is the only Mode 3 surface in this window.

---

## 4. Genesis validator bootstrap track detail (Phases 479-481)

### Phase 479 — Bootstrap Specification (no ilc_core/ mutation)

Phase 479 publishes the bootstrap specification document before any runtime code is written.

Deliverable: `docs/specs/ilc_genesis_validator_bootstrap_specification_479_v0.1.md`

Content:
- Signing key format for CDL-051 validator identity (Ed25519 public key encoding, registry
  format, human-readable identifier binding).
- Enrollment record structure (validator_id, public_key, cluster_id, vote_weight, epoch_zero).
- Key-loading ceremony protocol (sequence of steps for a human operator: key generation,
  public-key extraction, enrollment record submission, verification).
- Epoch-zero state record format (quorum-record seed, genesis block anchor, epoch counter).
- Admission-control pre-population bundle format (static bundle consumed by the runtime).
- Non-goals: private key management, hardware security module integration, threshold
  signatures (all out of scope for this bootstrap specification).

### Phase 480 — Bootstrap Runtime Part 1 (epoch-zero state + enrollment tooling)

Extends `ilc_core/genesis/`:
- `ilc_core/genesis/validator_bootstrap_runtime.py`
- Functions: `generate_validator_enrollment_record`, `verify_genesis_enrollment`,
  `materialize_epoch_zero_state`, `verify_epoch_zero_state`.
- Deterministic ceremony-sequence verification (validators are enrolled in a locked order).
- Deterministic epoch-zero construction must include `quorum_record_seed` in addition to
  `validator_set_hash`; Phase 480 should define and test the seed-derivation rule explicitly.
- `CDL_051_RATIFICATION_DEPENDENCY` version token, matching the exported constant in
  `ilc_core/consensus/finality_evaluator.py` (value: `"cdl_051_constitutional_consensus_and_epoch_finality_443.v0.1"`).
  Phase 480 must use this exact name — NOT `CDL_051_DEPENDENCY`.
- `GENESIS_BOOTSTRAP_VERSION` constant.

Out of scope in Phase 480: admission-control enforcement, network join.

### Phase 480 additional dependency note

Phase 480 enrollment records reference two CDL surfaces for validator_id semantics:
1. `CDL_051_RATIFICATION_DEPENDENCY` from `ilc_core/consensus/finality_evaluator.py` (quorum
   and finality context),
2. `CDL_042_DEPENDENCY` from `ilc_core/identity/agent_id_runtime.py` (key-derived agent_id
   and flat namespace format).

The finality evaluator governs finality evaluation; validator identity FORMAT comes from
CDL-042. Both dependencies must be declared in Phase 480's runtime module.

### Phase 481 — Bootstrap Runtime Part 2 (admission-control enforcement)

Extends `ilc_core/genesis/`:
- `ilc_core/genesis/admission_control_bootstrap.py`
- Functions: `build_genesis_admission_control_bundle`, `verify_admission_control_bundle`,
  `enforce_genesis_admission`.
- Links to CDL-040 identity-envelope ratification for admission-control semantics.
- Deterministic rejection tokens for unauthorized validator attempts.
- `CDL_040_DEPENDENCY` version token. No canonical runtime export currently exists, so
  Phase 481 should declare the ratified token locally rather than inventing an import path.

Out of scope in Phase 481: validator network join and recovery flow (deferred to later lane).

---

## 5. Key dependencies and open questions

### CDL-052 runtime dependencies

- CDL-V7 Popperian gate runtime (`ilc_core/consensus/popperian_gate_runtime.py`) must be
  referenced by Phase 477's mode-routing for the Mode 2 path. Phase 477 should import from
  `ilc_core.consensus` (which re-exports `CDL_V7_DEPENDENCY` and `CDL_V7_RUNTIME_VERSION`),
  not duplicate it. Note: the Popperian gate is in `ilc_core/consensus/`, NOT
  `ilc_core/analysis/`.
- CDL-034 authored-envelope boundary must be preserved. The `refutation_criterion` field
  lives in the authored envelope only (Phase 462 locked this). Phase 477 must enforce this.
- Staking constants: all numeric values remain TBD. Phase 477/478 should use symbolic
  constants (e.g. `SUBMISSION_STAKE_AMOUNT_TBD`) with explicit deferred markers rather than
  hard-coded zeros.

### Genesis validator dependencies

- CDL-051 consensus machinery (Phase 445 runtime) governs validator identity and membership.
  Phase 480 must reference the Phase 445 finality evaluator's validator_id semantics.
- CDL-040 admission-control ratification (Phase 393) governs the admission-control contract.
  Because no canonical runtime export exists yet, Phase 481 should declare the
  `CDL_040_DEPENDENCY` ratified token locally and document why.
- CDL-042 flat agent namespace (Phase 407 ratification) governs key-derived agent_id. Phase
  480 enrollment record generation must be consistent with this namespace.

### Phase 483 synthesis obligations (two-window capsule gap + ADR-0022 carry-forward)

Capsule v2.1 was published during Phase 466 (Window 460-468) and describes "Window 460-468 is
active. Phase 467 is next." Window 469-474 did NOT produce a capsule update. Therefore capsule
v2.2 (Phase 483) must retroactively cover both windows:

1. **Window 469-474 coverage**: diversity-aware finality evaluation path, distributed and
   degraded-network measurement, bridge-realism exercise, adversarial hardening findings.
2. **Window 475-484 coverage**: CDL-052 epistemic runtime, genesis validator bootstrap.

Additionally, the Window 460-468 candidate phase grouping document contains an explicit
carry-forward obligation for capsule v2.2:

> Carry-forward note for the next capsule refresh:
> - the next capsule update should explicitly reference `ADR-0022` as the active
>   local-first/private-use boundary,
> - disposition minimum-scope `CDL-053` separately from the private/gated shard
>   rights/access lane,
> - and state that shard-header, access-right, and rights/licensing hardening remain
>   future planning lanes rather than silently activated protocol law.

This obligation has NOT been discharged in capsule v2.1. Phase 483's prompt must either
(a) include these items in capsule v2.2, or (b) explicitly defer them again with rationale.

### Phase 476 naming disambiguation note

The existing `ilc_core/genesis/` package exports `EpistemicWorkTask` (from `work_task.py`),
which is a genesis-layer work-task construct. The new `ilc_core/epistemic/` package (Phase
477) introduces `EpistemicNodeSubmission`, `EpistemicRefutationSubmission`, etc., which are
CDL-052 graph-side evaluation constructs. These are architecturally distinct and must not be
confused. Phase 476's contract specification must include a naming disambiguation note:
`EpistemicWorkTask` is a genesis-layer concept; the new `Epistemic*` envelopes in
`ilc_core/epistemic/` are CDL-052 evaluation-surface concepts.

Phase 476 does NOT create `ilc_core/epistemic/__init__.py` or any code. That is Phase 477's
responsibility. Phase 476 produces a specification document only.

### Open question: ceremony tooling placement

The key-loading ceremony protocol (Phase 479 spec) will eventually need interactive tooling.
Should that tooling live under `tools/` or `ilc_core/genesis/`? Recommendation: `tools/`
for the human-facing ceremony script; `ilc_core/genesis/` for the deterministic verifier.
Phase 479 should make this placement decision explicit in the spec.

---

## 6. Rationale for two-track window

**Why CDL-052 runtime now?** CDL-052 was ratified in Phase 466 and scoped in Phase 468.
The epistemic evaluation architecture is the core of ILC's knowledge graph economy. Deferring
its runtime beyond Window 475 means ILC cannot operate as a knowledge protocol in any
meaningful sense — there is no submission path, no refutation path, and no mode-routing.
This is the highest-priority runtime work at the current stage.

**Why genesis validator bootstrap now?** The genesis validator architecture was scoped in
Phase 468 alongside the CDL-052 scoping. The user has indicated they will begin preparing
genesis validator key material. The bootstrap specification (Phase 479) is SENSITIVE
(consistent with the phase table) because the ceremony protocol and enrollment record format
carry CDL-051 constitutional coupling; it will materially help the user understand what key
material they need to prepare. The runtime phases (480-481)
follow naturally and are bounded in scope (no network join, no private key management).

**Why not separate windows?** A single 10-phase window keeps the epistemic submission
surface (CDL-052 runtime) and the validator bootstrap surface (genesis) in the same
constitutional scope, which is coherent because a genesis validator is fundamentally a CDL-052
graph participant: they submit, route, and evaluate nodes. Implementing them together in the
same window makes the dependency visible and governed. Separating them would create a window
where CDL-052 runtime exists but no validator bootstrap mechanism does, which is a valid but
arguably less complete launch-readiness position.

**Why 10 phases?** Prior windows with dual runtime tracks have been 10-12 phases:
Window 392-401 (10), Window 402-413 (12), Window 414-423 (10). 10 phases accommodates two
contract-specification phases (476, 479) that act as pre-implementation checkpoints and two
synthesis phases (482, 483) without compressing the runtime implementation phases.
