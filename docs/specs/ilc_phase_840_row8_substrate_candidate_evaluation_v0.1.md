# ILC Phase 840 — Row 8 Substrate Candidate Evaluation v0.1

**Phase:** 840
**Date:** 2026-04-26
**Window:** 839–843

`row8_substrate_candidate_evaluation_840_complete`
`row8_candidate_named_and_classified`
`row8_candidate_passes_exclusion_matrix`
`row8_candidate_evaluation_blocker_discharged`

## 1. Purpose

Phase 840 names a specific sovereign substrate candidate and evaluates it
against the Phase 673 exclusion matrix and Phase 675 independence lock. This
is the sole remaining blocker for Option B gate re-synthesis.

This artifact does **not** select a substrate. It evaluates admissibility.

## 2. Governing criteria

### 2.1 Phase 673 exclusion rules (disqualifying)

| Rule | Disqualifies if... |
|------|--------------------|
| E1 | Protocol legitimacy can be overridden or nullified by an outside governance body |
| E2 | Admission or namespace authority can be created outside protocol lineage |
| E3 | Public settlement legitimacy can be declared without protocol receipt basis |
| E4 | Public reputation continuity depends on outside operator or vendor approval |
| E5 | The only practical audit or exit path runs through one hosted control plane |
| E6 | Migration requires privileged consent from the original operator or provider |

### 2.2 Phase 675 locked independence rule

Later substrate families may not make protocol legitimacy subordinate to an
outside veto authority. Outside systems may carry already-legitimate protocol
state but may not become the constitutional center that authors legitimacy.

### 2.3 ADR-0028 graduated requirements (hard-closure rows)

- Row 7 proof obligations satisfied: ✅ (`runtime_closed`)
- Row 8 exclusion-matrix evaluation against a specific candidate: **this phase**
- CDL-017 ratification: ✅ (Phase 765)

## 3. Candidate named

**Candidate:** ILC Native Minimal L1 — a purpose-built, protocol-owned BFT
settlement chain operated exclusively by ILC validators, governed by the
existing CDL constitutional framework, with ILC as the canonical currency and
the ILC Genesis record as the legitimacy root.

**Character:** Sovereign minimal L1. The ILC validator network (already present
as Mysticeti BFT consensus, Phase 830 settlement-path gate) is extended from a
testnet into a public settlement chain. No external chain, rollup, or third-party
sequencer is involved. The validator set is governed by CDL-017. The canonical
legitimacy root is the ILC Genesis record.

**Classification under Phase 673 §4 matrix:**
"sovereign minimal L1 / BFT network where protocol legitimacy stays upstream
and exit is credible" → **presumptively admissible**.

## 4. Exclusion matrix evaluation

### E1 — Outside governance override

**Evaluation:** No outside governance body has authority over ILC protocol
legitimacy. CDL constitutional amendments require on-chain validator quorum
plus the CDL ratification process. No external party holds veto.

**Verdict:** ✅ Not disqualified.

### E2 — Admission or namespace outside protocol lineage

**Evaluation:** Agent admission is governed by CDL-042 (flat namespace,
key-derived agent_id) and CDL-017 (validator admission). Both are CDL-governed.
No admission or namespace authority exists outside ILC protocol lineage.

**Verdict:** ✅ Not disqualified.

### E3 — Settlement legitimacy without protocol receipt

**Evaluation:** Settlement legitimacy is grounded in the epoch settlement record
and the Mysticeti BFT consensus commit. No external chain or sequencer declares
settlement legitimacy independently. ECU transfers are valid only if they carry
a protocol receipt basis (CDL-054 validator reward routing, CDL-050 treasury
governor lane).

**Verdict:** ✅ Not disqualified.

### E4 — Reputation continuity depends on outside approval

**Evaluation:** CDL-V1 temporal decay and CDL-V2 sybil resistance govern
reputation. The CDL-V chain is ILC-internal. No outside operator approval is
required to preserve or contest reputation continuity.

**Verdict:** ✅ Not disqualified.

### E5 — Only audit/exit path through one hosted control plane

**Evaluation:** The M-022 strong-exitability drill demonstrated: state can be
exported, independently verified, replayed on a fresh node, and migrated without
any original-operator API call (`operator_api_calls: 0`). Row 7 exitability
is `runtime_closed`. Multiple validator operators exist (CDL-017 governs admission
of independent validators). No single hosted control plane is the only exit path.

**Verdict:** ✅ Not disqualified.

### E6 — Migration requires privileged operator consent

**Evaluation:** Migration requires no privileged consent from any original
operator or provider. The M-022 drill is the runtime evidence. The Phase 675
lock names this as a carry-forward obligation that the candidate satisfies.

**Verdict:** ✅ Not disqualified.

## 5. Phase 675 independence rule evaluation

The ILC Native Minimal L1 candidate does not make protocol legitimacy
subordinate to any outside veto authority. The ILC Genesis record is the
legitimacy root. Validator admission is CDL-governed. Settlement requires
protocol receipt basis. No outside system can author legitimacy — outside
infrastructure (hosting, connectivity) may carry already-legitimate state but
is downstream of protocol truth.

**Verdict:** ✅ Independence rule satisfied.

## 6. Risky-but-admissible considerations

The candidate is **presumptively admissible**, not merely risky. The risky
considerations that apply to downstream settlement layers (E3, E4) are fully
mitigated by the CDL-governed receipt basis and the CDL-V reputation chain.

The one ongoing legitimacy risk is validator centralization — a small initial
validator set risks de facto founder sovereignty. This is mitigated by:

- CDL-017 governing independent validator admission (ratified),
- the Phase 812 ADR-0028 graduation clause requiring honest acknowledgement of
  any open parallel obligations,
- Row 5 privacy as an explicit parallel-obligation carry-forward.

This risk does not disqualify the candidate. It is a named carry-forward
obligation for the post-graduation operational posture.

## 7. Row 8 evaluation verdict

| Check | Result |
|-------|--------|
| Candidate named | ✅ ILC Native Minimal L1 |
| Phase 673 matrix classification | ✅ Presumptively admissible |
| All 6 exclusion rules evaluated | ✅ None triggered |
| Phase 675 independence lock | ✅ Satisfied |
| ADR-0028 Row 8 hard-closure requirement | ✅ Discharged |

**Row 8 evaluation verdict:**
`row8_candidate_named_and_classified`
`row8_candidate_passes_exclusion_matrix`
`row8_candidate_evaluation_blocker_discharged`

The Row 8 substrate candidate evaluation obligation is discharged. The
ILC Native Minimal L1 candidate is presumptively admissible under the Phase 673
and Phase 675 criteria.

This evaluation does **not** select a substrate. Option B gate re-synthesis
occurs in Phase 841.
