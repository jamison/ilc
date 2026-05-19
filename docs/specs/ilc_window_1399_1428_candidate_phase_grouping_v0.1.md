# ILC Window 1399–1428: Candidate Phase Grouping

**Author:** Claude Sonnet 4.6 (local architectural reviewer)
**Date:** 2026-05-19
**Baseline:** Window 1391-1398 COMPLETE (J-series 163 tests; J-008 gate verdict INCOMPLETE,
7/10 blocking conditions NOT_MET). Window 1369-1390 CLOSED Phase 1390 (`43401835`).
CDL-090 ratified Phase 1373 (last CDL). Capsule v5.58.
**Planning note:** This is a candidate grouping, not a locked sequence. Phases 1399–1420 are
the hard minimum lanes for J-008 gate resolution (7 CDL/runtime/ADR tracks). Phases 1421–1428
are the coherence, manifest design, rehearsal planning, and gate closure tail — fixed. No
conditional tail slots: all CDL tracks are pre-authorized by J-008 gate definition.

> **STATUS: PROPOSAL — requires human review and sequence lock GO before any phase executes.**
> This document is the guidance doc input, not an approved sequence lock.

---

## 1. Window Identity and Scope

**Window 1399–1428** resolves all 7 blocking conditions from the J-008 production jury
activation gate (Phase 1398 verdict INCOMPLETE) and produces the architectural specifications
needed for the private soft-RC rehearsal and clean public RC activation event.

Three parallel tracks:

1. **Jury Economy CDL track (Phases 1399–1420):** Three CDL-opening/ratification sequences
   (J-004 jury incentive economics → CapProof → maintenance lottery pool), one ADR + VRF
   implementation track, one review lane wiring track, and one anti-capture verification pass,
   closing all 7 J-008 blocking conditions. One copyright counsel disposition.

2. **Launch Readiness Design track (Phases 1422–1424):** Launch Readiness Manifest schema
   (`public_rc_launch_readiness_manifest_v1`), private soft-RC rehearsal entry criteria
   (3-machine / 7-agent topology, scripted agents, Lean Mathlib dataset plan), and public RC
   activation certificate design (epoch 0→1 transition, Genesis signing, hello-world provenance
   node design).

3. **Gate closure tail (Phases 1425–1428):** Pre-gate verification, soft RC re-run (forward
   obligation from Phase 1367), J-008 gate re-run expecting `verdict="PASS"`, window closure.

The J-008 `evaluate_jury_activation_gate()` function will flip automatically to `verdict="PASS"`
when all 7 blocking condition tokens are met; no source changes to the gate module are needed
for the re-run phase.

**Tail-slot policy:** No conditional tail slots. All CDL tracks are required by J-008 gate
conditions and are pre-authorized by the Phase 1398 gate verdict. Phase numbers 1399–1428 are
reserved. If a CDL track takes fewer phases, remaining numbers in that block are unused and
the window proceeds to the next track.

---

## 2. Baseline and Inheritance

### 2.1 Ratified CDL Chain (relevant portion)

| CDL | Status | Phase | Note |
|-----|--------|-------|------|
| CDL-047 | Ratified | 418 | Treasury ECU governance |
| CDL-048 | Ratified | 419; activated 1388 | ECU-to-ILC conversion path |
| CDL-050 | Ratified | 459 | Bounded Treasury ECU-governor lane |
| CDL-051 | Ratified | 443 | Epoch-state / quorum-record contract |
| CDL-052 | Ratified | 466 | Three-mode epistemic evaluation architecture |
| CDL-054 | Ratified | 491 | Validator reward-pool routing |
| CDL-085 | Ratified | 1185 | Werner φ-bound |
| CDL-086 | Ratified | 1220 | Public-launch packaging governance |
| CDL-087 | Ratified | 1278 Fix1 | Canonical fetch distribution policy |
| CDL-088 | Ratified | 1376 | Public claimability authority |
| CDL-089 | Ratified | 1364 | Blocking-authority activation vehicle |
| CDL-090 | **Ratified** | **1373** | **Identity bootstrap** |
| CDL-091 | To be opened | 1399 | Jury incentive economics (this window) |
| CDL-092 | To be opened | 1402 | CapProof pricing and CV signing (this window) |
| CDL-093 | To be opened | 1406 | Maintenance lottery pool distribution (this window) |

Next fresh CDL number after this window: **CDL-094**.

### 2.2 Active Runtime Chain (relevant portion)

| Module | Version token | Phase |
|--------|---------------|-------|
| `ilc_core/epistemic/jury_activation_gate.py` | `jury_activation_gate_phase_j008.v0.1` | 1398 |
| `ilc_core/epistemic/ingestion_shadow_harness.py` | `ingestion_shadow_harness_phase_j007.v0.1` | 1397 |
| `ilc_core/epistemic/jury_assignment_runtime.py` | `jury_assignment_runtime_phase_j006.v0.1` | 1396 |
| `ilc_core/ledger/public_economics_admission_firewall.py` | (Phase 1387a) | 1387a |
| `ilc_core/sidecars/claim_nullifier_registry_v1.py` | (Phase 1389b) | 1389b |
| `ilc_core/governance/challenge_node_runtime.py` | (Phase 1382) | 1382 |
| `ilc_core/governance/fork_legitimacy_runtime.py` | (Phase 1383) | 1383 |

