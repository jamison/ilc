# ILC Integration Coherence Report — Phase 944

**Window:** 939–944 (post-H-013: SIM-BEACON-01, SIM-REUSE-01, CDL-081 ratification)
**Phase:** 944
**Date:** 2026-04-28
**Capsule:** v5.31 (v5.32 to follow at Phase 945)

---

## 1. Summary

This coherence report covers the work executed in Phases 939–943 following the
closure of H-013 window 930–938. Three tracks completed:

1. **SIM-BEACON-01** (Phase 939) — noise budget calibration for gossip beacon
   emission parameters. Key finding: adversary reduction is mathematically
   constant (~0.68) for T=10 Gaussian averaging, regardless of sigma. Real
   privacy protection comes from sealed-sender (ADR-0034), not sigma alone.

2. **SIM-REUSE-01** (Phases 940–941) — REUSE edge attribution rate calibration.
   Resolved CDL-081 Q6: `REUSE_ATTRIBUTION_RATE = Decimal("0.20")`. Sharp floor
   confirmed at rate=0.10. Gaming structurally non-attractive at all rates.

3. **CDL-081 ratification** (Phases 942–943) — Hyperedge ECU attribution
   constitutionally locked. 30 ratification evidence tests. Two-commit pattern
   enforced by pre-commit hook (runtime mutation separate from CDL log mutation).

Additionally, two housekeeping actions were performed in this session:
- **Phase file zero-padding** (897 `docs/phases/` files renamed — 4-digit numbers)
- **CLAUDE.md created** (mandatory phase workflow instructions, schema citations)

---

## 2. What Changed This Window

| Phase | Artifact | Type |
|-------|----------|------|
| 939 | `simulations/sim_beacon_01_noise_budget_938.py` | Simulation |
| 939 | `simulations/run_sim_beacon_01_938.py` | Simulation runner |
| 939 | `docs/specs/ilc_sim_beacon_01_noise_budget_commissioning_results_939_v0.1.md` | Evidence |
| 940–941 | `simulations/sim_reuse_01_attribution_rate_940.py` | Simulation |
| 940–941 | `simulations/run_sim_reuse_01_940.py` | Simulation runner |
| 941 | `docs/specs/ilc_sim_reuse_01_attribution_rate_results_synthesis_941_v0.1.md` | Synthesis |
| 941 | `docs/specs/ilc_cdl_081_hyperedge_ecu_attribution_opening_929_v0.1.md` (Q6 lock) | CDL update |
| 942 | `tests/test_phase_942_cdl_081_hyperedge_ecu_attribution.py` (30 tests) | Tests |
| 942 | `docs/specs/ilc_cdl_081_hyperedge_ecu_attribution_ratification_evidence_942_v0.1.md` | Evidence |
| 943 | `ilc_core/types.py`: `REUSE_ATTRIBUTION_RATE = Decimal("0.20")` | Runtime mutation |
| 943 | CDL-081 spec: OPEN → RATIFIED | CDL mutation |
| 943 | Constitutional decision log: CDL-081 ratified entry | CDL mutation |
| — | `docs/phases/` 897 files zero-padded to 4-digit numbers | Housekeeping |
| — | `CLAUDE.md` created with mandatory phase workflow instructions | Housekeeping |

---

## 3. Cross-Cutting Coherence

### 3.1 CDL-081 constitutional chain complete

CDL-081 constitutionalises ECU attribution for hyperedge traversal. The full
decision chain is locked:

| Question | Decision |
|----------|----------|
| Q1 Edge type triggers | REUSE + CO_AUTHORSHIP trigger; ATTESTATION / EPOCH_BOUNDARY excluded; REFUTATION conditional on CDL-V7 |
| Q2 Stake floor | None — zero-member → commons transition via ADR-0015 / CDL-047 |
| Q3 Buy-in decay | CDL-V1 temporal decay from buy-in epoch; no hard lockout |
| Q4 Ejected stake | Treasury accumulation (H-CON-02 quorum required for distribution) |
| Q5 Attribution target | Target node creator receives ECU (Option A); consumer excluded |
| Q6 Per-traversal rate | `REUSE_ATTRIBUTION_RATE = Decimal("0.20")` — SIM-REUSE-01 evidence |

