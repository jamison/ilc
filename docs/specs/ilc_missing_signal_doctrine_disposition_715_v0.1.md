# ILC Missing Signal Doctrine Disposition 715 v0.1

**Phase:** 715  
**Window:** 713-716  
**Date:** 2026-04-17  
**Author:** Codex

`missing_signal_behavior_explicitly_selected`

## 1. Baseline

The active gossip lane is the Python D2d path under:

- static peer registry,
- single-hop bounded-fanout gossip,
- envelope validation from `CDL-061`,
- privacy constraints from `CDL-039`,
- temporal-decay semantics from `CDL-V1`.

This doctrine does not ratify a new CDL. It chooses explicit behavior for the
already-live missing-signal problem in the inherited lane.

## 2. Selected behavior

Selected behavior:

- grace period + alert, then fail-soft degradation.

This means:

1. a missing expected gossip signal first triggers a local grace window rather
   than immediate hard failure,
2. the node emits an explicit alert / operator-visible missing-signal event,
3. if the signal remains absent past the grace window, the node degrades
   behavior without treating the condition as success,
4. the node continues bounded operation over the same static peer set rather
   than halting the whole lane or authorizing new topology rights.

This is stricter than silent fail-open and less brittle than immediate
fail-closed under the current static baseline.

## 3. Escalation path

Immediate path:

- detect missing expected signal,
- enter grace period,
- alert locally,
- attempt bounded reconnect / re-sync within the same static peer set.

If the signal remains missing after grace:

- enter fail-soft degraded behavior,
- keep the node inside the static topology baseline,
- continue to reject discovery or topology-shuffling shortcuts,
- preserve explicit auditability of the degraded state.

`behavior_defines_escalation_without_new_ratification`

`CDL-V1` temporal decay participates only as a longer-horizon reputational
pressure on persistently absent contribution across issuance epochs. It does not
replace immediate transport diagnosis, and it does not silently convert a
missing-signal event into a transport-layer success.

## 4. Implicated source surfaces

The implicated source surfaces are:

- `docs/specs/ilc_cdl_v1_temporal_decay_runtime_handoff_388_v0.1.md`
- `docs/specs/ilc_cdl_060_gossip_centrality_extension_ratification_evidence_541_v0.1.md`
- `docs/specs/ilc_cdl_061_gossip_http_envelope_ratification_evidence_561_v0.1.md`
- `docs/specs/ilc_cdl_039_topology_shuffling_authorization_scope_note_711_v0.1.md`
- `ilc_core/network/d2d/gossip_peer_registry.py`
- `ilc_core/network/d2d/centrality_delta_gossip_runtime.py`
- `ilc_core/network/d2d/gossip_transport.py`
- `ilc_core/network/d2d/http_gossip_transport_runtime.py`

The doctrine depends on those existing surfaces but does not ratify or reopen
them.

## 5. Deferred items and non-goals

Deferred:

- dynamic discovery as a missing-signal response,
- topology shuffling as a missing-signal response,
- any benchmark-results claim for repair quality,
- any `CDL-039` ratification or authorization expansion,
- any runtime mutation in this docs-only phase.

Carry-forward precision still required in a later runtime contract or evidence-bearing
implementation lane:

- what concrete detector starts a "missing expected signal" event,
- how the grace window is measured or bounded,
- what exact node behaviors constitute fail-soft degraded operation.

This disposition intentionally selects the doctrine shape without fixing those
runtime-level thresholds or behaviors numerically in the docs-only window.

Non-goals:

- no new CDL row,
- no decision-log mutation,
- no claim that missing-signal handling is benchmark-validated in-window.

`no_dynamic_discovery_or_topology_shuffling_authorized_here`

`CDL-039` ratification does not occur here.