Key gate conditions already MET:
- `J007_HARNESS_PASS` — ingestion shadow harness present and tested (Phase 1397)
- `PUBLIC_ECONOMICS_FIREWALL` — firewall module present (Phase 1387a)
- `NO_EPOCH_HASH_PRODUCTION_PRIVACY_CLAIM` — no such claim in any artifact

Key gate conditions NOT_MET (this window must close all 7):
- `VRF_VERIFIER_IMPLEMENTED`
- `CAPPROOF_CDL_RATIFIED`
- `MAINTENANCE_LOTTERY_CDL_RATIFIED`
- `JURY_INCENTIVE_CDL_RATIFIED`
- `REVIEW_LANE_WIRING_COMPLETE`
- `ANTI_CAPTURE_DIVERSITY_VERIFIED`
- `COPYRIGHT_COUNSEL_DISPOSITION`

### 2.3 Canonical Anchors Inherited

- Capsule v5.58 — PRIMARY context reference
- `docs/specs/ilc_window_1369_1390_handoff_1390_v0.1.md` — Window 1369-1390 closure
- `docs/phases/phase_1398_j008_production_jury_activation_gate_walkthrough.md` — J-008 gate verdict and 10-condition table
- `docs/specs/ilc_production_jury_activation_gate_j008_v0.1.md` — gate spec with evidence_ref and routing per condition
- `docs/adr/ADR_0040_Jury_Eligibility_Assignment.md` — VRF production boundary; `vrf_proof_verifier_not_implemented` token
- `docs/adr/ADR_0041_Agent_INIT_and_Ingestion_Protocol.md` — ADR-0041 §5 copyright boundary (CDL-gated)
- `docs/specs/ilc_cdl_jury_incentive_economics_opening_v0.1.md` — J-004 CDL opened but NOT ratified
- `docs/specs/ilc_epoch_start_capability_maintenance_contract_v0.1.md` — J-005 CapProof ±15% pricing boundary
- `ilc_core/epistemic/jury_assignment_runtime.py` — `vrf_required_for_production_high_value_assignment` boundary
- Phase 1367 soft RC gate: treasury blocker fixed but `soft_rc_eligible=true` never recorded (Phase 1426 forward obligation)

---

## 3. Track Inventory

### 3.1 Constitutionally Obligated

| Track | Obligation source | This window |
|-------|------------------|-------------|
| Jury incentive economics CDL ratification | J-008 `JURY_INCENTIVE_CDL_RATIFIED` condition | Phases 1399–1401 |
| CapProof CDL opening and ratification | J-008 `CAPPROOF_CDL_RATIFIED` condition | Phases 1402–1405 |
| Maintenance lottery pool CDL opening and ratification | J-008 `MAINTENANCE_LOTTERY_CDL_RATIFIED` condition | Phases 1406–1409 |
| VRF proof verifier ADR + implementation | J-008 `VRF_VERIFIER_IMPLEMENTED` condition; ADR-0040 §Assignment Source | Phases 1410–1413 |
| Review lane wiring T0.5→T1+ | J-008 `REVIEW_LANE_WIRING_COMPLETE` condition | Phases 1414–1417 |
| Anti-capture diversity production verification | J-008 `ANTI_CAPTURE_DIVERSITY_VERIFIED` condition | Phases 1418–1419 |
| Copyright counsel disposition (ADR-0041 §5) | J-008 `COPYRIGHT_COUNSEL_DISPOSITION` condition | Phase 1420 |
| Soft RC gate re-run | Forward obligation from Phase 1367 (treasury blocker resolved, gate not re-run) | Phase 1426 |
| J-008 gate re-run | Requires all 7 blocking conditions MET | Phase 1427 |

### 3.2 Deferred Governance (visible, not this window)

| Item | Status | Window |
|------|--------|--------|
| Mode-2 settlement-grade refutation path | Carried from Window 1391-1398; stake/CDL-029 wiring deferred | Post-1428 |
| GOVERNS/CONSTRAINS merge CDL | Identified in 1387i synthesis; post-RC ADR | Post-1428 |
| CDL-031 dynamic ranking runtime | CDL-031 ratified deferred Phase 288; CDL-019 prerequisite | Long-range |
| ADR-0015 node transfer economics | Requires live network data | Post-public-RC |
| Public RC publication, release signing | Requires explicit publication GO | Post-1428 |
| Production minting activation | Deferred from Phase 1368 | Post-public-RC |
| Mainnet split-custody ceremony | Required before mainnet launch | Long-range |
| v0.3_candidate signing ceremony | Forward obligation from Phase 1387j | This window (Phase 1424) |

### 3.3 Simulation-Conditional

| Track | Condition | Status |
|-------|-----------|--------|
| VRF calibration SIM | If VRF implementation reveals calibration needs | Conditional: Phase 1413 may spawn a SIM phase |
| Review lane throughput SIM | If review lane wiring reveals throughput/incentive calibration needs | Conditional: Phase 1417 may spawn a SIM phase |

These do not have reserved phase numbers. If needed, they will be inserted as sub-phases
(e.g., 1413a, 1417a) under the existing authorized tracks.

---

## 4. Jury Incentive Economics CDL Track (CDL-091)

**Authorized scope:** J-004 opened the jury incentive economics CDL in Phase 1394 with a
specific recommendation: reject approval-only reviewer payment; adopt fixed base review fee
plus delayed accuracy-weighted bonus. The Phase 1394 opening spec is
`docs/specs/ilc_cdl_jury_incentive_economics_opening_v0.1.md`.

