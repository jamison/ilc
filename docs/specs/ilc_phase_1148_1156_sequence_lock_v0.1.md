# ILC Phase 1148-1156 Sequence Lock v0.1

Status: locked by Phase 1148
Date: 2026-05-04
Window: 1148-1156
Sensitivity: mixed; Phases 1148-1154 NON-SENSITIVE, Phase 1155 SENSITIVE, Phase 1156 conditional SENSITIVE

`window_1148_1156_sequence_lock_committed`

---

## 1. Purpose

This sequence lock opens Window 1148-1156 from the Phase 1147 handoff and capsule v5.39.
The firm work is Atlas Tier-2 candidate construction, GENESIS-COMPILE checkpoint #2,
Genesis 32-node composability audit, SIM-SPECTRAL-04 program specification, Genesis
Canonical Lineage Contract planning, and pre-public-RC obligations synthesis.

This window does not open or ratify any CDL. `CDL-085` remains unopened and SIM-gated.
This window does not mutate signed v0.1 Genesis artifacts.

---

## 2. Firm Phase Order

| Order | Phase | Topic | Sensitivity |
|-------|-------|-------|-------------|
| 1 | 1148 | Sequence lock + ADR status normalization | NON-SENSITIVE |
| 2 | 1149 | Atlas Tier-2 curated seed patch, v0.2 candidate | NON-SENSITIVE |
| 3 | 1150 | GENESIS-COMPILE checkpoint #2 | NON-SENSITIVE |
| 4 | 1151 | Genesis 32-node composability audit | NON-SENSITIVE |
| 5 | 1152 | SIM-SPECTRAL-04 program spec | NON-SENSITIVE |
| 6 | 1153 | Genesis Canonical Lineage Contract planning spec | NON-SENSITIVE |
| 7 | 1154 | Pre-public-RC obligations synthesis | NON-SENSITIVE |
| 8 | 1155 | Coherence + capsule v5.40 + closure gate | SENSITIVE |
| 9 | 1156 | Atlas Tier-2 signing ceremony | conditional SENSITIVE |

Phases 1148-1154 may be Strike Forced because they are NON-SENSITIVE and do not mutate
CDLs, runtime semantics, or signed v0.1 artifacts. Phase 1155 requires explicit human GO.
Phase 1156 executes only if separately authorized under a release key or Genesis
exceptional signing path.

---

## 3. ADR Status Normalization Gate

The hard gate for Phase 1148 is:

`adr_status_normalization_required_before_tier2_promotion`

All planning-bridge ADR candidates are audited against file headers before Phase 1149.
The promotion rule is strict: Phase 1149 may reflect accepted canon only. Proposed ADRs
are blocked from canonical Tier-2 promotion.

| ADR | Correct title | Header status | Phase 1148 disposition |
|-----|---------------|---------------|------------------------|
| ADR-0019 | Graph-Native Governance Compilation Boundary | Accepted | promote in Phase 1149 |
| ADR-0026 | Protocol vs Harness/Product Boundary | Accepted | promote in Phase 1149 |
| ADR-0028 | Settlement Substrate Graduation and Governance Route | Accepted | promote in Phase 1149 |
| ADR-0031 | Subgraph Homomorphism Query Contract | Accepted | promote in Phase 1149 |
| ADR-0012 | ECU-ILC-Graph Coupling and Anti-Reflexivity Contract | Proposed | blocked |
| ADR-0020 | Knowledge-Node-First Design Principle | Proposed | blocked; priority acceptance review before Tier-3 |
| ADR-0022 | Local-First Private Use and Publication-Bound Economics | Proposed | blocked |
| ADR-0023 | Multi-Layer Quality Signal Architecture | Proposed | blocked |
| ADR-0008 | Node Usefulness vs Governance Weight and Genesis Dilution | Proposed | blocked |
| ADR-0034 | D2d Sealed-Sender Mechanism | Accepted | deferred to Window 1166+ Tier-3 runtime linkage |

Disposition tokens:

- `adr_0019_tier2_promote_phase_1149`
- `adr_0026_tier2_promote_phase_1149`
- `adr_0028_tier2_promote_phase_1149`
- `adr_0031_tier2_promote_phase_1149`
- `adr_0012_tier2_blocked_status_proposed_not_accepted`
- `adr_0020_tier2_blocked_status_proposed_not_accepted`
- `adr_0022_tier2_blocked_status_proposed_not_accepted`
- `adr_0023_tier2_blocked_status_proposed_not_accepted`
- `adr_0008_tier2_blocked_status_proposed_not_accepted`
- `adr_0034_tier2_deferred_to_window_1166_plus`
- `adr_0020_acceptance_review_priority_before_tier3_embedding_linkage`

---

## 4. Atlas Tier-2 Candidate Scope

Phase 1149 produces an unsigned v0.2 candidate star map:

- Accepted ADRs promoted: 4.
- Expected node count: 36 nodes (32 signed v0.1 nodes + 4 accepted ADR nodes).
- Output: `out/genesis_core_star_map_v0.2_candidate.json`.
- Curated seed: `docs/sims/sim_spectral_02/genesis_core_star_map_curated_seed_v0.2.json`.

Signed v0.1 artifacts remain untouched:

- `out/genesis_core_star_map_v0.1.json`
- `out/genesis_compile_coverage_diagnostic_v0.1.json`
- `out/genesis_signing_root_envelope_v0.1.json`
- `out/genesis_signing_root_envelope_v0.1.sig`

---

## 5. Tooling Preconditions

GENESIS-COMPILE diagnostic supports versioned paths now:

- `tools/genesis_compile_coverage_diagnostic.py --star-map`
- `tools/genesis_compile_coverage_diagnostic.py --json-out`
- `tools/genesis_compile_coverage_diagnostic.py --report-out`

The crawler currently supports versioned output paths but must receive a versioned curated
seed path before Phase 1149 can safely build v0.2. If it lacks `--curated-seed`, Phase
1149 must add that flag before generating v0.2 candidate artifacts.

---

## 6. CDL And Runtime Boundary

No CDL mutation is authorized in firm Phases 1148-1154.

`CDL-085` remains SIM-gated for the whole firm window and cannot open without positive
SIM-SPECTRAL-04 evidence plus explicit human override of Phase 1146 DEFER.

Runtime semantic mutations are out of scope. `epoch_attribution_settle_runtime_1129_fix1.v0.5`
remains the runtime frontier.

---

## 7. Conditional Tail Slot

Phase 1156 is not firm. Scenario A is effectively deferred because no operational release
key ADR is in scope this window. Scenario B requires explicit human Genesis exceptional
signing authorization. If neither is authorized by Phase 1155, Phase 1156 does not
execute and the v0.2 candidate remains unsigned.

`phase_1156_scenario_a_release_key_deferred_to_window_1157_plus`

---

`window_1148_1156_sequence_lock_committed`
