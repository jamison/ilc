# ILC Foundational Carry-Forward Closure Program 701+ v0.1

Status: planning carry-forward artifact
Date: 2026-04-15
Classification: non-checklist closure program
Primary program anchor: `docs/research/ilc_option_d_to_option_b_transition_program_guide_2026_04_14_v0.1.md`

## 1. Purpose and boundary

This artifact exists to prevent historically important ILC ideas from falling
into a permanent gray zone after the `Option D -> Option B` checklist closes.

The repo now has a visible split between:
- concepts that are already constitutional law,
- concepts that are architecturally real but not yet ratified,
- concepts that are partially scaffolded but not fully operationalized,
- and concepts that should remain explanatory doctrine rather than be forced
  into CDL text.

This program is the explicit closure lane for the second and third groups.

It does **not** silently promote these items into current checklist blockers.
Unless a later lane explicitly elevates one of them, this program remains
post-`700` carry-forward work rather than a hidden requirement for `CDL-062`
opening or row-`5`/row-`7`/row-`8` closure.

## 2. Authority and source order

For every item in this program, authority order is:
1. ratified CDL / ADR and live runtime contracts
2. current economic / architecture / checklist specs
3. historical recovery and session-historization artifacts
4. `Z_Past_Chats` foundational literature
5. only then new doctrinal synthesis

Primary source anchors:
- `docs/specs/ilc_economic_architecture_comprehensive_v0.1.md`
- `docs/whitepaper/ilc_whitepaper_working_draft_v6_0.md`
- `docs/research/ilc_foundational_principles_and_window_687_692_context_2026_04_15_v0.1.md`
- `docs/research/ilc_historical_formula_and_mechanism_catalog_v0.1.md`
- `Z_Past_Chats/2026_03_05_Opus_Conversation_Werner_Political_Economy_Phase358_Review.md`
- `Z_Past_Chats/2026_03_22_ILC - Inverted ECU Model Design and Phase 453-459 Hardening.md`
- `Z_Past_Chats/2025_12_01_ILC - Q&A regarding Local Influence and other future governance nodes being on-graph and ajustable.txt`

## 3. Completion modes

Not every item should end as a CDL.

Allowed completion modes in this program are:
1. `constitutional_lock`
   Meaning: the item changes protocol rights, obligations, runtime semantics,
   or durable governance constraints and therefore warrants CDL/ADR treatment.
2. `spec_or_contract_lock`
   Meaning: the item needs a stable engineering contract or namespace/governance
   specification, but not necessarily constitutional law.
3. `doctrine_lock`
   Meaning: the item should be preserved as explanatory whitepaper/economic
   doctrine, with explicit text saying it is interpretive rather than binding.
4. `explicit_non_ratification`
   Meaning: the item is intentionally preserved as historical context,
   inspiration, or implementation freedom, but is not to be presented as
   settled protocol law.

Success for this program is not “ratify everything.”
Success is “every important under-locked item has a deliberate, auditable final
disposition.”

### 3.1 Disposition authority and elevation gates

Default disposition authority:
- sequence-lock artifact for the owning window proposes the intended completion
  mode,
- the companion conversation/research frame states the evidence standard,
- the handoff or closure artifact records the final disposition,
- only a later explicit CDL/ADR lane may upgrade an item into
  `constitutional_lock`.

Default elevation gates:
- `doctrine_lock` requires source traceability plus explicit “not binding law”
  language,
- `spec_or_contract_lock` requires a stable artifact with scope boundary,
  non-goals, and at least one worked example or conformance hook,
- `constitutional_lock` requires an opening stub, prelock evidence, and
  explicit justification that the item changes durable protocol/governance
  rights or obligations,
- `explicit_non_ratification` requires a drop/defer note stating why the item is
  being preserved as history or implementation freedom rather than law.

## 4. Item register and routing

### 4.1 Economic doctrine and kernel-calibration items

| Item | Current status | Recommended completion mode | Earliest honest start | Suggested artifacts |
|---|---|---|---|---|
| `W_e = ΔH / E_cost` | real economic background, not ratified | `doctrine_lock` unless later evidence requires stronger law | after `693-700`, or in parallel with long-tail economics review | `docs/research/ilc_w_e_traceability_and_kernel_mapping_note_v0.1.md` |
| BAL-profile weights for the four-component ECU kernel | components are canon; exact weights are not settled | `spec_or_contract_lock` first, with optional later `constitutional_lock` only if evidence justifies | after replay/live calibration evidence is available | `docs/specs/ilc_ecu_kernel_profile_calibration_note_v0.1.md` |
| “ILC is post-banking” framing | real explanatory frame, not governance text | `doctrine_lock` | any time after `693-700` | `docs/research/ilc_post_banking_economic_doctrine_note_v0.1.md` |
| Inverted ECU model | historically important, partially echoed by decay and forced circulation | `spec_or_contract_lock` for explicit runtime traceability, plus doctrine preservation | after `693-700`, ideally beside economic monitoring review | `docs/research/ilc_inverted_ecu_model_runtime_traceability_note_v0.1.md` |

#### Completion rule for this block

This block closes when:
- every item above has a declared disposition,
- every runtime-relevant implication is mapped to existing canonical mechanics,
- and any candidate for later ratification has a replay/sim/live-evidence path
  instead of remaining as hand-wavy background.

Special requirement for the inverted-ECU item:
- the closure artifact must say explicitly whether and how current ratified
  mechanisms such as `CDL-V1` temporal decay and `CDL-048` mandatory
  conversion are being treated as operational implementation of the inverted
  circulation model.