**Scope of CDL-091:**
- Governance constants: base review fee, accuracy-weighted bonus parameters, panel size
  multiplier, approval-volume bias mitigation mechanism
- Funding source: petition-bond vs. fixed pooled budget (deliberation question for prelock)
- Runtime stub: `ilc_core/epistemic/jury_incentive_runtime.py` — default off; wires
  `JURY_INCENTIVE_CDL_RATIFIED_TOKEN` constant; `reviewer_payment_not_activated` boundary
  preserved; no live ECU distribution
- Non-goals: does NOT activate reviewer payment; does NOT mutate the ledger; does NOT
  change epoch economics; does NOT amend CDL-047 treasury framework

**CDL-091 does not activate reviewer payment.** Phase 1401 runtime stub is default-off.
Live payment activation requires a separate production GO after the J-008 gate reaches PASS.

---

## 5. CapProof CDL Track (CDL-092)

**Authorized scope:** J-005 locked the CapProof boundary in Phase 1395: CapProof adjusts
ECU pricing ±15% only — never mints ILC; AWP/IIH depends on CapProof infrastructure.
This CDL governs the CapProof content-addressing, CV signing chain, and pricing band.

**Scope of CDL-092:**
- CapProof content-addressing: how a CapProof node is content-addressed (hash inputs)
- CV signing chain: how CapProof chains back to Genesis-rooted agent identity
- ±15% pricing band: the exact bound and how it applies to ECU pricing for CapProof-covered
  work; band edges are constitutional constants, not operator policy
- Non-goals: does NOT activate CapProof pricing; does NOT mint ILC; does NOT wire CapProof
  into the production review lane (that is Phase 1415-1416); does NOT amend CDL-047

**Deliberation questions for Phase 1403:**
- Q1: What fields constitute the CapProof content-address input (CV hash, timestamp, scope)?
- Q2: How does the CV signing chain anchor to ADR-0038 birth attestation?
- Q3: What is the exact ±15% band application rule (additive? multiplicative? floor/ceiling?)?
- Q4: Does CapProof apply to all ECU-earning work types or only specific lane types?

---

## 6. Maintenance Lottery Pool CDL Track (CDL-093)

**Authorized scope:** J-005 defined the maintenance task lifecycle (proposed → rewarded)
and noted that maintenance tasks are reward-eligible only after passing the review lane.
This CDL governs the lottery pool distribution rules.

**Scope of CDL-093:**
- Lottery pool funding source: what fraction of epoch ECU (or treasury allocation) feeds the pool
- Draw mechanism: deterministic lottery using epoch hash (shadow assignment pattern from J-006)
  vs. separate VRF draw — deliberation question
- Distribution: per-task, per-agent, or per-cluster; payout timing (epoch boundary)
- Eligibility: which maintenance task types are pool-eligible; minimum audit state required
- Non-goals: does NOT activate lottery distribution; does NOT amend CDL-047; does NOT overlap
  with reviewer payment (CDL-091)

**Deliberation question for Phase 1407:**
- Q1: Does the maintenance lottery use the same VRF path as production jury assignment (Phase
  1411-1412), or does it use epoch-hash shadow assignment (Phase 1396 pattern)?
- Q2: What is the funding fraction? (SIM may be needed post-ratification if calibration required)

---

## 7. VRF Proof Verifier Track

**Authorized scope:** ADR-0040 §Assignment Source defines the VRF production/high-value
boundary: epoch-hash shadow assignment (Phase 1396) is the shadow mode; VRF is required for
production high-value jury assignment. Phase 1398 records `vrf_proof_verifier_not_implemented_phase_j008`.
This track specifies, implements, and integrates a VRF proof verifier.

**Phase 1410 ADR scope:**
- VRF algorithm selection (ECVRF per IETF draft, consistent with ADR-0038 agent keypairs)
- Proof structure (proof inputs: epoch seed, agent keypair; output: deterministic pseudo-random bytes)
- Verification API: `verify_vrf_proof(proof, public_key, epoch_seed) -> bool`
- Integration contract with `jury_assignment_runtime.py`: VRF replaces epoch-hash for
  high-value slots; fallback to epoch-hash shadow ONLY if VRF not yet deployed

**Phase 1411 implementation scope:**
- `ilc_core/epistemic/vrf_proof_verifier.py` — pure verification logic; no private key operations
- `VRF_PROOF_VERIFIER_VERSION = "vrf_proof_verifier_phase_1411.v0.1"` version token
- Token `vrf_proof_verifier_implemented_phase_1411` required for J-008 `VRF_VERIFIER_IMPLEMENTED` condition
- No `import random` (ICSS §2 PRNG ban)

**Phase 1412 integration scope:**
- `jury_assignment_runtime.py` updated to accept optional `vrf_proof` parameter
- VRF-verified path replaces epoch-hash for `capability_tier` above a defined threshold
- `PRODUCTION_ASSIGNMENT_NOT_ACTIVATED = True` remains; VRF integration is not production activation

---

## 8. Review Lane Wiring Track

**Authorized scope:** The J-003 taxonomy defines T0.5 (pending public ingestion) as the
quarantine state before T1+ admission. The review lane wiring track implements the
T0.5→T1+ admission runtime: dedup enforcement, reviewer-payment settlement stub, and the
`REVIEW_LANE_WIRING_COMPLETE` token.