### 3.2 SIM-BEACON-01 model limitation — sealed-sender is the primary mechanism

The Q-SIGMA sweep found that `adversary_reduction ≈ 0.684` regardless of sigma.
This is the mathematical constant `1 - 1/√T` for T=10 observations — Gaussian
averaging always reduces estimation error by this fraction, independent of noise
magnitude. The privacy target (adversary_reduction ≤ 0.50) is not achievable via
sigma tuning with a T=10 free-observation adversary.

**Correct interpretation:** In the ADR-0034 sealed-sender context, accumulating
T=10 observations of the same node is non-trivial — each beacon is sealed
per-recipient with a different emission ID. The sealed-sender protocol is the
primary privacy mechanism; sigma noise is secondary obfuscation. The adversary
model needs revision for a future SIM before any mainnet sigma parameter change.

Provisional mainnet recommendations (pending CDL amendment):
- `H013_TESTNET_EMISSION_SIGMA = 0.05` — keep; routing correctness 97.65%
- `H013_CHANGE_THRESHOLD` → raise from 0.10 to 0.15 (exits spurious-emission regime)
- `DEFAULT_DEAD_PEER_SILENCE_EPOCHS = 10` — confirmed at 0% false-dead rate

### 3.3 SIM-REUSE-01 gaming resistance is structural

Gaming (fake reuse traversal at 1.5× creation cost) has `gaming_roi_ratio < 0.02`
at all tested rates. This is structural — a single fake traversal yields
`rate × TRAVERSAL_ECU_BASE` ECU while costing 1.5 ECU overhead. The mechanism is
gaming-resistant by design regardless of rate parameter choice.

### 3.4 REUSE_ATTRIBUTION_RATE type is Decimal, not float

`ilc_core/types.py` now declares `REUSE_ATTRIBUTION_RATE: Decimal = Decimal("0.20")`.
The ratification evidence test (Test 07) asserts both value equality and type:
`isinstance(REUSE_ATTRIBUTION_RATE, Decimal)`. Float is explicitly rejected — ECU
arithmetic requires Decimal precision. Any future amendment must preserve the
Decimal type.

### 3.5 EpochAttributionBatch.settle() remains gated

`CDL_HCON_01_DEPENDENCY = "h_con_01_cdl_required_before_settle_executes"` is still
active. `settle()` raises `NotImplementedError`. This is correct — H-012
(attribution runtime implementation) and H-CON-02 (panel quorum rules) are the
post-CDL-081 forward obligations. CDL-081 ratification does not automatically
unlock `settle()`.

### 3.6 Two-commit CDL ratification pattern confirmed

The pre-commit hook enforces that CDL-authorized commits (`ILC_CDL_MUTATION_AUTHORIZED=1`)
must not touch `ilc_core/` files. CDL-081 ratification used the correct two-commit
pattern:
- Commit 1 (`36b3eb4b`): `ilc_core/types.py` + test update (no CDL env var)
- Commit 2 (`41ef695e`): CDL-081 spec + constitutional log (CDL env var required)

---

## 4. Phase Numbering Remediation Notice

### 4.1 Situation

ILC uses two phase numbering tracks:

| Track | Range | Status |
|-------|-------|--------|
| Normal constitutional lane | 0055 – 0943 (current) | Active |
| Cluster-A G8 parallel track | 0951 – 1014 | **CLOSED** — all work complete |

The normal lane will collide with the Cluster-A range at **phase 0951** — currently
8 phases away.

### 4.2 Resolution

**The normal lane jumps from 0989 to 1100 before reaching 0951.**

Specifically:
- Phases 0944–0989: available for normal lane use (46 phases of runway)
- Phases 0951–1014: **permanently reserved** as Cluster-A G8 legacy range
- Phases 1015–1099: **reserved buffer** — do not use
- Phases 1100+: normal lane resumes