This block should **not** constitutionalize economic metaphors just because they
are historically resonant.

### 4.2 Governance-minimization and graph-native governance items

| Item | Current status | Recommended completion mode | Earliest honest start | Suggested artifacts |
|---|---|---|---|---|
| “Governance as a bug” | real design principle, partially incorporated | `spec_or_contract_lock` for sunset taxonomy and human-lever classification; optional later ADR/CDL where necessary | start as soon as bootstrap/founder-era lever inventory is stable enough to classify honestly; do not wait for final sovereign-substrate choice | `docs/specs/ilc_governance_minimization_and_sunset_taxonomy_v0.1.md` |
| Scoring algorithms as first-class on-graph governance objects | scaffolded historically, not fully realized | `spec_or_contract_lock` first | after `693-700`; may overlap with post-`700` graph-native governance work | `docs/specs/ilc_algorithm_governance_and_namespace_contract_v0.1.md` |
| Local-influence / scoring-family worked example | toy/proto implementation exists historically | `spec_or_contract_lock` | after the algorithm-governance contract exists | `docs/research/ilc_local_influence_algorithm_family_and_selection_note_v0.1.md` |

Early-start sublane inside this block:
- `CDL-017` bootstrap transition criteria and Genesis sunset triggers should be
  treated as an earlier-start governance-hardening item, because its subject is
  protocol/bootstrap governance rather than later sovereign-substrate choice.
- The governance-minimization block should therefore allow a pre-`707`
  initiation path for `CDL-017` evidence hardening and opening work if the
  bootstrap/runbook material is mature enough.

#### Completion rule for this block

This block closes when:
- the repo has a durable inventory of human levers, override classes, and
  sunset expectations,
- algorithm-governance surfaces are no longer implicit or “sacred”
  implementation details,
- and the project can say clearly which governance claims are philosophy and
  which are actual runtime/governance law.

### 4.3 Adaptive resilience and transport-doctrine items

| Item | Current status | Recommended completion mode | Earliest honest start | Suggested artifacts |
|---|---|---|---|---|
| Levin-inspired adaptive gossip | real design influence; not cleanly formalized law | `spec_or_contract_lock` | after row-`9` maturity closure and after sovereign-substrate path stabilizes | `docs/specs/ilc_adaptive_gossip_and_partition_repair_contract_v0.1.md` |
| Active repair/reselection under missing-signal conditions | partially implied by resilience discussions | `spec_or_contract_lock` | with the adaptive-gossip contract | `docs/research/ilc_missing_signal_adaptive_repair_benchmark_plan_v0.1.md` |
| Economic coupling between connectivity and usefulness | historical idea, not explicit runtime law | `explicit_non_ratification` or later `doctrine_lock` unless a real runtime dependency emerges | after adaptive-gossip benchmarking | fold into the benchmark plan or a later doctrine note |

#### Completion rule for this block

This block closes when:
- the repo has an explicit answer on what adaptive behavior the protocol
  requires versus what remains implementation freedom,
- resilience claims are benchmarked rather than metaphorical,
- and the Levin influence is either operationalized or explicitly retained only
  as background inspiration.

## 5. Suggested window routing

### 5.1 `701-706` — Foundational Economic Doctrine and Kernel Calibration

Primary closure targets:
- `W_e = ΔH / E_cost`
- BAL-profile weight disposition
- post-banking doctrine lock
- inverted-ECU runtime traceability

Recommended outputs:
- doctrine/law classification table
- kernel traceability note
- calibration/replay plan for any profile candidate
- whitepaper/economic-architecture amendment packet

Nearer-term non-blocking requirement for `687-692`:
- if sovereign-substrate benchmarking or comparison work uses BAL-profile kernel
  weights as planning inputs, the lane must say so explicitly and must label
  those weights as unratified planning assumptions pending the `701-706`
  calibration/disposition lane.

### 5.2 `707-712` — Governance Minimization and Graph-Native Algorithm Governance

Primary closure targets:
- governance-minimization inventory
- human-lever sunset taxonomy
- algorithm-governance namespace and selection contract
- local-influence family worked example

Recommended outputs:
- governance taxonomy artifact
- graph-native algorithm contract
- worked example and non-goal boundary note

Allowed early-start carry-forward before `707`:
- `CDL-017` bootstrap transition criteria / Genesis sunset triggers
- bootstrap-lever inventory and observable-trigger hardening
- explicit split between founder-rent sunset and steward/infrastructure
  incentive continuity where required

### 5.3 `713-716` — Adaptive Gossip and Resilience Operationalization

Primary closure targets:
- adaptive-gossip contract
- partition-repair benchmark pack
- missing-signal doctrine disposition

Recommended outputs:
- transport resilience contract
- benchmark pack
- explicit law-vs-freedom decision memo

## 6. Integration rules for current planning

To prevent these items from being forgotten before `701+`, the repo should
carry three explicit rules now:
1. every sequence-lock or handoff that touches these topics must either point to
   this program or explicitly say the item is out of scope for the current lane,
2. `TODO.txt` must retain a dedicated carry-forward block with concrete trigger
   conditions and suggested artifact paths,
3. doctrinal restoration memos may not be cited as if they themselves
   constitutionalize the claim.

## 7. Non-goals

This program does **not** do the following:
- reopen rows `5-9`,
- silently block `CDL-062`,
- force every historical idea into a CDL,
- or treat metaphysical language as sufficient for runtime/governance law.

## 8. Bottom line

The project now has enough historical recovery to know which ideas matter.
What it lacks is a durable closure route for ideas that sit between “real” and
“ratified.”

This artifact is that route.
