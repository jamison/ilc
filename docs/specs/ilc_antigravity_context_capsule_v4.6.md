# ILC Antigravity Context Capsule v4.6

Supersedes: docs/specs/ilc_antigravity_context_capsule_v4.5.md
Date: 2026-04-17
Owner lane: G8 governance minimization and validator-agent prelock closure

This capsule is self-contained.

## 1. Current frontier state

Capsule v4.6 supersedes v4.5.
Window 707-712 is now closed as the governance-minimization and validator-agent prelock lane.
Window 713-716 is the next planned continuation.

New frontier state at the close of Window 707-712:
- `CDL-066` is now `ratified`
- `CDL-067` is now `ratified`
- `CDL-017` remains `open` and unratified
- validator-agent design evidence is now published
- `SIM-VALIDATOR-01` is commissioned
- `SIM-TOPOLOGY-01` is commissioned
- topology shuffling remains later-authorized only
- row 5 remains `spec_closed_runtime_pending`
- row 6 remains `closed`
- row 7 remains `spec_closed_runtime_pending`
- row 8 remains `closed` and reconfirmed
- row 9 remains `closed`
- Track B status: `M-011 binary_complete; M-012 next planned; real 4-validator run still pending provisioning`

## 2. Frozen inherited boundary state

The following inherited boundaries remain frozen:

- Phase 576 and Phase 581 read-only wallet boundary
- Phase 587-589 receipt, identity, and settlement-linked legitimacy boundary
  stack
- Phase 609 ECU / ILC / bounded-runtime separation
- Phase 612 two-form MVP gate requirement
- ADR-0028 bounded-bridge posture
- row-6 upstream/downstream legitimacy boundary
- rows-7-and-8 criteria lock from Phase 675
- Window 693-700 chosen-substrate legitimacy closure state

Capsule v4.6 does not reopen:

- wallet widening
- public claimability
- ILC transferability
- row-5 or row-7 runtime closure claims
- `CDL-017` ratification or activation
- final production topology-shuffling law
- final Option B production selection

## 3. Window 707-712 closure state

Window 707-712 is now fixed as:

- Phase 707 sequence lock complete
- Phase 708 governance-minimization inventory, ADR-0019 disposition, and `CDL-066` ratification complete
- Phase 709 algorithm-governance contract, local-influence example, and `CDL-067` ratification complete
- Phase 710 validator-agent design evidence complete
- Phase 711 simulation commissioning and `CDL-039` scope note complete
- Phase 712 coherence, capsule, and closure gate complete

This window ratified the narrow governance lanes that were ready and bounded the
validator-agent lane as prelock evidence rather than premature law.

## 4. Remaining later-lane blockers

The surviving later-lane blockers now include:

- `CDL-017` ratification and later activation boundary work
- `SIM-VALIDATOR-01` execution and numeric floor evidence
- `SIM-TOPOLOGY-01` execution and topology-seed / diversity evidence
- row-5 runtime leakage confirmation
- row-7 runtime censorship and exitability confirmation
- Track B progression from `M-011` into `M-012` and later real liveness runs
- final Option B production selection
- legal-positioning memo work before broader public RC claims

## 5. Next authorized continuation

The next planned continuation is Window 713-716.

Window 713-716 carries:

- adaptive gossip and resilience operationalization
- explicit resilience contract versus implementation-freedom decisions
- transport-repair and failure-taxonomy hardening
- preparation inputs that will later support the Mysticeti convergence window
  without collapsing it into this lane
