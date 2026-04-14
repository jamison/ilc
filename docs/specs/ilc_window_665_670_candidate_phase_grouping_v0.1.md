# ILC Window 665-670: Candidate Phase Grouping

**Author:** Codex
**Date:** 2026-04-14
**Baseline:** Window 659-664 CLOSED. Capsule v4.0 is current. Rows 1-4 remain `runtime_closed`; row 5 remains `not_started`; row 6 is `closed`; rows 7-9 remain open-state checklist items, with row 9 still `partial`. The next planned target is row-9 transport and discovery operational maturity.
**Planning note:** This is a candidate grouping, not a locked sequence. Phases 665-670 are the hard minimum lane and there are no conditional tail slots. The window closes row 9 if and only if the maturity contract is met, the closure-grade evidence exists, and the closure gate passes. The lane is allowed to close honestly with row 9 still `partial` if the evidence does not justify closure.

## 1. Window identity and scope

Window 665-670 is the first major operational-maturity lane after the row-6
governance closure. Its purpose is to attack checklist row 9 directly under the
transport posture already locked by ADR-0025 and Window 555-564:

1. define what “mature enough” means for bounded public-participant transport
   and discovery use;
2. build and run the actual multi-machine and VPN-backed canary machinery; and
3. either close row 9 honestly or publish an honest partial-state carry-forward
   with reusable evidence and tooling for later lanes.

This window is not a dynamic-discovery lane. It is not an anonymity-network
lane. It is not a substrate-selection lane. It is an operationalization and
maturity-evidence lane for the current authorized transport posture.

Tail-slot policy statement:
- no conditional tail slots are authorized in this window
- every phase from 665 through 670 is firm
- the lane must distinguish `closure tier` evidence from `stretch tier`
  evidence rather than quietly smuggling long-tail goals into closure criteria

## 2. Baseline and inheritance

Inherited canon and carry-forward:
- ADR-0025 already accepted HTTP/3 over QUIC as the preferred D2d gossip
  binding with HTTP/2 fallback
- CDL-061 already ratified the gossip HTTP envelope contract
- Window 555-564 already completed the transport adapter and static peer
  registry v1
- curated bootstrap and explicit promotion already exist as the RC/testbed
  posture
- Window 659-664 already sharpened row-9 evidence families and explicitly
  deferred exact thresholds into this window
- the current machine-legible checklist artifact is
  `docs/specs/ilc_option_b_graduation_checklist_state_664_v0.1.json`

Inherited rule set:
- static peer registry v1 remains the authorized discovery posture
- curated bootstrap sources are allowed; candidate discovery is not active-peer
  admission
- dynamic peer discovery remains deferred beyond this window
- heavy graph/canon payloads remain pull-only and receiver-controlled
- PUSH remains bounded to small metadata and topology signals
- `Option D` remains active
- `CDL-062` remains unopened

Operational planning inputs newly emphasized in this window:
- the two external VPNs are available as realistic but bounded distributed test
  infrastructure
- OpenClaw may be used on remote VPS infrastructure as an overlay harness for
  agent operability, but it is not a required dependency for transport
  correctness

## 3. Track inventory

### 3.1 Operationally obligated

- row-9 maturity contract with explicit closure-tier versus stretch-tier split
- VPN firewall posture verification and port-exposure matrix
- reproducible multi-machine canary harness
- churn, partition/recovery, fallback, restart/rejoin, and bounded push / pull
  correctness drills
- operator playbook and reusable metrics/evidence packaging
- honest maturity decision for row 9 at closure

### 3.2 Deferred governance or research

- dynamic peer discovery
- DHT, swarm, or mirror-based peer-learning that can autonomously alter the
  runtime peer set
- anonymous-communication or privacy-overlay ambitions beyond the current
  transport posture
- row 5 privacy closure
- rows 7 and 8 closure
- `CDL-062` opening
- final `Option B` selection