**Phase 1414 ADR scope:**
- Admission gate: what evidence passes a T0.5 node to T1+ (minimum reviewer count, quorum)
- Dedup enforcement at admission: canonical external_id check against nullifier registry
- Reviewer-payment settlement stub: how payment instructions are queued (not executed)
- Integration with `ingestion_shadow_harness.py` (Phase 1397) admission path

**Phase 1415 implementation scope:**
- `ilc_core/epistemic/review_lane_admission_runtime.py`
- `REVIEW_LANE_ADMISSION_VERSION` version token
- T0.5→T1+ gate: reviewer count check, quorum check, dedup check
- Production serving and payment settlement remain default-off

**Phase 1416 scope:**
- Dedup enforcement wired into admission runtime
- Reviewer-payment settlement stub: `queue_reviewer_payment_stub()` — queues instructions,
  does not execute; `REVIEWER_PAYMENT_NOT_ACTIVATED` constant preserved
- Integration tests with Phase 1397 harness

---

## 9. Anti-Capture Diversity Track

**Authorized scope:** J-008 `ANTI_CAPTURE_DIVERSITY_VERIFIED` requires confirming that the
CDL-V3 diversity floor and VRF wiring together prevent operator-domain capture in production
jury assignment. This is a design + verification pass, not a new CDL.

**Phase 1418 scope:** Document the anti-capture design: CDL-V3 diversity floor applied to
VRF-assigned panels; independence_k=3 enforcement at production scale; operator-domain cap
with VRF as the selection primitive.

**Phase 1419 scope:** Verification pass — confirm that the Phase 1412 VRF integration
correctly enforces CDL-V3 + independence_k=3 constraints. Record
`anti_capture_diversity_verified_phase_1419` token.

---

## 10. Copyright Counsel Disposition (Phase 1420)

**ADR-0041 §5** records a copyright boundary on extraction provenance: if a submitted node
derives from copyrighted third-party text (DOI-anchored paper content, arXiv abstract body),
a counsel disposition is required before the network can reward such content through the
review lane. Phase 1420 closes this condition via:

- A Genesis-authority self-counsel disposition document (following the pattern established in
  Phase 1388a for CDL-048)
- The disposition must address: (a) extractive provenance vs. original work boundary,
  (b) fair use scope for academic-abstract-anchored nodes, (c) conditions under which
  reward eligibility applies to such nodes
- Token: `copyright_counsel_disposition_phase_1420`
- Sensitivity: SENSITIVE (governance disposition under Genesis authority)
- Does NOT constitute external legal advice; Genesis-authority self-counsel only

---

## 11. Launch Readiness Design Track (Phases 1422–1424)

### 11.1 Launch Readiness Manifest Schema (Phase 1422)

Define `public_rc_launch_readiness_manifest_v1` structure. The manifest is a Genesis-signable
artifact aggregating existing machine-verifiable gate verdicts:

- Field: `hardening_gate_verdict` — from Phase 1387 rerun v0.2 (`pre_activation_hardening_gate_pass_phase_1387`)
- Field: `public_claimability_gate_verdict` — from Phase 1389 rerun v0.2 (`result=public_claimability_activated`)
- Field: `jury_activation_gate_verdict` — from Phase 1427 gate re-run (`production_jury_activation_gate_pass_phase_1427`)
- Field: `soft_rc_eligible` — from Phase 1426 (`soft_rc_eligible=true`)
- Field: `validator_identity_bundle_hashes` — public keys of bootstrap VPS agents (post-ADR-0038 init)
- Field: `genesis_root_envelope_hash` — from Phase 1340 signing ceremony
- Field: `non_claim_inventory` — list of things that are explicitly NOT claimed
- Field: `unresolved_blockers` — should be empty at manifest time

The manifest is a spec document phase; no runtime code is written in Phase 1422.

### 11.2 Private Soft-RC Rehearsal Entry Criteria (Phase 1423)

Document the entry criteria and operational plan for the private soft-RC rehearsal:

**Topology:** 3 machines, 7 agents — mirroring launch roadmap v1.1.

**Agent identity init:** Each VPS generates its own keypair locally via the ADR-0038 +
ADR-0041 INIT path. Public identity bundles exported to Genesis. Genesis does NOT generate
and distribute private keys to VPS agents (practices correct operational path).

**What persists through wipe/reinit:**
- Genesis Agent 01 identity, all committed ADR/CDL/spec artifacts, signed root envelope

**What has wipe rights:**
- LMDB state, local graph DB, nullifier registries, test agent graph content, rehearsal
  economic balances, jury harness outputs

**Test dataset — Phase 1 (initial rehearsal):**
- ~50–100 hand-curated synthetic mathematical nodes with known provenance relationships
  (axioms → lemmas → theorems → corollaries)
- Expected taxonomy: T0→T0.5→T2 progression with known correct outcomes
- Rationale: deterministic expected outcomes, suitable for automated regression; obscures
  no infrastructure failures behind bulk-import complexity

**Test dataset — Phase 2 (second rehearsal after infrastructure confirmed):**
- Lean Mathlib subset: PFR (Polynomial Freiman-Ruzsa) formalization chain or Lean 4 Mathlib
  axiom ancestry graph. Apache 2.0 licensed; no copyright concern for internal rehearsal.
- Rationale: real-world content complexity; provenance chains from first principles; T2/T5/T6
  taxonomy variety

**Agent behavioral mode:** Deterministic scripted agents only during infrastructure validation.
No live LLM API calls until after multi-machine QUIC networking and basic epoch cycling are
confirmed. LLM integration introduced after scripted-agent baseline is stable.

