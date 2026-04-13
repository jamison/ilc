# ILC PRNG, Timeout, and Invariant Enforcement Hardening 645 v0.1

Status: hardening artifact
Date: 2026-04-14
Classification: implementation and security hardening
Phase: 645
Owner lane: G8 security boundary and remaining-float strike force

## 1. Scope and threat basis

Phase 645 removes predictable PRNG from the touched runtime/security-sensitive
paths, hardens the peer HTTP timeout contract, and replaces touched production
`assert` enforcement with explicit checks.

## 2. Touched PRNG removal strategy

Touched paths no longer use Mersenne Twister:
- `ilc_core/network/peer.py` now derives peer fanout order from a canonical
  hash of local port, endpoint, payload, and target
- `ilc_core/epistemic/aesthetic_panel_runtime.py` now derives bucket ordering
  from a seed/model/agent hash rather than `random.Random(...).shuffle(...)`

`predictable_prng_removed_from_touched_runtime_paths`
`hash_derived_or_secure_selection_replaces_mersenne_twister_in_touched_paths`

## 3. Timeout contract

`ilc_core/network/peer.py` now uses a bifurcated timeout contract with separate
connect and read timeouts on the default sender path.

`bifurcated_http_timeout_contract_applied_to_touched_peer_or_cli_surface`

## 4. Explicit invariant enforcement contract

`ilc_core/economics/passive_ecu_attribution_runtime.py` no longer relies on
module-level `assert` for dependency and authorship-primacy invariants. The
touched runtime now performs explicit validation at import time and raises a
named runtime contract error if the module invariants are invalid.

`production_invariants_no_longer_depend_on_assert_in_touched_runtime`

## 5. Broad-catch regression guardrail

This phase removes the broad catch-all path from the touched peer delivery loop
so explicit invariant or programming failures are not silently swallowed under a
generic runtime logging path.

`assert_replacement_does_not_introduce_broad_exception_swallowing`
`touched_timeout_hardening_preserves_existing_runtime_contract_shape`

## 6. Verification evidence

Verification in this phase covers:
- touched PRNG removal and deterministic behavior
- bifurcated timeout behavior on peer delivery
- explicit passive-attribution runtime contract validation
- continued pass of the touched legacy runtime tests