### 3.3 Simulation and live-infra expectations

- repeated canary and drill execution is required in this window
- closure-grade evidence must include multi-machine runs
- selected VPN-backed evidence is required if firewall posture and operator GO
  allow it
- OpenClaw sidecar investigation is encouraged where it makes the internal RC
  stack more informative, but it does not replace the raw transport harness

## 4. Practical maturity contract baseline

The practical row-9 target in this lane is:
- bounded public-participant transport/discovery maturity
- not full internet-scale proof
- not a toy single-host demo

Default closure-tier baseline:
- at least `5` nodes across `3` machines
- selected VPN-backed evidence where feasible
- `3` clean repetitions after the final hardening round
- `1` soak run
- documented manual bootstrap and fallback allowed
- heroics, code edits, DB surgery, or bespoke debugging during ordinary
  operation are forbidden

Stretch-tier baseline:
- `7+` nodes if feasible
- more repetitions where cost is low
- broader VPN-backed scenario coverage
- longer soak or churn windows
- OpenClaw-assisted remote-agent usability checks on top of the base harness

The lane must treat closure-tier success as enough for row-9 closure if no
core defect remains. Stretch-tier findings only block closure if they reveal a
core maturity failure that invalidates the closure-tier evidence.

## 5. Discovery and bootstrap posture for this window

The row-9 lane must not reopen basic discovery-governance questions.

This window inherits:
- static peer registry v1
- curated bootstrap sources
- explicit promotion before runtime peer use

This window must preserve:
- `candidate_discovery_not_active_peer_admission`
- `bootstrap_inventory_not_admission_authority_by_itself`
- `explicit_promotion_required_before_runtime_peer_use`

This window does not authorize:
- dynamic discovery
- DHT or swarm discovery
- gossip-driven autonomous peer-set expansion
- anonymous overlay networking as a closure requirement

## 6. Candidate phase table

| Order | Phase | Topic | Character | Sensitivity |
|---|---:|---|---|---|
| 1 | 665 | Sequence lock, open-questions register, and historical recovery | Foundation / Planning | **SENSITIVE** |
| 2 | 666 | Maturity criteria, threshold contract, and evidence schema | Planning / Contract | planning |
| 3 | 667 | Multi-machine harness and VPN canary pack | Implementation / Tooling | **SENSITIVE** |
| 4 | 668 | Drill execution and failure harvest | Live canary / Evidence | **SENSITIVE** |
| 5 | 669 | Hardening loop and maturity decision | Implementation / Review | **SENSITIVE** |
| 6 | 670 | Closure gate, checklist delta, capsule, and handoff | Gate | **SENSITIVE** |

### Conditional note on Phases 665-670

There are no conditional tail slots in this window. All six phases are firm.

### Note on live infrastructure

Phases 667-669 are operational phases. They may require:
- explicit human GO before any live VPN or remote-host interaction
- explicit human GO before any firewall or port-posture change
- honest fallback to partial-state evidence if the infra posture is not yet
  sufficient for the desired VPN-backed scenario set

### Note on OpenClaw

OpenClaw is allowed only as an overlay harness or sidecar in this window. The
raw transport harness must remain independently valid and must not require
OpenClaw for base transport correctness.

## 7. Sensitivity classification

### SENSITIVE phases list

- Phase 665: sequence-lock and live-infra-policy boundary phase
- Phase 667: may mutate transport/harness/tooling surfaces and define live
  topology machinery
- Phase 668: executes live drills and records closure-grade evidence
- Phase 669: may mutate runtime/tooling surfaces based on failures and makes
  the maturity decision
- Phase 670: official closure boundary for row 9

### NON-SENSITIVE phases list

- Phase 666: contract-writing and threshold-setting phase only; no live infra
  execution required

### Human-GO rules

- explicit human GO required before every **SENSITIVE** phase commit
- explicit human GO also required before any live VPN/OpenClaw/remote-host
  execution or firewall change, even inside a non-commit checkpoint