**Key open question to resolve in Phase 1423:** Whether the 7 rehearsal agent identities
carry over to public RC or whether public RC starts with fresh identities.

### 11.3 Public RC Activation Certificate Design (Phase 1424)

Define `activation_certificate_v1` structure:
- Signed by Genesis Agent 01 under ADR-0037 / ADR-0038 authority chain
- References `public_rc_launch_readiness_manifest_v1` hash
- Defines the epoch 0→1 transition trigger: validators accept this certificate as the
  transition from pre-launch (epoch 0) to active (epoch 1)
- Does NOT rely on any jury vote or graph content claim to start protocol time (circular
  bootstrap problem avoided)

**Post-activation provenance node design:**
- After epoch 1 starts, Genesis may publish a normal public graph node recording the
  activation event (citing the manifest hash and certificate hash as provenance)
- This "hello world" node is a T6 validator-consensus-class fact record
- It does NOT trigger or cause epoch 1 start; it records it after the fact
- It can be reviewed, attested, and retained through the normal review lane

---

## 12. CDL Number Assignments

| CDL | Title (candidate) | Decision digest anchor | Opening phase | Ratification phase |
|-----|-------------------|----------------------|---------------|--------------------|
| CDL-091 | Jury Incentive Economics | fixed base review fee + accuracy-weighted bonus; approval-volume bias mitigation | Phase 1399 | Phase 1400 |
| CDL-092 | CapProof Content-Addressing, CV Signing, and Pricing Band | CapProof hash inputs; Genesis-rooted CV signing chain; ±15% band | Phase 1402 | Phase 1405 |
| CDL-093 | Maintenance Lottery Pool Distribution | funding source; draw mechanism (VRF or epoch-hash); eligibility criteria | Phase 1406 | Phase 1408 |

CDL-091/092/093 are pre-authorized by the J-008 gate conditions. No additional opening
authorization is required beyond the sequence lock GO.

---

## 13. Candidate Phase Table

| Order | Phase | Topic | Character | Sensitivity |
|-------|-------|-------|-----------|-------------|
| 1 | 1399 | CDL-091 jury incentive economics — prelock | Constitutional | **SENSITIVE** |
| 2 | 1400 | CDL-091 jury incentive economics — ratification | Constitutional | **SENSITIVE** |
| 3 | 1401 | CDL-091 jury incentive economics runtime stub | Runtime | NON-SENSITIVE |
| 4 | 1402 | CDL-092 CapProof — opening | Constitutional | **SENSITIVE** |
| 5 | 1403 | CDL-092 CapProof — deliberation | Constitutional | constitutional |
| 6 | 1404 | CDL-092 CapProof — prelock | Constitutional | constitutional |
| 7 | 1405 | CDL-092 CapProof — ratification | Constitutional | **SENSITIVE** |
| 8 | 1406 | CDL-093 maintenance lottery pool — opening | Constitutional | **SENSITIVE** |
| 9 | 1407 | CDL-093 maintenance lottery pool — deliberation / prelock | Constitutional | constitutional |
| 10 | 1408 | CDL-093 maintenance lottery pool — ratification | Constitutional | **SENSITIVE** |
| 11 | 1409 | CDL-093 maintenance lottery pool runtime stub | Runtime | NON-SENSITIVE |
| 12 | 1410 | VRF proof verifier ADR | Spec / ADR | NON-SENSITIVE |
| 13 | 1411 | VRF proof verifier implementation | Runtime | NON-SENSITIVE |
| 14 | 1412 | VRF integration with jury_assignment_runtime.py | Runtime | NON-SENSITIVE |
| 15 | 1413 | VRF integration tests and security review | Testing | NON-SENSITIVE |
| 16 | 1414 | Review lane wiring — T0.5→T1+ ADR | Spec / ADR | NON-SENSITIVE |
| 17 | 1415 | Review lane wiring — admission runtime | Runtime | NON-SENSITIVE |
| 18 | 1416 | Review lane wiring — dedup + payment settlement stub | Runtime | NON-SENSITIVE |
| 19 | 1417 | Review lane wiring — integration tests; `REVIEW_LANE_WIRING_COMPLETE` token | Testing | NON-SENSITIVE |
| 20 | 1418 | Anti-capture diversity — CDL-V3 + VRF wiring design | Spec | NON-SENSITIVE |
| 21 | 1419 | Anti-capture diversity — production verification; `anti_capture_diversity_verified_phase_1419` | Runtime/Audit | NON-SENSITIVE |
| 22 | 1420 | Copyright counsel disposition — ADR-0041 §5 | Governance | **SENSITIVE** |
| 23 | 1421 | Window coherence and capsule update | Synthesis | NON-SENSITIVE |
| 24 | 1422 | Launch Readiness Manifest schema — `public_rc_launch_readiness_manifest_v1` | Spec | NON-SENSITIVE |
| 25 | 1423 | Private soft-RC rehearsal entry criteria — 3-machine / 7-agent topology plan | Spec | NON-SENSITIVE |
| 26 | 1424 | Public RC activation certificate design — `activation_certificate_v1`; hello-world node design | Spec | NON-SENSITIVE |
| 27 | 1425 | Pre-gate re-run verification — confirm all 7 blocking conditions MET | Gate | NON-SENSITIVE |
| 28 | 1426 | Soft RC gate re-run — record `soft_rc_eligible=true` | Gate | **SENSITIVE** |
| 29 | 1427 | J-008 gate re-run — `evaluate_jury_activation_gate()` expecting `verdict="PASS"` | Gate | **SENSITIVE** |
| 30 | 1428 | Window 1399–1428 closure gate | Gate | **SENSITIVE** |

