# ILC Window 717-722 Guidance v0.1

**Prepared by:** Claude Sonnet 4.6 (local reviewer)  
**Date:** 2026-04-17  
**For:** Codex  
**Capsule at open:** v4.7  
**Frontier at open:** Window 713-716 CLOSED; Window 717-722 is next planned continuation

---

## 1. Window purpose

Window 717-722 closes the **ADR-0015 family**: node transfer economics, commons
dedication, and leasehold calibration. This family has been structurally real but
ungoverned — the mechanisms are structurally related and should not be opened as
disconnected micro-decisions.

This is a research, simulation, and conversation-heavy window. It does not ratify
new CDLs unless honest evidence clearly requires it. Its job is to produce a
durable, explicit disposition for each member of the family — not to constitutionalize
economic metaphors because they are historically resonant.

**Primary source:** `docs/research/ilc_option_d_to_option_b_transition_program_guide_2026_04_14_v0.1.md`
§11 (`717-722` scope description).

---

## 2. In scope

- **Transfer tax**: governing structure, rate, and duration for node ownership transfers
- **Cooling period**: post-transfer lockout or restricted-participation window
- **Public-goods dedication / commons routing**: how a fraction of transfer
  proceeds routes to the commons pool
- **Leasehold / reversion timing**: when and how node ownership reverts,
  what triggers reversion, and what the reversion path looks like
- **ADR-0015 disposition**: the ADR-0015 family must receive an explicit
  accepted/amended/rejected/deferred disposition — it may not remain silently
  relied upon while still proposed

For each item, the required output is an **explicit decision** on whether it is:
- `launch_bound` — must be in place before public RC
- `post_launch_bound` — scheduled for a specific later window
- `deferred` — intentionally not settled in this window, with a written reason

---

## 3. Hard constraints

- No CDL ratification unless the evidence genuinely demands it — the 714
  law-vs-freedom classification pattern applies here: distinguish between
  governing principles and calibrated numeric parameters
- CDL-017 remains open and is **not** ratified in this window
- Row 5 and Row 7 remain `spec_closed_runtime_pending`; this window may
  **advance** their runtime-form evidence but does not claim closure
- No runtime mutation in `ilc_core/` or `ilc_consensus/`
- CDL-039 ratification does not occur here
- Do not silently adopt new topology or discovery authority

---

## 4. Required outputs

| Output | Form | Notes |
|---|---|---|
| ADR-0015 disposition note | `docs/specs/ilc_adr_0015_node_transfer_economics_disposition_717_v0.1.md` | Explicit accepted/amended/deferred verdict per mechanism |
| Simulation or replay contract | commissioned evidence pack (results in later window) | Transfer-tax, cooling-period, lease-duration — define the sim scenarios and pass criteria now; results may come later |
| Node-transfer economics governance package | spec or doctrine artifact | Covers transfer tax rate range, cooling period duration class, commons dedication fraction, reversion trigger taxonomy |
| Launch-bound vs deferred decision | recorded in closure gate | Explicit per-mechanism disposition required |
| Coherence report | `docs/specs/ilc_coherence_report_NNN_v0.1.md` | Standard window closure artifact |
| Capsule v4.8 | `docs/specs/ilc_antigravity_context_capsule_v4.8.md` | Supersedes v4.7; records Track B line from STATUS.md tail |
| Closure gate | `docs/specs/ilc_window_717_722_closure_gate_NNN_v0.1.md` | Confirms no unauthorized ratification, names carry-forward |

---

## 5. Suggested phase structure

| Phase | Purpose |
|---|---|
| 717 | Sequence lock — inherit 714 law-vs-freedom discipline; name the ADR-0015 mechanisms explicitly; state what counts as evidence for a launch-bound vs deferred verdict |
| 718 | ADR-0015 inventory and scoping — map each mechanism to its current status, historical artifacts, and governing constraints |
| 719 | Node transfer economics governance package — transfer tax structure, cooling period, leasehold/reversion taxonomy |
| 720 | Commons dedication mechanics — public-goods routing fraction, destination governance, interaction with CDL-047 treasury framework |
| 721 | Simulation/replay commissioning — define scenarios, pass criteria, and evidence format for the family; commission but do not claim results |
| 722 | Coherence report, capsule v4.8, closure gate |

These phases are a suggested skeleton. Codex may restructure within the window
as long as every required output is produced and every hard constraint is honored.

---

## 6. Inherited governing baselines

These are inherited settled law, not reopened here:

- CDL-047: Treasury ECU-governor framework
- CDL-048: mandatory ECU conversion deadline
- CDL-051: epoch-state and quorum-record contract
- CDL-059: aesthetic panel
- CDL-060: centrality-delta gossip with bounded fanout
- CDL-061: gossip HTTP envelope contract
- CDL-066: agent sender authorization ratified
- CDL-067: settlement-state governance vehicle ratified
- ADR-0028: Option D active posture

---

## 7. Key questions this window must answer honestly

1. Is the transfer tax `launch_bound` or `post_launch`? What evidence threshold
   justifies a launch-bound answer?
2. What cooling period duration class is appropriate — epochs, issuance cycles,
   or calendar time? Which is governed vs operator-configurable?
3. Is commons dedication a constitutional fraction or an operator-configured
   parameter? Does it interact with CDL-047 treasury routing?
4. What are the reversion triggers? Is reversion automatic, governance-triggered,
   or dispute-resolved? Does it interact with CDL-046 stake release?
5. Does the ADR-0015 family need new CDLs, or does `spec_or_contract_lock`
   with explicit non-ratification language satisfy the governance requirement?

Window 717-722 does not need to answer all of these at constitutional depth.
It needs to choose a completion mode for each and produce an honest artifact
that records the choice and its evidence basis.

---

## 8. No pre-window conversation required

§5.3 of the carry-forward program carries no pre-window conversation gate for
717-722. This guidance doc is sufficient for Codex to draft the packet and
proceed after standard review.

---

## 9. Track B line at window open

From `docs/phases/STATUS.md` tail (verified 2026-04-18):

> M-014 complete `34e492a5`; next planned phase: TBD