## 8. Scope notes for fixed phases

### Phase 665 — sequence lock and recovery register

Sensitivity: **SENSITIVE**. Explicit human GO required before commit.

Deliverables:
- `docs/specs/ilc_phase_665_670_sequence_lock_v0.1.md`
- `docs/specs/ilc_transport_open_questions_and_historical_recovery_665_v0.1.md`
- `tests/test_phase_665_window_665_670_sequence_lock.py`

Required content spec:
- row-9 target as bounded public-participant maturity
- closure-tier versus stretch-tier framing
- dynamic discovery explicit defer
- VPN firewall posture as an early gate
- OpenClaw overlay-harness boundary
- “lazy network, deterministic failure semantics” framing

### Phase 666 — maturity criteria and threshold contract

Deliverables:
- `docs/specs/ilc_transport_maturity_contract_666_v0.1.md`
- `docs/specs/ilc_transport_maturity_contract_666_v0.1.json`
- `tests/test_phase_666_transport_maturity_contract.py`

Required content spec:
- closure-tier and stretch-tier definitions
- topology minimum
- repeatability bar
- broad timing bands
- operator-burden rules
- scenario catalog and evidence schema

### Phase 667 — multi-machine harness and VPN canary pack

Sensitivity: **SENSITIVE**. Explicit human GO required before commit and before
any live remote execution.

Deliverables:
- `docs/specs/ilc_transport_harness_and_vpn_canary_pack_667_v0.1.md`
- targeted runtime/tooling implementation in `ilc_core/network/d2d/`,
  `tools/testbed/`, and tests as needed
- `tests/test_phase_667_transport_harness_and_vpn_canary_pack.py`

Required content spec:
- tiered topology support (`Tier A`, `Tier B`, `Tier C`)
- VPN posture checks that fail closed
- machine-readable metrics capture
- no dynamic discovery and no OpenClaw hard dependency

### Phase 668 — drill execution and failure harvest

Sensitivity: **SENSITIVE**. Explicit human GO required before live remote
execution or commit.

Deliverables:
- `docs/specs/ilc_transport_drill_execution_report_668_v0.1.md`
- `docs/specs/ilc_transport_drill_metrics_668_v0.1.json`
- `tests/test_phase_668_transport_drill_execution.py`

Required scenario families:
- bootstrap
- steady-state dissemination
- churn
- partition/heal/recovery
- HTTP/2 fallback activation
- restart/rejoin
- bounded push correctness
- pull-only heavy payload correctness

### Phase 669 — hardening loop and maturity decision

Sensitivity: **SENSITIVE**. Explicit human GO required before commit and before
any rerun on live infra.

Deliverables:
- `docs/specs/ilc_transport_hardening_and_maturity_decision_669_v0.1.md`
- targeted runtime/tooling/test changes as needed
- `tests/test_phase_669_transport_hardening_and_maturity_decision.py`

Required decision rule:
- row 9 becomes a closure candidate if and only if closure-tier evidence passes
  after the final hardening round
- stretch-tier failures block closure only if they reveal a core maturity defect

### Phase 670 — closure and handoff

Sensitivity: **SENSITIVE**. Explicit human GO required before commit.

Deliverables:
- `docs/specs/ilc_window_665_670_handoff_670_v0.1.md`
- `docs/specs/ilc_option_b_graduation_checklist_state_670_v0.1.json`
- `docs/specs/ilc_antigravity_context_capsule_v4.1.md`
- `tools/run_window_665_670_transport_maturity_closure_gate_phase_670.sh`
- `tests/test_phase_670_window_665_670_closure_and_handoff.py`

Required closure rule:
- row 9 is `closed` if and only if the maturity contract is met and the gate
  passes
- otherwise row 9 remains `partial` with explicit carry-forward
- rows 5, 7, and 8 remain open
- next planned lane is Window 671-676