### Note on Phase 1399 (CDL-091 prelock)

CDL-091 was opened in Phase 1394 (J-004) with opening spec
`docs/specs/ilc_cdl_jury_incentive_economics_opening_v0.1.md`. Phase 1399 is the prelock, not
a re-opening. The deliberation questions from the Phase 1394 spec must be resolved in the
prelock document. Historical hardening test must assert CDL-091 at `status: open` at the
Phase 1394 opening commit ref.

### Note on Phase 1405 / 1408 runtime mutation pattern

CDL-092 and CDL-093 ratification phases (1405, 1408) may or may not include simultaneous
runtime stub commits. If runtime stubs are not ready at ratification time, they follow in
dedicated phases (1409 for CDL-093, no separate phase needed for CDL-092 since the CapProof
runtime wiring is part of the review lane track at Phase 1415-1416). All CDL register mutations
require two-commit pattern: Commit 1 = runtime/tests (if any), Commit 2 = CDL doc mutation only.

### Note on Phase 1427 gate re-run

`evaluate_jury_activation_gate()` in `ilc_core/epistemic/jury_activation_gate.py` evaluates
conditions dynamically by checking for token presence or module-level flags. For conditions
that require checking external modules or files, the gate module must be confirmed (via Phase
1425 pre-gate verification) to correctly detect the new tokens before Phase 1427 executes.
If the gate module's condition checks are token-string-based (checking a hardcoded token list),
the condition-checking functions may need to be updated in a Phase 1425a to accept the new
completion tokens. This must be verified in Phase 1425.

---

## 14. Sensitivity Classification

### SENSITIVE phases (require explicit GO token)

- **Phase 1399** — CDL-091 prelock: CDL is open; prelock hardens but does not mutate register.
  SENSITIVE because it is a constitutional prelock authorizing future ratification GO.
- **Phase 1400** — CDL-091 ratification: CDL register mutation (`ILC_CDL_MUTATION_AUTHORIZED=1`).
- **Phase 1402** — CDL-092 opening: CDL register mutation (`ILC_CDL_MUTATION_AUTHORIZED=1`).
- **Phase 1405** — CDL-092 ratification: CDL register mutation (`ILC_CDL_MUTATION_AUTHORIZED=1`).
- **Phase 1406** — CDL-093 opening: CDL register mutation (`ILC_CDL_MUTATION_AUTHORIZED=1`).
- **Phase 1408** — CDL-093 ratification: CDL register mutation (`ILC_CDL_MUTATION_AUTHORIZED=1`).
- **Phase 1420** — Copyright counsel disposition: Genesis-authority governance decision.
- **Phase 1426** — Soft RC gate re-run: constitutional gate; first `soft_rc_eligible=true` verdict.
- **Phase 1427** — J-008 gate re-run: constitutional gate; first `production_jury_activation_gate_pass` verdict.
- **Phase 1428** — Window closure gate: structural boundary.

### NON-SENSITIVE phases (may proceed after prompt approval)

All other phases: 1401, 1403, 1404, 1407, 1409, 1410, 1411, 1412, 1413, 1414, 1415, 1416,
1417, 1418, 1419, 1421, 1422, 1423, 1424, 1425.

### Pre-commit hook requirement

CDL register mutations require:
```
ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=<phase>
```
Required for: Phases 1400, 1402, 1405, 1406, 1408.

CDL prelock phases (1399, 1403-1404, 1407) do NOT mutate the register; no hook required.

---

## 15. Scope Notes for Fixed Phases

### Phase 1399 — CDL-091 jury incentive economics prelock
**SENSITIVE.** Requires explicit `GO Phase 1399` before executing.

**Deliverables:**
- `docs/specs/ilc_cdl_091_jury_incentive_economics_prelock_1399_v0.1.md`
- `tests/test_phase_1399_cdl_091_prelock.py` — historical hardening (assert CDL-091 `status: open` at Phase 1394 commit)

**Required prelock content:**
- Resolved deliberation questions: funding source, bonus calculation formula, bias mitigation mechanism
- Locked governance constants: base fee (Decimal, ECU), accuracy-weight bonus formula, panel size factor
- Explicit non-ratification statement: "CDL-091 remains open and unratified after Phase 1399"

**Commit subject:** `const(1399): CDL-091 jury incentive economics prelock`

---

### Phase 1400 — CDL-091 ratification
**SENSITIVE.** Requires explicit `GO Phase 1400` and `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1400`.

**Deliverables:**
- `docs/specs/ilc_cdl_091_jury_incentive_economics_ratification_evidence_1400_v0.1.md`
- CDL-only mutation commit: changes CDL-091 row from `open` to `ratified`
- `tests/test_phase_1400_cdl_091_ratification.py` — 2 tests (prelock hardening + ratification evidence)

**Commit pattern:** 2 commits — Commit 1: evidence doc + tests (no CDL env); Commit 2: CDL mutation only.
**Commit subject (C2):** `const(1400): CDL-091 jury incentive economics ratification`

---

### Phase 1402 — CDL-092 CapProof opening
**SENSITIVE.** Requires explicit `GO Phase 1402` and `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1402`.

