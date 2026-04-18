# ILC Window 723-726 Guidance v0.1

**Prepared by:** Codex  
**Date:** 2026-04-18  
**For:** Codex  
**Capsule at open:** v4.8  
**Frontier at open:** Window 717-722 CLOSED; Window 723-726 is next planned continuation

---

## 1. Window purpose

Window 723-726 closes the question of **sequestered financial-shard eligibility**
without activating that lane.

This is not a financial-market launch window. It is the eligibility,
trigger, and separation window for answering when such a lane could honestly
open later, and what would have to be true first.

The central job is to keep three things out of limbo:

- whether the sequestered financial-shard idea remains a real post-launch
  candidate or should be explicitly dormant,
- what the minimum post-launch trigger conditions would be,
- how that candidate lane stays separate from both ordinary shard-lifecycle law
  and the private/gated access hardening lane.

Primary source anchors:
- `docs/specs/ilc_foundational_carry_forward_closure_program_701_plus_v0.1.md` §4.5
- `docs/research/ilc_option_d_to_option_b_transition_program_guide_2026_04_14_v0.1.md` §12
- `docs/specs/ilc_economic_architecture_comprehensive_v0.1.md` §4.3

---

## 2. In scope

- sequestered financial-shard **eligibility prefilter**
- post-launch **trigger matrix**
- contagion / firewall / auditability **prerequisite list**
- explicit separation from:
  - ordinary shard-lifecycle law,
  - private/gated shard rights and access hardening,
  - sovereign substrate / `CDL-062` work
- explicit written answer on whether any new CDL opening is needed now or
  deferred

This window is about **eligibility and deferment discipline**, not activation.

---

## 3. Hard constraints

- No financial-shard activation in this window
- No CDL ratification unless extraordinary evidence genuinely forces it
- No new CDL opening should be assumed by default
- `CDL-062` remains the sovereign-substrate research lane and must not be
  conflated with this financial-shard eligibility lane
- ADR-0022 private/gated shard rights/access hardening remains a separate lane
- ordinary shard-lifecycle law is not reopened here
- no runtime mutation in `ilc_core/` or `ilc_consensus/`
- no claim that post-launch trigger conditions are already satisfied before
  launch has happened
- do not cite “ADR-0018” as accepted live ADR text; treat it as a historical
  concept reference carried by later planning docs unless and until a real ADR
  artifact exists in `docs/adr/`

---

## 4. Required outputs

| Output | Form | Notes |
|---|---|---|
| Financial-shard eligibility prefilter | `docs/specs/ilc_sequestered_financial_shard_eligibility_prefilter_724_v0.1.md` | Must state what qualifies the lane even to be considered later |
| Post-launch trigger matrix | spec artifact | Must record minimum trigger, disqualifiers, and current verdict |
| Contagion / firewall prerequisites | spec artifact | Must keep `B_hft`, firewalling, and auditability explicit |
| Lane separation note | integrated into prefilter and trigger artifacts | Must separate from ordinary shard lifecycle, ADR-0022, and `CDL-062` |
| Coherence report | `docs/specs/ilc_coherence_report_726_v0.1.md` | Standard window closure artifact |
| Capsule v4.9 | `docs/specs/ilc_antigravity_context_capsule_v4.9.md` | Supersedes v4.8; records Track B line from `STATUS.md` tail |
| Closure gate | `docs/specs/ilc_window_723_726_closure_gate_726_v0.1.md` | Confirms no activation, no ratification, carry-forward explicit |

---

## 5. Suggested phase structure

| Phase | Purpose |
|---|---|
| 723 | Sequence lock — freeze the no-activation, no-conflation, post-launch-only posture |
| 724 | Eligibility prefilter — define candidate scope, exclusions, and lane separation |
| 725 | Trigger matrix + contagion/firewall prerequisites — define what would have to become true later |
| 726 | Coherence report, capsule v4.9, closure gate |

These phases are a suggested skeleton. Codex may restructure within the window
as long as every required output is produced and every hard constraint is
honored.

---

## 6. Inherited governing baselines

These are inherited settled law or active governing boundaries, not reopened
here:

- `CDL-047`: treasury governance framework
- `CDL-048`: mandatory ECU conversion discipline
- `CDL-066`: sender authorization ratified
- `CDL-067`: settlement-state governance vehicle ratified
- `CDL-062`: sovereign-substrate research lane open and separate
- ADR-0022: local-first private/public boundary remains separate
- ADR-0028: Option D active posture

Window 723-726 inherits Window 717-722’s explicit ADR-0015 closure and mixed
launch/defer disposition.

---

## 7. Key questions this window must answer honestly

1. Is the sequestered financial shard still a real later-lane candidate, or
   should it be recorded as explicitly dormant?
2. What minimum trigger conditions would justify later eligibility:
   public launch, observed demand, post-launch monitoring, or something
   stronger?
3. What contagion / firewall prerequisites are non-negotiable before a future
   lane could open?
4. How is this lane kept separate from ordinary shard lifecycle and from
   private/gated access hardening?
5. Does this window require a new CDL opening now, or is explicit deferment
   the honest answer?

Window 723-726 does not need to authorize the lane. It needs to make the
eligibility and deferment boundary explicit.

---

## 8. No pre-window conversation required

The carry-forward program does not impose a pre-window conversation gate here.
This guidance doc is sufficient to draft the packet and proceed after standard
review.

---

## 9. Track B line at window open

From `docs/phases/STATUS.md` tail (verified 2026-04-18):

> M-015 complete `f173c860`; next planned phase: M-016 (Workload D: Replayability and State Extraction)