The skip is recorded in this coherence report and in CLAUDE.md as the authoritative
reference. No retroactive renaming of Cluster-A docs is required — the `g8_constitution_cluster_a_`
prefix in their filenames already distinguishes them.

### 4.3 Named series are unaffected

The following named series use non-integer phase identifiers and are unaffected:
- **B-series** (`B-1`..`B-5`) — Row 5 mechanism analysis track (CLOSED)
- **M-series** (`M-009`..`M-022`) — Mysticeti/milestone track
- **SIM-series** (`SIM-BEACON-01`, `SIM-REUSE-01`, etc.) — simulation evidence
- **H-series** (`H-013`, `H-012`, etc.) — horizontal implementation obligations
- **CDL-series** (`CDL-001`..`CDL-081`) — constitutional decision log

`phase_numbering_remediation_recorded_phase_944`
`normal_lane_skip_0989_to_1100_authorized`
`cluster_a_range_0951_1014_permanently_reserved`

---

## 5. Workflow Remediation

### 5.1 Artifact chain gap identified

Phases 849–943 (normal constitutional lane) were executed without the full
five-step artifact chain. `docs/phases/` walkthrough files were not produced for
any phase in this range. The work itself is complete and correct (all commits
and `docs/specs/` artifacts exist), but the pre-execution audit layer (Window
Guidance doc, Phase Prompt drafts) was missing.

### 5.2 Standing fix applied

Two artifacts lock the corrected workflow going forward:

- **`CLAUDE.md`** (project root) — loaded automatically by Claude Code every
  session. Cites all schemas. Prohibits autonomous SENSITIVE phase execution
  without human GO token. Prohibits self-declaring windows closed.

- **`memory/feedback_phase_window_workflow_mandatory.md`** — persists the rule
  with the *why* across Claude sessions.

### 5.3 Retrospective walkthrough policy

The ~94 phases without walkthrough files (849–943) are **not retroactively
regenerated** in this coherence report. The git commit record is authoritative.
If individual phase walkthroughs are needed for audit purposes, they should be
generated on demand from the git log, tagged as `**Status:** retrospective`.

`workflow_remediation_recorded_phase_944`
`claude_md_created_phase_workflow_instructions`
`docs_phases_zero_padded_4_digit_897_files`

---

## 6. Test Coverage

| Scope | Tests | Pass |
|-------|-------|------|
| CDL-081 ratification evidence | 30 | 30 |
| H-013 spectral beacon | 35 | 35 |
| Full regression | 7,643 collected | all pass |

30/30 CDL-081 ratification tests pass. Full regression clean.

---

## 7. Open Obligations Forward

| Item | Scope | Prerequisite |
|------|-------|-------------|
| H-012: `EpochAttributionBatch.settle()` runtime | Attribution runtime | CDL-081 ✅ |
| H-CON-02: Panel hyperedge quorum rules | PROVENANCE + treasury | CDL-081 ✅ |
| Werner φ-bound CDL | `EDGE_MINT_PHI_BOUND = None` | Separate CDL |
| SIM-BEACON-01 adversary model revision | Revised SIM with sealed-sender constraints | Future SIM |
| H013 `change_threshold` CDL amendment | Raise 0.10 → 0.15 | CDL amendment |
| H-011 patent assessment | PoSK admission gate | Ongoing |
| Capsule v5.32 | Phase 945 | This coherence report |
| Phase numbering remediation notice | Recorded here §4 | — |
| Retrospective Phase Guidance docs (849–943) | On-demand, tagged retrospective | — |

---

## 8. Coherence Verdict

`coherence_report_944_verdict=pass`

All CDL-081 artifacts coherent and consistent. SIM evidence anchored.
Phase numbering remediation recorded. Workflow standing instructions locked.
Window post-H-013 work complete. Capsule v5.32 to follow at Phase 945.
