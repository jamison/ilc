# ILC Human Decision Log — 2026-04-26 v0.1

**Date:** 2026-04-26
**Context:** Post-HIGH-002 Phase B closure. All current operator-gated items surfaced,
reviewed, and decided. Six decisions recorded.

`human_decision_log_2026_04_26_published`
`option_b_selection_confirmed_operative_phase_814`
`first_validator_gate_pull_authorized_pending_provisioning`
`b_impl_authorized_after_first_validator_gate`
`cdl_070_deferred`
`cdl_071_deferred_higher_priority_than_cdl_070`
`capsule_v5_19_patch_authorized`

---

## D1 — Option B Selection: Phase 814 Record is Operative

**Question posed:** Phase 814 (2026-04-23) recorded `option_b_selected_by_human_authorization_2026_04_23`
and `adr_0028_posture=option_b`. Phase 841 (2026-04-26) re-synthesized the gate
and framed it as `option_b_selectable_not_selected`, which was carried into capsule
v5.18. Which record is authoritative?

**Human decision:** Phase 814 is the correct and operative record. Option B was
explicitly authorized by the human operator on 2026-04-23. That selection stands.

**Investigation finding:** Phase 823-829 sequence lock (2026-04-24) correctly
carried `option_b_selected_adr_0028_posture_confirmed` forward after Phase 814.
Phase 841 was scoped as a gate re-synthesis only and was written in a separate
conversation lane that did not see Phase 814's selection token. No material
downstream harm: no code, CDL, or gate decisions in Window 839-843 were
conditioned on Option B selection status. The error was confined to the capsule
v5.18 framing.

**Correction:** Capsule v5.19 restores `adr_0028_posture=option_b` and records
the Phase 841 gate=go as corroborating confirmation, not a new selectability gate.

`adr_0028_posture=option_b`
`option_b_selection_reconfirmed_2026_04_26`
`phase_841_framing_error_corrected_in_capsule_v5_19`

---

## D2 — First-Validator Human Gate (Phase 826 §6)

**Question posed:** All code-verifiable Phase 826 entry conditions are satisfied.
HIGH-002 is now closed. Is the operator ready to pull the first-validator human gate?

**Human decision:** Yes — authorize pull (Option A). However, key provisioning
requires a joint planning session. Specific inputs needed:

- Validator keys and recovery keys must be generated (analogous to genesis key
  ceremony for M-007); operator and reviewer to do this together.
- Three VPSes are currently available. Machine count and assignment (how many VPSes
  are needed for the non-Genesis validators, whether existing VPSes are used or new
  ones provisioned) to be determined in the provisioning session.
- Deployment and rollback runbook references must be confirmed before the gate form
  is signed.

**Next action:** Joint key-provisioning and gate-pull planning session. When
complete, Phase 826 §6 form is drafted by the reviewer and signed by the operator.

`first_validator_gate_pull_authorized_pending_provisioning_session`

---

## D3 — Rust Privacy Lane Integration Gate → B-Impl → SIM-LEAKAGE-03

**Question posed:** The Row 5 B-Impl implementation window (6 Rust obligations
in `node.rs`, `k=30`/`k=20` rolling group, jitter, bounded_hold) is commissioned
and ready. When is the human integration gate authorized?

**Human decision:** Authorized after the first-validator gate is pulled (Decision D2).
Sequencing: gate pull first (lower implementation cost), then open B-Impl window.

`b_impl_authorized_after_first_validator_gate_pull`
`sim_leakage_03_authorized_after_b_impl_complete`

---

## D4 — CDL-070: PQ Migration Ceremony

**Question posed:** CDL-070 covers the D1 recovery spec wire format mismatch
between Rust `pq_keygen` and Python `encode_recovery_spec`. Open now or defer?

**Human decision:** Defer. Revisit at each phase window closure. No current
implementation or gate work is blocked on CDL-070. Will be taken up when
PQ migration has concrete implementation urgency or when 1–2+ more phase windows
have completed.

`cdl_070_deferred_no_blocking_dependency`

---

## D5 — CDL-071: Temporal Tier Reconciliation

**Question posed:** CDL-071 covers temporal tier reconciliation across the protocol.
Open now or defer?

**Human decision:** Defer. Revisit at each phase window closure. CDL-071 is
considered higher user priority than CDL-070 when CDL work is taken up. Will
be opened before CDL-070 if both become active in the same window.

`cdl_071_deferred_higher_priority_than_cdl_070_when_taken_up`

---

## D6 — Capsule v5.19 Patch

**Question posed:** Capsule v5.18 is stale on two points: HIGH-002 still described
as planned (now closed), and Option B framing incorrect (D1 above). Patch now
or bundle into next window coherence phase?

**Human decision:** Patch now. Capsule v5.19 written in this session.

`capsule_v5_19_authorized_and_published`

---

## Summary

| Decision | Outcome | Next action |
|----------|---------|-------------|
| D1 — Option B posture | Phase 814 operative; `adr_0028_posture=option_b` restored | Capsule v5.19 published |
| D2 — First-validator gate | Authorized; requires provisioning session | Schedule joint key-gen session |
| D3 — B-Impl / SIM-LEAKAGE-03 | Authorized after D2 gate pull | Wait for D2 |
| D4 — CDL-070 | Deferred | Revisit each window closure |
| D5 — CDL-071 | Deferred (higher priority than CDL-070) | Revisit each window closure |
| D6 — Capsule patch | Done — v5.19 published | — |