**Deliverables:**
- `docs/specs/ilc_cdl_092_capproof_opening_1402_v0.1.md` — opening scope and deliberation questions
- CDL register mutation: CDL-092 row added with `status: open`
- `tests/test_phase_1402_cdl_092_opening.py` — confirm CDL-092 open and unratified

**Commit pattern:** 2 commits — Commit 1: opening doc + tests; Commit 2: CDL mutation.
**Commit subject (C2):** `const(1402): CDL-092 CapProof pricing and signing opening`

---

### Phase 1405 — CDL-092 ratification
**SENSITIVE.** Requires explicit `GO Phase 1405` and `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1405`.

Pattern is identical to Phase 1400 (CDL-091 ratification). Evidence doc, 2-commit pattern,
prelock hardening at Phase 1402 opening commit ref.

**Commit subject (C2):** `const(1405): CDL-092 CapProof ratification`

---

### Phase 1406 — CDL-093 maintenance lottery pool opening
**SENSITIVE.** Requires explicit `GO Phase 1406` and `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1406`.

Pattern identical to Phase 1402.
**Commit subject (C2):** `const(1406): CDL-093 maintenance lottery pool opening`

---

### Phase 1408 — CDL-093 ratification
**SENSITIVE.** Requires explicit `GO Phase 1408` and `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1408`.

Pattern identical to Phase 1400/1405.
**Commit subject (C2):** `const(1408): CDL-093 maintenance lottery pool ratification`

---

### Phase 1411 — VRF proof verifier implementation
**NON-SENSITIVE.** Proceeds after Phase 1410 ADR approval.

**Deliverables:**
- `ilc_core/epistemic/vrf_proof_verifier.py`
- `tests/test_phase_1411_vrf_proof_verifier.py` — minimum 15 tests
- Required token in source: `vrf_proof_verifier_implemented_phase_1411`
- No `import random` (ICSS §2); use `secrets` or `cryptography` library for any randomness
- No float values for VRF outputs (ICSS §3); outputs are bytes or Decimal

**Commit subject:** `feat(1411): VRF proof verifier implementation`

---

### Phase 1427 — J-008 gate re-run
**SENSITIVE.** Requires explicit `GO Phase 1427`. All 7 blocking conditions must be confirmed
MET by Phase 1425 pre-gate verification before this phase executes.

**Deliverables:**
- `docs/specs/ilc_jury_activation_gate_rerun_report_1427_v0.1.md`
- `tests/test_phase_1427_j008_gate_rerun.py` — confirm `verdict="PASS"`, `blocking_not_met=[]`,
  `production_activated=False` (gate PASS does not activate production)
- Token: `production_jury_activation_gate_pass_phase_1427`

**Non-authorizations:** Gate PASS does not activate production jury assignment, live reviewer
payment, live ECU distribution, public jury admission, or public RC publication. Those require
a separate production GO.

**Commit subject:** `gate(1427): J-008 gate rerun — verdict PASS`

---

### Phase 1428 — Window 1399–1428 closure gate
**SENSITIVE.** Requires explicit `GO Phase 1428`.

Follows `docs/specs/ilc_window_closure_handoff_doc_schema_v0.1.md`. Must record:
- `window_1399_1428_closed_phase_1428.v0.1`
- `window_1399_1428_closure_verdict_recorded_phase_1428`
- `mempalace_refresh_disposition_recorded_phase_1428`
- `window_1429_not_open_phase_1428`
- `go_window_1429_required_next`

---

## 16. Key Dependencies and Open Questions

### Must-resolve at window entry (before Phase 1399)

| Item | Resolution needed |
|------|------------------|
| CDL-091 deliberation questions from Phase 1394 | Resolved in Phase 1399 prelock |
| Next fresh CDL number confirmed as CDL-091 | Confirmed — CDL-090 is last ratified CDL |
| Gate condition token-checking mechanism in `jury_activation_gate.py` | Verify in Phase 1425 that condition checks will detect new tokens; update if needed |

### Sequencing constraints

- Phase 1400 requires Phase 1399 complete
- Phase 1405 requires Phase 1402-1404 complete
- Phase 1408 requires Phase 1406-1407 complete
- Phase 1412 requires Phase 1411 complete
- Phase 1419 requires Phase 1412 and Phase 1417 complete (both VRF and review lane needed)
- Phase 1425 requires Phases 1400, 1405, 1408, 1413, 1417, 1419, 1420 all complete
- Phase 1426 requires Phase 1425 complete
- Phase 1427 requires Phase 1426 complete
- Phase 1428 requires Phase 1427 complete

CDL tracks (1399-1409), VRF track (1410-1413), review lane track (1414-1417), and anti-capture
track (1418-1419) are mostly independent and may be interleaved or parallelized.

### Open questions

| Question | Stakes | Resolution path |
|----------|--------|-----------------|
| Does maintenance lottery CDL-093 use VRF or epoch-hash draw? | Sequencing: if VRF, CDL-093 ratification should follow Phase 1412 | Resolve at Phase 1407 deliberation |
| Do rehearsal VPS agent identities carry over to public RC? | Launch narrative coherence | Resolve in Phase 1423 |
| Does Phase 1427 gate re-run require source changes to `jury_activation_gate.py` condition checks? | May add Phase 1425a if needed | Verify in Phase 1425 |

### Permanently deferred from this window

- Mode-2 settlement-grade refutation path (stake calibration, CDL-029 wiring)
- GOVERNS/CONSTRAINS merge CDL
- Production activation of reviewer payment (requires production GO after gate PASS)
- Public RC publication

