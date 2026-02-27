# ILC Cmax Symbolic Origin and Numeric Binding Gap 274 fix2 v0.1

Status: Non-ratified provenance and gap-closure memo
Date: 2026-02-23
Owner lane: G8 Constitution Cluster A

## 1. Purpose

Document the recovered historical origin for the 25,920,000 supply symbol and
record the current canon gap: `CDL-026` is ratified as cap type (`explicit finite cap`)
but does not yet bind a numeric `C_max` value in constitutional canon.

This memo is input evidence for:
- a non-sensitive numeric candidate prelock lane, and
- a sensitive numeric binding ratification lane.

## 2. Recovered historical origin (primary evidence)

Recovered source chain:

1. `Z_Past_Chats/2025_06_03_ILC - Higher Dimensional Geometry in DS.txt:3396`
   - introduces `25,920,000` as Platonic/precessional-cycle candidate.
2. `Z_Past_Chats/2025_06_03_ILC - Higher Dimensional Geometry in DS.txt:3408`
   - marks `25,920,000 ILC` as recommended in that design discussion.
3. `Z_Past_Chats/2025_06_03_ILC - Higher Dimensional Geometry in DS.txt:3446`
   - founder-side acceptance of `25.92 million` with low-profile symbolism intent.
4. `Z_Past_Chats/2025_06_05_ILC - Whitepaper Section 2 Draft.txt:5721`
   - carries the same 25.92M framing into token-model draft language.
5. `Z_Past_Chats/2025_06_18_ILC - 4D Cognitive AI Model.txt:7004`
   - uses 25.92M baseline for Genesis 5-6% target arithmetic.

Interpretation:
- historical origin is clear and consistent: symbolic/cosmological branding anchor.
- the origin is not itself constitutional ratification; it is design lineage evidence.

## 3. Divergent later proposals in historical corpus

Later discussions include alternate numeric cap recommendations:

- `Z_Past_Chats/2025_11_12_ILC - ILC latest main thread Oct25.txt:4686`
  (`1,000,000,000` as a suggested round figure),
- `Z_Past_Chats/2025_11_12_ILC - ILC latest main thread Oct25.txt:20840`
  (`100,000,000` as a recommended hard cap in that thread).

These are historical alternatives and do not supersede constitutional ratification.

## 4. Current canonical state (gap statement)

Current ratified state:
- `docs/specs/ilc_constitutional_decision_log_v0.1.md:51`
  - `CDL-026` is ratified.
  - selected option class: `explicit finite cap`.

Current gap:
- `docs/specs/ilc_cdl_026_cmax_lock_ratification_evidence_273_v0.1.md:31`
  records a "selected finite `C_max` lock candidate" but does not bind a numeric value.

Result:
- cap type is ratified,
- numeric `C_max` constant remains unbound in constitutional canon.

## 5. Working decision candidate for numeric binding lanes

Candidate to carry into prelock + ratification lanes:
- `C_max_candidate = 25,920,000 ILC`

Rationale for candidate admission:
- strongest recovered lineage continuity across June 2025 design artifacts,
- coherent with existing Genesis 5% target language,
- preserves intended symbolic anchor while still requiring formal constitutional binding.

## 6. Genesis accrual objective carried forward

Objective (policy target, not runtime change in this memo):
- Genesis cumulative accrual cap across Genesis wallet(s):
  `G_max = 0.05 * C_max = 0.05 * 25,920,000 = 1,296,000 ILC`.
- Genesis accrual should be front-loaded in early epochs and taper sooner rather than later,
  with no accrual beyond `1,296,000 ILC` under the canonical hard-cap frame.

This memo does not set the governor function. It only locks objective framing for the
next simulation/evidence lane.

## 7. Required follow-on lanes

1. Non-sensitive evidence lane:
   - bind numeric candidate from recovered lineage,
   - run deterministic scenario sweeps for early-epoch front-loading and taper timing,
   - publish candidate lock artifact and rejection set for alternatives.

2. Sensitive ratification lane:
   - constitutionally bind the numeric `C_max` value,
   - keep mutation scope constrained to ratification protocol fields,
   - preserve dependency continuity with `CDL-025`, `CDL-026`, and downstream `CDL-027`/`CDL-030`.

## 8. Non-goals

This memo does not:
- mutate decision-log rows,
- ratify any CDL,
- change `ilc_core/` runtime behavior,
- alter fee-burn split candidate selection work in `CDL-028` lanes.
