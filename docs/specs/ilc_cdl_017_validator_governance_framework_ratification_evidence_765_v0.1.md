# ILC CDL-017 Validator Governance Framework Ratification Evidence 765 v0.1

Status: ratification evidence artifact
Date: 2026-04-21
Decision vehicle: CDL-017
Phase: 765
Owner lane: G8 later CDL-017 ratification lane
Document schema: `docs/specs/README.md#sequence-locks-phase-window-guidance-and-phase-artifacts`

`cdl_017_ratification_evidence_765_complete`
`cdl_017_ratified_validator_governance_framework_lane`
`phase_764_carry_forward_verdicts_reread_verbatim_in_phase_765`
`cdl_068_adjacent_lane_reaffirmed_unchanged_in_phase_765`
`sec_004_post_ratification_scope_reread_with_named_acceptance_test`
`ratification_opens_validator_governance_lane_only_in_phase_765`
`first_non_genesis_validator_deployment_human_gate_preserved_after_cdl_017_ratification`
`m007_hooks_remain_unimplemented_after_cdl_017_ratification`
`phase_765_commit_1_does_not_mutate_decision_log`
`phase_765_commit_2_mutates_only_cdl_017_row`

## 1. Phase 764 carry-forward verdicts re-read verbatim

This ratification phase re-reads the exact interaction verdicts from
`docs/specs/ilc_cdl_017_interaction_synthesis_and_activation_boundary_record_764_v0.1.md`
rather than paraphrasing them.

### 1.1 CDL-055 exact carry-forward statement

Verbatim from Phase `764` Section `2`:

> `CDL-017` does not alter validator participation stake, liveness penalties,
> equivocation slash boundary, or the separate re-admission boundary. These
> remain governed by ratified `CDL-055`.

Phase `765` ratification preserves that verdict unchanged.

### 1.2 CDL-056 exact carry-forward statement

Verbatim from Phase `764` Section `2`:

> `CDL-017` does not alter the non-inheritable trust-tier flag, its
> liveness-threshold tie to `CDL-055`, or the bounded consensus-dispute
> tiebreaker. These remain governed by ratified `CDL-056`.

Phase `765` ratification preserves that verdict unchanged.

### 1.3 CDL-068 adjacent-lane exact statement

Verbatim from Phase `764` Section `2`:

> `CDL-068` continues to govern topology-shuffle authorization, diversity
> thresholds, and randomness-source boundary. `CDL-017` consumes this as an
> adjacent constitutional neighbor rather than amending it.

Phase `765` ratification preserves `CDL-068` as adjacent and unchanged.

## 2. SEC-004 post-ratification implementation scope re-read

Phase `765` also re-reads the exact SEC-004 boundary from Phase `764`
Section `2`:

> `SEC-004` remains an implementation obligation that begins only after
> `CDL-017` ratifies. `TransferCertificate` epoch binding and historical
> validator-set resolution are not solved by this phase or by ratification
> rhetoric alone.

The inherited Phase `763` and Phase `755` acceptance condition remains fixed:

- `TransferCertificate` must gain `epoch: EpochSeq`,
- certificate verification must resolve the historically active
  `ValidatorSet` for that epoch,
- the named acceptance test is
  `test_ejected_validator_sig_rejected_after_epoch_boundary`.

SEC-004 is therefore post-ratification implementation work, not a claim of
already-complete activation safety.

## 3. Ratified constitutional decision

`CDL-017` is ratified as the constitutional validator-governance framework
covering:

- validator admission and ejection as governed protocol actions,
- bootstrap transition criteria,
- Genesis-sunset trigger design as it applies to validator authority,
- the dynamic validator-set activation boundary.

The ratified constitutional meaning remains narrow and explicit:

- Genesis-only validator authority remains operative for the near-term testnet
  at ratification time,
- ratification opens the validator-governance lane in constitutional law,
- ratification does not itself deploy a non-Genesis validator,
- ratification does not itself activate dynamic validator-set hooks.

Verbatim from Phase `764` Section `3.2`:

> This is the constitutional opening of the validator-governance lane only.

## 4. Preserved activation boundary at ratification

The activation-boundary record synthesized in Phase `764` remains operative at
ratification time.

### 4.1 State at ratification

The inherited state remains:

- Genesis-only validator authority is still operative,
- no non-Genesis validator has been admitted by constitutional act alone,
- `admit_validator` is still `unimplemented!`,
- `eject_validator` is still `unimplemented!`,
- `SEC-004` is still not implemented.

### 4.2 What ratification changes

Ratification changes constitutional authority only:

- validator admission and ejection now sit on a ratified constitutional lane,
- bootstrap-transition and Genesis-sunset governance law now have a ratified
  home,
- later activation work may proceed on a ratified constitutional basis.

### 4.3 What ratification does not change automatically

Verbatim from Phase `764` Section `3.3`, ratification does **not**
automatically do any of the following:

- activate the M-007 `admit_validator` / `eject_validator` hooks,
- implement `SEC-004`,
- authorize the first non-Genesis validator deployment without a later human
  gate,
- rewrite `CDL-055`,
- rewrite `CDL-056`,
- rewrite `CDL-068`.

The first non-Genesis validator therefore remains a later operator decision
after ratification and after the required post-ratification activation work is
ready.

## 5. Preserved non-conflation obligations

The seven non-conflation obligations from the Phase `763` sequence lock remain
binding at ratification time:

1. `CDL-017` ratification is not runtime hook activation.
2. `CDL-017` ratification is not first non-Genesis validator deployment.
3. SEC-004 activation scope is not proof that SEC-004 is already implemented.
4. `CDL-017` activation law is not silent supersession of `CDL-055`.
5. `CDL-017` activation law is not silent supersession of `CDL-056`.
6. row `7` runtime closure is inherited evidence, not a new ratification
   claim.
7. row `5` honest fail record remains true and is not erased by validator-law
   ratification.

## 6. Two-commit mutation discipline and decision-log consequence

This phase uses the dedicated two-commit constitutional mutation pattern
required by the Phase `763` sequence lock.

Commit `1` touches exactly these five paths:

- `docs/specs/ilc_cdl_017_validator_governance_framework_ratification_evidence_765_v0.1.md`
- `tests/test_phase_765_cdl_017_ratification_evidence.py`
- `docs/phases/phase_765_g8_cdl_017_ratification_walkthrough.md`
- `docs/phases/STATUS.md`
- `docs/PLANNING_INDEX.md`

Commit `1` does **not** mutate
`docs/specs/ilc_constitutional_decision_log_v0.1.md`.

Commit `2` mutates exactly one row in
`docs/specs/ilc_constitutional_decision_log_v0.1.md`:

- `CDL-017`

Commit `2` changes exactly:

- `status: open` -> `status: ratified`
- appends `ratified_phase: 765`
- appends `ratified_date: 2026-04-21`
- appends
  `evidence_document: docs/specs/ilc_cdl_017_validator_governance_framework_ratification_evidence_765_v0.1.md`

No other file may change in commit `2`. No other CDL row may change in commit
`2`.

## 7. Preserved exclusions and non-goals

This ratification does not:

- activate `admit_validator`,
- activate `eject_validator`,
- claim SEC-004 is already implemented,
- authorize the first non-Genesis validator automatically,
- amend `CDL-055`,
- amend `CDL-056`,
- amend `CDL-068`,
- mutate `ilc_core/` or `ilc_consensus/`,
- erase the row `5` honest-fail record,
- reopen row `7`,
- evaluate a row `8` substrate candidate,
- claim Option B graduation.