---

## 17. Known Patterns and Technical Constraints

### Novel patterns this window

1. **First VRF implementation in `ilc_core/`:** VRF introduces a new cryptographic primitive.
   Algorithm must be consistent with ADR-0038 agent keypairs (Ed25519 or equivalent). The
   `vrf_proof_verifier.py` module verifies proofs but does NOT generate proofs (no private key
   operations in `ilc_core/`). Proof generation is an operator/consensus-layer concern.

2. **Review lane wiring completes the T0.5→T1+ path:** This is the first time the full
   ingestion pathway from raw submission through quarantine to public admission has runtime
   support. Be careful not to activate the serving path — wiring means the admission gate
   exists and is tested, not that it is live.

3. **Multi-CDL prelock in single window:** Three CDL prelock/ratification sequences in one
   window. The historical hardening test for each ratification must reference the correct
   opening commit ref for its CDL, not a shared ref. Each CDL's prelock test asserts the
   CDL's `status: open` at its own opening commit, not at another CDL's opening.

### Historical prelock hardening

Each ratification phase (1400, 1405, 1408) must harden the corresponding prelock test to
assert the CDL is at `status: open` at the historical opening commit ref:
- Phase 1400: assert CDL-091 at Phase 1394 opening commit (`4d7aa833`)
- Phase 1405: assert CDL-092 at Phase 1402 opening commit (TBD)
- Phase 1408: assert CDL-093 at Phase 1406 opening commit (TBD)

### Phantom edit guard

The following `ilc_core/` runtime files are mutation targets in this window:
- `ilc_core/epistemic/jury_assignment_runtime.py` (Phase 1412 VRF integration)
- New files: `vrf_proof_verifier.py`, `review_lane_admission_runtime.py`, `jury_incentive_runtime.py`

For Phase 1412, verify before committing that `jury_assignment_runtime.py` only contains the
intended VRF integration changes and has not acquired phantom edits from other phases.
Detection: `git diff HEAD -- ilc_core/epistemic/jury_assignment_runtime.py`

### Pre-commit hook clean-state guard

Runtime mutation phases (1401, 1411, 1412, 1415, 1416) and CDL mutation phases (1400, 1402,
1405, 1406, 1408) must be in separate commits. Runtime and CDL mutations must never appear
in the same commit. The pre-commit hook enforces this.

### ILC Coding Security Standards

All new `ilc_core/` modules in this window must satisfy:
- §1: `sort_keys=True` on all protocol-artifact JSON
- §2: No `import random` — use `secrets` or `cryptography` for any randomness in VRF
- §3: No float for ECU/reward values — Decimal only
- §4: No `assert` in production paths
- §5: OOM guards on any network streams
- §8: TLS verification must not be disabled
- §9: Atomic writes for protocol artifacts

---

## 18. Non-Goals and Explicitly Deferred Items

- Does NOT activate production reviewer payment (CDL-091 ratification is governance; payment
  activation requires a separate production GO after J-008 gate PASS)
- Does NOT activate production jury assignment for any node tier
- Does NOT activate CapProof pricing in any live context
- Does NOT activate the maintenance lottery pool
- Does NOT publish public RC artifacts, sign releases, push to public repository
- Does NOT activate public HTTP claimability serving (Phase 1389 activated the gate verdict;
  serving remains separately gated)
- Does NOT complete Mode-2 settlement-grade refutation path
- Does NOT open or ratify any CDL beyond CDL-091/092/093
- Does NOT constitute a mainnet launch
- Does NOT claim external legal advice (Phase 1420 is Genesis-authority self-counsel only)

---

## 19. Key Canonical Anchors for Prompt Drafting

- **PRIMARY context reference:** `docs/specs/ilc_antigravity_context_capsule_v5.58.md`
- **Prior window closure:** `docs/specs/ilc_window_1369_1390_handoff_1390_v0.1.md`
- **J-008 gate spec:** `docs/specs/ilc_production_jury_activation_gate_j008_v0.1.md`
- **J-008 walkthrough:** `docs/phases/phase_1398_j008_production_jury_activation_gate_walkthrough.md`
- **CDL register:** `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- **J-004 CDL opening:** `docs/specs/ilc_cdl_jury_incentive_economics_opening_v0.1.md`
- **ADR-0040 (jury eligibility + VRF boundary):** `docs/adr/ADR_0040_Jury_Eligibility_Assignment.md`
- **ADR-0041 (ingestion + §5 copyright boundary):** `docs/adr/ADR_0041_Agent_INIT_and_Ingestion_Protocol.md`
- **J-005 CapProof boundary:** `docs/specs/ilc_epoch_start_capability_maintenance_contract_v0.1.md`
- **J-006 jury assignment runtime:** `ilc_core/epistemic/jury_assignment_runtime.py`
- **J-007 shadow harness:** `ilc_core/epistemic/ingestion_shadow_harness.py`
- **J-008 gate module:** `ilc_core/epistemic/jury_activation_gate.py`
- **Phase completion log:** `docs/phases/STATUS.md`
- **ADM-003 reference:** 7+1 panel architecture; `independence_k=3`; outsider-seat rule
- **Launch roadmap:** `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md`
- **For Phase 1428 closure gate:** all Phase 1399–1427 test files and artifacts

---

*This document is a PROPOSAL. It requires human review and explicit `GO Window 1399` (or
equivalent sequence lock authorization) before any phase executes.*
